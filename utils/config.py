import os

class coreConfig():
    def __init__(self):
        """
        Initializes the FolderManager class and retrieves folder and configuration details.
        """
        self.folders = self.requiredFolders()
        self.config = self.requiredValues()

    def verifyFolders(self) -> None:
        """
        Checks the existence of a list of required folders and creates any that do not exist.

        This function retrieves a dictionary of folder paths from the `requiredFolders` function.
        It iterates over the dictionary, checking each folder path to see if it exists. If a folder
        does not exist, it is created. 

        Returns:
            None: This function does not return any value.
        """
        for _, path in self.folders.items():  # Iterate over key-value pairs
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                print(f"Created folder: {path}")

    @staticmethod
    def requiredValues() -> dict: 
        """
        Returns a dictionary of required configuration values.

        The dictionary includes:
            - low_confidence_threshold: Integer threshold for low confidence.
            - output_extension: File extension for output files.
            - image_extensions: Tuple of supported image file extensions.

        Returns:
            dict: Dictionary with configuration settings.
        """
        return {
            "low_confidence_threshold" : 75,
            "output_extension" : ".json",
            "image_extensions": ('.TIF', '.png', '.jpg', '.jpeg'),
        }

    @staticmethod
    def requiredFolders() -> dict:
        """
        Returns a dictionary of required folder paths for the project.

        The dictionary includes:
            - input_folder: Path for input files, the entry point to the pipeline.
            - core_folders: Base path for core folders, all folders below this exists within the core folder.
            - logs_folder: Path for log files.
            - json_folder: Path for JSON files.
            - images_folder: Path for image files.
            - json_sorter: Path for sorted JSON files.
            - failed_folder: Path for failed processing files.
            - images_sorter: Path for sorted image files.
            - failed_ocr_folder: Path for files with failed OCR.
            - processed_folder: Path for successfully processed files.
            - low_confidence_folder: Path for files with low OCR confidence.

        Returns:
            dict: Dictionary mapping folder names to their paths.
        """

        return {
            "input_folder": "input",
            "core_folders": "core_folders",
            "logs_folder": "core_folders/logs",
            "json_folder": "core_folders/json",
            "images_folder": "core_folders/images",
            "json_sorter" : "core_folders/json_sorter",
            "failed_folder": "core_folders/failed_alto",
            "images_sorter" : "core_folders/images_sorter",
            "failed_ocr_folder": "core_folders/failed_ocr",
            "processed_folder": "core_folders/success_alto",
            "low_confidence_folder": "core_folders/failed_low_confidence",
        }







