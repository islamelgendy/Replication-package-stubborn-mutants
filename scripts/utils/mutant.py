
import re

class Mutant:
    detected = True
    status = 'KILLED'
    sourceFile = ''
    lineNumber = 0
    index = 0
    mutator = ''
    killingTests = list()
    succeedingTests = list()

    def parse(self, line):
        self.detected = getDetected(line)
        self.status = getStatus(line)
        self.sourceFile = getToken(line, 'sourceFile')
        self.lineNumber = getToken(line, 'lineNumber')
        self.mutatedMethod = getToken(line, 'mutatedMethod')
        self.mutatedClass = getToken(line, 'mutatedClass')
        self.index = getToken(line, 'index')
        self.mutator = sanitizeMutator( getToken(line, 'mutator') )
        killing = getToken(line, 'killingTests')
        self.killingTests = parseTests(killing)
        succeeding = getToken(line, 'succeedingTests')
        self.succeedingTests = parseTests(succeeding)

    def equals(self, mutant:str):
        curMut = str(self.lineNumber) + '::' + str(self.mutator) + '::' + str(self.index)

        return curMut == mutant.strip()

def sanitizeMutator(mutator):
    tokens = re.split('\\.', mutator)
    return tokens[-1]
    
def getMethodsAndMutants(listMutants):
    
    methods = set()
    mutatns = set()

    for infoLine in listMutants:
        # loop through all killing tests
        for killingTest in infoLine.killingTests:
            methods.add(killingTest)
        
        # loop through all succeeding tests
        for succeedingTest in infoLine.succeedingTests:
            methods.add(succeedingTest)

        # Add the mutant to the set of mutants
        mutatns.add(str(infoLine.lineNumber) + '::' + str(infoLine.mutator) + '::' + str(infoLine.index))

    return methods, mutatns

def buildMutantMap(listMutants):

    # The killMap is a dict, where the keys are the method names, and the values are dict of {mutant, killed} pairs
    killMap = dict() 


    methods, mutants = getMethodsAndMutants(listMutants)

    # Build the kill map
    for method in methods:
        # The mutantMap is a dict where the keys are the mutants, and the values are the killed status 0 for killed, 1 otherwise
        mutantMap = dict()

        # Build the dict of the mutants
        for mutant in mutants:
            mutantMap[mutant] = '0' # By default, the mutant is not killed

        killMap[method] = mutantMap

    # Start populating the kill map using the list of mutants
    for mut in listMutants:
        # Get the current mutant
        curMutant = str(mut.lineNumber) + '::' + str(mut.mutator) + '::' + str(mut.index)

        # Loop through the killing tests and set the mutant to killed
        for killingTest in mut.killingTests:

            # Get the dict of mutants for that method
            d = killMap[killingTest]

            d[curMutant] = '1'
    
    return killMap

def getHeader(listMutants):
    mutantOrder = list()
    lineHeader = 'Class::Test , '
    for infoLine in listMutants:
        lineHeader += str(infoLine.lineNumber) + '::' + str(infoLine.mutator) + '::' + str(infoLine.index) + ' , '
        mutantOrder.append(str(infoLine.lineNumber) + '::' + str(infoLine.mutator) + '::' + str(infoLine.index))

    return lineHeader[0:len(lineHeader)-2], mutantOrder

def getCSVKillMap(listMutants):
    
    contents = list()
    header, mutantOrder = getHeader(listMutants)
    contents.append(header + '\n')

    killMap = buildMutantMap(listMutants)

    # Loop through the keys of the killMap (methodNames)
    for record in sorted(killMap.keys()):
        line = record + ' , '
        mutDict = killMap[record]

        # Loop through the mutants of that record
        for mut in mutantOrder:
            mutantStatus = mutDict[mut]

            line += mutantStatus + ' , '
        
        contents.append(line + '\n')
    
    return contents
    
def getDetected(line):
    return getValue(line, 'detected')

def getStatus(line):
    return getValue(line, 'status')

def getToken(line, key):
    line = str(line)    
    openTag = '<' + key + '>'
    closeTag = '</' + key + '>'
    startPos = line.find(openTag)
    endPos = line.find(closeTag)
    return line[startPos + len(openTag): endPos].strip()

def getValue(line, att):
    line = str(line)
    
    startPos = line.find(att) + len(att) + 2
    endPos = line.find("'", startPos)
    return line[startPos: endPos].strip()

def parseTests(testsLine):
    # delimeter is | between tests
    testList = list()
    if testsLine == '':
        return testList
    tests = re.split('\\|', testsLine)
    for test in tests:
        testList.append(getClassTestName(test))
    
    return sorted(testList)

def getClassTestName(test):
    pos = test.find('(')
    test = test[0:pos]
    tokens = re.split('\\.', test)
    return tokens[-2] + '::' + tokens[-1]