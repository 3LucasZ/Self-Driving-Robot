#utils
import Modules.utils as util
config = util.get_config()
on_pi = config['ON_PI']

#IMPORTS
#networking
from flask import Flask,request, render_template
from flask_socketio import SocketIO, emit


#camera
import Modules.camera as cam


#motors
import Modules.motor_controller as motor


#ML model inference
import tflite_runtime.interpreter as tflite
import numpy as np


#General purpose 
import os
import time


#SETUP
#paths
currDir = os.path.dirname(os.path.abspath(__file__))
modelPath = os.path.join(currDir, "model17.tflite")


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
HOST = config['SERVER']['HOST']
PORT = config['SERVER']['PORT']


#camera
#camera setup
camera = cam.Camera()
FPS = 8
canInference = False


#motors
motorController = motor.MotorController()
MOTOR_DEFAULT = 20
motorBias = 0


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
    motorController.on()
    canInference = True


@socketio.on('stopInference')
def stop_inference():
    print("Inference stopped")
    print("Motor stopped")
    global canInference
    motorController.off()
    canInference = False


@socketio.on('livestreamSystem')
def livestream_system():
    while True:
        frame, encodedFrame = camera.take_picture()
        if canInference:
            #INFERENCE
            to_predict = np.float32((frame / 255).reshape(1, 64, 64, 3))
            interpreter.set_tensor(input_details[0]['index'], to_predict)
            interpreter.invoke()
            tflite_results = interpreter.get_tensor(output_details[0]['index'])
            motorBias = int(np.ndarray.item(tflite_results))
            #print("bias:", motorBias)
            motorController.set_to(left=MOTOR_DEFAULT+motorBias, right=MOTOR_DEFAULT-motorBias)
            emit("bias", motorBias)
        socketio.emit('jpg_string', encodedFrame)
        #async sleep
        socketio.sleep(1/FPS)    


#FLASK HTTP
@app.route('/')
def home():
    return render_template('index.html')


#RUN APP
if __name__ == '__main__':
    print("Ready for clients.")
    print('Running on <SERVER_IP>:' + str(PORT))
    socketio.run(app, host=HOST, port=PORT)
    
    
#CLEAN UP
if on_pi:
    GPIO.cleanup()
print("Closing program")