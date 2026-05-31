from parsers.vrp_parser import VRPInstance, VRPSolution
from utils.route_utils import get_route_distance, get_solution_cost, get_route_demand

def get_2opt_refinements(instance: VRPInstance, solution: VRPSolution) -> VRPSolution:
    '''Improve solution using 2-opt local search (segment reversals).
    
    2-opt reverses a segment of a route and checks if the resulting cost improves. 
    Under Euclidean distances, reversing a segment is equivalent to uncrossing edges.
    
    Algorithm (per-route):
    1. Assume no improvement found (improved = False)
    2. Scan all possible segment reversals [i, j]
    3. If improvement found: accept it, set improved=True, restart scan with new route
    4. If no improvement found in full scan: exit while loop, move to next route
    5. Repeat until reaching local optimum (no single 2-opt move improves cost)
    
    Control flow:
    - While loop continues as long as improved=True (found improvement last scan)
    - When full (i,j) scan finds nothing, improved stays False
    - While loop exits, fully-improved route is appended
    - First-improvement strategy: accept first improvement (in j loop), don't search for best
    
    Args:
        instance: VRPInstance with distance_matrix, depot_idx
        solution: VRPSolution to improve
        
    Returns:
        VRPSolution with improved routes and updated total cost.
        Routes may be identical to input if no improvements possible.
    '''
    
    routes = solution.routes
    improved_routes = []

    # Improve each route independently
    for route in routes:
        improved = True
        
        # Keep iterating while improvements are found in last scan
        while improved:
            improved = False
            baseline_distance = get_route_distance(route, instance)
            
            # Try all possible segment reversals
            for i in range(len(route)):
                for j in range(i + 2, len(route)):
                    # Create alternative route by reversing segment [i+1, j]
                    left_segment = route[: i + 1]                               # Up to and including i
                    reversed_segment = list(reversed(route[i + 1 : j + 1]))     # Reverse segment [i+1, j]
                    right_segment = route[j + 1 :]                              # After j
                    
                    alt_route = left_segment + reversed_segment + right_segment
                    alt_distance = get_route_distance(alt_route, instance)
                    
                    # Accept first j improvement
                    if alt_distance < baseline_distance:
                        route = alt_route               # Update route with improvement
                        improved = True                 # Signal to continue while loop
                        break                           # Exit j loop, restart with new route
                
                # If improvement found, exit i loop to restart full (i,j) scan
                if improved:
                    break
        
        # While loop exited: no improvements found in full scan, route is locally optimal
        improved_routes.append(route)
    
    cost = get_solution_cost(improved_routes, instance)
    
    return VRPSolution(cost = cost, routes = improved_routes)

def get_relocate_refinements(instance: VRPInstance, solution: VRPSolution) -> VRPSolution:
    '''Improve solution by relocating single nodes between routes.
    
    Relocate moves a single node from one route to the best position in another route.
    Uses best-improvement strategy: scan all possible relocations, apply the best one found.
    
    Algorithm:
    1. For each full scan of all possible relocations:
    2.   Track the best relocation found (lowest cost)
    3.   After scan completes, apply the best relocation
    4.   If improvement found, restart scan with new solution
    5. Exit when a full scan finds no improvements
    
    Args:
        instance: VRPInstance with distance_matrix, capacity, demands
        solution: VRPSolution to improve
        
    Returns:
        VRPSolution with improved routes and updated cost
        
    Note:
        - Best-improvement strategy: scan all options, apply the best
        - Operates across routes (unlike 2-opt which improves within routes)
    '''
    
    optimal_cost = solution.cost
    routes = solution.routes
    improved = True
    
    # Keep iterating while improvements found in last scan
    while improved:
        improved = False

        # Track best move found in this full scan
        best_move_src_idx = None
        best_move_target_idx = None
        best_move_src_route = None
        best_move_temp_target_route = None
        
        # Try relocating each node in each route
        for src_route_idx in range(len(routes)):
            src_route = routes[src_route_idx].copy()
            
            for src_node_idx in range(len(src_route)):
                src_node = src_route[src_node_idx]
            
                # Try moving this node to every other route
                for target_route_idx in range(len(routes)):
                    target_route = routes[target_route_idx].copy()
                    if src_route_idx == target_route_idx:
                        continue
                    
                    # Try every position in the target route
                    # Note: The + 1 allows to go till the end of the target_route.
                    #       At that point, target_route[target_node_idx :] = [], so no error is thrown up.
                    for target_node_idx in range(len(target_route) + 1):
                        temp_src_route = src_route.copy()
                        temp_src_route.pop(src_node_idx)
                        
                        temp_target_route = target_route[: target_node_idx] + [src_node] + target_route[target_node_idx :]
                        temp_demand = get_route_demand(temp_target_route, instance)
                        
                        # Check capacity feasibility
                        if temp_demand <= instance.capacity:
                        
                            temp_routes = routes.copy()
                            temp_routes[src_route_idx] = temp_src_route.copy()
                            temp_routes[target_route_idx] = temp_target_route.copy()
                            
                            temp_cost = get_solution_cost(temp_routes, instance)
                            
                            # Track best improvement found
                            if temp_cost < optimal_cost:
                                improved = True
                                optimal_cost = temp_cost

                                best_move_src_idx = src_route_idx
                                best_move_target_idx = target_route_idx
                                best_move_src_route = temp_src_route.copy()
                                best_move_temp_target_route = temp_target_route.copy()
                                
        # Apply best move found after full scan completes
        if improved:
            routes[best_move_src_idx] = best_move_src_route
            routes[best_move_target_idx] = best_move_temp_target_route
                
    cost = get_solution_cost(routes, instance)
    return VRPSolution(cost = cost, routes = routes)