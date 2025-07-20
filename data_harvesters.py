# data_harvesters.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

import re
import logging
from custom_patterns import get_patterns
from config import UNWANTED_AUTHORS, STANDARDIZATION_RULES

logger = logging.getLogger(__name__)

def find_patterns(text, filename=""):
    """
    Searches through the given text to find all predefined regex patterns.

    Args:
        text (str): The OCR'd text from a document.
        filename (str): The filename to include in search content.

    Returns:
        dict: A dictionary with extracted data including models, author, and qa_numbers.
    """
    logger.info("Searching for patterns in the document text.")
    
    # Get the compiled regex patterns
    model_patterns, qa_patterns = get_patterns()
    
    # Create search content including filename for better matching
    search_content = f"{text}\n{filename.replace('_', ' ')}"
    
    # Find model matches
    model_matches = set()
    for pattern in model_patterns:
        try:
            matches = pattern.findall(search_content)
            for match in matches:
                # Handle both single matches and group matches
                if isinstance(match, tuple):
                    model_matches.add(match[0].strip())
                else:
                    model_matches.add(match.strip())
        except Exception as e:
            logger.warning(f"Error applying model pattern {pattern.pattern}: {e}")
            continue
    
    # Apply standardization rules to models
    standardized_models = []
    for model in model_matches:
        standardized_model = model
        for rule, replacement in STANDARDIZATION_RULES.items():
            standardized_model = standardized_model.replace(rule, replacement)
        standardized_models.append(standardized_model)
    
    # Find QA number matches
    qa_matches = set()
    for pattern in qa_patterns:
        try:
            matches = pattern.findall(search_content)
            for match in matches:
                # Handle both single matches and group matches
                if isinstance(match, tuple):
                    qa_matches.add(match[0].strip())
                else:
                    qa_matches.add(match.strip())
        except Exception as e:
            logger.warning(f"Error applying QA pattern {pattern.pattern}: {e}")
            continue
    
    # Find author
    author = ""
    author_match = re.search(r"^Author:\s*(.*)", text, re.MULTILINE | re.IGNORECASE)
    if author_match:
        found_author = author_match.group(1).strip()
        if found_author and found_author not in UNWANTED_AUTHORS:
            author = found_author
    
    # Format results
    models_str = ", ".join(sorted(standardized_models)) if standardized_models else "Not Found"
    qa_numbers_str = ", ".join(sorted(qa_matches)) if qa_matches else ""
    
    result = {
        "models": models_str,
        "author": author,
        "qa_numbers": qa_numbers_str
    }
    
    logger.info(f"Pattern search results: Models='{models_str}', Author='{author}', QA='{qa_numbers_str}'")
    return result

def harvest_all_data(text, filename):
    """
    Legacy function name for compatibility.
    
    Args:
        text (str): The OCR'd text from a document.
        filename (str): The filename.
        
    Returns:
        dict: Extracted data dictionary.
    """
    return find_patterns(text, filename)