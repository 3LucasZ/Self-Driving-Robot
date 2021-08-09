import Modules.utils as util
config = util.get_config()

on_pi = config["ON_PI"]

import cv2
import base64

class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)

        #changing these might break the camera!!
        self.camera.set(3, 64)
        self.camera.set(4, 64)

        #get camera info and print it
        _, frame = self.camera.read()

        self.height = frame.shape[0]
        self.width = frame.shape[1]
        self.channels = frame.shape[2]
        print("cam px height:", self.height)
        print("cam px width:", self.width)
        print("cam channels:", self.channels)
        
    def take_picture(self):
        #take picture into frame
        _, frame = self.camera.read()

        if not on_pi:
            #crop the image to 64 x 64
            frame = frame[int(self.height/2)-32:int(self.height/2)+32, int(self.width/2)-32:int(self.width/2)+32]
        if on_pi:
            #flip the image horiz and vert
            frame = cv2.flip(frame, -1)

        #encode frame to jpg
        retval, encodedFrame = cv2.imencode('.jpg', frame)
        #encode to base 64 string
        encodedFrame = str(base64.b64encode(encodedFrame))
        #remove b''
        encodedFrame = encodedFrame[2:-1]

        return frame, encodedFrame 