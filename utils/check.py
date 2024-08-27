import os
from utils.config import CoreConfig

class CheckEmptyFolder:
    def __init__(self):
        # Initialisation of required folders and parameters
        core_config = CoreConfig()
        self.folders = core_config.requiredFolders()
        
        # Folders nmaes from config.py
        self.json_folder = self.folders["json_folder"]
        self.images_folder = self.folders["images_folder"]
        

    def is_json_folder_empty(self):
        # Check if the images folder is empty
        if os.path.exists(self.json_folder):
            # Check if there are any entries in the folder that are directories and not '.keep'
            folders_present = any(entry.is_dir() and entry.name != '.keep' for entry in os.scandir(self.json_folder))
            
            # Return True if there are only folders (excluding '.keep'), False otherwise
            return folders_present
        return False

    def is_images_folder_empty(self):
        # Check if the images folder is empty
        if os.path.exists(self.images_folder):
            # Check if there are any entries in the folder that are directories and not '.keep'
            folders_present = any(entry.is_dir() and entry.name != '.keep' for entry in os.scandir(self.images_folder))
            
            # Return True if there are only folders (excluding '.keep'), False otherwise
            return folders_present
        return False