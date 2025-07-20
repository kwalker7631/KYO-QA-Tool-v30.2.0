@echo off
TITLE KYO QA ServiceNow Knowledge Tool Launcher
COLOR 0F

ECHO.
ECHO ++--------------------------------------------------------------------------------------++
ECHO ++--------------------------------------------------------------------------------------++
ECHO ++                                                                                      ++
ECHO ++                                                                                      ++
ECHO ++                                                                                      ++
ECHO ++   888    d8P Y88b   d88P  .d88888b.   .d8888b.  8888888888 8888888b.         d8888   ++
ECHO ++   888   d8P   Y88b d88P  d88P^^^Y88b d88P  Y88b 888        888   Y88b       d88888   ++
ECHO ++   888  d8P     Y88o88P   888     888 888    888 888        888    888      d88P888   ++
ECHO ++   888d88K       Y888P    888     888 888        8888888    888   d88P     d88P 888   ++
ECHO ++   8888888b       888     888     888 888        888        8888888P^     d88P  888   ++
ECHO ++   888  Y88b      888     888     888 888    888 888        888 T88b     d88P   888   ++
ECHO ++   888   Y88b     888     Y88b. .d88P Y88b  d88P 888        888  T88b   d8888888888   ++
ECHO ++   888    Y88b    888      ^Y88888P^   ^Y8888P^  8888888888 888   T88b d88P     888   ++
ECHO ++                                                                                      ++
ECHO ++                                                                                      ++
ECHO ++                                                                                      ++
ECHO ++--------------------------------------------------------------------------------------++
ECHO ++--------------------------------------------------------------------------------------++
ECHO.
ECHO                    ServiceNow Knowledge Tool v30.2.0
ECHO                           by Kenneth Walker
ECHO.
ECHO    ++---------------------------------------------------------------++
ECHO.

REM Check Python installation first
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    ECHO ❌ ERROR: Python is not installed or not in PATH
    ECHO.
    ECHO Please install Python 3.9+ from: https://www.python.org/downloads/
    ECHO Make sure to check "Add Python to PATH" during installation
    ECHO.
    PAUSE
    EXIT /B 1
)

REM Check for critical files
SET MISSING_FILES=
IF NOT EXIST requirements.txt SET MISSING_FILES=%MISSING_FILES% requirements.txt
IF NOT EXIST server.py SET MISSING_FILES=%MISSING_FILES% server.py
IF NOT EXIST backend.py SET MISSING_FILES=%MISSING_FILES% backend.py

IF NOT "%MISSING_FILES%"=="" (
    ECHO ❌ ERROR: Missing critical files:%MISSING_FILES%
    ECHO.
    ECHO Please ensure all application files are in this directory:
    FOR %%F IN (%MISSING_FILES%) DO ECHO    • %%F
    ECHO.
    PAUSE
    EXIT /B 1
)

REM Check if this is the first run
IF NOT EXIST venv (
    ECHO 🆕 First time setup detected
    ECHO We'll guide you through the initial setup process
    ECHO.
    GOTO FIRST_RUN
)

REM Regular run - give user options
:REGULAR_RUN
ECHO Choose your launcher:
ECHO.
IF EXIST enhanced_launcher.py (
    ECHO [1] Smart Enhanced Launcher  ^(Auto-detects best mode^)
) ELSE (
    ECHO [1] Smart Enhanced Launcher  ^(⚠️  File missing^)
)
IF EXIST simple_launcher.py (
    ECHO [2] Simple Console Launcher  ^(No GUI, always works^)
) ELSE (
    ECHO [2] Simple Console Launcher  ^(⚠️  File missing^)
)
IF EXIST launch.py (
    ECHO [3] Direct Launch           ^(Skip setup, fastest^)
) ELSE (
    ECHO [3] Direct Launch           ^(⚠️  File missing^)
)
IF EXIST diagnose_system.py (
    ECHO [4] Diagnostics             ^(Check for problems^)
) ELSE (
    ECHO [4] Diagnostics             ^(⚠️  File missing^)
)
ECHO [5] Basic Setup               ^(Create venv and install deps^)
ECHO [6] Exit
ECHO.
SET /P choice="Enter your choice (1-6): "

