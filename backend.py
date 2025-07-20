# backend.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

import uuid
import threading
import logging
from processing_engine import process_files

# --- Job Management ---

# A dictionary to store the status of background jobs.
# In a real-world multi-user app, this would be a database or a more robust store.
jobs = {}
logger = logging.getLogger(__name__)

def start_processing_job(filepaths):
    """
    Starts a file processing job in a background thread.
    
    Args:
        filepaths (list): A list of absolute paths to the files to be processed.
        
    Returns:
        str: A unique ID for the created job.
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'total_files': len(filepaths),
        'processed_files': 0,
        'results': [],
        'log': [f"Job {job_id} created with {len(filepaths)} files."]
    }
    
    # The target function for the thread needs to be a callable.
    # We use a lambda here to pass the required arguments to the processing function.
    thread = threading.Thread(
        target=lambda: process_files(job_id, filepaths, jobs)
    )
    thread.daemon = True
    thread.start()
    
    logger.info(f"Background processing thread started for job ID: {job_id}")
    return job_id

def get_job_status(job_id):
    """
    Retrieves the status of a specific job.
    
    Args:
        job_id (str): The ID of the job to check.
        
    Returns:
        dict or None: The status dictionary for the job, or None if not found.
    """
    return jobs.get(job_id)
