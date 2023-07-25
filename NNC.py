import pandas as pd
from keras.models import load_model

class NNC:
    def __init__(self):
        self.__controlModelDirPath__ = "controlModel/"
        self.__minMaxValuesFilePath__ = "min_max_values.csv"
        self.__minMaxDict__ = self.getMinMaxValuesDict()
    
    
    def getMinMaxValuesDict(self):
        minMax = pd.read_csv(self.__minMaxValuesFilePath__)
        minMaxDict = {}
        
        for indexRow, row in minMax.iterrows():
            minMaxDict[row["parametr_name"]] = [row["min_value"], row["max_value"]]
        
        return minMaxDict
    
    
    def calculate(self, data):
        tmpInputData = {"x": [], "y": [], "z": [], "theta": [], "psi": [], "phi": []}
        
        for tmpData in data:
            for key in tmpInputData:
                tmpInputData[key].append(tmpData[key])
        
        inputData = pd.DataFrame(tmpInputData)
        
        for columnName in inputData.columns:
            minValue = self.__minMaxDict__[columnName][0]
            maxValue = self.__minMaxDict__[columnName][1]

            if minValue == maxValue:
                inputData = inputData.drop(columns = columnName)
            else:
                inputData[columnName] = inputData[columnName].apply(lambda value: self.normolized(value, minValue, maxValue))
        
        model = load_model(self.__controlModelDirPath__)
        
        outputDataArray = model.predict(inputData)
        
        moduleNamesArray = []
        
        for moduleName in self.__minMaxDict__.keys():
            if "module_" in moduleName:
                moduleNamesArray.append(moduleName)
        
        dataArray = []
        
        for outputData in outputDataArray:
            dataDict = {}
            
            for i in range(len(outputData)):
                moduleId = int(moduleNamesArray[i].replace("module_", "")) - 1
                minValue = self.__minMaxDict__[moduleNamesArray[i]][0]
                maxValue = self.__minMaxDict__[moduleNamesArray[i]][1]
                value = self.unnormolized(outputData[i], minValue, maxValue)
                
                dataDict[moduleId] = value
            
            dataArray.append(dataDict.copy())
            
        return dataArray
    
    
    def normolized(self, value, minValue, maxValue):
        return (value - minValue) / (maxValue - minValue)
    
    
    def unnormolized(self, value, minValue, maxValue):
        return value * (maxValue - minValue) + minValue