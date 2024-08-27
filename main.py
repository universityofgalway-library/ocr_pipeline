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

from utils.client import TextractOCR
from utils.config import CoreConfig
from utils.sort import SortOCR

# Instantiate and verify all required folders
core_config = CoreConfig()
core_config.verifyFolders()
input_folder = core_config.requiredFolders()["input_folder"]


if __name__ == '__main__':
    # Instantiate the TextractOCR class
    textract_ocr = TextractOCR()
    sort_ocr = SortOCR()

    # Define the parent input folder
    textract_ocr.select_image(input_folder)
    sort_ocr.main()
