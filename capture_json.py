# -*- coding: utf-8 -*-
"""
Created on Fri may  5 23:10:44 2024

@author: alberto navas rubio
@mail: alberto.navas@adif.es

files with config installation parameters
"""


import config
import requests
from datetime import datetime


def download_data():
    print("download_data")
    resp = requests.get(config.gbfs_server)
    resp_dict = resp.json()

    last_updated = resp_dict['last_updated']
    dt = str(datetime.fromtimestamp(last_updated, tz=None))
    station_data = resp_dict['data']['stations']
    print(dt)
    date = dt[0:10]
    time = dt[11:16]

    text_data = dt[0:4]+dt[5:7]+dt[8:10]+'_'+dt[11:13]+dt[14:16]
    file_name = config.path_to_status_files + 'capstone_data_'+text_data+'_status.csv'
    with open(file_name, 'w') as file:
        file.writelines('date,time,station_id,n_bikes_available,n_docks_available\n')
        for station in station_data:
            #date,time,station_id,n_bikes_available,n_docks_available
            station_id = station['station_id']
            n_bikes_available = station['num_bikes_available']
            n_docks_available = station['num_docks_available']
            row_line = date + ',' + time + ',' + str(station_id) + ',' + str(n_bikes_available) + ','+ str(n_docks_available) +'\n'
            file.writelines(row_line)

    return dt