#IMPORTS
from flask import Flask, render_template
import Modules.utils as utils
import os
import sys


#SETUP
#paths
ROOT = utils.get_root()
DATASET_NAME = os.path.basename(sys.argv[1])
DATASET_PATH = os.path.join(ROOT, 'Datasets', DATASET_NAME)
IMAGES_PATH = os.path.join(DATASET_PATH, 'Images')
LABELS_PATH = os.path.join(DATASET_PATH, 'labels.txt')

#extra information for serving
cmd = 'ls '+os.path.join(DATASET_PATH, 'Images')+' | wc -l'
MAX_FRAMES = int(os.popen(cmd).read())
LABELS_FILE = open(LABELS_PATH, "r")
LABELS_LIST = [int(value) for value in LABELS_FILE.read().splitlines()]

#app
config = utils.get_config()
app = Flask(__name__, static_folder=ROOT)
app.config['SECRET_KEY'] = 'mysecret'
HOST = config['SERVER']['HOST']
PORT = config['SERVER']['PORT']


#FLASK SERVING
@app.route('/')
def home():
    return render_template('index.html', maxFrames=MAX_FRAMES, labelsList=LABELS_LIST, datasetName=DATASET_NAME)


#RUN APP
if __name__ == '__main__':
    app.run(host=HOST, port=PORT)