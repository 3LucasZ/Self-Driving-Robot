import Modules.utils as utils
import os
import sys
import time

DATASETS_PATH = os.path.join(utils.get_root(), 'Datasets')

for dataset in sys.argv[1:]:
    #sometimes the dataset ends with / and messes the program up
    if dataset[-1] == '/':
        del dataset[-1] 
    DATASET_NAME = os.path.basename(dataset)
    DATASET_PATH = os.path.join(DATASETS_PATH, DATASET_NAME)
    ZIPPED_PATH = DATASET_PATH+'.zip'

    print("Zipping", DATASET_NAME, "to", ZIPPED_PATH)
    time.sleep(2)
    os.chdir(DATASET_PATH)
    cmd = 'zip -r '+ZIPPED_PATH+' .'
    os.system(cmd)
    os.chdir(DATASETS_PATH)

print("Finished")