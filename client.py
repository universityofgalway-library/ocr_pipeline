import os
import json
import boto3
import shutil
from pathlib import Path
from utils.config import requiredFolders,requiredValues, verifyFolders

'''
CONVERSION OF IMAGES TO JSON
'''

# Config values 
verifyFolders()
get_folders = requiredFolders()
get_values = requiredValues()



json_sorter = get_folders["json_sorter"]
input_folder = get_folders["input_folder"]
images_sorter = get_folders["images_sorter"]
failed_ocr_folder = get_folders["failed_ocr_folder"]
low_confidence_folder = get_folders["low_confidence_folder"]

image_extensions = get_values["image_extensions"]
output_extension = get_values["output_extension"]
low_confidence_threshold = get_values["low_confidence_threshold"]

def delete_empty_folder(directory_path):
    if not os.listdir(directory_path):
        os.rmdir(directory_path)

def extract_json_from_image(input_file, output_file) -> bool: 
    # Create a Textract client
    client = boto3.client('textract')

    # Open the image file
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

    # Save the JSON response to a file
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(response, json_file, indent=4)
        print(f"Processed file saved to {output_file}")
    except Exception as e:
        print(f"Error saving file {output_file}: {e}")

    return True # Return true if images is successfully OCRed


def move_extracted_images(directory_name, file_path):
    output_directory = Path(images_sorter) / directory_name
    output_directory.mkdir(parents=True, exist_ok=True)

    shutil.move(file_path, output_directory)

    directory_moved = Path('input') / directory_name
    delete_empty_folder(directory_moved)


def select_image(parent_input_folder):
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