IF "%choice%"=="1" GOTO SMART_LAUNCHER
IF "%choice%"=="2" GOTO SIMPLE_LAUNCHER  
IF "%choice%"=="3" GOTO DIRECT_LAUNCH
IF "%choice%"=="4" GOTO DIAGNOSTICS
IF "%choice%"=="5" GOTO BASIC_SETUP
IF "%choice%"=="6" GOTO EXIT
ECHO ❌ Invalid choice. Please enter 1-6.
GOTO REGULAR_RUN

:FIRST_RUN
ECHO 🚀 Starting first-time setup...
IF EXIST simple_launcher.py (
    ECHO Using the Simple Console Launcher for reliability
    TIMEOUT /T 2 /NOBREAK >NUL
    GOTO SIMPLE_LAUNCHER
) ELSE (
    ECHO Simple launcher not found, using basic setup
    TIMEOUT /T 2 /NOBREAK >NUL
    GOTO BASIC_SETUP
)

:SMART_LAUNCHER
ECHO.
ECHO ++==============================================================++
ECHO ++                🎯 Smart Enhanced Launcher                    ++
ECHO ++==============================================================++
ECHO.

IF NOT EXIST enhanced_launcher.py (
    ECHO ❌ ERROR: enhanced_launcher.py not found
    ECHO Please ensure all files are in the correct directory
    ECHO Falling back to basic setup...
    TIMEOUT /T 3 /NOBREAK >NUL
    GOTO BASIC_SETUP
)

ECHO Starting enhanced launcher with automatic GUI/console detection...
ECHO.

REM Create basic venv if it doesn't exist
IF NOT EXIST venv (
    ECHO 🔧 Creating virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        ECHO ❌ ERROR: Failed to create virtual environment
        ECHO Please ensure Python 3.9+ is installed
        PAUSE
        GOTO REGULAR_RUN
    )
)

REM Run the enhanced launcher
ECHO 🚀 Launching enhanced setup interface...
python enhanced_launcher.py

REM Check if the launcher ran successfully
IF ERRORLEVEL 1 (
    ECHO.
    ECHO ⚠️  Enhanced launcher encountered an issue
    ECHO Falling back to Simple Console Launcher...
    ECHO.
    TIMEOUT /T 3 /NOBREAK >NUL
    GOTO SIMPLE_LAUNCHER
)

GOTO END

:SIMPLE_LAUNCHER
ECHO.
ECHO ++=============================================================++
ECHO ++               🖥️  Simple Console Launcher                   ++
ECHO ++=============================================================++
ECHO.

IF NOT EXIST simple_launcher.py (
    ECHO ❌ ERROR: simple_launcher.py not found
    ECHO Please ensure all files are in the correct directory
    ECHO Falling back to basic setup...
    TIMEOUT /T 3 /NOBREAK >NUL
    GOTO BASIC_SETUP
)

ECHO Using console-only setup (no GUI required)
ECHO This mode works on all systems and provides step-by-step feedback
ECHO.

REM Run the simple launcher
python simple_launcher.py

REM Check if it ran successfully
IF ERRORLEVEL 1 (
    ECHO.
    ECHO ❌ Simple launcher failed
    ECHO Trying direct launch method...
    ECHO.
    TIMEOUT /T 3 /NOBREAK >NUL
    GOTO DIRECT_LAUNCH
)

GOTO END

:DIRECT_LAUNCH
ECHO.
ECHO ++==============================================================++
ECHO ++                    ⚡ Direct Launch                          ++
ECHO ++==============================================================++
ECHO.

IF NOT EXIST launch.py (
    ECHO ❌ ERROR: launch.py not found
    ECHO Please ensure all application files are present
    ECHO Falling back to basic setup...
    TIMEOUT /T 3 /NOBREAK >NUL
    GOTO BASIC_SETUP
)

ECHO Using direct launch (assumes setup is already complete)
ECHO.

IF NOT EXIST venv (
    ECHO ❌ ERROR: Virtual environment not found
    ECHO Please run setup first using option 2 or 5
    PAUSE
    GOTO REGULAR_RUN
)

ECHO 🔧 Activating virtual environment...
CALL venv\Scripts\activate.bat

ECHO 📦 Checking dependencies...
pip install -q -r requirements.txt

