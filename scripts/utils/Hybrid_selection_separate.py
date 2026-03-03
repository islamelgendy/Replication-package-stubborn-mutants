import sys
import copy

from utils.CSVLoader import CSVLoader, getMatrixCoverage
from utils.Coverage_selection import getMaxCoverage
from utils.Diversity_selection import getMaxOfMins
from utils.utilsIO import filterFiles

class SeparateHybridSelection:

    def __init__(self, coverageCSV: CSVLoader, simlarityCSV: CSVLoader, foundation = None, selectionPool = None):
        self.listCols, self.covmatrix = deepcopyCovMatrix(coverageCSV)
        self.T, self.divmatrix = deepcopyDivMatrix(simlarityCSV)
        self.coverage = 0
        
        self.matrixP = dict()
        self.P = list()                     # The new permutation

        # if there is a selection pool passed, select from it
        self.selectionPool = selectionPool.copy()

        # if there is a foundation passed, build over it
        if foundation:
            for key in foundation:
                self.matrixP[key] = self.covmatrix.pop(key)

                # Add it to the permutation
                self.P.append(key)

                # Remove it from the diversity matrix
                # self.divmatrix.pop(key)
                # self.T.remove(key)     

                # Filter the selectionPool (if any) by removing the tests already in the foundation
                if self.selectionPool and key in self.selectionPool:
                    self.selectionPool.remove(key) 
                
            self.coverage = getMatrixCoverage(self.matrixP, self.listCols, False)
        
        # Calculate the min dictionary
        self.minValues = getMinValues(self.divmatrix, self.T)

        # Flag to select based on coverage (True) or diversity (False)
        self.flag = True

        # Flag to indicate if this is the first time to select based on diversity
        self.firstSelectionDiv = True

    def makeOneSelection(self):
        # If flag is True, selection is based on coverage
        if self.flag:
            method = self.makeOneSelectionCoverage()
            self.flag = False
        else:
            method = self.makeOneSelectionDiversity()
            self.flag = True
        
        self.coverage = getMatrixCoverage(self.matrixP, self.listCols, False)

        return method

    def prioritize(self):
        while len(self.divmatrix) > 0:
            self.makeOneSelectionDiversity()
    
    def makeOneSelectionDiversity(self):
        # If P is empty, then this is the first step
        if self.firstSelectionDiv:
            found, method = self.__firstSelection()
            if not found:
                self.makeOneSelectionDiversity()
            
            self.firstSelectionDiv = False
            return method
        else:
            found, method = self.__anotherSelection()
            if not found:
                self.makeOneSelectionDiversity()
            
            return method
        
    
    def __firstSelection(self):
        maxKey = getMaxOfMins(self.minValues, self.selectionPool)
        
        # self.minValuesP[maxKey] = self.minValues[maxKey]
        
        self.divmatrix.pop(maxKey)
        self.T.remove(maxKey)

        if maxKey in self.matrixP.keys():
            # Calculate the min dictionary
            self.minValues = getMinValues(self.divmatrix, self.T)
            return False, maxKey
        self.P.append(maxKey)

        if maxKey in self.covmatrix.keys():
           self.matrixP[maxKey] = self.covmatrix.pop(maxKey)

        if self.selectionPool:
            self.selectionPool.remove(maxKey)

        return True, maxKey
    
    def __anotherSelection(self):
        # Calculate the min dictionary
        self.minValues = getMinValuesForP(self.divmatrix, self.T, self.P)

        maxKey = getMaxOfMins(self.minValues, self.selectionPool)
        self.divmatrix.pop(maxKey)
        self.T.remove(maxKey) 
        
        if maxKey in self.matrixP.keys():
            return False, maxKey
        self.P.append(maxKey)
        # self.minValuesP[maxKey] = self.minValues[maxKey]
        
        if maxKey in self.covmatrix.keys():
           self.matrixP[maxKey] = self.covmatrix.pop(maxKey)

        if self.selectionPool:
            self.selectionPool.remove(maxKey)

        return True, maxKey

    def makeOneSelectionCoverage(self):
        
        # if there is a selection pool passed, select from it
        if self.selectionPool:
            # Pick the max coverage record from the selection pool
            methodName = getMaxCoverage(self.covmatrix, self.listCols, self.selectionPool)
            self.selectionPool.remove(methodName)
        else:
            # Pick the max coverage record from the original matrix
            methodName = getMaxCoverage(self.covmatrix, self.listCols)
        self.matrixP[methodName] = self.covmatrix.pop(methodName)

        # Add it to the permutation
        self.P.append(methodName)

        # # Remove it from the diversity matrix
        # self.divmatrix.pop(methodName)
        # self.T.remove(methodName)

        return methodName
        
    
# def getMaxOfMins(minValues:dict):
#     maxKey = ''
#     maxV = -1

#     for key in minValues.keys():
#         curKey, curValue = minValues[key]
#         if float(curValue) > maxV:
#             maxV = float(curValue)
#             maxKey = key

#     return maxKey

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

def deepcopyDivMatrix(simlarityCSV: CSVLoader):
    listMethods = copy.deepcopy(simlarityCSV.listMethods)
    matrix = dict()

    for mtd in listMethods:
        matrix[mtd] = copy.deepcopy(simlarityCSV.matrix[mtd])

    return listMethods, matrix

def deepcopyCovMatrix(coverageCSV: CSVLoader):
    listCols = copy.deepcopy(coverageCSV.listCols)
    matrix = dict()

    for mtd in coverageCSV.listMethods:
        matrix[mtd] = copy.deepcopy(coverageCSV.matrix[mtd])

    return listCols, matrix

def getMinValues(simMat, methods):
    minValues = dict()

    # simMat = simlarityCSV.matrix
    # methods = simlarityCSV.listMethods
    # go through the similarity matrix row by row and find the min value of each row
    for mtd in methods:
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

