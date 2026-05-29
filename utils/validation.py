from dataclasses import dataclass
from typing import Set, List, Dict
from parsers.vrp_parser import VRPInstance
from utils.route_utils import get_route_demand

@dataclass
class ValidationReport:
    '''Container for solution validation results'''
    
    is_feasible : bool
    missing_customers : Set[int]
    duplicate_customers : Set[int]
    capacity_violations : List[Dict]

def get_solution_validation(routes: List[List[int]], instance: VRPInstance) -> ValidationReport:
    '''Check if solution is feasible against instance constraints.
    
    Validates:
      1. All customers visited exactly once (no missing, no duplicates)
      2. Capacity constraints respected on each route
    
    Args:
        routes: List of routes to validate
        instance: VRPInstance with constraints
        
    Returns:
        ValidationReport with feasibility status and detailed errors
    '''
    
    dimension = instance.dimension
    capacity = instance.capacity
    depot_idx = instance.depot_idx
    
    missing_customers = set()
    duplicate_customers = set()
    capacity_violations = []
    
    # Extract all visited customers
    visited = set()
    for route in routes:
        visited.update(route)
    
    # Check all customers visited exactly once
    all_customers = set(range(dimension)) - {depot_idx}
    missing_customers = all_customers - visited
    
    if len(visited) != sum(len(route) for route in routes):
        for idx in range(dimension):
            if idx == depot_idx:
                continue
            count = sum(1 for route in routes if idx in route)
            if count > 1:
                duplicate_customers.add(idx)
    
    # Check capacity constraints
    for route_idx, route in enumerate(routes):
        route_demand = get_route_demand(route, instance)
        if route_demand > capacity:
            capacity_violations.append({'route_idx' : route_idx,
                                        'demand' : route_demand,
                                        'capacity' : capacity})
    
    is_feasible = (len(missing_customers) == 0 and
                   len(duplicate_customers) == 0 and
                   len(capacity_violations) == 0)
    
    return ValidationReport(is_feasible = is_feasible,
                            missing_customers = missing_customers,
                            duplicate_customers = duplicate_customers,
                            capacity_violations = capacity_violations
                            )

def get_validation_report(report: ValidationReport) -> None:
    '''Pretty-print validation report.
    
    Args:
        report: ValidationReport from get_solution_validation()
    '''
    
    if report.is_feasible:
        print('✓ Solution is feasible')
    else:
        print('✗ Solution is infeasible')
        
        if report.missing_customers:
            print(f'  Missing customers: {report.missing_customers}')
        
        if report.duplicate_customers:
            print(f'  Duplicate customers: {report.duplicate_customers}')
        
        if report.capacity_violations:
            print('  Capacity violations:')
            for violation in report.capacity_violations:
                print(f'    Route {violation["route_idx"]}: demand {violation["demand"]} > capacity {violation["capacity"]}')