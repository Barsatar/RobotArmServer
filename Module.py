from StepperMotor import StepperMotor
from multiprocessing import Process

class Module:
    def __init__(self, id, type, minAngle, maxAngle, minSpeedLevel, maxSpeedLevel,  startAngle, startSpeedLevel, pulPin, dirPin, enaPin, step, driverMultiplier, reducerMultiplier, correctionMultiplier, directionMultiplier, priority, minDelay, maxDelay):
        self.__id__ = id
        self.__type__ = type
        self.__minAngle__ = minAngle
        self.__maxAngle__ = maxAngle
        self.__minSpeedLevel__ = minSpeedLevel
        self.__maxSpeedLevel__ = maxSpeedLevel
        self.__startAngle__ = startAngle
        self.__startSpeedLevel__ = startSpeedLevel
        self.__angle__ = startAngle
        self.__speedLevel__ = startSpeedLevel
        self.__pulPin__ = pulPin
        self.__dirPin__ = dirPin
        self.__enaPin__ = enaPin
        self.__step__ = step
        self.__driverMultiplier__ = driverMultiplier
        self.__reducerMultiplier__ = reducerMultiplier
        self.__correctionMultiplier__ = correctionMultiplier
        self.__directionMultiplier__ = directionMultiplier
        self.__priority__ = priority
        self.__minDelay__ = minDelay
        self.__maxDelay__ = maxDelay
        
        self.__stepperMotor__ = StepperMotor(self.__pulPin__, self.__dirPin__, self.__enaPin__)
    
    
    def getConfiguration(self):
        return "\"" + str(self.__id__) + "\": {\"id\":" + str(self.__id__) + ", \"type\":\"" + str(self.__type__) + "\", \"min_angle\":" + str(self.__minAngle__) + ", \"max_angle\":" + str(self.__maxAngle__) + ", \"min_speed_level\":" + str(self.__minSpeedLevel__) + ", \"max_speed_level\":" + str(self.__maxSpeedLevel__) + "}"
    
    
    def getCurrentConfiguration(self):
        return "\"" + str(self.__id__) + "\": {\"id\":" + str(self.__id__) + ", \"angle\":" + str(round(self.__angle__)) + ", \"speed_level\":" + str(self.__speedLevel__) + "}"
    
    
    def rotate(self, angle, speedLevel):
        if angle < self.__minAngle__:
            angle = self.__minAngle__
            
        if angle > self.__maxAngle__:
            angle = self.__maxAngle__
        
        if speedLevel < self.__minSpeedLevel__:
            speedLevel = self.__minSpeedLevel__
        
        if speedLevel > self.__maxSpeedLevel__:
            speedLevel = self.__maxSpeedLevel__
        
        deltaAngle = angle - self.__angle__
        
        step = int(self.convertAngleToStep(abs(deltaAngle)))
        delay = self.convertSpeedLevelToDelay(speedLevel)
        
        if self.__type__ == "type_5":
            step = int(self.convertCompressionProcentageToStep(abs(deltaAngle)))

        self.__stepperMotor__.turnOn()
        
        rotateProcess = None
        
        if (deltaAngle * self.__directionMultiplier__ < 0):
            rotateProcess = Process(target = self.__stepperMotor__.forwardMode, args = (step, delay,))
        else:
            rotateProcess = Process(target = self.__stepperMotor__.reverseMode, args = (step, delay,))
        
        rotateProcess.start()
        rotateProcess.join()
        
        self.__angle__ = angle
        self.__speedLevel__ = speedLevel
    
    
    def turnOff(self):
        self.__stepperMotor__.turnOff()
    
    
    def convertAngleToStep(self, angle):
        return (((360 / self.__step__) * self.__driverMultiplier__ * self.__reducerMultiplier__ * (angle * 100 / 360)) / 100) * self.__correctionMultiplier__
    
    
    def convertCompressionProcentageToStep(self, compressionProcentage):
        return (((360 / self.__step__) * self.__driverMultiplier__ * self.__reducerMultiplier__) * compressionProcentage) * (self.__correctionMultiplier__ / 100)
    
    
    def convertSpeedLevelToDelay(self, speedLevel):
        return self.__maxDelay__ - (self.__maxDelay__ - self.__minDelay__) / (self.__maxSpeedLevel__ - self.__minSpeedLevel__) * speedLevel