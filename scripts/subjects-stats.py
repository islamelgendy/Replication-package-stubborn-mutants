
import sys
import re
import csv
from utils.CSVLoader import CSVLoader
from utils.utilsIO import filterFiles
from typing import List

def writeCSVstats(file_name, data) -> None:
    # Initialize sums for each column
    total_mutants = total_randoop = total_evosuite = total_developer = total_sum = 0

    # Write to CSV file
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['ID', '#Mutants', '#Randoop', '#EvoSuite', '#Developer', 'Total'])
        
        # Write each row
        for key, stats in data.items():
            mutants = stats['mutants']
            randoop = stats['Randoop']
            evosuite = stats['Evosuite']
            developer = stats['Developer']
            total = stats['Total']

            # Write row data
            writer.writerow([key, mutants, randoop, evosuite, developer, total])

            # Update totals
            total_mutants += mutants
            total_randoop += randoop
            total_evosuite += evosuite
            total_developer += developer
            total_sum += total
        
        # Write the final row with sums
        writer.writerow(['Total', total_mutants, total_randoop, total_evosuite, total_developer, total_sum])

def countMethodsPerCategory(methods: List[str]):
    numRandoop = numEvosuite = numDeveloper = 0

    for mtd in methods:
        if re.match(r'RegressionTest\d+::test\d+', mtd):
            numRandoop += 1
        elif re.match(r'.+_ESTest::test\d+', mtd):
            numEvosuite += 1
        else:
            numDeveloper += 1

    return numRandoop, numEvosuite, numDeveloper

def getStatsForProject(root, project, id):
    stats = {}
    mutationFolder = root + "/resources/mutation/"
    similarityFolder = root + "/resources/similarity/"
    similarityExt = 'textSimilarity.csv'
    mutationExt = 'mutation.csv'

    # Find out how many mutants for this project
    try:
        mutationFile = filterFiles(mutationFolder, project + '.' + id + 'f', mutationExt)[0]
        mutationCSV = CSVLoader(mutationFile)
        stats['mutants'] = len(mutationCSV.listCols)
    except:
        print('Mutation file can NOT be loaded')

    # Load the textual similarity matrix
    try:
        similarityFile = filterFiles(similarityFolder, project + '.' + id + 'f', similarityExt)[0]
        simlarityCSV = CSVLoader(similarityFile)
        numRan, numEvo, numDev = countMethodsPerCategory(simlarityCSV.listMethods)
        stats['Randoop'] = numRan
        stats['Evosuite'] = numEvo
        stats['Developer'] = numDev
        stats['Total'] = numRan + numEvo + numDev
    except:
        print('Similarity matrix can NOT be loaded')
    
    return stats


if __name__ == "__main__":
    args = sys.argv
    lastSlashPos = args[0].rfind('/')
    secondToLastSlashPos = args[0][:lastSlashPos].rfind('/')
    root = args[0][:secondToLastSlashPos]
    prj = 'lang'

    if prj == 'math':
        projects = ['4', '5', '6', '9', '13', '14', '17', '18', '19',
                    '20', '21', '23', '24', '25', '26', '27', '28', 
                    '30', '32', '33', '37', '42', '47', '49', '50', 
                    '51', '52', '54', '56', '58', '61', '64', '65', 
                    '67', '68', '69', '70', '73', '76', '78', '80', '81']
    elif prj == 'jsoup':
        projects = [ '4', '15', '16', '19', '20', '26', '27', '29', 
                    '30', '33', '35', '36', '37', '38', '39', '40']
    elif prj == 'lang':
        projects = [ '4', '6', '15', '16', '17', '19', '22', '23', '24', '25', '27', '28', '31', '33', '35']
    elif prj == 'time':
        projects = ['11','13']
    elif prj == 'cli':
        projects = ['30','31','32','33','34']
    elif prj == 'csv':
        projects = ['2', '3', '4', '5', '7', '8', '10', '11', '12', '16']
    elif prj == 'compress':
        projects = ['1', '11', '16', '22', '24', '26', '27']

    data = {}
    for id in projects:
        # try:
            print('Running Project ' + str(id) + '...')
            stats = getStatsForProject(root, prj, id)
            data[id] = stats
    
    csvFile = root + '/resources/stats/' + prj + '.csv'
    writeCSVstats(csvFile, data)