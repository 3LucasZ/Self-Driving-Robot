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


#General purpose 
import os
import time


#SETUP


#tflite model
modelName = 'model17.tflite'
model = inference.TfliteModel(modelName)


#camera
#camera setup
camera = cam.Camera()
FPS = 8
canInference = False


#motors
motorController = motor.MotorController()
MOTOR_DEFAULT = 20
motorBias = 0


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


@socketio.on('livestreamSystem')
def livestream_system():
    while True:
        frame, encodedFrame = camera.take_picture()
        if canInference:
            motorBias = model.predict(frame)
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