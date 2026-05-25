import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class VRPInstance:
    
    '''Represents a complete VRP instance.'''
    
    name            : str
    dimension       : int
    capacity        : int
    depot           : int
    coords          : Dict[int, Tuple[float, float]]
    demands         : Dict[int, int]
    distance_matrix : np.ndarray

def parse_vrp_instance(filepath: str) -> VRPInstance:
    
    '''
    Parse a TSPLIB format VRP file (.vrp).
    
    Args:
        filepath: Path to .vrp file
    
    Returns:
        VRPInstance with all parsed data
    '''
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    lines = [line.split('\n')[0].strip() for line in lines if line.strip()]
    
    # Parse metadata
    name      = lines[0].split(': ')[1].strip()
    dimension = int(lines[3].split(': ')[1].strip())
    capacity  = int(lines[5].split(': ')[1].strip())
    
    # Find section indices
    coord_section_idx_start  = [i for i, line in enumerate(lines) if 'NODE_COORD_SECTION' in line][0]
    demand_section_idx_start = [i for i, line in enumerate(lines) if 'DEMAND_SECTION' in line][0]
    depot_section_idx_start  = [i for i, line in enumerate(lines) if 'DEPOT_SECTION' in line][0]
    
    # Parse coordinates
    coords = {}
    for coord_info in lines[coord_section_idx_start + 1 : demand_section_idx_start]:
        if coord_info:
            coord_idx, coord_x, coord_y = coord_info.split()
            coords[int(coord_idx)] = (float(coord_x), float(coord_y))
    
    # Parse demands
    demands = {}
    for demand_info in lines[demand_section_idx_start + 1 : depot_section_idx_start]:
        if demand_info:
            demand_idx, demand = demand_info.split()
            demands[int(demand_idx)] = int(demand)
    
    # Parse depot
    depot = int(lines[depot_section_idx_start + 1])
    
    # Build distance matrix
    distance_matrix = np.zeros([dimension + 1, dimension + 1])
    for i in range(1, dimension + 1):
        for j in range(1, dimension + 1):
            distance_matrix[i][j] = np.sqrt((coords[i][0] - coords[j][0])**2 +  (coords[i][1] - coords[j][1])**2)
    
    return VRPInstance(name            = name,
                       dimension       = dimension,
                       capacity        = capacity,
                       depot           = depot,
                       coords          = coords,
                       demands         = demands,
                       distance_matrix = distance_matrix
                     )