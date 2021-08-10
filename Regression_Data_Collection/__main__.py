#custom package
import Modules.utils as util
config = util.get_config()
on_pi = config['ON_PI']


#IMPORTS
#networking
from flask import Flask,request, render_template
from flask_socketio import SocketIO


#camera
import cv2
import Modules.camera as cam


#motors
import Modules.motor_controller as motor


#data collection
import os
import shutil
import pathlib
import time


#SETUP
#app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)
HOST = config['SERVER']['HOST']
PORT = config['SERVER']['PORT']

#motor setup
motorController = motor.MotorController()
MOTOR_DEFAULT = 20
motorBias = 0

#camera setup
camera = cam.Camera()
canRecord = False
FPS = 15

#data collection
#path names
ROOT_PATH = os.path.join(util.get_root(), 'Data_Collection')
DATA_PATH = os.path.join(ROOT_PATH, "datasets")
#clear all the tubs (for debugging only)
#for oldTub in os.listdir(datasetPath):
#    shutil.rmtree(os.path.join(datasetPath, oldTub))
if os.listdir(DATA_PATH):
    max = 1
    for oldTub in os.listdir(DATA_PATH):
        oldTubId = int(oldTub[3:])
        if oldTubId > max:
            max = oldTubId
    tubName = "tub" + str(max + 1)
else:
    tubName = "tub1"
TUB_PATH = os.path.join(DATA_PATH, tubName)
IMAGES_PATH = os.path.join(TUB_PATH, "Images")
BIAS_PATH = os.path.join(TUB_PATH, "bias.txt")
biasList = []

#create the directories
os.mkdir(TUB_PATH)
os.mkdir(IMAGES_PATH)
#open bias file and allow writing data. If file already exists it is overridden.
biasFile = open(BIAS_PATH, "w")


#SOCKETIO
@socketio.on('startRecording')
def record():
    global canRecord
    canRecord = True
    motorController.set_to(left=MOTOR_DEFAULT, right=MOTOR_DEFAULT)
    print("Recording started")
    print("Starting motors")


@socketio.on('pauseRecording')
def stop_record():
    global canRecord
    canRecord = False
    motorController.set_to(left=0, right=0)
    print("Recording paused")
    print("Stopping motors")


@socketio.on('recordingSystem') 
def recording_system():
    framesTaken = 0
    while True:
        frame, encodedFrame = camera.take_picture()
        if canRecord:
            framesTaken += 1
            #save frame
            cv2.imwrite(os.path.join(IMAGES_PATH, "frame"+str(framesTaken)+".jpg"), frame)
            #save current motor bias
            biasList.append(motorBias)
            #sanity checks
            print("On frame: " + str(framesTaken))
            print("bias list elements: " + str(len(biasList)))
        #emit text
        socketio.emit('jpg_string', encodedFrame)
        #async sleep
        socketio.sleep(1/FPS)  


@socketio.on('connect')
def connect():
    print('A client connected.')
    motors_on()
    

@socketio.on('disconnect')
def disconnect():
    print('A client disconnected.')
    motors_off()
    

@socketio.on('motorsOn')
def motors_on():
    print("motor on received")
    motorController.on()
    

@socketio.on('motorsOff')
def motors_off():
    print("motor off received") 
    motorController.off()


@socketio.on('motorBias')
def set_motor_bias(data):
    global motorBias
    motorBias = data
    print(motorBias)
    leftMotor = MOTOR_DEFAULT + motorBias
    rightMotor = MOTOR_DEFAULT - motorBias
    motorController.set_to(left=leftMotor, right=rightMotor)
    

#FLASK SERVING
@app.route('/')
def home():
    return render_template('index.html')


#RUN APP
if __name__ == '__main__':
    print('Ready for clients.')
    print('Running on <SERVER_IP>:' + str(PORT))
    socketio.run(app, host=HOST, port=PORT)
    

#CLEAN UP
print("Closing program")
#add biases to biasFile and close the file
for b in biasList:
    biasFile.write(str(b) + "\n")
biasFile.close()

#sanity check
print("recorded motor values: " + os.popen("wc -l < " + str(BIAS_PATH)).read().strip())
print("recorded images: " + os.popen("ls " + str(IMAGES_PATH) + " | wc -l").read().strip())