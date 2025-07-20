#!/usr/bin/env python3
# enhanced_launcher.py
# Robust visual launcher for KYO QA Tool with proper error handling
# Author: Kenneth Walker

import os
import sys
import time
import threading
import subprocess
from pathlib import Path

def print_banner():
    """Print a nice console banner."""
    print("\n" + "="*70)
    print("🚀 KYO QA Tool - Enhanced Setup & Launcher")
    print("   Author: Kenneth Walker | Version: 30.2.0")
    print("="*70)

def check_gui_availability():
    """Check if GUI (tkinter) is available."""
    try:
        import tkinter as tk
        # Try to create a simple test window
        root = tk.Tk()
        root.withdraw()  # Hide it immediately
        root.destroy()
        return True
    except Exception as e:
        print(f"⚠️  GUI not available: {e}")
        print("   Falling back to console mode...")
        return False

def check_requests_availability():
    """Check if requests module is available, install if needed."""
    try:
        import requests
        return True, requests
    except ImportError:
        print("📦 Installing requests module (required for server checks)...")
        try:
            # Try to install requests
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "requests"],
                capture_output=True,
                check=True,
                timeout=60
            )
            import requests
            print("✅ Requests module installed successfully")
            return True, requests
        except Exception as e:
            print(f"⚠️  Could not install requests: {e}")
            print("   Will use alternative server checking method")
            return False, None

def check_server_with_requests(url, timeout=2):
    """Check server using requests module."""
    try:
        has_requests, requests = check_requests_availability()
        if not has_requests:
            return False
        
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False

def check_server_with_urllib(url, timeout=2):
    """Fallback server check using urllib (built-in)."""
    try:
        import urllib.request
        import socket
        
        # Set timeout
        socket.setdefaulttimeout(timeout)
        
        with urllib.request.urlopen(url) as response:
            return response.getcode() == 200
    except Exception:
        return False

def check_server_ready(url="http://127.0.0.1:5000", timeout=2):
    """Check if server is ready using best available method."""
    # Try requests first (preferred)
    if check_server_with_requests(url, timeout):
        return True
    
    # Fallback to urllib
    if check_server_with_urllib(url, timeout):
        return True
    
    return False

