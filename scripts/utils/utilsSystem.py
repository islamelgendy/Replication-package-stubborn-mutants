#!/usr/bin/python3

import subprocess
import os
from utils.utilsIO import *

def checkoutVersion(pid, vid, path, fixed=True):
    if fixed:
        command = 'defects4j checkout -p ' + pid + ' -v ' + vid + 'f -w ' + path + '/' + vid
    else:
        command = 'defects4j checkout -p ' + pid + ' -v ' + vid + 'b -w ' + path + '/' + vid

    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read(), path + '/' + vid

def runBuggyVersion(root, path, javaTestFiles, signatures, tool):
    outputfile = os.path.abspath(path+'/output-' + tool + '.txt')
    abspath = os.path.dirname(outputfile)

    # if randoop, all you need to run is the main regression test suite
    if tool == "randoop":
        command = root + "/scripts/bash/runmaven.sh '%s' '%s' '%s'" % (str(abspath), str(next(iter(signatures))+'.RegressionTest'), str(tool))
    elif tool == "evosuite":
        classes = prepareEvoSuiteTestClasses(javaTestFiles)
        command = root + "/scripts/bash/runmaven.sh '%s' '%s' '%s'" % (str(abspath), str(classes), str(tool))

    os.system(command)

    fails, errors = processMavenOutput(outputfile)
    if fails > 0 or errors > 0:
        return True
    else:
        return False
    
def createFolder(path):
    # Check whether the specified path exists or not
    if not os.path.exists(path):
        # Create a new directory because it does not exist
        os.makedirs(path)

def runSingleTestMethod(root, path, packageName, className, methodName):
    outputfile = os.path.abspath(path+'/output-' + className + '-' + methodName + '.txt')
    abspath = os.path.dirname(outputfile)

    command = root + "/scripts/bash/runsingletestmethod.sh '%s' '%s' '%s'" % (str(abspath), str(packageName + '.' + className), str(methodName))

    os.system(command)

def runMavenTest(root, path):
    outputfile = os.path.abspath(path+'/output-all.txt')
    abspath = os.path.dirname(outputfile)

    command = root + "/scripts/bash/runmaventest.sh '%s'" % (str(abspath))

    os.system(command)

def runMutation(root, path, project):
    # outputfile = os.path.abspath(path+'/output-' + className + '-' + methodName + '.txt')
    # abspath = os.path.dirname(outputfile)

    command = root + "/scripts/bash/runmutation.sh '" + (str(path)) + "' '" + (str(project)) + "'"

    os.system(command)

    return path + "/output-mutation/" + "output-" + str(project) + ".txt"


def prepareEvoSuiteTestClasses(javaFiles):
    list=""
    packageLines = getPackageLines(javaFiles)
    testpaths, signatures = getFolder(packageLines)
    # signatureList = convert(signatures)
    index = 0

    for file in javaFiles:
        if not file.endswith("_scaffolding.java"):
            className = os.path.basename(file)
            classSignature = getProperSignature(file, signatures) + '.' + className[0:len(className)-5]
            list+=classSignature+','
            index+=1

    return list[0:len(list)-1]

def getProperSignature(file, signatures):

    # initially the target is the first path
    target = next(iter(signatures))

    # get rid of the file name and keep the path
    file = os.path.dirname(file)
    fileTokens = re.split('/', file)
    
    # Find which path in the list of dst that matches the file best
    for signature in signatures:
        # if signature ending with / remove it
        signatureTokens = re.split('\\.', signature)

        # compare the last 4 elements of both tokens, and if they match, that is the proper target
        if fileTokens[-1] == signatureTokens[-1]:
            if len(fileTokens) > 1 and len(signatureTokens) > 1:
                if fileTokens[-2] == signatureTokens[-2]:
                    if len(fileTokens) > 2 and len(signatureTokens) > 2:
                        if fileTokens[-3] == signatureTokens[-3]:
                            if len(fileTokens) > 3 and len(signatureTokens) > 3:
                                if fileTokens[-4] == signatureTokens[-4]:
                                    target = signature
                                else:
                                    continue
                            else:
                                target = signature
                        else:
                             continue
                    else:
                        target = signature
                else:
                     continue
            else:
                target = signature
        break
    
    return target

# Get the exact bytecode test class path using the name of the class
def getBytecodeFile(javaBytecodeFiles:list, classname:str, packagename:str):
    path = packagename.replace('.', '/')
    for file in javaBytecodeFiles:
        if file.endswith(path + '/' + classname + '.class'):
            return file

    return None

# program to convert a  set into a list
def convert(s):
    return list(map(lambda x: x, s))

def writeOnlyFaultDetectingMethods(listMethodsDetectingRealFaults, csvPath):

    # Header of file
    contents = ['Method,Fault-Detected\n']
    for method in listMethodsDetectingRealFaults:
        contents.append(method + ', 1\n')

    createFolder( os.path.dirname(os.path.abspath(csvPath)) )
    with open(csvPath, "w") as f:
        contents = "".join(contents)
        f.write(contents)

# path='/home/islam/MyWork/New-work-2023/DBT-workbench/subjects/buggy/84'
# server='org.apache.commons.math.optimization.direct.RegressionTest'

# runBuggyVersion(path,[],server,'randoop')

# Run the mutation for the current project
# print("Running mutation.................................", end="")
# runMutation('/home/islam/MyWork/New-work-2023/DBT-workbench/resources/subjects/fixed/math/66')
# print("OK")


# versions = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33', '35']
# root = '/home/islam/MyWork/New-work-2023/DBT-workbench/'
# project = 'lang'
# # version = '4'

# for version in versions:
#     buggyfolder = copyEvoSuiteTestFiles(root, project, version)

#     csvFaultsDetectedPath = root + "resources/realfault/" + project + '/' + project + "." + version + "f.realfaults-detected.csv"
#     print("Running tests on buggy version.................................", end="", flush=True)
#     runMavenTest(root, buggyfolder)
#     print("OK")

#     outputfile = buggyfolder + '/output-details/output-all.txt'

#     # Check the outputfile, if there are any errors or faults, then the method detects the error
#     failingMethods = processMavenOutputAndParseFailedMethods(outputfile)

#     # Write the methods detecting the real faults
#     print("Write tests detecting real faults.............................", end="", flush=True)

#     writeOnlyFaultDetectingMethods(failingMethods, csvFaultsDetectedPath)
#     print("OK")