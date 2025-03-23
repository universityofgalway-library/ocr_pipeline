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
        self.parameters = core_config.requiredValues()
        

        # Folders nmaes from config.py
        self.json_folder = self.folders["json_folder"]
        self.logs_folder = self.folders["logs_folder"]
        self.core_folders = self.folders["core_folders"]
        self.input_folder = self.folders["input_folder"]
        self.output_folder = self.folders["libnas_output"]
        self.images_folder = self.folders["images_folder"]
        
        
        # Parameters from config.py 
        self.overwrite_files = self.parameters["overwrite_files"]
    

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
    
    def is_output_folder_structured(self) -> None:
        """
        Moves child directories from subdirectories in the output folder to the output folder,
        and deletes all empty subdirectories.
        
        For example, if you have:
        /output/subdirectory/children
        this moves "children" to /output, and then removes any now-empty directories.
        """
        # Move nested child directories (e.g., /output/subdirectory/child -> /output/child)
        for item in os.listdir(self.output_folder):
            subfolder_path = os.path.join(self.output_folder, item)
            if os.path.isdir(subfolder_path):
                # Look for directories inside each subdirectory
                for child in os.listdir(subfolder_path):
                    child_path = os.path.join(subfolder_path, child)
                    if os.path.isdir(child_path):
                        destination = os.path.join(self.output_folder, child)
                        if os.path.exists(destination):
                            # If the destination already exists, merge the contents
                            print(f"Merging directory: {child_path} into {destination}")
                            self.log_activity.processing(f"Merging directory: {child_path} into {destination}")
                            for child_item in os.listdir(child_path):
                                src_path = os.path.join(child_path, child_item)
                                
                                dest_path = os.path.join(destination, os.path.basename(src_path))
                                if self.overwrite_files and os.path.exists(dest_path):
                                    # Check if dest_path is a directory or file
                                    if os.path.isdir(dest_path):
                                        shutil.rmtree(dest_path)
                                    elif os.path.isfile(dest_path):
                                        os.remove(dest_path)
                                    else:
                                        print(f"Skipping removal for unknown type: {dest_path}")
                                    
                                shutil.move(src_path, destination)
                            os.rmdir(child_path)
                        else:
                            # Otherwise, move the entire child directory
                            print(f"Moving directory: {child_path} to {destination}")
                            self.log_activity.processing(f"Moving directory: {child_path} to {destination}")
                            shutil.move(child_path, destination)

        # Remove any empty directories left in the output folder (excluding the output folder itself)
        for root, d, _ in os.walk(self.output_folder, topdown=False):
            if root == self.output_folder:
                continue
            if not os.listdir(root):  # If the directory is empty
                print(f"Deleting empty directory: {root}")
                self.log_activity.processing(f"Deleting empty directory: {root}")
                os.rmdir(root)
    
    
    def is_folder_empty(self, folder_path) -> bool:
        """Check if a given folder is empty."""
        return not any(os.scandir(folder_path))