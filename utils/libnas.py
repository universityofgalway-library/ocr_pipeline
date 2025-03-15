import os 
import shutil
from datetime import datetime
from utils.config import CoreConfig
from utils.log import LogActivities

class LibNas:
    """
    Manages file transfer operations between LibNas and local folders.

    This class handles copying directories from the LibNas input folder to a local
    destination, and then moves processed directories back to the LibNas output folder.

    Attributes:
        folders (dict): Paths to various folders.
        logs_folder (str): Path to the logs folder.
        libnas_input (str): Path to the LibNas input folder.
        libnas_output (str): Path to the LibNas output folder.
        destination_root (str): Path to the local destination folder.
        processed_folder (str): Path to the local processed folder.
        log_activity (LogActivities): Logger for recording errors.

    Methods:
        move_and_override(dst_dir):
            Removes the destination directory if it exists.
        copy_from_libnas() -> None:
            Copies directories from LibNas input to the local destination folder.
        send_to_libnas() -> None:
            Moves processed directories from local processed folder to LibNas output.
    """
     
    def __init__(self):
        core_config = CoreConfig()


        self.folders = core_config.requiredFolders()
        self.parameters = core_config.requiredValues()

        self.logs_folder = self.folders['logs_folder']
        self.libnas_input = self.folders['libnas_input']
        self.libnas_output = self.folders['libnas_output']
        self.destination_root = self.folders['input_folder']
        self.processed_folder = self.folders['processed_folder']
        self.overwrite_files = self.parameters['overwrite_files']
        self.image_extensions = self.parameters['image_extensions']
        self.log_activity = LogActivities(self.logs_folder)

    @staticmethod
    def move_and_override(dest_file) -> None:
        """
        Removes the destination file if it exists and overwrite is True.

        Args:
            dest_file (str): The path to the directory or file to be removed.
        """

        # If the destination file exists, remove it
        if os.path.exists(dest_file):
            if os.path.isfile(dest_file):
                os.remove(dest_file)  # Remove the file


    def copy_from_libnas(self) -> None:
        """
        Copies directories from LibNas input to the local destination folder.
        Handles potential conflicts by removing existing directories at the destination.
        """
        entry_folder = self.libnas_input
        exit_folder = self.destination_root
        try:
            for root, _, files in os.walk(entry_folder):
                    for filename in files:
                        _, extension = os.path.splitext(filename)
                        if extension in self.image_extensions:
                            src_file = os.path.join(root, filename)
                            parent_dir = os.path.basename(root)
                            dest_dir = os.path.join(exit_folder, parent_dir)
                            
                            # Avoid creating root directory for individual images without directories
                            if os.path.basename(dest_dir) != os.path.basename(entry_folder):
                                # Create the destination directory if it does not already exist
                                os.makedirs(dest_dir, exist_ok=True)
                                dest_file = os.path.join(dest_dir, filename)
                            else:
                                dest_dir = exit_folder
                                dest_file = os.path.join(dest_dir, filename)

                            if os.path.exists(dest_file):
                                if self.overwrite_files:
                                    shutil.copy(src_file, dest_dir)
                                    self.log_activity.overwrite(f"File {filename} was overwritten input folder: {dest_dir}")    
                                else:
                                    # raise FileExistsError(f"File {dest_file} already exists. Aborting copy, overwrite turned off.")
                                    self.log_activity.overwrite(f"File {filename} already exist in pipeline input folder, (overwrite turned off): {dest_dir}")   
                            else:
                                shutil.copy(src_file, dest_dir)

        except Exception as e:
            self.log_activity.error(f"File {filename} failed -  {e}")   
           
                    
            
    def send_to_libnas(self) -> None:
        """
        Moves processed directories from the local folder to LibNas output.
        Handles potential conflicts by removing existing directories at the LibNas output.
        """

        # entry_folder = self.processed_folder
        # exit_folder = self.destination_root
        # self.walk_through_folders(entry_folder, exit_folder)

        try:
            for root, dirs, _ in os.walk(self.processed_folder):
                for dirname in dirs:
                    src_dir = os.path.join(root, dirname)

                    self.move_and_override(self.libnas_output)
                    shutil.move(src_dir, self.libnas_output)

                    
        except FileExistsError:
            print(f"Folder already exist on LibNas or Output destination: {self.libnas_output}")
            self.log_activity.processing(f"Folder already exist on LibNas or Output destination: {self.libnas_output}")
        except Exception as e:
            self.log_activity.error(f"An error occurred while moving to LibNas: {str(e)}")



 