# processing_engine.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

import logging
import time
import os

# --- Corrected Imports ---
# Import from the renamed modules
from ocr_utils import process_single_document
from data_harvesters import find_patterns
from excel_generator import create_excel_report
from file_utils import handle_zip_file
from custom_exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

def update_job_progress(job_id, jobs, message, is_error=False):
    """Helper function to update the progress and log of a job."""
    if job_id in jobs:
        jobs[job_id]['log'].append(message)
        if is_error:
            logger.error(message)
        else:
            logger.info(message)
        
        # Update progress percentage
        processed = jobs[job_id]['processed_files']
        total = jobs[job_id]['total_files']
        if total > 0:
            jobs[job_id]['progress'] = int((processed / total) * 100)

def process_files(job_id, filepaths, jobs):
    """
    The main worker function that processes a list of files.
    This function is run in a background thread.
    """
    job = jobs.get(job_id)
    if not job:
        logger.error(f"Job {job_id} not found. Aborting processing.")
        return

    job['status'] = 'processing'
    update_job_progress(job_id, jobs, "Processing job started.")

    all_results = []
    
    # Expand any ZIP files into the list of filepaths
    expanded_filepaths = []
    for path in filepaths:
        if path.lower().endswith('.zip'):
            try:
                unzipped_files = handle_zip_file(path)
                expanded_filepaths.extend(unzipped_files)
                update_job_progress(job_id, jobs, f"Extracted {len(unzipped_files)} files from {os.path.basename(path)}.")
            except Exception as e:
                update_job_progress(job_id, jobs, f"Failed to extract ZIP file {os.path.basename(path)}: {e}", is_error=True)
        else:
            expanded_filepaths.append(path)
            
    # Update total file count after expansion
    job['total_files'] = len(expanded_filepaths)

    for filepath in expanded_filepaths:
        filename = os.path.basename(filepath)
        update_job_progress(job_id, jobs, f"Starting to process: {filename}")
        
        try:
            # Step 1: Perform OCR and get text
            document_text = process_single_document(filepath)
            
            # Step 2: Find patterns in the extracted text
            found_data = find_patterns(document_text)
            found_data['filename'] = filename # Add filename to the results
            
            # Step 3: Add result to the list
            all_results.append(found_data)
            job['results'].append({'filename': filename, 'status': 'success', 'data': found_data})
            update_job_progress(job_id, jobs, f"Successfully processed: {filename}")

        except DocumentProcessingError as e:
            # Handle custom errors for files that need review
            job['results'].append({'filename': filename, 'status': 'review', 'reason': str(e)})
            update_job_progress(job_id, jobs, f"File needs review {filename}: {e}", is_error=True)
            
        except Exception as e:
            # Handle unexpected errors
            job['results'].append({'filename': filename, 'status': 'error', 'reason': str(e)})
            update_job_progress(job_id, jobs, f"An unexpected error occurred with {filename}: {e}", is_error=True)
        
        finally:
            # Increment the processed file count regardless of outcome
            job['processed_files'] += 1
            # Recalculate progress after each file
            update_job_progress(job_id, jobs, f"Finished with {filename}.")

    # Step 4: Create Excel report from all successfully processed files
    try:
        if any(res.get('status') == 'success' for res in job['results']):
            report_path = create_excel_report(all_results)
            update_job_progress(job_id, jobs, f"Excel report created at: {report_path}")
        else:
            update_job_progress(job_id, jobs, "No files were processed successfully, skipping Excel report generation.")
    except Exception as e:
        update_job_progress(job_id, jobs, f"Failed to create Excel report: {e}", is_error=True)

    job['status'] = 'complete'
    update_job_progress(job_id, jobs, "Processing job finished.")

