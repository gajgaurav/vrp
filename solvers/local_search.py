import numpy as np
from parsers.vrp_parser import VRPInstance, VRPSolution
from utils.route_utils import get_route_distance, get_solution_cost

def get_2opt_refinements(instance: VRPInstance, solution: VRPSolution) -> VRPSolution:
    '''Improve solution using 2-opt moves (segment reversals).
    
    2-opt reverses a segment of each route and checks if cost improves.
    Iterates until no more improvements found (first-improvement strategy).
    
    Args:
        instance: VRPInstance (for distance_matrix, depot_idx)
        solution: VRPSolution to improve
        
    Returns:
        VRPSolution with improved routes and updated cost
    '''
    
    routes = solution.routes
    improved_routes = []

    for route in routes:
        improved = True
        
        while improved:
            improved = False
            baseline_distance = get_route_distance(route, instance)
            
            for i in range(len(route)):
                for j in range(i + 2, len(route)):
                    left_segment = route[: i + 1]
                    reversed_segment = list(reversed(route[i + 1 : j + 1]))
                    right_segment = route[j + 1 :]
                    
                    alt_route = left_segment + reversed_segment + right_segment
                    alt_distance = get_route_distance(alt_route, instance)
                    
                    if alt_distance < baseline_distance:
                        route = alt_route
                        improved = True
                        break
                
                if improved:
                    break
                
        improved_routes.append(route)
    
    cost = get_solution_cost(improved_routes, instance)
    
    return VRPSolution(cost = cost, routes = improved_routes)