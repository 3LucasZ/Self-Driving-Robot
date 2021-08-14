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
import Modules.dataset as data


#misc
import time
import os


#SETUP
#app
app = Flask(__name__, static_folder=os.path.join(util.get_root(), 'static'))
app.config['SECRET_KEY'] = 'mysecret'
HOST = config['SERVER']['HOST']
PORT = config['SERVER']['PORT']
socketio = SocketIO(app)

#nmotor setup
motorController = motor.MotorController()
FORWARD_SPEED = 45
PIVOT_SPEED = 15
# 3 motor labels: 0 is left pivot, 1 is forward, 2 is right pivot
directionID = 1

# camera setup
camera = cam.Camera()
canRecord = False
FPS = 8

# dataset setup
datasetName = input("Enter dataset name: ")
dataset = data.Dataset(name=datasetName, debug=False)
labelsList = []


#SOCKETIO
@socketio.on('startRecording')
def record():
    motorController.forward(FORWARD_SPEED)
    global canRecord
    canRecord = True
    print("Starting motors")
    print("Recording started")


@socketio.on('pauseRecording')
def stop_record():
    motorController.stop()
    global canRecord
    canRecord = False
    print("Stopping motors")
    print("Recording paused")


#make sure recordingSystem is started once only during the program's lifetime
recordingStarted = False
@socketio.on('recordingSystem') 
def recording_system():
    global recordingStarted
    global directionID
    if not recordingStarted:
        recordingStarted = True
        framesTaken = 0
        while True:
            frame, encodedFrame = camera.take_picture()
            if canRecord:
                framesTaken += 1
                dataset.saveImage(image=frame, imageName='frame'+str(framesTaken)+'.jpg')
                #save current motor label
                labelsList.append(directionID)
                
                #sanity checks
                print("On frame: " + str(framesTaken))
                print("labels list elements: " + str(len(labelsList)))
            #emit text
            socketio.emit('jpg_string', encodedFrame)
            #async sleep
            socketio.sleep(1/FPS)  

@socketio.on('connect')
def connect():
    print('A client connected.')
    motorController.on()
    

@socketio.on('disconnect')
def disconnect():
    print('A client disconnected.')
    motorController.stop()


@socketio.on('direction')
def set_direction(data):
    global directionID
    directionID = data
    if directionID == 0:
        motorController.left_pivot(PIVOT_SPEED)
    elif directionID == 1:
        motorController.forward(FORWARD_SPEED)
    elif directionID == 2:
        motorController.right_pivot(PIVOT_SPEED)
    elif directionID == 3:
        motorController.forward(FORWARD_SPEED)
    

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
dataset.saveLabelsList(labelsList)
dataset.close()