#!/usr/bin/python3

import os
import pickle
import re
import shutil

from utils.CoverageLineInfo import CSV_HTML


def readFile(file):
    with open(file, "r") as f:
        contents = f.readlines()
    
    return contents

def writeFile(file, contents):
    with open(file, "w") as f:
        contents = "".join(contents)
        f.write(contents)

def appendToFile(file, line):
    with open(file, "a") as f:
        f.write(line)

#  Save a data structure as a pickle file
def saveDataStructure(data, file):
    with open(file, 'wb') as file:
        pickle.dump(data, file)

# Load the data structure from the pickle file 
def loadDataStructure(file):
    with open(file, 'rb') as file:
        loaded_data = pickle.load(file)
    
    return loaded_data

def getAllFilesEndingWith(folder, ext):
    # Loop through all files in the directory of the project and store the compressed files in a list
    allFiles = [os.path.join(root, name)
             for root, dirs, files in os.walk(folder)
                 for name in files
                    if name.endswith((ext))]
    
    return allFiles

def getExactFile(folder, file, classSig):
    # Loop through all files in the directory of the project and store the compressed files in a list
    allFiles = [os.path.join(root, name)
             for root, dirs, files in os.walk(folder)
                 for name in files
                    if name == (file)]
    
    # if more than one file has the same name, use the class signature to identify the correct file
    if len(allFiles)>1:
        tokens = re.split('\\.', classSig)
        for file in allFiles:
            flag = True
            fileparts = re.split('[/\\.]', file)
            for elem in tokens:
                if not elem in fileparts:
                    flag = False
                    break
            if flag:
                return file
    return allFiles[0]

def filterFiles(folder, prefix, postfix):
    # Loop through all files in the directory of the project and store the compressed files in a list
    allFiles = [os.path.join(root, name)
             for root, dirs, files in os.walk(folder)
                 for name in files
                    if name.endswith(postfix) and name.startswith(prefix)]
    
    return allFiles

def extractInfo(file):
    # Get file name
    filename = os.path.basename(file)

    list = re.split('-',filename)

    # Extract project id
    pid = list[0]

    # Extract version number
    vid = list[1][0:len(list[1])-1]

    # Extract the tool
    tool = re.split('\\.', list[2])[0]

    return pid,vid,tool

def getFolder(packageLines):
    folderList = set()
    signatures = set()

    for packageLine in packageLines:
        # Remove the starting package word of the line
        packageLine = packageLine[8:]

        # Remove the semicolon of the line
        semiColonPos = packageLine.find(';')
        packageLine = packageLine[0:semiColonPos]

        # Split the packageLine to get the right folder
        folders = re.split('\\.', packageLine)

        # Build the path of the folder
        folder='/'
        for dir in folders:
            folder+=dir+'/'

        folderList.add(folder)
        signatures.add(packageLine)

    return folderList, signatures

def getFile(path, packageLine, classname, ext):
    # Split the packageLine to get the right folder
    folders = re.split('\\.', packageLine)

    # Build the path of the folder
    folder='/'
    for dir in folders:
        folder+=dir+'/'

    return path + folder + classname + '.' + ext

def processRealFaultFile(realfaultFile):
    fault_tests = list()
    with open(realfaultFile, "r") as f:
            realfaultContents = f.readlines()

    for line in realfaultContents:
        if line.startswith('Method,Fault-Detected'):
            continue
        tokens = re.split(',', line)
        fault_tests.append(tokens[0].strip())
    
    return fault_tests
# def getClassSignature(classFilename):

#     # Remove the java extention position
#     extentionPos = classFilename.find('.java')
#     classFilename = classFilename[0:extentionPos]

#     # Split the packageLine to get the right folder
#     folders = re.split('/', classFilename)

#     # Build the path of the folder
#     signature=''
#     for dir in folders:
#         signature+=dir+'.'

#     return signature[0:len(signature)-1]

def copyFiles(javaFiles, dst, tool):

    try:
        if tool == "randoop":
            for file in javaFiles:
                shutil.copy(file, next(iter(dst)))
        elif tool == "evosuite":
            for file in javaFiles:
                # Copy only the test classes, not the scaffolding classes
                if not file.endswith("_scaffolding.java"):
                    processEvoSuiteTestClass(file)
                    target = getProperTargetPath(file, dst)
                    shutil.copy(file, target)
        return True
    except:
        return False
    
def copyIntoFixedVersion(javaFiles, dst, tool):

    try:
        if tool == "randoop":
            for file in javaFiles:
                shutil.copy(file, next(iter(dst)))
        elif tool == "evosuite":
            for file in javaFiles:
                # Copy only the test classes, not the scaffolding classes
                if not file.endswith("_scaffolding.java"):
                    processEvoSuiteTestClass(file)
                    target = getProperTargetPath(file, dst)
                    shutil.copy(file, target)
        return True
    except:
        return False

# Read the contents of the file and delete the scaffolding superclass
def processEvoSuiteTestClass(evosuiteFile):
    
    contents = readFile(evosuiteFile)
    
    # Search the contents for the class defintion
    for i, x in enumerate(contents):
        if "@RunWith(EvoRunner.class)" in x:
            del contents[i]
        if "public class" in contents[i] and "extends" in contents[i]:
            line = contents[i]
            pos = line.find("extends")
            # Delete from the position of the "extends" keyword
            contents[i] = line[0:pos] + '{'
            break

    writeFile(evosuiteFile, contents)
    
