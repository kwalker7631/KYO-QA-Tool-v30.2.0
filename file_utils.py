# file_utils.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

import os
import zipfile
import logging
from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)

def handle_zip_file(zip_path):
    """
    Extracts all PDF files from a given ZIP archive into a temporary directory.

    Args:
        zip_path (str): The absolute path to the ZIP file.

    Returns:
        list: A list of absolute paths to the extracted PDF files.
        
    Raises:
        zipfile.BadZipFile: If the file is not a valid ZIP archive.
        Exception: For other file-related errors.
    """
    logger.info(f"Handling ZIP file: {zip_path}")
    extracted_files = []
    
    # Create a temporary directory that will be automatically cleaned up.
    # We store it on the class instance to prevent it from being garbage collected.
    # A more robust solution might manage temp directories more explicitly.
    if not hasattr(handle_zip_file, "temp_dirs"):
        handle_zip_file.temp_dirs = []
        
    temp_dir = TemporaryDirectory()
    handle_zip_file.temp_dirs.append(temp_dir)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                # Only extract files, and only if they are PDFs.
                if not member.is_dir() and member.filename.lower().endswith('.pdf'):
                    # To avoid issues with nested paths, extract to a flat structure.
                    # The filename is sanitized to prevent path traversal issues.
                    sanitized_name = os.path.basename(member.filename)
                    target_path = os.path.join(temp_dir.name, sanitized_name)
                    
                    # Extract the file's content and write it to the target path
                    with open(target_path, 'wb') as f:
                        f.write(zip_ref.read(member.filename))
                        
                    extracted_files.append(target_path)
                    logger.info(f"Extracted '{sanitized_name}' from ZIP archive.")

        return extracted_files
        
    except zipfile.BadZipFile:
        logger.error(f"'{zip_path}' is not a valid ZIP file.")
        raise
    except Exception as e:
        logger.error(f"An error occurred while handling the ZIP file {zip_path}: {e}", exc_info=True)
        raise

