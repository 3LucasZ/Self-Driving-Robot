import Modules.utils as utils
import os
import sys

DATASETS_PATH = os.path.join(utils.get_root(), 'Datasets')
DATASET_NAME = os.path.basename(sys.argv[1])
DATASET_PATH = os.path.join(DATASETS_PATH, DATASET_NAME)
ZIPPED_PATH = DATASET_PATH+'.zip'

#zip whole folder
cmd = 'zip -r '+ZIPPED_PATH+' '+DATASET_PATH
os.system(cmd)