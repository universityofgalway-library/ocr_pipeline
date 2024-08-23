import os
import json
import boto3
from pathlib import Path
from utils.core_folders import core

'''
CONVERSION OF IMAGES TO JSON
'''

# Get valid image extensions
core_folders_name = core()
image_extensions = core_folders_name["image_extensions"]


def extract_json_from_image(input_file, output_file):
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
        return

    # Save the JSON response to a file
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(response, json_file, indent=4)
        print(f"Processed file saved to {output_file}")
    except Exception as e:
        print(f"Error saving file {output_file}: {e}")

    # Print newly created Json file to terminal
    # print(json.dumps(response, indent=4))


def select_image(parent_input_folder):
    for root, _, files in os.walk(parent_input_folder):
        for filename in files:
            if '.' +  filename.split('.')[1] in image_extensions:
                input_file = os.path.join(root, filename)
                
                # Get the directory name for output
                directory_name = os.path.relpath(root, parent_input_folder)
                output_directory = Path('json_sorter') / directory_name
                output_directory.mkdir(parents=True, exist_ok=True)
                
                # Prepare the output file path
                output_file = os.path.join(output_directory, filename.rsplit('.', 1)[0] + '.json')
                
                # Print file paths for debugging
                print(f"Processing file: {input_file}")
                print(f"Output file: {output_file}")
                
                extract_json_from_image(input_file, output_file)

# Define the parent input folder
parent_input_folder = 'input'
select_image(parent_input_folder)