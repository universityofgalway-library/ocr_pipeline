import os
import shutil
from utils.config import CoreConfig
from utils.log import LogActivities

class CheckEmptyFolder:
    """
    A utility class to check if specific folders are empty or contain any files/folders 
    apart from the '.keep' file.

    Attributes:
        folders (dict): A dictionary containing paths to required folders.
        json_folder (str): Path to the JSON folder as specified in the configuration.
        images_folder (str): Path to the images folder as specified in the configuration.
    """

    def __init__(self):
        """
        Initializes the CheckEmptyFolder class by loading folder paths from the configuration file.
        """
         
        core_config = CoreConfig()
        self.folders = core_config.requiredFolders()
        

        # Folders nmaes from config.py
        self.json_folder = self.folders["json_folder"]
        self.logs_folder = self.folders["logs_folder"]
        self.core_folders = self.folders["core_folders"]
        self.images_folder = self.folders["images_folder"]
        self.input_folder = self.folders["input_folder"]

        # Logging initailisation has to come after logs folder name
        self.log_activity = LogActivities(self.logs_folder)

    def is_json_folder_empty(self) -> bool:
        """
        Checks if the JSON folder is empty or contains any directories other than '.keep'.

        Returns:
            bool: True if there are any directories in the folder (excluding '.keep'), False otherwise.
        """
        
        if os.path.exists(self.json_folder):
            # Check if there are any entries in the folder that are directories and not '.keep'
            folders_present = any(entry.is_dir() and entry.name != '.keep' for entry in os.scandir(self.json_folder))
            
            # Return True if there are only folders (excluding '.keep'), False otherwise
            return folders_present
        return False

    def is_images_folder_empty(self) -> bool:
        """
        Checks if the images folder is empty or contains any directories other than '.keep'.

        Returns:
            bool: True if there are any directories in the folder (excluding '.keep'), False otherwise.
        """
        
        if os.path.exists(self.images_folder):
            # Check if there are any entries in the folder that are directories and not '.keep'
            folders_present = any(entry.is_dir() and entry.name != '.keep' for entry in os.scandir(self.images_folder))
            
            # Return True if there are only folders (excluding '.keep'), False otherwise
            return folders_present
        return False

    
    def is_core_folder_empty(self) -> None:
        """
        Checks if the core folder is empty or contains empty directories other than '.keep'.

        Returns:
            void
        """
        for root, dirs, _ in os.walk(self.core_folders, topdown=False):
            for sub_dir in dirs:
                sub_dir_path = os.path.join(root, sub_dir)
                if self.is_folder_empty(sub_dir_path):
                    print(f"Deleting empty directory: {sub_dir_path}")
                    self.log_activity.processing(f"Deleting empty directory: {sub_dir_path}")
                    os.rmdir(sub_dir_path)
                    
        # Check if the parent folder "core_folders" is empty or contains on a .keep file
        main_files  = os.listdir(self.core_folders)
        
        if main_files == [".keep"]:
            try:
                shutil.rmtree(self.core_folders)
            except OSError as e:
                print(f"Error deleting {self.core_folders}: {e}")
                self.log_activity.processing(f"Error deleting {self.core_folders}: {e}")
        else:
            try:
                os.rmdir(self.core_folders)         
            except OSError as e:
                print("Core folder contains non empty folder")
                self.log_activity.processing("Core folder contains non empty folder")
                
    def is_input_folder_empty(self) -> None:
        """
        Checks if the input folder is empty or contains empty directories other than '.keep'.

        Returns:
            void
        """
        for root, dirs, _ in os.walk(self.input_folder, topdown=False):
            for sub_dir in dirs:
                sub_dir_path = os.path.join(root, sub_dir)
                if self.is_folder_empty(sub_dir_path):
                    print(f"Deleting empty directory: {sub_dir_path}")
                    self.log_activity.processing(f"Deleting empty directory: {sub_dir_path}")
                    os.rmdir(sub_dir_path)
                    
        # Check if the parent folder "core_folders" is empty or contains on a .keep file
        main_files  = os.listdir(self.input_folder)
        
        if main_files == [".keep"]:
            try:
                shutil.rmtree(self.input_folder)
            except OSError as e:
                print(f"Error deleting {self.input_folder}: {e}")
                self.log_activity.processing(f"Error deleting {self.input_folder}: {e}")
        else:
            try:
                os.rmdir(self.input_folder)         
            except OSError as e:
                print("Core folder contains non empty folder")
                self.log_activity.processing("Core folder contains non empty folder")
    
    def is_folder_empty(self, folder_path) -> bool:
        """Check if a given folder is empty."""
        return not any(os.scandir(folder_path))