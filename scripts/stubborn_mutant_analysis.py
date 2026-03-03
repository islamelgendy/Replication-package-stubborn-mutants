from collections import Counter
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
import math
import csv
import os

def generate_in_memory_data(id, allMS, totalSize, threshold_levels, ms_values, recalls, sizes):
    # Ensure the lengths of threshold_levels and ms_values are the same
    if len(threshold_levels) != len(ms_values):
        raise ValueError("The lengths of threshold_levels and ms_values must be the same.")

    # Create a list to store the data
    data = []

    # Add the header as the first dictionary (only for the first ID)
    if id == 1:  # Assuming the first ID is 1
        data.append({"ID": "ID", "Threshold Level": "Threshold Level", "All MS": "All MS", "Stubborn MS": "Stubborn MS", "Recall": "Recall", "Total Size": "Total Size", "Size of Stubborn Tests": "Size of Stubborn Tests"})

    # Add the data rows
    for threshold, ms, recall, size in zip(threshold_levels, ms_values, recalls, sizes):
        data.append({"ID": id, "Threshold Level": threshold, "All MS": allMS, "Stubborn MS": ms, "Recall": recall, "Total Size": totalSize, "Size of Stubborn Tests": size})

    return data

def vargha_delaney_effect_size(group1, average, recall = True, allValue = 1):
    """
    Computes the Vargha-Delaney A12 effect size for two groups.
    
    Parameters:
        group1: List of values for group 1
        group2: List of values for group 2
        
    Returns:
        A12: Vargha-Delaney effect size
    """
    numVer = 0
    group2 = []
    for item, ms in zip(group1, allValue):
        group2.append(average)
        if recall:
            if item >= 1:
                numVer += 1
        else:
            if item >= allValue[ms]:
                numVer += 1

    n1, n2 = len(group1), len(group2)
    rank_sum = sum((x > y) + 0.5 * (x == y) for x in group1 for y in group2)
    A12 = rank_sum / (n1 * n2)
    percentage = round(numVer / len(allValue), 2)
    return round(A12, 2), percentage

def get_summary_per_level(root, project, all_data, threshold_levels):
    # Combine all data into a single list
    summary = []
    totalAllMS = {}
    totalStbMS = {}
    totalRecall = {}
    totalAllSize = {}
    totalStbSize = {}
    IDs = set()
    
    for lvl in threshold_levels:
        totalAllMS[lvl] = 0
        totalStbMS[lvl] = 0
        totalRecall[lvl] = 0
        totalAllSize[lvl] = 0
        totalStbSize[lvl] = 0

    allMSGroup = {}
    stbMSGroup = {}
    recallGroup = {}
    for data in all_data:
        for elem in data:
            totalAllMS[elem['Threshold Level']] += elem['All MS']
            allMSGroup[elem['ID']] = elem['All MS']
            totalStbMS[elem['Threshold Level']] += elem['Stubborn MS']
            if elem['Threshold Level'] in stbMSGroup.keys():
                stbMSGroup[elem['Threshold Level']].append( elem['Stubborn MS'] )
            else:
                stbMSGroup[elem['Threshold Level']] = [elem['Stubborn MS']]
            totalRecall[elem['Threshold Level']] += elem['Recall']
            if elem['Threshold Level'] in recallGroup.keys():
                recallGroup[elem['Threshold Level']].append( elem['Recall'] )
            else:
                recallGroup[elem['Threshold Level']] = [elem['Recall']]
            totalAllSize[elem['Threshold Level']] += elem['Total Size']
            totalStbSize[elem['Threshold Level']] += elem['Size of Stubborn Tests']
            IDs.add(elem['ID'])
            
        # combined_data.append({"Threshold Level": threshold, "All MS": allMS, "Stubborn MS": ms, "Recall": recall, "Total Size": totalSize, "Size of Stubborn Tests": size})
    for lvl in threshold_levels:
        totalAllMS[lvl] = round( totalAllMS[lvl] / len(IDs), 2)
        totalStbMS[lvl] = round(totalStbMS[lvl] / len(IDs), 2)
        stbMSA12, stbMSVerCount = vargha_delaney_effect_size(stbMSGroup[lvl], totalStbMS[lvl], False, allMSGroup)
        totalRecall[lvl] = round(totalRecall[lvl] / len(IDs), 2)
        recallA12, recallVerCount  = vargha_delaney_effect_size(recallGroup[lvl], totalRecall[lvl], True, allMSGroup)
        totalAllSize[lvl] = math.ceil(totalAllSize[lvl] / len(IDs))
        totalStbSize[lvl] = math.ceil(totalStbSize[lvl] / len(IDs))
        summary.append({"Threshold Level": lvl, "Avg All MS": totalAllMS[lvl], "Avg Stubborn MS": totalStbMS[lvl], "A12 Stubborn MS": stbMSA12, "Perfect MS": stbMSVerCount, "Avg Recall": totalRecall[lvl], "A12 Recall":recallA12, "Perfect Recall": recallVerCount, "Avg Total Size": totalAllSize[lvl], "Avg Size of Stubborn Tests": totalStbSize[lvl]})


    # Define the CSV file name
    createFolder(root + '/resources/stubborn/' )
            
    csv_filename = f"{root}/resources/stubborn/{project}-summary.csv"

    # Write the combined data to a CSV file
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Threshold Level", "Avg All MS", "Avg Stubborn MS", "A12 Stubborn MS", "Perfect MS", "Avg Recall", "A12 Recall", "Perfect Recall", "Avg Total Size", "Avg Size of Stubborn Tests"])
        writer.writeheader()
        writer.writerows(summary)

    print(f"Combined CSV file '{csv_filename}' has been generated.")

