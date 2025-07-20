@echo off
TITLE KYO QA Tool Patcher
ECHO --- KYO QA Tool Automatic Patcher ---
ECHO This script will rename and update all necessary code files.
ECHO.

:: Create the Python patcher script on the fly
ECHO Creating temporary patcher script (apply_patch.py)...
(
    echo import os
    echo import glob
    echo import logging
    echo.
    echo logging.basicConfig(level=logging.INFO, format='%%(asctime)s - %%(levelname)s - %%(message)s')
    echo.
    echo def run_patch():
    echo     logging.info("Starting the KYO QA Tool Patcher...")
    echo     script_dir = os.path.dirname(os.path.abspath(__file__))
    echo     os.chdir(script_dir)
    echo.
    echo     logging.info("--- Renaming Files ---")
    echo     files_to_rename = glob.glob('*_20250719.py') + glob.glob('*_v30_2_0.py')
    echo     if not files_to_rename:
    echo         logging.warning("No files with old naming conventions were found. Skipping renaming.")
    echo     else:
    echo         for old_path in files_to_rename:
    echo             try:
    echo                 new_name = old_path.replace('_20250719', '').replace('_v30_2_0', '')
    echo                 new_path = os.path.join(script_dir, new_name)
    echo                 if os.path.exists(new_path):
    echo                     logging.warning(f"File '{new_path}' already exists. Deleting old file '{old_path}'.")
    echo                     os.remove(old_path)
    echo                 else:
    echo                     os.rename(old_path, new_path)
    echo                     logging.info(f"Renamed '{old_path}' to '{new_name}'")
    echo             except Exception as e:
    echo                 logging.error(f"Could not rename file {old_path}: {e}")
    echo.
    echo     logging.info("--- Patching Import Statements ---")
    echo     all_py_files = glob.glob('*.py')
    echo     replacements = {'_20250719': '', '_v30_2_0': ''}
    echo.
    echo     for py_file in all_py_files:
    echo         if py_file == os.path.basename(__file__):
    echo             continue
    echo         try:
    echo             with open(py_file, 'r', encoding='utf-8') as f:
    echo                 content = original_content = f.read()
    echo             for find_str, replace_str in replacements.items():
    echo                 content = content.replace(find_str, replace_str)
    echo             if content != original_content:
    echo                 with open(py_file, 'w', encoding='utf-8') as f:
    echo                     f.write(content)
    echo                 logging.info(f"Patched imports in: {py_file}")
    echo         except Exception as e:
    echo             logging.error(f"Could not patch file {py_file}: {e}")
    echo.
    echo     logging.info("Patching complete!")
    echo.
    echo if __name__ == '__main__':
    echo     run_patch()
) > apply_patch.py

:: Run the Python patcher script
ECHO.
ECHO Running patcher...
python apply_patch.py

:: Clean up the temporary script
ECHO.
ECHO Cleaning up temporary files...
del apply_patch.py

ECHO.
ECHO --- All files have been updated successfully! ---
ECHO You can now run START.bat to launch the application.
ECHO.
pause
