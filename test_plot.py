import os
from src.visualization.map_viewer import create_2d_map
from src.config import constants

print("Testing create_2d_map function...")
try:
    create_2d_map(
        clusters=[],
        all_detected_points_cartesian=[],
        title="Test Plot",
        save_path=os.path.join(constants.PLOTS_OUTPUT_DIR, "test_plot.png")
    )
    print("Test successful!")
except Exception as e:
    print(f"Test failed with error: {e}")
