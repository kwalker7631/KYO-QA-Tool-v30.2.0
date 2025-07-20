# run.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

"""Launcher for automatic virtual environment setup and application start."""

import sys
import subprocess
import os
from pathlib import Path

VENV_DIR = "venv"
REQUIREMENTS_FILE = "requirements.txt"
LAUNCH_SCRIPT = "launch.py"

def is_windows():
    """Check if the current operating system is Windows."""
    return os.name == 'nt'

def get_python_executable():
    """Construct the path to the Python executable within the virtual environment."""
    if is_windows():
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")

def setup_environment():
    """
    Create a virtual environment if it doesn't exist, then install or update
    the required packages from the requirements.txt file.
    """
    if not Path(VENV_DIR).exists():
        print("--- Creating virtual environment... ---")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
            print("--- Virtual environment created successfully. ---")
        except subprocess.CalledProcessError as e:
            print(f"--- FATAL ERROR: Failed to create virtual environment. {e} ---")
            sys.exit(1)
    
    print("--- Installing/updating dependencies... ---")
    try:
        pip_executable = get_python_executable().replace('python.exe', 'pip.exe') if is_windows() else get_python_executable().replace('python', 'pip')
        subprocess.check_call([pip_executable, "install", "--upgrade", "-r", REQUIREMENTS_FILE])
        print("--- Dependencies are up to date. ---")
    except subprocess.CalledProcessError as e:
        print(f"--- FATAL ERROR: Failed to install dependencies. {e} ---")
        sys.exit(1)

def main():
    """
    Main entry point for the application. Sets up the environment and
    launches the main application script.
    """
    print("--- KYO QA Tool Launcher ---")
    try:
        setup_environment()
        print(f"--- Launching application: {LAUNCH_SCRIPT} ---")
        python_executable = get_python_executable()
        subprocess.run([python_executable, LAUNCH_SCRIPT])
    except Exception as e:
        print(f"--- AN UNEXPECTED ERROR OCCURRED: {e} ---")
        print("--- Please check your Python installation and ensure scripts have permission to run. ---")
    finally:
        print("--- Application has been closed. ---")

if __name__ == "__main__":
    main()
