import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class ComplementaryFilter:
    """
    A complementary filter for estimating roll, pitch, and yaw.
    """
    def __init__(self, dt, alpha=0.98):
        self.dt = dt
        self.alpha = alpha
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0

    def update(self, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x=None, mag_y=None, mag_z=None):
        """
        Updates the filter with new sensor readings and estimates roll, pitch, and yaw.
        """
        # Accelerometer-derived angles
        accel_roll = np.arctan2(accel_y, np.sqrt(accel_x**2 + accel_z**2))
        accel_pitch = np.arctan2(-accel_x, np.sqrt(accel_y**2 + accel_z**2))

        # Gyroscope-derived angles (integrated)
        # Note: This is a simple integration. A more robust solution would use quaternions.
        self.roll += gyro_x * self.dt
        self.pitch += gyro_y * self.dt
        self.yaw += gyro_z * self.dt # Gyro-based yaw

        # Complementary filter fusion for roll and pitch
        self.roll = self.alpha * self.roll + (1 - self.alpha) * accel_roll
        self.pitch = self.alpha * self.pitch + (1 - self.alpha) * accel_pitch

        # Magnetometer-based yaw (tilt-compensated)
        if mag_x is not None and mag_y is not None and mag_z is not None:
            # Tilt compensation
            mag_x_comp = mag_x * np.cos(self.pitch) + mag_z * np.sin(self.pitch)
            mag_y_comp = mag_x * np.sin(self.roll) * np.sin(self.pitch) + mag_y * np.cos(self.roll) - mag_z * np.sin(self.roll) * np.cos(self.pitch)
            
            # Yaw calculation
            mag_yaw = np.arctan2(-mag_y_comp, mag_x_comp)
            
            # Fuse gyro yaw and magnetometer yaw
            # This is a simple approach. A better fusion would be needed for robust performance.
            self.yaw = self.alpha * self.yaw + (1 - self.alpha) * mag_yaw

        return np.degrees(self.roll), np.degrees(self.pitch), np.degrees(self.yaw)

def estimate_orientation(imu_data_df, dt=0.01, alpha=0.98):
    """
    Estimates orientation (roll, pitch, yaw) from a DataFrame of IMU data.
    """
    filter = ComplementaryFilter(dt, alpha)
    rolls, pitchs, yaws = [], [], []

    has_mag = all(col in imu_data_df.columns for col in ['mag_x', 'mag_y', 'mag_z'])
    if not has_mag:
        print("Magnetometer data not found. Yaw estimation will be based on gyroscope integration only.")

    for index, row in imu_data_df.iterrows():
        mag_x, mag_y, mag_z = (row['mag_x'], row['mag_y'], row['mag_z']) if has_mag else (None, None, None)
        
        roll, pitch, yaw = filter.update(
            row['accel_x'], row['accel_y'], row['accel_z'],
            row['gyro_x'], row['gyro_y'], row['gyro_z'],
            mag_x, mag_y, mag_z
        )
        rolls.append(roll)
        pitchs.append(pitch)
        yaws.append(yaw)
    
    imu_data_df['roll'] = rolls
    imu_data_df['pitch'] = pitchs
    imu_data_df['yaw'] = yaws
    return imu_data_df

if __name__ == "__main__":
    # Example usage with dummy data
    dummy_data = {
        'timestamp': np.linspace(0, 1, 100),
        'accel_x': np.zeros(100),
        'accel_y': np.zeros(100),
        'accel_z': np.full(100, 9.81),
        'gyro_x': np.zeros(100),
        'gyro_y': np.zeros(100),
        'gyro_z': np.full(100, 0.1), # Simulating a slow turn
        'mag_x': np.cos(np.linspace(0, np.pi, 100)),
        'mag_y': np.sin(np.linspace(0, np.pi, 100)),
        'mag_z': np.zeros(100),
    }
    dummy_df = pd.DataFrame(dummy_data)

    dt_example = dummy_data['timestamp'][1] - dummy_data['timestamp'][0]
    orientation_df = estimate_orientation(dummy_df.copy(), dt=dt_example)

    print("IMU data with estimated orientation:")
    print(orientation_df[['timestamp', 'roll', 'pitch', 'yaw']].head())

    # Plotting for visualization
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(orientation_df['timestamp'], orientation_df['roll'], label='Roll (degrees)')
    plt.plot(orientation_df['timestamp'], orientation_df['pitch'], label='Pitch (degrees)')
    plt.title('Estimated Roll and Pitch')
    plt.ylabel('Angle (degrees)')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(orientation_df['timestamp'], orientation_df['yaw'], label='Yaw (degrees)')
    plt.title('Estimated Yaw')
    plt.xlabel('Time (s)')
    plt.ylabel('Angle (degrees)')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()