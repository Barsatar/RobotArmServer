from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from time import sleep

class UDPSocket:
    def __init__(self, ip, port):
        self.__ip__ = ip
        self.__port__ = port
        self.__isWork__ = False
        
        self.__socket__ = None
        self.__address__ = None
        
        self.__socketThread__ = None
        self.__sendDataListenerThread__ = None
        self.__receiveDataListenerThread__ = None
        
        self.__sendDataArray__ = []
        self.__receivedDataArray__ = []

        self.createSocketThread()
    
    
    def run(self):
        self.__isWork__ = True
        
        self.createSocket()
        
        self.createSendDataListenerThread()
        self.createReceiveDataListenerThread()
    
    
    def createSocket(self):
        try:
            self.__socket__ = socket(AF_INET, SOCK_DGRAM)
            self.__socket__.bind((self.__ip__, self.__port__))
        except Exception as e:
            self.__isWork__ = False
    
    
    def closeSocket(self):
        try:
            self.__socket__.close()
        except Exception as e:
            self.__isWork__ = False
    
    
    def createSocketThread(self):
        self.__socketThread__ = Thread(target = self.run)
        self.__socketThread__.start()
    
    
    def createSendDataListenerThread(self):
        self.__sendDataListenerThread__ = Thread(target = self.sendDataListener)
        self.__sendDataListenerThread__.start()
    
    
    def createReceiveDataListenerThread(self):
        self.__receiveDataListenerThread__ = Thread(target = self.receiveDataListener)
        self.__receiveDataListenerThread__.start()
    
    
    def sendDataListener(self):
        while self.__isWork__:
            if len(self.__sendDataArray__) > 0:
                self.sendData(self.__sendDataArray__.pop(0))
                
                sleep(0.1)
    
    
    def receiveDataListener(self):
        while self.__isWork__:
            data, address = self.receiveData()
            
            if data != None and len(data) > 0:
                self.__receivedDataArray__.append(data)
                self.__address__ = address
    
    
    def sendData(self, data):
        try:
            self.__socket__.sendto(data, self.__address__)
            
            print("RAR_UDPSocket_SendData: OK (" + str(len(data)) + ")")
        except Exception as e:
            self.__isWork__ = False
            self.closeSocket()
    
    
    def receiveData(self):
        data = None
        address = None
        bufferSize = 1024
        
        try:
            bytesAddressPair = self.__socket__.recvfrom(bufferSize)
            data = bytesAddressPair[0]
            address = bytesAddressPair[1]
            
            print("RAR_UDPSocket_ReceiveData: OK (" + str(data.decode("utf-8")) + ")")
        except Exception as e:
            self.__isWork__ = False
            self.closeSocket()
            
        return data, address
    
    
    def isWork(self):
        return self.__isWork__


    def sendDataArrayPushBack(self, data):
        self.__sendDataArray__.append(data)
    
    
    def receiveDataArrayPopFront(self):
        data = None
        
        if len(self.__receivedDataArray__) > 0:
            data = self.__receivedDataArray__.pop(0)
        
        return data
    
    
    def getReceiveDataArraySize(self):
        return len(self.__receivedDataArray__)