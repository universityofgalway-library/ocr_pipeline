import os
from utils.config import CoreConfig

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
        self.images_folder = self.folders["images_folder"]
        

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