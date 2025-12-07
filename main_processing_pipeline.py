import os
import sys

# Add the project root to sys.path to enable absolute imports
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.pipeline.main_pipeline import run_processing_pipeline

if __name__ == "__main__":
    run_processing_pipeline()