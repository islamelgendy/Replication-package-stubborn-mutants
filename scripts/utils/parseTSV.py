import os
import csv

import numpy as np

def extract_times(tsv_file_path):
    """Extract SignatureTime and PrioritizationTime from the given TSV file."""
    with open(tsv_file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) > 1:  # Ensure there's a data line after the header
            values = lines[1].strip().split('\t')  # Split the second line by tab
            signature_time = round(float(values[0]), 2)  # First column
            prioritization_time = round(float(values[1]), 2)  # Second column
            return signature_time, prioritization_time
    return None, None

def count_lines(file_path):
    """Returns the number of lines (number of test cases) in a given text file."""
    with open(file_path, 'r') as file:
        return sum(1 for _ in file)

def process_all_folders(input_root_folder, output_root_folder, output_csv_path, filter):
    """Traverse the root folder, extract required data, and save to a CSV file."""
    results = []

    for root, dirs, files in os.walk(output_root_folder):
        for directory in dirs:
            # Match directories with naming convention {project}_v{ID}
            if (filter == '' and "_v" in directory) or ("_v" in directory and filter in directory):
                project, version = directory.split("_v")
                id_value = version  # Extract ID

                # Path to the target file
                tsv_file_path = os.path.join(root, directory, "FAST-pw-bbox.tsv")
                if os.path.exists(tsv_file_path):  # Ensure the file exists
                    input_file = f"{input_root_folder}{project}_v{version}/{project}-bbox.txt"
                    num_lines = count_lines(input_file)
                    signature_time, prioritization_time = extract_times(tsv_file_path)
                    if signature_time is not None and prioritization_time is not None:
                        results.append([project, id_value, num_lines, signature_time, prioritization_time])

    # Write results to a CSV file
    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        csv_writer.writerow(["Project", "ID", "Size", "SignatureTime", "PrioritizationTime"])
        # Write data
        csv_writer.writerows(results)

def parse_tsv(file_path):
    # Extract project name and ID from the file name
    parent_dir = os.path.dirname(file_path)
    base_name = os.path.basename(parent_dir)  # Get file name without the path
    project, version = base_name.split('_v')  # Split by "_v"
    project_name = project
    id_value = version.split('.')[0]  # Remove the file extension
    
    # Initialize variables to store the Signature Time
    signature_time = None

    # Read the TSV file and parse the data
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) > 1:  # Ensure there's a data line after the header
            # Second line has the values
            signature_time = float(lines[1].split('\t')[0])  # Get first column value

    return {
        "project": project_name,
        "id": id_value,
        "signature_time": signature_time
    }

# # Example usage
# if __name__ == "__main__":
#     tsv_file_path = "/home/islam/MyWork/Code/FAST-replication/output/math_v5/FAST-pw-bbox.tsv"  # Replace with the actual file path
#     result = parse_tsv(tsv_file_path)
    
#     print(f"Project Name: {result['project']}")
#     print(f"ID: {result['id']}")
#     print(f"Signature Time: {result['signature_time']:.2f}")

# Example usage
if __name__ == "__main__":
    filter = 'time'
    input_root_folder = "/home/islam/MyWork/Code/FAST-replication/input/"  # Replace with the actual root folder path
    output_root_folder = "/home/islam/MyWork/Code/FAST-replication/output/"  # Replace with the actual root folder path
    output_csv_path = f"/home/islam/MyWork/Code/FAST-replication/output/{filter}output.csv"  # Replace with the desired output CSV file path
    process_all_folders(input_root_folder, output_root_folder, output_csv_path, filter)
    print(f"Results saved to {output_csv_path}")