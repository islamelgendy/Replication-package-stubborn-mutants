import re
import os
import sys
import jellyfish

from utils.CSVLoader import CSVLoader
from utils.bytecode import parse_method_bytecode
from utils.utilsIO import readFile
from utils.utilsSystem import createFolder

class TestMethod:
    
    def __init__(self, srcFile, bytecodeFile, classname, mtdName, startLine, body = None, byteCode = None):
        self.sourceFile = srcFile
        self.sourceBytecodeFile = bytecodeFile
        self.methodNameOnly = mtdName
        self.methodName = classname + '::' + mtdName
        self.startLine = startLine
        self.endLine = 0
        if body:
            self.body = body.copy()
        else:
            self.body = list()
            self.loadMethod()
        
        if byteCode:
            self.byteCode = byteCode.copy()
        else:
            self.byteCode = list()
            self.loadBytecode()

    def loadMethod(self):
        # Open the source file
        try:
            with open(self.sourceFile, "r") as f:
                contents = f.readlines()
        except:
            print(self.sourceFile + ' is not found.')

        try:
            # Get the closing Line
            self.endLine = getClosingLine(contents, self.startLine)

            # Get the body of the test method
            self.body = contents[self.startLine:self.endLine+1]
        except:
            print(self.methodName + ' is not found at the specified lines (' 
                + str(self.startLine) + ':' + str(self.endLine) + ')')
            
    def loadBytecode(self):
        # Open the source file
        self.byteCode = parse_method_bytecode(self.sourceBytecodeFile, self.methodNameOnly)
            
    def getAsSingleString(self):
        return ''.join(self.body)
        # body = ''

    def fixTestcase(self):
        # Loop through the body and check it
        endLine = getClosingLine(self.body, 0)
        self.endLine = str(endLine + int(self.startLine))
        # Get the body of the test method
        self.body = self.body[:endLine+1]    
    
    def getBytecodeAsSingleString(self):

        return ''.join(self.byteCode)


def getClosingLine(contents, startLine):

    # The stack is intially having the opening braket
    stack = []
    stack.append('{')

    # Identify the start index
    if contents[startLine].count('{') > 0:
        index = startLine + 1
    else:
        index = startLine + 2

    # Loop in the contents from the startLine until the stack is empty
    while len(stack) > 0:
        # Get the number of occurrences of '{' and the number of occurrences of '}'
        openingBrackets = contents[index].count('{')
        closingBrackets = contents[index].count('}')

        # for each opening bracket append in the stack
        for i in range(openingBrackets):
            stack.append('{')

        # for each closing bracket pop from the stack
        for i in range(closingBrackets):
            stack.pop()

        index += 1

    return index - 1

def pairwiseLevenshtein(mtd1, mtd2, textual = True):
    if textual:
        method1 = mtd1.getAsSingleString()
        method2 = mtd2.getAsSingleString()
    else:
        method1 = mtd1.getBytecodeAsSingleString()
        method2 = mtd2.getBytecodeAsSingleString()

    return jellyfish.levenshtein_distance(method1, method2)

def loadNewTestMethods(newTestsTextSimPath):
    contents = readFile(newTestsTextSimPath)
    i = 0
    while i <len(contents):
        contents[i] = contents[i].strip()
        i += 1
    return contents


