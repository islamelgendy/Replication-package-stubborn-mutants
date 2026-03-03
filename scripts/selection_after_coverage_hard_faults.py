from utils.Hybrid_selection import HybridSelection
from utils.Coverage_selection import CoverageSelection

from utils.Diversity_selection import DiversitySelection
from utils.CSVLoader import CSVLoader, evaluateMutationScore, getMatrixCoverage
from utils.Hybrid_selection_combined import CombinedHybridSelection
from utils.Hybrid_selection_separate import SeparateHybridSelection
import sys

from utils.testsCoveringMutants import *
from utils.utilsIO import *
from utils.utilsSystem import createFolder
import pickle

# Load the saved pickle file
def loadPickleFile(file):
    with open(file, "rb") as f:
        loaded_prioritization = pickle.load(f)

    return loaded_prioritization

# Load the saved method names
def loadMethodNames(file):
    methodDict = dict()
    with open(file, "r") as f:
        contents = f.readlines()
    
    for i in range(len(contents)):
        methodDict[i+1] = contents[i][:-1]

    return methodDict

def checkMethodKillingMutant(mutant:str, method: str, killingTests: dict):
    if not mutant in killingTests.keys():
        return False
    
    for mtd in killingTests[mutant]:
        if method == mtd.strip():
            return True
    
    return False

def computeStubbornScore(coveringTests, killingTests):
    scores = dict()

    for mutant in killingTests.keys():
        killPool = killingTests[mutant]

        # check that the mutant is in the coveringTests dict
        if len(killPool) == 0:
            continue
        # elif not mutant in coveringTests.keys():
        #     stubbornFlag = True
        else:
            coverPool = getCoveringTestsForMutant(coveringTests, mutant)
            scores[mutant] = len(killPool) / len(coverPool)

    return scores

# Get the number of mutants achieving a stubborness score up to curScore
def getNumberMutants(scores, curScore):
    count = 0

    for elem in scores.keys():
        if scores[elem] <= curScore:
            count += 1

    return count

# Get a list of the number of mutants for each 0.01 stubborness score
def computeStubbornGraph(scores):
    stubbornGraph = dict()

    curScore = 1
    while curScore > 0:
        stubbornGraph[curScore] = getNumberMutants(scores, curScore)
        curScore -= 0.01
        curScore = round(curScore, 2)

    return stubbornGraph
    # return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

