@echo off
TITLE KYO QA Tool - Installation Cleanup Utility
COLOR 0E

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
ECHO.
ECHO                    🧹 KYO QA Tool Cleanup                   
ECHO                    Remove Unnecessary Files                  
ECHO ++---------------------------------------------------------------++
ECHO.
ECHO This utility will help you clean up your KYO QA Tool installation
ECHO by removing duplicate, temporary, and unnecessary files.
ECHO.

REM Set variables
SET TOTAL_SIZE=0
SET FILE_COUNT=0
SET FOLDER_COUNT=0

:MAIN_MENU
ECHO ++---------------------------------------------------------------++
ECHO Choose cleanup level:
ECHO.
ECHO [1] Quick Cleanup        ^(Remove duplicates and temp files^)
ECHO [2] Standard Cleanup     ^(Quick + logs and cache^)
ECHO [3] Deep Cleanup         ^(Standard + Python cache^)  
ECHO [4] Fresh Start          ^(Everything except core files^)
ECHO [5] Custom Cleanup       ^(Choose what to remove^)
ECHO [6] Preview Only         ^(Show what would be deleted^)
ECHO [7] Exit
ECHO.
SET /P choice="Enter your choice (1-7): "

IF "%choice%"=="1" GOTO QUICK_CLEANUP
IF "%choice%"=="2" GOTO STANDARD_CLEANUP
IF "%choice%"=="3" GOTO DEEP_CLEANUP
IF "%choice%"=="4" GOTO FRESH_START
IF "%choice%"=="5" GOTO CUSTOM_CLEANUP
IF "%choice%"=="6" GOTO PREVIEW_ONLY
IF "%choice%"=="7" GOTO EXIT

ECHO ❌ Invalid choice. Please enter 1-7.
GOTO MAIN_MENU

:QUICK_CLEANUP
ECHO.
ECHO 🚀 Starting Quick Cleanup...
ECHO.
CALL :REMOVE_DUPLICATES
CALL :REMOVE_TEMP_FILES
CALL :SHOW_SUMMARY
GOTO END

:STANDARD_CLEANUP
ECHO.
ECHO 🧹 Starting Standard Cleanup...
ECHO.
CALL :REMOVE_DUPLICATES
CALL :REMOVE_TEMP_FILES
CALL :REMOVE_LOGS
CALL :REMOVE_CACHE
CALL :SHOW_SUMMARY
GOTO END

:DEEP_CLEANUP
ECHO.
ECHO 🔧 Starting Deep Cleanup...
ECHO.
CALL :REMOVE_DUPLICATES
CALL :REMOVE_TEMP_FILES
CALL :REMOVE_LOGS
CALL :REMOVE_CACHE
CALL :REMOVE_PYTHON_CACHE
CALL :REMOVE_BUILD_FILES
CALL :SHOW_SUMMARY
GOTO END

:FRESH_START
ECHO.
ECHO ⚠️  FRESH START CLEANUP
ECHO This will remove EVERYTHING except core application files!
ECHO Your virtual environment will be deleted and you'll need to run setup again.
ECHO.
SET /P confirm="Are you sure? This cannot be undone! (type YES to confirm): "
IF NOT "%confirm%"=="YES" (
    ECHO Cancelled. Returning to menu.
    GOTO MAIN_MENU
)
ECHO.
ECHO 🗑️  Starting Fresh Start Cleanup...
ECHO.
CALL :REMOVE_DUPLICATES
CALL :REMOVE_TEMP_FILES
CALL :REMOVE_LOGS
CALL :REMOVE_CACHE
CALL :REMOVE_PYTHON_CACHE
CALL :REMOVE_BUILD_FILES
CALL :REMOVE_VENV
CALL :REMOVE_OUTPUT_DIRS
CALL :SHOW_SUMMARY
ECHO.
ECHO ✅ Fresh start complete! Run START.bat to set up everything again.
GOTO END

:CUSTOM_CLEANUP
ECHO.
ECHO 🎯 Custom Cleanup Options
ECHO.
ECHO Choose what to remove ^(y/n for each^):
ECHO.

SET /P dup="Remove duplicate files with old names? (y/n): "
SET /P temp="Remove temporary files? (y/n): "
SET /P logs="Remove log files? (y/n): "
SET /P cache="Remove cache directories? (y/n): "
SET /P pycache="Remove Python __pycache__? (y/n): "
SET /P build="Remove build/dist files? (y/n): "
SET /P venv="Remove virtual environment? (y/n): "
SET /P output="Remove output directories? (y/n): "

