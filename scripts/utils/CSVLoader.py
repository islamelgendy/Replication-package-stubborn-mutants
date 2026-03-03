import random
import time
import re

class CSVLoader:

    def __init__(self, file):
        self.fileName = file
        self.CSVType = str()
        self.listMethods = list()
        self.listMethodsCoverage = list()
        self.listCols = list()
        self.matrix = dict()
        self.load(file)

    def load(self, file):
        self.fileName = file
        if 'statement.coverage' in file:
            self.CSVType = 'statement'
        elif 'branch.coverage' in file:
            self.CSVType = 'branch'
        elif '.mutation' in file:
            self.CSVType = 'mutation'
        elif '.textSimilarity' in file:
            self.CSVType = 'similarity'
        
        with open(file, "r") as f:
            contents = f.readlines()
        
        index = 0
        for line in contents:
            if line.startswith('The time of execution of above matrix is'):
                continue
            if index == 0:
                # Header line of the CSV, then get the list of Cols
                self.listCols = getListCols(line)
            else:
                method, d = parseRecord(line, self.listCols)
                self.listMethods.append(method)
                self.matrix[method] = d
                self.listMethodsCoverage.append( self.getCoverageForMethod(method) )
                            
            index += 1
    
    def getCoverageForMethod(self, methodName):
        coverage = 0
        total = len(self.listCols)
        # Retrieve the coverage info for that method
        try:
            record = self.matrix[methodName]
        except:
            print('The ' + methodName + ' does not exist...exiting')
            return 0

        # Loop through the columns one by one and check the coverage
        for col in self.listCols:
            coverage += float(record[col])

        if self.CSVType == 'branch':
            coverage *= 2
            total *= 2

        return coverage / total
    
    def getTotalCoverage(self):
        
        coverage = getMatrixCoverage(self.matrix, self.listCols, self.CSVType == 'branch')

        return coverage
    
    def randomCoverageSelection(self):
        start_time = time.time()
        # list of coverage initially set to 0s
        covered = dict()
        for col in self.listCols:
            covered[col] = '0'
        
        # Get the original coverage
        orgCov = self.getTotalCoverage()
        copyMatrix = dict(self.matrix)

        # return a new matrix that have the same coverage as the original where methods are added randomly
        newMatrix = dict()

        # Set the current coverage initially to zero
        curCov = 0

        # Loop until the curCov reach the orgCov
        while curCov < orgCov:

            # Pick a random element from the original matrix
            methodName, methodRecord = random.choice( list( copyMatrix.items() ) )
            copyMatrix.pop(methodName)

            newCov = getAdditionalCoverage(covered, methodRecord, self.CSVType=='branch')

            if newCov > curCov:
                curCov = newCov
                newMatrix[methodName] = methodRecord
        
        return newMatrix, (time.time() - start_time)
    
    def randomSelection(self):
        start_time = time.time()
        # list of coverage initially set to 0s
        covered = dict()
        for col in self.listCols:
            covered[col] = '0'
        
        # Get the original coverage
        orgCov = self.getTotalCoverage()
        copyMatrix = dict(self.matrix)

        # return a new matrix that have the same coverage as the original where methods are added randomly
        newMatrix = dict()

        # Set the current coverage initially to zero
        curCov = 0

        # Loop until the curCov reach the orgCov
        while curCov < orgCov:

            # Pick a random element from the original matrix
            methodName, methodRecord = random.choice( list( copyMatrix.items() ) )
            copyMatrix.pop(methodName)

            curCov = getAdditionalCoverage(covered, methodRecord, self.CSVType=='branch')
            newMatrix[methodName] = methodRecord
            
        
        return newMatrix, (time.time() - start_time)
    
    def selectionStacked(self):
        start_time = time.time()
        
        # list of coverage initially set to 0s
        covered1 = dict()
        covered2 = dict()
        for col in self.listCols:
            covered1[col] = '0'
            covered2[col] = '0'
        
        # Get the original coverage
        orgCov = self.getTotalCoverage()
        copyMatrix1 = dict(self.matrix)
        copyMatrix2 = dict(self.matrix)

        # return a new matrix that have the same coverage as the original where methods are added randomly
        newMatrix1 = dict()
        newMatrix2 = dict()

        # Set the current coverage initially to zero
        curCov1 = 0
        curCov2 = 0

        # Loop until the curCov reach the orgCov
        while curCov1 < orgCov and curCov2 < orgCov:
            curCov1, curCov2 = makeSelection(copyMatrix1, copyMatrix2, covered1, covered2, newMatrix1, newMatrix2, curCov1, curCov2, self.CSVType=='branch')

        # Check which selection method is finished first and reset it

        # If random selection is not done yet, reset the other one and continue working
        while curCov1 < orgCov:
            resetCoverage(covered2)
            curCov1, curCov2 = makeSelection(copyMatrix1, copyMatrix2, covered1, covered2, newMatrix1, newMatrix2, curCov1, curCov2, self.CSVType=='branch')
        
        while curCov2 < orgCov:
            resetCoverage(covered1)
            curCov1, curCov2 = makeSelection(copyMatrix1, copyMatrix2, covered1, covered2, newMatrix1, newMatrix2, curCov1, curCov2, self.CSVType=='branch')
        
        return newMatrix1, newMatrix2, (time.time() - start_time)

