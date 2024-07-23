# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:51:14 2024

@author: alber
"""
import math
import config
import initialization

from PyQt5.QtCore import QVariant
from qgis._core import QgsField, QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.core import (QgsPoint, QgsFeature,
	               QgsGeometry, QgsProject, QgsRasterLayer, QgsVectorLayer, QgsRectangle)

def remove_feature_layer(layer:QgsVectorLayer,  project:QgsProject):

    print("Borrar capa: " + layer.name())
    # accessing Vector layer provider
    provider = layer.dataProvider()
    # deleting all features in the Vector layer
    provider.truncate()




def XYCoord(idstations):
    crs = '4326'
    stations_data = initialization.load_stations_data()
    ind = stations_data[idstations[0]]
    count = 1
    sql_query = 'virtual://?query=SELECT ' + str(count) + ' as id, MakePoint(' + str(ind[1]) + ',' + str(
        ind[0]) + ',' + str(crs) + ') as geom '

    for idstation in idstations[1:]:
        count += 1
        ind = stations_data[idstation]
        sql_query = sql_query + 'UNION SELECT ' + str(count) + ', MakePoint(' + str(ind[1]) + ',' + str(
            ind[0]) + ',' + str(crs) + ')'

    return sql_query

def create_layer_from_points(list_point):
    layer = QgsVectorLayer(
        "point?crs=epsg:4326field=id:integer",
        "temporary_points",
        "memory"
    )
    pr = layer.dataProvider()
    pr.addAttributes([QgsField("id", QVariant.Int)])
    pr.addAttributes([QgsField("station_id", QVariant.Int)])
    pr.addAttributes([QgsField("delta_bike", QVariant.Int)])
    layer.updateFields()
    number = len(list_point)
    # Create a QgsFeature for every point(coord pair)
    feats = [QgsFeature() for i in range(number)]
    for i, feat in enumerate(feats):
        point = QgsPoint(list_point[i][0], list_point[i][1])
        feat.setGeometry(point)
        feat.setAttributes([i+1,list_point[i][2],list_point[i][3]])
    # Add the feature to the layer provider

    pr.addFeatures(feats)
    return layer

def refresh_route_layers(stops_new:QgsVectorLayer, route_new:QgsVectorLayer, route:int, project:QgsProject):

    route_old = project.mapLayersByName('Route_'+str(route))[0] # change 'Layer B' to the name of your target layer
    pr_old = route_old.dataProvider()
    route_old.startEditing()
    route_feats = [f for f in route_new.getFeatures()]


    for feat in route_old.getFeatures():
        route_old.deleteFeature(feat.id())

    for feat in route_feats:
        old_feat = QgsFeature()
        old_feat.setGeometry(feat.geometry())
        pr_old.addFeature(feat)

    route_old.commitChanges()
    route_old.updateExtents()
    project.layerTreeRoot().findLayer(route_old.id()).setItemVisibilityCheckedParentRecursive(True)

    stops_old = project.mapLayersByName('stops_'+str(route))[0] # change 'Layer B' to the name of your target layer
    pr_old = stops_old.dataProvider()
    stops_old.startEditing()
    stops_feats = [f for f in stops_new.getFeatures()]

    for feat in stops_old.getFeatures():
        stops_old.deleteFeature(feat.id())

    for feat in stops_feats:
        old_feat = QgsFeature()
        old_feat.setGeometry(feat.geometry())
        pr_old.addFeature(feat)
    stops_old.commitChanges()
    stops_old.updateExtents()

    project.layerTreeRoot().findLayer(stops_old.id()).setItemVisibilityCheckedParentRecursive(True)



def refres_stations_data(stations:QgsVectorLayer = None, data:list=[] ,solve_data:list=[], batch = False):


    n_stations = 0
    n_No_pre_bike = 0
    n_No_pre_docks = 0
    n_No_opt_bike = 0
    n_No_opt_docks = 0

    # store data from covered demand
    optimized = {}
    for veh in solve_data:
        for station in veh:
            optimized[station[0]] = station[1]

    if not(batch):
        stations.startEditing()

        for feat in stations.getFeatures():
            id = int(feat['StationId'])
            attr = feat.attributes()[0:4]  #KeepValue of  4 first attributes (constants)
            # StationId  / Name / Latitude / Longitude

            # append next variable attributes
            if id in data.keys():
                n_stations = n_stations + 1
                if data[id]['pred_end_bikes'] < 0 :
                    n_No_pre_bike += 1
                if data[id]['pred_end_docks'] < 0:
                    n_No_pre_docks += 1
                attr.append(str(data[id]['ini_ava_bikes']))
                attr.append(str(data[id]['ini_ava_docks']))
                attr.append(str(data[id]['total_docks']))
                attr.append(str(data[id]['delta_bikes']))
                attr.append(str(data[id]['pred_end_bikes']))
                attr.append(str(data[id]['pred_end_docks']))
                if int(id) in optimized.keys():
                    if  optimized[id] < 0:
                        n_No_opt_bike += 1
                    else:
                        n_No_opt_docks += 1
                    attr.append(str(data[id]['pred_end_bikes'] - optimized[id]))
                    attr.append(str(data[id]['pred_end_docks'] + optimized[id]))
                else:
                    attr.append(str(data[id]['pred_end_bikes']))
                    attr.append(str(data[id]['pred_end_docks']))
            else:
                for i in range(8):
                    attr.append(str(0))  #Agrega valores de = si no encuentra la estacion

            feat.setAttributes(attr)
            stations.updateFeature(feat)

        stations.commitChanges()

    else:
        for id in data.keys():
            n_stations = n_stations + 1
            if data[id]['pred_end_bikes'] < 0:
                n_No_pre_bike += 1
            if data[id]['pred_end_docks'] < 0:
                n_No_pre_docks += 1
            if id in optimized.keys():
                if optimized[id] < 0:
                    n_No_opt_bike += 1
                else:
                    n_No_opt_docks += 1

    n_No_opt_bike = n_No_pre_bike - n_No_opt_bike
    n_No_opt_docks = n_No_pre_docks -  n_No_opt_docks
    return [n_stations, n_No_pre_bike, n_No_opt_bike, n_No_pre_docks, n_No_opt_docks]


def nearest_idStation(layer:QgsVectorLayer, point:QgsPointXY, project:QgsProject):
    """
    Function to select nearest station of a point
    """
    max_dist = config.max_dist_select_tool# maximun distance tolerance to fix nearest station
    id = None
    selected_feat_point = None
    for feat in layer.getFeatures():
        feat_point = feat.geometry()
        geo_proj = QgsGeometry(feat_point)

        sourceCrs = QgsCoordinateReferenceSystem(4326)
        destCrs = QgsCoordinateReferenceSystem(25831)

        tr = QgsCoordinateTransform(sourceCrs, destCrs, project)
        geo_proj.transform(tr)
        ref_point = geo_proj.asPoint()
        dist = math.sqrt(ref_point.sqrDist(point))
        if dist < max_dist:
            max_dist = dist
            print(str(dist))
            selected_feat_point = feat
    return selected_feat_point

