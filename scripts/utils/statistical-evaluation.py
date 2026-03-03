import statistics
from scipy.stats import kruskal
from scipy.stats import mannwhitneyu
from itertools import combinations

def vargha_delaney_effect_size(group1, group2):
    """
    Computes the Vargha-Delaney A12 effect size for two groups.
    
    Parameters:
        group1: List of values for group 1
        group2: List of values for group 2
        
    Returns:
        A12: Vargha-Delaney effect size
    """
    n1, n2 = len(group1), len(group2)
    rank_sum = sum((x > y) + 0.5 * (x == y) for x in group1 for y in group2)
    A12 = rank_sum / (n1 * n2)
    return A12

def calculate_stats(dataset):
    """Calculate the average and standard deviation for each dataset entry."""
    stats = {}
    for key, values in dataset.items():
        avg = sum(values) / len(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0  # Standard deviation

        # Sort the values
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # If the number of elements is odd
        if n % 2 == 1:
            median = sorted_values[n // 2]
        else:  # If the number of elements is even
            mid1 = sorted_values[n // 2 - 1]
            mid2 = sorted_values[n // 2]
            median = (mid1 + mid2) / 2
        # stats[key] = {"average": avg, "median": median, "std_dev": std_dev}
        stats[key] = {"median": median, "std_dev": std_dev}
    return stats

def perform_statisticalTesting(groups, alpha):
    for (group1, data1), (group2, data2) in combinations(groups.items(), 2):
        stat, p = mannwhitneyu(data1, data2, alternative="two-sided")
        print(f"Comparing {group1} vs {group2}: U-statistic={stat:.4f}, p-value={p:.4f}")
        if p < alpha:
            print(f"  -> Significant difference between {group1} and {group2}")
        else:
            print(f"  -> No significant difference between {group1} and {group2}")
        
        print(f"  -> A12: {vargha_delaney_effect_size(data1, data2):.2f}")

def printConstants(project, stats, columns, APFD = True):
    print(f'% {project}')
    for col in columns:
        # avg = f"{stats.get(col, {'average': 'N/A'})['average']:.1f}"
        median = f"{stats.get(col, {'median': 'N/A'})['median']:.1f}"
        std_dev = f"{stats.get(col, {'std_dev': 'N/A'})['std_dev']:.1f}"
        if APFD:
            print("\\newcommand{}\\{}mean{}{}{}{}{}".format("{", project, col, "}", "{", avg, "}"))
            print("\\newcommand{}\\{}median{}{}{}{}{}".format("{", project, col, "}", "{", median, "}"))
            print("\\newcommand{}\\{}sd{}{}{}{}{}".format("{", project, col, "}", "{", std_dev, "}"))
        else:
            print("\\newcommand{}\\{}mean{}Realfault{}{}{}{}".format("{", project, col, "}", "{", avg, "}"))
            print("\\newcommand{}\\{}median{}Realfault{}{}{}{}".format("{", project, col, "}", "{", median, "}"))
            print("\\newcommand{}\\{}sd{}Realfault{}{}{}{}".format("{", project, col, "}", "{", std_dev, "}"))
         
def setDataSet(prj, dataset_APFD, dataset_RF, dataset_runtime):
    if prj == 'all':
        dataset_APFD['bytecode'] = bytecode_APFD_all
        dataset_APFD['text'] = text_APFD_all
        dataset_APFD['fast'] = fast_APFD_all
        dataset_APFD['fast-bytecode'] = fast_bytecode_APFD_all
        dataset_APFD['covTot'] = coverage_APFD_all
        dataset_APFD['covAdd'] = coverageAdd_APFD_all

        dataset_RF['bytecode'] = bytecode_RF_all
        dataset_RF['text'] = text_RF_all
        dataset_RF['fast'] = fast_RF_all
        dataset_RF['fast-bytecode'] = fast_bytecode_RF_all
        dataset_RF['covTot'] = coverage_RF_all
        dataset_RF['covAdd'] = coverageAdd_RF_all

        dataset_runtime['bytecode-prep'] = all_runtime_bytecode_prep
        dataset_runtime['bytecode-prioritise'] = all_runtime_bytecode_prioritise
        dataset_runtime['text-prep'] = all_runtime_text_prep
        dataset_runtime['text-prioritise'] = all_runtime_text_prioritise
        dataset_runtime['fast-prep'] = all_runtime_fast_prep
        dataset_runtime['fast-prioritise'] = all_runtime_fast_prioritise
        dataset_runtime['covTot'] = all_runtime_covTot_prioritise
        dataset_runtime['covAdd'] = all_runtime_covAdd_prioritise
    elif prj == 'cli':
        dataset_APFD['bytecode'] = cli_APFD_bytecode_values
        dataset_APFD['text'] = cli_APFD_text
        dataset_APFD['fast'] = cli_APFD_fast_pw
        dataset_APFD['covTot'] = cli_APFD_coverage
        dataset_APFD['covAdd'] = cli_APFD_coverageAdditional

        dataset_RF['bytecode'] = cli_RF_bytecode_values
        dataset_RF['text'] = cli_RF_text
        dataset_RF['fast'] = cli_RF_fast_pw
        dataset_RF['covTot'] = cli_RF_coverage
        dataset_RF['covAdd'] = cli_RF_coverageAdditional

        dataset_runtime['bytecode-prep'] = cli_runtime_bytecode_prep
        dataset_runtime['bytecode-prioritise'] = cli_runtime_bytecode_prioritise
        dataset_runtime['text-prep'] = cli_runtime_text_prep
        dataset_runtime['text-prioritise'] = cli_runtime_text_prioritise
        dataset_runtime['fast-prep'] = cli_runtime_fast_prep
        dataset_runtime['fast-prioritise'] = cli_runtime_fast_prioritise
        dataset_runtime['covTot'] = cli_runtime_covTot_prioritise
        dataset_runtime['covAdd'] = cli_runtime_covAdd_prioritise
    elif prj == 'compress':
        dataset_APFD['bytecode'] = compress_APFD_bytecode_values
        dataset_APFD['text'] = compress_APFD_text
        dataset_APFD['fast'] = compress_APFD_fast_pw
        dataset_APFD['covTot'] = compress_APFD_coverage
        dataset_APFD['covAdd'] = compress_APFD_coverageAdditional

        dataset_RF['bytecode'] = compress_RF_bytecode_values
        dataset_RF['text'] = compress_RF_text
        dataset_RF['fast'] = compress_RF_fast_pw
        dataset_RF['covTot'] = compress_RF_coverage
        dataset_RF['covAdd'] = compress_RF_coverageAdditional

        dataset_runtime['bytecode-prep'] = compress_runtime_bytecode_prep
        dataset_runtime['bytecode-prioritise'] = compress_runtime_bytecode_prioritise
        dataset_runtime['text-prep'] = compress_runtime_text_prep
        dataset_runtime['text-prioritise'] = compress_runtime_text_prioritise
        dataset_runtime['fast-prep'] = compress_runtime_fast_prep
        dataset_runtime['fast-prioritise'] = compress_runtime_fast_prioritise
        dataset_runtime['covTot'] = compress_runtime_covTot_prioritise
        dataset_runtime['covAdd'] = compress_runtime_covAdd_prioritise
    elif prj == 'csv':
        dataset_APFD['bytecode'] = csv_APFD_bytecode_values
        dataset_APFD['text'] = csv_APFD_text
        dataset_APFD['fast'] = csv_APFD_fast_pw
        dataset_APFD['covTot'] = csv_APFD_coverage
        dataset_APFD['covAdd'] = csv_APFD_coverageAdditional

        dataset_RF['bytecode'] = csv_RF_bytecode_values
        dataset_RF['text'] = csv_RF_text
        dataset_RF['fast'] = csv_RF_fast_pw
        dataset_RF['covTot'] = csv_RF_coverage
        dataset_RF['covAdd'] = csv_RF_coverageAdditional

        dataset_runtime['bytecode-prep'] = csv_runtime_bytecode_prep
        dataset_runtime['bytecode-prioritise'] = csv_runtime_bytecode_prioritise
        dataset_runtime['text-prep'] = csv_runtime_text_prep
        dataset_runtime['text-prioritise'] = csv_runtime_text_prioritise
        dataset_runtime['fast-prep'] = csv_runtime_fast_prep
        dataset_runtime['fast-prioritise'] = csv_runtime_fast_prioritise
        dataset_runtime['covTot'] = csv_runtime_covTot_prioritise
        dataset_runtime['covAdd'] = csv_runtime_covAdd_prioritise
    elif prj == 'jsoup':
        dataset_APFD['bytecode'] = jsoup_APFD_bytecode_values
        dataset_APFD['text'] = jsoup_APFD_text
        dataset_APFD['fast'] = jsoup_APFD_fast_pw
        dataset_APFD['covTot'] = jsoup_APFD_coverage
        dataset_APFD['covAdd'] = jsoup_APFD_coverageAdditional

        dataset_RF['bytecode'] = jsoup_RF_bytecode_values
        dataset_RF['text'] = jsoup_RF_text
        dataset_RF['fast'] = jsoup_RF_fast_pw
        dataset_RF['covTot'] = jsoup_RF_coverage
        dataset_RF['covAdd'] = jsoup_RF_coverageAdditional

        dataset_runtime['bytecode-prep'] = jsoup_runtime_bytecode_prep
        dataset_runtime['bytecode-prioritise'] = jsoup_runtime_bytecode_prioritise
        dataset_runtime['text-prep'] = jsoup_runtime_text_prep
        dataset_runtime['text-prioritise'] = jsoup_runtime_text_prioritise
        dataset_runtime['fast-prep'] = jsoup_runtime_fast_prep
        dataset_runtime['fast-prioritise'] = jsoup_runtime_fast_prioritise
        dataset_runtime['covTot'] = jsoup_runtime_covTot_prioritise
        dataset_runtime['covAdd'] = jsoup_runtime_covAdd_prioritise
    elif prj == 'lang':
        dataset_APFD['bytecode'] = lang_APFD_bytecode_values
        dataset_APFD['text'] = lang_APFD_text
        dataset_APFD['fast'] = lang_APFD_fast_pw
        dataset_APFD['covTot'] = lang_APFD_coverage
        dataset_APFD['covAdd'] = lang_APFD_coverageAdditional

        dataset_RF['bytecode'] = lang_RF_bytecode_values
        dataset_RF['text'] = lang_RF_text
        dataset_RF['fast'] = lang_RF_fast_pw
        dataset_RF['covTot'] = lang_RF_coverage
        dataset_RF['covAdd'] = lang_RF_coverageAdditional

        dataset_runtime['bytecode-prep'] = lang_runtime_bytecode_prep
        dataset_runtime['bytecode-prioritise'] = lang_runtime_bytecode_prioritise
        dataset_runtime['text-prep'] = lang_runtime_text_prep
        dataset_runtime['text-prioritise'] = lang_runtime_text_prioritise
        dataset_runtime['fast-prep'] = lang_runtime_fast_prep
        dataset_runtime['fast-prioritise'] = lang_runtime_fast_prioritise
        dataset_runtime['covTot'] = lang_runtime_covTot_prioritise
        dataset_runtime['covAdd'] = lang_runtime_covAdd_prioritise
    elif prj == 'math':
        dataset_APFD['bytecode'] = math_APFD_bytecode_values
        dataset_APFD['text'] = math_APFD_text
        dataset_APFD['fast'] = math_APFD_fast_pw
        dataset_APFD['covTot'] = math_APFD_coverage
        dataset_APFD['covAdd'] = math_APFD_coverageAdditional

        dataset_RF['bytecode'] = math_RF_bytecode_values
        dataset_RF['text'] = math_RF_text
        dataset_RF['fast'] = math_RF_fast_pw
        dataset_RF['covTot'] = math_RF_coverage
        dataset_RF['covAdd'] = math_RF_coverageAdditional

        dataset_runtime['bytecode-prep'] = math_runtime_bytecode_prep
        dataset_runtime['bytecode-prioritise'] = math_runtime_bytecode_prioritise
        dataset_runtime['text-prep'] = math_runtime_text_prep
        dataset_runtime['text-prioritise'] = math_runtime_text_prioritise
        dataset_runtime['fast-prep'] = math_runtime_fast_prep
        dataset_runtime['fast-prioritise'] = math_runtime_fast_prioritise
        dataset_runtime['covTot'] = math_runtime_covTot_prioritise
        dataset_runtime['covAdd'] = math_runtime_covAdd_prioritise
    elif prj == 'time':
        dataset_APFD['bytecode'] = time_APFD_bytecode_values
        dataset_APFD['text'] = time_APFD_text
        dataset_APFD['fast'] = time_APFD_fast_pw
        dataset_APFD['covTot'] = time_APFD_coverage
        dataset_APFD['covAdd'] = time_APFD_coverageAdditional

        dataset_RF['bytecode'] = time_RF_bytecode_values
        dataset_RF['text'] = time_RF_text
        dataset_RF['fast'] = time_RF_fast_pw
        dataset_RF['covTot'] = time_RF_coverage
        dataset_RF['covAdd'] = time_RF_coverageAdditional

        dataset_runtime['bytecode-prep'] = time_runtime_bytecode_prep
        dataset_runtime['bytecode-prioritise'] = time_runtime_bytecode_prioritise
        dataset_runtime['text-prep'] = time_runtime_text_prep
        dataset_runtime['text-prioritise'] = time_runtime_text_prioritise
        dataset_runtime['fast-prep'] = time_runtime_fast_prep
        dataset_runtime['fast-prioritise'] = time_runtime_fast_prioritise
        dataset_runtime['covTot'] = time_runtime_covTot_prioritise
        dataset_runtime['covAdd'] = time_runtime_covAdd_prioritise

def getTotalTime(prepTime, prioritiseTime):
    totalTime = list()
    size = len(prepTime)

    for i in range(size):
        totalTime.append(prepTime[i] + prioritiseTime[i])

    return totalTime

def setGroups(prj):
    if prj == 'all':
        groups_APFD = {"Bytecode_Div": bytecode_APFD_all, "Text_Div": text_APFD_all, "FAST_pw": fast_APFD_all, "FAST_bytecode": fast_bytecode_APFD_all, "Coverage_Tot": coverage_APFD_all, "coverage_Add": coverageAdd_APFD_all}
        groups_RF = {"Bytecode_Div": bytecode_RF_all, "Text_Div": text_RF_all, "FAST_pw": fast_RF_all, "FAST_bytecode": fast_bytecode_RF_all,"Coverage_Tot": coverage_RF_all, "coverage_Add": coverageAdd_RF_all}
        groups_runtime = {"Bytecode_Div": getTotalTime(all_runtime_bytecode_prep, all_runtime_bytecode_prioritise), 
                          "Text_Div": getTotalTime(all_runtime_text_prep, all_runtime_text_prioritise), 
                          "FAST_pw": getTotalTime(all_runtime_fast_prep, all_runtime_fast_prioritise), 
                          "Coverage_Tot": all_runtime_covTot_prioritise, 
                          "coverage_Add": all_runtime_covAdd_prioritise}
    elif prj == 'cli':
        groups_APFD = {"Bytecode_Div": cli_APFD_bytecode_values, "Text_Div": cli_APFD_text, "FAST_pw": cli_APFD_fast_pw, "Coverage_Tot": cli_APFD_coverage, "coverage_Add": cli_APFD_coverageAdditional}
        groups_RF = {"Bytecode_Div": cli_RF_bytecode_values, "Text_Div": cli_RF_text, "FAST_pw": cli_RF_fast_pw, "Coverage_Tot": cli_RF_coverage, "coverage_Add": cli_RF_coverageAdditional}
        groups_runtime = {"Bytecode_Div": getTotalTime(cli_runtime_bytecode_prep, cli_runtime_bytecode_prioritise), 
                          "Text_Div": getTotalTime(cli_runtime_text_prep, cli_runtime_text_prioritise), 
                          "FAST_pw": getTotalTime(cli_runtime_fast_prep, cli_runtime_fast_prioritise), 
                          "Coverage_Tot": cli_runtime_covTot_prioritise, 
                          "coverage_Add": cli_runtime_covAdd_prioritise}
    elif prj == 'compress':
        groups_APFD = {"Bytecode_Div": compress_APFD_bytecode_values, "Text_Div": compress_APFD_text, "FAST_pw": compress_APFD_fast_pw, "Coverage_Tot": compress_APFD_coverage, "coverage_Add": compress_APFD_coverageAdditional}
        groups_RF = {"Bytecode_Div": compress_RF_bytecode_values, "Text_Div": compress_RF_text, "FAST_pw": compress_RF_fast_pw, "Coverage_Tot": compress_RF_coverage, "coverage_Add": compress_RF_coverageAdditional}
        groups_runtime = {"Bytecode_Div": getTotalTime(compress_runtime_bytecode_prep, compress_runtime_bytecode_prioritise), 
                          "Text_Div": getTotalTime(compress_runtime_text_prep, compress_runtime_text_prioritise), 
                          "FAST_pw": getTotalTime(compress_runtime_fast_prep, compress_runtime_fast_prioritise), 
                          "Coverage_Tot": compress_runtime_covTot_prioritise, 
                          "coverage_Add": compress_runtime_covAdd_prioritise}
    elif prj == 'csv':
        groups_APFD = {"Bytecode_Div": csv_APFD_bytecode_values, "Text_Div": csv_APFD_text, "FAST_pw": csv_APFD_fast_pw, "Coverage_Tot": csv_APFD_coverage, "coverage_Add": csv_APFD_coverageAdditional}
        groups_RF = {"Bytecode_Div": csv_RF_bytecode_values, "Text_Div": csv_RF_text, "FAST_pw": csv_RF_fast_pw, "Coverage_Tot": csv_RF_coverage, "coverage_Add": csv_RF_coverageAdditional}
        groups_runtime = {"Bytecode_Div": getTotalTime(csv_runtime_bytecode_prep, csv_runtime_bytecode_prioritise), 
                          "Text_Div": getTotalTime(csv_runtime_text_prep, csv_runtime_text_prioritise), 
                          "FAST_pw": getTotalTime(csv_runtime_fast_prep, csv_runtime_fast_prioritise), 
                          "Coverage_Tot": csv_runtime_covTot_prioritise, 
                          "coverage_Add": csv_runtime_covAdd_prioritise}
    elif prj == 'jsoup':
        groups_APFD = {"Bytecode_Div": jsoup_APFD_bytecode_values, "Text_Div": jsoup_APFD_text, "FAST_pw": jsoup_APFD_fast_pw, "Coverage_Tot": jsoup_APFD_coverage, "coverage_Add": jsoup_APFD_coverageAdditional}
        groups_RF = {"Bytecode_Div": jsoup_RF_bytecode_values, "Text_Div": jsoup_RF_text, "FAST_pw": jsoup_RF_fast_pw, "Coverage_Tot": jsoup_RF_coverage, "coverage_Add": jsoup_RF_coverageAdditional}
        groups_runtime = {"Bytecode_Div": getTotalTime(jsoup_runtime_bytecode_prep, jsoup_runtime_bytecode_prioritise), 
                          "Text_Div": getTotalTime(jsoup_runtime_text_prep, jsoup_runtime_text_prioritise), 
                          "FAST_pw": getTotalTime(jsoup_runtime_fast_prep, jsoup_runtime_fast_prioritise), 
                          "Coverage_Tot": jsoup_runtime_covTot_prioritise, 
                          "coverage_Add": jsoup_runtime_covAdd_prioritise}
    elif prj == 'lang':
        groups_APFD = {"Bytecode_Div": lang_APFD_bytecode_values, "Text_Div": lang_APFD_text, "FAST_pw": lang_APFD_fast_pw, "Coverage_Tot": lang_APFD_coverage, "coverage_Add": lang_APFD_coverageAdditional}
        groups_RF = {"Bytecode_Div": lang_RF_bytecode_values, "Text_Div": lang_RF_text, "FAST_pw": lang_RF_fast_pw, "Coverage_Tot": lang_RF_coverage, "coverage_Add": lang_RF_coverageAdditional}
        groups_runtime = {"Bytecode_Div": getTotalTime(lang_runtime_bytecode_prep, lang_runtime_bytecode_prioritise), 
                          "Text_Div": getTotalTime(lang_runtime_text_prep, lang_runtime_text_prioritise), 
                          "FAST_pw": getTotalTime(lang_runtime_fast_prep, lang_runtime_fast_prioritise), 
                          "Coverage_Tot": lang_runtime_covTot_prioritise, 
                          "coverage_Add": lang_runtime_covAdd_prioritise}
    elif prj == 'math':
        groups_APFD = {"Bytecode_Div": math_APFD_bytecode_values, "Text_Div": math_APFD_text, "FAST_pw": math_APFD_fast_pw, "Coverage_Tot": math_APFD_coverage, "coverage_Add": math_APFD_coverageAdditional}
        groups_RF = {"Bytecode_Div": math_RF_bytecode_values, "Text_Div": math_RF_text, "FAST_pw": math_RF_fast_pw, "Coverage_Tot": math_RF_coverage, "coverage_Add": math_RF_coverageAdditional}
        groups_runtime = {"Bytecode_Div": getTotalTime(math_runtime_bytecode_prep, math_runtime_bytecode_prioritise), 
                          "Text_Div": getTotalTime(math_runtime_text_prep, math_runtime_text_prioritise), 
                          "FAST_pw": getTotalTime(math_runtime_fast_prep, math_runtime_fast_prioritise), 
                          "Coverage_Tot": math_runtime_covTot_prioritise, 
                          "coverage_Add": math_runtime_covAdd_prioritise}
    elif prj == 'time':
        groups_APFD = {"Bytecode_Div": time_APFD_bytecode_values, "Text_Div": time_APFD_text, "FAST_pw": time_APFD_fast_pw, "Coverage_Tot": time_APFD_coverage, "coverage_Add": time_APFD_coverageAdditional}
        groups_RF = {"Bytecode_Div": time_RF_bytecode_values, "Text_Div": time_RF_text, "FAST_pw": time_RF_fast_pw, "Coverage_Tot": time_RF_coverage, "coverage_Add": time_RF_coverageAdditional}
        groups_runtime = {"Bytecode_Div": getTotalTime(time_runtime_bytecode_prep, time_runtime_bytecode_prioritise), 
                          "Text_Div": getTotalTime(time_runtime_text_prep, time_runtime_text_prioritise), 
                          "FAST_pw": getTotalTime(time_runtime_fast_prep, time_runtime_fast_prioritise), 
                          "Coverage_Tot": time_runtime_covTot_prioritise, 
                          "coverage_Add": time_runtime_covAdd_prioritise}
    
    return groups_APFD, groups_RF, groups_runtime

# Cli - APFD
# cli_APFD_bytecode_values = [79.98, 92.93, 94.24, 95.85, 93.38]    # Filtered big
# cli_APFD_bytecode_values = [59.08, 86.88, 94.75, 92.98, 85.84]    # All bytecode
cli_APFD_bytecode_values = [64.92, 87.86, 96.54, 96.33, 87.07]      # Filtered small
cli_APFD_text = [50.99, 87.28, 95.37, 93.46, 82.11]
cli_APFD_fast_pw = [93.74, 90.26, 93.75, 96.99, 96.08]
cli_APFD_fast_bytecode = [96.09, 87.85, 95.02, 97.06, 93.06]
# cli_APFD_fast_bytecode = [96.77, 91.25, 95.32, 97.06, 90.3]        # Filtered small
cli_APFD_coverage = [96.34, 89.21, 98.04, 97.14, 86.42]
cli_APFD_coverageAdditional = [98.98, 95.98, 97.65, 99.2, 95.22]

# Cli - RealFaults
# cli_RF_bytecode_values = [363, 693, 10, 443, 108]     # Filtered big
# cli_RF_bytecode_values = [701, 896, 42, 641, 200]     # All bytecode
cli_RF_bytecode_values = [689, 299, 38, 445, 75]       # Filtered small
cli_RF_text = [1173, 617, 110, 263, 193]
cli_RF_fast_pw = [1265, 505, 3, 9, 10]
cli_RF_fast_bytecode = [162, 294, 11, 34, 4]
# cli_RF_fast_bytecode = [71, 145, 2, 17, 8]        # Filtered small
cli_RF_coverage = [9, 352, 1, 213, 722]
cli_RF_coverageAdditional = [6, 53, 1, 31, 36]

# Cli - runtime
cli_runtime_fast_prep = [33.14,4.97,2.51,2.61,5.65,48.88]
cli_runtime_fast_prioritise = [2.28,3.17,0.88,0.63,3.06,10.02]
cli_runtime_bytecode_prep = [4.04,3.43,0.82,0.81,4.87,13.97]
cli_runtime_bytecode_prioritise = [183.82,405.52,40.37,26.22,381.31,1037.24]
cli_runtime_text_prep = [95995.26,22654.98,3012.38,4882.04,51236.13,177780.79]
cli_runtime_text_prioritise = [197.4,462.52,52.19,27.74,421.82,1161.67]
cli_runtime_covTot_prioritise = [10.77,16.2,1.8,1.26,5.44,35.47]
cli_runtime_covAdd_prioritise = [12.93,18.21,2.55,1.87,7.07,42.63]

# Compress - APFD
# compress_APFD_bytecode_values = [64.25, 89.07, 90.18, 80.34, 93.88, 94.76, 91.1]  # Filtered big
# compress_APFD_bytecode_values = [46.29, 75.96, 89.73, 82.28, 96.16, 93.81, 92.09]    # All bytecode
compress_APFD_bytecode_values = [54.18, 76.9, 81.75, 73.81, 97.05, 93.52, 93.38]  # Filtered small
compress_APFD_text = [53.84, 75.36, 79.94, 81.22, 86.8, 99.08, 88.77]
compress_APFD_fast_pw = [85.84, 98.28, 95.32, 84.92, 97.8, 99.87, 91.3]
compress_APFD_fast_bytecode = [95.98, 98.58, 96.58, 90.39, 99.29, 99.91, 98.74]
# compress_APFD_fast_bytecode = [99.45, 98.95, 97.11, 91.45, 99.47, 99.91, 99.45]        # Filtered small
compress_APFD_coverage = [99.59, 82.48, 93.2, 81.22, 95.02, 99.98, 81.98]
compress_APFD_coverageAdditional = [99.7, 98.96, 98.91, 92.86, 97.47, 99.98, 93.22]

# Compress - RealFaults
# compress_RF_bytecode_values = [965, 2, 176, 39, 149, 6, 51]  # Filtered big
# compress_RF_bytecode_values = [456, 367, 136, 16, 341, 2, 225]   # All bytecode
compress_RF_bytecode_values = [965, 330, 145, 14, 288, 10, 157]  # Filtered small
compress_RF_text = [382, 322, 158, 16, 318, 27, 268]
compress_RF_fast_pw = [17, 17, 3, 6, 3, 4, 199]
compress_RF_fast_bytecode = [3, 6, 2, 43, 3, 311]
# compress_RF_fast_bytecode = [52, 2, 3, 1, 7, 3, 21]        # Filtered small
compress_RF_coverage = [13, 244, 36, 1, 1315, 1, 422]
compress_RF_coverageAdditional = [11, 2, 2, 1, 9, 1, 4]

# Compress - runtime
compress_runtime_fast_prep = [7.89,2.53,1.52,0.56,8.75,6.48,9]
compress_runtime_fast_prioritise = [4.47,0.57,0.25,0.16,4.92,4.88,4.96]
compress_runtime_bytecode_prep = [16.36,1.4,0.25,0.01,26.83,19.52,34.88]
compress_runtime_bytecode_prioritise = [606.22,3.34,0.76,0.01,730.02,595.19,751.48]
compress_runtime_text_prep = [144054.05,25601.66,1891.46,25.16,128696.65,80825.08,124760.89]
compress_runtime_text_prioritise = [654.48,3.46,0.82,0.01,797.79,750.53,796.56]
compress_runtime_covTot_prioritise = [5.44,0.29,0.11,0.03,11.36,2.69,9.42]
compress_runtime_covAdd_prioritise = [7.83,0.35,0.15,0.04,13.43,3.38,12.44]

# Csv - APFD
# csv_APFD_bytecode_values = [93.01, 88.63, 88.79, 59.83, 88.34, 99.98, 75.22, 84.46, 99.98, 86.3]  # Filtered big
# csv_APFD_bytecode_values = [85.75, 85.78, 85.15, 49.2, 85.46, 99.98, 72.49, 79.52, 99.98, 83.37]     # All bytecode
csv_APFD_bytecode_values = [90.41, 88.33, 88.5, 55.02, 88.34, 99.98, 75.49, 83.99, 99.98, 85.86]  # Filtered small
csv_APFD_text = [87.39, 86.37, 83.93, 45.8, 85.25, 99.98, 74.56, 76.0, 99.93, 81.81]
csv_APFD_fast_pw = [99.54, 62.93, 65.07, 66.7, 70.56, 99.98, 55.84, 95.44, 99.93, 60.33]
csv_APFD_fast_bytecode = [99.73, 98.92, 97.52, 94.68, 95.75, 99.93, 96.0, 97.03, 99.56, 92.79]
# csv_APFD_fast_bytecode = [96.35, 96.26, 94.02, 95.6, 94.49, 99.88, 93.69, 91.5, 99.93, 88.64]        # Filtered small
csv_APFD_coverage = [84.21, 92.7, 79.09, 80.93, 83.52, 99.98, 89.08, 83.95, 99.93, 86.2]
csv_APFD_coverageAdditional = [99.82, 83.9, 84.99, 84.88, 81.19, 99.98, 82.77, 78.96, 99.93, 80.53]

# Csv - RealFaults
# csv_RF_bytecode_values = [492, 61, 1220, 381, 652, 272, 18, 336, 851, 86]         # Filtered big
# csv_RF_bytecode_values = [1221, 119, 1772, 681, 1037, 1427, 253, 325, 550, 68]      # All bytecode
csv_RF_bytecode_values = [1084, 17, 1636, 627, 720, 629, 126, 353, 676, 50]         # Filtered small
csv_RF_text = [168, 103, 1564, 865, 916, 1865, 551, 495, 659, 80]
csv_RF_fast_pw = [6, 1797, 1775, 425, 798, 1951, 697, 15, 1764, 1004]
csv_RF_fast_bytecode = [3, 36, 45, 43, 4, 3, 29, 18, 90, 399]
# csv_RF_fast_bytecode = [46, 137, 135, 64, 61, 596, 28, 285, 1092, 639]        # Filtered small
csv_RF_coverage = [1770, 6, 950, 406, 81, 1884, 177, 18, 16, 102]
csv_RF_coverageAdditional = [2015, 12, 1956, 1268, 5, 2009, 742, 6, 2049, 1177]

# Csv - runtime
csv_runtime_fast_prep = [5.26,6.35,6.22,6.02,4.18,5.15,3.04,3.25,5.86,4.16]
csv_runtime_fast_prioritise = [2.75,2.94,2.71,1.23,1.01,3.57,0.45,0.7,3.12,1.02]
csv_runtime_bytecode_prep = [5.19,6.55,4.88,7.77,2.65,3.3,0.91,1.08,4.72,1.14]
csv_runtime_bytecode_prioritise = [322.05,375.81,322.36,87.94,61.38,367.63,12.27,29.19,425.68,54.6]
csv_runtime_text_prep = [21980.34,43121.32,37589.75,87609.76,14627.43,31301.62,18891.55,12076.68,33471.6,16405.23]
csv_runtime_text_prioritise = [377.13,413.68,362.53,91.52,67.65,425.03,13.22,31.97,466.3,69.7]
csv_runtime_covTot_prioritise = [1.39,2.1,3.46,2.46,1.22,11.17,0.92,0.83,11.16,1.35]
csv_runtime_covAdd_prioritise = [1.38,2.96,4.46,3.35,1.69,13.98,1.23,1.17,14.48,1.95]

# Jsoup - APFD
# Filtered big
# jsoup_APFD_bytecode_values = [78.27, 79.54, 60.75, 87.95, 94.65, 83.12, 93.79, 94.97, 85.48, 85.55, 82.93, 96.84, 88.82, 77.7, 92.23, 94.49]
# All bytecode
# jsoup_APFD_bytecode_values = [69.71, 77.67, 56.45, 73.12, 89.64, 81.63, 88.55, 92.06, 72.44, 77.41, 84.44, 92.25, 86.71, 77.32, 88.65, 95.13]
# Filtered small
jsoup_APFD_bytecode_values = [78.06, 78.77, 60.08, 74.33, 93.03, 81.65, 96.24, 92.79, 73.17, 80.15, 90.08, 93.82, 88.79, 81.69, 91.63, 97.44]
jsoup_APFD_text = [70.76, 78.54, 75.4, 68.51, 87.62, 73.1, 96.52, 97.48, 70.77, 81.94, 84.0, 83.87, 88.62, 79.55, 89.1, 98.97]
jsoup_APFD_fast_pw = [95.76, 63.44, 64.25, 62.36, 88.55, 96.05, 94.32, 87.45, 67.77, 58.39, 85.43, 85.1, 81.2, 70.33, 93.57, 96.79]
jsoup_APFD_fast_bytecode = [91.48, 93.87, 90.32, 85.53, 96.95, 91.73, 88.9, 96.32, 85.89, 80.12, 97.49, 76.91, 81.23, 79.69, 55.73, 66.54]
# jsoup_APFD_fast_bytecode = [97.19, 98.66, 98.25, 90.05, 98.12, 91.07, 91.35, 86.9, 91.94, 82.54, 72.07, 88.36, 80.2, 59.89, 92.43, 74.74]        # Filtered small
jsoup_APFD_coverage = [93.33, 96.44, 98.39, 91.78, 94.28, 84.29, 96.88, 98.33, 83.24, 88.35, 98.84, 89.08, 92.09, 98.46, 91.15, 99.23]
jsoup_APFD_coverageAdditional = [98.95, 99.24, 98.92, 90.07, 92.75, 90.37, 97.59, 96.18, 94.09, 87.81, 92.07, 68.17, 89.01, 92.01, 85.89, 98.72]

# Jsoup - RealFaults
# jsoup_RF_bytecode_values = [18, 702, 88, 180, 8, 13, 3, 1947, 49, 1766, 2080, 1, 947, 1455, 10, 1] # Filtered big
# jsoup_RF_bytecode_values = [1, 642, 100, 416, 12, 10, 4, 941, 8, 2800, 2952, 3, 1884, 2159, 14, 1]   # All bytecode
jsoup_RF_bytecode_values = [1, 687, 75, 339, 11, 12, 1, 1118, 11, 2745, 3339, 2, 1614, 1908, 7, 1] # Filtered small
jsoup_RF_text = [1, 736, 2, 482, 20, 11, 3, 1664, 38, 1205, 2493, 46, 2140, 2193, 3, 1]
jsoup_RF_fast_pw = [44, 1108, 3, 649, 5, 25, 2, 3653, 255, 2599, 3445, 26, 2404, 2418, 10, 2]
jsoup_RF_fast_bytecode = [17, 119, 3, 210, 9, 106, 3, 412, 94, 719, 195, 5, 1193, 890, 86, 2]
# jsoup_RF_fast_bytecode = [10, 31, 2, 8, 6, 21, 4, 3270, 15, 529, 2601, 11, 1887, 2142, 6, 2]        # Filtered small
jsoup_RF_coverage = [1, 128, 1, 5, 3, 22, 1, 690, 1, 495, 49, 5, 1507, 26, 7, 2]
jsoup_RF_coverageAdditional = [1, 14, 1, 2, 4, 3, 1, 3, 1, 3, 41, 6, 3763, 19, 4, 2]

# Jsoup - runtime
jsoup_runtime_fast_prep = [0.54,6.13,1.02,3.2,0.4,3.84,0.19,12.76,1.67,11.32,14.23,0.83,12.51,10.15,0.56,1]
jsoup_runtime_fast_prioritise = [0.02,1.43,0.03,0.35,0.02,0.59,0,10.64,0.14,6.9,9.53,0.05,10.11,4.29,0.01,0.03]
jsoup_runtime_bytecode_prep = [0.18,2.94,0.05,0.91,0.01,1.7,0.01,11.3,0.23,12.45,13.41,0.02,20.16,9.87,0.01,0.03]
jsoup_runtime_bytecode_prioritise = [0.08,125.05,0.14,8.24,0.09,18.17,0,2353.46,1.64,1418.47,2226.98,0.24,2412.37,639.21,0.03,0.16]
jsoup_runtime_text_prep = [5.9,544.15,6.05,108.72,1.49,32141.62,0.98,423185.88,4415.67,188441.43,293380.44,46.1,307938.11,217232.11,13.62,361.26]
jsoup_runtime_text_prioritise = [0.08,131.74,0.14,8.51,0.1,20.25,0.01,2731.66,1.7,1552.27,2488.83,0.27,2707.9,710.18,0.03,0.16]
jsoup_runtime_covTot_prioritise = [0.01,30.01,0,0.4,0.01,0.18,0,8.78,0.05,44.46,231.64,0.04,32.02,98.47,0.01,0]
jsoup_runtime_covAdd_prioritise = [0.01,38.89,0.01,0.62,0.02,0.27,0.01,12.16,0.08,53.34,294.3,0.05,40.16,128.71,0.01,0.01]

# Lang - APFD
# Filtered big
# lang_APFD_bytecode_values = [83.47, 93.43, 61.37, 95.96, 99.3, 95.41, 99.25, 82.2, 96.23, 99.37, 96.22, 95.96, 87.42, 89.53, 82.29]
# All bytecode
# lang_APFD_bytecode_values = [99.88, 97.08, 56.68, 96.59, 99.68, 91.59, 98.99, 78.63, 97.51, 92.25, 96.4, 88.46, 93.48, 88.56, 93.26]
# Filtered small
lang_APFD_bytecode_values = [99.97, 96.84, 65.85, 96.6, 99.56, 93.41, 99.21, 81.5, 97.27, 98.78, 96.59, 92.07, 94.55, 89.43, 93.89]
lang_APFD_text = [99.88, 96.67, 69.25, 90.94, 99.78, 86.73, 98.86, 75.06, 91.98, 98.24, 88.54, 83.35, 92.27, 89.28, 92.18]
lang_APFD_fast_pw = [99.42, 97.78, 57.41, 55.46, 98.46, 83.78, 93.9, 23.26, 65.19, 99.63, 15.06, 82.44, 71.36, 81.7, 86.98]
lang_APFD_fast_bytecode = [99.88, 97.83, 65.31, 92.36, 93.64, 91.81, 92.91, 35.88, 97.26, 99.48, 76.9, 74.91, 90.26, 63.94, 89.89]
# lang_APFD_fast_bytecode = [99.46, 97.8, 59.42, 46.39, 93.99, 99.8, 91.85, 75.51, 47.87, 99.49, 16.15, 82.22, 74.45, 67.32, 81.91]        # Filtered small
lang_APFD_coverage = [99.97, 95.94, 95.07, 95.49, 95.56, 99.9, 96.4, 99.58, 95.83, 99.65, 94.57, 99.92, 88.46, 90.99, 91.75]
lang_APFD_coverageAdditional = [99.97, 96.67, 95.21, 97.26, 98.26, 99.92, 99.59, 98.87, 98.32, 99.65, 97.14, 99.92, 98.32, 99.21, 98.4]

# Lang - RealFaults
# lang_RF_bytecode_values = [638, 2, 29, 47, 915, 2, 4, 190, 1, 7, 20, 2, 142, 155, 1243]   # Filtered big
# lang_RF_bytecode_values = [311, 510, 34, 6, 518, 210, 182, 195, 1, 7, 8, 2, 129, 50, 881]   # All bytecode
lang_RF_bytecode_values = [251, 394, 17, 5, 504, 140, 35, 137, 1, 8, 7, 2, 81, 117, 1256]  # Filtered small
lang_RF_text = [513, 401, 28, 14, 588, 287, 129, 280, 1, 1, 10, 2, 153, 37, 706]
lang_RF_fast_pw = [190, 1370, 96, 1607, 1561, 274, 3254, 1369, 1597, 16, 1984, 2, 2548, 244, 768]
lang_RF_fast_bytecode = [1055, 1199, 41, 16, 1410, 3, 3684, 944, 33, 1894, 14, 157, 567, 1214, 1684]
# lang_RF_fast_bytecode = [104, 1038, 121, 1960, 1176, 3, 3053, 385, 1885, 1970, 1990, 2, 2291, 484, 897]        # Filtered small
lang_RF_coverage = [1003, 2, 4, 2, 384, 1, 1806, 2, 1, 1014, 2, 1, 184, 8, 1678]
lang_RF_coverageAdditional = [1028, 3, 7, 9, 22, 1, 7, 3, 1, 1014, 10, 1, 188, 10, 49]

# Lang - runtime
lang_runtime_fast_prep = [5.1,2.88,0.87,2.72,4.15,6.86,7.59,5.2,2.61,3.36,2.69,3.72,3.05,4.35,4.84]
lang_runtime_fast_prioritise = [1.6,1.38,0.02,3.37,2,2.01,10.21,1.63,3.3,2.78,3.36,0.46,4.46,2.07,3.3]
lang_runtime_bytecode_prep = [12.64,2.03,0.07,2.46,3.35,11.19,11.73,5.24,1.98,1.25,1.95,4.31,2.86,5.76,11.16]
lang_runtime_bytecode_prioritise = [145.93,95.8,0.07,309.57,176.64,194.29,2466.31,144.44,285.44,157.66,291.83,15.38,518.43,218.48,448.3]
lang_runtime_text_prep = [93608.43,13926.58,491.14,2373.2,22204.97,471658.61,81598.55,50420.1,2118.28,19933.67,2032.19,79549.41,5029.25,34593.1,51219.11]
lang_runtime_text_prioritise = [143.79,118.16,0.07,496.03,217.79,209.46,2715.99,152.86,479.86,354.19,480.8,13.9,786.61,219.81,456.01]
lang_runtime_covTot_prioritise = [0.56,0.45,0.11,25.43,0.57,1.27,45.42,0.67,18.59,0.32,17.86,0.18,96.72,10.14,61.07]
lang_runtime_covAdd_prioritise = [0.83,0.63,0.15,30.88,0.8,1.68,53.09,0.96,29.33,0.46,28.01,0.24,122.79,13.5,60.78]

# Math - APFD
# Filtered big
# math_APFD_bytecode_values = [68.59, 91.28, 93.62, 85.84, 91.55, 86.76, 72.68, 97.43, 93.13, 77.33, 96.75, 94.45, 96.83, 97.07, 93.04, 97.42, 96.01, 99.13, 76.37, 94.63, 95.44, 95.66, 90.62, 94.64, 64.62, 64.39, 95.35, 99.02, 95.07, 99.74, 98.8, 98.2, 95.78, 96.7, 98.77, 95.09, 94.23, 97.35, 79.16, 85.62, 60.43, 68.85]
# All bytecode
# math_APFD_bytecode_values = [53.65, 90.05, 93.39, 82.29, 94.22, 84.01, 62.89, 96.82, 82.03, 65.52, 90.52, 91.04, 83.61, 91.2, 91.16, 97.51, 95.27, 99.64, 69.37, 89.85, 94.82, 92.67, 91.61, 93.96, 67.77, 60.63, 93.69, 98.58, 94.34, 88.02, 96.75, 96.34, 93.77, 92.97, 96.98, 94.17, 94.59, 94.81, 70.27, 85.48, 51.92, 64.71]
# Filtered small
math_APFD_bytecode_values = [60.39, 91.85, 94.11, 85.2, 94.12, 84.01, 65.72, 98.48, 88.29, 72.61, 96.57, 92.58, 89.74, 90.33, 92.09, 97.57, 95.49, 99.53, 76.08, 94.22, 95.69, 93.93, 91.76, 95.2, 76.3, 69.14, 94.86, 99.1, 94.7, 99.74, 97.45, 97.79, 95.3, 96.45, 98.44, 95.76, 94.44, 95.46, 76.76, 83.64, 56.48, 66.45]
math_APFD_text = [50.74, 89.83, 88.56, 78.69, 93.25, 75.59, 57.94, 98.25, 66.44, 49.76, 85.39, 90.45, 80.42, 80.11, 90.54, 97.2, 97.1, 98.88, 60.01, 92.73, 93.88, 83.09, 89.72, 93.3, 67.94, 65.29, 93.08, 99.27, 93.13, 98.44, 97.93, 93.01, 91.93, 90.99, 94.79, 92.31, 94.32, 92.85, 71.32, 83.87, 76.45, 68.74]
math_APFD_fast_pw = [47.87, 77.12, 75.49, 81.14, 86.43, 82.92, 87.68, 82.41, 88.74, 94.19, 94.55, 87.29, 98.65, 99.02, 76.88, 88.47, 86.33, 98.84, 88.26, 94.08, 78.58, 54.12, 77.84, 57.87, 16.52, 38.8, 45.67, 87.31, 98.55, 94.53, 98.38, 96.79, 60.83, 50.52, 34.1, 95.83, 29.59, 66.02, 72.19, 85.41, 46.62, 54.87]
# All bytecode
math_APFD_fast_bytecode = [86.68, 89.59, 92.44, 81.09, 76.4, 91.04, 94.42, 97.12, 98.7, 95.56, 64.79, 89.91, 94.26, 98.15, 97.64, 96.47, 93.18, 97.77, 90.49, 90.74, 96.95, 95.53, 97.38, 80.83, 92.08, 88.05, 90.16, 98.65, 97.8, 96.61, 94.9, 98.76, 72.76, 74.62, 99.08, 99.35, 99.28, 99.65, 88.69, 90.1, 52.04, 62.62]
# Filtered small
# math_APFD_fast_bytecode = [85.97, 89.95, 90.67, 53.83, 91.4, 78.07, 91.57, 90.47, 85.34, 86.7, 58.47, 95.66, 97.73, 98.59, 64.12, 83.77, 79.8, 98.66, 89.47, 85.83, 83.39, 70.87, 78.74, 64.75, 97.72, 81.9, 80.29, 73.38, 97.85, 97.4, 97.44, 98.11, 63.75, 63.64, 98.19, 88.86, 87.38, 95.55, 87.31, 85.24, 62.97, 68.7]        
math_APFD_coverage = [96.11, 85.02, 93.47, 94.74, 81.0, 98.15, 99.28, 97.49, 99.8, 99.47, 97.48, 95.89, 99.14, 97.28, 95.36, 98.03, 97.71, 99.66, 95.79, 90.57, 91.01, 95.49, 92.05, 90.96, 99.3, 99.69, 95.76, 99.33, 97.61, 98.18, 95.9, 98.53, 97.8, 98.07, 99.34, 97.08, 99.23, 99.89, 98.88, 93.81, 76.65, 72.11]
math_APFD_coverageAdditional = [93.93, 93.52, 97.66, 87.69, 81.2, 95.09, 95.55, 99.57, 94.97, 95.07, 97.76, 94.1, 96.72, 99.67, 96.35, 98.58, 98.06, 99.63, 95.18, 94.51, 88.43, 97.25, 89.36, 92.93, 93.6, 93.67, 95.93, 99.82, 99.31, 98.7, 98.05, 98.84, 97.01, 95.0, 99.24, 99.8, 93.91, 98.46, 90.46, 88.37, 80.91, 75.17]

# Math - RealFaults
# Filtered big
# math_RF_bytecode_values = [42, 548, 2, 88, 63, 19, 122, 10, 133, 69, 1, 24, 17, 1, 332, 341, 3, 48, 1, 24, 147, 69, 124, 141, 380, 792, 167, 18, 1, 1, 62, 38, 6, 16, 66, 39, 1181, 172, 62, 3, 1, 1]
# All bytecode
# math_RF_bytecode_values = [24, 809, 9, 102, 55, 3, 93, 6, 226, 96, 3, 5, 181, 43, 540, 434, 3, 167, 1, 11, 245, 82, 382, 307, 254, 460, 148, 15, 1, 46, 156, 124, 11, 10, 244, 219, 1181, 102, 77, 6, 3, 4]
# Filtered small
math_RF_bytecode_values = [39, 681, 14, 105, 70, 7, 91, 6, 168, 78, 1, 13, 75, 10, 448, 455, 3, 143, 1, 13, 191, 80, 272, 195, 317, 2, 151, 16, 1, 1, 176, 62, 7, 8, 106, 182, 1133, 68, 68, 6, 3, 3]
math_RF_text = [36, 764, 7, 104, 26, 1, 93, 3, 189, 147, 6, 73, 211, 71, 618, 408, 3, 218, 48, 14, 359, 80, 563, 542, 254, 302, 97, 18, 32, 88, 76, 139, 12, 16, 193, 362, 1370, 19, 64, 9, 6, 5]
math_RF_fast_pw = [44, 920, 9, 64, 191, 28, 75, 730, 862, 294, 1, 78, 8, 6, 1246, 125, 31, 63, 12, 6, 1782, 64, 155, 1003, 885, 4, 248, 75, 8, 151, 3, 12, 67, 352, 154, 3, 2529, 3, 3, 41, 9, 5]
# All bytecode
math_RF_fast_bytecode = [17, 53, 4, 60, 102, 109, 94, 17, 189, 59, 19, 5, 22, 8, 22, 57, 45, 25, 7, 26, 71, 12, 2, 262, 12, 9, 4, 31, 14, 13, 8, 5, 105, 21, 8, 2, 2, 3, 92, 14, 15, 66]
# Filtered small
# math_RF_fast_bytecode = [7, 61, 1, 213, 317, 28, 17, 78, 164, 96, 14, 11, 6, 6, 861, 84, 39, 4, 4, 39, 1250, 75, 129, 463, 577, 555, 143, 770, 11, 10, 8, 15, 89, 291, 10, 40, 1687, 1345, 7, 16, 59, 63]        
math_RF_coverage = [106, 723, 1, 21, 22, 14, 2, 2, 23, 3, 1, 7, 8, 20, 315, 186, 2, 2, 1, 6, 729, 15, 210, 558, 13, 4, 121, 4, 1, 10, 271, 23, 1, 1, 23, 9, 4, 12, 1, 3, 3, 11]
math_RF_coverageAdditional = [24, 61, 1, 50, 45, 22, 2, 4, 919, 4, 1, 167, 508, 18, 13, 694, 3, 3, 1, 6, 8, 14, 7, 5, 549, 3, 319, 9, 1, 14, 33, 15, 1, 1, 15, 10, 505, 6, 1, 2, 2, 10]

# Math - runtime
math_runtime_fast_prep = [2.45,2.36,0.92,1.55,3.29,1,2.3,1.59,3.22,1.61,0.13,1.69,3.07,1.96,3.29,3.42,0.6,1.86,1.08,0.56,3.4,0.41,3.43,3.51,3.07,4.38,1.33,3.16,1.27,1.28,1.24,1.55,0.77,1.41,2.59,4.27,5.72,5.06,0.6,1.41,0.58,0.52]
math_runtime_fast_prioritise = [0.16,0.93,0.04,0.04,0.29,0.02,0.39,0.06,0.6,0.09,0.01,0.1,0.45,0.16,1.76,2.79,0,0.04,0.02,0,2.56,0.01,2.88,0.89,0.79,1.9,0.08,2.06,0.05,0.03,0.1,0.08,0.01,0.1,0.4,0.71,4.67,3.34,0,0.07,0,0.01]
math_runtime_bytecode_prep = [1.22,0.68,0.12,0.62,2.98,0.09,0.71,0.48,1.42,0.51,0.01,0.28,1.09,0.25,1.65,1.99,0.02,0.21,0.04,0.01,1.86,0.08,2.79,5.39,1.1,2.46,0.48,1.96,1.49,0.16,0.13,0.44,0.06,0.11,1.77,10,5.35,3.91,0.22,0.03,0.01,0.01]
math_runtime_bytecode_prioritise = [2.36,40.99,0.26,0.3,5.45,0.13,11.61,0.49,25,0.8,0.01,0.87,13.61,2.02,140.26,270.48,0.01,0.24,0.09,0.01,234.36,0.04,253.57,53.76,33.97,171.44,0.68,185.73,0.39,0.15,0.96,0.78,0.06,1.07,10.98,32.68,681.29,393.95,0.01,0.62,0.01,0.01]
math_runtime_text_prep = [31750.15,7886.69,262.18,11517.84,27117.83,470.76,8989.57,2796.29,10727.33,2183.57,2.43,5256.42,16956.53,5015.47,16340.99,10328.71,5.99,2798.45,2593.57,13.01,15082.52,363.45,13711.66,31803.29,5306.23,10796.7,4362.71,11292.98,2885.59,1867.7,425.98,3972.14,205.85,779.65,10949.89,35132.63,19605.52,14128.03,106.88,1227.2,8.32,9.18]
math_runtime_text_prioritise = [2.57,58.46,0.36,0.34,6.07,0.15,12.99,0.49,27.85,0.85,0.01,0.92,16.45,2.17,177.45,369.43,0.01,0.24,0.09,0.01,334.66,0.04,377.93,54.97,41.3,208.19,0.7,244.9,0.39,0.15,1,0.84,0.06,1.08,12.3,35.48,847.47,473.97,0.01,0.67,0.01,0.01]
math_runtime_covTot_prioritise = [0.17,3.61,0.49,0.01,0.15,0.01,6.55,0.32,3.95,0.46,0.01,0.12,0.61,0.09,3.07,4.96,0.01,0.01,0.03,0.01,9.57,0.03,9.51,3.05,0.74,1.81,0.13,32.93,0.03,0.03,0.03,0.31,0.01,0.05,1.39,0.41,0.84,3.56,0.01,0.09,0.03,0.03]
math_runtime_covAdd_prioritise = [0.23,4.41,0.68,0.02,0.22,0.01,8.14,0.49,5.47,0.67,0.01,0.18,0.97,0.13,4.09,6.92,0.01,0.01,0.05,0.01,12.1,0.04,11.36,4.18,1.03,2.64,0.2,44.01,0.04,0.04,0.04,0.45,0.01,0.08,2.25,0.62,1.15,5.27,0.01,0.13,0.04,0.05]

# Time - APFD
# time_APFD_bytecode_values = [60.55, 93.16]    # Filtered big
# time_APFD_bytecode_values = [72.27, 93.56]      # All bytecode
time_APFD_bytecode_values = [74.81, 94.73]    # Filtered small
time_APFD_text = [77.76, 93.56]
time_APFD_fast_pw = [55.7, 89.68]
time_APFD_fast_bytecode = [78.17, 92.22]
# time_APFD_fast_bytecode = [84.43, 89.22]        # Filtered small
time_APFD_coverage = [95.88, 91.45]
time_APFD_coverageAdditional = [95.48, 96.71]

# Time - RealFaults
# time_RF_bytecode_values = [45, 24]    # Filtered big
# time_RF_bytecode_values = [48, 100]     # All bytecode
time_RF_bytecode_values = [52, 58]    # Filtered small
time_RF_text = [53, 109]
time_RF_fast_pw = [147, 454]
time_RF_fast_bytecode = [146, 89]
# time_RF_fast_bytecode = [181, 512]       # Filtered small
time_RF_coverage = [186, 71]
time_RF_coverageAdditional = [186, 29]

# Time - runtime
time_runtime_fast_prep = [0.82,1.81]
time_runtime_fast_prioritise = [0.03,0.22]
time_runtime_bytecode_prep = [0.12,0.36]
time_runtime_bytecode_prioritise = [0.16,3.27]
time_runtime_text_prep = [13.4,619.87]
time_runtime_text_prioritise = [0.16,3.8]
time_runtime_covTot_prioritise = [0.13,2.08]
time_runtime_covAdd_prioritise = [0.17,2.5]

# All - APFD
bytecode_APFD_all = cli_APFD_bytecode_values + compress_APFD_bytecode_values + csv_APFD_bytecode_values + jsoup_APFD_bytecode_values + lang_APFD_bytecode_values + math_APFD_bytecode_values + time_APFD_bytecode_values
text_APFD_all = cli_APFD_text + compress_APFD_text + csv_APFD_text + jsoup_APFD_text + lang_APFD_text + math_APFD_text + time_APFD_text
fast_APFD_all = cli_APFD_fast_pw + compress_APFD_fast_pw + csv_APFD_fast_pw + jsoup_APFD_fast_pw + lang_APFD_fast_pw + math_APFD_fast_pw + time_APFD_fast_pw
fast_bytecode_APFD_all = cli_APFD_fast_bytecode + compress_APFD_fast_bytecode + csv_APFD_fast_bytecode + jsoup_APFD_fast_bytecode + lang_APFD_fast_bytecode + math_APFD_fast_bytecode + time_APFD_fast_bytecode
coverage_APFD_all = cli_APFD_coverage + compress_APFD_coverage + cli_APFD_coverage + jsoup_APFD_coverage + lang_APFD_coverage + math_APFD_coverage + time_APFD_coverage
coverageAdd_APFD_all = cli_APFD_coverageAdditional + compress_APFD_coverageAdditional + csv_APFD_coverageAdditional + jsoup_APFD_coverageAdditional + lang_APFD_coverageAdditional + math_APFD_coverageAdditional + time_APFD_coverageAdditional

# All - RealFaults
bytecode_RF_all = cli_RF_bytecode_values + compress_RF_bytecode_values + csv_RF_bytecode_values + jsoup_RF_bytecode_values + lang_RF_bytecode_values + math_RF_bytecode_values + time_RF_bytecode_values
text_RF_all = cli_RF_text + compress_RF_text + csv_RF_text + jsoup_RF_text + lang_RF_text + math_RF_text + time_RF_text
fast_RF_all = cli_RF_fast_pw + compress_RF_fast_pw + csv_RF_fast_pw + jsoup_RF_fast_pw + lang_RF_fast_pw + math_RF_fast_pw + time_RF_fast_pw
fast_bytecode_RF_all = cli_RF_fast_bytecode + compress_RF_fast_bytecode + csv_RF_fast_bytecode + jsoup_RF_fast_bytecode + lang_RF_fast_bytecode + math_RF_fast_bytecode + time_RF_fast_bytecode
coverage_RF_all = cli_RF_coverage + compress_RF_coverage + cli_RF_coverage + jsoup_RF_coverage + lang_RF_coverage + math_RF_coverage + time_RF_coverage
coverageAdd_RF_all = cli_RF_coverageAdditional + compress_RF_coverageAdditional + csv_RF_coverageAdditional + jsoup_RF_coverageAdditional + lang_RF_coverageAdditional + math_RF_coverageAdditional + time_RF_coverageAdditional


# All - runtime
all_runtime_fast_prep = cli_runtime_fast_prep + compress_runtime_fast_prep + csv_runtime_fast_prep + jsoup_runtime_fast_prep + lang_runtime_fast_prep + math_runtime_fast_prep + time_runtime_fast_prep
all_runtime_fast_prioritise = cli_runtime_fast_prioritise + compress_runtime_fast_prioritise + csv_runtime_fast_prioritise + jsoup_runtime_fast_prioritise + lang_runtime_fast_prioritise + math_runtime_fast_prioritise + time_runtime_fast_prioritise
all_runtime_bytecode_prep = cli_runtime_bytecode_prep + compress_runtime_bytecode_prep + csv_runtime_bytecode_prep + jsoup_runtime_bytecode_prep + lang_runtime_bytecode_prep + math_runtime_bytecode_prep + time_runtime_bytecode_prep
all_runtime_bytecode_prioritise = cli_runtime_bytecode_prioritise + compress_runtime_bytecode_prioritise + csv_runtime_bytecode_prioritise + jsoup_runtime_bytecode_prioritise + lang_runtime_bytecode_prioritise + math_runtime_bytecode_prioritise + time_runtime_bytecode_prioritise
all_runtime_text_prep = cli_runtime_text_prep + compress_runtime_text_prep + csv_runtime_text_prep + jsoup_runtime_text_prep + lang_runtime_text_prep + math_runtime_text_prep + time_runtime_text_prep
all_runtime_text_prioritise = cli_runtime_text_prioritise + compress_runtime_text_prioritise + csv_runtime_text_prioritise + jsoup_runtime_text_prioritise + lang_runtime_text_prioritise + math_runtime_text_prioritise + time_runtime_text_prioritise
all_runtime_covTot_prioritise = cli_runtime_covTot_prioritise + compress_runtime_covTot_prioritise + csv_runtime_covTot_prioritise + jsoup_runtime_covTot_prioritise + lang_runtime_covTot_prioritise + math_runtime_covTot_prioritise + time_runtime_covTot_prioritise
all_runtime_covAdd_prioritise = cli_runtime_covTot_prioritise + compress_runtime_covTot_prioritise + csv_runtime_covTot_prioritise + jsoup_runtime_covTot_prioritise + lang_runtime_covTot_prioritise + math_runtime_covTot_prioritise + time_runtime_covTot_prioritise

# print(fast_bytecode_APFD_all)
# print(fast_bytecode_RF_all)

prj = 'all'
dataset_APFD = {}
dataset_RF = {}
dataset_runtime = {}
setDataSet(prj, dataset_APFD, dataset_RF, dataset_runtime)

columns = ["bytecode", "text", "fast", "fast-bytecode", "covTot", "covAdd"]

# Calculate statistics (average and standard deviation)
print('****************APFD*******************')
stats = calculate_stats(dataset_APFD)

for col in columns:
    # print(f"{col}: {stats.get(col, {'average': 'N/A'})['average']:.2f}/{stats.get(col, {'median': 'N/A'})['median']:.2f}/{stats.get(col, {'std_dev': 'N/A'})['std_dev']:.2f}")
    print(f"{col}: {stats.get(col, {'median': 'N/A'})['median']:.2f}/{stats.get(col, {'std_dev': 'N/A'})['std_dev']:.2f}")


# Perform the Kruskal-Wallis test
statistic, p_value = kruskal(bytecode_APFD_all, text_APFD_all, fast_APFD_all)


# Display the results
print(f"Kruskal-Wallis Test Statistic: {statistic:.4f}")
print(f"P-Value: {p_value:.4f}")

# Interpret the results
alpha = 0.05  # Significance level
if p_value < alpha:
    print("Reject the null hypothesis: Significant differences between groups.")
else:
    print("Fail to reject the null hypothesis: No significant differences between groups.")


# Pairwise comparisons
# groups_APFD = {"Bytecode_Div": bytecode_APFD_all, "Text_Div": text_APFD_all, "FAST_pw": fast_APFD_all, "Coverage_Tot": coverage_APFD_all, "coverage_Add": coverageAdd_APFD_all}

groups_APFD, groups_RF, groups_runtime = setGroups(prj)

# Perform pairwise Mann-Whitney U tests
alpha = 0.05  # Significance level

# Adjust the alpha for multiple comparisons
adjusted_alpha = alpha / 5  # Divide alpha by the number of comparisons

perform_statisticalTesting(groups_APFD, alpha)
# exit()

# Perform for RealFaults
print('****************REAL-FAULTS*******************')

# Calculate statistics (average and standard deviation)
stats = calculate_stats(dataset_RF)

# printConstants(prj, stats, columns, False)
# exit()

for col in columns:
    print(f"{col}: {stats.get(col, {'median': 'N/A'})['median']:.2f}/{stats.get(col, {'std_dev': 'N/A'})['std_dev']:.2f}")

# Perform the Kruskal-Wallis test
statistic, p_value = kruskal(bytecode_RF_all, text_RF_all, fast_RF_all)

# Display the results
print(f"Kruskal-Wallis Test Statistic: {statistic:.4f}")
print(f"P-Value: {p_value:.4f}")

# Interpret the results
alpha = 0.05  # Significance level
if p_value < alpha:
    print("Reject the null hypothesis: Significant differences between groups.")
else:
    print("Fail to reject the null hypothesis: No significant differences between groups.")


# Pairwise comparisons
# groups_RF = {"Bytecode_Div": bytecode_RF_all, "Text_Div": text_RF_all, "FAST_pw": fast_RF_all, "Coverage_Tot": coverage_RF_all, "coverage_Add": coverageAdd_RF_all}

# Perform pairwise Mann-Whitney U tests
alpha = 0.05  # Significance level

# Adjust the alpha for multiple comparisons
adjusted_alpha = alpha / 5  # Divide alpha by the number of comparisons

perform_statisticalTesting(groups_RF, alpha)

exit()
# Perform for Runtime
print('****************RUNTIME*******************')

columns = ["bytecode-prep", "bytecode-prioritise", 
           "text-prep", "text-prioritise",
           "fast-prep", "fast-prioritise",
           "covTot", "covAdd"]

# Calculate statistics (average and standard deviation)
stats = calculate_stats(dataset_runtime)

# printConstants(prj, stats, columns, False)
# exit()

for col in columns:
    print(f"{col}: {stats.get(col, {'average': 'N/A'})['average']:.2f}/{stats.get(col, {'median': 'N/A'})['median']:.2f}/{stats.get(col, {'std_dev': 'N/A'})['std_dev']:.2f}")

# Perform the Kruskal-Wallis test
statistic, p_value = kruskal(all_runtime_bytecode_prep, all_runtime_text_prep, all_runtime_fast_prep)

# Display the results
print(f"Preperation times")
print(f"Kruskal-Wallis Test Statistic: {statistic:.4f}")
print(f"P-Value: {p_value:.4f}")

# Interpret the results
alpha = 0.05  # Significance level
if p_value < alpha:
    print("Reject the null hypothesis: Significant differences between groups.")
else:
    print("Fail to reject the null hypothesis: No significant differences between groups.")

# Perform the Kruskal-Wallis test
statistic, p_value = kruskal(all_runtime_bytecode_prioritise, all_runtime_text_prioritise, all_runtime_fast_prioritise)

# Display the results
print(f"Priotrisation times")
print(f"Kruskal-Wallis Test Statistic: {statistic:.4f}")
print(f"P-Value: {p_value:.4f}")

# Interpret the results
alpha = 0.05  # Significance level
if p_value < alpha:
    print("Reject the null hypothesis: Significant differences between groups.")
else:
    print("Fail to reject the null hypothesis: No significant differences between groups.")


# Pairwise comparisons
# groups_RF = {"Bytecode_Div": bytecode_RF_all, "Text_Div": text_RF_all, "FAST_pw": fast_RF_all, "Coverage_Tot": coverage_RF_all, "coverage_Add": coverageAdd_RF_all}

# Perform pairwise Mann-Whitney U tests
alpha = 0.05  # Significance level

# Adjust the alpha for multiple comparisons
adjusted_alpha = alpha / 5  # Divide alpha by the number of comparisons

perform_statisticalTesting(groups_runtime, alpha)