# def generate_csv(root, project, id, allMS, threshold_levels, ms_values):
def combine_data_and_write_csv(root, project, all_data):
    # Combine all data into a single list
    combined_data = []
    for data in all_data:
        combined_data.extend(data)

    # Define the CSV file name
    createFolder(root + '/resources/stubborn/' )
            
    csv_filename = f"{root}/resources/stubborn/{project}.csv"

    # Write the combined data to a CSV file
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Threshold Level", "All MS", "Stubborn MS", "Recall", "Total Size", "Size of Stubborn Tests"])
        writer.writeheader()
        writer.writerows(combined_data)

    print(f"Combined CSV file '{csv_filename}' has been generated.")

def write_dict_to_csv(data: dict, csv_path: str):
    """
    Writes a dictionary to a CSV file.

    Parameters:
    - data (dict): Dictionary where each key-value pair is written as a row.
    - csv_path (str): Path to the output CSV file.
    """
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Key', 'Value'])  # Header
        for key, value in data.items():
            writer.writerow([key, value])

# # Example usage
# threshold_levels = [0.5, 0.1, 0.01]
# ms_values = [0.63, 0.63, 0.63]
# project = "example_project"
# id = "123"

# generate_csv(threshold_levels, ms_values, project, id)

def compute_overlap(stubborn_tests, real_fault_tests):
    """
    Compute precision, recall, and F1-score for the overlap between 
    tests killing stubborn mutants and tests detecting real faults.

    :param stubborn_tests: Set of test names killing stubborn mutants
    :param real_fault_tests: Set of test names detecting real faults
    :return: Dictionary containing precision, recall, and F1-score
    """
    stubborn_set = set(stubborn_tests)
    real_fault_set = set(real_fault_tests)
    
    intersection = stubborn_set & real_fault_set  # Tests in both sets
    intersection_count = len(intersection)
    
    # precision = intersection_count / len(stubborn_set) if stubborn_set else 0
    recall = intersection_count / len(real_fault_set) if real_fault_set else 0
    # f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return recall
    # return {
    #     "precision": precision,
    #     "recall": recall,
    #     "f1_score": f1_score,
    #     "overlapping_tests": intersection
    # }

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

def checkStubbornNature(folder, RSM:dict, rank:int, mutationsFile:str):
    mutantsList = list()
    for mutant in RSM.keys():
        
        if RSM[mutant] == rank:
            mutInfo = parseMutantFromXML(folder, mutationsFile, mutant)
            if mutInfo:
                mutantsList.append(mutInfo)
            
    return mutantsList

def generate_summary(data):
    summary = {
        'Type of node': Counter(),
        'Nesting level': Counter(),
        'Cyclomatic complexity': Counter(),
        'Access modifier': Counter(),
        'Is void': Counter(),
        'Is static': Counter(),
        'Mutator': Counter(),
    }

    for record in data:
        for key, value in record.items():
            summary[key][value] += 1

    return summary

def sort_summary(summary):
    # Flatten the summary into a list of (key, value, count) tuples
    flattened_summary = []
    for key, counter in summary.items():
        for value, count in counter.items():
            flattened_summary.append((key, value, count))

    # Sort by key (alphabetically) and then by count (descending)
    flattened_summary.sort(key=lambda x: (x[0], -x[2]))

    return flattened_summary