# Read the contents of the statement coverage and fix the naming of the methods
def processSimFileFromStatmentFile(simFile, statementFile):
    
    contentsStatments = readFile(statementFile)
    
    contentsSimilarity = readFile(simFile)

    methods = list()

    # Extract the class method name pair from the statement coverage file
    for i, x in enumerate(contentsStatments):
        if i==0:
            continue
        classMethodPair = re.split(',', contentsStatments[i])[0]
        methods.append(classMethodPair)

    # Extract the class method name pair from the statement coverage file
    for i, x in enumerate(contentsSimilarity):
        if i==0:
            line = 'Class::Test ,'
            for mtd in methods:
                line += mtd + ' ,'
            contentsSimilarity[i] = line[0:len(line)-1] +'\n'
        else:
            tokens = re.split(',', contentsSimilarity[i])
            line = methods[i-1] + ' ,'
            first = True
            for elem in tokens:
                if first:
                    first = False
                    continue
                line += elem + ' ,'
            contentsSimilarity[i] = line[0:len(line)-1]

    writeFile(simFile, contentsSimilarity)
    
def getProperTargetPath(file, dst):

    # initially the target is the first path
    target = next(iter(dst))

    # get rid of the file name and keep the path
    file = os.path.dirname(file)
    fileTokens = re.split('/', file)
    
    # Find which path in the list of dst that matches the file best
    for path in dst:
        # if path ending with / remove it
        if path.endswith('/'):
            pathTokens = re.split('/', path[0:len(path)-1])
        else:
            pathTokens = re.split('/', path)

        # compare the last 4 elements of both tokens, and if they match, that is the proper target
        if fileTokens[-1] == pathTokens[-1]:
            if len(fileTokens) > 1 and len(pathTokens) > 1:
                if fileTokens[-2] == pathTokens[-2]:
                    if len(fileTokens) > 2 and len(pathTokens) > 2:
                        if fileTokens[-3] == pathTokens[-3]:
                            if len(fileTokens) > 3 and len(pathTokens) > 3:
                                if fileTokens[-4] == pathTokens[-4]:
                                    target = path
                                else:
                                    continue
                            else:
                                target = path
                        else:
                             continue
                    else:
                        target = path
                else:
                     continue
            else:
                target = path
            break
    
    return target

def deleteFolders(folder):
    listdir = os.listdir(folder)
    for item in listdir:
        path = folder+'/'+item
        if os.path.isdir(path):
            shutil.rmtree(path)

def deleteEntireFolder(folder):
    shutil.rmtree(folder)

# Read the contents of the PIT mutation outputfile and get if there are any errors
def processMutationOutput(folder, mutationOutputFile):
    contents = readFile(mutationOutputFile)

    # Search the contents for the class defintion
    for i, x in enumerate(contents):
        if 'BUILD FAILURE' in x:
            return False
    
    return True

# Read the contents of the Maven outputfile and get if there are any errors
def processMavenOutput(outputfile):
    
    contents = readFile(outputfile)

    # Search the contents for the class defintion
    for i, x in enumerate(contents):
        if x.startswith('Tests run: '):
            # Split the packageLine to get the right folder
            tokens = re.split(',', x)
            fails = re.split(':',tokens[1])[1].strip()
            errors = re.split(':',tokens[2])[1].strip()
            return int(fails), int(errors)
        
    return 0, 0

# Copy the EvoSuite test files from fixed version to the corrosponding buggy version
def copyEvoSuiteTestFiles(root, project, version):
    fixedPath = root + 'resources/subjects/fixed/' + project + '/' + version + '/src/test/'
    buggyRootPath = root + 'resources/subjects/buggy/' + project + '/' + version 
    evosuiteFiles = getAllFilesEndingWith(fixedPath, '_ESTest.java')
    for file in evosuiteFiles:
        lastslashpos = file.rindex('/')
        filePath = file[:lastslashpos]
        buggyPath = filePath.replace("/fixed/", "/buggy/")
        if os.path.isdir(buggyPath):
            shutil.copy(file, buggyPath)
    
    return buggyRootPath

# Read the contents of the Maven output file, and parse the failed tests (if any)
def processMavenOutputAndParseFailedMethods(outputfile):
    startError = -1
    endError = -1
    startFail = -1
    endFail = -1

    failingMethods = list()
    failLines = []
    errorLines = []

    contents = readFile(outputfile)

    # Search the contents for the class defintion
    for i, x in enumerate(contents):
        if x.startswith('Failed tests: '):
            startFail = i
        if x.startswith('Tests in error:'):
            endFail = i
            startError = i
        if x.startswith('Tests run: '):
            endError = i
            if startError == -1:
                endFail = i
    
    if startFail > -1 and endFail > -1:
        # There are some tests causing failures
        failLines = contents[startFail:endFail]

    if startError > -1 and endError > -1:
        # There are some tests causing errors
        errorLines = contents[startError+1:endError]

    # Start parsing the lines and add to the failingMethods list
    for failLine in failLines:
        if failLine.strip() == '':
            continue
        mtd = parseErrorLine(failLine)
        if mtd.strip() == 'Failed tests:::' or mtd.strip() == '::':
            continue
        failingMethods.append(mtd)
    for errorLine in errorLines:
        if errorLine.strip() == '':
            continue
        mtd = parseErrorLine(errorLine)
        failingMethods.append(mtd)
        
    return failingMethods

def parseErrorLine(line:str):
    methodName = ''
    className = ''

    # find pos of the first (
    openBrace = line.find('(')
    # find pos of the first )
    closeBrace = line.find(')')

    #Check if this is the special case of a failed test at the first line
    if line.startswith('Failed tests:'):
        colonPos = line.find(':')
        methodName = line[colonPos+1:openBrace].strip()
        # find pos of the last dot before the className
        dotPos = line[:closeBrace].rfind('.')
        className = line[dotPos+1:closeBrace].strip()
    else:
        if openBrace == -1 or closeBrace == -1:
            # find first :
            colonPos = line.find(':')
            dotPos = line.find('.')
            className = line[:dotPos].strip()
            methodName = line[dotPos+1:colonPos]
        else:
            methodName = line[:openBrace].strip()
            # find pos of the last dot before the className
            dotPos = line[:closeBrace].rfind('.')
            className = line[dotPos+1:closeBrace].strip()
            

    return className + '::' + methodName

