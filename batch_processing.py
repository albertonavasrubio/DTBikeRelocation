import sys

import config
import Optimization
import initialization
from QgisScripts import refres_stations_data

# st = [37,56,79,401,405]


# Analys number of bikes needed to perform total KPI under required parameter
def number_bikes(kmax:float = 0.01, t:int =4000, files:list =['capstone_data_20221026_1900_status.csv'] ):
    global st
    stations = initialization.load_stations_data()
    st = list(stations.keys())
    kpi = [1.0, 1.0]
    for file in files:
        data = initialization.generate_estimated_demands(file)
        for station in st[98:]:
            #start with 8 vehicles
            start_stations = [station for i in range(2)]
            while (kpi[1]>kmax) and len(start_stations) <21:
                start_stations.append(station)
                solve, printSolve = Optimization.main(file=file,initStations=start_stations,time_limit=t)
                KPIs = refres_stations_data(solve_data=solve, data=data, batch=True)
                kpi[0]=KPIs[2]/KPIs[0]
                kpi[1]=KPIs[4]/KPIs[0]

            with open('c:/temp/prueba2.txt', 'a') as f:
                f.write(str(station))
                for i in KPIs:
                    f.write(';' + str(i))
                f.write(';' + str(len(start_stations)))
                f.write('\n')
            kpi = [1.0, 1.0]

            print("********Total number of vehicles: " + str(len(start_stations)) + '  in station: ' + str(station))


#Analys number of bikes neede to perform total KPI under required parameter
def time_bikes(kmax:float = 0.01, vehicles:int =8, files:list =['capstone_data_20221026_1900_status.csv'] ):
    global st
    stations = initialization.load_stations_data()
    kpi = [1.0, 1.0]
    time_d = 0
    st = [5] #list(stations.keys())
    for file in files:
        data = initialization.generate_estimated_demands(file)
        for station in st:  # list(stations.keys())[20:]:
            # start with 8 vehicles
            start_stations = [station for i in range(vehicles)]
            while (kpi[1] > kmax) and time_d < 10000:
                time_d = time_d + 450 #increase of 15'
                solve, printSolve = Optimization.main(file=file, initStations=start_stations, time_limit=time_d)
                KPIs = refres_stations_data(solve_data=solve, data=data, batch=True)
                kpi[0] = KPIs[2] / KPIs[0]
                kpi[1] = KPIs[4] / KPIs[0]


            with open('c:/temp/prueba3.txt', 'a') as f:
                f.write(str(station))
                for i in KPIs:
                    f.write(';' + str(i))
                f.write(';' + str(time_d))
                f.write('\n')
            kpi = [1.0, 1.0]
            time_d = 0
            print("********Total number of vehicles: " + str(len(start_stations)) + '  in station: ' + str(station))
def kpis_bikes(vehicles:int = 8, t:int =4000, files:list =['capstone_data_20221026_1900_status.csv'] ):
    global st
    stations = initialization.load_stations_data()
    st = list(stations.keys())
    kpi = [1.0, 1.0]
    for file in files:
        file_name = config.path_to_proccesing_files + file[0:27] + '_Kpis_veh_' + str(vehicles) + '_time_' + str(
            t) + '.csv'
        with open(file_name, 'w') as f:
            f.write(
                'stationID;num_stations;ini_No_bikes;end_No_bikes;ini_No_docks;end_No_docks;KpiResult;numvehicles;TimeNeeded\n')

        data = initialization.generate_estimated_demands(file)

        for station in st[:99]:
            #start with 8 vehicles
            start_stations = [station for i in range(vehicles)]
            solve, printSolve = Optimization.main(file=file,initStations=start_stations,time_limit=t)
            KPIs = refres_stations_data(solve_data=solve, data=data, batch=True)
            kpi[0]=KPIs[2]/KPIs[0]
            kpi[1]=KPIs[4]/KPIs[0]

            with open(file_name, 'a') as f:
                f.write(str(station))
                for i in KPIs:
                    f.write(';' + str(i))
                f.write(';' + str(kpi[0]))
                f.write(';' + str(vehicles))
                f.write(';' + str(t))
                f.write('\n')
            kpi = [1.0, 1.0]





def time_kpi(depot:int = 34, vehicles:int =8, files:list =['capstone_data_20221026_1900_status.csv']):
    stations = initialization.load_stations_data()
    kpi = [1.0, 1.0]
    time_d = 0
    st = [5]  # list(stations.keys())
    for file in files:
        file_name = config.path_to_proccesing_files + file[0:27]+ '_Time_KPI_Veh_'+str(vehicles) + '_depot_'+str(depot)+'.csv'
        with open(file_name, 'w') as f:
            f.write('stationID;num_stations;ini_No_bikes;end_No_bikes;ini_No_docks;end_No_docks;KpiObjetive;numvehicles;TimeNeeded\n')
        data = initialization.generate_estimated_demands(file)
        for kmax in [ 0.01 - 0.01*(value) for value in range(2)]:  # list(stations.keys())[20:]:
            # start with 8 vehicles
            start_stations = [depot for i in range(vehicles)]
            KPIs=[]
            while (kpi[0] > kmax) and time_d < 12000:
                time_d = time_d + 300  # increase of 5'
                solve, printSolve = Optimization.main(file=file, initStations=start_stations, time_limit=time_d)
                KPIs = refres_stations_data(solve_data=solve, data=data, batch=True)
                kpi[0] = KPIs[2] / KPIs[0]
                kpi[1] = KPIs[4] / KPIs[0]

            with open(file_name ,'a') as f:
                f.write(str(depot))
                for i in KPIs:
                    f.write(';' + str(i))
                f.write(';' + str(kmax))
                f.write(';' + str(vehicles))
                f.write(';' + str(time_d))
                f.write('\n')
            kpi = [1.0, 1.0]
            time_d = 0
            print("********Total time: " + str(time_d))


if __name__ == "__main__":
    # number_bikes()
   # time_bikes()
   # time_kpi()
    kpis_bikes()
