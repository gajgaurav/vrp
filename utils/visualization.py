import matplotlib.pyplot as plt
import numpy as np
from parsers.vrp_parser import VRPInstance, VRPSolution

def get_color_palette(n_colors: int, colormap: str = 'hsv'):
    '''Generate n distinct colors from a perceptually uniform colormap
    
    Args:
        n_colors: Number of colors to generate
        colormap: Matplotlib colormap name ('hsv', 'rainbow', 'tab20', 'nipy_spectral', etc.)
        
    Returns:
        List of n_colors RGBA tuples
    '''
    
    cmap = plt.cm.get_cmap(colormap)
    colors = [cmap(i / n_colors) for i in range(n_colors)]
    return colors

def get_solution_visual(instance: VRPInstance, solution: VRPSolution, title: str = None, figsize = (10, 10), colormap: str = 'hsv') -> None:
    '''Visualize VRP solution with routes and nodes.
    
    Displays:
      - Depot as red star
      - Customers as blue circles
      - Routes as colored paths (depot -> route -> depot)
      - Cost in title
    
    Args:
        instance: VRPInstance with coords
        solution: VRPSolution with routes
        title: Custom title (defaults to cost-based title)
        figsize: Figure size tuple
        colormap: Matplotlib colormap name ('hsv', 'rainbow', 'tab20', 'nipy_spectral', etc.)
    '''
    
    fig, ax = plt.subplots(figsize = figsize)
    
    coords = instance.coords
    depot_idx = instance.depot_idx
    routes = solution.routes
    cost = solution.cost
    
    # Generate color palette
    colors = get_color_palette(len(routes), colormap = colormap)
    
    # Plot nodes
    for node_id, (x, y) in coords.items():
        if node_id == depot_idx:
            ax.plot(x, y, 'r*', markersize = 20, label = 'Depot')
        else:
            ax.plot(x, y, 'bo', markersize = 8)
    
    # Plot routes in different colors
    for route_idx, route in enumerate(routes):
        color = colors[route_idx]
        
        nodes_in_path = [depot_idx] + route + [depot_idx]
        x_coords = [coords[node][0] for node in nodes_in_path]
        y_coords = [coords[node][1] for node in nodes_in_path]
        
        ax.plot(x_coords, y_coords, color = color, linewidth = 1.5, alpha = 0.7, label = f'Route {route_idx + 1}')
    
    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    if title is None:
        title = f'{instance.name}: Cost = {cost:.2f}'
    ax.set_title(title)
    
    plt.tight_layout()
    plt.show()