def getPackageLines(testFiles):
    
    packageLines = set()
    for testFile in testFiles:
        contents = readFile(testFile)

        # Search the contents for the class defintion
        for i, x in enumerate(contents):
            if x.startswith('package '):
                packageLines.add(x)
                break

    return packageLines

def writeBoxPlotsAPFD(plotFile, dstPlot, combined_values, coverage_values, diversity_values, bytecode_values, coverageAdditional_values, hybrid_values, bytecodeByt_values, APFD=True):
    contents = list()

    contents.append( 'import numpy as np\n' )
    contents.append( 'import matplotlib.pyplot as plt\n' )
    contents.append( 'import sys\n' )
    contents.append( 'from pylab import plot, show, savefig, xlim, figure, ylim, legend, boxplot, setp, axes\n' )
    contents.append( '\n' )
    contents.append( 'plt.style.use(\'ggplot\')\n' )
    contents.append( '\n' )
    contents.append( '#Dataset\n' )
    contents.append( 'combined = ' + str(combined_values) +  '\n' )
    contents.append( 'hybrid = ' + str(hybrid_values) +  '\n' )
    contents.append( 'coverage = ' + str(coverage_values) +  '\n' )
    contents.append( 'diversity = ' + str(diversity_values) +  '\n' )
    contents.append( 'bytecode = ' + str(bytecode_values) +  '\n' )
    contents.append( 'coverageAdditional = ' + str(coverageAdditional_values) +  '\n' )
    contents.append( 'bytecode_bytes = ' + str(coverageAdditional_values) +  '\n' )
    contents.append( '\n' )
    contents.append( 'dev = [combined, coverage, coverageAdditional, diversity, bytecode, bytecode_bytes, hybrid]\n' )
    contents.append( '\n' )
    contents.append( 'fig, ax = plt.subplots()\n' )
    contents.append( 'fig.set_size_inches(11.5, 8)\n' )
    contents.append( '\n' )
    contents.append( 'bp1 = ax.boxplot(dev, positions=[1, 2, 3, 4, 5, 6, 7], widths=0.35, patch_artist=True, boxprops=dict(facecolor="cyan"))\n' )
    contents.append( '\n' )
    
    contents.append( 'plt.xticks([1, 2, 3, 4, 5, 6, 7], [\'combined\', \'coverageTot\', \'coverageAdd\', \'diversity\', \'bytecode\', \'bytecodeByt\', \'hybrid\'], fontsize = 16, rotation = 45)\n' )
    contents.append( '\n' )
    contents.append( 'plt.subplots_adjust(bottom = 0.2, top = 0.95, right = 0.95)\n' )
    if APFD:
        contents.append( 'ax.set_ylabel(\'APFD\', fontsize = 16)\n' )
        contents.append( 'ax.set_ylim(50,110)\n' )
        contents.append( 'show()\n' )
        contents.append( 'fig.savefig(\'' + dstPlot + '-APFD.pdf\', dpi=100)\n' )
    else:
        contents.append( 'ax.set_ylabel(\'First test to detect real fault\', fontsize = 16)\n' )
        contents.append( 'show()\n' )
        contents.append( 'fig.savefig(\'' + dstPlot + '-realfault.pdf\', dpi=100)\n' )

    writeFile(plotFile, contents)

def writeBoxPlotsAPFDDevRandoop(plotFile, dstPlot, dev_combinedAPFD, dev_coverageAPFD, dev_diversityAPFD, dev_bytecodeAPFD, dev_randomAPFD,
                      randoop_combinedAPFD, randoop_coverageAPFD, randoop_diversityAPFD, randoop_bytecodeAPFD, randoop_randomAPFD):
    contents = list()

    contents.append( 'import numpy as np\n' )
    contents.append( 'import matplotlib.pyplot as plt\n' )
    contents.append( 'import sys\n' )
    contents.append( 'from pylab import plot, show, savefig, xlim, figure, ylim, legend, boxplot, setp, axes\n' )
    contents.append( '\n' )
    contents.append( 'plt.style.use(\'ggplot\')\n' )
    contents.append( '\n' )
    contents.append( '#Dev APFD\n' )
    contents.append( 'dev_combined = ' + str(dev_combinedAPFD) +  '\n' )
    contents.append( 'dev_coverage = ' + str(dev_coverageAPFD) +  '\n' )
    contents.append( 'dev_diversity = ' + str(dev_diversityAPFD) +  '\n' )
    contents.append( 'dev_bytecode = ' + str(dev_bytecodeAPFD) +  '\n' )
    contents.append( 'dev_random = ' + str(dev_randomAPFD) +  '\n' )
    contents.append( '\n' )
    contents.append( '#Randoop APFD\n' )
    contents.append( 'randoop_combined = ' + str(randoop_combinedAPFD) +  '\n' )
    contents.append( 'randoop_coverage = ' + str(randoop_coverageAPFD) +  '\n' )
    contents.append( 'randoop_diversity = ' + str(randoop_diversityAPFD) +  '\n' )
    contents.append( 'randoop_bytecode = ' + str(randoop_bytecodeAPFD) +  '\n' )
    contents.append( 'randoop_random = ' + str(randoop_randomAPFD) +  '\n' )
    contents.append( '\n' )
    contents.append( 'dev = [dev_combined, dev_coverage, dev_diversity, dev_bytecode, dev_random]\n' )
    contents.append( 'randoop = [randoop_combined, randoop_coverage, randoop_diversity, randoop_bytecode, randoop_random]\n' )
    contents.append( '\n' )
    contents.append( 'fig, ax = plt.subplots()\n' )
    contents.append( 'fig.set_size_inches(11.5, 8)\n' )
    contents.append( '\n' )
    contents.append( 'bp1 = ax.boxplot(dev, positions=[0.8, 1.8, 2.8, 3.8, 4.8], widths=0.35, patch_artist=True, boxprops=dict(facecolor="cyan"))\n' )
    contents.append( 'bp2 = ax.boxplot(randoop, positions=[1.2, 2.2, 3.2, 4.2, 5.2], widths=0.35, patch_artist=True, boxprops=dict(facecolor="red"))\n' )
    contents.append( '\n' )
    contents.append( 'ax.set_ylabel(\'APFD\', fontsize = 16)\n' )
    contents.append( 'plt.xticks([1, 2, 3, 4, 5], [\'combined\', \'coverage\', \'diversity\', \'bytecode\', \'random\'], fontsize = 16, rotation = 45)\n' )
    contents.append( 'ax.legend([bp1["boxes"][0], bp2["boxes"][0]], [\'dev\', \'Randoop\'], fontsize = 13, loc = \'lower right\')\n' )
    contents.append( '\n' )
    contents.append( 'ax.set_ylim(50,110)\n' )
    contents.append( 'plt.subplots_adjust(bottom = 0.2, top = 0.95, right = 0.95)\n' )
    contents.append( 'show()\n' )
    contents.append( 'fig.savefig(\'' + dstPlot + '-APFD.pdf\', dpi=100)\n' )

    writeFile(plotFile, contents)

