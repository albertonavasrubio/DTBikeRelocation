# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 18:21:25 2024

@author: alberto navas rubio

Modulo que contiene variables de inicializacion

"""
import csv
import config
import os

def generate_pred_data(from_status_data):

    print("generate_pred_data: from_Status_Data")
    pred_data={}
    for date in from_status_data.keys():
        pred_data[date] = {}
        for time in from_status_data[date].keys():
            period_time = time+'-'+str(int(time[0:2]) +1) + ':' + time[3:5]
            pred_data[date][period_time]={}
            for station in from_status_data[date][time].keys():
                bikes = from_status_data[date][time][station][0]
                docks = from_status_data[date][time][station][1]
                # Applied a strategic predicion of +/- 2 bikes in next hour
                if config.prediction_strategy == 'MINUS_2_BIKE_PREDICTION':
                    delta_bikes =  - 2
                elif config.prediction_strategy == 'PLUS_2_BIKE_PREDICTION':
                    delta_bikes =  + 2
                elif config.prediction_strategy == 'PESIMISTIC_2_PREDICTION':
                    if bikes < docks:
                        delta_bikes =  - 2
                    else:
                        delta_bikes =  2
                elif config.prediction_strategy == 'OPTIMISTIC_2_PREDICTION':
                    if bikes < docks:
                        delta_bikes =   2
                    else:
                        delta_bikes =-  2
                else:
                    #CONSTANT_DEMAND:
                    delta_bikes = 0
                pred_data[date][period_time][station] = delta_bikes

                #print(str(station) + ' - ' + str(delta_bikes))
    return pred_data
def generate_estimated_demands(status_file):
    """
    file format : capstone_data_20231034_1900_status.csv
    file format : capstone_data_pred_mocked_20231034_1900.csv
        '2022-10-26','19:00-20:00'
    Extrae los datos de prediciones del archivo y lo salmacenan en el dic: demands
    """
    print("generate_Estimated_demands: status_file="+status_file)

    period = status_file[23:25] + ':' + status_file[25:27] + '-' + str(int(status_file[23:25])+1) + ':' + status_file[25:27]
    date = status_file[14:18] + '-' + status_file[18:20] + '-' + status_file[20:22]

    #fileName='capstone_data_'+ file[26:34]+'_status.csv'
    status_data = load_status_data(status_file)
    # Format:  status_data[date][time][station_id] = [n_bikes,n_docks]
    print("status_data:" + str(status_data))
    pred_file = 'capstone_data_pred_mocked_'+ status_file[15:28] + '.csv'
    if os.path.isfile(config.path_to_pronostic_files+ pred_file):
        pred_data = load_pred_data(pred_file)
    else:
        pred_data = generate_pred_data(status_data)
    print(pred_data)
    time = period.split('-')[0]
    stations_state = status_data[date][time]
    # Format:  stations_date[station_id] = [n_bikes, n_docks]

    stations_pred = pred_data[date][period]
    # Format: stations_pre[Station_id] = delta_bikes
    total_demand = 0
    stations_without_docks =0
    stations_without_bikes =0
    demands={}

    for station in stations_state.keys():

        # [station][0] current avaliable bikes /  [station][1] current avaliable docks

        # if delta <0 means bikes retired (avaliable bikes reduction )
        # if delta >0 means bikes docked (avaliable bikes increase)

        # positve demand means bikes to pick
        # negative demand means bikes to take
        if stations_pred[station] > stations_state[station][1]:
            #if more new bikes docked than avaliable docks
            demand = stations_pred[station] - stations_state[station][1]
            stations_without_docks += 1
        elif (-stations_pred[station]) > stations_state[station][0]:
            #if new picked bikes is more than avaliable bikes
            demand= stations_state[station][0] + stations_pred[station]
            stations_without_bikes += 1
        else:
            demand = 0

        demands[station] = {'ini_ava_bikes': stations_state[station][0],
                            'ini_ava_docks': stations_state[station][1],
                            'total_docks': stations_state[station][0] + stations_state[station][1],
                            'delta_bikes': stations_pred[station],
                            'pred_end_bikes': stations_state[station][0] + stations_pred[station] ,
                            'pred_end_docks': stations_state[station][1] - stations_pred[station],
                            'demand': demand}
        total_demand = total_demand + demand

        #compensation
        # Si faltan bicis
    i = 0
    stations_ids = list(stations_state.keys())
    print(stations_without_docks)
    print(stations_without_bikes)
    print(total_demand)
    if total_demand < 0:
            while total_demand < 0:
                # Donde hay exceso de bicis se cogen mas
                if demands[stations_ids[i]]['demand']>0:
                    demands[stations_ids[i]]['demand'] = demands[stations_ids[i]]['demand'] + 1
                    total_demand += 1
                i+=1
                if i > (len(stations_ids)-1):
                    i = 0
    elif total_demand > 0:
            while total_demand > 0:
                if demands[stations_ids[i]]['demand']<0:
                    demands[stations_ids[i]]['demand'] = demands[stations_ids[i]]['demand'] - 1
                    total_demand -= 1
                i+=1
                if i > (len(stations_ids)-1):
                    i = 0

    print("Demandas:" + str(total_demand))
    return demands



def load_status_data(fileName='capstone_data_20221026_1100_status.csv'):
    """
    format input csv:
        date,time,station_id,n_bikes_available,n_docks_available
    Stores dat relted to station status on a dictionary

    Returns dictionary: status_data[date][time][station_id] = [n_bikes,n_docks]
    -------
    status_data : TYPE
        DESCRIPTION.

    """
    print("load_status_data: filename="+fileName)
    file = config.path_to_status_files + fileName
    status_data={}
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        row_count = sum(1 for row in csv_reader)
        csv_file.seek(0)  #retorna aa la primera linea del fichero   
        data_line = csv_reader.__next__()
        data_line = csv_reader.__next__()
        date = data_line[0]
        status_data[date]={}
        time = data_line[1]
        status_data[date][time]={}
        station_id =int(data_line[2])
        n_bikes = int(data_line[3])
        n_docks = int(data_line[4])
        #****+TEPORARY SOLUTION FOR NEW STATIONS: DATA NOT IN OSM_MATRIX
        if station_id <520 or station_id==1000:
            status_data[date][time][station_id]=[n_bikes,n_docks]
        for row in range(row_count-2):
            data_line = csv_reader.__next__()
            date = data_line[0]
            time = data_line[1]
            station_id =int(data_line[2])
            n_bikes = int(data_line[3])
            n_docks = int(data_line[4])
            if not(date in status_data.keys()):
                status_data[date]={}
            if not(time in status_data[date].keys()):
                status_data[date][time]={}
            # ****+TEPORARY SOLUTION FOR NEW STATIONS: DATA NOT IN OSM_MATRIX
            if station_id < 520 or station_id == 1000:
                status_data[date][time][station_id] = [n_bikes,n_docks]

       # print(status_data)  
            
    
    return status_data

def load_pred_data(file):
    """
    format input csv:
        date,period,station_id,delta_bikes

    Returns
    -------
    pred_data : TYPE
        DESCRIPTION.

    """
    print("load_pred_data: file=" + file)
    file = config.path_to_pronostic_files + file
    pred_data={}
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        row_count = sum(1 for row in csv_reader)
        csv_file.seek(0)  #retorna aa la primera linea del fichero   
        data_line = csv_reader.__next__()
        data_line = csv_reader.__next__()
        date = data_line[0]
        pred_data[date]={}
        period_time = data_line[1]
        pred_data[date][period_time]={}
        station_id =int(data_line[2])
        delta_bikes = int(data_line[3])
        pred_data[date][period_time][station_id]=delta_bikes
        for row in range(row_count-2):
            data_line = csv_reader.__next__()
            date = data_line[0]
            period_time = data_line[1]
            station_id =int(data_line[2])
            delta_bikes = int(data_line[3])
            if not(date in pred_data.keys()):
                pred_data[date]={}
            if not(period_time in pred_data[date].keys()):
                pred_data[date][period_time]={} 
            pred_data[date][period_time][station_id] = delta_bikes

   # print(pred_data)        
    return pred_data

def load_osm_data():
    """
    Load Origin_Destination_Time_matrix from file
    The csv imput file must have these headers
    o_id|d_id|duration
    the data must be orderde o-id ASC, d_id ASC
    """
    print("load_osm_data")
    file = config.folder + 'osm_stations_duration.csv'
   
    distance_matrix=[]
    ids  =[]
    with open(file) as csv_file:
       csv_reader = csv.reader(csv_file, delimiter='|')
       row_count = sum(1 for row in csv_reader)
       num_stations = int(pow(row_count-1,0.5)) #calcula el  numero de estaciones
       csv_file.seek(0)  #retorna aa la primera linea del fichero   
       data_line = csv_reader.__next__()
       
       
       for row in range(num_stations):
         
           row_line=[]
           for time_distance in range(num_stations):
               data_line = csv_reader.__next__()
               row_line.append(int(float((data_line[2])))) #time_distance is the second element of data_line                      
           distance_matrix.append(row_line)
           ids.append(int(data_line[0]))
        
       osm_data ={'ids':ids,'distance_matrix':distance_matrix }

    return osm_data

def load_stations_data():
    """
    The csv imput file msut have these headers
    StationId;Name;Latitude;Longitude

    Returns
    -------
    stations_data : TYPE
        DESCRIPTION.

    """
    print("load_Stations_data")
    stations_data={}
    file = config.folder + 'stations_lat_lon.csv'
    with open(file, encoding='utf-8') as csv_file:
       csv_reader = csv.reader(csv_file, delimiter=';')
       row_count = 0
       for row in csv_reader:
           row_count = row_count + 1
       csv_file.seek(0)  #retorna  la primera linea del fichero
       data_line = csv_reader.__next__()
       for row in range(row_count-1):
           data_line = csv_reader.__next__()
           stations_data[int(data_line[0])]=(float(data_line[2]), float(data_line[3]))

    # stations_data[id_station]=(lat, lon)
    return stations_data

if __name__ == "__main__":

    #generate_estimated_demands('2022-10-26','19:00-20:00')
    #create_day_data('2022-10-26')
    stations_data = load_stations_data()
    status_data=load_status_data()
    #pred_data=load_pred_data()
    osm_data= load_osm_data()
    #print(osm_data['ids'])
    #print(len(osm_data['ids']))
    #print(pred_data)
    #print(status_data)
    #print(stations_data)
    # file = 'C:/Users/alber/OneDrive - ADIF/Compartido/bikeRelocation/data/osm_stations_duration.csv'
    # m= load_from_file(file)