ECHO.
ECHO 🧹 Starting Custom Cleanup...
ECHO.

IF /I "%dup%"=="y" CALL :REMOVE_DUPLICATES
IF /I "%temp%"=="y" CALL :REMOVE_TEMP_FILES
IF /I "%logs%"=="y" CALL :REMOVE_LOGS
IF /I "%cache%"=="y" CALL :REMOVE_CACHE
IF /I "%pycache%"=="y" CALL :REMOVE_PYTHON_CACHE
IF /I "%build%"=="y" CALL :REMOVE_BUILD_FILES
IF /I "%venv%"=="y" CALL :REMOVE_VENV
IF /I "%output%"=="y" CALL :REMOVE_OUTPUT_DIRS

CALL :SHOW_SUMMARY
GOTO END

:PREVIEW_ONLY
ECHO.
ECHO 👀 Preview Mode - Showing what would be deleted
ECHO ^(No files will actually be removed^)
ECHO.
SET PREVIEW_MODE=1
CALL :REMOVE_DUPLICATES
CALL :REMOVE_TEMP_FILES
CALL :REMOVE_LOGS
CALL :REMOVE_CACHE
CALL :REMOVE_PYTHON_CACHE
CALL :REMOVE_BUILD_FILES
CALL :SHOW_SUMMARY
SET PREVIEW_MODE=
ECHO.
ECHO 💡 Run cleanup again without preview mode to actually delete these files.
GOTO END

REM ===============================================================
REM CLEANUP FUNCTIONS
REM ===============================================================

:REMOVE_DUPLICATES
ECHO 📁 Removing duplicate files with old naming conventions...

REM Remove files with _20250719 suffix
FOR %%F IN (*_20250719.*) DO (
    CALL :DELETE_FILE "%%F" "Duplicate file with old date suffix"
)

REM Remove files with _v30_2_0 suffix  
FOR %%F IN (*_v30_2_0.*) DO (
    CALL :DELETE_FILE "%%F" "Duplicate file with version suffix"
)

REM Remove files with version numbers in name
FOR %%F IN (*_v30.*) DO (
    CALL :DELETE_FILE "%%F" "Old version file"
)

REM Remove backup files
FOR %%F IN (*.bak *.backup *.old *.orig) DO (
    CALL :DELETE_FILE "%%F" "Backup file"
)

ECHO ✅ Duplicate file cleanup complete
ECHO.
GOTO :EOF

:REMOVE_TEMP_FILES
ECHO 🗂️  Removing temporary files...

REM Remove common temporary files
FOR %%F IN (*.tmp *.temp temp_*.* ~*.* .DS_Store Thumbs.db) DO (
    CALL :DELETE_FILE "%%F" "Temporary file"
)

REM Remove editor temporary files
FOR %%F IN (*.swp *.swo *~ .#*) DO (
    CALL :DELETE_FILE "%%F" "Editor temporary file"
)

REM Remove Python temporary files
FOR %%F IN (temp_launcher.py apply_patch.py) DO (
    IF EXIST "%%F" CALL :DELETE_FILE "%%F" "Python temporary file"
)

ECHO ✅ Temporary file cleanup complete
ECHO.
GOTO :EOF

:REMOVE_LOGS
ECHO 📄 Removing log files...

REM Remove log files but keep the most recent one
FOR %%F IN (*.log) DO (
    IF NOT "%%F"=="kyo_qa_tool.log" (
        CALL :DELETE_FILE "%%F" "Old log file"
    )
)

REM Remove logs directory if it exists
IF EXIST "logs" (
    CALL :DELETE_FOLDER "logs" "Logs directory"
)

REM Remove specific log patterns
FOR %%F IN (debug.log error.log application.log setup.log) DO (
    IF EXIST "%%F" CALL :DELETE_FILE "%%F" "Application log"
)

ECHO ✅ Log file cleanup complete
ECHO.
GOTO :EOF

:REMOVE_CACHE
ECHO 💾 Removing cache directories and files...

REM Remove cache directories
FOR %%D IN (.cache cache .pytest_cache .coverage) DO (
    IF EXIST "%%D" (
        CALL :DELETE_FOLDER "%%D" "Cache directory"
    )
)

REM Remove cache files
FOR %%F IN (*.cache *.cached) DO (
    CALL :DELETE_FILE "%%F" "Cache file"
)

ECHO ✅ Cache cleanup complete
ECHO.
GOTO :EOF

:REMOVE_PYTHON_CACHE
ECHO 🐍 Removing Python cache files...