def writePlots(project, id, testType, combined_hybrid_values, coverage_values, diversity_values, bytecode_values,
               coverage_additional_values, hybrid_values, bytecodeByt_values, APFD1, APFD2, APFD3, APFD4, APFD5, APFD6, APFD7, race, plotFile, dst):
    contents = list()

    contents.append( 'import matplotlib.pyplot as plt\n' )
    contents.append( 'import numpy as np\n' )
    contents.append( 'from scipy.interpolate import make_interp_spline\n\n' )
    contents.append( '# Dataset\n' )
    contents.append( 'combined_hybrid_values = np.array(' + str(combined_hybrid_values) +  ')\n' )
    contents.append( 'hybrid_values = np.array(' + str(hybrid_values) +  ')\n' )
    contents.append( 'coverage_values = np.array(' + str(coverage_values) +  ')\n' )
    contents.append( 'diversity_values = np.array(' + str(diversity_values) +  ')\n' )
    contents.append( 'bytecode_values = np.array(' + str(bytecode_values) +  ')\n' )
    contents.append( 'bytecodeByt_values = np.array(' + str(bytecodeByt_values) +  ')\n' )
    contents.append( 'coverage_additional_values = np.array(' + str(coverage_additional_values) +  ')\n\n' )
    contents.append( '# Get the x-axis and smooth the plots\n' )
    contents.append( 'x_axis = np.array(range(len(combined_hybrid_values)))\n' )
    contents.append( 'combined_hybrid_Spline = make_interp_spline(x_axis, combined_hybrid_values)\n' )
    contents.append( 'hybrid_Spline = make_interp_spline(x_axis, hybrid_values)\n' )
    contents.append( 'coverage_Spline = make_interp_spline(x_axis, coverage_values)\n' )
    contents.append( 'diversity_Spline = make_interp_spline(x_axis, diversity_values)\n' )
    contents.append( 'bytecode_Spline = make_interp_spline(x_axis, bytecode_values)\n' )
    contents.append( 'bytecodeByt_Spline = make_interp_spline(x_axis, bytecodeByt_values)\n' )
    contents.append( 'coverage_additional_Spline = make_interp_spline(x_axis, coverage_additional_values)\n\n' )
    contents.append( '# Returns evenly spaced numbers over the interval\n' )
    contents.append( 'X_ = np.linspace(x_axis.min(), x_axis.max(), len(combined_hybrid_values))\n' )
    contents.append( 'Y_hybridCombined = combined_hybrid_Spline(X_)\n' )
    contents.append( 'Y_hybrid = hybrid_Spline(X_)\n' )
    contents.append( 'Y_bytecode = bytecode_Spline(X_)\n' )
    contents.append( 'Y_bytecodeByt = bytecodeByt_Spline(X_)\n' )
    contents.append( 'Y_coverage = coverage_Spline(X_)\n' )
    contents.append( 'Y_diverstiy = diversity_Spline(X_)\n' )
    contents.append( 'Y_coverage_additional = coverage_additional_Spline(X_)\n\n' )
    contents.append( '# Plotting the graph\n' )
    if race:
        contents.append( 'plt.plot(X_, Y_hybridCombined, \'r-\', label="Combined Hybrid - APFD=' + str(round(APFD1*100, 1)) + '% - RI: ' + str(race['combined']) + '")\n' )
        contents.append( 'plt.plot(X_, Y_hybrid, \'m-\', label="Hybrid - APFD=' + str(round(APFD6*100, 1)) + '% - RI: ' + str(race['hybrid']) + '")\n' )
        contents.append( 'plt.plot(X_, Y_coverage, \'g-\', label="Coverage - APFD=' + str(round(APFD2*100, 1))+ '% - RI: ' + str(race['recoverage']) + '")\n' )
        contents.append( 'plt.plot(X_, Y_diverstiy, \'b-\', label="Diversity - APFD=' + str(round(APFD3*100, 1)) + '% - RI: ' + str(race['diversity']) + '")\n' )
        contents.append( 'plt.plot(X_, Y_bytecode, \'y-\', label="BytecodeTxt - APFD=' + str(round(APFD4*100, 1)) + '% - RI: ' + str(race['bytecode']) + '")\n' )
        contents.append( 'plt.plot(X_, Y_bytecodeByt, \'y-\', label="BytecodeByt - APFD=' + str(round(APFD7*100, 1)) + '% - RI: ' + str(race['bytecodeByt']) + '")\n' )
        contents.append( 'plt.plot(X_, Y_coverage_additional, \'k-\', label="Coverage Additional - APFD=' + str(round(APFD5*100, 1)) + '% - RI: ' + str(race['recoverageAdditional']) + '")\n' )
    else:
        contents.append( 'plt.plot(X_, Y_hybridCombined, \'r-\', label="Combined Hybrid - APFD=' + str(round(APFD1*100, 1)) + '% - RI: NaN")\n' )
        contents.append( 'plt.plot(X_, Y_hybrid, \'m-\', label="Hybrid - APFD=' + str(round(APFD6*100, 1)) + '% - RI: NaN")\n' )
        contents.append( 'plt.plot(X_, Y_coverage, \'g-\', label="Coverage - APFD=' + str(round(APFD2*100, 1))+ '% - RI: NaN")\n' )
        contents.append( 'plt.plot(X_, Y_diverstiy, \'b-\', label="Diversity - APFD=' + str(round(APFD3*100, 1)) + '% - RI: NaN")\n' )
        contents.append( 'plt.plot(X_, Y_bytecode, \'y-\', label="BytecodeTxt - APFD=' + str(round(APFD4*100, 1)) + '% - RI: NaN")\n' )
        contents.append( 'plt.plot(X_, Y_bytecodeByt, \'y-\', label="BytecodeByt - APFD=' + str(round(APFD7*100, 1)) + '% - RI: NaN")\n' )
        contents.append( 'plt.plot(X_, Y_coverage_additional, \'k-\', label="Coverage Additional - APFD=' + str(round(APFD5*100, 1)) + '% - RI: NaN")\n' )
    contents.append( 'plt.title("' + str(project) + str(id) + '-' + str(testType) + '")\n' )
    contents.append( 'plt.xlabel("Test suite size")\n' )
    contents.append( 'plt.ylabel("Fault-detection")\n' )
    contents.append( 'plt.legend(loc="lower right")\n' )
    contents.append( 'plt.savefig("' + dst + '/' + str(project) + str(id) + '-' + str(testType)  + '.pdf")\n' )
    contents.append( 'plt.show()\n' )

    writeFile(plotFile, contents)

