# config.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

"""Configuration file for the KYO QA Tool."""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
PDF_TXT_DIR = BASE_DIR / "PDF_TXT"
CACHE_DIR = BASE_DIR / ".cache"

# Tesseract OCR configuration
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Data processing configuration
UNWANTED_AUTHORS = ["Knowledge Import"]
STANDARDIZATION_RULES = {"TASKalfa-": "TASKalfa ", "ECOSYS-": "ECOSYS "}

# Excel column names
META_COLUMN_NAME = "Meta"
AUTHOR_COLUMN_NAME = "Author"
DESCRIPTION_COLUMN_NAME = "Short description"
QA_NUMBERS_COLUMN_NAME = "QA Numbers"

# Create necessary directories
def ensure_directories():
    """Create all necessary directories if they don't exist."""
    for directory in [OUTPUT_DIR, LOGS_DIR, PDF_TXT_DIR, CACHE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
ensure_directories()