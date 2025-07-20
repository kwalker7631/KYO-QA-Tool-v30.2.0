# custom_patterns.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

"""Manages loading and saving of user-defined regex patterns."""

import re
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PATTERNS_FILE = Path(__file__).parent / "user_defined_patterns.json"

DEFAULT_PATTERNS = {
    "model_patterns": [
        r"\bFS-\d+[A-Z]*\b",
        r"\bKM-\d+[A-Z]*\b", 
        r"\bECOSYS\s+[A-Z]+\d+[a-z]*\b",
        r"\bTASKalfa\s+\d+[a-z]*\b",
    ],
    "qa_patterns": [
        r"\bQA-\d+\b",
        r"\bSB-\d+\b",
    ]
}

def _initialize_patterns_file():
    """Initialize the patterns file with default patterns if it doesn't exist."""
    if not PATTERNS_FILE.exists():
        try:
            with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_PATTERNS, f, indent=4)
            logger.info("Created default patterns file")
        except Exception as e:
            logger.error(f"Failed to create patterns file: {e}")

def get_patterns():
    """
    Get compiled regex patterns for model and QA number detection.
    
    Returns:
        tuple: (compiled_model_patterns, compiled_qa_patterns)
    """
    _initialize_patterns_file()
    
    try:
        with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        model_patterns = data.get("model_patterns", DEFAULT_PATTERNS["model_patterns"])
        qa_patterns = data.get("qa_patterns", DEFAULT_PATTERNS["qa_patterns"])
        
        # Compile regex patterns
        compiled_model = []
        compiled_qa = []
        
        for pattern in model_patterns:
            try:
                compiled_model.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                logger.warning(f"Invalid model pattern '{pattern}': {e}")
                
        for pattern in qa_patterns:
            try:
                compiled_qa.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                logger.warning(f"Invalid QA pattern '{pattern}': {e}")
        
        logger.debug(f"Loaded {len(compiled_model)} model patterns and {len(compiled_qa)} QA patterns")
        return compiled_model, compiled_qa
        
    except Exception as e:
        logger.error(f"Failed to load patterns: {e}")
        # Return compiled default patterns as fallback
        compiled_model = [re.compile(p, re.IGNORECASE) for p in DEFAULT_PATTERNS["model_patterns"]]
        compiled_qa = [re.compile(p, re.IGNORECASE) for p in DEFAULT_PATTERNS["qa_patterns"]]
        return compiled_model, compiled_qa

def get_pattern_strings():
    """
    Get the raw pattern strings (for editing in UI).
    
    Returns:
        tuple: (model_pattern_strings, qa_pattern_strings)
    """
    _initialize_patterns_file()
    
    try:
        with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("model_patterns", []), data.get("qa_patterns", [])
    except Exception as e:
        logger.error(f"Failed to load pattern strings: {e}")
        return DEFAULT_PATTERNS["model_patterns"], DEFAULT_PATTERNS["qa_patterns"]

def save_patterns(model_patterns, qa_patterns):
    """
    Save patterns to the patterns file.
    
    Args:
        model_patterns (list): List of model pattern strings
        qa_patterns (list): List of QA pattern strings
    """
    _initialize_patterns_file()
    
    if not isinstance(model_patterns, list) or not isinstance(qa_patterns, list):
        raise ValueError("Patterns must be provided as lists.")
    
    # Validate patterns by trying to compile them
    for pattern in model_patterns:
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid model pattern '{pattern}': {e}")
            
    for pattern in qa_patterns:
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid QA pattern '{pattern}': {e}")
    
    try:
        with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "model_patterns": model_patterns, 
                "qa_patterns": qa_patterns
            }, f, indent=4)
        logger.info("Patterns saved successfully")
    except Exception as e:
        logger.error(f"Failed to save patterns: {e}")
        raise

# Initialize patterns file on module import
_initialize_patterns_file()