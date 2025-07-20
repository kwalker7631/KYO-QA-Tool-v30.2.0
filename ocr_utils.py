# ocr_utils.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import logging
import os

logger = logging.getLogger(__name__)

# --- Tesseract Configuration ---
def init_tesseract():
    """Initialize Tesseract OCR with proper path configuration."""
    try:
        from config import TESSERACT_PATH
        if TESSERACT_PATH and os.path.exists(TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
            logger.info(f"Tesseract configured at: {TESSERACT_PATH}")
            return True
    except (ImportError, AttributeError):
        logger.warning("TESSERACT_PATH not found in config.py. Trying default locations...")
    
    # Try common Windows installation paths
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "tesseract"  # Assume it's in PATH
    ]
    
    for path in common_paths:
        try:
            if path == "tesseract":
                # Test if tesseract is in PATH
                pytesseract.pytesseract.tesseract_cmd = "tesseract"
                # Try a quick test
                pytesseract.get_tesseract_version()
                logger.info("Tesseract found in system PATH")
                return True
            elif os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract found at: {path}")
                return True
        except Exception:
            continue
    
    logger.error("Tesseract OCR not found. Please install Tesseract or update the path in config.py")
    return False

# Initialize Tesseract on module import
TESSERACT_AVAILABLE = init_tesseract()

def process_single_document(filepath):
    """
    Performs OCR on a single PDF document and returns the full text.

    Args:
        filepath (str): The absolute path to the PDF file.

    Returns:
        str: The extracted text from the entire document.
    
    Raises:
        Exception: If the document cannot be opened or processed.
    """
    logger.info(f"Starting OCR process for: {os.path.basename(filepath)}")
    
    if not TESSERACT_AVAILABLE:
        raise Exception("Tesseract OCR is not available. Please install and configure Tesseract.")
    
    full_text = ""
    
    try:
        doc = fitz.open(filepath)
        
        # Check if document is encrypted
        if doc.is_encrypted:
            doc.close()
            raise Exception("Document is password protected and cannot be processed.")
        
        total_pages = len(doc)
        logger.info(f"Processing {total_pages} pages...")
        
        for page_num in range(total_pages):
            try:
                page = doc.load_page(page_num)
                
                # Try to extract text directly first (faster for text-based PDFs)
                direct_text = page.get_text().strip()
                if direct_text:
                    full_text += direct_text + "\n\n"
                    logger.debug(f"Extracted text directly from page {page_num + 1}")
                else:
                    # Use OCR for image-based content
                    logger.debug(f"Using OCR for page {page_num + 1}")
                    pix = page.get_pixmap(dpi=300)  # Higher DPI for better OCR accuracy
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    
                    try:
                        page_text = pytesseract.image_to_string(img, lang='eng')
                        full_text += page_text + "\n\n"
                    except pytesseract.TesseractNotFoundError:
                        logger.error("Tesseract is not installed or not in your PATH.")
                        raise Exception("Tesseract OCR is not installed or configured correctly.")
                    except Exception as ocr_error:
                        logger.warning(f"OCR failed on page {page_num + 1}: {ocr_error}")
                        continue
                        
            except Exception as page_error:
                logger.warning(f"Failed to process page {page_num + 1}: {page_error}")
                continue

        doc.close()
        
        if not full_text.strip():
            raise Exception("No text could be extracted from the document.")
            
        logger.info(f"Successfully extracted text from {os.path.basename(filepath)}")
        return full_text
        
    except Exception as e:
        logger.error(f"Failed to process PDF file {os.path.basename(filepath)}: {e}")
        raise