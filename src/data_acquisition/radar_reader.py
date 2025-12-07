import pandas as pd
import os

def read_radar_data(file_path):
    """
    Reads radar data from a specified .data file.

    Args:
        file_path (str): The absolute path to the radar data .data file.
                         Assumes a header line starting with '#' and comma-separated values.

    Returns:
        pd.DataFrame: A DataFrame containing the radar data, or None if the file is not found or an error occurs.
    """
    if not os.path.exists(file_path):
        print(f"Error: Radar data file not found at {file_path}")
        return None

    try:
        with open(file_path, 'r') as f:
            header_line = f.readline().strip()
        
        # Remove '#' and split by comma to get column names
        column_names = [name.strip() for name in header_line.lstrip('# ').split(',')]

        # Read the CSV data, skipping the header line and assigning column names
        df_radar = pd.read_csv(file_path, skiprows=1, header=None, names=column_names)
        
        print(f"Successfully loaded radar data from {file_path}.")
        print(f"Radar DataFrame shape: {df_radar.shape}")
        return df_radar
    except Exception as e:
        print(f"Error reading radar data from {file_path}: {e}")
        return None

if __name__ == "__main__":
    # Example usage: Create a dummy radar data file for demonstration
    dummy_radar_data = {
        'Time (seconds)': [0.0, 0.1, 0.2, 0.3, 0.4],
        'f0_f0_f0': [0.1, 0.11, 0.12, 0.13, 0.14],
        'f0_f0_f1': [0.0, 0.01, 0.02, 0.03, 0.04],
        'f0_f0_f2': [9.8, 9.81, 9.82, 9.83, 9.84],
    }
    dummy_df_radar = pd.DataFrame(dummy_radar_data)
    dummy_file_path = "dummy_radar_data.data"
    dummy_df_radar.to_csv(dummy_file_path, index=False)
    print(f"Created dummy radar data file: {dummy_file_path}")

    # Test reading the dummy file
    radar_data = read_radar_data(dummy_file_path)
    if radar_data is not None:
        print("\nDummy radar data read successfully:")
        print(radar_data.head())
    
    # Clean up dummy file
    os.remove(dummy_file_path)
    print(f"Removed dummy radar data file: {dummy_file_path}")
