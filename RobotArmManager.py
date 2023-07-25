from SocketManager import SocketManager
from Camera import Camera
from Module import Module
from NNC import NNC
from Detection import Detection

from math import atan2, pi
from PIL import Image
from time import sleep
from threading import Thread
import pandas as pd
import json
import os
import math

class RobotArmManager:
    def __init__(self):
        self.__ip__ = "192.168.43.154"
        self.__port__ = 7000
        self.__isWork__ = False
        self.__camera__ = Camera()
        self.__detection__ = Detection()
        self.__nnc__ = NNC()
        self.__socketManager__ = SocketManager(self.__ip__, self.__port__)
        self.__modules__ = []
        self.__classScripts__ = {}
        
        with open("modules_configuration.json", "r", encoding = "utf-8") as config:
            data = json.load(config)
            
            for index in data:
                module = Module(
                    data[index]["id"],
                    data[index]["type"],
                    data[index]["min_angle"],
                    data[index]["max_angle"],
                    data[index]["min_speed_level"],
                    data[index]["max_speed_level"],
                    data[index]["start_angle"],
                    data[index]["start_speed_level"],
                    data[index]["pul_pin"],
                    data[index]["dir_pin"],
                    data[index]["ena_pin"],
                    data[index]["step"],
                    data[index]["driver_multiplier"],
                    data[index]["reducer_multiplier"],
                    data[index]["correction_multiplier"],
                    data[index]["direction_multiplier"],
                    data[index]["priority"],
                    data[index]["min_delay"],
                    data[index]["max_delay"]
                    )
                self.__modules__.append(module)
            
        self.__robotArmManagerThread__ = Thread(target = self.run)
        self.__robotArmManagerThread__.start()
    
    def run(self):
        print("Start RobotArmManager.")
        self.__isWork__ = True
        
        while self.__isWork__:
            if self.__socketManager__ != None and self.__socketManager__.getReceiveDataArraySizeTCPSocket() > 0:
                data = json.loads(self.__socketManager__.receiveDataArrayPopFrontTCPSocket())
                
                if data["command_type"] == "request" and data["command"] == "get_modules_configuration":
                    self.getModulesConfiguration()
                
                if data["command_type"] == "request" and data["command"] == "get_current_modules_configuration":
                    self.getCurrentModulesConfiguration()
                
                if data["command_type"] == "control" and data["command"] == "manual_control":
                    self.manualControl(data["data"])
                    
                    command = "{\"socket\":\"tcp\", \"command_type\":\"answer\", \"command\":\"control_command\", \"data\":{}}"
                    self.__socketManager__.sendDataArrayPushBackTCPSocket(command)
                
                if data["command_type"] == "control" and data["command"] == "neural_network_control":
                    self.neuralNetworkControl(data["data"])
                    
                    command = "{\"socket\":\"tcp\", \"command_type\":\"answer\", \"command\":\"control_command\", \"data\":{}}"
                    self.__socketManager__.sendDataArrayPushBackTCPSocket(command)
                
                if data["command_type"] == "control" and data["command"] == "script":
                    self.scriptControl(data["data"])
                    
                    command = "{\"socket\":\"tcp\", \"command_type\":\"answer\", \"command\":\"control_command\", \"data\":{}}"
                    self.__socketManager__.sendDataArrayPushBackTCPSocket(command)
                
                if data["command_type"] == "control" and data["command"] == "sort_objects":
                    self.sortObjects(data["data"])
                    
                    command = "{\"socket\":\"tcp\", \"command_type\":\"answer\", \"command\":\"control_command\", \"data\":{}}"
                    self.__socketManager__.sendDataArrayPushBackTCPSocket(command)
                
                if data["command_type"] == "control" and data["command"] == "start_position":
                    self.startPosition()
                    
                    command = "{\"socket\":\"tcp\", \"command_type\":\"answer\", \"command\":\"control_command\", \"data\":{}}"
                    self.__socketManager__.sendDataArrayPushBackTCPSocket(command)
                
                if data["command_type"] == "detection" and data["command"] == "detect_objects":
                    self.detectObjects(data["data"])
    
    
    def getModulesConfiguration(self):
            modulesConfiguration = ""
            
            for module in self.__modules__:
                modulesConfiguration += module.getConfiguration() + ", "

            command = "{\"socket\":\"tcp\", \"command_type\":\"answer\", \"command\":\"get_modules_configuration\", \"data\": {" + modulesConfiguration[:-2] + "}}"
            
            self.__socketManager__.sendDataArrayPushBackTCPSocket(command)
    
    
    def getCurrentModulesConfiguration(self):
        currentModulesConfiguration = ""
            
        for module in self.__modules__:
            currentModulesConfiguration += module.getCurrentConfiguration() + ", "        
        
        command = "{\"socket\":\"tcp\", \"command_type\":\"answer\", \"command\":\"get_current_modules_configuration\", \"data\":{" + currentModulesConfiguration[:-2] + "}}"
        
        self.__socketManager__.sendDataArrayPushBackTCPSocket(command)
    
    
    def startPosition(self):
        for module in sorted(self.__modules__, key = lambda x: x.__priority__):
            module.rotate(module.__startAngle__, module.__startSpeedLevel__)
        
        for module in reversed(self.__modules__):
            module.turnOff()
    
    
    def manualControl(self, data):  
        for index in data:
            for module in sorted(self.__modules__, key = lambda x: x.__priority__):
                if data[index]["id"] == module.__id__:
                    module.rotate(data[index]["angle"], data[index]["speed_level"])   
    
    
    def neuralNetworkControl(self, data):
        inputData = [{"x": float(data["x"]), "y": float(data["y"]), "z": float(data["z"]), "theta": float(data["theta"]), "psi": float(data["psi"]), "phi": float(data["phi"])}]
        moduleData = self.__nnc__.calculate(inputData)
        
        for module in sorted(self.__modules__, key = lambda x: x.__priority__):
            for moduleId in moduleData[0]:
                if module.__id__ == moduleId:
                    module.rotate(moduleData[0][moduleId], module.__speedLevel__)
                    
    
    def scriptControl(self, data):
        for index in data:
            if data[index]["command"] == "manual_control":
                self.manualControl(data[index]["data"])
            
            if data[index]["command"] == "neural_network_control":
                self.neuralNetworkControl(data[index]["data"])
    
    
    def sortObjects(self, data):
        for className in data:
            self.__classScripts__[className] = data[className]
        
        width, height = Image.open("bufferTVS/image.png").size
        objectsDataCSV = pd.read_csv("bufferTVS/image.csv")
        objectsData = []
        
        coordinateSystemConfiguration = None
        
        with open("coordinate_system_configuration.json", "r", encoding = "utf-8") as config:
            coordinateSystemConfiguration = json.load(config)
        
        for index, row in objectsDataCSV.iterrows():
            imageX = row["min_x"] + (row["max_x"] - row["min_x"]) / 2
            imageY = row["min_y"] + (row["max_y"] - row["min_y"]) / 2
            
            x = coordinateSystemConfiguration["offset_x"] + (height - imageY) * coordinateSystemConfiguration["factor_x"]
            y = coordinateSystemConfiguration["offset_y"] + (imageX - width / 2) * coordinateSystemConfiguration["factor_y"]
            phi = -90 + atan2(y, x) * 180 / pi
            
            objectsData.append({"class": row["class"], "x": x, "y": y, "z": 5, "theta": 90, "psi": 0, "phi": phi})
        
        modulesData = self.__nnc__.calculate(objectsData)
        
        preparationModulesConfig1 = []
        
        with open("preparation_configuration_1.json", "r", encoding = "utf-8") as config:
            data = json.load(config)
            
            for index in data:
                for module in self.__modules__:
                    if data[index]["id"] == module.__id__:
                        preparationModulesConfig1.append({"module": module, "angle": data[index]["angle"], "speed_level": data[index]["speed_level"]})
        
        preparationModulesConfig2 = []
        
        with open("preparation_configuration_2.json", "r", encoding = "utf-8") as config:
            data = json.load(config)
            
            for index in data:
                for module in self.__modules__:
                    if data[index]["id"] == module.__id__:
                        preparationModulesConfig2.append({"module": module, "angle": data[index]["angle"], "speed_level": data[index]["speed_level"]})
        
        for i in range(len(objectsData)):
            objectClass = objectsData[i]["class"]
            objectModulesAngle = modulesData[i]
            
            if objectClass in self.__classScripts__:
                for preparationModule in preparationModulesConfig1:
                    preparationModule["module"].rotate(preparationModule["angle"], preparationModule["speed_level"])
            
                for module in sorted(self.__modules__, key = lambda x: x.__priority__):
                    for moduleId in objectModulesAngle:
                        if module.__id__ == moduleId:
                            module.rotate(objectModulesAngle[moduleId], module.__speedLevel__)
                
                for preparationModule in preparationModulesConfig2:
                    preparationModule["module"].rotate(preparationModule["angle"], preparationModule["speed_level"])
                
                self.scriptControl(self.__classScripts__[objectClass])
    
    
    def detectObjects(self, data):
        self.__camera__.createImage()
        self.__detection__.detectObjects(data["threshold"])
        
        file = open("bufferTVS/image.png", "rb")   
        partSize = 40960
        
        file.seek(0, os.SEEK_END)  
        fileSize = file.tell()
        file.seek(0, 0)
        
        count = math.floor(fileSize / partSize)
        lastPartSize = fileSize - count * partSize
        
        if lastPartSize < partSize:
            count += 1
        
        command = "{\"socket\":\"tcp\", \"command_type\":\"answer\", \"command\":\"detect_objects\", \"data\":{\"count_of_frame_parts\":" + str(count) + ", \"last_part_size\":" + str(lastPartSize) + "}}"
        self.__socketManager__.sendDataArrayPushBackTCPSocket(command)
        
        imageData = file.read(partSize)
        
        while imageData:
            self.__socketManager__.sendDataArrayPushBackUDPSocket(imageData)
            imageData = file.read(partSize)
            
        file.close()