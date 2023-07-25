from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep

class TCPSocket:
    def __init__(self, ip, port):
        self.__ip__ = ip
        self.__port__ = port
        self.__isWork__ = False

        self.__socket__ = None
        self.__user__ = None
        self.__address__ = None

        self.__socketThread__ = None
        self.__sendDataListenerThread__ = None
        self.__receiveDataListenerThread__ = None
        self.__testConnectionThread__ = None
        
        self.__sendDataArray__ = []
        self.__receivedDataArray__ = []

        self.createSocketThread()
    
    
    def run(self):
        self.__isWork__ = True
        
        self.createSocket()
        self.createConnection()
        
        self.createSendDataListenerThread()
        self.createReceiveDataListenerThread()
        self.createTestConnectionThread()
    
    def createSocket(self):
        try:
            self.__socket__ = socket(AF_INET, SOCK_STREAM)
            self.__socket__.bind((self.__ip__, self.__port__))
            self.__socket__.listen(0)
        except Exception as e:
            self.__isWork__ = False
    
    
    def createConnection(self):
        try:
            self.__user__, self.__address__ = self.__socket__.accept()
        except Exception as e:
            self.__isWork__ = False
            self.closeSocket()
    
    
    def closeSocket(self):
        try:
            self.__socket__.close()
        except Exception as e:
            self.__isWork__ = False
    
    
    def closeConnection(self):
        try:
            self.__user__.close()
        except Exception as e:
            self.__isWork__ = False
            self.closeSocket()
    
    
    def createSocketThread(self):
        self.__socketThread__ = Thread(target = self.run)
        self.__socketThread__.start()
    
    
    def createSendDataListenerThread(self):
        self.__sendDataListenerThread__ = Thread(target = self.sendDataListener)
        self.__sendDataListenerThread__.start()
    
    
    def createReceiveDataListenerThread(self):
        self.__receiveDataListenerThread__ = Thread(target = self.receiveDataListener)
        self.__receiveDataListenerThread__.start()
    
    
    def createTestConnectionThread(self):
        self.__testConnectionThread__ = Thread(target = self.testConnection)
        self.__testConnectionThread__.start()
    
    
    def sendDataListener(self):
        while self.__isWork__:
            if len(self.__sendDataArray__) > 0:
                self.sendData(self.__sendDataArray__.pop(0))
                
                sleep(0.1)
    
    
    def receiveDataListener(self):
        while self.__isWork__:
            data = self.receiveData()
            
            if len(self.removeTestConnectionData(data.decode('utf-8'))) != 0:
                self.__receivedDataArray__.append(data)
    
    
    def testConnection(self):
        while self.__isWork__:
            self.sendData("RA_TestConnection".encode('utf-8'))

            sleep(1)

    
    def sendData(self, data):
        try:
            self.__user__.send(data)
            
            if len(self.removeTestConnectionData(data.decode('utf-8'))) != 0:
                print("RAR_TCPSocket_SendData: OK (" + str(data.decode('utf-8')) + ")")
        except Exception as e:
            self.__isWork__ = False
            self.closeConnection()
            self.closeSocket()
    
    
    def receiveData(self):
        data = None
        bufferSize = 1024
        
        try:
            data = self.__user__.recv(bufferSize)
            
            if len(self.removeTestConnectionData(data.decode("utf-8"))) != 0:
                print("RAR_TCPSocket_ReceiveData: OK (" + str(data.decode("utf-8")) + ")")
        except Exception as e:
            self.__isWork__ = False
            self.closeConnection()
            self.closeSocket()
        
        return self.removeTestConnectionData(data.decode("utf-8")).encode("utf-8")
    
    
    def removeTestConnectionData(self, data):
        return data.replace("RA_TestConnection", "")
    
    
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