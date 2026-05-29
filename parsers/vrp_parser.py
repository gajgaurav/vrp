import os
import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List
 
@dataclass
class VRPInstance:
    
    '''Container for VRP instance data'''
    
    name : str
    dimension : int
    capacity : int
    coords : Dict[int, Tuple[float, float]]
    demands : Dict[int, int]
    depot_idx : int
    distance_matrix : np.ndarray
    edge_weight_type : str
 
@dataclass
class VRPSolution:
    
    '''Container for VRP solution data'''
    
    cost : float
    routes : List[List[int]]

def get_vrp_attribute(attribute, info, splitter = ':'):
    
    '''Fetches single row VRP attributes (case-insensitive) and their associated index'''
    
    attribute_idx = [i for i, line in enumerate(info) if attribute.lower() in line.lower()][0]
    attribute = info[attribute_idx].split(splitter)[-1].strip().lower()
    return attribute_idx, attribute

def parse_vrp_instance(vrp_filepath):
    
    '''Parses TSPLIB95 format VRP instances'''
    
    with open(vrp_filepath, 'r') as f:
        vrp_lines = f.readlines()
    vrp_lines = [line.split('\n')[0].strip().replace('\t', ' ') for line in vrp_lines if line.strip()]

    problem_attributes = {}
    for attribute in ['name', 'type', 'dimension', 'capacity', 'edge_weight_type']:
        problem_attributes[attribute] = get_vrp_attribute(attribute, vrp_lines)[1]

    if problem_attributes['type'].lower() != 'cvrp':
        raise ValueError(f'Problem type must be CVRP, got {problem_attributes["type"]}')

    demand_section_idx = get_vrp_attribute('demand_section', vrp_lines)[0]
    depot_section_idx = get_vrp_attribute('depot_section', vrp_lines)[0]

    try:
        coord_section_idx = get_vrp_attribute('node_coord_section', vrp_lines)[0]
        
        # Extract node coordinates (0-indexed)
        coords = {}
        for coord_info in vrp_lines[coord_section_idx + 1 : demand_section_idx]:
            coord_idx, coord_x, coord_y = coord_info.split(' ')
            coords[int(coord_idx) - 1] = (float(coord_x), float(coord_y))
    except:
        raise ValueError(f'No node coordinate section found in {vrp_filepath}')

    # Extract customer demands (0-indexed)
    demands = {}
    for demand_info in vrp_lines[demand_section_idx + 1 : depot_section_idx]:
        demand_idx, demand = demand_info.split(' ')
        demands[int(demand_idx) - 1] = int(demand)
        
    # Extract depot location (0-indexed) and verify 0-demand
    depot_idx = int(vrp_lines[depot_section_idx + 1]) - 1
    assert demands[depot_idx] == 0, f"Depot {depot_idx} must have demand 0, got {demands[depot_idx]}"

    # Extract edge information
    distance_matrix = None
    dimension = int(problem_attributes['dimension'])
    
    try:
        edge_weight_type = problem_attributes['edge_weight_type']
    except:
        raise ValueError('Edge weight type is required but not found in problem file')

    if edge_weight_type == 'explicit':
        raise ValueError('Explicit edge weight handling not part of current functionality.')
    elif edge_weight_type == 'euc_2d':
        coords_array = np.array([coords[i] for i in range(dimension)])
        distance_matrix = np.sqrt(((coords_array[:, np.newaxis, :] - coords_array[np.newaxis, :, :]) ** 2).sum(axis = 2))
    else:
        raise ValueError(f'Edge weight type must be either euc_2d or explicit, got {edge_weight_type}')

    instance = VRPInstance(name = problem_attributes['name'],
                           dimension = int(problem_attributes['dimension']),
                           capacity = int(problem_attributes['capacity']),
                           coords = coords,
                           demands = demands,
                           depot_idx = depot_idx,
                           distance_matrix = distance_matrix,
                           edge_weight_type = edge_weight_type
                          )
                    
    return instance

def parse_vrp_solution(sol_filepath):

    '''Parses TSPLIB95 format VRP solutions'''
    
    with open(sol_filepath, 'r') as f:
        sol_lines = f.readlines()
        
    sol_lines = [line.split('\n')[0].strip().replace('\t', ' ') for line in sol_lines if line.strip()]
    sol_cost = float(get_vrp_attribute('cost', sol_lines, ' ')[1])
    sol_routes = [line.split(': ')[1].split() for line in sol_lines if 'route' in line.lower()]
    sol_routes = [np.array(sol_route, dtype = int).tolist() for sol_route in sol_routes]

    solution = VRPSolution(cost = sol_cost, routes = sol_routes)
    
    return solution