def writeRealFaultPlots(project, id, testType, combined_hybrid_values, coverage_values, diversity_values, bytecode_values,
               coverage_additional_values, hybrid_values, race, plotFile, dst):
    contents = list()

    contents.append( 'import matplotlib.pyplot as plt\n' )
    contents.append( 'import numpy as np\n' )
    contents.append( 'from scipy.interpolate import make_interp_spline\n\n' )
    contents.append( '# Dataset\n' )
    contents.append( 'combined_hybrid_values = np.array(' + str(combined_hybrid_values) +  ')\n' )
    contents.append( 'hybrid_values = np.array(' + str(hybrid_values) +  ')\n' )
    contents.append( 'coverage_values = np.array(' + str(coverage_values) +  ')\n' )
    contents.append( 'diversity_values = np.array(' + str(diversity_values) +  ')\n' )
    contents.append( 'bytecode_values = np.array(' + str(bytecode_values) +  ')\n' )
    contents.append( 'coverage_additional_values = np.array(' + str(coverage_additional_values) +  ')\n\n' )
    contents.append( '# Get the x-axis and smooth the plots\n' )
    contents.append( 'x_axis = np.array(range(len(combined_hybrid_values)))\n' )
    contents.append( 'combined_hybrid_Spline = make_interp_spline(x_axis, combined_hybrid_values)\n' )
    contents.append( 'hybrid_Spline = make_interp_spline(x_axis, hybrid_values)\n' )
    contents.append( 'coverage_Spline = make_interp_spline(x_axis, coverage_values)\n' )
    contents.append( 'diversity_Spline = make_interp_spline(x_axis, diversity_values)\n' )
    contents.append( 'bytecode_Spline = make_interp_spline(x_axis, bytecode_values)\n' )
    contents.append( 'coverage_additional_Spline = make_interp_spline(x_axis, coverage_additional_values)\n\n' )
    contents.append( '# Returns evenly spaced numbers over the interval\n' )
    contents.append( 'X_ = np.linspace(x_axis.min(), x_axis.max(), len(combined_hybrid_values))\n' )
    contents.append( 'Y_hybridCombined = combined_hybrid_Spline(X_)\n' )
    contents.append( 'Y_hybrid = hybrid_Spline(X_)\n' )
    contents.append( 'Y_bytecode = bytecode_Spline(X_)\n' )
    contents.append( 'Y_coverage = coverage_Spline(X_)\n' )
    contents.append( 'Y_diverstiy = diversity_Spline(X_)\n' )
    contents.append( 'Y_coverage_additional = coverage_additional_Spline(X_)\n\n' )
   
    # Draw the plots
    contents.append( '# Plotting the graph\n' )
    contents.append( 'plt.plot(X_, Y_hybridCombined, \'r-\', label="Combined Hybrid - RI: ' + str(race['combined']) + '")\n' )
    contents.append( 'plt.plot(X_, Y_hybrid, \'m-\', label="Hybrid - RI: ' + str(race['hybrid']) + '")\n' )
    contents.append( 'plt.plot(X_, Y_coverage, \'g-\', label="Coverage - RI: ' + str(race['recoverage']) + '")\n' )
    contents.append( 'plt.plot(X_, Y_diverstiy, \'b-\', label="Diversity - RI: ' + str(race['diversity']) + '")\n' )
    contents.append( 'plt.plot(X_, Y_bytecode, \'y-\', label="Bytecode - RI: ' + str(race['bytecode']) + '")\n' )
    contents.append( 'plt.plot(X_, Y_coverage_additional, \'k-\', label="Coverage Additional - RI: ' + str(race['recoverageAdditional']) + '")\n' )
  
    contents.append( 'plt.title("' + str(project) + str(id) + '-' + str(testType) + '")\n' )
    contents.append( 'plt.xlabel("Test suite size")\n' )
    contents.append( 'plt.ylabel("Fault-detection probability")\n' )
    contents.append( 'plt.legend(loc="lower right")\n' )
    contents.append( 'plt.savefig("' + dst + '/' + str(project) + str(id) + '-' + str(testType)  + '.pdf")\n' )
    contents.append( 'plt.show()\n' )

    writeFile(plotFile, contents)

