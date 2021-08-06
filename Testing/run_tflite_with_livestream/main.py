#IMPORTS
#networking
from flask import Flask,request, render_template
from flask_socketio import SocketIO, emit


#livestream
import cv2
import base64


#ML model inference
import tflite_runtime.interpreter as tflite
import numpy as np


#General purpose 
import os


#SETUP
#paths
currDir = os.path.dirname(os.path.abspath(__file__))
imagePath = os.path.join(currDir, "frame1.jpg")
modelPath = os.path.join(currDir, "model1.tflite")


#image setup
image = cv2.imread(imagePath)
imageArr = np.float32(np.array(image)).reshape(1, 64, 64, 3)


#interpreter set up
interpreter = tflite.Interpreter(model_path=modelPath)
interpreter.allocate_tensors()
#get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
print(input_details)
print(output_details)


#app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)


#camera
camera = cv2.VideoCapture(0)
camera.set(3, 64)
camera.set(4, 64)
FPS = 5
canInference = False


#motors
MOTOR_DEFAULT = 50
motorBias = 0


#WEBSOCKET COMMUNICATIONS
@socketio.on('connect')
def connect():
    print('A client connected.')


@socketio.on('disconnect')
def disconnect():
    print('A client disconnected.')


@socketio.on('startInference')
def record():
    global canInference
    canInference = True
    print("Starting inference")


@socketio.on('stopInference')
def stopRecord():
    global canInference
    canInference = False
    print("Motors stopped")
    print("Inference stopped")


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
        #crop the image
        frame = frame[int(height/2)-32:int(height/2)+32, int(width/2)-32:int(width/2)+32]
        if canInference:
            #INFERENCE
            to_predict = np.float32((frame / 255).reshape(1, 64, 64, 3))
            interpreter.set_tensor(input_details[0]['index'], to_predict)
            interpreter.invoke()
            tflite_results = interpreter.get_tensor(output_details[0]['index'])
            motorBias = np.ndarray.item(tflite_results)
            emit("bias",motorBias)
            print(motorBias)
           
            
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