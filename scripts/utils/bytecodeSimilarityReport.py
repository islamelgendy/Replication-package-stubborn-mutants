import os
import sys
from utils.utilsIO import *
from utils.utilsSystem import runMavenTest
from utils.jacocohtmlParser import *
from utils.CoverageLineInfo import *
from utils.testMethod import *

#project = input("Enter project id: ")
args = sys.argv
if len(args) == 1:
    project = "time"
    id = "13"
else: 
    project = args[1]
    id = args[2]

print(args)

lastSlashPos = args[0].rfind('/')
secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
root = args[0][:secondToLastSlashPos]
fixedVersionPath = root + '/resources/subjects/fixed/' + project + '/' + id


folder = root + "/resources/similarity/" + project + "/"

if not os. path. isdir(folder):
    print(folder + ' does not exist')
    sys.exit(1)

# Generate the byte code of the tests
runMavenTest(root, fixedVersionPath)

# Load the test cases from the folder
listTestMethods = loadTestcases(folder, project, id)


# Calculate the similarity values and output into CSV file
print("Calculating textual similarity.................................", end="")
simMat = getSimilarityMatrix(listTestMethods)
print("OK")

csvTextSimPath = root + "/resources/similarity/" + project + "." + id + "f.textSimilarity.csv"
writeSimMatrixToFile(simMat, listTestMethods, csvTextSimPath)

