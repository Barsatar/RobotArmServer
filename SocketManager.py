from TCPSocket import TCPSocket
from UDPSocket import UDPSocket

from threading import Thread
import json

class SocketManager:
    def __init__(self, ip, port):
        self.__ip__ = ip
        self.__port__ = port
        self.__isWork__ = False
        
        self.__sendDataArrayTCPSocket__ = []
        self.__receiveDataArrayTCPSocket__ = []
        
        self.__sendDataArrayUDPSocket__ = []
        self.__receiveDataArrayUDPSocket__ = []
        
        self.__TCPSocket__ = None
        self.__UDPSocket__ = None
        
        self.__socketManagerThread__ = Thread(target = self.run)
        self.__socketManagerThread__.start()
    
    
    def run(self):
        self.__isWork__ = True
        
        self.__TCPSocket__ = TCPSocket(self.__ip__, self.__port__)
        self.__UDPSocket__ = UDPSocket(self.__ip__, self.__port__)
        
        while self.__isWork__:
            #if not self.__TCPSocket__.isWork():
                #self.__TCPSocket__ = TCPSocket(self.__ip__, self.__port__)
            
            #if not self.__UDPSocket__.isWork():
                #self.__UDPSocket__ = UDPSocket(self.__ip__, self.__port__)
            
            while len(self.__sendDataArrayTCPSocket__) > 0:
                if self.__TCPSocket__ != None:
                    self.__TCPSocket__.sendDataArrayPushBack(self.__sendDataArrayTCPSocket__.pop(0).encode('utf-8'))
            
            while True:
                if self.__TCPSocket__ != None and self.__TCPSocket__.getReceiveDataArraySize() > 0:
                    self.__receiveDataArrayTCPSocket__.append(str(self.__TCPSocket__.receiveDataArrayPopFront().decode('utf-8')))
                else:
                    break
            
            while len(self.__sendDataArrayUDPSocket__) > 0:
                if self.__UDPSocket__ != None:
                    self.__UDPSocket__.sendDataArrayPushBack(self.__sendDataArrayUDPSocket__.pop(0))
            
            while True:
                if self.__UDPSocket__ != None and self.__UDPSocket__.getReceiveDataArraySize() > 0:
                    self.__receiveDataArrayUDPSocket__.append(str(self.__UDPSocket__.receiveDataArrayPopFront().decode('utf-8')))
                else:
                    break
    
    
    def sendDataArrayPushBackTCPSocket(self, data):
        self.__sendDataArrayTCPSocket__.append(data)
    
    
    def receiveDataArrayPopFrontTCPSocket(self):
        data = ""
        
        if len(self.__receiveDataArrayTCPSocket__) > 0:
            data = self.__receiveDataArrayTCPSocket__.pop(0)
        
        return data
    
    
    def sendDataArrayPushBackUDPSocket(self, data):
        self.__sendDataArrayUDPSocket__.append(data)
    
    
    def receiveDataArrayPopFrontUDPSocket(self):
        data = ""
        
        if len(self.__receiveDataArrayUDPSocket__) > 0:
            data = self.__receiveDataArrayUDPSocket__.pop(0)
        
        return data
    
    
    def receiveDataArrayByCommandTCPSocket(self, command):
        data = ""
        
        for i in range(len(self.__receiveDataArrayTCPSocket__)):
            tmp_data = json.loads(self.__receiveDataArrayTCPSocket__[i])
            
            if tmp_data["command"] == command:
                data = self.__receiveDataArrayTCPSocket__.pop(i)
                break
        
        return data
    
    
    def getReceiveDataArraySizeTCPSocket(self):
        return len(self.__receiveDataArrayTCPSocket__)
    
    
    def getReceiveDataArraySizeUDPSocket(self):
        return len(self.__receiveDataArrayUDPSocket__)