import tflite_runtime.interpreter as tflite
import numpy as np
import os
import cv2

#SETUP
#paths
currDir = os.path.dirname(os.path.abspath(__file__))
imagePath = os.path.join(currDir, "frame1.jpg")
modelPath = os.path.join(currDir, "model17.tflite")

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

#QUALITY CHECKS
print(imageArr.shape)

#INFERENCE
interpreter.set_tensor(input_details[0]['index'], imageArr)
interpreter.invoke()
tflite_results = interpreter.get_tensor(output_details[0]['index'])
print(tflite_results)