def runExp(root, project, id, testType, stubbornScoreThreshold = 0.01):

    mutationFolder = root + "/resources/mutation/"
    mutationExt = 'mutation.csv'
    FASTfile = root + '/resources/FAST-replication/output/{}_v{}/prioritized/FAST-pw-bbox-1.pickle'.format(project, id)
    LedruTextfile = root + '/resources/Prioritisation/{}_v{}/testDiv.pickle'.format(project, id)
    LedruBytecodefile = root + '/resources/Prioritisation/{}_v{}/bytecodeDiv.pickle'.format(project, id)
    maxCovfile = root + '/resources/Prioritisation/{}_v{}/maxCoverage.pickle'.format(project, id)
    minCovfile = root + '/resources/Prioritisation/{}_v{}/minCoverage.pickle'.format(project, id)
    methodNamesFile = root + f'/resources/FAST-replication/input/{project}_v{id}/{project}-keys.txt'
    FASTfileBytecode = root + '/resources/FAST-replication/output/{}_v{}/prioritized/FAST-pw-bbox-1-bytecode.pickle'.format(project, id)
    methodNamesFileBytecode = root + f'/resources/FAST-replication/input/{project}_v{id}/{project}-keys-bytecode.txt'
    realfaultFolder = root + "/resources/realfault/" + project + "/"
    realfaultExt = "realfaults-detected.csv"
    
    # Load the mutation file into CSVLoader obj
    try:
        mutationFile = filterFiles(mutationFolder, project + '.' + id + 'f', mutationExt)[0]
        # mutationCSV = CSVLoader(mutationFile)
    except:
        print('Mutation file can NOT be loaded')

    # Load the coverage files into CSVLoader obj
    # try:
    #     statementCoverageFile = filterFiles(coverageFolder, project + '.' + id + 'f', coverageExt)[0]
    #     statementCSV = CSVLoader(statementCoverageFile) 
    # except:
    #     print('Statement coverage files can NOT be loaded')

    # Load the coverage priotization
    try:
        maxCovlist = loadPickleFile(maxCovfile)
        minCovlist = loadPickleFile(minCovfile)
    except:
        print('Similarity bytecode matrix can NOT be loaded')
     
    # Load the Ledru priotization
    try:
        LedruTextlist = loadPickleFile(LedruTextfile)
        LedruBytecodelist = loadPickleFile(LedruBytecodefile)
    except:
        print('Similarity bytecode matrix can NOT be loaded')

    # Load the FAST priotization
    try:
        FASTlist = loadPickleFile(FASTfile)
        FASTlistBytecode = loadPickleFile(FASTfileBytecode)

        # Load the keys (method names)
        methodNames = loadMethodNames(methodNamesFile)
        methodNamesBytecode = loadMethodNames(methodNamesFileBytecode)
    except:
        print('FAST files can NOT be loaded')

    # Load the real-faults files into fault_tests list
    try:
        realfaultFile = filterFiles(realfaultFolder, project + '.' + id + 'f', realfaultExt)[0]
        fault_tests = processRealFaultFile(realfaultFile)

    except:
        print('Real-fault files can NOT be loaded')

    print('A number of ', len(fault_tests), ' tests can kill the real fault.')

    mutContents = readFile(mutationFile)

   
    killingTests, lineNumbers = getMutants(mutContents)


    # calculate the original statement coverage
    # totalStatementCoverage = statementCSV.getTotalCoverage()

    # calculate the original mutation score 
    # MS = mutationCSV.getTotalCoverage()

    # print('statement coverage ', totalStatementCoverage)
    # print('mutation score ', MS)

    RSM, WSM, maxRank = getRankAndWieghtedStubborness(killingTests)
    stubbornMutants, easyMutants = getStubbornMutants(RSM, maxRank, stubbornScoreThreshold)

    print('A number of ', len(stubbornMutants), ' stubborn mutants are still alive.')

    # For each hard fault, perform selection using the pool of tests that execute that mutant
    bytecodeOrders = list()
    bytecodeBytOrders = list()
    maxcoverageOrders = list()
    maxcoverageAdditionalOrders = list()
    mincoverageOrders = list()
    diversityOrders = list()
    FASTOrders = list()
    FASTBytOrders = list()

    bytecodeRanks = list()
    bytecodeBytRanks = list()
    maxcoverageRanks = list()
    maxcoverageAdditionalRanks = list()
    mincoverageRanks = list()
    diversityRanks = list()
    FASTRanks = list()
    FASTBytRanks = list()

    THRESHOLD = maxRank * stubbornScoreThreshold       # the upper boundary of killing tests

    # the number of tests killing the real fault should be less than threshold to be considered a hard fault
    if len(fault_tests) < THRESHOLD:

        # race list: who detects the real fault first
        raceWithRank = dict()
        raceWithIndex = dict()
        raceIndex = 1
        # `order` is the value of which selection method managed to kill the mutant first. The higher the value the faster it killed the mutant
        order = 6 # There are 5 selection methods

        # randomObj = CoverageSelection(statementCSV, None, pool)   
        
        noIterations = min(len(maxCovlist), len(LedruTextlist))
        
        # The ind is the index of the FAST list
        ind = 0

        # while combinedhybridObject.coverage < totalStatementCoverage or coverageObj.coverage < totalStatementCoverage:
        while raceIndex <= noIterations and len(raceWithRank) < 9:
            killFlag = 0

            if not 'FAST-Text' in raceWithRank.keys():
                FASTMethod = methodNames[ FASTlist[ind] ]
                if FASTMethod in fault_tests:
                    killFlag += 1
                    raceWithRank['FAST-Text'] = order
                    raceWithIndex['FAST-Text'] = raceIndex
                    FASTOrders.append(raceIndex)
                    FASTRanks.append(order)
            
            if not 'FAST-Bytecode' in raceWithRank.keys():
                FASTBytecodeMethod = methodNamesBytecode[ FASTlistBytecode[ind] ]
                if FASTBytecodeMethod in fault_tests:
                    killFlag += 1
                    raceWithRank['FAST-Bytecode'] = order
                    raceWithIndex['FAST-Bytecode'] = raceIndex
                    FASTBytOrders.append(raceIndex)
                    FASTBytRanks.append(order)

            if not 'bytecodeByt' in raceWithRank.keys():
                bytecodeBytMethod = LedruBytecodelist[ind]
                if bytecodeBytMethod in fault_tests:
                    killFlag += 1
                    raceWithRank['bytecodeByt'] = order
                    raceWithIndex['bytecodeByt'] = raceIndex
                    bytecodeBytOrders.append(raceIndex)
                    bytecodeBytRanks.append(order)
            
            if not 'maxcoverage' in raceWithRank.keys():
                maxcoverageMethod = maxCovlist[ind]
                if maxcoverageMethod in fault_tests:
                    killFlag += 1
                    raceWithRank['maxcoverage'] = order
                    raceWithIndex['maxcoverage'] = raceIndex
                    maxcoverageOrders.append(raceIndex)
                    maxcoverageRanks.append(order)
            
            if not 'mincoverage' in raceWithRank.keys():
                mincoverageMethod = minCovlist[ind]
                if mincoverageMethod in fault_tests:
                    killFlag += 1
                    raceWithRank['mincoverage'] = order
                    raceWithIndex['mincoverage'] = raceIndex
                    mincoverageOrders.append(raceIndex)
                    mincoverageRanks.append(order)
            
            if not 'diversity' in raceWithRank.keys():
                diversityMethod = LedruTextlist[ind]
                if diversityMethod in fault_tests:
                    killFlag += 1
                    raceWithRank['diversity'] = order
                    raceWithIndex['diversity'] = raceIndex
                    diversityOrders.append(raceIndex)
                    diversityRanks.append(order)
            
            order -= killFlag

            raceIndex += 1
            ind += 1
        
        # TODO: Change this into new files for hard faults
        createFolder(root + '/PlotGeneration/hardfaults/' + project + '/score' + str(stubbornScoreThreshold))
        plotFile = root + '/PlotGeneration/hardfaults/' + project + '/score' + str(stubbornScoreThreshold) + '/' + project + id + testType + '.py'
        rankplotFile = root + '/PlotGeneration/hardfaults/' + project + '/score' + str(stubbornScoreThreshold) + '/' + project + id + testType + '-rank.py'
        dstPlot = root + '/resources/plots/after-coverage/hardfaults/' + project + '/score' + str(stubbornScoreThreshold)

        createFolder(dstPlot)
        
        # plotFile = './matplots/' + project + id + testType + '.py'
        writeStubbornMutantsPlots(project, id, testType, FASTOrders, FASTBytOrders, bytecodeOrders, bytecodeBytOrders,
                maxcoverageOrders, maxcoverageAdditionalOrders, mincoverageOrders, diversityOrders, plotFile, dstPlot)
        writeStubbornMutantsPlots(project, id, testType, FASTRanks, FASTBytRanks, bytecodeRanks, bytecodeBytRanks,
                maxcoverageRanks, maxcoverageAdditionalRanks, mincoverageRanks, diversityRanks, rankplotFile, dstPlot, True)
    
    # Put all lists into one collection to return it at the end
    listrestuls = list()
    # listrestuls.append(orginalOrders)
    # listrestuls.append(randomOrders)
    listrestuls.append(FASTOrders)
    listrestuls.append(bytecodeOrders)
    listrestuls.append(maxcoverageOrders)
    # listrestuls.append(maxcoverageAdditionalOrders)
    listrestuls.append(mincoverageOrders)
    listrestuls.append(diversityOrders)
    listrestuls.append(FASTBytOrders)
    listrestuls.append(bytecodeBytOrders)

    # listrestuls.append(orginalRanks)
    # listrestuls.append(randomRanks)
    listrestuls.append(FASTRanks)
    listrestuls.append(bytecodeRanks)
    listrestuls.append(maxcoverageRanks)
    # listrestuls.append(maxcoverageAdditionalRanks)
    listrestuls.append(mincoverageRanks)
    listrestuls.append(diversityRanks)
    listrestuls.append(FASTBytRanks)
    listrestuls.append(bytecodeBytRanks)
    
    return listrestuls

