import re

# from selection_after_coverage import runExp

# Given the mutation csv, return a dictionary of mutants and killing tests, and the line numbers where mutants exist
def getMutants(mutContents):
    mutants = list()
    lineNumbers = set()
    killingTests = dict()
    
    # Get the header where all the mutants are written
    header = mutContents[0]
    tokens = re.split(',', header)

    for elem in tokens:
       
       # skip the first element of the header
       if elem.strip() == 'Class::Test':
            continue
         
       #Add the mutants
       mutants.append(elem)
         
       # Find the index of the current mutant
       mutIndex = tokens.index(elem)
       # Extract the line number where the mutant is
       lineNumber = re.split('::', elem)[0]
       lineNumbers.add(lineNumber.strip())
       # Get all tests that kill the current mutant
       tests = getCoveringTests(mutContents, mutIndex)
       # Add the killing tests to that mutant to build the kill dictionary
       killingTests[elem] = tests

    return killingTests, lineNumbers

# Given the contents of a csv and the element index, get all tests covering that elem
def getCoveringTests(contents, index):
    coverTests = list()
    for line in contents:
         tokens = re.split(',', line)
         if tokens[index].strip() == '1':
               coverTests.append(tokens[0].strip())
    
    return coverTests

# Given the coverage csv, get all tests
def getAllTests(covContents):
    allTests = list()

    for line in covContents:
        # skip the header
       if line.strip().startswith('Class::Test'):
            continue
       
       method = re.split(',', line)[0].strip()
       allTests.append(method)
    
    return allTests

# Given the coverage csv and the information about the mutants (i.e. lines where they are and the mutants themselves)
# get all tests that execute the mutant
def getTestsExecutingMutants(covContents, lineNumbers):
    coveringTests = dict()

    # Get the header where all the lines are
    header = covContents[0]
    tokens = re.split(',', header)

    for elem in tokens:
       # skip the first element of the header
       if elem.strip() == 'Class::Test':
            continue
       
       # Skip the last elem or elements where an error would happen
       if not ':' in elem:
            continue
       # Find the index of the current line
       lineIndex = tokens.index(elem)

       # Extract the line number
       lineNumber = re.split(':', elem)[1]

       # If the current line does not exist in the list of the mutants lines, then skip
       if not lineNumber in lineNumbers:
            continue

       # Get all tests that execute the current line
       tests = getCoveringTests(covContents, lineIndex)

       # Add the covering tests to that mutant to build the coverage dictionary
       coveringTests[elem] = tests

    return coveringTests

def normalizeTests(coveringTests):
    normalizedSetOfTests = set()
    for elem in coveringTests.keys():
         list = coveringTests[elem]
         normalizedSetOfTests.update(list)
    
    return sorted(normalizedSetOfTests)

# Given the minimal tests achieving max coverage, identify the mutants killed and the stubborn mutants
def getCategorizedMutants(foundationMethods : list, killingTests : dict):
    easyMutants = list()
    stubbornMutants = list()
    unreachableMutants = list()

    for mutant in killingTests.keys():
        stubbornFlag = True
        currentTests = killingTests[mutant]
        if len(currentTests) == 0:
            unreachableMutants.append(mutant)
        else:
            for test in currentTests:
                if test.strip() in foundationMethods:
                    stubbornFlag = False
                    easyMutants.append(mutant)
                    break
            
            if stubbornFlag:
                stubbornMutants.append(mutant)
    
    return easyMutants, stubbornMutants, unreachableMutants

# Given the tests that cover the mutants and the tests that kill the mutants, 
# identify the stubborn mutants (i.e. mutant that can be killed only if there is less than 50% killing tests over covering tests)
def getReachabilityStubbornMutants(coveringTests : dict, killingTests : dict, stubbornProbablity = 0.5):
    stubbornMutants = list()
    easyMutants = list()

    for mutant in killingTests.keys():
        stubbornFlag = True
        killPool = killingTests[mutant]

        # check that the mutant is in the coveringTests dict
        if len(killPool) == 0:
            continue
        # elif not mutant in coveringTests.keys():
        #     stubbornFlag = True
        else:
            coverPool = getCoveringTestsForMutant(coveringTests, mutant)
            if len(killPool) > (stubbornProbablity * len(coverPool)):
                stubbornFlag = False
                easyMutants.append(mutant)
            
        if stubbornFlag:
            stubbornMutants.append(mutant)
    
    return stubbornMutants, easyMutants

# Given the tests that cover the mutants and the tests that kill the mutants, 
# identify the stubborn mutants (i.e. mutant that can be killed only if there is less than 50% killing tests over covering tests)
def getStubbornMutants(RSM : dict, maxRank : int, stubbornProbablity = 0.5):
    stubbornMutants = list()
    easyMutants = list()

    for mutant in RSM.keys():
        stubbornFlag = True
        
        if RSM[mutant] > (stubbornProbablity * maxRank):
            stubbornFlag = False
            easyMutants.append(mutant)
        
        if stubbornFlag:
            stubbornMutants.append(mutant)
    
    return stubbornMutants, easyMutants