def writeStubbornMutantsPlots(project, id, testType, FASTOrders, FASTBytOrders, bytecodeOrders, bytecodeBytOrders,
               maxcoverageOrders, maxcoverageAdditionalOrders, mincoverageOrders, diversityOrders, plotFile, dstPlot, rank = False):
    contents = list()

    contents.append( 'import matplotlib.pyplot as plt\n' )
    contents.append( 'import numpy as np\n\n' )
    
    contents.append( '# Dataset\n' )
    contents.append( 'FAST_Text_values = np.array(' + str(FASTOrders) +  ')\n' )
    contents.append( 'FAST_Bytecode_values = np.array(' + str(FASTBytOrders) +  ')\n' )
    contents.append( 'bytecode_values = np.array(' + str(bytecodeOrders) +  ')\n' )
    contents.append( 'bytecodeByt_values = np.array(' + str(bytecodeBytOrders) +  ')\n' )
    contents.append( 'max_coverage_values = np.array(' + str(maxcoverageOrders) +  ')\n' )
    # contents.append( 'max_coverage_additional_values = np.array(' + str(maxcoverageAdditionalOrders) +  ')\n' )
    contents.append( 'min_coverage_values = np.array(' + str(mincoverageOrders) +  ')\n' )
    contents.append( 'diversity_values = np.array(' + str(diversityOrders) +  ')\n\n' )
    contents.append( 'all_data = [max_coverage_values, min_coverage_values, FAST_Text_values, FAST_Bytecode_values, diversity_values, bytecodeByt_values]\n' )
    contents.append( "labels = ['Max_Cov', 'Min_Cov', 'FAST-Text', 'FAST-Bytecode', 'Ledru-Text', 'Ledru-Bytecode']\n" )
    # Inclusing max_add_cov
    # contents.append( 'all_data = [max_coverage_values, max_coverage_additional_values, min_coverage_values, FAST_Text_values, FAST_Bytecode_values, diversity_values, bytecodeByt_values]\n' )
    # contents.append( "labels = ['Max_Cov', 'Max_Add_Cov', 'Min_Cov', 'FAST-Text', 'FAST-Bytecode', 'Ledru-Text', 'Ledru-Bytecode']\n" )
    # contents.append( "colors = ['pink', 'lightblue', 'aqua', 'lightgreen', 'magenta', 'orange', 'yellow', 'black', 'indigo']\n\n" )


    contents.append( 'fig, ax = plt.subplots(figsize=(10, 6))\n\n' )

    contents.append( '# Plotting the graph\n' )
    contents.append( 'bplot = ax.boxplot(all_data, vert=True, patch_artist=True, labels=labels)\n\n' )

    contents.append( '# Set colors\n' )
    contents.append( "colors = ['lightblue', 'steelblue', 'lightgreen', 'gold', 'violet', 'lightskyblue']\n" )
    contents.append( "for patch, color in zip(bplot['boxes'], colors):\n" )
    contents.append( '    patch.set_facecolor(color)\n\n' )

    contents.append( '# Scatter plot data points\n' )
    contents.append( "for i, data in enumerate(all_data, 1):\n" )
    contents.append( "    y = data\n" )
    contents.append( '    x = np.random.normal(i, 0.04, size=len(y))  # Small jitter\n' )
    contents.append( "    ax.scatter(x, y, alpha=0.7, color='black', s=10)  # Scatter plot\n\n" )

    contents.append( '# Rotate x-axis labels\n' )
    contents.append( 'plt.xticks(rotation=45, ha="right", fontsize=12)' )

    contents.append( '# Gridlines\n' )
    contents.append( 'ax.yaxis.grid(True, linestyle="--", alpha=0.7)\n\n' )

    # contents.append( "for patch, color in zip(bplot['boxes'], colors):\n" )
    # contents.append( "\tpatch.set_facecolor(color)\n" )
    
    contents.append( 'ax.set_title("Stubborn mutants in ' + str(project) + str(id) + '-' + str(testType) + ' , #mutants: " + str(len(max_coverage_values)))\n' )
    contents.append( 'plt.tight_layout(pad=2)\n' )
    
    if rank:
        contents.append( 'ax.set_ylabel("Ranking of the first to kill the stubborn mutant")\n' )
        contents.append( 'plt.savefig("' + dstPlot + '/' + str(project) + str(id) + '-' + str(testType)  + 'rank.pdf")\n' )
    else:
        contents.append( 'ax.set_ylabel("First test case to kill")\n' )
        contents.append( 'plt.savefig("' + dstPlot + '/' + str(project) + str(id) + '-' + str(testType)  + '.pdf")\n' )
    
    contents.append( 'plt.show()\n' )

    writeFile(plotFile, contents)
    
