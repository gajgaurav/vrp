from parsers.vrp_parser import VRPInstance, VRPSolution
from utils.route_utils import get_route_distance, get_solution_cost

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