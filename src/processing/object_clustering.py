import numpy as np
from sklearn.cluster import DBSCAN # Using DBSCAN for robust clustering

def cluster_detected_points(detected_points_cartesian, eps=0.5, min_samples=3):
    """
    Clusters detected Cartesian points into objects using DBSCAN.

    Args:
        detected_points_cartesian (list): A list of (x, y) tuples representing detected points.
        eps (float): The maximum distance between two samples for one to be considered as in the neighborhood of the other.
        min_samples (int): The number of samples (or total weight) in a neighborhood for a point to be considered as a core point.

    Returns:
        list: A list of lists, where each inner list contains the *indices* of the points
              belonging to a cluster within the original `detected_points_cartesian` list.
              Noise points (label -1) are not included in any cluster list.
    """
    if not detected_points_cartesian:
        return []

    # Convert list of tuples to a NumPy array for DBSCAN
    points_array = np.array(detected_points_cartesian)

    # Apply DBSCAN clustering
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(points_array)
    labels = db.labels_

    # Extract clusters as lists of indices
    unique_labels = set(labels)
    clusters_indices = []
    for k in unique_labels:
        if k == -1:
            # Noise points, ignore for now
            continue
        class_member_mask = (labels == k)
        cluster_point_indices = np.where(class_member_mask)[0].tolist()
        clusters_indices.append(cluster_point_indices)
    
    return clusters_indices

if __name__ == "__main__":
    # Example usage:
    dummy_points = [
        (1.0, 1.0), (1.1, 1.2), (0.9, 1.1), # Cluster 1
        (5.0, 5.0), (5.2, 5.1), (4.9, 5.0), # Cluster 2
        (10.0, 10.0), # Noise point
        (1.0, 1.05),
        (5.05, 5.0)
    ]

    clusters = cluster_detected_points(dummy_points, eps=0.2, min_samples=2)
    print(f"Detected clusters (indices): {clusters}")