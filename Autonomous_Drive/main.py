on_pi = True

#IMPORTS
#networking
from flask import Flask,request, render_template
from flask_socketio import SocketIO, emit


#livestream
import cv2
import base64


if on_pi:
    #motor control
    import RPi.GPIO as GPIO
    import smbus2 as smbus
    import int_to_byte


#ML model inference
import tflite_runtime.interpreter as tflite
import numpy as np


#General purpose 
import os


#SETUP
#paths
currDir = os.path.dirname(os.path.abspath(__file__))
modelPath = os.path.join(currDir, "model1.tflite")


#interpreter
interpreter = tflite.Interpreter(model_path=modelPath)
interpreter.allocate_tensors()
#get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
#print(input_details)
#print(output_details)


#app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)


#camera
camera = cv2.VideoCapture(0)
camera.set(3, 64)
camera.set(4, 64)
FPS = 15
canInference = False


#motors
MOTOR_DEFAULT = 20
motorBias = 0
if on_pi:
    PIN_I2C6_POWER_ENABLE = 17
    bus = smbus.SMBus(1)
    DEVICE_ADDRESS = 0x53
    GPIO.setmode(GPIO.BCM)
    time.sleep(0.1) #important
    GPIO.setup(PIN_I2C6_POWER_ENABLE, GPIO.OUT)
    time.sleep(0.1) #important
def set_motors(left, right, verbose=False):
    if on_pi:
        bus.write_i2c_block_data(DEVICE_ADDRESS,3,int_to_byte.int_to_byte_array(left))
        bus.write_i2c_block_data(DEVICE_ADDRESS,4,int_to_byte.int_to_byte_array(right))
    if verbose:
        print("Left:", left)
        print("Right:", right)
def motors_on():
    print("motor on received")
    if on_pi:
        GPIO.output(PIN_I2C6_POWER_ENABLE, GPIO.HIGH)
def motors_off():
    print("motor off received") 
    if on_pi:
        GPIO.output(PIN_I2C6_POWER_ENABLE, GPIO.LOW)


#WEBSOCKET COMMUNICATIONS
@socketio.on('connect')
def connect():
    print('A client connected.')


@socketio.on('disconnect')
def disconnect():
    print('A client disconnected.')
    stop_inference()


@socketio.on('startInference')
def start_inference():
    print("Starting inference")
    global canInference
    canInference = True
    motors_on()


@socketio.on('stopInference')
def stop_inference():
    print("Inference stopped")
    print("Motor stopped")
    global canInference
    canInference = False
    motors_off()


@socketio.on('livestreamSystem')
def livestream_system():
    #print and get some camera data
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
        if not on_pi:
            #crop the image
            frame = frame[int(height/2)-32:int(height/2)+32, int(width/2)-32:int(width/2)+32]
        if on_pi:
            #flip image
            frame = cv2.flip(frame, -1)
        if canInference:
            #INFERENCE
            to_predict = np.float32((frame / 255).reshape(1, 64, 64, 3))
            interpreter.set_tensor(input_details[0]['index'], to_predict)
            interpreter.invoke()
            tflite_results = interpreter.get_tensor(output_details[0]['index'])
            motorBias = int(np.ndarray.item(tflite_results))
            #print("bias:", motorBias)
            set_motors(left=MOTOR_DEFAULT+motorBias, right=MOTOR_DEFAULT-motorBias)
            emit("bias", motorBias)
            
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


#FLASK HTTP
@app.route('/')
def home():
    return render_template('index.html')


#RUN APP
if __name__ == '__main__':
    print("Ready for clients.")
    socketio.run(app, host='0.0.0.0', port=5000)
    
    
#CLEAN UP
print("Closing program")