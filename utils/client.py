import os
import json
import boto3
import shutil
from pathlib import Path
from utils.config import coreConfig

class TextractOCR: 
    def __init__(self):

        """
        Initialize the TextractOCR class with required folder paths and parameters from the config file.
        """

        # Initialisation of required folders and parameters
        core_config = coreConfig()
        self.folders = core_config.requiredFolders()
        self.parameters = core_config.requiredValues()
        
        # Folders nmaes from config.py
        self.logs_folder = self.folders["logs_folder"]
        self.json_sorter = self.folders["json_sorter"]
        self.images_sorter = self.folders["images_sorter"]
        self.failed_ocr_folder = self.folders["failed_ocr_folder"]
        self.low_confidence_folder = self.folders["low_confidence_folder"]
        
        # Parameters from config.py 
        self.image_extensions = self.parameters["image_extensions"]
        self.output_extension = self.parameters["output_extension"]
        self.low_confidence_threshold = self.parameters["low_confidence_threshold"]

        # AWS Textract client
        self.client = boto3.client("textract")


    def delete_empty_folder(self, directory_path) -> None:
        """
        Deletes the specified directory if it is empty.

        Args:
            directory_path (str): The path to the directory to check and delete.
        """
        if not os.listdir(directory_path):
            os.rmdir(directory_path)


    def extract_json_from_image(self, input_file, output_file) -> bool: 
        """
        Extracts text from image in the input_folder's path using AWS Textract and saves the result as a JSON file to json_sorter folder.

        Args:
            input_file (str): The path to the input image file.
            output_file (str): The path to the output JSON file.

        Returns:
            bool: True if the image was successfully processed and saved, False otherwise.
        """
        
        try:
            with open(input_file, "rb") as document:
                # Call Textract to analyze the document
                response = self.client.detect_document_text(
                    Document={"Bytes": document.read()}
                )
        except Exception as e:
            print(f"Error processing file {input_file}: {e}")
            shutil.move(input_file, self.failed_ocr_folder)
            return False

        # Extract confidence scores for lines
        line_confidences = [block["Confidence"] for block in response["Blocks"] if block["BlockType"] == "LINE"]
        
        # for one_value in line_confidences:
        #     with open("line_confidence_score.txt", "a", encoding="UTF-8") as f: 
        #         f.write(input_file + ": " + str(one_value) + "\n")

        # Calculate the average confidence score
        if line_confidences:
            average_confidence = sum(line_confidences) / len(line_confidences)
            
            # Log the average confidence score of each file
            with open(f"{self.logs_folder.rstrip('/') + '/'}avg_confidence_score.txt", "a", encoding="UTF-8") as f: 
                f.write(input_file + ": " + str(average_confidence) + "\n")
        else:
            # Handle case where no lines are detected
            average_confidence = 0

        # Compare average confidence with the threshold
        if average_confidence < self.low_confidence_threshold:
            print("Warning: The image may contain handwritten text, leading to potential OCR inaccuracies.")
            shutil.move(input_file, self.low_confidence_folder)
            return False
        
        
        try:
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(response, json_file, indent=4)
            print(f"Processed file saved to {output_file}")
        except Exception as e:
            print(f"Error saving file {output_file}: {e}")

        return True


    def move_extracted_images(self, directory_name, file_path) -> None:
        """
        Moves the processed image file to the designated subdirectory within the images_sorter folder
        and deletes the original directory if empty.

        Args:
            directory_name (str): The directory name to be used in the destination path.
            file_path (str): The path to the file to be moved.
        """
        
        output_directory = Path(self.images_sorter) / directory_name
        output_directory.mkdir(parents=True, exist_ok=True)

        shutil.move(file_path, output_directory)

        directory_moved = Path("input") / directory_name
        self.delete_empty_folder(directory_moved)


    # Entry point to the script
    def select_image(self, parent_input_folder) -> None:
        """
        Selects image files from the specified folder, processes them, and organizes them based on the OCR results.

        Args:
            parent_input_folder (str): The path to the parent folder containing images to process.
        """
        
        for root, _, files in os.walk(parent_input_folder):
            for filename in files:
                if "." +  filename.split(".")[1] in self.image_extensions: # Ensure the selected file is a valid images
                    input_file = os.path.join(root, filename)
                    
                    # Get the directory name for output
                    directory_name = os.path.relpath(root, parent_input_folder)
                    output_directory = Path(self.json_sorter) / directory_name
                    output_directory.mkdir(parents=True, exist_ok=True)
                    
                    # Prepare the output file path
                    output_file = os.path.join(output_directory, filename.rsplit(".", 1)[0] + self.output_extension)

                    # Print file paths for debugging
                    print(f"Processing file: {input_file}")
                    print(f"Output file: {output_file}")
                    
                    # Move processed images file to images_sorter directory if OCR works
                    if self.extract_json_from_image(input_file, output_file):
                        self.move_extracted_images(directory_name, input_file)

        # Remove empty folder from input resulting from failed OCR
        for root, dirs, _ in os.walk(parent_input_folder):
            for dirname in dirs:
                self.delete_empty_folder(os.path.join(root, dirname))
