# High-Level Project Workflow: Radar-Room-Scanner

This document outlines the high-level workflow for the Radar-Room-Scanner project, based on the project roadmap.

## Stage 1: Hardware Interfacing & Data Acquisition

*   **Goal:** Establish communication with the radar and IMU sensors and stream their data to a PC.
*   **Tasks:**
    *   Connect the BGT60TR13C radar and IMU to the PC.
    *   Develop a Python script (`src/data_acquisition.py`) to handle the raw data streaming from the sensors.
    *   Save the raw sensor data to files in the `data/raw/` directory for offline processing and analysis.

## Stage 2: Radar Signal Processing & 2D Mapping (Stationary Scanner)

*   **Goal:** Process the raw radar data to detect objects and create a 2D map from a stationary (but rotating) scanner.
*   **Tasks:**
    *   Implement a signal processing pipeline in Python (`src/signal_processing.py`) that includes:
        *   Fast Fourier Transform (FFT) for range and speed information.
        *   Constant False Alarm Rate (CFAR) for peak detection.
    *   Develop a mapping module (`src/mapping.py`) to convert the detected objects' polar coordinates (angle, distance) into Cartesian coordinates (x, y).
    *   Visualize the resulting 2D point map.

## Stage 3: IMU Sensor Fusion & Orientation Tracking

*   **Goal:** Use the IMU data to get a stable estimate of the scanner's orientation in 3D space.
*   **Tasks:**
    *   Implement a sensor fusion algorithm (e.g., Madgwick, Complementary, or Kalman filter) in `src/sensor_fusion.py`.
    *   Process the raw IMU data (accelerometer, gyroscope, magnetometer) to calculate the device's roll, pitch, and yaw.
    *   Test the orientation tracking accuracy.

## Stage 4: Motion-Compensated Mapping (Handheld Scanner)

*   **Goal:** Integrate the IMU's orientation data with the radar data to create accurate maps even when the scanner is moved by hand.
*   **Tasks:**
    *   Modify the mapping module (`src/mapping.py`) to use the orientation data from the sensor fusion module to transform the radar measurements into a stable world frame.
    *   This will compensate for the tilting and rotation of the handheld scanner.
    *   Test by creating maps while moving the scanner and comparing them to maps created with the stationary scanner.

## Stage 5: Simultaneous Localization and Mapping (SLAM)

*   **Goal:** Track the scanner's position within the environment and build a consistent, unified map as the scanner moves through the room.
*   **Tasks:**
    *   Research and choose a suitable SLAM algorithm (e.g., a hybrid approach using IMU for odometry and radar for loop closure).
    *   Implement the SLAM algorithm in a new module (`src/slam.py`).
    *   This will involve:
        *   **Scan Matching:** Aligning new radar scans with the existing map.
        *   **Pose Estimation:** Updating the scanner's estimated position and orientation.
        *   **Map Updating:** Integrating the new scan data into the global map.
    *   Test the full SLAM system in a real environment.