def loadTestcases(folder, project, id, simFile = None):
    listTestMethods = list()
    if simFile:
        contents = readFile(simFile)
    else:
        file = folder + project + '.' + id + 'f.test-cases.txt'
        contents = readFile(file)
    firstMethodFlag = True
    body = list()
    bytecodeBody = list()
    sourceCode = False
    byteCode = False

    # Start parsing the lines
    for line in contents:
        if line.startswith('Source File:'):
            # if this is the start of a new test case, add the previous into the list of methods
            if firstMethodFlag:
                firstMethodFlag = False
                body = list()
                bytecodeBody = list()
            else:
                mtd = TestMethod(sourceFile, bytecodeFile, className, methodName, startLine, body, bytecodeBody)
                listTestMethods.append(mtd)
                body = list()
                bytecodeBody = list()
                sourceCode = False
                byteCode = False
            sourceFile = re.split(':', line)[1].strip()
        elif line.startswith('Bytecode File:'):
            bytecodeFile = re.split(':', line)[1].strip()
        elif line.startswith('Class name:'):
            className = re.split(':', line)[1].strip()
        elif line.startswith('Method name:'):
            methodName = re.split(':', line)[1].strip()
        elif line.startswith('Start line:'):
            startLine = re.split(':', line)[1].strip()
        elif line.startswith('End line:'):
            endLine = re.split(':', line)[1].strip()
        elif line.startswith('Method source code: '):
            sourceCode = True
            byteCode = False
        elif line.startswith('Method byte code: '):
            sourceCode = False
            byteCode = True
        # if the line is comment, then ignore it
        elif line.strip().startswith('//'):
            continue
        elif sourceCode:
            body.append(line)
        elif byteCode:
            bytecodeBody.append(line)
        
    # Add the last test method
    mtd = TestMethod(sourceFile, bytecodeFile, className, methodName, startLine, body, bytecodeBody)
    listTestMethods.append(mtd)

    return listTestMethods

def checkMethod(listTestMethods, className, methodName):
    method = className + '::' + methodName
    for mtd in listTestMethods:
        if method == mtd.methodName:
            return True
    
    return False

def getSimilarityMatrix(listTestMethods, textual = True):
    simMatrix = dict()

    # Build the matrix
    for mtd in listTestMethods:
        record = dict()
        for innermtd in listTestMethods:
            record[innermtd.methodName] = 0

        simMatrix[mtd.methodName] = record

    # Populate the matrix
    iteration, total = 0, float(len(listTestMethods))
    for i in closed_range(0, len(listTestMethods)-1):
        iteration += 1
        sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
        sys.stdout.flush()
        for j in closed_range(i+1, len(listTestMethods)-1):
            simValue = pairwiseLevenshtein(listTestMethods[i], listTestMethods[j], textual)
            simMatrix[listTestMethods[i].methodName][listTestMethods[j].methodName] = simValue
            simMatrix[listTestMethods[j].methodName][listTestMethods[i].methodName] = simValue

    return simMatrix

def findMethodInListTestMethods(listTestMethods, methodName):
    i = 0 
    for elem in listTestMethods:
        if elem.methodName == methodName:
            return i
        i += 1
    
    return -1

def recalculateSimilarityMatrix(listTestMethods, simlarityCSV, textual = True):
    simMatrix = simlarityCSV.matrix

    for testMtd in listTestMethods:
        newMethod = testMtd.methodName
        if '_ESTest::test' in testMtd.methodName or ('::test' in testMtd.methodName and testMtd.methodName.startswith('RegressionTest')):
            continue

        for oldMethod in simMatrix.keys():
            oldMethodIndex = findMethodInListTestMethods(listTestMethods, oldMethod)
            simValue = pairwiseLevenshtein(listTestMethods[oldMethodIndex], testMtd, textual)
            simMatrix[oldMethod][newMethod] = simValue
            simMatrix[newMethod][oldMethod] = simValue

    return simMatrix

def addToSimilarityMatrix(listTestMethods, newMethods, simlarityCSV:CSVLoader, textual = True):
    simMatrix = simlarityCSV.matrix

    for newMethod in newMethods:
        simMatrix[newMethod] = dict() # the new row for the current new method
        curMethodIndex = findMethodInListTestMethods(listTestMethods, newMethod)
        for oldMethod in simMatrix.keys():
            oldMethodIndex = findMethodInListTestMethods(listTestMethods, oldMethod)
            simValue = pairwiseLevenshtein(listTestMethods[oldMethodIndex], listTestMethods[curMethodIndex], textual)
            simMatrix[oldMethod][newMethod] = simValue
            simMatrix[newMethod][oldMethod] = simValue
        
        simMatrix[newMethod][newMethod] = 0

    return simMatrix

def closed_range(start, stop, step=1):
  dir = 1 if (step > 0) else -1
  return range(start, stop + dir, step)

