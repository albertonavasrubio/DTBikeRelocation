# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 21:55:02 2024

@author: alberto navas rubio

Optimizacion de la funcion de reocalizacion bicicletas

n vehiculos con ci capacidad de bicieltas cada uno
se trata de recoger bicciletas en una estaccion para llevarlas a otro

parametros:
    tperiodo: (minutos) intervalo de tirmpo para calcular la optimizacion 
              la recogida en una estacion y entrega en otra consume un tiempo
              la suma de tiempos debera ser menor que tperiodo
    
    
variables:
    ci: capacidad actual del vehiculo i
    Ci: capacidad maxima del vehiculo i
    ui: esatacioin actual del vehiculo i
    Ui: estacion inicial del vehiculo i
    

KPI a optimizar:
    Ev: numero de estaciones vacias al final del periodo
    Ell: numero de estaciones llenas al final del periodo
    
Datos de estaciones:
https://opendata-ajuntament.barcelona.cat/data/es/dataset/informacio-estacions-bicing
    
"""

"""Simple Vehicles Routing Problem (VRP).

   This is a sample using the routing library python wrapper to solve a VRP
   problem.
   A description of the problem can be found here:
   http://en.wikipedia.org/wiki/Vehicle_routing_problem.

   Distances are in meters.
   
   
   https://or-tools.github.io/docs/python/index.html
   https://or-tools.github.io/docs/pdoc/ortools.html
   https://developers.google.com/optimization/routing?hl=es-419
   https://acrogenesis.com/or-tools/documentation/documentation_hub.html#user_manual
