# Description of the replication to FAST-TCP

This file describes how to use the FAST replication package.

## Repository Structure

The replication package consists of the following directories:

### 1. `py/`
This directory contains all Python scripts used to execute various steps of FAST.

### 2. `input/`
This directory contains essential data files used in FAST-TCP approaches, including:
- **Text representation**: The text of the test cases are stored in text files in the format `{project-name}-bbox.txt`.
- **All bytecode representation**: The text of the test cases are stored in text files in the format `{project-name}-bbox-bytecode.txt`.
- **Filtered bytecode representation**: The text of the test cases are stored in text files in the format `{project-name}-bbox-bytecode-filter.txt`.

### 3. `output/`
This directory includes results of FAST-TCP, where each version in each project in a separate file.

### 4. Other
The other folders are not required in the package and are here from the original FAST replication.

## How to Use

To replicate the results, follow these steps:

1. **Run FAST-pw**
   Execute the `py/prioitize.py` to reproduce TCP results. Use the following command:

    ```bash
    python3 py/prioritize.py [project] [type]
    ```

    #### Parameters:
    - **[project]**: Specify the project to analyze. Choose one of the following options:
        - `cli`
        - `compress`
        - `csv`
        - `jsoup`
        - `lang`
        - `math`
        - `time`
    - **[type]**: Specify the type of artefact to be used. Choose one of the following options:
        - Use `text` for **FAST-Text**.
        - Use `bytecode` for **FAST-Bytecode**.
        - Use `bytecode-filter` for **FAST-Bytecode-Filter**.

    #### Example:
    To run **FAST-Text** on the `math` project:
    ```bash
    python3 py/prioritize.py math text
    ```

    To run **FAST-Bytecode** on the `jsoup` project:
    ```bash
    python3 py/prioritize.py jsoup bytecode
    ```

## You might want to clear the `output` directory and delete the `.sig` files in the `input` directory!