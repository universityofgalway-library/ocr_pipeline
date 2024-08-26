import os 
import shutil

'''
RETURN FOLDERS TO THEIR ORIGINAL DIRECTORY 
NOT TO BE USED IN PRODUCTION
'''

for root, dirs , files in os.walk('core_folders/images_sorter'):
    for dirname in dirs: 
        shutil.move(os.path.join(root, dirname), 'input')


for root, dirs , files in os.walk('core_folders/json_sorter'):
    for dirname in dirs: 
        shutil.rmtree(os.path.join(root, dirname))