def updateList(allscores, scores):
    index = 0
    while index < 100:
        allscores[index] += scores[index]
        index += 1

def getCSVHeader():
    return 'Version, St Cov, MS, Easy mutants, Stubbron mutants, Live mutants \n'

def getCSVRecord(id, cov, ms, easyMut, stubbornMut, liveMutants):
    return str(id) + ', ' + str(cov) + ', ' + str(ms) + ', ' + str(easyMut) + ', ' + str(stubbornMut) + ', ' + str(liveMutants) + '\n '
# runExp('math', '23', 'randoop')

args = sys.argv
if len(args) == 1:
    prj = "time"

    stubbornScoreThresholdValues = [0.001, 0.002, 0.003, 0.005, 0.01, 0.02, 0.03, 0.05, 0.1, 0.15, 0.25, 0.5, 0.75]
elif len(args) == 2:
    prj = args[1]
    stubbornScoreThresholdValues = [0.75, 0.5, 0.25, 0.15, 0.1, 0.05, 0.03, 0.02, 0.01, 0.005, 0.003, 0.002, 0.001]
elif len(args) == 3:
    prj = args[1]
    stbValue = float(args[2])
    stubbornScoreThresholdValues = [stbValue]
else: 
    print('Wrong number of arugments passed')
    exit()

