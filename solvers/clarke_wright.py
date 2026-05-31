from parsers.vrp_parser import VRPInstance, VRPSolution
from utils.route_utils import get_route_demand, get_solution_cost

def get_cw_savings(instance: VRPInstance) -> list:
    '''Compute Clarke-Wright savings for every pair (i,j) of demand nodes.
    
    Savings represents the distance reduction achieved by combining two 
    single-customer routes into one: s_ij = d(D,i) + d(D,j) - d(i,j).
    Larger savings indicate pairs that benefit most from being merged.
    
    Args:
        instance: VRPInstance with distance_matrix, depot_idx
        
    Returns:
        List of tuples [(i, j), savings_value] sorted descending by savings.
        Only includes customer pairs (excludes depot).
    '''
    
    savings = {}
    
    # Compute savings for all customer pairs
    for i in range(instance.depot_idx + 1, len(instance.distance_matrix)):
        for j in range(i + 1, len(instance.distance_matrix)):
            d_D_i = instance.distance_matrix[instance.depot_idx][i]
            d_D_j = instance.distance_matrix[instance.depot_idx][j]
            d_i_j = instance.distance_matrix[i][j]
            
            # Savings formula: distance saved by merging routes
            s_i_j = (2 * (d_D_i + d_D_j)) - (d_D_i + d_i_j + d_D_j)
            savings[(i, j)] = s_i_j

    # Sort by savings value (descending)
    savings = sorted(savings.items(), key = lambda x: x[1], reverse = True)
    return savings

def get_cw_solution(instance: VRPInstance) -> VRPSolution:
    '''Solve VRP using Clarke-Wright Savings Algorithm.
    
    Algorithm:
    1. Initialize: Each customer forms its own single-customer route
    2. Compute savings for all customer pairs (sorted descending)
    3. For each saving in order:
       - If customers are in different routes AND at route endpoints
       - And merged route respects capacity constraint
       - Then merge the two routes
    4. Return final set of routes and total cost
    
    This is a construction heuristic that often produces better solutions 
    than greedy nearest-neighbor, especially on larger instances.
    
    Args:
        instance: VRPInstance with dimension, capacity, demands, distance_matrix
        
    Returns:
        VRPSolution with routes (list of customer lists) and total cost
        
    Note:
        - Starts with single customer routes
        - Routes are merged in order of decreasing savings
        - A customer can only be at a route endpoint (not interior) to enable merging
        - Capacity validation required before finalizing merge
    '''
    
    # CW savings on the distance matrix
    savings = get_cw_savings(instance)
    
    # Initialize: Each customer is its own route
    routes = [[customer_idx] for customer_idx in set(range(instance.dimension)) - {instance.depot_idx}]   
    
    # Iterate through savings in descending order and attempt merges
    for edge_idx in range(len(savings)):
        edge_idx1, edge_idx2 = savings[edge_idx][0]
        
        # Find which route contains each customer
        idx1_route = next((i for i, route in enumerate(routes) if (edge_idx1 in route)))
        idx2_route = next((i for i, route in enumerate(routes) if (edge_idx2 in route)))
        in_different_routes = (idx1_route != idx2_route)
        
        # Check if customers are at route endpoints (required for merging)
        is_idx1_route_start = (routes[idx1_route][0] == edge_idx1)
        is_idx1_route_end = (routes[idx1_route][-1] == edge_idx1)
        is_idx2_route_start = (routes[idx2_route][0] == edge_idx2)
        is_idx2_route_end = (routes[idx2_route][-1] == edge_idx2)
        in_ends = ((is_idx1_route_start or is_idx1_route_end) and (is_idx2_route_start or is_idx2_route_end))
        
        # Attempt merge if conditions satisfied
        if in_different_routes and in_ends:
            route1 = routes[idx1_route]
            route2 = routes[idx2_route]
            
            # Reverse routes if needed so edge_idx1 is at end of route1, edge_idx2 at start of route2
            if route1[0] == edge_idx1:
                route1 = list(reversed(route1))
            
            if route2[-1] == edge_idx2:
                route2 = list(reversed(route2))
            
            # Merge by concatenating: route1 ends at edge_idx1, route2 starts at edge_idx2
            potential_merged_route = route1 + route2
            
            # Only finalize merge if capacity constraint is satisfied,
            # and remove old routes (higher index first to avoid index shifting)
            if get_route_demand(potential_merged_route, instance) <= instance.capacity:
                routes.pop(max(idx1_route, idx2_route))
                routes.pop(min(idx1_route, idx2_route))
                routes.append(potential_merged_route)
    
    cost = get_solution_cost(routes, instance)
    
    return VRPSolution(cost = cost, routes = routes)