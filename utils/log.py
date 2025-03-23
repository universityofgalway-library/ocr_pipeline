from datetime import datetime

class LogActivities:
    """
    A class to handle logging of activities related to file processing.
    """    

    def __init__(self, logs_folder: str):
        """
        Initializes the LogActivities class with the path to the log folder.
        """
        self.logs_folder = logs_folder.rstrip('/')  # Ensure no trailing slash

    def confidence(self, input_file: str, average_confidence: float) -> None:
        """
        Logs the average confidence score

        Args:
            input_file (str): The name of the input file.
            average_confidence (float): The average confidence score to be logged.
        Returns:
            None
        """
        log_file_path = f"{self.logs_folder}/avg_confidence_score.log"
        try:
            with open(log_file_path, "a", encoding="UTF-8") as f:
                f.write(f"{datetime.now()} - {input_file}: {average_confidence}\n")
        except Exception as e:
            self.error(f"{datetime.now()} - Error logging confidence score: {e}")


    def sorting(self, message: str) -> None:
        """
        Logs the activies of file being sorted into the Json and images folder

        Args:
            message (str): The name of the input file.
        Returns:
            None
        """
        log_file_path = f"{self.logs_folder}/sorting.log"
        try:
            with open(log_file_path, "a", encoding="UTF-8") as f:
                f.write(f"{datetime.now()} - {message} \n")
        except Exception as e:
            self.error(f"{datetime.now()} - Error logging sorting activities: {e}")


    def error(self, message: str) -> None:
        """
        Logs the activies of file being sorted into the Json and images folder

        Args:
            message (str): The name of the input file.
        Returns:
            None
        """
        log_file_path = f"{self.logs_folder}/errors.log"
        self.messageLogging(log_file_path, message)

    def overwrite(self, message: str) -> None:
        """
        Logs the activies of file being sorted into the Json and images folder

        Args:
            message (str): The name of the input file.
        Returns:
            None
        """
        log_file_path = f"{self.logs_folder}/overwrite.log"
        self.messageLogging(log_file_path, message)
        
    def processing(self, message: str) -> None:
        """
        Logs terminal outputs to the a processing log file

        Args:
            message (str): The name of the input file.
        Returns:
            None
        """
        log_file_path = f"{self.logs_folder}/processing.log"
        self.messageLogging(log_file_path, message)
    
    @staticmethod
    def messageLogging(log_file_path, message):
        try:
            with open(log_file_path, "a", encoding="UTF-8") as f:
                f.write(f"{datetime.now()} - {message} \n")
        except Exception as e:
            with open(log_file_path, "a", encoding="UTF-8") as f:
                f.write(f"{datetime.now()} - Error logging error message: {e} \n")