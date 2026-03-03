#!/usr/bin/python3

import re
import os
from utils.CoverageLineInfo import CoverageLineInfo

# Read the contents of the html file
def processHTML(htmlFile):
    
    with open(htmlFile, "r") as f:
        contents = f.readlines()

    infoList = list()
    
    # Search the contents for the class defintion
    for i, x in enumerate(contents):
        if x.startswith('<span class='):
            lineInfo = CoverageLineInfo()
            lineInfo.parseLine(x)
            infoList.append(lineInfo)
    
    return infoList

def getMethodCoverageRecord(className, methodName, infoList):
    lineRecord = className + '::' + methodName + ' , '
    branchRecord = className + '::' + methodName + ' , '
    for infoLine in infoList:
        if infoLine.lineNumber == 1499:
            debug = True
        if 'fc' in infoLine.status or 'pc' in infoLine.status:
            lineRecord += '1 , '
            if infoLine.branch and 'bfc' in infoLine.status:
                branchRecord += '1 , '
            elif infoLine.branch and 'bpc' in infoLine.status:
                branchRecord += '0.5 , '
            elif infoLine.branch and 'bnc' in infoLine.status:
                branchRecord += '0 , '
        else:
            lineRecord += '0 , '
            if infoLine.branch and 'bnc' in infoLine.status:
                branchRecord += '0 , '
        

    return lineRecord[0:len(lineRecord)-2], branchRecord[0:len(branchRecord)-2]

def getHeader(infoList):
    lineHeader = 'Class::Test , '
    branchHeader = 'Class::Test , '
    for infoLine in infoList:
        lineHeader += str(infoLine.lineNumber) + ' , '

        # check if this is a branch, and if so, add to branch header
        if infoLine.branch:
            branchHeader += str(infoLine.lineNumber) + ' , '

    return lineHeader[0:len(lineHeader)-2], branchHeader[0:len(branchHeader)-2]

def writeContentsToFile(csvFile, csvPath):
    with open(csvPath, "w") as f:
        contents = "".join(csvFile.csvContents)
        f.write(contents)

def isRightTestFile(testfile, tarClasses, trigerClasses, RandoopOnly = False):
    # extract the test file name only
    filename = os.path.basename(testfile)
    filename = re.split('\\.', filename)[0]
    
    # if this is a Randoop test class, then return true
    if filename.startswith('RegressionTest'):
        return True
    
    # if the Randoop only flag is true, ignore any others
    if RandoopOnly:
        return False
    
    # For debug
    if 'MultiStartUnivariateRealOptimizerTest' in testfile:
        found = True
    
    # Find if the test file is the trigerClass
    for trigerClass in trigerClasses:
        if filename in trigerClass:
            return True
    
    # Find if the test file exist in the tarClasses
    for tarClass in tarClasses:

        target = re.split('\\.', tarClass)[-1]
        # Identify whether that test class is relevant or not
        if target in filename:
            return True
    
    return False

# Check if the method (node) contains any assert statements
def checkNode(node):
    methodName = node.name
    methodBody = node.body
    # Check if this is a helper method with any parameters, if so, return False
    if len(node.parameters) > 0:
        return False
    # Check if this is a private method, if so, return False
    methodModifiers = node.modifiers
    for modifier in methodModifiers:
        if modifier == 'static' or modifier == 'protected' or modifier == 'private':
            return False

    # check if the name starts with test
    if str(methodName).startswith('test'):
        return True
    # for stItem in methodBody:
    #     if isinstance(stItem, javalang.tree.StatementExpression):
    #         ex = stItem.expression
    #         try:
    #             mem = ex.member
    #             if 'assert' in mem:
    #                 return True
    #         except:
    #             continue
    return False

def findIndexOfHTMLFile(csvList, htmlFile):
    index = 0
    for csvfile in csvList:
        if csvfile.htmlPath == htmlFile:
            return index
        index += 1
    
    return index

def deleteFlakeyTest(testfile, methodName):

    with open(testfile, "r") as f:
        contents = f.readlines()

    # Search the contents for the method
    for i, x in enumerate(contents):
        if "public " in x and methodName in x:
            # place the starting comment symbol on the line before
            # However, if the line before has already a closing comment, place it properly
            if '*/' in contents[i-1]:
                contents[i-1] = '*/ /*' + contents[i-1][2:]
            contents[i-1] = '/*' + contents[i-1]
            methodPos = i
            break
            
    # Find the next test case or closing end
    # Search the contents for the method
    for i, x in enumerate(contents, methodPos):
        # If index i has reached the end of the file, place the closing comment symbol before the end of file
        if i == len(contents):
            contents[i-2] = contents[i-2] + '*/'
            break
        elif "@Test" in contents[i]:
            # place the ending comment symbol on the line before
            
            contents[i-1] = '*/' + contents[i-1]
            break

    with open(testfile, "w") as f:
        contents = "".join(contents)
        f.write(contents)


# Test the jacoco parsing
# htmlFile = '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/subjects/fixed/time/13/target/site/jacoco/org.joda.time.format/PeriodFormatterBuilder.java.html'
# infoList = processHTML(htmlFile)

# contents = list()
# statementHeader, branchHeader = getHeader(infoList)
# contents.append(branchHeader + '\n')
# t1 = re.split(',', branchHeader)

# statementRecord, branchRecord = getMethodCoverageRecord('PeriodFormatterBuilder', 'testFormatStandard_negative', infoList)
# contents.append(branchRecord + '\n')
# t2 = re.split(',', branchRecord)

# project = 'time'
# id = '13'
# csvfilePath = "/home/islam/MyWork/New-work-2023/DBT-workbench/resources/coverage/" + project + "." + id + "f." + "PeriodFormatterBuilder" + ".branch.coverage.csv"
# with open(csvfilePath, "w") as f:
#     contents = "".join(contents)
#     f.write(contents)