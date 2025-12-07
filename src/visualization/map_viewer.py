import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm # For colormaps
import os
from src.config import constants

def create_2d_map(clusters, all_detected_points_cartesian=None, title="2D Radar Map with Clusters", grid_resolution=0.1, map_extent_m=10, save_path=None):
    plt.figure(figsize=(10, 10))
    ax = plt.gca()
    min_x = -map_extent_m / 2
    max_x = map_extent_m / 2
    min_y = -map_extent_m / 2
    max_y = map_extent_m / 2
    if all_detected_points_cartesian:
        num_cells_x = int((max_x - min_x) / grid_resolution)
        num_cells_y = int((max_y - min_y) / grid_resolution)
        occupancy_grid = np.zeros((num_cells_y, num_cells_x))
        for x, y in all_detected_points_cartesian:
            if min_x <= x < max_x and min_y <= y < max_y:
                grid_x = int((x - min_x) / grid_resolution)
                grid_y = int((y - min_y) / grid_resolution)
                occupancy_grid[grid_y, grid_x] += 1
        ax.imshow(occupancy_grid, cmap='Greys', origin='lower', extent=[min_x, max_x, min_y, max_y], alpha=0.5)
    if all_detected_points_cartesian:
        clustered_point_indices = set()
        for cluster_indices in clusters:
            for idx in cluster_indices:
                clustered_point_indices.add(idx)
        unclustered_x = []
        unclustered_y = []
        for i, (x, y) in enumerate(all_detected_points_cartesian):
            if i not in clustered_point_indices:
                unclustered_x.append(x)
                unclustered_y.append(y)
        if unclustered_x:
            ax.scatter(unclustered_x, unclustered_y, color='lightgray', label='Unclustered Points', s=10, alpha=0.6)
    colors = cm.get_cmap('tab10', len(clusters))
    for i, cluster_indices in enumerate(clusters):
        if cluster_indices:
            cluster_points = [all_detected_points_cartesian[idx] for idx in cluster_indices]
            cluster_x = [p[0] for p in cluster_points]
            cluster_y = [p[1] for p in cluster_points]
            ax.scatter(cluster_x, cluster_y, color=colors(i), label=f'Object {i+1}', s=30, edgecolor='black', linewidth=0.5)
    ax.set_title(title)
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.grid(True)
    ax.set_aspect('equal', adjustable='box')
    ax.legend()
    if save_path:
        plt.savefig(save_path)
        print(f"2D map saved to {save_path}")
    plt.show()

def plot_cfar_detection(radar_profile, cfar_threshold, detected_indices, frame_index=None, save_path=None):
    plt.figure(figsize=(12, 6))
    plt.plot(radar_profile, label='Radar Profile')
    plt.plot(cfar_threshold, label='CFAR Threshold', linestyle='--')
    if len(detected_indices) > 0:
        plt.scatter(detected_indices, radar_profile[detected_indices], color='red', marker='o', s=50, label='Detected Points')
    plt.title(f'CFAR Detection - Frame {frame_index}' if frame_index is not None else 'CFAR Detection')
    plt.xlabel('Range Bin')
    plt.ylabel('Magnitude')
    plt.legend()
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
        print(f"CFAR plot saved to {save_path}")
    plt.show()

def plot_raw_imu_data(df_imu, save_path=None):
    if df_imu is None or df_imu.empty:
        print("No IMU data to plot.")
        return
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle('Raw IMU Data')
    axs[0].plot(df_imu['timestamp'], df_imu['accel_x'], label='Accel X')
    axs[0].plot(df_imu['timestamp'], df_imu['accel_y'], label='Accel Y')
    axs[0].plot(df_imu['timestamp'], df_imu['accel_z'], label='Accel Z')
    axs[0].set_ylabel('Acceleration (g)')
    axs[0].legend()
    axs[0].grid(True)
    axs[1].plot(df_imu['timestamp'], df_imu['gyro_x'], label='Gyro X')
    axs[1].plot(df_imu['timestamp'], df_imu['gyro_y'], label='Gyro Y')
    axs[1].plot(df_imu['timestamp'], df_imu['gyro_z'], label='Gyro Z')
    axs[1].set_ylabel('Angular Velocity (rad/s)')
    axs[1].legend()
    axs[1].grid(True)
    if 'mag_x' in df_imu.columns:
        axs[2].plot(df_imu['timestamp'], df_imu['mag_x'], label='Mag X')
        axs[2].plot(df_imu['timestamp'], df_imu['mag_y'], label='Mag Y')
        axs[2].plot(df_imu['timestamp'], df_imu['mag_z'], label='Mag Z')
        axs[2].set_ylabel('Magnetic Field (uT)')
        axs[2].legend()
        axs[2].grid(True)
    else:
        axs[2].set_visible(False)
    axs[-1].set_xlabel('Time (s)')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    if save_path:
        plt.savefig(save_path)
        print(f"Raw IMU data plot saved to {save_path}")
    plt.show()

def plot_imu_orientation(df_imu_orientation, save_path=None):
    if df_imu_orientation is None or df_imu_orientation.empty:
        print("No IMU orientation data to plot.")
        return
    plt.figure(figsize=(12, 6))
    plt.plot(df_imu_orientation['timestamp'], df_imu_orientation['roll'], label='Roll (degrees)')
    plt.plot(df_imu_orientation['timestamp'], df_imu_orientation['pitch'], label='Pitch (degrees)')
    if 'yaw' in df_imu_orientation.columns:
        plt.plot(df_imu_orientation['timestamp'], df_imu_orientation['yaw'], label='Yaw (degrees)')
    plt.title('Estimated IMU Orientation')
    plt.xlabel('Time (s)')
    plt.ylabel('Angle (degrees)')
    plt.legend()
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
        print(f"IMU orientation plot saved to {save_path}")
    plt.show()

def plot_polar_map(polar_points, title="2D Radar Polar Plot", save_path="output/plots/2d_radar_polar_plot.png"):
    if not polar_points:
        print("No polar points to plot.")
        return
    plt.figure(figsize=(10, 10))
    ax = plt.subplot(111, projection='polar')
    r = [p[0] for p in polar_points]
    theta = [p[1] for p in polar_points]
    ax.scatter(theta, r, s=10)
    ax.set_title(title, va='bottom')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(-22.5)
    ax.grid(True)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Polar plot saved to {save_path}")
    plt.show()