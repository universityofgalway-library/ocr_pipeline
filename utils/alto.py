import os
import json
import math
import shutil
from PIL import Image
from utils.config import CoreConfig
from utils.log import LogActivities
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, tostring


class AltoGenerator():

    def __init__(self):

        """
        Initialise the AltoGenerator class with required folder paths and parameters from the config file.
        """

        # Initialisation of required folders and parameters
        core_config = CoreConfig()
        self.folders = core_config.requiredFolders()
        self.parameters = core_config.requiredValues()
        
        # Folders nmaes from config.py
        self.logs_folder = self.folders["logs_folder"]
        self.json_folder = self.folders["json_folder"]
        self.failed_folder = self.folders["failed_folder"]
        self.images_folder = self.folders["images_folder"]
        self.processed_folder = self.folders["processed_folder"]
        
        # Parameters from config.py 
        self.image_extensions = self.parameters["image_extensions"]
        self.output_extension = self.parameters["output_extension"]
        self.rename_failed_json = self.parameters["rename_failed_json"]
        self.rename_failed_image = self.parameters["rename_failed_image"]
        self.low_confidence_threshold = self.parameters["low_confidence_threshold"]

        # Logging initailisation has to come after logs folder name
        self.log_activity = LogActivities(self.logs_folder)


        self.process_files(self.json_folder, self.failed_folder, self.images_folder, self.image_extensions, self.processed_folder)

    def process_files(self, json_folder, failed_folder, images_folder, image_extensions, processed_folder):
   
            # List all folders in the json folder sorted in alphabetical order
            json_folders = sorted([d for d in os.listdir(json_folder) if os.path.isdir(os.path.join(json_folder, d))], reverse=True)
            
            # Throw an Exception and stop script if the json folder is empty
            if not json_folders:
                raise FileNotFoundError("No folders found in the json directory.")
                # return
            
            # Get the top folder from the sorted json folder
            top_json_folder = json_folders[0]
            top_json_folder_path = os.path.join(json_folder, top_json_folder) 
            top_images_folder_path = os.path.join(images_folder, top_json_folder) 
        
            
            subfolder_top_json_folder =  sorted([subfolders for subfolders in os.listdir(top_json_folder_path) if os.path.isdir(os.path.join(top_json_folder_path, subfolders))], reverse=True)
        
            for subfolder in subfolder_top_json_folder:
                
                json_subfolder_path = os.path.join(top_json_folder_path, subfolder)
                image_subfolder_path = os.path.join(top_images_folder_path, subfolder)

                # Path to the new failed folder based on the subdirectory
                new_failed_folder = os.path.join(failed_folder, top_json_folder)
            
                # Check if the sub directories directory match
                image_subdirs = os.listdir(top_images_folder_path)
                json_subdirs =os.listdir(top_json_folder_path)
                missing_dir = set(image_subdirs) ^ set(json_subdirs)

                # Move missing subfolder to failed folder
                if missing_dir:
                    for folder in missing_dir:
                        os.makedirs(new_failed_folder, exist_ok=True)
                        if os.path.exists(os.path.join(top_images_folder_path, folder)):              
                            old_path = os.path.join(top_images_folder_path,folder)
                            new_path = old_path + '_image'
                            os.rename(old_path, new_path)
                            shutil.move(new_path, new_failed_folder)
                        
                        if os.path.exists(os.path.join(top_json_folder_path, folder)):
                            shutil.move(os.path.join(top_json_folder_path,folder), new_failed_folder)

                # Extract all JSON file names (without extension) from the current subfolder
                json_files = [os.path.splitext(f)[0] for f in os.listdir(json_subfolder_path) if f.endswith(self.output_extension)]

                # Code to move JSON and images to failed folder if either fails
                if not json_files:

                    # create a parent folder in the failed folder if it does not exist
                    os.makedirs(new_failed_folder, exist_ok=True)
                    shutil.move(os.path.join(json_folder, top_json_folder), new_failed_folder)

                    # check the images folders if the same folder exist and move its
                    if os.path.exists(image_subfolder_path):
                        new_image_folder_name = os.path.join(image_subfolder_path + '_image')
                        shutil.move(new_image_folder_name, new_failed_folder)


                    raise FileNotFoundError("No JSON files found in the sub folder.")
                else:
                    # If no equivalent image file is found, move the exisiting json folder to failed folder
                    if not os.path.exists(image_subfolder_path):
                        # create a parent folder in the failed folder if it does not exist
                        os.makedirs(new_failed_folder, exist_ok=True)

                        shutil.move(os.path.join(image_subfolder_path, '_images'), new_failed_folder)
                        shutil.move(os.path.join(json_folder, top_json_folder), new_failed_folder) # Move the JSON folder

                        raise FileNotFoundError("No corresponding folder found in the images directory.") 
                    else:
                        # Creates a list of images from the images folders for further extraction
                        image_files = [os.path.splitext(f)[0] for f in os.listdir(image_subfolder_path) if f.endswith(image_extensions)]
        
                        
                    
                        # Splits the files/images name from the extension for comparison
                        json_file_names = {os.path.splitext(f)[0] for f in json_files}
                        image_file_names = {os.path.splitext(f)[0] for f in image_files}
                    
                                
                        # Stops the script and move the json/image folder to the failed folder
                        if len(json_files) != len(image_files) or json_file_names != image_file_names:
                            # Create parant folder in sub directory
                            os.makedirs(new_failed_folder, exist_ok=True)
                            old_path = os.path.join(top_json_folder_path, subfolder)
                            # Move content for subdirectory to failed folder
                            shutil.move(old_path, new_failed_folder)

                            # os.rename(os.path.join(new_failed_folder, top_json_folder_path), new_path)
                            old_path = os.path.join(top_images_folder_path, subfolder)
                            new_path = old_path +  '_image'
                            os.rename(old_path, new_path)  
                            shutil.move(new_path, new_failed_folder)
                            

                            raise ValueError("Mismatch in number of files or names between JSON and images folder.")
            
                        # Generate the ALTO XML file
                        stripped_subfolder_name = subfolder.replace("(", "").replace(")", "")
                        
                        # Create the output directory if it doesn't exist
                        output_dir = os.path.join(processed_folder, top_json_folder, subfolder)
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                    
                        output_file = os.path.join(processed_folder, top_json_folder,subfolder,f"{stripped_subfolder_name.split('-')[0].replace(' ','')}.xml")
                        
                        
                        # Begin generating the ALTO XML file
                        self.generate_alto_xml(json_files, output_file, top_json_folder, subfolder)
                        # return 
                    
                        # Create a new folder in the success directory with the original JSON folder name
                        processed_json_folder = os.path.join(processed_folder, top_json_folder, subfolder)
                        os.makedirs(processed_json_folder, exist_ok=True)

                        # Rename and move the JSON and image folders
                        json_renamed_folder = os.path.join(processed_json_folder, self.rename_failed_json)
                        image_renamed_folder = os.path.join(processed_json_folder, self.rename_failed_image)

                        os.rename(json_subfolder_path, json_renamed_folder)
                        os.rename(image_subfolder_path, image_renamed_folder)

                        print(f"Processing completed successfully for {top_json_folder}")

            # Check if the folder exists and is empty
            if os.path.exists(top_json_folder_path) and len(os.listdir(top_json_folder_path)) == 0:
                os.rmdir(top_json_folder_path)

            if os.path.exists(top_images_folder_path) and len(os.listdir(top_images_folder_path)) == 0:
                os.rmdir(top_images_folder_path)


            # Order: 3

    def generate_alto_xml(self, json_files, output_file, top_json_folder, subfolder):

        root = Element("alto", attrib={
            'xmlns': "http://www.loc.gov/standards/alto/ns-v3#",
            'xmlns:xlink': "http://www.w3.org/1999/xlink",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'xsi:schemaLocation': "http://www.loc.gov/standards/alto/ns-v3# http://www.loc.gov/alto/v3/alto-3-0.xsd"
        })

    # Create the description section of the ALTO XML 
        description = SubElement(root, "Description")
        measurement_unit = SubElement(description, "MeasurementUnit")
        measurement_unit.text = "pixel" # Measurement unit in pixel 
        SubElement(description, "sourceImageInformation")
        ocr_processing = SubElement(description, "OCRProcessing", attrib={'ID': "OCR_0"})
        ocr_processing_step = SubElement(ocr_processing, "ocrProcessingStep")
        processing_software = SubElement(ocr_processing_step, "processingSoftware")
        software_name = SubElement(processing_software, "softwareName")
        software_name.text = "Abbyy Finder"

        layout = SubElement(root, "Layout")

        self.process_json_files(json_files, top_json_folder, layout, subfolder)

        xml_string = tostring(root, encoding='utf-8')
        parsed_xml = parseString(xml_string)
        xml_string_pretty = parsed_xml.toprettyxml()

        with open(output_file, 'w',encoding='utf-8') as f:
            f.write(xml_string_pretty)   

    def get_image_size(image_path):
        with Image.open(image_path) as img:
            return img.size

    def process_json_files(self, json_files, top_json_folder, layout, subfolder):

        for json_file in json_files:
            json_file_path = os.path.join(self.json_folder, top_json_folder,subfolder,json_file + self.output_extension)
            json_file_name = os.path.splitext(json_file)[0]

            image_files = []
            for ext in self.image_extensions:
                full_path = os.path.join(self.images_folder,top_json_folder,subfolder, json_file_name + ext)
                if os.path.exists(full_path):
                    image_files.append(full_path)
        
            # image_path_extension = image_file
            image_file_path = image_files[0] if image_files else None
        
            if image_file_path is None or not os.path.exists(image_file_path):
                raise FileNotFoundError(f"Image file corresponding to {json_file} not found.")
            else:
                image_width, image_height = self.get_image_size(image_file_path)

                # Load JSON data
                with open(json_file_path, 'r',encoding='utf-8') as f:
                    data = json.load(f)

                page = SubElement(layout, "Page", attrib={
                    'WIDTH': str(image_width), 'HEIGHT': str(image_height),
                    'PHYSICAL_IMG_NR': "0", 'ID': json_file_name
                })
                print_space = SubElement(page, "PrintSpace", attrib={
                    'HPOS': "0", 'VPOS': "0",
                    'WIDTH': str(image_width), 'HEIGHT': str(image_height)
                })

                line_count = 0
                string_count = -1
                cblock_count = 0

                # Calculate the VPOS, HPOS, Width and Height 
                self.calculate_positions(data, image_width, image_height, print_space, line_count, string_count, cblock_count)   

    def calculate_positions(self, data, image_width, image_height, print_space, line_count, string_count, cblock_count):
        for block in data['Blocks']:
                if block['BlockType'] == 'LINE':
                    composed_block = SubElement(print_space, "ComposedBlock", attrib={
                        'ID': f"cblock_{cblock_count}",
                        'HPOS': str(math.ceil(block['Geometry']['BoundingBox']['Left'] * image_width) ),
                        'VPOS': str(math.ceil(block['Geometry']['BoundingBox']['Top'] * image_height) ),
                        'WIDTH': str(math.ceil(block['Geometry']['BoundingBox']['Width'] * image_width) ),
                        'HEIGHT': str(math.ceil(block['Geometry']['BoundingBox']['Height'] * image_height) )
                    })
                    cblock_count += 1

                    text_block = SubElement(composed_block, "TextBlock", attrib={
                        'ID': f"block_{line_count}",
                        'HPOS': str(math.ceil(block['Geometry']['BoundingBox']['Left'] * image_width) ),
                        'VPOS': str(math.ceil(block['Geometry']['BoundingBox']['Top'] * image_height) ),
                        'WIDTH': str(math.ceil(block['Geometry']['BoundingBox']['Width'] * image_width) ),
                        'HEIGHT': str(math.ceil(block['Geometry']['BoundingBox']['Height'] * image_height) )
                    })

                    text_line = SubElement(text_block, "TextLine", attrib={
                        'ID': f"line_{line_count}",
                        'HPOS': str(math.ceil(block['Geometry']['BoundingBox']['Left'] * image_width) ),
                        'VPOS': str(math.ceil(block['Geometry']['BoundingBox']['Top'] * image_height) ),
                        'WIDTH': str(math.ceil(block['Geometry']['BoundingBox']['Width'] * image_width) ),
                        'HEIGHT': str(math.ceil(block['Geometry']['BoundingBox']['Height'] * image_height) )
                    })
                    line_count += 1

                    for index, word_id in enumerate(block['Relationships'][0]['Ids']):
                        word = next((word for word in data['Blocks'] if word['Id'] == word_id), None)
                        if word:
                            string_count += 1

                            string = SubElement(text_line, "String", attrib={
                                'ID': f"string_{string_count}",
                                'HPOS': str(math.ceil(word['Geometry']['BoundingBox']['Left'] * image_width)),
                                'VPOS': str(math.ceil(word['Geometry']['BoundingBox']['Top'] * image_height)),
                                'WIDTH': str(math.ceil(word['Geometry']['BoundingBox']['Width'] * image_width)),
                                'HEIGHT': str(math.ceil(word['Geometry']['BoundingBox']['Height'] * image_height)),
                                'CONTENT': word['Text'],
                                'WC': str(round(word['Confidence'] / 100, 2))
                            })

                            if index < len(block['Relationships'][0]['Ids']) - 1:
                                next_word = next((word for word in data['Blocks'] if word['Id'] == block['Relationships'][0]['Ids'][index + 1]), None)
                                if next_word:
                                    sp_width = next_word['Geometry']['BoundingBox']['Left'] - (
                                            word['Geometry']['BoundingBox']['Left'] + word['Geometry']['BoundingBox']['Width'])
                                    sp = SubElement(text_line, "SP", attrib={
                                        'WIDTH': str(math.ceil(sp_width * image_width)),
                                        'VPOS': str(math.ceil(word['Geometry']['BoundingBox']['Top'] * image_height)),
                                        'HPOS': str(math.ceil(word['Geometry']['BoundingBox']['Left'] + word['Geometry']['BoundingBox']['Width'] * image_width))
                                    })