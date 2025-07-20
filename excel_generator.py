# excel_generator.py
# Author: Kenneth Walker
# Date: 2025-07-19
# Version: 30.2.0

import pandas as pd
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def create_excel_report(data_list):
    """
    Creates an Excel spreadsheet from a list of dictionaries.

    Args:
        data_list (list): A list of dictionaries, where each dictionary
                          represents a row of data.

    Returns:
        str: The path to the newly created Excel file.
        
    Raises:
        Exception: If the report cannot be created.
    """
    if not data_list:
        logger.warning("Data list is empty. Cannot create Excel report.")
        return None

    logger.info(f"Creating Excel report with {len(data_list)} rows.")
    
    try:
        # Convert the list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(data_list)
        
        # Define the output directory and filename
        output_dir = "processed_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a unique filename with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"KYO_QA_Report_{timestamp}.xlsx"
        report_path = os.path.join(output_dir, filename)
        
        # Write the DataFrame to an Excel file
        df.to_excel(report_path, index=False)
        
        logger.info(f"Successfully created Excel report: {report_path}")
        return report_path
        
    except Exception as e:
        logger.error(f"Failed to generate Excel report: {e}", exc_info=True)
        raise