# def getStubbornMutantsFixCap(mutContents, TSSize, stubbornProbablity = 0.05):
#     stubbornMutants = list()
#     easyMutants = list()

#     for mutant in RSM.keys():
#         stubbornFlag = True
        
#         if RSM[mutant] > (stubbornProbablity * maxRank):
#             stubbornFlag = False
#             easyMutants.append(mutant)
        
#         if stubbornFlag:
#             stubbornMutants.append(mutant)
    
#     return stubbornMutants, easyMutants

# Given the mutation csv, return a dictionary of mutants and killing tests, and the line numbers where mutants exist
def getKillableMutants(mutContents, TSSize, percentage = 1):
    mutants = list()
    killingTests = set()
    proportionOfMutants = TSSize*percentage
    
    # Get the header where all the mutants are written
    header = mutContents[0]
    tokens = re.split(',', header)

    for elem in tokens:
       
       # skip the first element of the header
       if elem.strip() == 'Class::Test':
            continue
                 
       # Find the index of the current mutant
       mutIndex = tokens.index(elem)

       # Get all tests that kill the current mutant
       tests = getCoveringTests(mutContents, mutIndex)

       if len(tests) > 0 and percentage == 1:
           #Add the mutants
           mutants.append(elem)
           killingTests.update(tests)
       elif len(tests) > 0 and len(tests) <= proportionOfMutants:
           mutants.append(elem)
           killingTests.update(tests)

        

    return mutants, killingTests

# Given all tests and the tests that kill the mutants, 
# identify the Rank-Stubborness Model (RSM) and the Weight-Stubborness Model (WSM)
# RSM/WSM is a map, where the test cases are the keys, and the values are the corresponding rank/weight of the mutants killed
def getRankAndWieghtedStubborness(killingTests : dict):
    maxRank = 0
    RSM = dict()        # RSM is the Rank-Stubborness Model
    WSM = dict()        # WSM is the Weight-Stubborness Model

    for mutant in killingTests.keys():
        killPool = killingTests[mutant]
        rank = len(killPool)
        if rank == 0:
            continue
        if rank > maxRank:
            maxRank = rank
        
        RSM[mutant] = rank
        WSM[mutant] = 1.0 / rank
    
    return RSM, WSM, maxRank


# Given all covering tests and a specific mutant, get the tests that cover it
def getCoveringTestsForMutant(coveringTests : dict, mutant: str):
    coverTests = list()

    # Extract the line number where the mutant is
    mutantlineNumber = re.split('::', mutant)[0].strip()

    for classline in coveringTests.keys():
        currentTests = coveringTests[classline]
        
        # Extract the line number of the current test
        testlineNumber = re.split(':', classline)[1]

        if testlineNumber == mutantlineNumber:
            coverTests = currentTests.copy()
            break
            
        
    return coverTests

# args = sys.argv
# if len(args) == 1:
#     project = "math"
#     id = "26"
#     testsType = "auto"
#     tool = "randoop"
# elif len(args) == 3:
#     project = args[1]
#     id = args[2]
#     testsType = ""
#     tool = ""
# else: 
#     project = args[1]
#     id = args[2]
#     testsType = args[3]
#     tool = args[4]

    # lastSlashPos = args[0].rfind('/')
    # secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
    # root = args[0][:secondToLastSlashPos]

    # if testsType == "auto":
    #     mutationFile = root + "/resources/mutation/" + project + "/" + testsType + "/" + tool + "/" + project + "." + id + "f.mutation." + tool + ".csv"
    #     coverageFile = root + "/resources/coverage/" + project + "/" + testsType + "/" + tool + "/" + project + "." + id + "f.statement.coverage." + tool + ".csv"
    # elif testsType == "dev":
    #     mutationFile = root + "/resources/mutation/" + project + "/" + testsType + "/" + project + "." + id + "f.mutation.dev.csv"
    #     coverageFile = root + "/resources/coverage/" + project + "/" + testsType + "/" + project + "." + id + "f.statement.coverage.dev.csv"
    # else:
    #     mutationFile = root + "/resources/mutation/" + project + "/" + project + "." + id + "f.mutation.csv"
    #     coverageFile = root + "/resources/coverage/" + project + "/" + project + "." + id + "f.statement.coverage.csv"

    # with open(mutationFile, "r") as f:
    #         mutContents = f.readlines()

    # with open(coverageFile, "r") as f:
    #         covContents = f.readlines()

    # killingTests, lineNumbers = getMutants(mutContents)

    # coveringTests = getTestsExecutingMutants(covContents, lineNumbers)

    # normalizedSetOfTests = normalizeTests(coveringTests)

    # print(killingTests)

# ra1, ra2, ra3, ra4, ra5 = runExp(root, project, id, 'randoop')