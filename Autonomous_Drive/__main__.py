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
import Modules.inference as inference
import numpy as np


#General purpose 
import os
import time


#SETUP
#tflite model
modelName = 'ClassTrackLeftRight.tflite'
mode = 'classification'
model = inference.TfliteModel(modelName, mode)


#camera
#camera setup
camera = cam.Camera()
FPS = 8
canInference = False


#motors
motorController = motor.MotorController()
if mode == 'regression':
    MOTOR_DEFAULT = 20
    motorBias = 0
elif mode == 'classification':
    FORWARD_SPEED = 20
    PIVOT_SPEED = 20
else:
    print("Error")


#app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)
HOST = config['SERVER']['HOST']
PORT = config['SERVER']['PORT']


#WEBSOCKET COMMUNICATIONS
@socketio.on('connect')
def connect():
    motorController.on()
    print('A client connected.')


@socketio.on('disconnect')
def disconnect():
    print('A client disconnected.')
    stop_inference()


@socketio.on('startInference')
def start_inference():
    print("Starting inference")
    print("Motors on")
    motorController.on()
    global canInference
    canInference = True


@socketio.on('stopInference')
def stop_inference():
    print("Inference stopped")
    print("Motors stopped")
    motorController.stop()
    global canInference
    canInference = False


livestreamRunning = False
@socketio.on('livestreamSystem')
def livestream_system():
    global livestreamRunning
    if not livestreamRunning :
        livestreamRunning = True
        while True:
            frame, encodedFrame = camera.take_picture()
            if canInference: 
                if mode == 'regression':
                    prediction = model.predict(frame)
                    motorController.set_to(left=MOTOR_DEFAULT+prediction, right=MOTOR_DEFAULT-prediction)
                elif mode == 'classification':
                    prediction = model.predict(frame)
                    if prediction == 1:
                        motorController.left_pivot(PIVOT_SPEED)
                    elif prediction == 2:
                        motorController.forward(FORWARD_SPEED)
                    elif prediction == 3:
                        motorController.right_pivot(PIVOT_SPEED)
                else:
                    print("Error")
                #socketio.emit("prediction", prediction)
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