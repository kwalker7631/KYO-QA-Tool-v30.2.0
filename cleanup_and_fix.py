#!/usr/bin/env python3
# cleanup_and_fix.py
# Script to clean up duplicate files and fix import issues in KYO QA Tool

import os
import glob
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_duplicate_files():
    """Remove duplicate files with old naming conventions."""
    logger.info("=== Cleaning up duplicate files ===")
    
    # Files to remove (old versions with timestamps/version suffixes)
    patterns_to_remove = [
        '*_20250719.py',
        '*_v30_2_0.py'
    ]
    
    removed_count = 0
    for pattern in patterns_to_remove:
        files = glob.glob(pattern)
        for file_path in files:
            try:
                os.remove(file_path)
                logger.info(f"Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                logger.error(f"Failed to remove {file_path}: {e}")
    
    logger.info(f"Removed {removed_count} duplicate files")

def fix_import_statements():
    """Fix import statements in Python files."""
    logger.info("=== Fixing import statements ===")
    
    # Get all Python files
    python_files = glob.glob('*.py')
    
    # Import replacements to fix
    replacements = {
        'from config_v30_2_0 import': 'from config import',
        'from config_20250719 import': 'from config import',
        'import config_v30_2_0': 'import config',
        'import config_20250719': 'import config',
        'from custom_patterns_v30_2_0 import': 'from custom_patterns import',
        'from custom_patterns_20250719 import': 'from custom_patterns import',
        'import custom_patterns_v30_2_0': 'import custom_patterns',
        'import custom_patterns_20250719': 'import custom_patterns',
        'from data_harvesters_v30_2_0 import': 'from data_harvesters import',
        'from data_harvesters_20250719 import': 'from data_harvesters import',
        'from processing_engine_v30_2_0 import': 'from processing_engine import',
        'from processing_engine_20250719 import': 'from processing_engine import',
        'from backend_v30_2_0 import': 'from backend import',
        'from backend_20250719 import': 'from backend import',
        '_v30_2_0': '',
        '_20250719': ''
    }
    
    fixed_count = 0
    for file_path in python_files:
        if file_path == os.path.basename(__file__):
            continue  # Don't modify this cleanup script
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all replacements
            for find_str, replace_str in replacements.items():
                content = content.replace(find_str, replace_str)
            
            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Fixed imports in: {file_path}")
                fixed_count += 1
                
        except Exception as e:
            logger.error(f"Failed to fix imports in {file_path}: {e}")
    
    logger.info(f"Fixed imports in {fixed_count} files")

def create_missing_init_file():
    """Create __init__.py if it doesn't exist."""
    init_file = "__init__.py"
    if not os.path.exists(init_file):
        try:
            with open(init_file, 'w') as f:
                f.write('# KYO QA Tool Package\n')
            logger.info("Created __init__.py")
        except Exception as e:
            logger.error(f"Failed to create __init__.py: {e}")

def verify_critical_files():
    """Verify that all critical files exist."""
    logger.info("=== Verifying critical files ===")
    
    critical_files = [
        'launch.py',
        'server.py', 
        'backend.py',
        'processing_engine.py',
        'ocr_utils.py',
        'data_harvesters.py',
        'custom_patterns.py',
        'config.py',
        'excel_generator.py',
        'file_utils.py',
        'custom_exceptions.py',
        'version.py',
        'web/index.html',
        'web/app.js',
        'requirements.txt',
        'START.bat'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            logger.warning(f"Missing critical file: {file_path}")
        else:
            logger.info(f"✓ Found: {file_path}")
    
    if missing_files:
        logger.error(f"Missing {len(missing_files)} critical files!")
        return False
    else:
        logger.info("All critical files are present")
        return True

def create_directories():
    """Create necessary directories."""
    logger.info("=== Creating necessary directories ===")
    
    directories = [
        'uploads',
        'output', 
        'logs',
        'PDF_TXT',
        '.cache',
        'processed_output'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")

def main():
    """Main cleanup function."""
    logger.info("Starting KYO QA Tool cleanup and fix process...")
    
    try:
        # Step 1: Clean up duplicate files
        cleanup_duplicate_files()
        
        # Step 2: Fix import statements
        fix_import_statements()
        
        # Step 3: Create missing files
        create_missing_init_file()
        
        # Step 4: Create necessary directories
        create_directories()
        
        # Step 5: Verify critical files
        if verify_critical_files():
            logger.info("✅ Cleanup completed successfully!")
            logger.info("You can now run START.bat to launch the application.")
        else:
            logger.error("❌ Cleanup completed but some critical files are missing.")
            logger.error("Please check the logs above and ensure all required files are present.")
        
    except Exception as e:
        logger.error(f"Cleanup failed with error: {e}", exc_info=True)

if __name__ == '__main__':
    main()