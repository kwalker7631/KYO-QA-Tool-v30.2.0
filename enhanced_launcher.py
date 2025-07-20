#!/usr/bin/env python3
# enhanced_launcher.py
# Robust visual launcher for KYO QA Tool with fallback options
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

class ConsoleLauncher:
    """Console-based launcher as fallback when GUI isn't available."""
    
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
        self.update_progress(1, 5, "Checking Python version...")
        
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
            self.update_progress(2, 5, "Creating virtual environment...")
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "venv", "venv"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.log_message("Virtual environment created successfully", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.log_message(f"Failed to create virtual environment: {e}", "ERROR")
                return False
        else:
            self.update_progress(2, 5, "Virtual environment exists - OK")
            self.log_message("Using existing virtual environment", "SUCCESS")
            
        time.sleep(1)
        return True
        
    def install_dependencies(self):
        """Install Python dependencies."""
        if self.is_first_run:
            self.update_progress(3, 5, "Installing dependencies...")
            
            # Determine pip executable path
            if os.name == 'nt':  # Windows
                pip_path = os.path.join("venv", "Scripts", "pip.exe")
            else:  # Unix-like
                pip_path = os.path.join("venv", "bin", "pip")
                
            try:
                print("   📦 Installing packages (this may take a moment)...")
                result = subprocess.run(
                    [pip_path, "install", "-r", "requirements.txt"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    self.log_message("All dependencies installed successfully", "SUCCESS")
                else:
                    self.log_message("Some dependencies had issues, but continuing...", "WARNING")
                    if result.stderr:
                        print(f"   Error details: {result.stderr[:200]}...")
                    
            except subprocess.TimeoutExpired:
                self.log_message("Installation timed out, but continuing...", "WARNING")
            except Exception as e:
                self.log_message(f"Error installing dependencies: {e}", "ERROR")
                return False
        else:
            self.update_progress(3, 5, "Dependencies already installed - OK")
            self.log_message("Dependencies check passed", "SUCCESS")
            
        return True
        
    def check_tesseract(self):
        """Check Tesseract OCR installation."""
        self.update_progress(4, 5, "Checking Tesseract OCR...")
        
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
        """Start the Flask server."""
        self.update_progress(5, 5, "Starting application server...")
        
        try:
            # Determine python executable path
            if os.name == 'nt':  # Windows
                python_path = os.path.join("venv", "Scripts", "python.exe")
            else:  # Unix-like
                python_path = os.path.join("venv", "bin", "python")
                
            self.server_process = subprocess.Popen(
                [python_path, "server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.log_message("Server process started")
            
            # Wait for server to be ready
            print("   🔄 Waiting for server to start...")
            for attempt in range(30):  # Wait up to 30 seconds
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:5000", timeout=2)
                    if response.status_code == 200:
                        self.server_ready = True
                        self.log_message("Server is ready!", "SUCCESS")
                        break
                except Exception:
                    pass
                    
                print(f"   ⏳ Still waiting... ({attempt + 1}/30)")
                time.sleep(1)
                
            if not self.server_ready:
                self.log_message("Server failed to start properly", "ERROR")
                return False
                
        except Exception as e:
            self.log_message(f"Failed to start server: {e}", "ERROR")
            return False
            
        return True
        
    def launch_application(self):
        """Launch the main application UI."""
        if not self.server_ready:
            print("❌ Server is not ready. Cannot launch application.")
            return False
            
        self.log_message("Launching application interface...", "SUCCESS")
        
        try:
            # Import and start the UI
            import webview
            
            print("\n🚀 Starting application window...")
            print("   The application will open in a new window.")
            print("   Close this console when you're done with the application.")
            
            # Create the webview window
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
            
        except Exception as e:
            self.log_message(f"Failed to launch UI: {e}", "ERROR")
            print(f"\n❌ Failed to start the application UI: {e}")
            print("\nThis might be due to:")
            print("   • Missing webview dependencies")
            print("   • Display/graphics issues")
            print("   • Antivirus blocking the application")
            print("\nTry running: python launch.py")
            return False
            
    def cleanup(self):
        """Clean up resources."""
        if self.server_process:
            try:
                self.log_message("Shutting down server...", "INFO")
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()
                
    def run(self):
        """Run the complete setup and launch process."""
        print_banner()
        
        try:
            print("\n🔧 Starting setup process...")
            
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
                    self.log_message("Setup complete. You can launch later by running START.bat", "SUCCESS")
                    return True
            except KeyboardInterrupt:
                print("\n\nSetup cancelled by user.")
                return False
                
        except Exception as e:
            self.log_message(f"Setup failed: {e}", "ERROR")
            print(f"\n❌ Setup failed with error: {e}")
            return False
        finally:
            self.cleanup()

class GUILauncher:
    """GUI-based launcher using tkinter."""
    
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
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
        # Configure colors
        self.bg_color = "#F2F2F2"  # Kyocera light grey
        self.accent_color = "#DA291C"  # Kyocera red
        self.text_color = "#282828"  # Kyocera dark grey
        
        self.root.configure(bg=self.bg_color)
        
    def setup_variables(self):
        """Initialize control variables."""
        self.current_step = 0
        self.total_steps = 5
        self.is_first_run = not Path("venv").exists()
        self.server_process = None
        self.server_ready = False
        
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
            text="Step 0 of 5",
            font=("Arial", 10),
            fg="#666666",
            bg=self.bg_color
        )
        self.step_label.pack(pady=5)
        
        # Log area
        log_frame = self.tk.Frame(content_frame, bg="#FFFFFF", relief="sunken", bd=1)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        self.log_text = self.tk.Text(
            log_frame,
            wrap=self.tk.WORD,
            font=("Consolas", 9),
            bg="#FFFFFF",
            fg="#333333",
            state=self.tk.DISABLED
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
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
        
    def launch_application(self):
        """Launch the webview application."""
        try:
            import webview
            webview.create_window(
                'KYO QA ServiceNow Knowledge Tool',
                'http://127.0.0.1:5000',
                width=1200,
                height=800
            )
            self.root.withdraw()
            webview.start(debug=False)
            self.root.deiconify()
        except Exception as e:
            self.messagebox.showerror("Launch Error", f"Failed to start UI: {e}")
            
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
        console_launcher = ConsoleLauncher()
        
        def setup_thread():
            try:
                self.update_progress(1, "Checking Python version...")
                console_launcher.check_python_version()
                time.sleep(1)
                
                self.update_progress(2, "Setting up virtual environment...")
                if not console_launcher.setup_virtual_environment():
                    return
                time.sleep(1)
                
                self.update_progress(3, "Installing dependencies...")
                if not console_launcher.install_dependencies():
                    return
                
                self.update_progress(4, "Checking Tesseract OCR...")
                console_launcher.check_tesseract()
                time.sleep(1)
                
                self.update_progress(5, "Starting server...")
                if not console_launcher.start_server():
                    return
                
                self.server_process = console_launcher.server_process
                self.server_ready = console_launcher.server_ready
                
                self.launch_button.config(state=self.tk.NORMAL)
                self.status_label.config(text="Ready to launch!")
                self.log_message("Setup completed successfully!")
                
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