def save_summary(summary, csvFile, printFlag = True):

    with open(csvFile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(['Key', 'Value', 'Count'])
        
        # Write the sorted summary data
        for key, value, count in summary:
            writer.writerow([key, value, count])

    # with open(csvFile, mode='w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     # Write the header
    #     writer.writerow(['Key', 'Value', 'Count'])
        
    #     # Write the summary data
    #     for key, counter in summary.items():
    #         for value, count in counter.items():
    #             writer.writerow([key, value, count])

    if printFlag:
        print(f"Summary saved to '{csvFile}'")

def runExp(root, project, id, testType, stubbornScoreThreshold, curRank):

    folder = root + "/resources/subjects/fixed/" + project + "/" + id
    coverageFolder = root + "/resources/coverage/"
    mutationFolder = root + "/resources/mutation/"
    realfaultFolder = root + "/resources/realfault/"
    realfaultExt = "realfaults-detected.csv"

    # set the path for PIT XML files
    mutationsFile = f"{root}/resources/subjects/fixed/{project}/{id}/target/pit-reports/mutations.xml"
    
    coverageExt = 'branch.coverage.csv'

    mutationExt = 'mutation.csv'

    # Run the mutation for the current project
    print("Running mutation.................................", end="", flush=True)
    try:
        if not os.path.isfile(mutationsFile):
            mutationOutputFile = runMutation(root, folder, project)
        print("OK")
    except:
        print("failed")

    # Load the coverage files into CSVLoader obj
    try:
        statementCoverageFile = filterFiles(coverageFolder, project + '.' + id + 'f', coverageExt)[0]
        statementCSV = CSVLoader(statementCoverageFile) 
    except:
        print('Statement coverage files can NOT be loaded')

    # Load the mutation file into CSVLoader obj
    try:
        csvfilePath = root + "/resources/mutation/" + project + "/" + project + "." + id + "f." + "mutation.csv"
        if not os.path.isfile(csvfilePath):
            parseMutationsXML(mutationsFile, csvfilePath)
        mutationFile = filterFiles(mutationFolder, project + '.' + id + 'f', mutationExt)[0]
        mutationCSV = CSVLoader(mutationFile)
    except:
        
        print('Mutation file can NOT be loaded')
    
    # Load the real-faults files into fault_tests list
    try:
        realfaultFile = filterFiles(realfaultFolder, project + '.' + id + 'f', realfaultExt)[0]
        fault_tests = processRealFaultFile(realfaultFile)

    except:
        print('Real-fault files can NOT be loaded')

    mutContents = readFile(mutationFile)

    covContents = readFile(statementCoverageFile)
        
    killingTests, lineNumbers = getMutants(mutContents)

    coveringTests = getTestsExecutingMutants(covContents, lineNumbers)

    allTests = getAllTests(covContents)

    # calculate the original statement coverage
    totalStatementCoverage = statementCSV.getTotalCoverage()
    coverageObj = CoverageSelection(statementCSV, totalStatementCoverage,branch=True)

    # calculate the original mutation score 
    MS = mutationCSV.getTotalCoverage()

    print('statement coverage ', totalStatementCoverage)
    print('mutation score ', MS)

    ms_values = list()
    recalls = list()
    sizes = list()
    totalSize = len(allTests)

    # Calculate the RSM
    RSM, WSM, maxRank = getRankAndWieghtedStubborness(killingTests)
    
    # TODO: check the nature of all Rank 1 stubborn mutants
    stbNatureList = checkStubbornNature(folder, RSM, curRank, mutationsFile)

    # return data, stbNatureList

    # Find out all killable mutants
    allmutants, killingTestsAll = getKillableMutants(mutContents, totalSize)

    allmutants5Percent, killingTests5Percent = getKillableMutants(mutContents, totalSize, 0.05)
    evaluateMutantsImpact(mutationCSV, allmutants5Percent, killingTests5Percent, fault_tests, ms_values, recalls, sizes)

    allmutants2andhalfPercent, killingTests2andhalfPercent = getKillableMutants(mutContents, totalSize, 0.025)
    evaluateMutantsImpact(mutationCSV, allmutants2andhalfPercent, killingTests2andhalfPercent, fault_tests, ms_values, recalls, sizes)

    killablemutants = {'All':len(allmutants), 'Hard0.05':len(allmutants5Percent), 'Hard0.025':len(allmutants2andhalfPercent)}
    thresholdLabels = ['Hard0.05', 'Hard0.025']
    # print(f"All killable mutants are {len(allmutants)}, while hard0.05 mutants are {len(allmutants5Percent)}")

    for stbLevel in stubbornScoreThreshold:
        stubbornMutants, easyMutants = getStubbornMutants(RSM, maxRank, stbLevel)
        killablemutants[f'Stb{stbLevel}'] = len(stubbornMutants)
        thresholdLabels.append(f'Stb{stbLevel}')

        # Get the tests that kill the stubborn mutants
        allTestsKillingStubbon = set()
        for stbMut in stubbornMutants:
            killpool = killingTests[stbMut]
            allTestsKillingStubbon.update(killpool)
        
        evaluateMutantsImpact(mutationCSV, stubbornMutants, allTestsKillingStubbon, fault_tests, ms_values, recalls, sizes)

    # generate_csv(root, prj, id, MS, stubbornScoreThreshold, ms_values)

    data = generate_in_memory_data(id, MS, totalSize, thresholdLabels, ms_values, recalls, sizes)
    return data, stbNatureList, killablemutants

def evaluateMutantsImpact(mutationCSV, stubbornMutants, allTestsKillingStubbon, fault_tests, ms_values, recalls, sizes):
    score = evaluateMutationScore(mutationCSV.matrix, allTestsKillingStubbon, mutationCSV.listCols)
    recall = compute_overlap(allTestsKillingStubbon, fault_tests)
    ms_values.append(score)
    recalls.append(recall)
    sizes.append(len(stubbornMutants))
    
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

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        prj = "math"
        rank = 1
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

    loadAll = False
    if loadAll:
        all_natures = list()
        picklePath = f"{root}/resources/stubborn/natures/"
        summary_files = getAllFilesEndingWith(picklePath, '-nature-summary.pkl')
        for pickleFile in summary_files:
            cur_natures = loadDataStructure(pickleFile)
            all_natures.extend(cur_natures)
        
        # Generate the summary
        all_summary = generate_summary(all_natures)
        all_sorted_summary = sort_summary(all_summary)
        csvFile = f"{root}/resources/stubborn/all-nature-summary.csv"
        save_summary(all_sorted_summary, csvFile)
        exit()

    if prj == 'math':
        projects = [ '76', '80']

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
    dataList = list()
    natureList = list()

    # Initialize all killable mutants
    thresholdLabels = ['Hard0.05', 'Hard0.025']
    allkillablemutants = {'All':0, 'Hard0.05':0, 'Hard0.025':0}
    for lvl in stubbornScoreThresholdValues:
        allkillablemutants[f'Stb{lvl}'] = 0
        thresholdLabels.append(f'Stb{lvl}')

    for id in projects:
        # try:
        print('Running Project ' + str(id) + '...')
        data, stbNatureList, killablemutants = runExp(root, prj, id, 'all', stubbornScoreThresholdValues, rank)

        for key in allkillablemutants.keys():
            allkillablemutants[key] += killablemutants[key]
        
        dataList.append(data)
        natureList.extend(stbNatureList)
    

            # except:
            #     print('Project ' + str(id) + ' failed to run properly')

    get_summary_per_level(root, prj, dataList, thresholdLabels)
    # Combine all data and write to a single CSV file
    combine_data_and_write_csv(root, prj, dataList)

    # Define the CSV file name
    createFolder(root + '/resources/stubborn/natures/' )
    pickleFile = f"{root}/resources/stubborn/natures/{prj}-nature-summary.pkl"
    saveDataStructure(natureList, pickleFile)

    # Generate the summary
    summary = generate_summary(natureList)
    sorted_summary = sort_summary(summary)
    csvFile = f"{root}/resources/stubborn/{prj}-nature-summary.csv"
    save_summary(sorted_summary, csvFile)

    csvFile = f"{root}/resources/stubborn/natures/{prj}-all-killable-mutants.csv"
    write_dict_to_csv(allkillablemutants, csvFile)

    # Print the summary
    # for key, counter in summary.items():
    #     print(f"{key}:")
    #     for value, count in counter.items():
    #         print(f"  {value}: {count}")

            

    # Example to run from terminal:
    # python3 /home/islam/MyWork/New-work-2023/DBT-workbench/scripts/selection_after_coverage_stubborn_mutants.py time False Branch 0.001

    # Example to run from HPC:
    # bash /data/islam/DBT-workbench/scripts/bash/hpc-job-stubborn-selection.sh compress False Branch 0.75 0.5 0.25 0.15 0.1 0.05 0.03 0.02 0.01 0.005 0.003 0.002 0.001
