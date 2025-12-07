import subprocess
import sys
import os

def install_dependencies():
    """
    Installs dependencies from requirements.txt using pip.
    """
    # Get the path to requirements.txt in the parent directory
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")

    if not os.path.exists(requirements_path):
        print(f"Error: {requirements_path} not found.")
        return

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
    except FileNotFoundError:
        print("Error: pip is not available. Please ensure pip is installed and in your PATH.")

if __name__ == "__main__":
    install_dependencies()
