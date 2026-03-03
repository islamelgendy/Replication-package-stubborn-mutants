import sys
import copy

from utils.CSVLoader import CSVLoader
from utils.utilsIO import filterFiles

class DiversitySelection:

    def __init__(self, simlarityCSV: CSVLoader, foundation = None, selectionPool = None):
        self.T, self.matrix = deepcopyMatrix(simlarityCSV)
        
        self.matrixP = dict()
        self.P = list()                     # The new permutation

        # Calculate the min dictionary
        self.minValues = getMinValues(self.matrix, self.T)

        # if there is a selection pool passed, select from it
        if selectionPool:
            self.selectionPool = selectionPool.copy()
        else:
            self.selectionPool = None

        # if there is a foundation passed, build over it
        if foundation:
            for key in foundation:
                self.matrixP[key] = self.matrix.pop(key)   
                self.P.append(key)
                self.T.remove(key)  
                # Filter the selectionPool (if any) by removing the tests already in the foundation
                if self.selectionPool and key in self.selectionPool:
                    self.selectionPool.remove(key)   
                
            # self.coverage = getMatrixCoverage(self.matrixP, self.listCols, False)

    def prioritize(self):
        while len(self.matrix) > 0:
            self.makeOneSelection()
    
    def makeOneSelection(self):
        # If P is empty, then this is the first step
        if len(self.P) == 0:
            method = self.__firstSelection()
        else:
            method = self.__anotherSelection()

        return method
        
    
    def __firstSelection(self):
        maxKey = getMaxOfMins(self.minValues, self.selectionPool)
        self.P.append(maxKey)
        # self.minValuesP[maxKey] = self.minValues[maxKey]
        
        self.matrixP[maxKey] = copy.deepcopy( self.matrix[maxKey] )
        self.matrix.pop(maxKey)
        self.T.remove(maxKey)
        
        if self.selectionPool:
            self.selectionPool.remove(maxKey)
        
        return maxKey
    
    def __anotherSelection(self):
        # Calculate the min dictionary
        self.minValues = getMinValuesForP(self.matrix, self.T, self.P)

        maxKey = getMaxOfMins(self.minValues, self.selectionPool)
        self.P.append(maxKey)
        # self.minValuesP[maxKey] = self.minValues[maxKey]
        
        self.matrixP[maxKey] = copy.deepcopy( self.matrix[maxKey] )
        self.matrix.pop(maxKey)
        self.T.remove(maxKey)  

        if self.selectionPool:
            self.selectionPool.remove(maxKey)  

        return maxKey  
    
def getMaxOfMins(minValues:dict, selectionPool:set):
    maxKey = ''
    maxV = -1

    if selectionPool:
        for key in selectionPool:
            curKey, curValue = minValues[key]
            if float(curValue) > maxV:
                maxV = float(curValue)
                maxKey = key
    else:
        for key in minValues.keys():
            curKey, curValue = minValues[key]
            if float(curValue) > maxV:
                maxV = float(curValue)
                maxKey = key

    return maxKey

def getMinOfMins(minValues:dict):
    minKey = ''
    minV = sys.maxsize

    for key in minValues.keys():
        curKey, curValue = minValues[key]
        if float(curValue) < minV:
            minV = float(curValue)
            minKey = key

    return minKey

def getMaxNotInP(record:dict, listP:list):
    maxKey = ''
    maxV = -1

    for key in record.keys():
        curValue = record[key]
        if float(curValue) > maxV and not key in listP:
            maxV = float(curValue)
            maxKey = key

    return maxKey

def deepcopyMatrix(simlarityCSV: CSVLoader):
    listMethods = copy.deepcopy(simlarityCSV.listMethods)
    matrix = dict()

    for mtd in listMethods:
        matrix[mtd] = copy.deepcopy(simlarityCSV.matrix[mtd])

    return listMethods, matrix

def getMinValues(simMat, methods):
    minValues = dict()

    # simMat = simlarityCSV.matrix
    # methods = simlarityCSV.listMethods
    # go through the similarity matrix row by row and find the min value of each row
    for mtd in methods:
        if not mtd in simMat:
            continue
        curRecord = simMat[mtd]
        # Get the minmum value of the current record
        minKey = findMinValue(mtd, curRecord)
        # minKey = min(curRecord, key=curRecord.get)
        minValues[mtd] = (minKey, float(curRecord[minKey]))

    return minValues

def getMinValuesForP(simMat, T, P):
    minValues = dict()
    tmpMatrix = dict()

    #Loop through T
    for ti in T:
        if not ti in simMat:
            continue
        tmpMatrix[ti] = dict()
        curRec = simMat[ti]
        # Loop through P
        for pi in P:
            tmpMatrix[ti][pi] = curRec[pi]

    minValues = getMinValues(tmpMatrix, T)
    return minValues

# Get the min value, but no with the same key as the method name (Don't get 0 the value of sim to itself)
def findMinValue(mtd, curRecord:dict):
    minKey = ''
    min = sys.maxsize

    for key in curRecord.keys():
        if minKey == '': # Only in the first instance
            minKey = key
        curValue = float(curRecord[key])
        if key != mtd and curValue < min:
            min = curValue
            minKey = key

    return minKey
    
# project = "time"
# id = "3"
# similarityFolder = "../resources/similarity/"
# similarityFolder = "D:\\Work\\PhD\\DBT-workbench\\resources\\similarity\\"

# # Load the similarity matrix
# try:
#     similarityFile = filterFiles(similarityFolder, project + '.' + id + 'f', 'textSimilarity.csv')[0]
#     similarityFile = similarityFolder + 'LedruCar.csv'
#     simlarityCSV = CSVLoader(similarityFile)

#     obj = DiversitySelection(simlarityCSV)

#     obj.prioritize()
#     print(obj.P)
#     # obj.makeOneSelection()
#     # obj.makeOneSelection()
#     # obj.makeOneSelection()
#     # obj.makeOneSelection()
# except:
#     print('Similarity matrix can NOT be loaded')

