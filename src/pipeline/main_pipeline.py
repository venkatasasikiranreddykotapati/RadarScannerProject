import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Import Project Modules ---
from src.config import constants
from src.data_acquisition.radar_reader import read_radar_data
from src.processing.cfar_processor import process_and_cfar_data # Import the main processing function

def run_processing_pipeline():
    """
    Main function to run the complete radar data processing pipeline.
    """
    print("--- Starting Radar Processing Pipeline ---")

    # Create output directory for plots if it doesn't exist
    os.makedirs(constants.PLOTS_OUTPUT_DIR, exist_ok=True)

    # --- 1. Define File Paths ---
    radar_file_path = constants.RADAR_DATA_FILE
    imu_file_path = constants.IMU_DATA_FILE if os.path.exists(constants.IMU_DATA_FILE) else None
    mag_file_path = constants.MAGNETOMETER_DATA_FILE if os.path.exists(constants.MAGNETOMETER_DATA_FILE) else None

    # --- 2. Run the main processing and visualization ---
    process_and_cfar_data(
        file_path=radar_file_path,
        imu_file_path=imu_file_path,
        mag_file_path=mag_file_path
    )
    
    print("\n--- Pipeline Finished ---")

if __name__ == "__main__":
    run_processing_pipeline()