ECHO 🚀 Starting application...
python launch.py

IF ERRORLEVEL 1 (
    ECHO.
    ECHO ❌ Direct launch failed
    ECHO Try running diagnostics (option 4) to identify issues
    PAUSE
)

GOTO END

:BASIC_SETUP
ECHO.
ECHO ++=============================================================++
ECHO ++                   🔧 Basic Setup Mode                       ++
ECHO ++=============================================================++
ECHO.
ECHO This will create a virtual environment and install dependencies
ECHO without launching the application.
ECHO.

REM Create virtual environment
IF NOT EXIST venv (
    ECHO 🔧 Creating virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        ECHO ❌ ERROR: Failed to create virtual environment
        ECHO Please ensure Python 3.9+ is installed and accessible
        PAUSE
        GOTO REGULAR_RUN
    )
    ECHO ✅ Virtual environment created successfully
) ELSE (
    ECHO ✅ Virtual environment already exists
)

REM Activate and install dependencies
ECHO 📦 Activating virtual environment...
CALL venv\Scripts\activate.bat

ECHO 📦 Installing/upgrading pip...
python -m pip install --upgrade pip

ECHO 📦 Installing dependencies from requirements.txt...
pip install -r requirements.txt

IF ERRORLEVEL 1 (
    ECHO.
    ECHO ⚠️  Some dependencies may have failed to install
    ECHO Installing critical packages individually...
    
    pip install Flask
    pip install webview
    pip install requests
    pip install Pillow
    pip install PyMuPDF
    pip install pandas
    pip install pytesseract
    pip install openpyxl
    
    ECHO.
    ECHO ✅ Critical packages installation attempted
) ELSE (
    ECHO ✅ All dependencies installed successfully
)

ECHO.
ECHO 🎉 Basic setup complete!
ECHO.
ECHO You can now:
ECHO   • Run option 1 or 2 to launch the application
ECHO   • Run option 3 for direct launch (if launch.py exists)
ECHO   • Access the application at http://127.0.0.1:5000 (if server is running)
ECHO.
PAUSE
GOTO REGULAR_RUN

:DIAGNOSTICS
ECHO.
ECHO ++=============================================================++
ECHO ++                    🔍 System Diagnostics                    ++
ECHO ++=============================================================++
ECHO.

IF NOT EXIST diagnose_system.py (
    ECHO ❌ ERROR: diagnose_system.py not found
    ECHO.
    ECHO Manual diagnostic check:
    ECHO.
    ECHO Checking Python...
    python --version
    ECHO.
    ECHO Checking virtual environment...
    IF EXIST venv (
        ECHO ✅ Virtual environment exists
    ) ELSE (
        ECHO ❌ Virtual environment missing
    )
    ECHO.
    ECHO Checking critical files...
    FOR %%F IN (server.py backend.py requirements.txt launch.py) DO (
        IF EXIST %%F (
            ECHO ✅ %%F
        ) ELSE (
            ECHO ❌ %%F
        )
    )
    PAUSE
    GOTO REGULAR_RUN
)

ECHO Running comprehensive system diagnostics...
ECHO This will help identify any issues with your setup
ECHO.

python diagnose_system.py

ECHO.
ECHO Diagnostics complete. Check the output above for any issues.
PAUSE
GOTO REGULAR_RUN

:EXIT
ECHO.
ECHO 👋 Thank you for using the KYO QA Tool!
ECHO.
TIMEOUT /T 2 /NOBREAK >NUL
EXIT /B 0

:END
ECHO.
ECHO ++=========================================================++
ECHO.
ECHO 🏁 Session complete!
ECHO.
ECHO 💡 Troubleshooting tips:
ECHO    • Check kyo_qa_tool.log for detailed error messages
ECHO    • Run diagnostics (option 4) if you encounter issues  
ECHO    • Simple Console Launcher (option 2) works on all systems
ECHO    • Direct Launch (option 3) is fastest for repeat use
ECHO    • Basic Setup (option 5) for manual environment setup
ECHO.
ECHO 🔗 Support resources:
ECHO    • Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
ECHO    • Python: https://www.python.org/downloads/
ECHO.
ECHO Press any key to close this window...
PAUSE >NUL