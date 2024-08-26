import os
import shutil
from utils.config import coreConfig


# Initialisation of required folders and parameters
core_config = coreConfig()
parameters = core_config.requiredValues()
folders = core_config.requiredFolders()

json_sorter_folder = folders["json_sorter"]
images_sorter_folder = folders["images_sorter"] 
image_extensions = parameters["image_extensions"]



# Verify json or images sorter folder contains sub folders
def contains_subfolders(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            return True
    return False


def process_sub_folders(parent_folder_path, file_extention,destination):
    subfolders = []
    for f in os.listdir(parent_folder_path):
        if os.path.isdir(os.path.join(parent_folder_path, f)):
            subfolders.append(f)
    
    # Get the files under each sub folders    
    for subfolder in subfolders:
        for file_name in os.listdir(os.path.join(parent_folder_path, subfolder)):
            if file_name.endswith(file_extention):
                split_files( parent_folder_path,file_name,subfolder,destination)
                
        # Delete the parent folder from the sorting forlder after processing
        shutil.rmtree(os.path.join(parent_folder_path,subfolder))

   
def split_files(parent_folder_path,filename,subfolder,destination):
    original_file_path  = os.path.join(parent_folder_path,subfolder,filename)
    project_folder_name = filename.rsplit('-')[0]  # Split at '-'
    new_file_folder_path = os.path.join(destination,subfolder.split('-',1)[0].replace(' ',''), project_folder_name) # Split folders name from the left side
    	
    # Create the sub folder in the new destination
    if not os.path.exists(new_file_folder_path):
        os.makedirs(new_file_folder_path)

    try:
        # Delete existing file and replace with new one
        moving_path = os.path.join(new_file_folder_path, filename)
        if os.path.exists(moving_path):
            print(f"Deleting existing folder {moving_path} ...")
            os.remove(moving_path)

        print(f"Moving file from {original_file_path} to {new_file_folder_path}")
        shutil.move(original_file_path, new_file_folder_path)
        print(new_file_folder_path)
    except Exception as e:
        print(f"Error moving file: {e}")

def main():
    if contains_subfolders(json_sorter_folder):
        process_sub_folders(json_sorter_folder, '.json', 'json')


    if contains_subfolders(images_sorter_folder):
        process_sub_folders(images_sorter_folder, image_extensions, 'images')