REM Remove __pycache__ directories recursively
FOR /D /R . %%D IN (__pycache__) DO (
    IF EXIST "%%D" (
        CALL :DELETE_FOLDER "%%D" "Python cache directory"
    )
)

REM Remove .pyc files
FOR /R . %%F IN (*.pyc) DO (
    CALL :DELETE_FILE "%%F" "Python compiled file"
)

REM Remove .pyo files
FOR /R . %%F IN (*.pyo) DO (
    CALL :DELETE_FILE "%%F" "Python optimized file"
)

ECHO ✅ Python cache cleanup complete
ECHO.
GOTO :EOF

:REMOVE_BUILD_FILES
ECHO 🔨 Removing build and distribution files...

REM Remove build directories
FOR %%D IN (build dist *.egg-info .eggs) DO (
    IF EXIST "%%D" (
        CALL :DELETE_FOLDER "%%D" "Build directory"
    )
)

REM Remove setup files
FOR %%F IN (MANIFEST.in setup.cfg) DO (
    IF EXIST "%%F" CALL :DELETE_FILE "%%F" "Setup file"
)

ECHO ✅ Build file cleanup complete
ECHO.
GOTO :EOF

:REMOVE_VENV
ECHO 🗑️  Removing virtual environment...

IF EXIST "venv" (
    CALL :DELETE_FOLDER "venv" "Virtual environment"
    ECHO ⚠️  Virtual environment removed! You'll need to run the setup again.
) ELSE (
    ECHO ℹ️  No virtual environment found
)

ECHO ✅ Virtual environment cleanup complete
ECHO.
GOTO :EOF

:REMOVE_OUTPUT_DIRS
ECHO 📤 Removing output directories...

REM Remove output directories
FOR %%D IN (output processed_output uploads results) DO (
    IF EXIST "%%D" (
        CALL :DELETE_FOLDER "%%D" "Output directory"
    )
)

REM Remove specific output files
FOR %%F IN (*.xlsx *.csv) DO (
    IF EXIST "processed_output\%%F" (
        CALL :DELETE_FILE "processed_output\%%F" "Output file"
    )
)

ECHO ✅ Output directory cleanup complete
ECHO.
GOTO :EOF

REM ===============================================================
REM UTILITY FUNCTIONS
REM ===============================================================

:DELETE_FILE
SET filename=%~1
SET description=%~2

IF DEFINED PREVIEW_MODE (
    ECHO [PREVIEW] Would delete: %filename% ^(%description%^)
    SET /A FILE_COUNT+=1
) ELSE (
    IF EXIST %filename% (
        DEL /Q %filename% 2>NUL
        IF NOT EXIST %filename% (
            ECHO ✅ Deleted: %filename%
            SET /A FILE_COUNT+=1
        ) ELSE (
            ECHO ❌ Failed to delete: %filename%
        )
    )
)
GOTO :EOF

:DELETE_FOLDER
SET foldername=%~1
SET description=%~2

IF DEFINED PREVIEW_MODE (
    ECHO [PREVIEW] Would delete folder: %foldername% ^(%description%^)
    SET /A FOLDER_COUNT+=1
) ELSE (
    IF EXIST "%foldername%" (
        RD /S /Q "%foldername%" 2>NUL
        IF NOT EXIST "%foldername%" (
            ECHO ✅ Deleted folder: %foldername%
            SET /A FOLDER_COUNT+=1
        ) ELSE (
            ECHO ❌ Failed to delete folder: %foldername%
        )
    )
)
GOTO :EOF

:SHOW_SUMMARY
ECHO.
ECHO ===============================================================
IF DEFINED PREVIEW_MODE (
    ECHO 📊 PREVIEW SUMMARY
    ECHO Would delete: %FILE_COUNT% files and %FOLDER_COUNT% folders
) ELSE (
    ECHO 📊 CLEANUP SUMMARY
    ECHO Deleted: %FILE_COUNT% files and %FOLDER_COUNT% folders
)
ECHO ================================================================
GOTO :EOF

:END
ECHO.
ECHO 🎉 Cleanup operation completed!
ECHO.
ECHO Your installation directory is now cleaner.
ECHO.
ECHO 💡 Recommended next steps:
ECHO   • If you removed the virtual environment, run START.bat to set up again
ECHO   • If you kept the venv, you can run the application normally
ECHO   • Run diagnostics ^(option 4 in START.bat^) to verify everything works
ECHO.
PAUSE
GOTO :EOF

:EXIT
ECHO.
ECHO 👋 Cleanup utility closed. No changes made.
ECHO.
TIMEOUT /T 2 /NOBREAK >NUL
EXIT /B 0