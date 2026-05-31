import numpy as np
from utils.route_utils import get_solution_cost
from parsers.vrp_parser import VRPInstance, VRPSolution

def get_nn_solution(instance: VRPInstance) -> VRPSolution:
    '''Solve VRP using Nearest Neighbor heuristic.
    
    Constructs routes greedily by always adding the nearest feasible customer
    to the current route. When no more customers can fit, starts a new route.
    
    Algorithm:
    1. Initialize: all customers unvisited, empty routes
    2. Build routes: for each route, repeatedly add nearest unvisited customer
    3. Feasibility: customer must fit capacity, distance must be minimal
    4. Termination: when no more customers fit, start new route
    5. Stop: when all customers assigned
    
    Args:
        instance: VRPInstance with distance_matrix, demands, capacity, depot_idx
        
    Returns:
        VRPSolution with routes and total cost
    '''
    
    routes = []
    unvisited = set(range(0, instance.dimension)) - {instance.depot_idx}
    
    # Build routes until all customers assigned
    while len(unvisited) > 0:
        route = []
        current_idx = instance.depot_idx
        route_capacity = instance.capacity
        
        # Fill current route with nearest feasible customers
        while len(unvisited) > 0:
            closest_idx = None
            closest_distance = np.inf
            
            # Find nearest unvisited customer that fits capacity
            for idx in unvisited:
                idx_distance = instance.distance_matrix[current_idx][idx]
                idx_demand = instance.demands[idx]
                
                # Check feasibility (capacity) and optimality (distance)
                if route_capacity - idx_demand >= 0:
                    if idx_distance < closest_distance:
                        closest_idx = idx
                        closest_distance = idx_distance
            
            # Add customer to route if found, otherwise start new route
            if closest_idx is not None:
                route.append(closest_idx)
                route_capacity = route_capacity - instance.demands[closest_idx]
                unvisited = unvisited - {closest_idx}
                current_idx = closest_idx
            else:
                break  # No more customers fit in current route
        
        routes.append(route)
    
    cost = get_solution_cost(routes, instance)
    
    return VRPSolution(cost = cost, routes = routes)