print(args)
lastSlashPos = args[0].rfind('/')
secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
root = args[0][:secondToLastSlashPos]


if prj == 'math':
    projects = ['4', '5', '6', '9', '13', '14', '17', '18', '19',
                '20', '21', '23', '24', '25', '26', '27', '28', 
                '30', '32', '33', '37', '42', '47', '49', '50', 
                '51', '52', '54', '56', '58', '61', '64', '65', 
                '67', '68', '69', '70', '73', '78', '76', '80', '81']
    # projects = ['4', '5', '6', '9', '13', '14', '18', '17', '19',
    #             '20', '21', '23', '24', '25', '26', '27', '28', 
    #             '30', '32', '33', '37', '42', '47', '49', '50', 
    #             '51', '52', '54', '56', '58', '64', '65', 
    #             '67', '68', '69', '70', '73', '78', '76', '80', '81']   # Developer

# jsoup projects:
# prj = 'jsoup'
elif prj == 'jsoup':
    projects = [ '4', '15', '16', '19', '20', '26', '27', '29', 
                '30', '33', '35', '36', '37', '38', '39', '40']

# lang projects:
# prj = 'lang'
elif prj == 'lang':
    projects = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33', '35']
    # projects = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33']  #Evosuite

# time projects:
# prj = 'time'
elif prj == 'time':
    projects = ['11','13']

# cli projects:
# prj = 'cli'
elif prj == 'cli':
    projects = ['30','31','32','33','34']

# csv projects:
# prj = 'csv'
elif prj == 'csv':
    projects = ['2', '3', '4', '5', '7', '8', '10', '11', '12', '16']

# compress projects:
# prj = 'compress'
elif prj == 'compress':
    projects = ['1', '11', '16', '22', '24', '26', '27']


