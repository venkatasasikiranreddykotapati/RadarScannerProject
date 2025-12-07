import os

# --- Project Root ---
# Assumes this file is in src/config. The project root is two levels up.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# --- File Paths ---
# Define the session directory you want to process
SESSION_DIR_NAME = "undercharan" # As requested

# Construct absolute paths to the data files
DATA_DIR = os.path.join(PROJECT_ROOT, "Deep Craft", "Test", SESSION_DIR_NAME)
RADAR_DATA_FILE = os.path.join(DATA_DIR, "Radar-Data.data")
IMU_DATA_FILE = os.path.join(DATA_DIR, "IMU-Data.data")
MAGNETOMETER_DATA_FILE = os.path.join(DATA_DIR, "Magnetometer-Data.data")

FULL_RADAR_DATA_PATH = RADAR_DATA_FILE
FULL_IMU_DATA_PATH = IMU_DATA_FILE

# --- Radar & Processing Parameters ---
# These parameters are based on the BGT60TR13C sensor and common configurations.
# They might need to be adjusted based on your specific chirp configuration.
MAX_RANGE_M = 8.0  # Maximum range of the radar in meters

# --- CFAR (Constant False Alarm Rate) Parameters ---
# These values control the sensitivity of the object detection algorithm.
CFAR_NUM_TRAINING_CELLS = 10 # Number of cells on each side of the CUT to estimate noise
CFAR_NUM_GUARD_CELLS = 2    # Number of cells to ignore on each side of the CUT
CFAR_P_FA = 1e-1 # Desired Probability of False Alarm

# --- Clustering (DBSCAN) Parameters ---
# These values control how detected points are grouped into objects.
DBSCAN_EPS = 0.5        # The maximum distance between two samples for one to be considered as in the neighborhood of the other (in meters).
DBSCAN_MIN_SAMPLES = 3  # The number of samples in a neighborhood for a point to be considered as a core point.

# --- Visualization Parameters ---
MAP_EXTENT_M = 10.0     # The total size of the 2D map visualization (e.g., 10 means -5m to +5m)
GRID_RESOLUTION_M = 0.1 # The size of each cell in the occupancy grid background (in meters)

# --- IMU Parameters ---
# The sampling rate of your IMU. This is crucial for accurate orientation estimation.
# Check the configuration used during data collection. Let's assume 100 Hz for now.
IMU_SAMPLE_RATE_HZ = 100.0
IMU_DT = 1.0 / IMU_SAMPLE_RATE_HZ # Time delta in seconds

# --- Output Directories ---
PLOTS_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "plots")