def writeFaultDetectionToFile(listTestMethods, listMethodsDetectingRealFaults, csvPath):

    # Header of file
    contents = ['Method,Fault-Detected\n']
    for method in listTestMethods:
        if method.methodName in listMethodsDetectingRealFaults:
            contents.append(method.methodName + ', 1\n')
        else:
            contents.append(method.methodName + ', 0\n')

    with open(csvPath, "w") as f:
        contents = "".join(contents)
        f.write(contents)

def writeOnlyFaultDetectingMethodsToFile(listMethodsDetectingRealFaults, csvPath):

    # Header of file
    contents = ['Method,Fault-Detected\n']
    for method in listMethodsDetectingRealFaults:
        contents.append(method + ', 1\n')

    createFolder( os.path.dirname(os.path.abspath(csvPath)) )
    with open(csvPath, "w") as f:
        contents = "".join(contents)
        f.write(contents)

def writeSimMatrixToFile(simMat, listTestMethods, csvPath, timeInMS):

    records = convertMatrixToList(simMat, listTestMethods)

    # Add time taken to measure the matrix
    if timeInMS > 0:
        records.append("The time of execution of above matrix is :" + str(timeInMS) + '\n')

    with open(csvPath, "w") as f:
        contents = "".join(records)
        f.write(contents)

def writeTestCasesToFile(listTestMethods, csvPath, newLine = True):

    records = list()

    for mtd in listTestMethods:
        className = re.split('::', mtd.methodName)[0].strip()
        methodName = re.split('::', mtd.methodName)[1].strip()
        records.append('Source File: ' + mtd.sourceFile + '\n')
        records.append('Bytecode File: ' + mtd.sourceBytecodeFile + '\n')
        records.append('Class name: ' + className + '\n')
        records.append('Method name: ' + methodName + '\n')
        records.append('Start line: ' + str(mtd.startLine) + '\n')
        records.append('End line: ' + str(mtd.endLine) + '\n')
        records.append('Method source code: \n')
        for line in mtd.body:
            records.append(line)
        
        records.append('Method byte code: \n')
        for line in mtd.byteCode:
            if newLine:
                records.append(line + '\n')
            else:
                records.append(line)

    with open(csvPath, "w") as f:
        contents = "".join(records)
        f.write(contents)

def writeNewTestsToFile(newMethod, csvPath):
    # If the file already exists, add to it
    if os.path.isfile(csvPath):
        with open(csvPath, "a") as f:
            contents = "".join(newMethod)
            f.write(contents)
    else:
        with open(csvPath, "w") as f:
            contents = "".join(newMethod)
            f.write(contents)

def appendTestCaseToFile(mtd, csvPath):

    records = list()

    className = re.split('::', mtd.methodName)[0].strip()
    methodName = re.split('::', mtd.methodName)[1].strip()
    records.append('Source File: ' + mtd.sourceFile + '\n')
    records.append('Bytecode File: ' + mtd.sourceBytecodeFile + '\n')
    records.append('Class name: ' + className + '\n')
    records.append('Method name: ' + methodName + '\n')
    records.append('Start line: ' + str(mtd.startLine) + '\n')
    records.append('End line: ' + str(mtd.endLine) + '\n')
    records.append('Method source code: \n')
    for line in mtd.body:
        records.append(line)
    
    records.append('Method byte code: \n')
    for line in mtd.byteCode:
        records.append(line + '\n')

    with open(csvPath, "a") as f:
        contents = "".join(records)
        f.write(contents)

def convertMatrixToList(simMat, listTestMethods):
    records = list()
    # Set the header line first
    headerLine = ': , '
    for mtd in listTestMethods:
        headerLine += mtd.methodName + ' , '
    
    records.append(headerLine + '\n')

    # Start populating each record
    for mtd in listTestMethods:
        curLine = mtd.methodName + ' , '
        curRecord = simMat[mtd.methodName]
        # for cell in curRecord:
        for i in closed_range(0, len(listTestMethods)-1):
            curLine += str(simMat[mtd.methodName][listTestMethods[i].methodName]) + ' , '
        
        records.append(curLine + '\n')

    return records