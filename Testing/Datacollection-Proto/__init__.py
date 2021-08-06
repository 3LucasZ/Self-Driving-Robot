#IMPORTS
#networking
from flask import Flask,request, render_template
from flask_socketio import SocketIO


#camera
import cv2
import base64


#data collection
import os
import shutil
import pathlib
import subprocess
import time


#SETUP
#app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)


#camera
camera = cv2.VideoCapture(0)
camera.set(3, 64)
camera.set(4, 64)
FPS = 5
canRecord = False


#motors
MOTOR_DEFAULT = 50
motorBias = 0


#data collection
#path names
datasetPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "datasets/")
#clear all the tubs (for debugging only)
for oldTub in os.listdir(datasetPath):
    shutil.rmtree(os.path.join(datasetPath, oldTub))
tubName = "tub" + str(int(time.time())) + "/"
tubPath = os.path.join(datasetPath, tubName)
imagesPath = os.path.join(tubPath, "Images/")
biasFilePath = os.path.join(tubPath, "bias.txt")

#create the directories
os.mkdir(tubPath)
os.mkdir(imagesPath)

#open bias file and allow writing data. If file already exists it is overridden.
biasFile = open(biasFilePath, "w")


@socketio.on('startRecording')
def record():
    global canRecord
    canRecord = True
    print("Recording started")


@socketio.on('pauseRecording')
def stopRecord():
    global canRecord
    canRecord = False
    print("Recording paused")


@socketio.on('recordingSystem')
def recording_system():
    framesTaken = 0
    #get height and width of camera
    retval, frame = camera.read()
    height = frame.shape[0]
    width = frame.shape[1]
    channels = frame.shape[2]
    print("cam px height:", height)
    print("cam px width:", width)
    print("cam channels:", channels)
    while True:
        if canRecord:
            framesTaken += 1
            #take picture into frame
            retval, frame = camera.read()
            #crop the image
            #frame = frame[height-50:height, 0:width]
            #save image into images
            cv2.imwrite(imagesPath + "frame" + str(framesTaken) + ".jpg", frame)
            #save current motor bias to bias.txt
            biasFile.write(str(motorBias) + "\n")
            #encode picture to jpg
            retval, jpg = cv2.imencode('.jpg', frame)
            #encode to base 64 string
            jpg_as_text = str(base64.b64encode(jpg))
            #remove b''
            jpg_as_text = jpg_as_text[2:-1]
            #emit text
            socketio.emit('jpg_string', jpg_as_text)
        #async sleep
        socketio.sleep(1/FPS)    
        
'''
@socketio.on('startPracticing')
def practice():
    while True:
        #take picture into frame
        retval, frame = camera.read()
        #encode picture to jpg
        retval, jpg = cv2.imencode('.jpg', frame)
        #encode to base 64 string
        jpg_as_text = str(base64.b64encode(jpg))
        #remove b''
        jpg_as_text = jpg_as_text[2:-1]
        #emit text
        socketio.emit('jpg_string', jpg_as_text)
        #async sleep
        socketio.sleep(1/FPS)
'''

@socketio.on('connect')
def connect():
    print('A client connected.')


@socketio.on('disconnect')
def disconnect():
    print('A client disconnected.')


@socketio.on('motorsOn')
def motors_on():
    print("motor on received")


@socketio.on('motorsOff')
def motors_off():
    print("motor off received")


@socketio.on('motorBias')
def set_motor_bias(data):
    global motorBias
    motorBias = data
    print("Left motor:", MOTOR_DEFAULT - motorBias)
    print("Right motor:", MOTOR_DEFAULT + motorBias)
    

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    print("Ready for clients.")
    socketio.run(app, host='0.0.0.0', port=5000)
    
print("Closing program")
biasFile.close()
#sanity check
print("recorded motor values: " + os.popen("wc -l < " + biasFilePath).read().strip())
print("recorded images: " + os.popen("ls " + imagesPath + " | wc -l").read().strip())