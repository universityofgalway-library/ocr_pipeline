import os
import shutil
from datetime import datetime
from utils.config import CoreConfig
from utils.log import LogActivities

class SortOCR:
    """
    A class to manage and organise OCR files by sorting them into designated folders.
    """

    def __init__(self):
        '''
        Initialises the sortOCR class and retrieves required parameters and folders.
        '''
        self.core_config = CoreConfig()
        self.parameters = self.core_config.requiredValues()
        self.folders = self.core_config.requiredFolders()

        self.logs_folder = self.folders["logs_folder"]
        self.json_folder = self.folders["json_folder"]
        self.images_folder = self.folders["images_folder"]
        self.json_sorter_folder = self.folders["json_sorter"]
        self.images_sorter_folder = self.folders["images_sorter"]         
        self.image_extensions = self.parameters["image_extensions"]
        self.output_extension = self.parameters["output_extension"]

        # Logging initailisation has to come after logs folder name
        self.log_activity = LogActivities(self.logs_folder)

    @staticmethod
    def contains_subfolders(folder_path: str) -> bool:
        """
            Checks if the specified folder contains any subfolders.

            Args:
                folder_path (str): The path to the folder to be checked.
            Returns:
                bool: True if the folder contains at least one subfolder, False otherwise.
        """
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                return True
        return False


    def process_sub_folders(self, parent_folder_path: str, file_extention: str,destination: str) -> None:
        """
        Processes subfolders within the specified parent folder, moving files with a specified extension to a destination.

        Args:
            parent_folder_path (str): Path to the parent folder containing subfolders.
            file_extension (str): File extension to filter files that should be moved.
            destination (str): Destination folder where the filtered files will be moved.
        Returns:
            None
        """
         
        subfolders = []
        for f in os.listdir(parent_folder_path):
            if os.path.isdir(os.path.join(parent_folder_path, f)):
                subfolders.append(f)
        
        # Get the files under each sub folders    
        for subfolder in subfolders:
            for file_name in os.listdir(os.path.join(parent_folder_path, subfolder)):
                if file_name.endswith(file_extention):
                    self.split_files( parent_folder_path,file_name,subfolder,destination)
                    
            # Delete the parent folder from the sorting forlder after processing
            shutil.rmtree(os.path.join(parent_folder_path,subfolder))
    
    def split_files(self, parent_folder_path: str,filename: str,subfolder: str,destination: str) -> None:
        """
        Moves a file from its original location to a new structured destination folder.

        Args:
            parent_folder_path (str): Path to the parent folder containing the subfolder.
            filename (str): Name of the file to be moved.
            subfolder (str): Subfolder where the file is currently located.
            destination (str): Destination folder where the file will be moved.
        Returns:
            None
        """
        
        original_file_path  = os.path.join(parent_folder_path,subfolder,filename)
        project_folder_name = filename.rsplit('-')[0]  # Split at '-'
        new_file_folder_path = os.path.join(destination,subfolder.split('-',1)[0].replace(' ',''), project_folder_name) # Split folders name from the left side
            
        # Create the sub folder in the new destination
        if not os.path.exists(new_file_folder_path):
            os.makedirs(new_file_folder_path)

        try:
            # Delete existing file and replace with new one
            moving_path = os.path.join(new_file_folder_path, filename)
            if os.path.exists(moving_path):
                print(f"Deleting existing folder {moving_path} ...")
                os.remove(moving_path)
            
            # Log moving of files 
            # Log the average confidence score of each file
            self.log_activity.sorting(f"Moving file from {original_file_path} to {new_file_folder_path}")
            print(f"Sorting script still running ... {datetime.now()}")

            shutil.move(original_file_path, new_file_folder_path)

        except Exception as e:
            self.log_activity.error(f"Error moving file: {e}")

    def start_sorting(self):
        """
        Executes the main logic to process and organise OCR files by checking and processing subfolders in the 
        JSON and images sorting directories.
        
        Returns:
            None
        """
        if self.contains_subfolders(self.json_sorter_folder):
            self.process_sub_folders(self.json_sorter_folder, self.output_extension, self.json_folder)

        if self.contains_subfolders(self.images_sorter_folder):
            self.process_sub_folders(self.images_sorter_folder, self.image_extensions, self.images_folder)