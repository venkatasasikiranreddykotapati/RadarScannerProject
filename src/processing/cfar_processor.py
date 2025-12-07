import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import inspect
from src.data_acquisition.radar_reader import read_radar_data
from src.data_acquisition.imu_reader import read_and_merge_imu_data
from src.fusion.imu_fusion import estimate_orientation
from src.processing.cfar_detection import cfar_ca
from src.processing.object_clustering import cluster_detected_points
from src.visualization import map_viewer
print(f"map_viewer path: {inspect.getfile(map_viewer)}")
from src.processing.radar_fft import polar_to_cartesian, perform_fft, correct_for_imu_orientation
from src.visualization.map_viewer import create_2d_map, plot_cfar_detection, plot_raw_imu_data, plot_imu_orientation, plot_polar_map
from src.config import constants

def process_and_cfar_data(file_path, imu_file_path=None, mag_file_path=None):
    """
    Loads radar data, applies FFT and CFAR, clusters detected points, and visualizes the results, including a 2D map.
    Optionally loads and processes IMU and magnetometer data for orientation estimation.

    Args:
        file_path (str): Absolute path to the Radar-Data.data file.
        imu_file_path (str, optional): Absolute path to the IMU data CSV file.
        mag_file_path (str, optional): Absolute path to the Magnetometer data file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        df = read_radar_data(file_path)
        if df is None:
            print("Error: Could not load radar data.")
            return

        radar_columns = [col for col in df.columns if col.startswith('f0_f0_')]
        if not radar_columns:
            print("Error: No radar data columns found (e.g., 'f0_f0_fX').")
            return

        # --- IMU Data Processing ---
        imu_data_with_orientation = None
        if imu_file_path:
            df_imu = read_and_merge_imu_data(imu_file_path, mag_file_path)
            if df_imu is not None:
                imu_dt = (df_imu['timestamp'].iloc[1] - df_imu['timestamp'].iloc[0]) if len(df_imu) > 1 else 0.01
                imu_data_with_orientation = estimate_orientation(df_imu.copy(), dt=imu_dt)
                print("\nEstimated IMU Orientation (first 5 rows):")
                print(imu_data_with_orientation[['timestamp', 'roll', 'pitch', 'yaw']].head())
                
                plot_raw_imu_data(df_imu, save_path=os.path.join(constants.PLOTS_OUTPUT_DIR, "raw_imu_data.png"))
                plot_imu_orientation(imu_data_with_orientation, save_path=os.path.join(constants.PLOTS_OUTPUT_DIR, "imu_orientation.png"))
            else:
                print("IMU data could not be loaded or processed.")
        # --- End IMU Data Processing ---

        all_detected_points_cartesian = []
        all_detected_points_polar = []
        
        first_frame_range_profile = None
        first_frame_cfar_threshold = None
        first_frame_detected_indices = None

        for index, row in df.iterrows():
            raw_radar_profile = row[radar_columns].values.astype(float)
            range_profile = perform_fft(raw_radar_profile)
            range_bins = np.linspace(0, constants.MAX_RANGE_M, len(range_profile))

            detections = cfar_ca(range_profile, constants.CFAR_NUM_TRAINING_CELLS, constants.CFAR_NUM_GUARD_CELLS, constants.CFAR_P_FA)
            detected_indices = np.where(detections)[0]

            if index == 0:
                first_frame_range_profile = range_profile
                first_frame_cfar_threshold = np.zeros_like(range_profile)
                N = 2 * constants.CFAR_NUM_TRAINING_CELLS
                alpha = N * (constants.CFAR_P_FA**(-1/N) - 1)
                offset = constants.CFAR_NUM_TRAINING_CELLS + constants.CFAR_NUM_GUARD_CELLS
                for i in range(len(range_profile)):
                    if i < offset or i >= len(range_profile) - offset:
                        first_frame_cfar_threshold[i] = np.nan
                        continue
                    sum_training_cells = np.sum(range_profile[i - offset : i - constants.CFAR_NUM_GUARD_CELLS])
                    sum_training_cells += np.sum(range_profile[i + constants.CFAR_NUM_GUARD_CELLS + 1 : i + offset + 1])
                    noise_estimate = sum_training_cells / N
                    first_frame_cfar_threshold[i] = alpha * noise_estimate
                first_frame_detected_indices = detected_indices
            
            azimuth_angle_rad = (index / len(df)) * np.pi

            current_roll_rad, current_pitch_rad, current_yaw_rad = 0.0, 0.0, azimuth_angle_rad

            if imu_data_with_orientation is not None and not imu_data_with_orientation.empty:
                radar_timestamp = row['Time (seconds)']
                closest_imu_data = imu_data_with_orientation.iloc[(imu_data_with_orientation['timestamp'] - radar_timestamp).abs().argsort()[:1]]
                
                if not closest_imu_data.empty:
                    current_roll_rad = np.deg2rad(closest_imu_data['roll'].values[0])
                    current_pitch_rad = np.deg2rad(closest_imu_data['pitch'].values[0])
                    if 'yaw' in closest_imu_data.columns:
                        current_yaw_rad = np.deg2rad(closest_imu_data['yaw'].values[0])

            for detected_bin_index in detected_indices:
                r = range_bins[detected_bin_index]
                
                corrected_r, corrected_azimuth_rad = correct_for_imu_orientation(
                    r, azimuth_angle_rad, current_roll_rad, current_pitch_rad, current_yaw_rad
                )
                
                all_detected_points_polar.append((corrected_r, corrected_azimuth_rad))
                x, y = polar_to_cartesian(corrected_r, corrected_azimuth_rad)
                all_detected_points_cartesian.append((x, y))

        if all_detected_points_cartesian:
            clusters_indices = cluster_detected_points(all_detected_points_cartesian, eps=constants.DBSCAN_EPS, min_samples=constants.DBSCAN_MIN_SAMPLES)
            print(f"\nDetected {len(clusters_indices)} clusters.")
            create_2d_map(clusters=clusters_indices, all_detected_points_cartesian=all_detected_points_cartesian, title="2D Radar Occupancy Grid with Clusters", map_extent_m=constants.MAP_EXTENT_M, grid_resolution=constants.GRID_RESOLUTION_M, save_path=os.path.join(constants.PLOTS_OUTPUT_DIR, "2d_radar_map.png"))
            print(f"\nGenerated 2D occupancy grid with {len(all_detected_points_cartesian)} detected points.")
        else:
            print("\nNo points detected for clustering or mapping.")

        if first_frame_range_profile is not None:
            plot_cfar_detection(first_frame_range_profile, first_frame_cfar_threshold, first_frame_detected_indices, frame_index=0, save_path=os.path.join(constants.PLOTS_OUTPUT_DIR, "cfar_detection.png"))
            print(f"\nCFAR applied to first frame. Detected targets at range bins: {first_frame_detected_indices.tolist()}")

        if all_detected_points_polar:
            plot_polar_map(all_detected_points_polar, save_path=os.path.join(constants.PLOTS_OUTPUT_DIR, "2d_radar_polar_plot.png"))

    except Exception as e:
        print(f"Error processing radar data: {e}")
