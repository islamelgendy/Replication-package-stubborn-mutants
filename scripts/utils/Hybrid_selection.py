import sys
import copy

from utils.CSVLoader import CSVLoader, getCoverage, getMatrixCoverage
from utils.Coverage_selection import findCoverageForRecord
from utils.Diversity_selection import getMaxOfMins
from utils.utilsIO import filterFiles

class HybridSelection:

    def __init__(self, coverageCSV: CSVLoader, simlarityCSV: CSVLoader, maxCov, foundation = None, selectionPool = None, branch = False):
        self.listCols, self.covmatrix = deepcopyCovMatrix(coverageCSV)
        self.T, self.divmatrix = deepcopyDivMatrix(simlarityCSV)
        self.coverage = 0
        self.maxCoverage = maxCov
        self.isBranch = branch              # Is coverage selection based on branch coverage?
        
        self.matrixP = dict()
        self.P = list()                     # The new permutation

        # Calculate the min dictionary
        self.minValues = getMinValues(self.divmatrix, self.T)

        # The list of initial covered elements are all not covered
        self.coveredListCols = dict()
        for col in self.listCols:
            self.coveredListCols[col] = '0'

        # if there is a selection pool passed, select from it
        if selectionPool:
            self.selectionPool = selectionPool.copy()
        else:
            self.selectionPool = None

        # if there is a foundation passed, build over it
        if foundation:
            for key in foundation:
                self.matrixP[key] = self.covmatrix.pop(key)

                # Add it to the permutation
                self.P.append(key)

                # Remove it from the diversity matrix
                self.divmatrix.pop(key)
                self.T.remove(key)     

                # Filter the selectionPool (if any) by removing the tests already in the foundation
                if self.selectionPool and key in self.selectionPool:
                    self.selectionPool.remove(key)  
                
            self.coverage = getMatrixCoverage(self.matrixP, self.listCols, self.isBranch)

    def updateCoveredList(self, newRecord):
        for col in self.listCols:
            if float(self.coveredListCols[col]) < float(newRecord[col]):
                self.coveredListCols[col] = newRecord[col]
    
    def resetCoveredList(self):
        for col in self.listCols:
            self.coveredListCols[col] = '0'

    def makeOneSelection(self):
        
        method = self.makeOneSelectionCoverage()

        # Set the coveredListCols according the coverage of the maxKey
        self.updateCoveredList(self.matrixP[method])
        

        self.coverage = getMatrixCoverage(self.matrixP, self.listCols, self.isBranch)

        curCoveredCov = getCoverage(self.coveredListCols.values(), self.isBranch)
        if  curCoveredCov >= self.maxCoverage:
            self.resetCoveredList()

        return method

    def prioritize(self):
        while len(self.divmatrix) > 0:
            self.makeOneSelectionDiversity()
    
    def makeOneSelectionDiversity(self):
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
        
        # self.matrixP[maxKey] = copy.deepcopy( self.divmatrix[maxKey] )
        if maxKey in self.covmatrix.keys():
           self.matrixP[maxKey] = self.covmatrix.pop(maxKey)
        self.divmatrix.pop(maxKey)
        self.T.remove(maxKey)

        if self.selectionPool:
            self.selectionPool.remove(maxKey)
        
        return maxKey
    
    def __anotherSelection(self):
        # Calculate the min dictionary
        self.minValues = getMinValuesForP(self.divmatrix, self.T, self.P)

        maxKey = getMaxOfMins(self.minValues, self.selectionPool)
        self.P.append(maxKey)
        # self.minValuesP[maxKey] = self.minValues[maxKey]
        
        if maxKey in self.covmatrix.keys():
           self.matrixP[maxKey] = self.covmatrix.pop(maxKey)
        self.divmatrix.pop(maxKey)
        self.T.remove(maxKey)   

        if self.selectionPool:
            self.selectionPool.remove(maxKey)
        
        return maxKey

    
    def makeOneSelectionCoverage(self):
        selectedFlag = False
        
        # if there is a selection pool passed, select from it
        if self.selectionPool:
            # Pick the max coverage record from the selection pool
            # methodName, allMaxKeys = getMaxCoverage(self.covmatrix, self.listCols, self.selectionPool)
            methodName, allMaxKeys = getMaxAdditionalCoverage(self.covmatrix, self.coveredListCols, self.selectionPool)
            
            if len(allMaxKeys) == 1:
                self.selectionPool.remove(methodName)
            else:
                tempPool = self.selectionPool.copy()
                self.selectionPool = allMaxKeys
                # Find the most diverse out of them
                methodName = self.makeOneSelectionDiversity()
                self.selectionPool = tempPool
                self.selectionPool.remove(methodName)
                selectedFlag = True
        else:
            # Pick the max coverage record from the original matrix
            # methodName, allMaxKeys = getMaxCoverage(self.covmatrix, self.listCols)
            methodName, allMaxKeys = getMaxAdditionalCoverage(self.covmatrix, self.coveredListCols)
            if len(allMaxKeys) > 1:
                self.selectionPool = allMaxKeys.copy()
                # Find the most diverse out of them
                methodName = self.makeOneSelectionDiversity()
                self.selectionPool = None
                selectedFlag = True

        if selectedFlag:
            return methodName
        
        self.matrixP[methodName] = self.covmatrix.pop(methodName)

        # Add it to the permutation
        self.P.append(methodName)

        # Remove it from the diversity matrix
        self.divmatrix.pop(methodName)
        self.T.remove(methodName)

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