def makeSelection(copyMatrix1, copyMatrix2, covered1, covered2, newMatrix1, newMatrix2, curCov1, curCov2, branch):
    # Pick a random element from the original matrix
    methodName1, methodRecord1 = random.choice( list( copyMatrix1.items() ) )
    copyMatrix1.pop(methodName1)

    methodName2, methodRecord2 = random.choice( list( copyMatrix2.items() ) )
    copyMatrix2.pop(methodName2)

    newCov1 = getAdditionalCoverage(covered1, methodRecord1, branch)
    newMatrix1[methodName1] = methodRecord1
    if newCov1 > curCov1:
        curCov1 = newCov1

    newCov2 = getAdditionalCoverage(covered2, methodRecord2, branch)
    newMatrix2[methodName2] = methodRecord2
    if newCov2 > curCov2:
        curCov2 = newCov2
        
    
    return curCov1, curCov2

def getListCols(header):
    cols = list()
    tokens = re.split(',', header)
    for elem in tokens:
        if not (elem.strip() == 'Class::Test' or elem.strip() == ':' or elem.strip() == ''):
            cols.append(elem.strip())
    return cols

def parseRecord(record, listCols):
    
    tokens = re.split(',', record)
    method = tokens[0].strip()

    values = list()
    index = 0
    d = dict()
    for elem in tokens[1:]:
        value = elem.strip()
        if value == '':
            continue
        values.append(value)
        d[listCols[index]] = value

        index += 1

    return method, d

def getCoverage(covered, branch=False):
    count = 0
    for elem in covered:
        count += float(elem)

    if branch:
        return round( (count * 2) / (len(covered) * 2), 2)
    
    if len(covered) == 0:
        return 0
    
    return round( count / len(covered), 2 )

def getMatrixCoverage(matrix, listCols, branch = False):
    # An array of values to represent the coverage of col
    covered = list()

    for col in listCols:
        check = False
        for method in matrix.keys():
            item = matrix[method][col]

            # If it is fully covered add it
            if item == '1':
                covered.append(item)  
                check = True     
                break

        # If this is a branch and not yet covered, check for partial coverage
        if branch and item != '1':
                for methodAgain in matrix.keys():
                    item = matrix[methodAgain][col]

                    # If it is fully covered add it
                    if item == '0.5':
                        covered.append(item)    
                        check = True   
                        break
        
        if not check:
            covered.append('0')


    # calculate the coverage of the list
    coverage = getCoverage(covered, branch)

    return coverage

def getAdditionalCoverage(covered, methodRecord, branch = False):
    coverage = 0

    for col in covered.keys():
        if float(methodRecord[col]) > float(covered[col]):
            covered[col] = methodRecord[col]
        
        coverage += float(covered[col])

    if branch:
        return round( (coverage*2) / (len(covered)*2), 2)
    
    return round(float(coverage) / len(covered), 2)

def resetCoverage(covered):
    for col in covered.keys():
        covered[col] = '0'

# Find out the mutation score using the evaluated methods in it
def evaluateMutationScore(mutMatrix, evalMethods, mutantList):
    # list of coverage initially set to 0s
    covered = dict()
    for mutant in mutantList:
        covered[mutant] = '0'
    mutScore = 0
    
    for curMethod in evalMethods:
        if curMethod in mutMatrix:
            curRecord = mutMatrix[curMethod]
            mutScore = getAdditionalCoverage(covered, curRecord, False)
        else:
            debug = True

    return mutScore

# Test the class
# fileName = '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/coverage/time.13f.PeriodFormatterBuilder.branch.coverage.csv'
# fileName = '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/mutation/time.13f.mutation.csv'
# obj = CSVLoader(fileName)
# totalCov = obj.getTotalCoverage()
# print('Total coverage is ' + str(totalCov) )