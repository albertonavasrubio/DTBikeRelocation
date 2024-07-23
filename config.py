# -*- coding: utf-8 -*-
"""
Created on Fri may  5 23:10:44 2024

@author: alberto navas rubio
@mail: alberto.navas@adif.es

files with config installation parameters
"""

#LOCAL PATHS INSTALLATION
#path for the QGIS project file
path_to_project_file = "C:/Users/alber/OneDrive - ADIF/Compartido/bikeRelocation/bikeRelocation_qgis_project.qgz"

#path to pronostic files storage
path_to_pronostic_files ="C:/Users/alber/OneDrive - ADIF/Compartido/bikeRelocation/data/prediction data/"

#path to status files storage
path_to_status_files ="C:/Users/alber/OneDrive - ADIF/Compartido/bikeRelocation/data/status data/"

#path to common files
folder ='C:/Users/alber/OneDrive - ADIF/Compartido/bikeRelocation/data/'

#path to proccesinf batch files
path_to_proccesing_files ="C:/Users/alber/OneDrive - ADIF/Compartido/bikeRelocation/data/batch results data/"

#EXTERNAL CONECTIONS
#Conect to the vectortisel server
uri_inf_layer_map = 'type=xyz&url=https://mt1.google.com/vt/lyrs%3Dr%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0&0&crs=EPSG4326http-header:referer='

#connection to the real-ddta bike provider (gbfs - json format)
gbfs_server = 'https://barcelona.publicbikesystem.net/customer/gbfs/v2/en/station_status'

#Initial Config Parameters used in case of omission
depot_id =34
init_stations = [depot_id, depot_id, depot_id, depot_id, depot_id]
maximun_travel_time = 10000

# distance tolerance to fix nearest station search in map_canvas
max_dist_select_tool = 30

# maximun time for OR-Tools processing  (in seconds)
search_time_limit = 30

# maximun number of solution tested by OR-Tools
solution_limit = 100000

# maximun tolerance between solution for diferrent teams
SpanCostCoefficient  = 100

# Time spen in each station for operation in minutes
operation_time = 10

# -	CONSTANT_DEMAND:  The status data obtained as the start situation will be taken also as prediction for the following period (No delta increment on stations demands)
# -	PESSIMISTIC_2_PREDICTION: The prediction is generated aggregating a delta of -2 bikes (decrease) in each station
# -	OPTIMISTIC_2_PREDICTION: The prediction is generated aggregating a delta of 2 bikes (increases) in each station
# - MINUS_2_BIKE_PREDICTION'
# - PLUS_2_BIKE_PREDICTION'

prediction_strategy = 'PESIMISTIC_2_PREDICTION'

optimization_stretegy = 'PATH_CHEAPEST_ARC'