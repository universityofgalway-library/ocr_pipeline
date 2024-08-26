def config(): 
    settings = {
        "input_folder": "input",
        "output_extension" : ".json",
        "json_folder": "core_folders/json",
        "images_folder": "core_folders/images",
        "failed_folder": "core_folders/failed",
        "processed_folder": "core_folders/success",
        "json_sorter" : "core_folders/json_sorter",
        "images_sorter" : "core_folders/images_sorter",
        "image_extensions": ('.TIF', '.png', '.jpg', '.jpeg')
    }

    return settings