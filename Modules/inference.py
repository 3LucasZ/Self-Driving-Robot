import tflite_runtime.interpreter as tflite
import numpy as np
import Modules.utils as utils
import os

class TfliteModel():
    def __init__(self, modelName, mode, getDetails=False):
        modelPath = os.path.join(utils.get_root(), 'Tflite_Models', modelName)
        #interpreter
        self.interpreter = tflite.Interpreter(model_path=modelPath)
        self.interpreter.allocate_tensors()
        #get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.mode = mode
        if getDetails:
            print(self.input_details)
            print(self.output_details)

    def predict(self, image):
        #cropping?
        #frame shape should be: (1, 32, 64, 3)
        #image = image[0:32, :, :]
        processedImage = np.expand_dims(np.float32((image / 255)), axis=0)
        self.interpreter.set_tensor(self.input_details[0]['index'], processedImage)
        self.interpreter.invoke()
        tflite_results = self.interpreter.get_tensor(self.output_details[0]['index'])
        if self.mode == 'regression':
            prediction = int(np.ndarray.item(tflite_results))
        elif self.mode == 'classification':
            prediction = np.argmax(tflite_results)
        else:
            print("error")
        return prediction