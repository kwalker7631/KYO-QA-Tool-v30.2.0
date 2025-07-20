# custom_exceptions.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.1.5

import logging

logger = logging.getLogger(__name__)

class DocumentProcessingError(Exception):
    """
    Custom exception for errors that occur during document processing
    which indicate a file should be manually reviewed.
    """
    def __init__(self, message="A processing error occurred that requires manual review."):
        self.message = message
        logger.warning(f"DocumentProcessingError: {self.message}")
        super().__init__(self.message)

class PatternNotFoundError(DocumentProcessingError):
    """
    Raised when a critical pattern is not found in the document text.
    """
    def __init__(self, pattern_name):
        message = f"Critical pattern '{pattern_name}' was not found in the document."
        super().__init__(message)

class OCRProcessingError(Exception):
    """
    Custom exception for critical failures during the OCR process itself.
    """
    def __init__(self, message="A critical error occurred during OCR processing."):
        self.message = message
        logger.error(f"OCRProcessingError: {self.message}", exc_info=True)
        super().__init__(self.message)

