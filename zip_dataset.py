import Modules.utils as utils
import os
import sys

DATASETS_PATH = os.path.join(utils.get_root(), 'Datasets')
for i in range(1, len(sys.argv)):
    DATASET_NAME = os.path.basename(sys.argv[i])
    DATASET_PATH = os.path.join(DATASETS_PATH, DATASET_NAME)
    ZIPPED_PATH = DATASET_PATH+'.zip'

    os.chdir(DATASET_PATH)
    cmd = 'zip -r '+ZIPPED_PATH+' .'
    os.system(cmd)
    os.chdir(utils.get_root())