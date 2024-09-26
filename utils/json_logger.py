import os
import json
import shutil
from datetime import datetime
from utils.config import CoreConfig


class JsonLogger():
   
    def __init__(self):
        """
        Initialise the JsonLogger class with required folder paths from the config file.
        """

        # Initialisation of required folders and parameters
        core_config = CoreConfig()
        self.folders = core_config.requiredFolders()    
        self.json_log_path = self.folders["json_log_path"]


    def log_error_as_json(self, error_message: str, split_file_name: str) -> None:
        json_log_file = os.path.join(self.json_log_path, "failed_jobs_log.json")
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_data = {}

        # Check if the log file exists; if yes, load the existing data
        if os.path.exists(json_log_file):
            with open(json_log_file, 'r', encoding='UTF-8') as json_file:
                log_data = json.load(json_file)

        # Ensure the current date section exists in the dictionary
        if current_date not in log_data:
            log_data[current_date] = {}
        
        if error_message not in log_data[current_date]:
            log_data[current_date][error_message] = []
        
        # Log data under error_message
        log_data[current_date][error_message].append(split_file_name)

        # Write the updated log back to the JSON file
        with open(json_log_file, 'w', encoding='UTF-8') as json_file:
            json.dump(log_data, json_file, ensure_ascii=False, indent=4)
