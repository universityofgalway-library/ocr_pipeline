from utils.client import TextractOCR
from utils.config import coreConfig
from  utils.sort import main

# Instantiate and Verify all required folders
core_config = coreConfig()
core_config.verifyFolders()
input_folder = core_config.requiredFolders()["input_folder"]


if __name__ == '__main__':
    # Instantiate the TextractOCR class
    # textract_ocr = TextractOCR()

    # Define the parent input folder
    # textract_ocr.select_image(input_folder)
    main()
