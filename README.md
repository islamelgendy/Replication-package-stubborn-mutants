# Replication package for the paper "How Effective are Coverage- and Diversity-Based Test Selection at Killing Stubborn Mutants?"

This replication package contains all the necessary scripts, data, and results to reproduce the experiments from our study on the impact of diversity-based test selection in killing stubborn mutants.

## Setup

### Hardware Requirements
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** Approximately 13GB (including unzipped subjects)

### Software Requirements
- **OS:** Linux (tested on Ubuntu 22.04) or macOS.
- **Python:** version 3.10 or higher.

### Installation Steps (Estimated time: 5-10 minutes)
1. **Clone the repository:**
   ```bash
   git clone https://github.com/islamelgendy/Replication-package-stubborn-mutants.git
   cd Replication-package-stubborn-mutants
   ```

2. **Setup:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
## Repository Structure

The replication package consists of the following directories:

### 1. `Scripts/`
This directory contains all Python scripts used to execute various steps of our study, including:
- **Selection stubborn mutants**: A script to perform all test case selection approaches to kill the stubborn mutants for a project.
- **Subject-stats**: A Script to analyse the subjects to produce the stats about the stubborn mutants for a particular project.
- **Stubborn mutant analysis**: A script to analyse the nature of each stubborn mutant.
- **Stubborn mutant analysis cumulative**: A script to analyse the nature of each stubborn mutant across all versions of a project.
- **utils**: Scripts implementing utility functions.

### 2. `Resources/`
This directory contains essential data files used in our TCP approaches, including:
- **Similarity Files**: Precomputed similarity metrics for test cases.
- **Mutation Kill Maps**: Data files mapping tests to mutants.
- **Coverage Information**: Test coverage data for all test cases.
- **Error-Revealing Tests**: Identified error-revealing test cases from experiments.
- **Subjects**: The study subjects used in our study. Make sure to unzip these files!

### 3. `FAST-replication/`
This directory includes the implementation of **FAST-TCP**, modified to work with textual and bytecode information.

### 4. `Plots/`
This directory contains all plots generated from our experimental results.

## How to Use

To replicate the results, follow these steps:

1. **Run Test Case Selection Approaches**
   Execute the scripts in `Scripts/` to reproduce our results. 

   ## Running selection approaches to kill stubborn mutants

    Use the following command:

    ```bash
    python3 scripts/selection_stubborn_mutants.py [project] [True/False] [stubbornScoreThresholdValue]
    ```

    #### Parameters:
    - **[project]**: Specify the project to analyse. Choose one of the following options:
        - `cli`
        - `compress`
        - `csv`
        - `jsoup`
        - `lang`
        - `math`
        - `time`
    - **[True/False]**: 
        - Use `False` for **Normal stubbornness** (the one in our study).
        - Use `True` for **Reachability stubbornness** (future work still in progress).
    - **[stubbornScoreThresholdValue]**: 
        - Use `0.75` for an RSTM threshold stubbornness value of 0.75.
        - Use `0.5` for an RSTM threshold stubbornness value of 0.50.
        - Use `0.25` for an RSTM threshold stubbornness value of 0.25.
        - Use `0.1` for an RSTM threshold stubbornness value of 0.10.
        - Use `0.05` for an RSTM threshold stubbornness value of 0.05.
        - Use `0.01` for an RSTM threshold stubbornness value of 0.01.
        - Use `0.005` for an RSTM threshold stubbornness value of 0.005.
        - Use `0.003` for an RSTM threshold stubbornness value of 0.003.
        - Use `0.002` for an RSTM threshold stubbornness value of 0.002.        
        - Use `0.001` for an RSTM threshold stubbornness value of 0.001.        
        - Use `Hard0.05` for applying a fixed threshold of 0.05.        
        - Use `Hard0.025` for applying a fixed threshold of 0.025.        

    #### Example:
    To run using RSTM threshold value of 0.75 on the `math` project:
    ```bash
    python3 scripts/selection_stubborn_mutants.py math False 0.75
    ```

    To run using RSTM threshold value of 0.002 on the `jsoup` project:
    ```bash
    python3 scripts/selection_stubborn_mutants.py jsoup False 0.002
    ```
    
    To run using a fixed threshold value of 0.05 on the `compress` project:
    ```bash
    python3 scripts/selection_stubborn_mutants.py compress False Hard0.05
    ```

   By the end of the script, the tool will generate a folder `PlotGeneration` at the root directory, where it contains
   the required script to visualise the results. Running these scripts will output the visualisations in pdf files under
   the folder `resources/plots`.  Also, within the `resources/plots` folder, CSV files will be generated that
   give a summary of the number of mutants and types found using RSTM.

2. **Running mutation analysis**
   To view the mutation analysis (i.e. view how many stubborn mutants are identified per threshold and view the mutants' characteristics)
   open the `resources/Stubborn tables`. Run the following:

   ```bash
    python3 scripts/stubborn_mutant_analysis.py [project] [rank] 
    ```

   #### Parameters:
    - **[project]**: Specify the project to analyse. Choose one of the following options:
        - `cli`
        - `compress`
        - `csv`
        - `jsoup`
        - `lang`
        - `math`
        - `time`
    - **[rank]**: 
        - A rank 1 means analysis of only the mutants killed by 1 test case.
        - A rank 2 means analysis of only the mutants killed by 2 test cases.
     
   #### Example:
    To analyse all mutants of rank 1 (killed by only one test case) of the `time` project:
    ```bash
    python3 scripts/stubborn_mutant_analysis.py time 1
    ```

3. **Reproducing FAST-TCP Results**
   Navigate to `FAST-replication/` and follow the instructions in its README to run FAST-TCP experiments.

 ## Citation
If you use this replication package, please cite our paper:
```
Elgendy, I., Hierons, R., & McMinn, P. (2026, May). How Effective are Coverage- and Diversity-Based Test Selection at Killing Stubborn Mutants?. In 2026 IEEE Conference on Software Testing, Verification and Validation (ICST) (pp. xx-xx). IEEE.
```

## Contact
For any issues or questions, please contact i.elgendy@sheffield.ac.uk. 
