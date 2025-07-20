# server.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

import os
import shutil
import tempfile
import zipfile
import logging
from pathlib import Path
from flask import Flask, request, abort, send_file, render_template, jsonify
from werkzeug.utils import secure_filename

from backend import start_processing_job, get_job_status
from custom_patterns import get_pattern_strings, save_patterns
from config import ensure_directories

# Initialize directories
ensure_directories()

# Configure logging
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="web", static_folder="web", static_url_path="")

# Increase the maximum file upload size to 1 GB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 

# Global variable to store the current job ID
current_job_id = None
final_output_path = None

@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")

@app.route("/api/process", methods=["POST"])
def api_process():
    """Process uploaded files."""
    global current_job_id, final_output_path
    current_job_id = None
    final_output_path = None
    
    excel = request.files.get("excel")
    uploaded_files = request.files.getlist("pdfs[]")
    
    if not excel or not uploaded_files:
        logger.warning("Missing Excel template or PDF/ZIP files in request")
        return abort(400, "Missing Excel template or PDF/ZIP files.")

    # Create temporary directory for uploaded files
    workdir = tempfile.mkdtemp(prefix="qa_tool_")
    logger.info(f"Created temporary directory: {workdir}")
    
    try:
        # Save Excel template
        excel_path = os.path.join(workdir, secure_filename(excel.filename))
        excel.save(excel_path)
        logger.info(f"Saved Excel template: {excel.filename}")
        
        # Process uploaded files (PDFs and ZIPs)
        pdf_paths = []
        for f in uploaded_files:
            filename = secure_filename(f.filename)
            file_path = os.path.join(workdir, filename)
            f.save(file_path)
            logger.info(f"Saved uploaded file: {filename}")

            if filename.lower().endswith('.zip'):
                # Extract PDFs from ZIP
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            if (member.lower().endswith('.pdf') and 
                                not member.startswith('__MACOSX') and
                                not member.startswith('.DS_Store')):
                                
                                # Create safe filename for extracted PDF
                                base_name = Path(filename).stem
                                pdf_name = Path(member).name
                                extracted_filename = f"{base_name}_{pdf_name}"
                                extracted_path = os.path.join(workdir, extracted_filename)
                                
                                # Extract the file
                                with zip_ref.open(member) as source, open(extracted_path, "wb") as target:
                                    shutil.copyfileobj(source, target)
                                pdf_paths.append(extracted_path)
                                logger.info(f"Extracted PDF: {pdf_name} from {filename}")
                                
                except zipfile.BadZipFile:
                    logger.warning(f"Skipped corrupted ZIP file: {filename}")
                    continue
                    
            elif filename.lower().endswith('.pdf'):
                pdf_paths.append(file_path)

        if not pdf_paths:
            shutil.rmtree(workdir)
            logger.warning("No PDF files found in uploaded files")
            return abort(400, "No PDF files found in the selection or ZIP archives.")

        logger.info(f"Starting processing job with {len(pdf_paths)} PDF files")
        current_job_id = start_processing_job(pdf_paths)
        
        return jsonify({"status": "started", "job_id": current_job_id})
        
    except Exception as e:
        logger.error(f"Error in api_process: {e}", exc_info=True)
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
        return abort(500, f"Server error: {e}")

@app.route("/api/status")
def api_status():
    """Get the status of the current processing job."""
    global current_job_id, final_output_path
    
    if not current_job_id:
        return jsonify([])
    
    try:
        status = get_job_status(current_job_id)
        if not status:
            return jsonify([])
        
        # Convert status to message format expected by frontend
        messages = []
        
        # Add log messages
        for log_entry in status.get('log', []):
            messages.append({"type": "log", "msg": log_entry})
        
        # Add progress info
        if status.get('total_files', 0) > 0:
            messages.append({
                "type": "progress", 
                "current": status.get('processed_files', 0),
                "total": status.get('total_files', 0)
            })
        
        # Add file completion status
        for result in status.get('results', []):
            messages.append({
                "type": "file_complete",
                "status": result.get('status', 'unknown')
            })
            
            # Add review items
            if result.get('status') == 'review':
                messages.append({
                    "type": "review_item",
                    "data": {
                        "filename": result.get('filename', ''),
                        "reason": result.get('reason', 'Unknown error')
                    }
                })
        
        # Add finish status
        if status.get('status') == 'complete':
            messages.append({"type": "finish", "status": "Complete"})
            # Note: Excel file path would be handled differently in this version
        elif status.get('status') == 'error':
            messages.append({"type": "finish", "status": "Error"})
        
        return jsonify(messages)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}", exc_info=True)
        return jsonify([{"type": "log", "msg": f"Error getting status: {e}"}])

@app.route("/api/get-result")
def api_get_result():
    """Download the result file."""
    # This would need to be implemented based on how the excel_generator 
    # saves files in the current version
    return abort(404, "Result download not implemented in this version.")

@app.route('/api/patterns', methods=['GET', 'POST'])
def handle_patterns():
    """Handle pattern management (GET to retrieve, POST to save)."""
    try:
        if request.method == 'GET':
            model_patterns, qa_patterns = get_pattern_strings()
            return jsonify({
                'model_patterns': model_patterns, 
                'qa_patterns': qa_patterns
            })
            
        elif request.method == 'POST':
            data = request.json
            if not data:
                return abort(400, "No JSON data provided")
                
            model_patterns = data.get('model_patterns', [])
            qa_patterns = data.get('qa_patterns', [])
            
            save_patterns(model_patterns, qa_patterns)
            logger.info("Patterns saved successfully")
            return jsonify({'status': 'success'})
            
    except Exception as e:
        logger.error(f"Error handling patterns: {e}", exc_info=True)
        return abort(500, f"Server error: {e}")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)