def writeStubbornessGraph(project, allscores, plotFile, dstPlot):
    contents = list()

    contents.append( 'import seaborn as sns\n' )
    contents.append( 'import numpy as np\n' )
    contents.append( 'import matplotlib.pyplot as plt\n\n' )

    contents.append( '# Dataset\n' )
    contents.append( 'scores = np.array(' + str(allscores) +  ')\n' )
    contents.append( 'x = np.arange(1.0, 0.0, -0.01)\n' )

    contents.append( '# Plotting the graph\n' )
    contents.append( "plt.plot(x, scores)\n" )
    contents.append( "plt.xticks(np.arange(0.0, 1.05, 0.1))\n" )
    contents.append( "plt.yticks(np.arange(0, round(max(scores),-1), round(max(scores)/20,-2)))\n" )
    contents.append( "plt.ylabel('Number of mutants')\n" )
    # contents.append( 'ax.set(xlabel=None)\n' )

    contents.append( 'plt.savefig("' + dstPlot + '/' + str(project) + '-' + 'scores.pdf")\n' )
    contents.append( 'plt.show()\n' )

    writeFile(plotFile, contents)

def writeStubbornessScores(project, allscores, plotFile, dstPlot):
    contents = list()

    contents.append( 'import seaborn as sns\n' )
    contents.append( 'import numpy as np\n' )
    contents.append( 'import matplotlib.pyplot as plt\n\n' )

    contents.append( '# Dataset\n' )
    contents.append( 'scores = np.array(' + str(allscores) +  ')\n' )
    contents.append( 'x = range(0, len(scores))\n' )

    contents.append( '# Plotting the graph\n' )
    contents.append( 'ax = sns.barplot(x = x, y = scores)\n' )
    contents.append( 'ax.set_ylim(0, 1.5)\n' )
    contents.append( 'ax.set(xlabel=None)\n' )

    contents.append( 'plt.savefig("' + dstPlot + '/' + str(project) + '-' + 'scores.pdf")\n' )
    contents.append( 'plt.show()\n' )

    writeFile(plotFile, contents)

# Merge CSV lists into a single CSV list
def mergeCSVFiles(csvStatementList, mergedFile):
    newHeader = 'Class::Test,'
    newContents = dict()
    cols = dict()
    colCount = 0
    numCols = 0

    # CSV_HTML objects
    for csvElem in csvStatementList:
        name = csvElem.htmlFileName
        contents = csvElem.csvContents
        header = True
        for line in contents:
            tokens = re.split(',', line)
            if header:
                header = False
                numCols += len(tokens) - 1
                
                for col in tokens[1:]:
                    newHeader += name + ':' + col.strip() + ', '
                    cols[colCount] = name + ':' + col.strip()
                    colCount += 1
            else:
               
                method = tokens[0].strip()

                if not method in newContents:
                    newContents[method] = dict()

                start = numCols - len(tokens) + 1
                end = start + len(tokens) - 1
                for col in tokens[1:]:
                    colName = cols[start]
                    newContents[method][colName] =  col.strip()
                    
                    start += 1
    
    curContents = convertIntoList(newContents, cols, newHeader)
    writeFile(mergedFile, curContents)

def readCSVContents(file):
    with open(file, "r") as f:
        contents = f.readlines()

    return contents

def convertIntoList(newContents, cols, newHeader):
    contents = list()
    contents.append(newHeader + '\n')

    for key in newContents.keys():
        line = key + ', '
        # for elem in newContents[key].keys():
        #     line += newContents[key][elem] + ','
        for index in cols.keys():
            colName = cols[index]
            if not colName in newContents[key]:
                newContents[key][colName] = '0'
            
            line += newContents[key][colName] + ','
        
        contents.append(line + '\n')

    return contents

# Return 1 for EvoSuite, 2 for Randoop, 0 otherwise (developer-written)
def checkForAutoGenerationNamingConvention(name):
    if "::" in name:
        classname = re.split("::", name)[0]
        testname = re.split("::", name)[1]
        # pattern = re.compile("test^([0-9]+)")
        m = bool(re.match(r"test[0-9]+", testname))
        c1 = bool(classname.endswith("_ESTest"))
        c2 = bool(classname.startswith("RegressionTest"))

        if c1 and m:
            return '1'
        elif c2 and m:
            return '2'
    
    return '0'

def getColsInSimilarityCSV(tokens, headerVector):
    devRecord = ''
    randoopRecord = ''
    evosuiteRecord = ''
    i=0
    while i<len(headerVector):
        if headerVector[i] == 'x':
            devRecord += tokens[i] + ','
            randoopRecord += tokens[i] + ','
            evosuiteRecord += tokens[i] + ','
        elif headerVector[i] == '1':
            evosuiteRecord += tokens[i] + ','
        elif headerVector[i] == '2':
            randoopRecord += tokens[i] + ','
        else:
            devRecord += tokens[i] + ','

        i += 1
    
    return devRecord[:-2], randoopRecord[:-2], evosuiteRecord[:-2]

