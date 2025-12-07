import matplotlib.pyplot as plt
import numpy as np
import os
from src.config import constants

def create_2d_map(all_detected_points_cartesian, clusters=None, title="2D Radar Map", map_extent_m=10, grid_resolution=0.1):
    """
    Creates a 2D map of detected radar targets in Cartesian coordinates, with optional clustering.

    Args:
        all_detected_points_cartesian (list): A list of (x, y) tuples representing detected points.
        clusters (list, optional): A list of lists, where each inner list contains indices
                                   of points belonging to a cluster. Defaults to None.
        title (str): The title of the plot.
    """
    if not all_detected_points_cartesian:
        print("No targets to display on the 2D map.")
        return

    x_coords = [p[0] for p in all_detected_points_cartesian]
    y_coords = [p[1] for p in all_detected_points_cartesian]

    plt.figure(figsize=(10, 10))

    # Plot all detected points
    plt.scatter(x_coords, y_coords, c='blue', marker='.', label='Detected Points', alpha=0.6)

    # Plot clusters if provided
    if clusters:
        colors = plt.cm.get_cmap('tab10', len(clusters)) # Get a colormap for clusters
        for i, cluster_indices in enumerate(clusters):
            cluster_x = [x_coords[j] for j in cluster_indices]
            cluster_y = [y_coords[j] for j in cluster_indices]
            plt.scatter(cluster_x, cluster_y, color=colors(i), marker='o', s=100,
                        edgecolor='black', label=f'Cluster {i+1}')

    plt.xlabel("X-coordinate (m)")
    plt.ylabel("Y-coordinate (m)")
    plt.title(title)
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.legend(loc='upper right') # Ensure legend is clearly visible
    plt.axis('equal') # Ensure equal scaling for x and y axes
    
    # Set plot limits based on map_extent_m
    plt.xlim(-map_extent_m / 2, map_extent_m / 2)
    plt.ylim(0, map_extent_m) # Assuming radar looks forward, so y is positive
    
    # Save the plot
    output_path = os.path.join(constants.PLOTS_OUTPUT_DIR, "2d_radar_map.png")
    plt.savefig(output_path)
    print(f"2D Radar Map saved to {output_path}")
    plt.show()

if __name__ == '__main__':
    # Example usage:
    sample_points = [
        (1, 2), (1.2, 2.1), (0.9, 1.9),
        (5, 6), (5.3, 6.1), (4.8, 5.9),
        (-2, 3), (-2.3, 3.2)
    ]
    sample_clusters = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7]
    ]
    create_2d_map(sample_points, sample_clusters, "Sample 2D Radar Map with Clusters")

    # Example without clusters
    create_2d_map(sample_points, title="Sample 2D Radar Map (No Clusters)")