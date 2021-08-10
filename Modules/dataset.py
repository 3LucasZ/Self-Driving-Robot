import os
import shutil
import pathlib
import cv2
import Modules.utils as util

class Dataset():
    def __init__(self, name, debug=False):
        self.name = name
        datasetsPath = os.path.join(util.get_root(), 'Datasets')

        if debug:
            for oldData in os.listdir(datasetsPath):
                shutil.rmtree(os.path.join(datasetsPath, oldData))
        
        self.dataPath = os.path.join(datasetsPath, self.name)
        self.labelsPath = os.path.join(self.dataPath, "labels.txt")
        self.imagesPath = os.path.join(self.dataPath, "Images")

        #create files/directories
        os.mkdir(self.dataPath)
        os.mkdir(self.imagesPath)
        self.labelsFile = open(self.labelsPath, "w")
        
    def saveImage(self, image, imageName):
        cv2.imwrite(os.path.join(self.imagesPath, imageName), image)

    def saveLabelsList(self, labelsList):
        for label in labelsList:
            self.labelsFile.write(str(label) + "\n")
    
    def close(self):
        self.labelsFile.close()
        #sanity check
        print("recorded motor values: " + os.popen("wc -l < " + str(self.labelsPath)).read().strip())
        print("recorded images: " + os.popen("ls " + str(self.imagesPath) + " | wc -l").read().strip())