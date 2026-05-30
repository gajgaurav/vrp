from parsers.vrp_parser import VRPInstance, VRPSolution
from utils.route_utils import get_route_demand, get_solution_cost

def get_cw_savings(instance: VRPInstance) -> list:
    '''Compute Clarke-Wright savings for every pair (i,j) of demand nodes.'''
    
    savings = {}
    for i in range(instance.depot_idx + 1, len(instance.distance_matrix)):
        for j in range(i + 1, len(instance.distance_matrix)):
            d_D_i = instance.distance_matrix[instance.depot_idx][i]
            d_D_j = instance.distance_matrix[instance.depot_idx][j]
            d_i_j = instance.distance_matrix[i][j]
            s_i_j = (2 * (d_D_i + d_D_j)) - (d_D_i + d_i_j + d_D_j)
            savings[(i, j)] = s_i_j

    savings = sorted(savings.items(), key = lambda x: x[1], reverse = True)
    return savings

def get_cw_solution(instance: VRPInstance) -> VRPSolution:
    '''Get Clark-Wright routes based on savings from merges.'''
    
    savings = get_cw_savings(instance)
    routes = [[customer_idx] for customer_idx in set(range(instance.dimension)) - {instance.depot_idx}]   
    
    for edge_idx in range(len(savings)):
        edge_idx1, edge_idx2 = savings[edge_idx][0]
        
        idx1_route = next((i for i, route in enumerate(routes) if (edge_idx1 in route)))
        idx2_route = next((i for i, route in enumerate(routes) if (edge_idx2 in route)))
        in_different_routes = (idx1_route != idx2_route)
        
        is_idx1_route_start = (routes[idx1_route][0] == edge_idx1)
        is_idx1_route_end = (routes[idx1_route][-1] == edge_idx1)
        is_idx2_route_start = (routes[idx2_route][0] == edge_idx2)
        is_idx2_route_end = (routes[idx2_route][-1] == edge_idx2)
        in_ends = ((is_idx1_route_start or is_idx1_route_end) and (is_idx2_route_start or is_idx2_route_end))
        
        if in_different_routes and in_ends:
            route1 = routes[idx1_route]
            route2 = routes[idx2_route]
            
            if route1[0] == edge_idx1:
                route1 = list(reversed(route1))
            
            if route2[-1] == edge_idx2:
                route2 = list(reversed(route2))
            
            potential_merged_route = route1 + route2
            
            if get_route_demand(potential_merged_route, instance) > instance.capacity:
                pass
            else:
                routes.pop(max(idx1_route, idx2_route)) # Remove higher index element first
                routes.pop(min(idx1_route, idx2_route))
                routes.append(potential_merged_route)
    
    cost = get_solution_cost(routes, instance)
    
    return VRPSolution(cost = cost, routes = routes)