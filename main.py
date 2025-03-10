"""
Main script to perform OCR processing and file sorting.

This script performs the following steps:
1. Verifies that all required folders are present using the `CoreConfig` class.
2. Initialises the `TextractOCR` class for performing OCR on images located in the input folder.
3. Initialises the `SortOCR` class for organising the processed OCR output files.
4. Selects images from the input folder for OCR processing.
5. Executes the main sorting logic to organise the OCR results.

Classes:
    TextractOCR: Handles OCR operations using AWS Textract.
    CoreConfig: Manages configuration settings and folder paths.
    SortOCR: Organises the output files into appropriate directories.

Usage:
    Run this script to perform OCR processing on images and sort the results into folders.
"""
import time
from datetime import datetime
from utils.sort import SortOCR
from utils.config import CoreConfig
from utils.client import TextractOCR
from utils.log import LogActivities
from utils.alto import AltoGenerator
from utils.libnas import LibNas
from utils.check import CheckEmptyFolder

# Instantiate and verify all required folders
core_config = CoreConfig()
core_config.verifyFolders()

parameters = core_config.requiredValues()
folders = core_config.requiredFolders()
logs_folder = folders["logs_folder"]
input_folder =folders["input_folder"]

retry_count = 0
max_retries = parameters['max_retries']  # Maximum number of retries
retry_delay = parameters['retry_delay']  # Delay in seconds before retrying

if __name__ == '__main__':
    # Instantiate required classes
    libnas = LibNas()
    sort_ocr = SortOCR()
    check = CheckEmptyFolder()
    textract_ocr = TextractOCR()
    log_activity = LogActivities(logs_folder)

    # Get required folders and files from libnas
    libnas.copy_from_libnas()
    
    # Define the parent input folder
    textract_ocr.select_image(input_folder)

    sort_ocr.start_sorting()
    
    # exit()

    while retry_count < max_retries:
        try:
            while check.is_json_folder_empty() and check.is_images_folder_empty():
                current_datetime = datetime.now()
                print(f'Grab a cup of coffee, I am still running ... {current_datetime} ') 
                
                # Begin ALTO XML generation
                AltoGenerator()  
            
                time.sleep(3)
            else:
                current_datetime = datetime.now()
                log_activity.error(f'The Pipeline failed to run, because the JSON / Images folder is empty ... {current_datetime} ')
                break  # Exit the retry loop if successful
        except (ValueError, FileNotFoundError) as e:
            log_activity.error(f"Error encountered: {e}")
            retry_count += 1
            if retry_count < max_retries:
                log_activity.error(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    else:
        log_activity.error(f"Failed to run after {max_retries} retries. Exiting.")

    # Return processed files to libNas
    libnas.send_to_libnas()
    
    # Clean up core folders and empty sub directories
    check.is_core_folder_empty()