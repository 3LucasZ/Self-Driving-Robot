import Modules.utils as utils
import os
import sys
import time

DATASETS_PATH = os.path.join(utils.get_root(), 'Datasets')
NUM_DATASETS = len(sys.argv) - 1
print("Zipping", NUM_DATASETS, "datasets...")
for i in range(NUM_DATASETS):
    DATASET_NAME = os.path.basename(sys.argv[i + 1])
    DATASET_PATH = os.path.join(DATASETS_PATH, DATASET_NAME)
    ZIPPED_PATH = DATASET_PATH+'.zip'

    print("Zipping:", DATASET_NAME, "to", ZIPPED_PATH)
    time.sleep(2)
    os.chdir(DATASET_PATH)
    cmd = 'zip -r '+ZIPPED_PATH+' .'
    os.system(cmd)
    os.chdir(utils.get_root())