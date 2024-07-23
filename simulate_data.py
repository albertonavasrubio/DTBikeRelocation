# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 16:18:25 2024
@author: alberto navas rubio

Temporal module for extrating historic data and put it in format for the DT
"""

import csv
import config


def generate_simulate_time_distance(id_origen, id_destino):
    #generates stimate time travel between

    return time_distance
def generate_status_day_data(fileName='capstone_data_20220701-20221231_status.csv', date = '2022-10-06'):
    """
    format input csv:
        date,time,station_id,n_bikes_available,n_docks_available
    """
    file = config.folder + fileName
    status_data = {}
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        row_count = sum(1 for row in csv_reader)
        csv_file.seek(0)  # retorna  la primera linea del fichero
        data_line = csv_reader.__next__()  #salta la primera linea que es de nombre de campos
        data_line = csv_reader.__next__()
        date = data_line[0]
        status_data[date] = {}
        time = data_line[1]
        status_data[date][time] = {}
        station_id = int(data_line[2])
        n_bikes = int(data_line[3])
        n_docks = int(data_line[4])
        status_data[date][time][station_id] = [n_bikes, n_docks]
        for row in range(row_count - 2):
            data_line = csv_reader.__next__()
            date = data_line[0]
            time = data_line[1]
            station_id = int(data_line[2])
            n_bikes = int(data_line[3])
            n_docks = int(data_line[4])
            if not (date in status_data.keys()):
                status_data[date] = {}
            if not (time in status_data[date].keys()):
                status_data[date][time] = {}
            status_data[date][time][station_id] = [n_bikes, n_docks]

    date = '2022-10-26'
    #date,time,station_id,n_bikes_available,n_docks_available
    #2022-07-01,00:00,77,19,2
    print(date)
    date_=date[0:4] + date[5:7] + date[8:10]
    for time in status_data[date].keys():
        time_text = time[0:2]+time[3:5]
        write_file = config.path_to_pronostic_files + 'capstone_data_' + date_ + '_' + time_text+ '_status.csv'
        with open(write_file, 'w') as file:
            file.writelines('date,time,station_id,n_bikes_available,n_docks_available\n')
            for station in status_data[date][time].keys():
                line = date + ',' + time + ',' + str(station) + ',' + str(status_data[date][time][station][0]) +',' + str(status_data[date][time][station][1])+ '\n'
                file.writelines(line)

    times = list(status_data[date].keys())
    print(times)
    for i, time in enumerate(times[0:-1]):
        pred_file = config.path_to_pronostic_files + 'capstone_data_pred_processed_' + date_ + '_' + time[0:2] + time[3:5] +  '.csv'
        with open(pred_file, 'w') as predfile:
            predfile.writelines('date,period,station_id,delta_bikes\n')
            period = times[i] + '-' + times[i+1]
            for station in status_data[date][time].keys():
                    delta = status_data[date][times[i+1]][station][0] - status_data[date][time][station][0]
                    line = date + ',' + period + ',' + str(station) + ',' + str(delta) +'\n'
                    predfile.writelines(line)
        return 0

if __name__ == "__main__":
    generate_status_day_data(date='2022-10-06')