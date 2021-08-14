#utils
import Modules.utils as util
config = util.get_config()
on_pi = config['ON_PI']

#IMPORTS
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
FPS = 1
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

while True:
    frame, _ = camera.take_picture()

    if mode == 'regression':
        prediction = model.predict(frame)
        print(prediction)
        motorController.set_to(left=MOTOR_DEFAULT+prediction, right=MOTOR_DEFAULT-prediction)
    elif mode == 'classification':
        prediction = model.predict(frame)
        print(prediction)
        if prediction == 0:
            motorController.left_pivot(PIVOT_SPEED)
        elif prediction == 1:
            motorController.forward(FORWARD_SPEED)
        elif prediction == 2:
            motorController.right_pivot(PIVOT_SPEED)
    else:
        print("Error")
    time.sleep(1/FPS)

motorController.stop()
