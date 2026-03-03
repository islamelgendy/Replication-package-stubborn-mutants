from collections import Counter
from stubborn_mutant_analysis import *
from utils.mutationxml import *
from utils.Hybrid_selection import HybridSelection
from utils.Coverage_selection import CoverageSelection

from utils.Diversity_selection import DiversitySelection
from utils.CSVLoader import CSVLoader, evaluateMutationScore, getMatrixCoverage
from utils.Hybrid_selection_combined import CombinedHybridSelection
from utils.Hybrid_selection_separate import SeparateHybridSelection
import sys

from utils.testsCoveringMutants import *
from utils.utilsIO import *
from utils.utilsSystem import createFolder, runMutation
from tqdm import tqdm
import os

def checkStubbornNature(folder, RSM:dict, rank:int, mutationsFile:str):
    mutantsList = list()
    # for mutant in tqdm(RSM.keys(), desc="Processing Mutants", unit="mutant"):
    for mutant in RSM.keys():
        
        if RSM[mutant] <= rank:
            mutInfo = parseMutantFromXML(folder, mutationsFile, mutant)
            if mutInfo:
                mutantsList.append(mutInfo)
            
    return mutantsList

def runExpRank(root, project, id, curRank):

    folder = root + "/resources/subjects/fixed/" + project + "/" + id
    mutationFolder = root + "/resources/mutation/"

    # set the path for PIT XML files
    mutationsFile = f"{root}/resources/subjects/fixed/{project}/{id}/target/pit-reports/mutations.xml"

    mutationExt = 'mutation.csv'

    # Load the mutation file into CSVLoader obj
    try:
        mutationFile = filterFiles(mutationFolder, project + '.' + id + 'f', mutationExt)[0]
    except:
        print('Mutation file can NOT be loaded')

    mutContents = readFile(mutationFile)
        
    killingTests, lineNumbers = getMutants(mutContents)

    # Calculate the RSM
    RSM, WSM, maxRank = getRankAndWieghtedStubborness(killingTests)
    
    # TODO: check the nature of all Rank 1 stubborn mutants
    # Run the mutation for the current project
    # print("Running mutation.................................", end="", flush=True)
    try:
        if not os.path.isfile(mutationsFile):
            mutationOutputFile = runMutation(root, folder, project)
        # print("OK")
    except:
        print("failed")
    stbNatureList = checkStubbornNature(folder, RSM, curRank, mutationsFile)

    return stbNatureList


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        prj = "time"
        rank = 10
        stubbornScoreThresholdValues = [ 0.5, 0.1, 0.01]
    elif len(args) == 2:
        prj = args[1]
        rank = 1
        stubbornScoreThresholdValues = [0.75, 0.5, 0.25, 0.15, 0.1, 0.05, 0.03, 0.02, 0.01, 0.005, 0.003, 0.002, 0.001]
    elif len(args) == 3:
        prj = args[1]
        rank = int(args[2])
        stubbornScoreThresholdValues = [0.75, 0.5, 0.25, 0.15, 0.1, 0.05, 0.03, 0.02, 0.01, 0.005, 0.003, 0.002, 0.001]
    elif len(args) == 4:
        prj = args[1]
        rank = int(args[2])
        stbValue = float(args[3])
        stubbornScoreThresholdValues = [stbValue]
    else: 
        print('Wrong number of arugments passed')
        exit()

    print(args)
    lastSlashPos = args[0].rfind('/')
    secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
    root = args[0][:secondToLastSlashPos]

    loadAll = True
    if loadAll:
        
        picklePath = f"{root}/resources/stubborn/ranks/natures/"
        for curRank in range(1, rank+1):
            all_natures = list()
            summary_files = getAllFilesEndingWith(picklePath, f'{curRank}-nature-summary.pkl')
            for pickleFile in summary_files:
                cur_natures = loadDataStructure(pickleFile)
                all_natures.extend(cur_natures)
            
            # Generate the summary
            all_summary = generate_summary(all_natures)
            all_sorted_summary = sort_summary(all_summary)
            csvFile = f"{root}/resources/stubborn/ranks/all-{curRank}-nature-summary.csv"
            save_summary(all_sorted_summary, csvFile, False)
        exit()

    if prj == 'math':
        projects = ['4', '5', '6', '9', '13', '14', '17', '18', 
                    '21', '23', '25', '27', '28', 
                    '30', '32', '33', '37', '49', '50', 
                    '52', '56', '58', '61', '64',  
                    '67', '69', '70', '73', '78', '76', '80']

    # jsoup projects:
    # prj = 'jsoup'
    elif prj == 'jsoup':
        projects = [ '4', '15', '16', '19', '20', '26', '29', 
                    '33', '35', '37']

    # lang projects:
    # prj = 'lang'
    elif prj == 'lang':
        projects = [ '4', '6', '15', '16', '19', '22', '23', '25', '31', '33', '35']
 
     # time projects:
    # prj = 'time'
    elif prj == 'time':
        projects = ['11','13']

    # cli projects:
    # prj = 'cli'
    elif prj == 'cli':
        projects = ['30','31','32','34']

    # csv projects:
    # prj = 'csv'
    elif prj == 'csv':
        projects = ['2', '3', '4', '5', '8']

    # compress projects:
    # prj = 'compress'
    elif prj == 'compress':
        projects = ['1', '11', '22', '24', '26']

    # stubbornScoreThreshold = 0.4
    for curRank in tqdm(range(1, rank+1), desc="Processing Ranks", unit="Rank"):
    # for curRank in range(1, rank+1):
            
        natureList = list()

        # for id in projects:
        for id in tqdm(projects, desc=f"Rank {curRank}", leave=False, unit="Project"):
            stbNatureList = runExpRank(root, prj, id, curRank)
            natureList.extend(stbNatureList)

        # Define the CSV file name
        createFolder(root + '/resources/stubborn/ranks/natures/' )
        pickleFile = f"{root}/resources/stubborn/ranks/natures/{prj}-{curRank}-nature-summary.pkl"
        saveDataStructure(natureList, pickleFile)

        # Generate the summary
        summary = generate_summary(natureList)
        sorted_summary = sort_summary(summary)
        csvFile = f"{root}/resources/stubborn/ranks/{prj}-{curRank}-nature-summary.csv"
        save_summary(sorted_summary, csvFile, False)