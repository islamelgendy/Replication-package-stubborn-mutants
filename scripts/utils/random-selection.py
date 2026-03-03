from CSVLoader import CSVLoader, evaluateMutationScore
import sys

from utils.utilsIO import *


#project = input("Enter project id: ")
args = sys.argv
if len(args) == 1:
    project = "time"
    id = "3"
else: 
    project = args[1]
    id = args[2]

print(args)

coverageFolder = "../resources/coverage/"
mutationFolder = "../resources/mutation/"
similarityFolder = "../resources/similarity/"

# Load coverage CSV files for the project and id
statementCoverageFiles = filterFiles(coverageFolder, project + '.' + id + 'f', 'statement.coverage.csv')
branchCoverageFiles = filterFiles(coverageFolder, project + '.' + id + 'f', 'branch.coverage.csv')

# Load the coverage files into CSVLoader obj
try:
    stCoverageCSV = list()
    for stCoverageFile in statementCoverageFiles:
        stItem = CSVLoader(stCoverageFile)
        stCoverageCSV.append(stItem)
except:
    print('Statement coverage files can NOT be loaded')

try:
    brCoverageCSV = list()
    for brCoverageFile in branchCoverageFiles:
        brItem = CSVLoader(brCoverageFile)
        brCoverageCSV.append(brItem)
except:
    print('Branch coverage files can NOT be loaded')

# Load the mutation file into CSVLoader obj
try:
    mutationFile = filterFiles(mutationFolder, project + '.' + id + 'f', 'mutation.csv')[0]
    mutationCSV = CSVLoader(mutationFile)
except:
    print('Mutation file can NOT be loaded')

# Load the similarity matrix
try:
    similarityFile = filterFiles(similarityFolder, project + '.' + id + 'f', 'textSimilarity.csv')[0]
    simlarityCSV = CSVLoader(similarityFile)
except:
    print('Similarity matrix can NOT be loaded')

# calculate the original statement coverage
totalStatementCoverage = 0
for stCSV in stCoverageCSV:
    totalStatementCoverage += stCSV.getTotalCoverage()

totalStatementCoverage /= len(stCoverageCSV)

# calculate the original branch coverage
totalBranchCoverage = 0
for brCSV in brCoverageCSV:
    totalBranchCoverage += brCSV.getTotalCoverage()

totalBranchCoverage /= len(brCoverageCSV)

# calculate the original mutation score 
MS = mutationCSV.getTotalCoverage()

print('statement coverage ', totalStatementCoverage)
print('branch coverage ', totalBranchCoverage)
print('mutation score ', MS)

# newMatrix1, execTime1 = mutationCSV.randomSelection()
# newMatrix2, execTime2 = mutationCSV.randomCoverageSelection()

# print('size of original suite is ', len(mutationCSV.matrix))
# print('size of random selected suite is ', len(newMatrix1))
# print('selection made in %s seconds' %execTime1)
# print('size of random coverage selected suite is ', len(newMatrix2))
# print('selection made in %s seconds' %execTime2)

randomList = list()
randomCoverageList = list()

for brCSV in brCoverageCSV:
    newMatrix1, newMatrix2, execTime = brCSV.selectionStacked()

    # print('size of original suite is ', len(brCSV.matrix))
    # print('size of random selected suite is ', len(newMatrix1))
    # print('selection made in %s seconds' %execTime1)
    # print('size of random coverage selected suite is ', len(newMatrix2))
    # print('selection made in %s seconds' %execTime2)

    MS1 = evaluateMutationScore(mutationCSV.matrix, newMatrix1.keys(), mutationCSV.listCols)
    MS2 = evaluateMutationScore(mutationCSV.matrix, newMatrix2.keys(), mutationCSV.listCols)
    print('MS1 is ', MS1)
    print('MS2 is ', MS2)