import os
import json
import boto3
import shutil
from pathlib import Path
from dotenv import load_dotenv
from utils.config import CoreConfig
from utils.log import LogActivities
from utils.json_logger import JsonLogger

# Load environment variables from .env file
load_dotenv()

class TextractOCR: 
    """
    A class to handle OCR processing using AWS Textract, managing folder paths, configurations, 
    and interactions with the AWS Textract service.
    """
    def __init__(self):

        """
        Initialise the TextractOCR class with required folder paths and parameters from the config file.
        """

        # Initialisation of required folders and parameters
        core_config = CoreConfig()
        self.folders = core_config.requiredFolders()
        self.parameters = core_config.requiredValues()
        
        # Folders nmaes from config.py
        self.logs_folder = self.folders["logs_folder"]
        self.json_log_path = self.folders["json_log_path"]
        self.json_sorter = self.folders["json_sorter"]
        self.text_sorter = self.folders["text_sorter"]
        self.images_sorter = self.folders["images_sorter"]
        self.failed_ocr_folder = self.folders["failed_ocr_folder"]
        self.low_confidence_folder = self.folders["low_confidence_folder"]
        
        # Parameters from config.py 
        self.overwrite_files = self.parameters["overwrite_files"]
        self.image_extensions = self.parameters["image_extensions"]
        self.output_extension_json = self.parameters["output_extension_json"]
        self.output_extension_text = self.parameters["output_extension_text"]
        self.low_confidence_threshold = self.parameters["low_confidence_threshold"]
        self.low_confidence_error_message = self.parameters["low_confidence_error_message"]
        self.exception_save_error_message = self.parameters["exception_save_error_message"]
        self.ocr_processing_error_message = self.parameters["ocr_processing_error_message"]


        # Logging initailisation has to come after logs folder name
        self.log_activity = LogActivities(self.logs_folder)
        self.json_logging = JsonLogger()

        # AWS Textract client
        self.client = boto3.client("textract",
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION"))


    def delete_empty_folder(self, directory_path: str) -> None:
        """
        Deletes the specified directory if it is empty.

        Args:
            directory_path (str): The path to the directory to check and delete.
        """
        if not os.listdir(directory_path):
            os.rmdir(directory_path)


    def extract_from_image(self, input_file: str, output_file_json: str, output_file_text: str) -> bool: 
        """
        Extracts text from image in the input_folder's path using AWS Textract and saves the result as a JSON file to json_sorter folder.

        Args:
            input_file (str): The path to the input image file.
            output_file_json (str): The path to the output JSON file.
            output_file_text (str): The path to the output TXT file.
        Returns:
            bool: True if the image was successfully processed and saved, False otherwise.
        """
        
        try:
            with open(input_file, "rb") as document:
                # Call Textract to analyse the document
                response = self.client.detect_document_text(
                    Document={"Bytes": document.read()}
                )
        except Exception as e:
            # Log error in JSON file
            self.json_logging.log_error_as_json(self.ocr_processing_error_message,input_file )
            self.log_activity.error(f"Error processing OCR for file {input_file}: {e}")
            shutil.move(input_file, self.failed_ocr_folder)
            return False

        # Extract confidence scores for lines
        line_confidences = [block["Confidence"] for block in response["Blocks"] if block["BlockType"] == "LINE"]
        
        # Calculate the average confidence score
        if line_confidences:
            average_confidence = sum(line_confidences) / len(line_confidences)
            
            # Log the average confidence score of each file
            self.log_activity.confidence(input_file,average_confidence)
            
            # with open(f"{self.logs_folder.rstrip('/') + '/'}avg_confidence_score.txt", "a", encoding="UTF-8") as f: 
            #     f.write(input_file + ": " + str(average_confidence) + "\n")
        else:
            # Handle case where no lines are detected
            average_confidence = 0
 
        # Compare average confidence with the threshold
        if average_confidence < self.low_confidence_threshold:
            print("WARNING: The image may contain handwritten text, leading to potential OCR inaccuracies.")
            self.log_activity.processing("WARNING: The image may contain handwritten text, leading to potential OCR inaccuracies.")
            
            # Log error in JSON file
            self.json_logging.log_error_as_json(self.low_confidence_error_message,input_file )

            shutil.move(input_file, self.low_confidence_folder)
            return False
        
        
        try:
            with open(output_file_json, "w", encoding="utf-8") as json_file:
                json.dump(response, json_file, indent=4)
            print(f"Processed file saved to {output_file_json}")
            self.log_activity.processing(f"Processed file saved to {output_file_json}")
        except Exception as e:
            # Log error in JSON file
            self.json_logging.log_error_as_json(self.exception_save_error_message,input_file )
            self.log_activity.error(f"Error saving file {output_file_json}: {e}")

        # Extract text from Textract response
        extracted_text = ''
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                extracted_text += item['Text'] + '\n'

        try:
            with open(output_file_text, "w", encoding="utf-8") as text_file:
                text_file.write(extracted_text.strip())
            print(f"Processed file saved to {output_file_text}")
            self.log_activity.processing(f"Processed file saved to {output_file_text}")
        except Exception as e:
            # Log error in JSON file
            self.json_logging.log_error_as_json(self.exception_save_error_message,input_file )
            self.log_activity.error(f"Error saving file {output_file_text}: {e}")

        return True


    def move_extracted_images(self, directory_name: str, file_path: str) -> None:
        """
        Moves the processed image file to the designated subdirectory within the images_sorter folder
        and deletes the original directory if empty.

        Args:
            directory_name (str): The directory name to be used in the destination path.
            file_path (str): The path to the file to be moved.
        """
        
        output_directory = Path(self.images_sorter) / directory_name
        output_directory.mkdir(parents=True, exist_ok=True)

        filename = os.path.basename(file_path)
        try:
            shutil.move(file_path, output_directory)
        except FileExistsError:
            if self.overwrite_files:
                os.remove(os.join(output_directory, filename))
                self.log_activity.overwrite(f"File {filename} was overwritten input folder: {output_directory}")#
            else:
                self.log_activity.overwrite(f"File {filename} already exist in pipeline input folder, (overwrite turned off): {output_directory}")  
        except Exception as e:
            self.log_activity.error(f"An error occurred while moving {filename} : {str(e)}")

        # Delete directory if its empty
        directory_moved = Path("input") / directory_name
        self.delete_empty_folder(directory_moved)


    # Entry point to the script
    def select_image(self, parent_input_folder: str) -> None:
        """
        Selects image files from the specified folder, processes them, and organises them based on the OCR results.

        Args:
            parent_input_folder (str): The path to the parent folder containing images to process.
        """
        
        for root, _, files in os.walk(parent_input_folder):
            for filename in files:
                if "." +  filename.split(".")[1] in self.image_extensions: # Ensure the selected file is a valid images
                    input_file = os.path.join(root, filename)
                    
                    # Get the directory name for output
                    directory_name = os.path.relpath(root, parent_input_folder)
                    output_directory_json = Path(self.json_sorter) / directory_name
                    output_directory_text = Path(self.text_sorter) / directory_name
                    output_directory_json.mkdir(parents=True, exist_ok=True)
                    output_directory_text.mkdir(parents=True, exist_ok=True)
                    
                    # Prepare the output file path
                    output_file_json = os.path.join(output_directory_json, filename.rsplit(".", 1)[0] + self.output_extension_json)
                    output_file_text = os.path.join(output_directory_text, filename.rsplit(".", 1)[0] + self.output_extension_text)

                    # Print file paths for debugging
                    print(f"Processing file: {input_file}")
                    print(f"Output Json & Text file: {output_file_json}")
                    self.log_activity.processing(f"Processing file: {input_file}")
                    self.log_activity.processing(f"Output Json & Text file: {output_file_json}")
                    
                    # Move processed images file to images_sorter directory if OCR works
                    if self.extract_from_image(input_file, output_file_json, output_file_text):
                        self.move_extracted_images(directory_name, input_file)

        # Remove empty folder from input resulting from failed OCR
        for root, dirs, _ in os.walk(parent_input_folder):
            for dirname in dirs:
                self.delete_empty_folder(os.path.join(root, dirname))
