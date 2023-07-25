import RPi.GPIO as GPIO
import time

class StepperMotor:
    def __init__(self, pulPin, dirPin, enaPin):
        self.__pulPin__ = pulPin
        self.__dirPin__ = dirPin
        self.__enaPin__ = enaPin
        self.__isEnable_ =  False
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.__pulPin__, GPIO.OUT)
        GPIO.setup(self.__dirPin__, GPIO.OUT)
        GPIO.setup(self.__enaPin__, GPIO.OUT)
    
    
    def forwardMode(self, step, delay):
        GPIO.output(self.__dirPin__, GPIO.LOW)
        
        for i in range(step):
            GPIO.output(self.__pulPin__, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.__pulPin__, GPIO.LOW)
            time.sleep(delay)
    
    
    def reverseMode(self, step, delay):
        GPIO.output(self.__dirPin__, GPIO.HIGH)
        
        for i in range(step):
            GPIO.output(self.__pulPin__, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.__pulPin__, GPIO.LOW)
            time.sleep(delay)
    
    
    def turnOn(self):
        GPIO.output(self.__enaPin__, GPIO.HIGH)
        self.__isEnable__ = True
    
    
    def turnOff(self):
        GPIO.output(self.__enaPin__, GPIO.LOW)
        self.__isEnable__ = False
    
    
    def isEnable(self):
        return self.__isEnable__