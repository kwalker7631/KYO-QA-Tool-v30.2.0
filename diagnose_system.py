#!/usr/bin/env python3
# diagnose_system.py
# System diagnostic script for KYO QA Tool
# Author: Kenneth Walker

import sys
import os
import platform
import subprocess
import importlib
from pathlib import Path

def print_header(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def check_python_environment():
    """Check Python version and environment."""
    print_header("PYTHON ENVIRONMENT")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")
        
    # Check virtual environment existence
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment directory exists")
        
        # Check for Python executable in venv
        if os.name == 'nt':
            venv_python = venv_path / "Scripts" / "python.exe"
        else:
            venv_python = venv_path / "bin" / "python"
            
        if venv_python.exists():
            print(f"✅ Virtual environment Python found: {venv_python}")
        else:
            print("❌ Virtual environment Python not found")
    else:
        print("❌ Virtual environment directory not found")

def check_dependencies():
    """Check if required dependencies are installed."""
    print_header("DEPENDENCY CHECK")
    
    required_packages = [
        'flask', 'werkzeug', 'openpyxl', 'PIL', 'webview', 
        'fitz', 'pandas', 'pytesseract', 'requests'
    ]
    
    for package in required_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'fitz':
                importlib.import_module('fitz')
            elif package == 'webview':
                import webview
                print(f"✅ {package} - Version: {webview.__version__ if hasattr(webview, '__version__') else 'Unknown'}")
                continue
            else:
                module = importlib.import_module(package)
                
            version = getattr(module, '__version__', 'Unknown')
            print(f"✅ {package} - Version: {version}")
            
        except ImportError as e:
            print(f"❌ {package} - NOT INSTALLED ({e})")
        except Exception as e:
            print(f"⚠️  {package} - ERROR: {e}")

def check_webview_backend():
    """Check webview backend availability."""
    print_header("WEBVIEW BACKEND CHECK")
    
    try:
        import webview
        print(f"✅ PyWebView imported successfully")
        
        # Try to detect the backend
        try:
            # This is a bit tricky as webview doesn't expose backend info directly
            print("🔍 Attempting to detect webview backend...")
            
            if os.name == 'nt':  # Windows
                try:
                    import webview.platforms.winforms
                    print("✅ Windows Forms backend available")
                except ImportError:
                    print("❌ Windows Forms backend not available")
                    
                try:
                    import webview.platforms.cef
                    print("✅ CEF backend available")
                except ImportError:
                    print("⚠️  CEF backend not available (this is normal)")
                    
            # Check for EdgeHTML/WebView2 on Windows
            if os.name == 'nt':
                try:
                    import webview.platforms.edgechromium
                    print("✅ Edge Chromium backend available")
                except ImportError:
                    print("⚠️  Edge Chromium backend not available")
                    
        except Exception as e:
            print(f"⚠️  Backend detection failed: {e}")
            
    except ImportError as e:
        print(f"❌ PyWebView not available: {e}")

def check_tesseract():
    """Check Tesseract OCR installation."""
    print_header("TESSERACT OCR CHECK")
    
    # Common Tesseract paths
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract"
    ]
    
    tesseract_found = False
    
    for path in tesseract_paths:
        if os.path.exists(path):
            print(f"✅ Tesseract found at: {path}")
            tesseract_found = True
            
            # Try to get version
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    print(f"   Version: {version_line}")
            except Exception as e:
                print(f"   ⚠️  Could not get version: {e}")
            break
    
    if not tesseract_found:
        # Try system PATH
        try:
            result = subprocess.run(["tesseract", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Tesseract found in system PATH")
                version_line = result.stdout.split('\n')[0]
                print(f"   Version: {version_line}")
                tesseract_found = True
        except Exception:
            pass
    
    if not tesseract_found:
        print("❌ Tesseract OCR not found")
        print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")

def check_critical_files():
    """Check if all critical application files exist."""
    print_header("CRITICAL FILES CHECK")
    
    critical_files = [
        'launch.py', 'enhanced_launcher.py', 'server.py', 'backend.py',
        'processing_engine.py', 'ocr_utils.py', 'data_harvesters.py',
        'custom_patterns.py', 'config.py', 'excel_generator.py',
        'file_utils.py', 'custom_exceptions.py', 'version.py',
        'web/index.html', 'web/app.js', 'requirements.txt', 'START.bat'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} critical files are missing!")
    else:
        print("\n✅ All critical files present")

def check_network_and_ports():
    """Check network connectivity and port availability."""
    print_header("NETWORK & PORTS CHECK")
    
    try:
        import socket
        
        # Check if port 5000 is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result == 0:
            print("⚠️  Port 5000 is already in use")
            print("   Another Flask application might be running")
        else:
            print("✅ Port 5000 is available")
            
    except Exception as e:
        print(f"❌ Network check failed: {e}")
    
    # Test localhost connectivity
    try:
        import requests
        response = requests.get("http://127.0.0.1", timeout=2)
        print("✅ Localhost connectivity OK")
    except:
        print("✅ Localhost not responding (this is normal)")

def run_webview_test():
    """Run a simple webview test."""
    print_header("WEBVIEW FUNCTIONALITY TEST")
    
    try:
        import webview
        print("🧪 Running webview test...")
        
        # Create a simple test window
        webview.create_window(
            'Test Window', 
            'data:text/html,<h1>Test Window</h1><p>If you can see this, webview is working!</p>',
            width=400,
            height=300
        )
        
        print("✅ Test window created successfully")
        print("   A test window should appear briefly...")
        
        # Start webview with a timeout
        import threading
        import time
        
        def close_after_delay():
            time.sleep(3)
            try:
                webview.windows[0].destroy()
            except:
                pass
        
        closer_thread = threading.Thread(target=close_after_delay, daemon=True)
        closer_thread.start()
        
        webview.start(debug=False)
        print("✅ Webview test completed successfully")
        
    except Exception as e:
        print(f"❌ Webview test failed: {e}")
        print("   This indicates a webview backend issue")

def main():
    """Run all diagnostic checks."""
    print("🔍 KYO QA Tool System Diagnostic")
    print("This script will check your system for potential issues.")
    
    try:
        check_python_environment()
        check_dependencies()
        check_webview_backend()
        check_tesseract()
        check_critical_files()
        check_network_and_ports()
        
        print_header("SUMMARY")
        print("Diagnostic complete!")
        print("\nIf any issues were found above, please address them before")
        print("running the application. The Enhanced Visual Launcher may")
        print("provide additional troubleshooting information.")
        
        # Ask if user wants to run webview test
        try:
            answer = input("\nWould you like to run a webview functionality test? (y/n): ")
            if answer.lower().startswith('y'):
                run_webview_test()
        except KeyboardInterrupt:
            print("\nDiagnostic cancelled by user.")
            
    except KeyboardInterrupt:
        print("\nDiagnostic cancelled by user.")
    except Exception as e:
        print(f"\nDiagnostic failed with error: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()