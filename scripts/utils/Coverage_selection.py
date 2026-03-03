import random
import copy

from utils.CSVLoader import CSVLoader, getCoverage, getMatrixCoverage
from utils.utilsIO import filterFiles

class CoverageSelection:

    def __init__(self, coverageCSV: CSVLoader, maxCov, foundation = None, selectionPool = None, branch = False):
        self.listCols, self.matrix = deepcopyMatrix(coverageCSV)
        self.coverage = 0
        self.maxCoverage = maxCov
        
        self.isBranch = branch              # Is coverage selection based on branch coverage?
        self.matrixP = dict()
        self.P = list()                     # The new permutation

        # if there is a selection pool passed, select from it
        if selectionPool:
            self.selectionPool = selectionPool.copy()
        else:
            self.selectionPool = None

        # The list of initial covered elements are all not covered
        self.coveredListCols = dict()
        for col in self.listCols:
            self.coveredListCols[col] = '0'
        
        # if there is a foundation passed, build over it
        if foundation:
            for key in foundation:
                self.matrixP[key] = self.matrix.pop(key)        
                # Filter the selectionPool (if any) by removing the tests already in the foundation
                if self.selectionPool and key in self.selectionPool:
                    self.selectionPool.remove(key)
                
            self.coverage = getMatrixCoverage(self.matrixP, self.listCols, self.isBranch)

            
    def prioritize(self):
        while len(self.matrix) > 0:
            self.makeOneSelection()

    def makeOneSelectionRandom(self):
        
        # if there is a selection pool passed, select from it
        if self.selectionPool:
            # Pick a random element from the selection pool
            methodName = random.choice( list(self.selectionPool) )
            self.selectionPool.remove(methodName)
        else:
            # Pick a random element from the original matrix
            methodName, methodRecord = random.choice( list( self.matrix.items() ) )
        
        self.matrixP[methodName] = self.matrix.pop(methodName)
        
        self.coverage = getMatrixCoverage(self.matrixP, self.listCols, self.isBranch)

        return methodName
    
    def makeOneSelectionCoverage(self, maxFlag = True):
        
        # if there is a selection pool passed, select from it
        if self.selectionPool:
            # Pick the max coverage record from the selection pool
            if maxFlag:
                methodName = getMaxCoverage(self.matrix, self.listCols, self.selectionPool)
            else:
                methodName = getMinCoverage(self.matrix, self.listCols, self.selectionPool)
            self.selectionPool.remove(methodName)
        else:
            # Pick the max coverage record from the original matrix
            if maxFlag:
                methodName = getMaxCoverage(self.matrix, self.listCols)
            else:
                methodName = getMinCoverage(self.matrix, self.listCols)

        self.matrixP[methodName] = self.matrix.pop(methodName)
        
        self.coverage = getMatrixCoverage(self.matrixP, self.listCols, self.isBranch)

        curCoveredCov = getCoverage(self.coveredListCols.values(), self.isBranch)
        if  curCoveredCov >= self.maxCoverage:
            self.resetCoveredList()

        return methodName

    def makeOneSelectionAdditionalCoverage(self):
        
        # Pick the max coverage record from the original matrix
        methodName = getMaxAdditionalCoverage(self.matrix, self.listCols, self.coveredListCols)

        # Set the coveredListCols according the coverage of the maxKey
        self.updateCoveredList(self.matrix[methodName])
        
        self.matrixP[methodName] = self.matrix.pop(methodName)
        
        self.coverage = getMatrixCoverage(self.matrixP, self.listCols, self.isBranch)

        curCoveredCov = getCoverage(self.coveredListCols.values(), self.isBranch)
        if  curCoveredCov >= self.maxCoverage:
            self.resetCoveredList()

        return methodName
    
    # force the selection of the specified method
    def forceSelection(self, method):
        
        # if there is a selection pool passed, select from it
        if method in self.selectionPool:
            self.selectionPool.remove(method)
        
        self.matrixP[method] = self.matrix.pop(method)
        
        self.coverage = getMatrixCoverage(self.matrixP, self.listCols, self.isBranch)

        return method
    
    def updateCoveredList(self, newRecord):
        for col in self.listCols:
            if float(self.coveredListCols[col]) < float(newRecord[col]):
                self.coveredListCols[col] = newRecord[col]
    
    def resetCoveredList(self):
        for col in self.listCols:
            self.coveredListCols[col] = '0'

