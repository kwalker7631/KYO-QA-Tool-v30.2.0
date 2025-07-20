# KYO QA Tool Fix Guide

## Overview
This guide will help you fix the issues in your KYO QA Tool v30.2.0. The main problems identified are:

1. **Duplicate files** with different naming conventions
2. **Import errors** due to inconsistent module names  
3. **Missing configuration** constants
4. **Tesseract OCR** configuration issues

## Step-by-Step Fix Process

### Step 1: Replace Core Files

Replace the following files with the fixed versions I've provided:

1. **Replace `launch.py`** - Fixed server startup and error handling
2. **Replace `config.py`** - Added missing TESSERACT_PATH and other constants
3. **Replace `ocr_utils.py`** - Fixed Tesseract configuration and error handling
4. **Replace `custom_patterns.py`** - Fixed regex compilation and pattern management
5. **Replace `data_harvesters.py`** - Fixed pattern matching logic
6. **Replace `server.py`** - Fixed API endpoints and file handling

### Step 2: Run Cleanup Script

1. **Save the cleanup script** as `cleanup_and_fix.py` in your main application directory
2. **Run the cleanup script**:
   ```bash
   python cleanup_and_fix.py
   ```
   This will:
   - Remove duplicate files with old naming conventions
   - Fix all import statements
   - Create necessary directories
   - Verify critical files are present

### Step 3: Install/Configure Tesseract OCR

1. **Download Tesseract** from: https://github.com/UB-Mannheim/tesseract/wiki
2. **Install with default settings** to: `C:\Program Files\Tesseract-OCR\`
3. **Verify installation** by opening Command Prompt and typing:
   ```bash
   tesseract --version
   ```

### Step 4: Install Python Dependencies

1. **Open Command Prompt** in your application directory
2. **Create/activate virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: Test the Application

1. **Run the application**:
   ```bash
   python launch.py
   ```
   OR double-click `START.bat`

2. **Check for errors** in the console output and `kyo_qa_tool.log` file

## Key Fixes Applied

### Configuration Issues Fixed
- Added missing `TESSERACT_PATH` constant
- Added proper directory creation
- Fixed import paths

### OCR Processing Fixed
- Automatic Tesseract detection and configuration
- Better error handling for missing OCR
- Support for both text-based and image-based PDFs

### Pattern Matching Fixed
- Proper regex compilation with error handling
- Fixed model and QA number detection
- Better standardization rules application

### Server/Backend Fixed
- Corrected Flask static file serving
- Fixed file upload and processing flow
- Better error handling and logging

### File Management Fixed
- Removed duplicate files
- Fixed all import statements
- Proper temporary file handling

## Common Issues and Solutions

### Issue: "Tesseract not found"
**Solution**: 
- Install Tesseract with default settings
- Or update `TESSERACT_PATH` in `config.py` with correct path

### Issue: "Module not found" errors
**Solution**:
- Run the cleanup script to fix imports
- Ensure you're in the correct directory
- Activate virtual environment

### Issue: Files not processing
**Solution**:
- Check `kyo_qa_tool.log` for specific errors
- Ensure PDFs are not password protected
- Verify Tesseract is working

### Issue: Web interface not loading
**Solution**:
- Check if Flask server started (look for "Running on http://127.0.0.1:5000")
- Try accessing http://127.0.0.1:5000 directly in browser
- Check firewall/antivirus settings

## File Structure After Fix

```
KYO-QA-Tool-v30.2.0/
├── START.bat                 # Application launcher
├── launch.py                 # Main application script
├── server.py                 # Flask web server
├── backend.py                # Background processing
├── processing_engine.py      # Main processing logic
├── ocr_utils.py              # OCR functionality
├── data_harvesters.py        # Pattern matching
├── custom_patterns.py        # Pattern management
├── config.py                 # Configuration
├── excel_generator.py        # Excel output
├── file_utils.py             # File handling
├── custom_exceptions.py      # Custom errors
├── version.py                # Version info
├── requirements.txt          # Dependencies
├── web/
│   ├── index.html           # Web interface
│   └── app.js               # Frontend JavaScript
├── uploads/                 # Temporary uploads
├── output/                  # Processing output
├── logs/                    # Log files
└── kyo_qa_tool.log         # Main log file
```

## Testing Checklist

After applying fixes, test these features:

- [ ] Application starts without errors
- [ ] Web interface loads correctly
- [ ] File upload works (PDF and ZIP)
- [ ] OCR processing works on sample PDF
- [ ] Pattern matching finds models/QA numbers
- [ ] Excel report generation works
- [ ] Pattern manager opens and saves
- [ ] Log output appears correctly

## Need Help?

If you encounter issues after following this guide:

1. Check the `kyo_qa_tool.log` file for detailed error messages
2. Ensure all dependencies are installed correctly
3. Verify Tesseract OCR is properly configured
4. Compare your setup with the working GitHub version you referenced

The fixes provided should resolve the main structural issues with your application and get it running properly.