"""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import initialization
import config

def create_data_model(file,init_station_id=[config.depot_id,config.depot_id]):
    print("create_data_model: file="+ file + ", init_station_id="+ str(init_station_id))
    data = {}
    dict_demands = initialization.generate_estimated_demands(file)
    # dicy_demands = status_data[date][time][station_id] = [n_bikes,n_docks]
    # generate_estimated_demands('2022-10-26','19:00-20:00')
    
    osm_data = initialization.load_osm_data()  # time-distance matrix
    station_pos = osm_data['ids']  # Lista de stations-ids ordenanda segun aparecen en fichero
    station_matrix = osm_data['distance_matrix']
    data["idStations"] = []
    data["demands"] = []
    data["distance_matrix"] = []
    pos_matrix=[]   #Posicion(numero de oreden) de la estacion dentro de la matriz data

    print(dict_demands.keys())

    # Agregamos a la lista de idStations solo las que tienen demanda
    for station in dict_demands.keys():

        if not(dict_demands[station]['demand'] == 0 ) and station in station_pos:
            #Si existe demanda para la estacion crea los elementos correspondientes
            data["idStations"].append(station)
            #print(dict_demands[station]['demand'])
            data["demands"].append(dict_demands[station]['demand'])

            # agrega a la lista de posiciones
            # la posicion de la linea en la que se encuentra la estacion
            pos_matrix.append(station_pos.index(station))
    # agregamos tambien las estaciones de salida

    for station in init_station_id:
        if not (station in data["idStations"]):
            data["idStations"].append(station)
            data["demands"].append(0)
            pos_matrix.append(station_pos.index(station))

        # Correccion realizada ya que si la demanda es negativa nunca se puede satisfacer
        elif data["demands"][data["idStations"].index(station)] < 0:
            prev_demand = data["demands"][data["idStations"].index(station)]
            data["demands"][data["idStations"].index(station)] = 0
    #reconstruimos la matrix distancias solo con las estaciones que se van a explorar
    #que son aquellas en las que hay que retirar o llevar bicicletas

    for pos_line in pos_matrix:
        row =[]
        for pos_column in pos_matrix:
            row.append(station_matrix[pos_line][pos_column])
        data["distance_matrix"].append(row)

    data["vehicle_capacities"] = [15 for i in range(len(init_station_id))]
    data["num_vehicles"] = len(init_station_id)
    
    #lista con el id_posicion de estaciones de origen
    data["starts"] = [data["idStations"].index(init_station_id[i]) for i in range(len(init_station_id))]

    #lista con el id_posicion de las estaciones finales
    #****No se usa en el algoritmo actual***Opcional en el futuro
    data["ends"] = [data["idStations"].index(init_station_id[i]) for i in range(len(init_station_id))]

    return data
def vectors_route(data, manager, routing, solution):
    print("vectors_route: data, manager,routing, solution")
    routes = []
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        route =[]
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            id_index = data["idStations"][manager.IndexToNode(index)]
            station_demand = data["demands"][node_index]
            route_load += data["demands"][node_index]
            index = solution.Value(routing.NextVar(index))
            route.append((id_index, station_demand))
        routes.append(route)
    # routes[team_n:[ stops: [(id_station , station_demand)]]]
    return routes
def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    toprint = f"Objective: {solution.ObjectiveValue()}" +'\n'
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle-team {vehicle_id+1}:\n"
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index =manager.IndexToNode(index)
            id_index= data["idStations"][manager.IndexToNode(index)]
            station_demand= data["demands"][node_index]
            route_load += station_demand
            plan_output += f" {id_index} Demand[{station_demand}] Load({route_load}) -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        node_index =manager.IndexToNode(index)
        plan_output += f" {id_index} Load({route_load})\n"
        plan_output += f"Time(s) of the route: {route_distance}s\n"
        plan_output += f"Load of the route: {route_load}\n"
        toprint=toprint + plan_output +'\n'
        total_distance += route_distance
        total_load += route_load
    toprint=toprint + f"Total time(h) of all routes: {total_distance/3600}h" +'\n'
    toprint=toprint +f"Total load of all routes: {total_load}" + '\n'

    return toprint

def main(file:str = 'capstone_data_20221026_2000_status.csv', initStations:list = [config.depot_id,config.depot_id], time_limit:int = config.maximun_travel_time):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(file,initStations)
    print("create_data_model")
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"],
        data["starts"], data["ends"]
    )
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    
    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
       demand_callback_index,
       0,  # null capacity slack
       data["vehicle_capacities"],  # vehicle maximum capacities
       True,  # start cumul to zero
       "Capacity",
       )

    # Add Distance constraint.
    dimension_name = "Distance"
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack  - Tiempo de espera en cada estacion para las operaciones
       time_limit,  # vehicle maximum travel distance (hay que restar tiempos de operacion)
        True,  # start cumul to zero
        dimension_name,
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(config.SpanCostCoefficient)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    if config.optimization_stretegy == 'PATH_CHEAPEST_ARC':
        search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
    else:
        search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )


    
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    
    # especificar limite de tiempo de busqueda
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.time_limit.seconds = config.search_time_limit
    
    # especificar limite masximo de soluciones
    search_parameters.solution_limit = config.solution_limit

    # Allow to drop nodes.
    penalty = 1000000000000
    #print(len(data["idStations"]))
    #print(len(data["distance_matrix"]))

    for node in range(0,len(data["distance_matrix"])):
        if not(node in data["starts"]):
            #print(node)
            #no se puede incluir ni el nodo final ni el inicial de cada vehiculo
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
    
    # print(search_parameters)
    # Solve the problem.
    sol = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if sol:
        toprint = print_solution(data, manager, routing, sol)
        vector = vectors_route(data, manager, routing, sol)
        #print(data["demands"])

        return vector, toprint
    else:
        return [], "No solution found !"

if __name__ == "__main__":

    from QgisScripts import refres_stations_data


    from capture_json import download_data
    item = download_data()

    time_text = item[0:4] + item[5:7] + item[8:10] + '_' + item[11:13] + item[14:16]
    file_name = "capstone_data_" + time_text + "_status.csv"
    print(file_name)
    data = initialization.generate_estimated_demands(file_name)
    solve, printSolve = main(initStations=[1000,423],time_limit=5000,file=file_name)
    KPIs = refres_stations_data(solve_data=solve,data=data, batch = True)
    print(printSolve)
    print(KPIs)