# Find the record with the highest coverage
def getMaxCoverage(simMat, listCols, selectionPool=None, branch=False):
    allMaxKeys = set()
    maxCov = 0
    if selectionPool:
        maxKey = list(selectionPool)[0]
        allMaxKeys.add(maxKey)

        # loop for each record, and get the coverage
        for key in selectionPool:
            curCov = findCoverageForRecord(simMat[key], listCols, branch)
            if curCov > maxCov:
                maxCov = curCov
                maxKey = key
                allMaxKeys.clear()
                allMaxKeys.add(key)
            elif curCov == maxCov:
                allMaxKeys.add(key)
    else:
        maxKey = list(simMat.keys())[0]
        allMaxKeys.add(maxKey)

        # loop for each record, and get the coverage
        for key in simMat.keys():
            curCov = findCoverageForRecord(simMat[key], listCols, branch)
            if curCov > maxCov:
                maxCov = curCov
                maxKey = key
                allMaxKeys.clear()
                allMaxKeys.add(key)
            elif curCov == maxCov:
                allMaxKeys.add(key)

    return maxKey, allMaxKeys

# Find the record with the highest coverage
def getMaxAdditionalCoverage(simMat, coveredListCols, selectionPool=None, branch=False):
    maxCov = 0
    allMaxKeys = set()

    if selectionPool:
        maxKey = list(selectionPool)[0]
        allMaxKeys.add(maxKey)

        # loop for each record, and get the coverage
        for key in selectionPool:
            curCov = findAdditionalCoverageForRecord(simMat[key], coveredListCols, branch)
            if curCov > maxCov:
                maxCov = curCov
                maxKey = key
                allMaxKeys.clear()
                allMaxKeys.add(key)
            elif curCov == maxCov:
                allMaxKeys.add(key)
    else:
        maxKey = list(simMat.keys())[0]

        # loop for each record, and get the coverage
        for key in simMat.keys():
            curCov = findAdditionalCoverageForRecord(simMat[key], coveredListCols, branch)
            if curCov > maxCov:
                maxCov = curCov
                maxKey = key
                allMaxKeys.clear()
                allMaxKeys.add(key)
            elif curCov == maxCov:
                allMaxKeys.add(key)

        
    return maxKey, allMaxKeys

# Get the coverage of a single record and the elements covered
def findAdditionalCoverageForRecord(record, coveredListCols, branch=False):
    coverage = 0
    
    for key in record.keys():
        # Add only an element that is not covered before
        if float(record[key]) > float(coveredListCols[key]):
            # coveredListCols[key] = record[key]
            coverage += float(record[key])
    
    if branch:
        return (coverage * 2) / (len(record) * 2)
    else:
        return coverage / len(record)
    
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

