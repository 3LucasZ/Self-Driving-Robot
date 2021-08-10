import tflite_runtime.interpreter as tflite
import numpy as np
import Modules.utils as utils
import os

class TfliteModel():
    def __init__(self, modelName, getDetails=False):
        modelPath = os.path.join(utils.get_root(), 'Tflite_Models', modelName)
        #interpreter
        self.interpreter = tflite.Interpreter(model_path=modelPath)
        self.interpreter.allocate_tensors()
        #get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        if getDetails:
            print(self.input_details)
            print(self.output_details)

    def predict(self, image):
        processedImage = np.float32((image / 255).reshape(1, 64, 64, 3))
        self.interpreter.set_tensor(self.input_details[0]['index'], processedImage)
        self.interpreter.invoke()
        tflite_results = self.interpreter.get_tensor(self.output_details[0]['index'])
        prediction = int(np.ndarray.item(tflite_results))
        return prediction