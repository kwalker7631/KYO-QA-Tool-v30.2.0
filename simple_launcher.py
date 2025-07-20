#!/usr/bin/env python3
# simple_launcher.py
# Robust console-only launcher for KYO QA Tool with proper error handling
# Author: Kenneth Walker

import os
import sys
import time
import subprocess
from pathlib import Path

def print_header():
    """Print header with progress indicator."""
    print("\n" + "="*60)
    print("🚀 KYO QA Tool - Simple Console Launcher")
    print("   No GUI required - Pure console setup")
    print("="*60)

def log_step(step, total, message, status="RUNNING"):
    """Log a step with progress."""
    percentage = int((step / total) * 100)
    status_emoji = {
        "RUNNING": "🔄",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    
    print(f"\n[{step}/{total}] {status_emoji.get(status, '🔄')} {message}")
    if status == "RUNNING":
        print(f"    Progress: {percentage}%")

def check_requirements():
    """Check basic requirements."""
    log_step(1, 7, "Checking Python environment", "RUNNING")
    
    version = sys.version_info
    if version.major < 3:
        log_step(1, 7, f"Python {version.major}.{version.minor} - TOO OLD", "ERROR")
        print("    ERROR: Python 3.x is required")
        return False
    else:
        log_step(1, 7, f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
    
    time.sleep(1)
    return True

def setup_venv():
    """Setup virtual environment."""
    log_step(2, 7, "Setting up virtual environment", "RUNNING")
    
    if not Path("venv").exists():
        print("    Creating new virtual environment...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "venv", "venv"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                log_step(2, 7, "Failed to create virtual environment", "ERROR")
                print(f"    Error: {result.stderr}")
                return False
            log_step(2, 7, "Virtual environment created", "SUCCESS")
        except subprocess.TimeoutExpired:
            log_step(2, 7, "Virtual environment creation timed out", "ERROR")
            return False
        except Exception as e:
            log_step(2, 7, f"Virtual environment creation failed: {e}", "ERROR")
            return False
    else:
        log_step(2, 7, "Virtual environment already exists", "SUCCESS")
    
    time.sleep(1)
    return True

def install_dependencies():
    """Install dependencies with robust error handling."""
    log_step(3, 7, "Installing dependencies", "RUNNING")
    
    # Determine pip path
    if os.name == 'nt':
        pip_path = Path("venv") / "Scripts" / "pip.exe"
        python_path = Path("venv") / "Scripts" / "python.exe"
    else:
        pip_path = Path("venv") / "bin" / "pip"
        python_path = Path("venv") / "bin" / "python"
    
    if not pip_path.exists():
        log_step(3, 7, f"Pip not found at {pip_path}", "ERROR")
        return False
    
    print("    Installing packages... (this may take 2-3 minutes)")
    
    try:
        # Upgrade pip first
        print("    📦 Upgrading pip...")
        subprocess.run(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            timeout=60
        )
        
        # Install from requirements.txt
        print("    📦 Installing from requirements.txt...")
        result = subprocess.run(
            [str(pip_path), "install", "-r", "requirements.txt", "--timeout", "300"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            log_step(3, 7, "Dependencies installed successfully", "SUCCESS")
        else:
            log_step(3, 7, "Some dependency issues, installing critical packages individually", "WARNING")
            print(f"    Warning details: {result.stderr[:200]}")
            
            # Install critical dependencies individually
            critical_deps = ["Flask>=2.0", "webview", "requests", "Pillow", "PyMuPDF", "pandas", "pytesseract"]
            success_count = 0
            
            for dep in critical_deps:
                try:
                    print(f"    🔧 Installing {dep}...")
                    result = subprocess.run(
                        [str(pip_path), "install", dep],
                        capture_output=True,
                        timeout=60,
                        check=True
                    )
                    success_count += 1
                    print(f"    ✅ {dep} installed")
                except Exception:
                    print(f"    ❌ Failed to install {dep}")
            
            if success_count >= len(critical_deps) // 2:
                log_step(3, 7, f"Installed {success_count}/{len(critical_deps)} critical packages", "SUCCESS")
            else:
                log_step(3, 7, f"Only {success_count}/{len(critical_deps)} packages installed", "WARNING")
                
    except subprocess.TimeoutExpired:
        log_step(3, 7, "Dependency installation timed out", "WARNING")
        print("    Continuing anyway - some packages may be missing")
    except Exception as e:
        log_step(3, 7, f"Dependency installation error: {e}", "WARNING")
        print("    Continuing anyway - some packages may be missing")
    
    time.sleep(1)
    return True

def check_critical_dependencies():
    """Check if critical dependencies are available."""
    log_step(4, 7, "Checking critical dependencies", "RUNNING")
    
    # Determine python path
    if os.name == 'nt':
        python_path = Path("venv") / "Scripts" / "python.exe"
    else:
        python_path = Path("venv") / "bin" / "python"
    
    critical_imports = {
        "Flask": "flask",
        "WebView": "webview", 
        "Requests": "requests",
        "PIL": "PIL"
    }
    
    available = {}
    for name, module in critical_imports.items():
        try:
            result = subprocess.run(
                [str(python_path), "-c", f"import {module}; print('OK')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            available[name] = result.returncode == 0
            status = "✅" if available[name] else "❌"
            print(f"    {status} {name}")
        except Exception:
            available[name] = False
            print(f"    ❌ {name}")
    
    # Check if we have enough to run
    required_count = sum(available.values())
    if required_count >= 3:  # Need at least Flask, WebView/Requests, and one other
        log_step(4, 7, f"Critical dependencies available ({required_count}/4)", "SUCCESS")
    else:
        log_step(4, 7, f"Missing critical dependencies ({required_count}/4)", "WARNING")
        print("    Application may have limited functionality")
    
    time.sleep(1)
    return True

def check_tesseract():
    """Check for Tesseract OCR."""
    log_step(5, 7, "Checking Tesseract OCR", "RUNNING")
    
    # Quick check for Tesseract
    tesseract_found = False
    
    # Check common Windows paths
    for path in [r"C:\Program Files\Tesseract-OCR\tesseract.exe", 
                 r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]:
        if os.path.exists(path):
            tesseract_found = True
            break
    
    # Check system PATH
    if not tesseract_found:
        try:
            subprocess.run(["tesseract", "--version"], 
                         capture_output=True, timeout=5, check=True)
            tesseract_found = True
        except:
            pass
    
    if tesseract_found:
        log_step(5, 7, "Tesseract OCR found", "SUCCESS")
    else:
        log_step(5, 7, "Tesseract OCR not found", "WARNING")
        print("    OCR functionality will be limited")
        print("    Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    time.sleep(1)
    return True

def start_server():
    """Start the Flask server with robust error handling."""
    log_step(6, 7, "Starting Flask server", "RUNNING")
    
    # Determine python path in venv
    if os.name == 'nt':
        python_path = Path("venv") / "Scripts" / "python.exe"
    else:
        python_path = Path("venv") / "bin" / "python"
    
    if not python_path.exists():
        log_step(6, 7, f"Python not found at {python_path}", "ERROR")
        return None
        
    if not Path("server.py").exists():
        log_step(6, 7, "server.py not found", "ERROR")
        print("    Make sure all application files are in the current directory")
        return None
    
    try:
        server_process = subprocess.Popen(
            [str(python_path), "server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        print("    Waiting for server to start...")
        
        # Wait for server to be ready with multiple checking methods
        max_attempts = 30
        for attempt in range(max_attempts):
            # Check if process is still running
            if server_process.poll() is not None:
                # Process died, get error info
                stdout, stderr = server_process.communicate()
                log_step(6, 7, "Server process died unexpectedly", "ERROR")
                if stderr:
                    print(f"    Server error: {stderr[:300]}...")
                elif stdout:
                    print(f"    Server output: {stdout[:300]}...")
                return None
            
            # Try multiple methods to check server readiness
            server_ready = False
            
            # Method 1: Try with requests if available
            try:
                result = subprocess.run(
                    [str(python_path), "-c", "import requests; r=requests.get('http://127.0.0.1:5000', timeout=2); print('OK' if r.status_code==200 else 'FAIL')"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    server_ready = True
            except:
                pass
            
            # Method 2: Try with urllib (built-in)
            if not server_ready:
                try:
                    result = subprocess.run(
                        [str(python_path), "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000', timeout=2); print('OK')"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and "OK" in result.stdout:
                        server_ready = True
                except:
                    pass
            
            if server_ready:
                log_step(6, 7, "Server started successfully", "SUCCESS")
                return server_process
                    
            print(f"    ⏳ Checking server... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
        
        log_step(6, 7, "Server failed to respond within timeout", "ERROR")
        # Get any error output
        try:
            stdout, stderr = server_process.communicate(timeout=2)
            if stderr:
                print(f"    Server error: {stderr[:300]}...")
            elif stdout:
                print(f"    Server output: {stdout[:300]}...")
        except:
            pass
        
        # Terminate the non-responsive server
        server_process.terminate()
        return None
        
    except Exception as e:
        log_step(6, 7, f"Failed to start server: {e}", "ERROR")
        return None

def launch_webview(server_process):
    """Launch the webview application with fallback options."""
    log_step(7, 7, "Launching application", "RUNNING")
    
    # Determine python path
    if os.name == 'nt':
        python_path = Path("venv") / "Scripts" / "python.exe"
    else:
        python_path = Path("venv") / "bin" / "python"
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("🚀 Launching KYO QA Tool...")
    print("="*60)
    
    # Try webview first
    try:
        # Check if webview is available
        result = subprocess.run(
            [str(python_path), "-c", "import webview; print('OK')"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("   Starting application window...")
            
            # Create a simple webview launcher script
            launcher_script = '''
import webview
import sys

try:
    webview.create_window(
        'KYO QA ServiceNow Knowledge Tool',
        'http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True
    )
    webview.start(debug=False)
    print("Application closed normally")
except Exception as e:
    print(f"WebView error: {e}")
    sys.exit(1)
'''
            
            # Write and run the launcher
            with open("temp_launcher.py", "w") as f:
                f.write(launcher_script)
            
            try:
                result = subprocess.run([str(python_path), "temp_launcher.py"], timeout=None)
                log_step(7, 7, "Application launched successfully", "SUCCESS")
                
                # Clean up
                try:
                    os.remove("temp_launcher.py")
                except:
                    pass
                    
                print("\n👋 Application closed by user")
                return True
                
            except KeyboardInterrupt:
                print("\n👋 Application cancelled by user")
                return True
            except Exception as e:
                print(f"\n⚠️  WebView had issues: {e}")
                # Fall through to browser option
        else:
            print("   WebView not available, trying browser option...")
            
    except Exception as e:
        print(f"   WebView check failed: {e}")
    
    # Fallback to browser
    log_step(7, 7, "WebView unavailable, using browser fallback", "WARNING")
    print("\n🌐 WebView not available, but the server is running!")
    print("   You can access the application at: http://127.0.0.1:5000")
    print("   Opening in your default web browser...")
    
    try:
        # Try to open browser
        import webbrowser
        webbrowser.open("http://127.0.0.1:5000")
        print("   ✅ Browser opened successfully")
    except Exception as e:
        print(f"   ⚠️  Could not auto-open browser: {e}")
        print("   Please manually open: http://127.0.0.1:5000")
    
    print(f"\n{'='*60}")
    print("🎯 Application is now running!")
    print("   • Web interface: http://127.0.0.1:5000")
    print("   • Close this window when you're done")
    print("   • Or press Ctrl+C to stop the server")
    print(f"{'='*60}")
    
    try:
        input("\nPress Enter when you're done using the application...")
    except KeyboardInterrupt:
        print("\n👋 Stopping server...")
    
    return True

def cleanup_server(server_process):
    """Clean up the server process."""
    if server_process:
        print("\n🛑 Shutting down server...")
        try:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("✅ Server shutdown complete")
            except subprocess.TimeoutExpired:
                print("⚠️  Forcing server shutdown...")
                server_process.kill()
                server_process.wait()
                print("✅ Server forcibly stopped")
        except Exception as e:
            print(f"⚠️  Error during server cleanup: {e}")

def main():
    """Main launcher function."""
    print_header()
    
    server_process = None
    
    try:
        # Run setup steps
        if not check_requirements():
            input("\nPress Enter to exit...")
            return
            
        if not setup_venv():
            input("\nPress Enter to exit...")
            return
            
        if not install_dependencies():
            input("\nPress Enter to exit...")
            return
            
        if not check_critical_dependencies():
            input("\nPress Enter to exit...")
            return
            
        if not check_tesseract():
            input("\nPress Enter to exit...")
            return
            
        server_process = start_server()
        if not server_process:
            input("\nPress Enter to exit...")
            return
        
        # Launch the application
        launch_webview(server_process)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   Check the log files for more details")
    finally:
        cleanup_server(server_process)
        print("\n👋 Launcher finished")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()