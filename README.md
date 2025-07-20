KYO QA ServiceNow Knowledge Tool v30.2.0
A powerful desktop application for automating the extraction of key information from Kyocera QA/service PDFs using OCR and AI-powered pattern matching.

Author: Kenneth Walker

Date: 2025-07-19
Version: 30.2.0

Features
Automated Setup: Double-click START.bat to automatically create a virtual environment and install all dependencies on the first run.

Modern Web UI: A responsive user interface that runs in its native desktop window, designed with official Kyocera branding.

Flexible File Input: Process individual PDFs, multiple PDFs at once, or ZIP archives containing PDFs.

Live Progress Tracking: Real-time progress bars, status updates, and a detailed log viewer.

Review System: Files that cannot be processed automatically are flagged in a "Needs Review" tab for manual inspection.

Detailed Logging: All operations are recorded  kyo_qa_tool.log for easy troubleshooting.

Requirements
Windows 10/11 (64-bit)

Python 3.9 or higher (ensure it's added to your system's PATH)

Tesseract OCR 5.0+ (ensure the installer is run with default settings so the executable is at C:\Program Files\Tesseract-OCR\tesseract.exe)

Installation & Usage
Download and Unzip: Place the entire KYO-QA-Tool-v30.2.0 folder in a convenient location (e.g., your Desktop).

Launch the Application: Navigate inside the folder and double-click the START.bat file.

First Run: A command window will appear and automatically create a venv folder and install all required Python packages. This may take a few moments. The application will launch once complete.

Subsequent Runs: The application will launch immediately.

How to Use the Tool
Select Files:

Click the "Choose file" button.

You can select one or more PDF files directly, or select a single one .zip file containing multiple PDFs.

Start Processing:

Click the "Start Processing" button.

The "Overall Progress" bar will show the status of the entire batch.

Review Results:

Processed Files Tab: Successfully processed files will appear here.

Needs Review Tab: If a file cannot be processed automatically (e.g., a key piece of information is missing), it will be listed here for you to check manually.

Live Log Tab: Shows a real-time stream of the application's operations. This is useful for seeing what's happening behind the scenes.

Troubleshooting
If you encounter an error, please check the kyo_qa_tool.log file located in the main application folder. This file contains detailed information that can help identify the problem.

File Structure
The project is organized as follows for clarity and maintainability.

KYO-QA-Tool-v30.2.0/
│
├── START.bat                 # Main script to launch the application
├── README.md                 # This file
├── requirements.txt          # List of Python dependencies
├── kyo_qa_tool.log           # Log file (created on first run)
│
├── launch.py                 # Core launch and setup logic
├── server.py                 # Web server (Flask)
├── backend.py                # Handles communication between UI and processing
├── processing_engine.py      # Main file processing logic
├── ... (other .py files)     # Helper modules for specific tasks
│
└─── web/
    ├── index.html            # The user interface
    └── app.js                  # JavaScript for UI interactivity

© 2025 Kenneth C. Walker Jr. All rights reserved.