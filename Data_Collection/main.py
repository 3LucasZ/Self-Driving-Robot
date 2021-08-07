on_pi = False

#IMPORTS
#networking
from flask import Flask,request, render_template
from flask_socketio import SocketIO


#camera
import cv2
import base64


if on_pi:
    #motor control
    import RPi.GPIO as GPIO
    import smbus2 as smbus
    import int_to_byte


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

#motor setup
if on_pi:
    PIN_I2C6_POWER_ENABLE = 17
    bus = smbus.SMBus(3)
    DEVICE_ADDRESS = 0x53
    GPIO.setmode(GPIO.BCM)
    time.sleep(0.1) #important
    GPIO.setup(PIN_I2C6_POWER_ENABLE, GPIO.OUT)
    time.sleep(0.1) #important
MOTOR_DEFAULT = 20
motorBias = 0
def set_motors(left, right, verbose=False):
    if on_pi:
        bus.write_i2c_block_data(DEVICE_ADDRESS,3,int_to_byte.int_to_byte_array(left))
        bus.write_i2c_block_data(DEVICE_ADDRESS,4,int_to_byte.int_to_byte_array(right))
    if verbose:
        print("Left:", left)
        print("Right:", right)


#camera setup
camera = cv2.VideoCapture(0)
time.sleep(0.5)
#changing these might break the camera!!
camera.set(3, 64)
camera.set(4, 64)
time.sleep(0.5)
#Fine-tune this
FPS = 15
canRecord = False


#data collection
#path names
datasetPath = os.path.join(pathlib.Path(__file__).parent.resolve(), "datasets/")
#clear all the tubs (for debugging only)
#for oldTub in os.listdir(datasetPath):
#    shutil.rmtree(os.path.join(datasetPath, oldTub))
if os.listdir(datasetPath):
    max = 1
    for oldTub in os.listdir(datasetPath):
        oldTubId = int(oldTub[3:])
        if oldTubId > max:
            max = oldTubId
    tubName = "tub" + str(max + 1)
else:
    tubName = "tub1"
tubPath = os.path.join(datasetPath, tubName)
imagesPath = os.path.join(tubPath, "Images/")
biasFilePath = os.path.join(tubPath, "bias.txt")
biasList = []

#create the directories
os.mkdir(tubPath)
os.mkdir(imagesPath)
#open bias file and allow writing data. If file already exists it is overridden.
biasFile = open(biasFilePath, "w")


#SOCKETIO
@socketio.on('startRecording')
def record():
    global canRecord
    canRecord = True
    set_motors(left=MOTOR_DEFAULT, right=MOTOR_DEFAULT)
    print("Recording started")
    print("Starting motors")


@socketio.on('pauseRecording')
def stop_record():
    global canRecord
    canRecord = False
    set_motors(left=0, right=0)
    print("Recording paused")
    print("Stopping motors")


@socketio.on('recordingSystem') 
def recording_system():
    framesTaken = 0
    #get camera info and print it
    retval, frame = camera.read()
    height = frame.shape[0]
    width = frame.shape[1]
    channels = frame.shape[2]
    print("cam px height:", height)
    print("cam px width:", width)
    print("cam channels:", channels)
    while True:
        #take picture into frame
        retval, frame = camera.read()
        #crop the image
        if not on_pi:
            frame = frame[int(height/2)-32:int(height/2)+32, int(width/2)-32:int(width/2)+32]
        if on_pi:
            #flip the image horiz and vert
            frame = cv2.flip(frame, -1)

        if canRecord:
            framesTaken += 1
            #save frame
            cv2.imwrite(imagesPath + "frame" + str(framesTaken) + ".jpg", frame)
            #save current motor bias
            biasList.append(motorBias)
            #sanity checks
            print("On frame: " + str(framesTaken))
            print("BiasList elements: " + str(len(biasList)))

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
    if on_pi:
        GPIO.output(PIN_I2C6_POWER_ENABLE, GPIO.HIGH) 
    

@socketio.on('motorsOff')
def motors_off():
    print("motor off received") 
    if on_pi:
        GPIO.output(PIN_I2C6_POWER_ENABLE, GPIO.LOW)


@socketio.on('motorBias')
def set_motor_bias(data):
    global motorBias
    motorBias = data
    leftMotor = MOTOR_DEFAULT + motorBias
    rightMotor = MOTOR_DEFAULT - motorBias
    set_motors(left=leftMotor, right=rightMotor)
    

#FLASK SERVING
@app.route('/')
def home():
    return render_template('index.html')


#RUN APP
if __name__ == '__main__':
    print("Ready for clients.")
    socketio.run(app, host='0.0.0.0', port=5000)
    

#CLEAN UP
print("Closing program")
#add biases to biasFile and close the file
for e in biasList:
    biasFile.write(str(e) + "\n")
biasFile.close()
if on_pi:
    GPIO.cleanup()
#sanity check
print("recorded motor values: " + os.popen("wc -l < " + biasFilePath).read().strip())
print("recorded images: " + os.popen("ls " + imagesPath + " | wc -l").read().strip())