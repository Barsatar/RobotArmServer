import os
import cv2
import numpy as np
import pandas as pd
import sys
import glob
import importlib.util
import tensorflow as tf
#from tflite_runtime.interpreter import Interpreter

class Detection:
    def __init__(self):
        self.__modelName__ = "detectionModel"
        self.__graphName__ = "detect.tflite"
        self.__labelmapName__ = "labelmap.txt"
        self.__imageName__ = "bufferTVS/image.png"
        self.__resultDirName__ = "bufferTVS/"
        self.__threshold__ = 0.5
        
    
    def detectObjects(self, threshold):
        self.__threshold__ = threshold
        cwdPath = os.getcwd()   
        pathToImages = os.path.join(cwdPath, self.__imageName__)
        images = glob.glob(pathToImages)
        
        pathToCKPT = os.path.join(cwdPath, self.__modelName__, self.__graphName__)
        pathToLabels = os.path.join(cwdPath, self.__modelName__, self.__labelmapName__)
        
        with open(pathToLabels, "r") as f:
            labels = []
            
            for line in f.readlines():
                labels.append(line.strip())
        
        if labels[0] == "???":
            del(labels[0])
        
        interpreter = tf.lite.Interpreter(model_path = pathToCKPT)
        interpreter.allocate_tensors()
        
        inputDetails = interpreter.get_input_details()
        outputDetails = interpreter.get_output_details()
        height = inputDetails[0]["shape"][1]
        width = inputDetails[0]["shape"][2]
        floatingModel = (inputDetails[0]["dtype"] == np.float32)
        inputMean = 127.5
        inputStd = 127.5
        outname = outputDetails[0]['name']
        
        if ("StatefulPartitionedCall" in outname):
            boxesIdx, classesIdx, scoresIdx = 1, 3, 0
        else:
            boxesIdx, classesIdx, scoresIdx = 0, 1, 2
        
        for imagePath in images:
            image = cv2.imread(imagePath)
            imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            imageHeight, imageWidth, _ = image.shape 
            imageResized = cv2.resize(imageRGB, (width, height))
            inputData = np.expand_dims(imageResized, axis = 0)
            
            if floatingModel:
                inputData = (np.float32(inputData) - inputMean) / inputStd
            
            interpreter.set_tensor(inputDetails[0]["index"], inputData)
            interpreter.invoke()
            
            boxes = interpreter.get_tensor(outputDetails[boxesIdx]["index"])[0]
            classes = interpreter.get_tensor(outputDetails[classesIdx]["index"])[0]
            scores = interpreter.get_tensor(outputDetails[scoresIdx]["index"])[0]
            
            detections = []
            
            for i in range(len(scores)):
                if ((scores[i] > self.__threshold__) and (scores[i] <= 1.0)):
                    yMin = int(max(1,(boxes[i][0] * imageHeight)))
                    xMin = int(max(1,(boxes[i][1] * imageWidth)))
                    yMax = int(min(imageHeight,(boxes[i][2] * imageHeight)))
                    xMax = int(min(imageWidth,(boxes[i][3] * imageWidth)))

                    cv2.rectangle(image, (xMin, yMin), (xMax, yMax), (10, 255, 0), 2)

                    objectName = labels[int(classes[i])]
                    label = '%s: %d%%' % (objectName, int(scores[i] * 100))
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
                    labelYMin = max(yMin, labelSize[1] + 10)

                    cv2.rectangle(image, (xMin, labelYMin - labelSize[1] - 10), (xMin + labelSize[0], labelYMin + baseLine - 10), (255, 255, 255), cv2.FILLED)
                    cv2.putText(image, label, (xMin, labelYMin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                    detections.append([objectName, scores[i], xMin, yMin, xMax, yMax])

                imageFileName = os.path.basename(imagePath)
                imageSavePath = os.path.join(cwdPath, self.__resultDirName__, imageFileName)

                baseFileName, ext = os.path.splitext(imageFileName)
                csvResultFileName = baseFileName + ".csv"
                csvSavePath = os.path.join(cwdPath, self.__resultDirName__, csvResultFileName)

                cv2.imwrite(imageSavePath, image)
                
                outputData = {"class": [], "accuracy": [], "min_x": [], "min_y": [], "max_x": [], "max_y": []}
                
                for detection in detections:
                    outputData["class"].append(detection[0])
                    outputData["accuracy"].append(detection[1])
                    outputData["min_x"].append(detection[2])
                    outputData["min_y"].append(detection[3])
                    outputData["max_x"].append(detection[4])
                    outputData["max_y"].append(detection[5])
                
                pd.DataFrame(outputData).to_csv(csvSavePath, index = None)
