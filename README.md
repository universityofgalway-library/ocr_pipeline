# Textract OCR Processing and File Sorting Script

This script automates the process of Optical Character Recognition (OCR) on images and organises the resulting files into appropriate directories. The script utilises AWS Textract for OCR and performs several key steps including configuration setup, image selection, OCR processing, and file sorting.

## Features

- **Folder Verification:** Ensures that all required folders are present and configured correctly using the `CoreConfig` class.
- **OCR Processing:** Performs OCR on images located in the input folder using the `TextractOCR` class.
- **File Sorting:** Organises the processed OCR output files into appropriate directories using the `SortOCR` class.
- **Error Handling:** Implements retry logic for robust execution, with logging of any errors encountered during the process.
- **ALTO XML Generation:** Generates ALTO XML files post-OCR processing.

## Classes

- **`CoreConfig`:** Manages configuration settings and folder paths. Ensures all necessary folders are available.
- **`TextractOCR`:** Handles OCR operations using AWS Textract.
- **`SortOCR`:** Organises OCR output files into the correct directories.
- **`LogActivities`:** Manages logging activities, capturing both routine operations and errors.
- **`AltoGenerator`:** Generates ALTO XML files from OCR output.
- **`LibNas`:** Manages file transfers to and from a network-attached storage (NAS) system.
- **`CheckEmptyFolder`:** Monitors the status of folders to ensure they are not empty before processing.

## Usage

1. **Run the Script:**
   - The script can be executed directly. It will automatically verify the necessary folders, process images using OCR, sort the results, and handle any errors with retry logic.

2. **OCR Process:**
   - The script selects images from the input folder and processes them using AWS Textract.
   - The results are sorted and organised into folders as per the configuration.

3. **Retry Logic:**
   - If errors are encountered, the script will log the error, wait for a specified delay, and retry the process up to a maximum number of retries.

4. **Finalisation:**
   - After processing, the script returns the processed files to the NAS storage.

## To run script: 
- Optionally, set up a virtual environment before running the installer to avoid conflicts with other projects.
- Ensure you have all the libraries listed in the requirements.txt file installed by running:

```bash
pip install -r requirements.txt

```bash
python main.py
```

## CoreConfig Class

## Overview

The `CoreConfig` class is designed to manage the configuration settings and folder paths required for the OCR processing pipeline. This class handles the creation of necessary folders and provides configuration values used throughout the pipeline.

`make changes to it with caution`

## Key Features

- **`Folder Verification`**: Ensures that all required folders exist and creates them if necessary.
- **`Configuration Management`**: Provides essential configuration settings such as retry limits, file extensions, and confidence thresholds.
- **`Customisable Paths`**: Allows customisation of input and output paths to suit your project's needs.

## Folder Paths

The `CoreConfig` class defines a set of folder paths required for the OCR process. These paths are returned as a dictionary by the `requiredFolders` method. 

### Default Folder Structure

Below is the default folder structure created and managed by the `CoreConfig` class:

- `input_folder`: Path for input files, the entry point to the pipeline.
- `core_folders`: Base path for core folders, containing all subsequent folders.
- `logs_folder`: Path for log files.
- `json_folder`: Path for JSON files.
- `images_folder`: Path for image files.
- `json_sorter`: Path for sorted JSON files.
- `failed_folder`: Path for failed processing files.
- `images_sorter`: Path for sorted image files.
- `failed_ocr_folder`: Path for files with failed OCR.
- `processed_folder`: Path for successfully processed files.
- `low_confidence_folder`: Path for files with low OCR confidence.

### Customising Input and Output Paths

The `CoreConfig` class also includes specific paths for input and output folders on LIBNAS system. By default, these paths are set as follows:

```python
"libnas_input": r"z:\\OCR outputs\\p155_kerby_miller\\Letters\\ocr_test\\input",
"libnas_output": r"z:\\OCR outputs\\p155_kerby_miller\\Letters\\ocr_test\\output",
```