for stubbornScoreThreshold in stubbornScoreThresholdValues:
    print('Current stubborness: ' + str(stubbornScoreThreshold*100) + '%')

    # allorginalOrders = list()
    # allrandomOrders = list()
    allcombinedOrders = list()
    allhybridOrders = list()
    # allseparateOrders = list()
    allbytecodeOrders = list()
    allbytecodeBytOrders = list()
    allmaxcoverageOrders = list()
    allmaxcoverageAdditionalOrders = list()
    allmincoverageOrders = list()
    alldiversityOrders = list()
    allFASTOrders = list()
    allFASTBytOrders = list()

    # allorginalRanks = list()
    # allrandomRanks = list()
    allcombinedRanks = list()
    allhybridRanks = list()
    # allseparateRanks = list()
    allbytecodeRanks = list()
    allbytecodeBytRanks = list()
    allmaxcoverageRanks = list()
    allmaxcoverageAdditionalRanks = list()
    allmincoverageRanks = list()
    alldiversityRanks = list()
    allFASTRanks = list()
    allFASTBytRanks = list()

    allscores = list()

    for id in projects:
        # try:
            print('Running Project ' + str(id) + '...')
            listrestuls = runExp(root, prj, id, 'all', stubbornScoreThreshold)
       
            # allorginalOrders.extend(listrestuls[0])
            # allrandomOrders.extend(listrestuls[1])
            allFASTOrders.extend(listrestuls[0])
            allbytecodeOrders.extend(listrestuls[1])
            allmaxcoverageOrders.extend(listrestuls[2])
            # allmaxcoverageAdditionalOrders.extend(listrestuls[4])
            allmincoverageOrders.extend(listrestuls[3])
            alldiversityOrders.extend(listrestuls[4])
            allFASTBytOrders.extend(listrestuls[5])
            allbytecodeBytOrders.extend(listrestuls[6])

            # allorginalRanks.extend(listrestuls[9])
            allFASTRanks.extend(listrestuls[7])
            allbytecodeRanks.extend(listrestuls[8])
            allmaxcoverageRanks.extend(listrestuls[9])
            # allmaxcoverageAdditionalRanks.extend(listrestuls[13])
            allmincoverageRanks.extend(listrestuls[10])
            alldiversityRanks.extend(listrestuls[11])
            allFASTBytRanks.extend(listrestuls[12])
            allbytecodeBytRanks.extend(listrestuls[13])

        # except:
        #     print('Project ' + str(id) + ' failed to run properly')

 
    if len(allFASTOrders) > 0:
        plotFile = root + '/PlotGeneration/hardfaults/' + prj + '-scores-graph.py'
        dstPlot = root + '/resources/plots/after-coverage/hardfaults'

        createFolder(root + '/PlotGeneration/hardfaults/' + prj + '/score' + str(stubbornScoreThreshold))
        plotFile = root + '/PlotGeneration/hardfaults/' + prj + '/score' + str(stubbornScoreThreshold) + '/' + prj + '-all.py'
        plotRankFile = root + '/PlotGeneration/hardfaults/' + prj + '/score' + str(stubbornScoreThreshold) + '/' + prj + '-rank-all.py'

        dstPlot = root + '/resources/plots/after-coverage/hardfaults/' + prj + '/score' + str(stubbornScoreThreshold)
        csvFile = root + '/resources/plots/after-coverage/hardfaults/' + prj + '/score' + str(stubbornScoreThreshold) + prj + '-report.csv'
        createFolder(dstPlot)

        
        # writeFile(csvFile, csvContents)
        writeStubbornMutantsPlots(prj, '', '', allFASTOrders, allFASTBytOrders, allbytecodeOrders, allbytecodeBytOrders,
                    allmaxcoverageOrders, allmaxcoverageAdditionalOrders, allmincoverageOrders, alldiversityOrders, plotFile, dstPlot)
        writeStubbornMutantsPlots(prj, '', '', allFASTRanks, allFASTBytRanks, allbytecodeRanks, allbytecodeBytRanks,
                    allmaxcoverageRanks, allmaxcoverageAdditionalRanks, allmincoverageRanks, alldiversityRanks, plotRankFile, dstPlot, True)
    
# Example to run from terminal:
# python3 /home/islam/MyWork/New-work-2023/DBT-workbench/scripts/selection_after_coverage_stubborn_mutants.py time False Branch 0.001

# Example to run from HPC:
# bash /data/islam/DBT-workbench/scripts/bash/hpc-job-stubborn-selection.sh compress False Branch 0.75 0.5 0.25 0.15 0.1 0.05 0.03 0.02 0.01 0.005 0.003 0.002 0.001