# Read the CSV file contents and extract the developer-written and automatically generated ones
def processCSVFile(csvFile, similarity = False):
    
    contents = readFile(csvFile)
    
    # Get file name
    folder = os.path.dirname(csvFile)
    fileName = os.path.basename(csvFile)
    fileTokens = re.split('\\.',fileName)
    project = fileTokens[0]
    id = fileTokens[1]
    fileType = fileTokens[-2]
    if fileType == "coverage":
        fileType = fileTokens[-3] + '.' + fileType
    devFileName = folder + '/dev/' + project + '.' + id + '.' + fileType + '.dev.csv' 
    randoopFileName = folder + '/auto/randoop/' + project + '.' + id + '.' + fileType + '.randoop.csv' 
    evosuiteFileName = folder + '/auto/evosuite/' + project + '.' + id + '.' + fileType + '.evosuite.csv' 

    dev_File = list()
    randoop_File = list()
    evosuite_File = list()

    # Search the contents for the class defintion
    for i, x in enumerate(contents):
        if contents[i].startswith('The time of execution of above matrix is'):
            continue
        tokens = re.split(',', contents[i])
        if i==0:
            if similarity:
                # This vector will have 0 for auto elem, 1 for developer elem, and x for whatever
                headerVector = list()
                for token in tokens:
                    headerVector.append( checkForAutoGenerationNamingConvention(token.strip()) )
                    
                headerVector[0] = 'x'

                devRecord, randoopRecord, evosuiteRecord = getColsInSimilarityCSV(tokens, headerVector)
                dev_File.append(devRecord+'\n')
                randoop_File.append(randoopRecord+'\n')
                evosuite_File.append(randoopRecord+'\n')
            else:
                dev_File.append(contents[i])
                randoop_File.append(contents[i])
                evosuite_File.append(contents[i])
            continue
        

        # check if the method name follows the convention of autogenerated test
        if checkForAutoGenerationNamingConvention(tokens[0]) == '2':
            if similarity:
                devRecord, randoopRecord, evosuiteRecord = getColsInSimilarityCSV(tokens, headerVector)
                randoop_File.append(randoopRecord+'\n')
            else:
                randoop_File.append(contents[i])
        elif checkForAutoGenerationNamingConvention(tokens[0]) == '1':
            if similarity:
                devRecord, randoopRecord, evosuiteRecord = getColsInSimilarityCSV(tokens, headerVector)
                evosuite_File.append(evosuiteRecord+'\n')
            else:
                evosuite_File.append(contents[i])
        else:
            if similarity:
                devRecord, randoopRecord, evosuiteRecord = getColsInSimilarityCSV(tokens, headerVector)
                dev_File.append(devRecord+'\n')
            else:
                dev_File.append(contents[i])

    writeFile(devFileName, dev_File)
    writeFile(randoopFileName, randoop_File)
    writeFile(evosuiteFileName, evosuite_File)
   
def processCSVFiles(allFiles):
    for file in allFiles:
        if "textSimilarity.csv" in file:
            processCSVFile(file, True)
        else:
            processCSVFile(file)

# csvStatementList = list()
# csvStatementFile = CSV_HTML()
# csvStatementFile.setFileName('MutableDateTime')
# csvStatementFile.csvContents = readCSVContents('/home/islam/MyWork/New-work-2023/DBT-workbench/resources/coverage/time.3f.MutableDateTime.statement.coverage.csv')
# csvStatementList.append(csvStatementFile)

# csvStatementFile = CSV_HTML()
# csvStatementFile.setFileName('UnsupportedDurationField')
# csvStatementFile.csvContents = readCSVContents('/home/islam/MyWork/New-work-2023/DBT-workbench/resources/coverage/time.1f.UnsupportedDurationField.branch.coverage.csv')
# csvStatementList.append(csvStatementFile)

# mergeCSVFiles(csvStatementList, '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/time.3f.statement.coverage.csv')

# checkoutVersion('Math', '2', '/home/islam/MyWork/New-work-2023/DBT-workbench/subjects/buggy')

# file = '/home/islam/MyWork/New-work-2023/DBT-workbench/scripts/math-tests/Math/randoop/3/Math-3f-randoop.3.tar.bz2'
# pid,vid,tool = extractInfo(file)

# print(pid)
# print(vid)
# print(tool)

# getFolder('org.apache.commons.math3.util;')

# list = ["/home/islam/MyWork/New-work-2023/DBT-workbench/scripts/math-tests/Math/evosuite/1/Math-1f-evosuite.1/org/apache/commons/math3/fraction/BigFraction_ESTest.java",
#         "/home/islam/MyWork/New-work-2023/DBT-workbench/scripts/math-tests/Math/evosuite/1/Math-1f-evosuite.1/org/apache/commons/math3/fraction/BigFraction_ESTest_scaffolding.java",
#         "/home/islam/MyWork/New-work-2023/DBT-workbench/scripts/math-tests/Math/evosuite/1/Math-1f-evosuite.1/org/apache/commons/math3/fraction/Fraction_ESTest.java",
#         "/home/islam/MyWork/New-work-2023/DBT-workbench/scripts/math-tests/Math/evosuite/1/Math-1f-evosuite.1/org/apache/commons/math3/fraction/Fraction_ESTest_scaffolding.java"]

# copyFiles(list,"/home/islam/MyWork/New-work-2023/DBT-workbench/scripts/math-tests/Math","evosuite")

# file = '/home/islam/MyWork/New-work-2023/DBT-workbench/subjects/buggy/84/output.txt'
# fails = processMavenOutput(file)
# if fails > 0:
#     print('error caught')
# else:
#     print('error NOT caught')


# statementFile = "D:\\Work\\PhD\\DBT-workbench\\resources\\coverage\\time.3f.MutableDateTime.statement.coverage.csv"
# similarityFile = "D:\\Work\\PhD\\DBT-workbench\\resources\\similarity\\time.3f.textSimilarity.csv"

# processSimFileFromStatmentFile(similarityFile, statementFile)


# csvFile = "/home/islam/MyWork/New-work-2023/csv files/similarity/math/math.5f.textSimilarity.csv"
# folder = "/home/islam/MyWork/New-work-2023/csv files/coverage/lang"
# allFiles = getAllFilesEndingWith(folder,'textSimilarity.csv')
# # processCSVFile(csvFile, True)
# processCSVFiles(allFiles)