class ConsoleLauncher:
    """Console-based launcher with robust error handling."""
    
    def __init__(self):
        self.is_first_run = not Path("venv").exists()
        self.server_process = None
        self.server_ready = False
        
    def log_message(self, message, level="INFO"):
        """Print a formatted log message."""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "WARNING": "⚠️ ",
            "ERROR": "❌"
        }.get(level, "")
        
        print(f"[{timestamp}] {prefix} {message}")
        
    def update_progress(self, step, total_steps, message):
        """Show progress in console."""
        percentage = int((step / total_steps) * 100)
        bar_length = 30
        filled_length = int(bar_length * step // total_steps)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\n📊 Progress: [{bar}] {percentage}% - Step {step}/{total_steps}")
        self.log_message(message)
        
    def check_python_version(self):
        """Check Python version."""
        self.update_progress(1, 6, "Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            self.log_message(f"Python {version.major}.{version.minor} detected", "WARNING")
            self.log_message("Python 3.9+ recommended for best compatibility", "WARNING")
        else:
            self.log_message(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
        
        time.sleep(1)
        return True
        
    def setup_virtual_environment(self):
        """Create virtual environment if needed."""
        if self.is_first_run:
            self.update_progress(2, 6, "Creating virtual environment...")
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "venv", "venv"],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=120
                )
                self.log_message("Virtual environment created successfully", "SUCCESS")
            except subprocess.TimeoutExpired:
                self.log_message("Virtual environment creation timed out", "ERROR")
                return False
            except subprocess.CalledProcessError as e:
                self.log_message(f"Failed to create virtual environment: {e}", "ERROR")
                if e.stderr:
                    print(f"   Error details: {e.stderr}")
                return False
            except Exception as e:
                self.log_message(f"Unexpected error creating venv: {e}", "ERROR")
                return False
        else:
            self.update_progress(2, 6, "Virtual environment exists - OK")
            self.log_message("Using existing virtual environment", "SUCCESS")
            
        time.sleep(1)
        return True
        
    def install_dependencies(self):
        """Install Python dependencies with better error handling."""
        self.update_progress(3, 6, "Installing/checking dependencies...")
        
        # Determine pip executable path
        if os.name == 'nt':  # Windows
            pip_path = Path("venv") / "Scripts" / "pip.exe"
            python_path = Path("venv") / "Scripts" / "python.exe"
        else:  # Unix-like
            pip_path = Path("venv") / "bin" / "pip"
            python_path = Path("venv") / "bin" / "python"
        
        if not pip_path.exists():
            self.log_message(f"Pip not found at {pip_path}", "ERROR")
            return False
            
        try:
            # Install/upgrade pip first
            print("   📦 Upgrading pip...")
            subprocess.run(
                [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                timeout=60
            )
            
            # Install requirements
            print("   📦 Installing packages from requirements.txt...")
            result = subprocess.run(
                [str(pip_path), "install", "-r", "requirements.txt", "--timeout", "300"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log_message("Dependencies installed successfully", "SUCCESS")
            else:
                self.log_message("Some dependency issues detected", "WARNING")
                print(f"   Warning details: {result.stderr[:300]}...")
                
                # Try to install critical dependencies individually
                critical_deps = ["Flask", "webview", "requests"]
                for dep in critical_deps:
                    try:
                        print(f"   🔧 Installing {dep} individually...")
                        subprocess.run(
                            [str(pip_path), "install", dep],
                            capture_output=True,
                            timeout=60,
                            check=True
                        )
                        self.log_message(f"{dep} installed successfully", "SUCCESS")
                    except Exception:
                        self.log_message(f"Failed to install {dep}", "WARNING")
                
        except subprocess.TimeoutExpired:
            self.log_message("Dependency installation timed out", "WARNING")
            print("   Continuing anyway - some packages may be missing")
        except Exception as e:
            self.log_message(f"Dependency installation error: {e}", "WARNING")
            print("   Continuing anyway - some packages may be missing")
        
        time.sleep(1)
        return True
        
    def check_tesseract(self):
        """Check for Tesseract OCR."""
        self.update_progress(4, 6, "Checking Tesseract OCR...")
        
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]
        
        tesseract_found = False
        for path in tesseract_paths:
            if os.path.exists(path):
                self.log_message(f"Tesseract found at: {path}", "SUCCESS")
                tesseract_found = True
                break
                
        if not tesseract_found:
            # Try system PATH
            try:
                result = subprocess.run(
                    ["tesseract", "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=5
                )
                self.log_message("Tesseract found in system PATH", "SUCCESS")
                tesseract_found = True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
                
        if not tesseract_found:
            self.log_message("Tesseract OCR not found", "WARNING")
            self.log_message("Download from: https://github.com/UB-Mannheim/tesseract/wiki", "WARNING")
            self.log_message("OCR functionality will be limited without Tesseract", "WARNING")
        
        time.sleep(1)
        return True
        
    def start_server(self):
        """Start the Flask server with robust error handling."""
        self.update_progress(5, 6, "Starting application server...")
        
        try:
            # Determine python executable path
            if os.name == 'nt':  # Windows
                python_path = Path("venv") / "Scripts" / "python.exe"
            else:  # Unix-like
                python_path = Path("venv") / "bin" / "python"
            
            if not python_path.exists():
                self.log_message(f"Python not found at {python_path}", "ERROR")
                return False
                
            if not Path("server.py").exists():
                self.log_message("server.py not found", "ERROR")
                return False
                
            self.server_process = subprocess.Popen(
                [str(python_path), "server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.log_message("Server process started, waiting for response...")
            
            # Wait for server to be ready with robust checking
            max_attempts = 30
            for attempt in range(max_attempts):
                # Check if process is still running
                if self.server_process.poll() is not None:
                    # Process died, get error info
                    stdout, stderr = self.server_process.communicate()
                    self.log_message("Server process died unexpectedly", "ERROR")
                    if stderr:
                        print(f"   Server error: {stderr[:300]}...")
                    return False
                
                # Check if server is responding
                if check_server_ready("http://127.0.0.1:5000", timeout=2):
                    self.server_ready = True
                    self.log_message("Server is ready and responding!", "SUCCESS")
                    return True
                    
                print(f"   ⏳ Waiting for server... ({attempt + 1}/{max_attempts})")
                time.sleep(1)
                
            self.log_message("Server failed to respond within timeout", "ERROR")
            # Get any error output
            try:
                stdout, stderr = self.server_process.communicate(timeout=2)
                if stderr:
                    print(f"   Server error: {stderr[:300]}...")
            except:
                pass
            return False
                
        except Exception as e:
            self.log_message(f"Failed to start server: {e}", "ERROR")
            return False
            
    def launch_application(self):
        """Launch the main application UI with proper error handling."""
        if not self.server_ready:
            print("❌ Server is not ready. Cannot launch application.")
            return False
            
        self.update_progress(6, 6, "Launching application interface...")
        
        try:
            # Try to import webview with error handling
            try:
                import webview
            except ImportError as e:
                self.log_message(f"WebView not available: {e}", "ERROR")
                print("\n🌐 WebView not available, but you can still use the application!")
                print("   Open your web browser and go to: http://127.0.0.1:5000")
                input("   Press Enter when you're done using the application...")
                return True
            
            print("\n🚀 Starting application window...")
            print("   The application will open in a new window.")
            print("   Close this console when you're done with the application.")
            
            # Create the webview window with error handling
            try:
                webview.create_window(
                    'KYO QA ServiceNow Knowledge Tool',
                    'http://127.0.0.1:5000',
                    width=1200,
                    height=800,
                    resizable=True
                )
                
                # Start the webview (this will block until the window is closed)
                webview.start(debug=False)
                
                self.log_message("Application window closed", "INFO")
                return True
                
            except Exception as webview_error:
                self.log_message(f"WebView failed to start: {webview_error}", "WARNING")
                print("\n🌐 WebView had issues, but the server is running!")
                print("   You can access the application at: http://127.0.0.1:5000")
                print("   Open that URL in your web browser")
                input("   Press Enter when you're done using the application...")
                return True
            
        except Exception as e:
            self.log_message(f"Failed to launch application: {e}", "ERROR")
            print(f"\n❌ Could not start the application: {e}")
            print("\nTroubleshooting options:")
            print("   • Server may still be running at: http://127.0.0.1:5000")
            print("   • Try opening that URL in your web browser")
            print("   • Check kyo_qa_tool.log for detailed error messages")
            return False
            
    def cleanup(self):
        """Clean up resources."""
        if self.server_process:
            try:
                self.log_message("Shutting down server...", "INFO")
                self.server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.server_process.wait(timeout=5)
                    self.log_message("Server shutdown complete", "SUCCESS")
                except subprocess.TimeoutExpired:
                    self.log_message("Forcing server shutdown...", "WARNING")
                    self.server_process.kill()
                    self.server_process.wait()
                    
            except Exception as e:
                self.log_message(f"Error during cleanup: {e}", "WARNING")
                
    def run(self):
        """Run the complete setup and launch process."""
        print_banner()
        
        try:
            print("\n🔧 Starting comprehensive setup process...")
            
            if not self.check_python_version():
                return False
                
            if not self.setup_virtual_environment():
                return False
                
            if not self.install_dependencies():
                return False
                
            if not self.check_tesseract():
                return False
                
            if not self.start_server():
                return False
                
            print(f"\n{'='*70}")
            print("🎉 Setup completed successfully!")
            print("🚀 Ready to launch the application!")
            print(f"{'='*70}")
            
            # Ask user if they want to launch now
            try:
                choice = input("\nWould you like to launch the application now? (y/n): ").lower()
                if choice.startswith('y'):
                    return self.launch_application()
                else:
                    self.log_message("Setup complete. Server is running at http://127.0.0.1:5000", "SUCCESS")
                    print("You can:")
                    print("  • Open http://127.0.0.1:5000 in your browser")
                    print("  • Run START.bat again and choose option 3 (Direct Launch)")
                    input("Press Enter to shutdown server and exit...")
                    return True
            except KeyboardInterrupt:
                print("\n\nSetup cancelled by user.")
                return False
                
        except Exception as e:
            self.log_message(f"Setup failed: {e}", "ERROR")
            print(f"\n❌ Setup failed with error: {e}")
            print("\nTroubleshooting tips:")
            print("  • Check your internet connection")
            print("  • Ensure Python 3.9+ is properly installed")
            print("  • Try running as administrator if on Windows")
            print("  • Check kyo_qa_tool.log for detailed error messages")
            return False
        finally:
            self.cleanup()

class GUILauncher:
    """GUI-based launcher using tkinter with enhanced error handling."""
    
    def __init__(self):
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            self.tk = tk
            self.ttk = ttk
            self.messagebox = messagebox
            
            self.root = tk.Tk()
            self.setup_window()
            self.setup_variables()
            self.setup_widgets()
        except Exception as e:
            print(f"Failed to initialize GUI: {e}")
            raise
        
    def setup_window(self):
        """Configure the main window with Kyocera branding."""
        self.root.title("KYO QA Tool - Setup & Launcher")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (550 // 2)
        self.root.geometry(f"600x550+{x}+{y}")
        
        # Configure colors
        self.bg_color = "#F2F2F2"  # Kyocera light grey
        self.accent_color = "#DA291C"  # Kyocera red
        self.text_color = "#282828"  # Kyocera dark grey
        
        self.root.configure(bg=self.bg_color)
        
    def setup_variables(self):
        """Initialize control variables."""
        self.current_step = 0
        self.total_steps = 6
        self.server_process = None
        self.server_ready = False
        self.console_launcher = ConsoleLauncher()
        
    def setup_widgets(self):
        """Create and layout all widgets."""
        # Header
        header_frame = self.tk.Frame(self.root, bg=self.bg_color, height=80)
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        title_label = self.tk.Label(
            header_frame, 
            text="KYOCERA", 
            font=("Arial", 24, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(side="left")
        
        subtitle_label = self.tk.Label(
            header_frame,
            text="QA Automation Tool v30.2.0",
            font=("Arial", 16),
            fg=self.text_color,
            bg=self.bg_color
        )
        subtitle_label.pack(side="left", padx=(10, 0))
        
        # Main content
        content_frame = self.tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Status
        self.status_label = self.tk.Label(
            content_frame,
            text="Initializing...",
            font=("Arial", 14, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.status_label.pack(pady=10)
        
        # Progress bar
        progress_frame = self.tk.Frame(content_frame, bg=self.bg_color)
        progress_frame.pack(fill="x", pady=10)
        
        self.progress = self.ttk.Progressbar(
            progress_frame,
            length=400,
            mode='determinate'
        )
        self.progress.pack(pady=5)
        
        # Step indicator
        self.step_label = self.tk.Label(
            content_frame,
            text="Step 0 of 6",
            font=("Arial", 10),
            fg="#666666",
            bg=self.bg_color
        )
        self.step_label.pack(pady=5)
        
        # Log area
        log_frame = self.tk.Frame(content_frame, bg="#FFFFFF", relief="sunken", bd=1)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        text_frame = self.tk.Frame(log_frame)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log_text = self.tk.Text(
            text_frame,
            wrap=self.tk.WORD,
            font=("Consolas", 9),
            bg="#FFFFFF",
            fg="#333333",
            state=self.tk.DISABLED
        )
        
        scrollbar = self.ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = self.tk.Frame(content_frame, bg=self.bg_color)
        button_frame.pack(fill="x", pady=10)
        
        self.launch_button = self.tk.Button(
            button_frame,
            text="Launch Application",
            font=("Arial", 12, "bold"),
            fg="white",
            bg=self.accent_color,
            padx=20,
            pady=10,
            state=self.tk.DISABLED,
            command=self.launch_application
        )
        self.launch_button.pack(side="right", padx=(10, 0))
        
        self.browser_button = self.tk.Button(
            button_frame,
            text="Open in Browser",
            font=("Arial", 12),
            fg=self.text_color,
            bg="#E0E0E0",
            padx=20,
            pady=10,
            state=self.tk.DISABLED,
            command=self.open_browser
        )
        self.browser_button.pack(side="right", padx=(5, 0))
        
        self.close_button = self.tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 12),
            fg=self.text_color,
            bg="#E0E0E0",
            padx=20,
            pady=10,
            command=self.close_application
        )
        self.close_button.pack(side="right")
        
    def log_message(self, message):
        """Add a message to the log area."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state=self.tk.NORMAL)
        self.log_text.insert(self.tk.END, f"[{timestamp}] {message}\n")
        self.log_text.config(state=self.tk.DISABLED)
        self.log_text.see(self.tk.END)
        self.root.update()
        
    def update_progress(self, step, message):
        """Update progress bar and status."""
        progress_value = (step / self.total_steps) * 100
        self.progress['value'] = progress_value
        self.status_label.config(text=message)
        self.step_label.config(text=f"Step {step} of {self.total_steps}")
        self.log_message(message)
        
    def open_browser(self):
        """Open the application in the default web browser."""
        try:
            import webbrowser
            webbrowser.open("http://127.0.0.1:5000")
            self.log_message("Opened application in web browser")
        except Exception as e:
            self.messagebox.showerror("Browser Error", f"Could not open browser: {e}")
            
    def launch_application(self):
        """Launch the webview application."""
        try:
            import webview
            self.log_message("Starting webview application...")
            webview.create_window(
                'KYO QA ServiceNow Knowledge Tool',
                'http://127.0.0.1:5000',
                width=1200,
                height=800
            )
            self.root.withdraw()
            webview.start(debug=False)
            self.root.deiconify()
            self.log_message("Application window closed")
        except Exception as e:
            self.log_message(f"WebView launch failed: {e}")
            self.messagebox.showerror("Launch Error", f"Failed to start UI: {e}\n\nTry using 'Open in Browser' instead.")
            
    def close_application(self):
        """Close the application."""
        if self.server_process:
            try:
                self.server_process.terminate()
            except:
                pass
        self.root.quit()
        
    def run_setup(self):
        """Run the setup process using ConsoleLauncher logic."""
        def setup_thread():
            try:
                # Redirect console launcher output to GUI
                original_print = print
                def gui_print(*args, **kwargs):
                    message = " ".join(str(arg) for arg in args)
                    if message.strip():
                        self.log_message(message)
                
                # Temporarily redirect print
                import builtins
                builtins.print = gui_print
                
                self.update_progress(1, "Checking Python version...")
                self.console_launcher.check_python_version()
                time.sleep(1)
                
                self.update_progress(2, "Setting up virtual environment...")
                if not self.console_launcher.setup_virtual_environment():
                    return
                
                self.update_progress(3, "Installing dependencies...")
                if not self.console_launcher.install_dependencies():
                    return
                
                self.update_progress(4, "Checking Tesseract OCR...")
                self.console_launcher.check_tesseract()
                
                self.update_progress(5, "Starting server...")
                if not self.console_launcher.start_server():
                    return
                
                self.server_process = self.console_launcher.server_process
                self.server_ready = self.console_launcher.server_ready
                
                self.update_progress(6, "Ready to launch!")
                
                # Enable buttons
                self.launch_button.config(state=self.tk.NORMAL)
                self.browser_button.config(state=self.tk.NORMAL)
                self.log_message("Setup completed successfully! Choose how to launch the application.")
                
                # Restore original print
                builtins.print = original_print
                
            except Exception as e:
                self.log_message(f"Setup failed: {e}")
                self.messagebox.showerror("Setup Error", f"Setup failed: {e}")
                
        threading.Thread(target=setup_thread, daemon=True).start()
        
    def run(self):
        """Start the GUI launcher."""
        self.root.after(500, self.run_setup)
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        self.root.mainloop()

def main():
    """Main entry point - choose between GUI and console launcher."""
    try:
        print("🚀 KYO QA Tool Enhanced Launcher")
        print("   Checking system capabilities...")
        
        # Try GUI first, fallback to console
        if check_gui_availability():
            print("✅ GUI available - starting visual launcher...")
            try:
                launcher = GUILauncher()
                launcher.run()
            except Exception as e:
                print(f"❌ GUI launcher failed: {e}")
                print("🔄 Falling back to console launcher...")
                launcher = ConsoleLauncher()
                launcher.run()
        else:
            print("🖥️  Using console launcher...")
            launcher = ConsoleLauncher()
            launcher.run()
            
    except KeyboardInterrupt:
        print("\n\n👋 Launcher cancelled by user.")
    except Exception as e:
        print(f"\n❌ Launcher failed: {e}")
        print("Try running: python launch.py")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()