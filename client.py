import os
import json
import boto3
import shutil
from pathlib import Path
from utils.config import requiredFolders,requiredValues, verifyFolders

'''
CONVERSION OF IMAGES TO JSON USING AMAZON TEXTRACT
'''

# Initialisation 
verifyFolders()
get_folders = requiredFolders()
get_values = requiredValues()
# Folders nmaes from config.py
json_sorter = get_folders["json_sorter"]
input_folder = get_folders["input_folder"]
images_sorter = get_folders["images_sorter"]
failed_ocr_folder = get_folders["failed_ocr_folder"]
low_confidence_folder = get_folders["low_confidence_folder"]
# Parameters from config.py 
image_extensions = get_values["image_extensions"]
output_extension = get_values["output_extension"]
low_confidence_threshold = get_values["low_confidence_threshold"]


def delete_empty_folder(directory_path) -> None:
    """
    Deletes the specified directory if it is empty.

    Args:
        directory_path (str): The path to the directory to check and delete.
    """
    if not os.listdir(directory_path):
        os.rmdir(directory_path)


def extract_json_from_image(input_file, output_file) -> bool: 
    """
    Extracts text from image in the input_folder's path using AWS Textract and saves the result as a JSON file.

    Args:
        input_file (str): The path to the input image file.
        output_file (str): The path to the output JSON file.

    Returns:
        bool: True if the image was successfully processed and saved, False otherwise.
    """
    client = boto3.client('textract')

    try:
        with open(input_file, 'rb') as document:
            # Call Textract to analyze the document
            response = client.detect_document_text(
                Document={'Bytes': document.read()}
            )
    except Exception as e:
        print(f"Error processing file {input_file}: {e}")
        shutil.move(input_file, failed_ocr_folder)
        return False

     # Analyze confidence scores to detect handwriting
    if any(block['Confidence'] < low_confidence_threshold for block in response['Blocks'] if block['BlockType'] == 'LINE'):
        print("Warning: The image may contain handwritten text, leading to potential OCR inaccuracies.")
        shutil.move(input_file, low_confidence_folder)
        return False
    
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(response, json_file, indent=4)
        print(f"Processed file saved to {output_file}")
    except Exception as e:
        print(f"Error saving file {output_file}: {e}")

    return True


def move_extracted_images(directory_name, file_path) -> None:
    """
    Moves the processed image file to the designated subdirectory within the images_sorter folder
    and deletes the original directory if empty.

    Args:
        directory_name (str): The directory name to be used in the destination path.
        file_path (str): The path to the file to be moved.
    """
      
    output_directory = Path(images_sorter) / directory_name
    output_directory.mkdir(parents=True, exist_ok=True)

    shutil.move(file_path, output_directory)

    directory_moved = Path('input') / directory_name
    delete_empty_folder(directory_moved)


def select_image(parent_input_folder) -> None:
    """
    Selects image files from the specified folder, processes them, and organizes them based on the OCR results.

    Args:
        parent_input_folder (str): The path to the parent folder containing images to process.
    """
     
    for root, _, files in os.walk(parent_input_folder):
        for filename in files:
            if '.' +  filename.split('.')[1] in image_extensions: # Ensure the selected file is a valid images
                input_file = os.path.join(root, filename)
                
                # Get the directory name for output
                directory_name = os.path.relpath(root, parent_input_folder)
                output_directory = Path(json_sorter) / directory_name
                output_directory.mkdir(parents=True, exist_ok=True)
                
                # Prepare the output file path
                output_file = os.path.join(output_directory, filename.rsplit('.', 1)[0] + output_extension)

                # Print file paths for debugging
                print(f"Processing file: {input_file}")
                print(f"Output file: {output_file}")
                
                # Move processed images file to images_sorter directory if OCR works
                if extract_json_from_image(input_file, output_file):
                    move_extracted_images(directory_name, input_file)

# Define the parent input folder
select_image(input_folder)