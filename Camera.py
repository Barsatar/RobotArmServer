import cv2

from time import sleep

class Camera:
    def __init__(self):
        self.__camera__ = None
    
    
    def createImage(self):
        self.__camera__ = cv2.VideoCapture(0)
        delay = 20
        i = 0
        
        while i != delay:
            ret, frame = self.__camera__.read()
            i += 1
            
        cv2.imwrite('bufferTVS/image.png', frame)
        
        self.__camera__.release()