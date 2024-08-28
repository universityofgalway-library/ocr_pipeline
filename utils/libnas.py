import os 
import shutil
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
        self.logs_folder = self.folders['logs_folder']
        self.libnas_input = self.folders['libnas_input']
        self.libnas_output = self.folders['libnas_output']
        self.destination_root = self.folders['input_folder']
        self.processed_folder = self.folders['processed_folder']

        self.log_activity = LogActivities(self.logs_folder)

    @staticmethod
    def move_and_override(dst_dir):
        """
        Removes the destination directory if it exists.

        Args:
            dst_dir (str): The path to the directory or file to be removed.
        """
        pass
        # If the destination exists, remove it
        # if os.path.exists(dst_dir):
        #     if os.path.isfile(dst_dir):
        #         os.remove(dst_dir)  # Remove the file
        #     else:
        #         shutil.rmtree(dst_dir)  # Remove the directory and its contents


    def copy_from_libnas(self) -> None:
        """
        Copies directories from LibNas input to the local destination folder.
        Handles potential conflicts by removing existing directories at the destination.
        """
        try:
            for root, dirs, _ in os.walk(self.libnas_input):
                for dirname in dirs:
                    src_dir = os.path.join(root, dirname)
                    dst_dir = os.path.join(self.destination_root, dirname)
                    
                    self.move_and_override(dst_dir)
                    
                    if not os.path.exists(dst_dir):
                        shutil.copytree(src_dir, dst_dir)
        except FileExistsError:
            self.log_activity.error(f"Folder already exist in pipeline input folder: {dst_dir}")            
            
    def send_to_libnas(self) -> None:
        """
        Moves processed directories from the local folder to LibNas output.
        Handles potential conflicts by removing existing directories at the LibNas output.
        """
        try:
            for root, dirs, _ in os.walk(self.processed_folder):
                for dirname in dirs:
                    src_dir = os.path.join(root, dirname)

                    self.move_and_override(self.libnas_output)
                    shutil.move(src_dir, self.libnas_output)
        except FileExistsError:
            print(f"Folder already exist on LibNas: {self.libnas_output}")
        except Exception as e:
            self.log_activity.error(f"An error occurred while moving to LibNas: {str(e)}")


