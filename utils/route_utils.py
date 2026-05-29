import numpy as np
from typing import List
from parsers.vrp_parser import VRPInstance

def get_route_distance(route: List[int], instance: VRPInstance) -> float:
    '''Compute total distance of a route: depot -> route -> depot'''
    
    total_distance = 0
    current_idx = instance.depot_idx
    for idx in route:
        total_distance = total_distance + instance.distance_matrix[current_idx][idx]
        current_idx = idx
    total_distance = total_distance + instance.distance_matrix[current_idx][instance.depot_idx]
    return total_distance

def get_route_demand(route: List[int], instance: VRPInstance) -> float:
    '''Compute total demand on a route'''
    
    return sum(instance.demands[node] for node in route)

def is_route_feasible(route: List[int], instance: VRPInstance) -> bool:
    '''Check if route respects capacity constraint'''
    
    route_demand = get_route_demand(route, instance)
    return route_demand <= instance.capacity

def get_solution_cost(routes: List[List[int]], instance: VRPInstance) -> float:
    '''Compute total cost of all routes'''
    
    total_cost = 0
    for route in routes:
        total_cost = total_cost + get_route_distance(route, instance)
    return total_cost