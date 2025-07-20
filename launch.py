# launch.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

import subprocess
import threading
import time
import webview
import logging
import sys
import os
import requests
from pathlib import Path

# --- Centralized Logging Setup ---
def setup_logging():
    """Configures logging to file and console."""
    try:
        from version import get_version
        __version__ = get_version()
    except ImportError:
        __version__ = "30.2.0"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("kyo_qa_tool.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info(f"--- Starting KYO QA Tool v{__version__} ---")

def wait_for_server(url="http://127.0.0.1:5000", timeout=30):
    """Wait for the Flask server to be ready."""
    logger = logging.getLogger(__name__)
    logger.info(f"Waiting for server at {url}")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                logger.info("Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        logger.info(f"Still waiting for server... ({int(time.time() - start_time)}s)")
    
    logger.error(f"Server failed to respond within {timeout} seconds")
    return False

def start_server(script_dir):
    """Starts the Flask web server in a separate process."""
    logger = logging.getLogger(__name__)
    logger.info("Attempting to start the Flask server.")
    
    try:
        # Determine the correct Python executable
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # We're in a virtual environment
            python_executable = sys.executable
        else:
            # Check if we should use the venv python
            venv_python = Path(script_dir) / "venv" / "Scripts" / "python.exe"
            if venv_python.exists():
                python_executable = str(venv_python)
            else:
                python_executable = sys.executable
                
        logger.info(f"Using Python executable: {python_executable}")
        
        server_process = subprocess.Popen(
            [python_executable, "server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=script_dir,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Monitor server output in a separate thread
        def log_server_output():
            while True:
                output = server_process.stdout.readline()
                if output == '' and server_process.poll() is not None:
                    break
                if output.strip():
                    logger.info(f"SERVER: {output.strip()}")
                    
        def log_server_errors():
            while True:
                output = server_process.stderr.readline()
                if output == '' and server_process.poll() is not None:
                    break
                if output.strip():
                    logger.error(f"SERVER ERROR: {output.strip()}")

        stdout_thread = threading.Thread(target=log_server_output, daemon=True)
        stderr_thread = threading.Thread(target=log_server_errors, daemon=True)
        stdout_thread.start()
        stderr_thread.start()

        logger.info("Flask server process started.")
        return server_process
        
    except FileNotFoundError:
        logger.error("Error: 'server.py' not found. Please ensure all files are in the correct directory.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while starting the server: {e}", exc_info=True)
        return None

class Api:
    """API methods exposed to the webview UI."""
    pass

def main():
    """Main application entry point."""
    # 1. Set up logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get the directory where this script is located
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Start the backend server
    server_process = None
    try:
        server_process = start_server(current_script_dir)
        if server_process is None:
            logger.error("Failed to start server. Exiting.")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # 3. Wait for server to be ready
        if not wait_for_server():
            logger.error("Server failed to start properly. Exiting.")
            input("Press Enter to exit...")
            sys.exit(1)

        # 4. Create and start the pywebview UI
        logger.info("Server ready. Creating UI window...")
        
        try:
            api = Api()
            webview.create_window(
                'KYO QA ServiceNow Knowledge Tool',
                'http://127.0.0.1:5000',
                width=1200,
                height=800,
                resizable=True,
                js_api=api
            )
            
            logger.info("Starting webview...")
            webview.start(debug=False)
            logger.info("UI window closed by user.")
            
        except Exception as e:
            logger.error(f"Failed to create or start the UI window: {e}", exc_info=True)
            print(f"\nERROR: Failed to start UI: {e}")
            print("This might be due to missing webview dependencies or display issues.")
            print("Try running the enhanced launcher instead: python enhanced_launcher.py")
            input("Press Enter to exit...")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"\nUnexpected error: {e}")
        input("Press Enter to exit...")
    finally:
        # Clean up server process
        if server_process:
            try:
                logger.info("Shutting down server...")
                server_process.terminate()
                server_process.wait(timeout=5)
                logger.info("Server shutdown complete")
            except:
                logger.warning("Forcing server shutdown...")
                server_process.kill()
        logger.info("--- Application has exited. ---")

if __name__ == '__main__':
    main()