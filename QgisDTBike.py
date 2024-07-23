# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 11:00:53 2024

@author: alberto navas rubio

modulo GUI basado en QTqgs  (QT for QGIS)
"""


import os
import sys

import capture_json  #modulo importacion datos desde json services
import Optimization  #modulo Optimizador
import config  #modulo con los valores configurables
import QgisScripts # Modulo con Scripts de pyQgis
import initialization

from datetime import datetime
from PyQt5.QtWidgets import QMessageBox

from uibikerelocation import Ui_MainWindow
from qgis.core import (QgsApplication, QgsCoordinateReferenceSystem, QgsFeature,
	               QgsGeometry, QgsProject, QgsRasterLayer, QgsVectorLayer, QgsRectangle)
from qgis.gui import (QgsLayerTreeMapCanvasBridge, QgsMapCanvas,
                    QgsMapMouseEvent,QgsMapToolIdentifyFeature,QgsMapToolPan)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QMenu, QAction, QMainWindow, QVBoxLayout


# GLOBAL VARIABLEs
init_teams_position =[config.depot_id for i in range(20)] # Posicion inicial en deposito


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

sys.path.append(r'C:/OSGeo4W/apps/qgis-ltr/python/plugins')
sys.path.append(r'C:/OSGeo4W/apps/qgis-ltr/plugins')
QgsApplication.setPrefixPath('C:/OSGeo4W/apps',True)
QgsApplication.setPluginPath('C:/OSGeo4W/apps/apps/qgis-ltr/plugins')
QgsApplication.setPkgDataPath('C:/OSGeo4W/apps/apps/qgis-ltr/.')
qgs = QgsApplication([], True)
qgs.initQgis()
wnd =MainWindow()
canvas = wnd.widget
project = QgsProject.instance()

from ORStools.ORStoolsPlugin import *
from ORStools.proc.provider import ORStoolsProvider

ORT = ORStoolsProvider()

import processing
from processing.core.Processing import Processing
proc = Processing()
proc.initialize()

QgsApplication.processingRegistry().addProvider(ORT)
locale = QgsSettings()
locale.setValue("locale/userLocale", "es-ES")



def populate_historic_comoBox(mw):
    lista_files = os.listdir(config.path_to_status_files)
    lista_menu = []
    for file in lista_files:
        if file[0:14]=="capstone_data_" and file[27:38]=="_status.csv":
            text = file[14:18] + '-' + file[18:20] + '-' + file[20:22]+ ' ' + file[23:25] +':' + file[25:27]

            if os.path.isfile(config.path_to_pronostic_files+"capstone_data_pred_mocked_" + file[14:27] +'.csv' ):
                pred = True
            else:
                pred = False
            lista_menu.append([text, pred])
    it = 0
    for item in lista_menu:
        er= mw.comboBox_2.addItem(item[0])
        if item[1]:
            # Change color when predition exist
            mw.comboBox_2.setItemData(it, QColor(205, 92, 92), Qt.BackgroundRole)
        it= it +1

def run_when_project_saved():
    print('Project saved')

def run_when_application_state_changed(state):
    print('State changed', state)

# a slot to populate the context menu
def populateContextMenu(menu: QMenu, event: QgsMapMouseEvent):
    """
    Rellena el menu contextual con los datos de las ficheros de Pronostico del directorio
    de almaceamiento de pronostico que estara definido en config.py.
    Los ficheros deben encontrarse por pares y tener la siguiente nomenclatura:
        20221026_status.csv
        pred_mocked_20221026_1900.csv
    """

    Posicion = event.mapPoint()

    subMenu = menu.addMenu('Change Init Station for a Team')
    subMenu.addAction('Team nº1').triggered.connect(lambda *args: signal_select_team(Posicion,1))
    subMenu.addAction('Team nº2').triggered.connect(lambda *args: signal_select_team(Posicion, 2))
    subMenu.addAction('Team nº3').triggered.connect(lambda *args: signal_select_team(Posicion, 3))
    subMenu.addAction('Team nº4').triggered.connect(lambda *args: signal_select_team(Posicion, 4))
    subMenu.addAction('Team nº5').triggered.connect(lambda *args: signal_select_team(Posicion, 5))
    subMenu.addAction('Team nº6').triggered.connect(lambda *args: signal_select_team(Posicion,6))
    subMenu.addAction('Team nº7').triggered.connect(lambda *args: signal_select_team(Posicion, 7))
    subMenu.addAction('Team nº8').triggered.connect(lambda *args: signal_select_team(Posicion, 8))
    subMenu.addAction('Team nº9').triggered.connect(lambda *args: signal_select_team(Posicion, 9))
    subMenu.addAction('Team nº10').triggered.connect(lambda *args: signal_select_team(Posicion, 10))
    subMenu.addAction('Team nº11').triggered.connect(lambda *args: signal_select_team(Posicion, 11))
    subMenu.addAction('Team nº12').triggered.connect(lambda *args: signal_select_team(Posicion, 12))

    subMenu2 = menu.addMenu('Station Identification Tool')
    subMenu2.addAction('Select Station').triggered.connect(lambda *args: signal_feature_identification(Posicion))

#   iaction.triggered.connect(lambda *args: print(f'Action triggered at {event.x()},{event.y()}'))

def btn_optimize():
    global project
    global init_teams_position

    dt = datetime.now()
    timeStamp =str(dt)
    print(timeStamp)

    # Cleancurrente route/stops layers

    for lay in range(5):
        route = project.mapLayersByName('Route_'+str(lay+1))[0]
        QgisScripts.remove_feature_layer(route,project)
        stops = project.mapLayersByName('stops_' + str(lay + 1))[0]
        QgisScripts.remove_feature_layer(stops,project)

    if wnd.realTimeCheckBox.isChecked():
        item  = capture_json.download_data()
        print("Real-Time Optimization: " + item)

    else:
        item =wnd.comboBox_2.currentText()

    time_text = item[0:4]+item[5:7]+item[8:10]+'_'+ item[11:13]+item[14:16]
    print(time_text)

    file_name="capstone_data_" + time_text + "_status.csv"
    teams = int(wnd.comboBox.currentText())  #numero de equipos que se planifica
    time_limit = int(wnd.comboBox_3.currentText())*60 #Change Time from minutes to seconds
    print("Number of teams: " + str(teams))
    strt=[init_teams_position[i] for i in range(teams)]
    print('Init_teams_position: ' + str(strt))

    solve , printSolve = Optimization.main(file_name, initStations=strt,time_limit=time_limit) #List Of routes
    wnd.textEdit.append(timeStamp + " Resultado Algoritmo Optimizador:" )
    wnd.textEdit.append(printSolve + '\n')

    #Actualizar atributos de la capa de estaciones
    data = initialization.generate_estimated_demands(file_name)
    stations_layer = project.mapLayersByName('stations')[0]
    KPIs = QgisScripts.refres_stations_data(stations_layer, data , solve)

    wnd.textEdit.append("----------KPIs predicted------")
    wnd.textEdit.append("nº Stations wihtout Bikes: " + str(KPIs[1]) + "/" + str (KPIs[0]) +" (" + str(KPIs[1]/KPIs[0]*100)+")")
    wnd.textEdit.append("nº Stations wihtout docks: " + str(KPIs[3]) + "/" + str (KPIs[0]) +" (" + str(KPIs[3]/KPIs[0]*100)+")"+'\n')
    wnd.textEdit.append("----------KPIs optimized------")
    wnd.textEdit.append("nº Stations wihtout Bikes: " + str(KPIs[2]) + "/" + str (KPIs[0]) +" (" + str(KPIs[2]/KPIs[0]*100)+")")
    wnd.textEdit.append("nº Stations wihtout docks: " + str(KPIs[4]) + "/" + str (KPIs[0]) +" (" + str(KPIs[4]/KPIs[0]*100)+")")
    wnd.textEdit.append('\n')
    route_number = 0
    for vehicleStations in solve:
        #vehicleStation is a list of stops-ids
        route_number = route_number + 1
        #strVirtual= main3.XYCoord(vehicleStations)

        #Create list of points from list of ids
        stations_data = initialization.load_stations_data()  #X-Y location of each station
        # vehiclestation[0] -> Data of the first Stop of the vehicle route
        # vehiclestation[0][0] -> Data of the Id  of the First Stop of the vichile Route
        # vehiclestation[0][1] -> Data of the demand covered in the First Stop of the vichile Route
        # stations_data[id_station]=(lat, lon)

        ind = stations_data[vehicleStations[0][0]]  # ind-> first stop[lat, long]
        points = [(ind[1], ind[0],vehicleStations[0][0],vehicleStations[0][1])]
        count = 0
        for station in vehicleStations[1:]:
            count += 1
            ind = stations_data[station[0]]
            #------ lon, lat, id_station, load_station
            points.append((ind[1],ind[0],station[0],station[1]))
        print(points)
        #Create memory layer form list of points
        point_layer = QgisScripts.create_layer_from_points(points)
        #project.addMapLayer(point_layer)
        print(point_layer)

        #Create a route that conect all points from ORS Tools route alghoritm
        myresult = processing.run("ORS Tools:directions_from_points_1_layer",
                                  {'CSV_COLUMN': '',
                                   'CSV_FACTOR': None,
                                   'EXPORT_ORDER': False,
                                   'EXTRA_INFO': [],
                                   'INPUT_AVOID_BORDERS': None,
                                   'INPUT_AVOID_COUNTRIES': '',
                                   'INPUT_AVOID_FEATURES': [],
                                   'INPUT_AVOID_POLYGONS': None,
                                   'INPUT_LAYER_FIELD': 'id',
                                   'INPUT_OPTIMIZE': None,
                                   'INPUT_POINT_LAYER': point_layer,
                                   'INPUT_PREFERENCE': 1,
                                   'INPUT_PROFILE': 0,
                                   'INPUT_PROVIDER': 0,
                                   'INPUT_SORTBY': 'id',
                                   'OUTPUT': 'TEMPORARY_OUTPUT'})
        route_layer = myresult['OUTPUT']
        print("Route Layer Created")
        #QgsProject.instance().addMapLayer
        print("Refresh Route layers")

        state = QgisScripts.refresh_route_layers(point_layer, route_layer, route_number, project)

    # Add our own algorithm provider
    #from example_algorithm_provider import ExampleAlgorithmProvider
    #provider = ExampleAlgorithmProvider()
    #QgsApplication.processingRegistry().addProvider(provider)

def signal_select_team(point: QgisScripts.QgsPointXY, men: int):
    global project
    global init_teams_position
    global wnd
    team = men

    if int(wnd.comboBox.currentText()) < team:
        QMessageBox.information(None, "Init Station for a Team:", "Before Selecting Start Point for team " + str(men) + " you must select the correct number of teams")
        return 0

    stations = project.mapLayersByName('stations')[0]
    station_feat = QgisScripts.nearest_idStation(stations, point, project)
    if station_feat is not None:
        init_teams_position[team-1]=int(station_feat.attribute("StationId"))
        wnd.textEdit.append("station Init for Teams Changed to: " + str(init_teams_position))
        # Refresh filter for showing init stations in map layer
        num_teams = int(wnd.comboBox.currentText())
        selection = "('" + str(init_teams_position[0]) + "'"
        for n in range(num_teams - 1):
            index = n + 1
            selection = selection + ",'" + str(init_teams_position[index]) + "'"
        selection = selection + ")"

        init_layer = project.mapLayersByName('init_stations')[0]
        querystring = '"StationId" IN' + selection
        init_layer.setSubsetString(querystring)

    else:
        msg = "NO station selected: (Actual search range from click position = " + str(
            config.max_dist_select_tool) + " m.)"
        QMessageBox.information(None, "Init Station for a Team:", msg)

def signal_start_points(cb):
    layer = project.mapLayersByName('init_stations')[0]
    if cb.isChecked():
        project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
    else:
        project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(False)
def signal_routes_checboxe(cb):
    texto = cb.text()
    if texto == 'Base Map':
        layer = project.mapLayersByName('btn')[0]
    else:
        team = 'Route_' + texto[5:]
        layer=project.mapLayersByName(team)[0]
    if cb.isChecked():
        project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
    else:
        project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(False)


def signal_button_depot():
    global init_teams_position
    num_teams = int(wnd.comboBox.currentText())
    for i in range(num_teams):
        init_teams_position[i] = config.depot_id
    wnd.textEdit.append('Teams start at:' + str(init_teams_position))
    selection = "('" + str(init_teams_position[0]) + "'"
    for n in range(len(init_teams_position)-1):
        index = n + 1
        selection = selection + ",'" + str(init_teams_position[index]) + "'"
    selection = selection + ")"

    init_layer = project.mapLayersByName('init_stations')[0]
    querystring = '"StationId" IN' + selection
    init_layer.setSubsetString(querystring)
def signal_change_number_of_teams():
    # Actualizar capa de presentacion de estaciones de INICIO
    num_teams = int(wnd.comboBox.currentText())
    selection ="('" + str(init_teams_position[0]) + "'"
    for n in range(num_teams-1):
        index = n + 1
        selection = selection + ",'" + str(init_teams_position[index]) + "'"
    selection = selection  + ")"

    init_layer = project.mapLayersByName('init_stations')[0]
    string = '"StationId" IN'  +  selection
    #response = init_layer.setSubsetString('"StationsId" IN(\'%s\'' % selection)
    response = init_layer.setSubsetString(string)
    print(string)
    print(response)
def signal_stations_radiobutton(rb):
    show_layers =[]
    hide_layers = []
    if rb.text() == 'No Stations':
        hide_layers.append(project.mapLayersByName('stations')[0])
        hide_layers.append(project.mapLayersByName('stations_to_optimize')[0])
        for team in range(13)[1:]:
            hide_layers.append(project.mapLayersByName('stops_'+ str(team))[0])

    elif rb.text() == 'Optimized Stations':
        hide_layers.append(project.mapLayersByName('stations')[0])
        hide_layers.append(project.mapLayersByName('stations_to_optimize')[0])
        for team in range(13)[1:]:
            show_layers.append(project.mapLayersByName('stops_'+ str(team))[0])

    elif rb.text() == 'Stations to Optimize':
        hide_layers.append(project.mapLayersByName('stations')[0])
        show_layers.append(project.mapLayersByName('stations_to_optimize')[0])
        for team in range(13)[1:]:
            show_layers.append(project.mapLayersByName('stops_'+ str(team))[0])

    elif rb.text() == 'All Stations':
        show_layers.append(project.mapLayersByName('stations')[0])
        show_layers.append(project.mapLayersByName('stations_to_optimize')[0])
        for team in range(13)[1:]:
            show_layers.append(project.mapLayersByName('stops_' + str(team))[0])

    # Hide all the layers
    for layer in hide_layers:
        project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(False)

    for layer in show_layers:
        project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)

def signal_feature_identification(position):
    """Code called when the feature is selected by the user"""
    global project
    stops_layer = project.mapLayersByName('stations')[0]
    feat_station = QgisScripts.nearest_idStation(stops_layer, position, project)

    if feat_station is not None:
        msg ="Selected Station: " + str(feat_station.id())
        names = stops_layer.fields().names()
        for index, value in enumerate(feat_station.attributes()):
            msg = msg + '\n' + names[index] + ": " + str(value)
    else:
        msg = "NO station selected: (Actual search range from click position = " + str(config.max_dist_select_tool) + " m.)"
    QMessageBox.information(None, "Station Information:", msg)

"""
************PROGRAM*******
"""
#Rellena el ComboBox con el listado de los pronostios encontrados
populate_historic_comoBox(wnd)
wnd.pushButton.clicked.connect(btn_optimize)
wnd.depotButton.clicked.connect(signal_button_depot)
wnd.checkBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.checkBox))
wnd.checkBox_2.clicked.connect(lambda *args: signal_routes_checboxe(wnd.checkBox_2))
wnd.checkBox_3.clicked.connect(lambda *args: signal_routes_checboxe(wnd.checkBox_3))
wnd.checkBox_4.clicked.connect(lambda *args: signal_routes_checboxe(wnd.checkBox_4))
wnd.checkBox_5.clicked.connect(lambda *args: signal_routes_checboxe(wnd.checkBox_5))
wnd.team6checkBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.team6checkBox))
wnd.team7checkBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.team7checkBox))
wnd.team8checkBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.team8checkBox))
wnd.team9checkBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.team9checkBox))
wnd.team10checkBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.team10checkBox))
wnd.team11checkBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.team11checkBox))
wnd.team12checkBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.team12checkBox))
wnd.MapcheckBox.clicked.connect(lambda *args: signal_routes_checboxe(wnd.MapcheckBox))

wnd.radioButton.clicked.connect(lambda *args: signal_stations_radiobutton(wnd.radioButton))
wnd.radioButton_2.clicked.connect(lambda *args: signal_stations_radiobutton(wnd.radioButton_2))
wnd.radioButton_3.clicked.connect(lambda *args: signal_stations_radiobutton(wnd.radioButton_3))
wnd.radioButton_4.clicked.connect(lambda *args: signal_stations_radiobutton(wnd.radioButton_4))

wnd.comboBox.currentTextChanged.connect(signal_change_number_of_teams)

wnd.startPointsCheckBox.clicked.connect(lambda *args: signal_start_points(wnd.startPointsCheckBox))
#Set path for the project file, configuration of layers presentation can be done witht QGIS app
project_file = config.path_to_project_file
project.read(project_file)
canvas.setProject(project)

# Context Menu set as tht Canvas Map Tool
mapTool = QgsMapToolPan(canvas)
canvas.setMapTool(mapTool)
canvas.contextMenuAboutToShow.connect(populateContextMenu)

canvas.zoomToFullExtent() # zoom to extend of all layer
canvas.freeze(True)
canvas.show()
canvas.refresh()
canvas.freeze(False)
canvas.repaint()
bridge = QgsLayerTreeMapCanvasBridge(
        project.layerTreeRoot(),
        canvas
    )

# Init Layers hidden:
signal_button_depot()
for layer in project.mapLayers():
    project.layerTreeRoot().findLayer(layer).setItemVisibilityChecked(False)

wnd.show()
project.projectSaved.connect(run_when_project_saved)
qgs.applicationStateChanged.connect(run_when_application_state_changed)

# ---- Muestra la Aplicacion
exitcode = qgs.exec()
# ---- Salida de la Apliacion

sys.exit(exitcode)
qgs.exitQgis()






