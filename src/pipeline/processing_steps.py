import numpy as np
import pandas as pd
from src.data_acquisition.imu_reader import read_imu_data
from src.fusion.imu_fusion import estimate_orientation
from src.processing.radar_fft import perform_fft, polar_to_cartesian, correct_for_imu_orientation
from src.processing.cfar_detection import cfar_ca
from src.config.constants import CFAR_NUM_TRAINING_CELLS, CFAR_NUM_GUARD_CELLS, CFAR_P_FA, MAX_RANGE_M
from src.visualization.map_viewer import plot_raw_imu_data, plot_imu_orientation

def process_imu_data(imu_file_path):
    """
    Loads and processes IMU data to estimate orientation.

    Args:
        imu_file_path (str): Path to the IMU data file.

    Returns:
        pd.DataFrame: IMU data with orientation estimates, or None if processing fails.
    """
    if not imu_file_path:
        return None

    df_imu = read_imu_data(imu_file_path)
    if df_imu is None:
        print("IMU data could not be loaded.")
        return None

    imu_dt = (df_imu['timestamp'].iloc[1] - df_imu['timestamp'].iloc[0]) if len(df_imu) > 1 else 0.01
    imu_data_with_orientation = estimate_orientation(df_imu.copy(), dt=imu_dt)
    
    print("\nEstimated IMU Orientation (first 5 rows):")
    print(imu_data_with_orientation[['timestamp', 'roll', 'pitch']].head())
    
    plot_raw_imu_data(df_imu)
    plot_imu_orientation(imu_data_with_orientation)
    
    return imu_data_with_orientation

def process_radar_frames(df_radar, imu_data_with_orientation):
    """
    Processes radar frames to detect points using FFT and CFAR.

    Args:
        df_radar (pd.DataFrame): DataFrame containing radar data.
        imu_data_with_orientation (pd.DataFrame): DataFrame with IMU orientation data.

    Returns:
        tuple: Tuple containing lists of detected points in Cartesian and polar coordinates,
               and data for the first frame's CFAR visualization.
    """
    radar_columns = [col for col in df_radar.columns if col.startswith('f0_f0_')]
    if not radar_columns:
        print("Error: No radar data columns found.")
        return [], [], None

    all_detected_points_cartesian = []
    all_detected_points_polar = []
    first_frame_viz_data = {}

    for index, row in df_radar.iterrows():
        raw_radar_profile = row[radar_columns].values.astype(float)
        range_profile = perform_fft(raw_radar_profile)
        range_bins = np.linspace(0, MAX_RANGE_M, len(range_profile))
        
        detections = cfar_ca(range_profile, CFAR_NUM_TRAINING_CELLS, CFAR_NUM_GUARD_CELLS, CFAR_P_FA)
        detected_indices = np.where(detections)[0]

        if index == 0:
            first_frame_viz_data['range_profile'] = range_profile
            first_frame_viz_data['detected_indices'] = detected_indices
            # Calculate CFAR threshold for visualization
            cfar_threshold_values = np.zeros_like(range_profile)
            N = 2 * CFAR_NUM_TRAINING_CELLS
            alpha = N * (CFAR_P_FA**(-1/N) - 1)
            offset = CFAR_NUM_TRAINING_CELLS + CFAR_NUM_GUARD_CELLS
            for i in range(len(range_profile)):
                if i >= offset and i < len(range_profile) - offset:
                    sum_training_cells = np.sum(range_profile[i - offset : i - CFAR_NUM_GUARD_CELLS]) + \
                                         np.sum(range_profile[i + CFAR_NUM_GUARD_CELLS + 1 : i + offset + 1])
                    noise_estimate = sum_training_cells / N
                    cfar_threshold_values[i] = alpha * noise_estimate
                else:
                    cfar_threshold_values[i] = np.nan
            first_frame_viz_data['cfar_threshold'] = cfar_threshold_values

        azimuth_angle_rad = (index / len(df_radar)) * np.pi
        current_roll_rad, current_pitch_rad, current_yaw_rad = 0.0, 0.0, azimuth_angle_rad

        if imu_data_with_orientation is not None:
            radar_timestamp = row['Time (seconds)']
            closest_imu = imu_data_with_orientation.iloc[(imu_data_with_orientation['timestamp'] - radar_timestamp).abs().argsort()[:1]]
            if not closest_imu.empty:
                current_roll_rad = np.deg2rad(closest_imu['roll'].values[0])
                current_pitch_rad = np.deg2rad(closest_imu['pitch'].values[0])

        for detected_bin_index in detected_indices:
            r = range_bins[detected_bin_index]
            corrected_r, corrected_azimuth_rad = correct_for_imu_orientation(r, azimuth_angle_rad, current_roll_rad, current_pitch_rad, current_yaw_rad)
            
            all_detected_points_polar.append((corrected_r, corrected_azimuth_rad))
            x, y = polar_to_cartesian(corrected_r, corrected_azimuth_rad)
            all_detected_points_cartesian.append((x, y))
            
    return all_detected_points_cartesian, all_detected_points_polar, first_frame_viz_data

def cluster_and_visualize(all_detected_points_cartesian, all_detected_points_polar, first_frame_viz_data):
    """
    Clusters detected points and visualizes the results.

    Args:
        all_detected_points_cartesian (list): List of detected points in Cartesian coordinates.
        all_detected_points_polar (list): List of detected points in polar coordinates.
        first_frame_viz_data (dict): Data for the first frame's CFAR visualization.
    """
    from src.processing.object_clustering import cluster_detected_points
    from src.visualization.map_viewer import create_2d_map, plot_cfar_detection, plot_polar_map
    from src.config.constants import DBSCAN_EPS, DBSCAN_MIN_SAMPLES, MAP_EXTENT_M, GRID_RESOLUTION_M

    if not all_detected_points_cartesian:
        print("\nNo points detected for clustering or visualization.")
        return

    clusters_indices = cluster_detected_points(all_detected_points_cartesian, eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES)
    print(f"\nDetected {len(clusters_indices)} clusters.")

    create_2d_map(
        clusters=clusters_indices,
        all_detected_points_cartesian=all_detected_points_cartesian,
        title="2D Radar Occupancy Grid with Clusters",
        map_extent_m=MAP_EXTENT_M,
        grid_resolution=GRID_RESOLUTION_M
    )
    print(f"\nGenerated 2D occupancy grid with {len(all_detected_points_cartesian)} detected points.")

    if first_frame_viz_data:
        plot_cfar_detection(
            first_frame_viz_data['range_profile'],
            first_frame_viz_data['cfar_threshold'],
            first_frame_viz_data['detected_indices'],
            frame_index=0
        )
        print(f"\nCFAR applied to first frame. Detected targets at range bins: {first_frame_viz_data['detected_indices'].tolist()}")

    if all_detected_points_polar:
        plot_polar_map(all_detected_points_polar)