def deepcopyMatrix(coverageCSV: CSVLoader):
    listCols = copy.deepcopy(coverageCSV.listCols)
    matrix = dict()

    for mtd in coverageCSV.listMethods:
        matrix[mtd] = copy.deepcopy(coverageCSV.matrix[mtd])

    return listCols, matrix

# Find the record with the highest coverage
def getMaxCoverage(simMat, listCols, selectionPool=None, branch=False):
    maxCov = 0
    if selectionPool:
        maxKey = list(selectionPool)[0]

        # loop for each record, and get the coverage
        index = 0
        for key in selectionPool:
            # if key == 'CpioArchiveOutputStream_ESTest::test04':
            #     debug = True
            curCov = findCoverageForRecord(simMat[key], listCols, branch)
            index += 1
            if curCov > maxCov:
                maxCov = curCov
                maxKey = key
    else:
        maxKey = list(simMat.keys())[0]

        # loop for each record, and get the coverage
        for key in simMat.keys():
            curCov = findCoverageForRecord(simMat[key], listCols, branch)
            if curCov > maxCov:
                maxCov = curCov
                maxKey = key

    return maxKey

# Find the record with the lowest coverage
def getMinCoverage(simMat, listCols, selectionPool=None, branch=False):
    minCov = 100
    if selectionPool:
        minKey = list(selectionPool)[0]

        # loop for each record, and get the coverage
        for key in selectionPool:
            curCov = findCoverageForRecord(simMat[key], listCols, branch)
            if curCov < minCov:
                minCov = curCov
                minKey = key
    else:
        minKey = list(simMat.keys())[0]

        # loop for each record, and get the coverage
        for key in simMat.keys():
            curCov = findCoverageForRecord(simMat[key], listCols, branch)
            if curCov < minCov:
                minCov = curCov
                minKey = key

    return minKey

# Find the record with the highest coverage
def getMaxAdditionalCoverage(simMat, listCols, coveredListCols, branch=False):
    maxCov = 0
    maxKey = list(simMat.keys())[0]

    # loop for each record, and get the coverage
    for key in simMat.keys():
        curCov = findAdditionalCoverageForRecord(simMat[key], listCols, coveredListCols, branch)
        if curCov > maxCov:
            maxCov = curCov
            maxKey = key
        
    return maxKey

# Get the coverage of a single record and the elements covered
def findAdditionalCoverageForRecord(record, listCols, coveredListCols, branch=False):
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

# Get the coverage of a single record and the elements covered
def findCoverageForRecord(record, listCols, branch=False):
    coverage = 0
    
    for key in record.keys():
        coverage += float(record[key])
    
    if branch:
        return (coverage * 2) / (len(record) * 2)
    else:
        return coverage / len(record)
    
# project = "time"
# id = "3"
# coverageFolder = "../resources/coverage/"
# coverageFolder = "D:\\Work\\PhD\\DBT-workbench\\resources\\coverage\\"

# # Load the similarity matrix
# try:
#     statementCoverageFile = filterFiles(coverageFolder, project + '.' + id + 'f', 'statement.coverage.csv')[0]
#     statementCSV = CSVLoader(statementCoverageFile) 

#     obj = CoverageSelection(statementCSV)

#     obj.makeOneSelectionRandom()
#     print('coverage ', obj.coverage)
#     print('methods ', obj.matrixP.keys())
#     obj.makeOneSelectionRandom()
#     print('coverage ', obj.coverage)
#     print('methods ', obj.matrixP.keys())
#     obj.makeOneSelectionRandom()
#     print('coverage ', obj.coverage)
#     print('methods ', obj.matrixP.keys())
#     obj.makeOneSelectionRandom()
#     print('coverage ', obj.coverage)
#     print('methods ', obj.matrixP.keys())
# except:
#     print('Statement matrix can NOT be loaded')

