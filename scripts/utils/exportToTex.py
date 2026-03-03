import re
import statistics

def extract_dataset(file_path):
    """Extract dataset values from the given Python file."""
    dataset = {}
    with open(file_path, 'r') as file:
        for line in file:
            # Skip empty lines or lines that don't contain '='
            if '=' not in line:
                continue
            
            # Split the line on '=' to separate the key and values
            parts = line.split('=')
            if len(parts) != 2:
                continue
            
            key = parts[0].strip()  # Extract and strip the key (e.g., "combined")
            values_part = parts[1].strip()  # Extract the part containing the values
            
            # Check if the values part starts and ends with brackets
            if values_part.startswith('[') and ']' in values_part:
                closingPos = values_part.find(']')
                # Remove brackets and split the inner content by comma
                values_str = values_part[1:closingPos].strip()
                try:
                    values = [float(v.strip()) for v in values_str.split(',')]
                    
                    dataset[key] = values
                except ValueError:
                    continue  # Skip lines where values cannot be converted to float
    return dataset

def calculate_stats(dataset):
    """Calculate the average and standard deviation for each dataset entry."""
    stats = {}
    for key, values in dataset.items():
        avg = sum(values) / len(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0  # Standard deviation
        stats[key] = {"average": avg, "std_dev": std_dev}
    return stats

def write_tex_table(project_name, stats, output_tex_path):
    """Write the dataset stats to a .tex table."""
    columns = ["Project", "diversity", "bytecode", "FAST", "coverage", "coverageAdditional", "combined", "hybrid"]

    # Start building the LaTeX table
    tex_lines = [
        "\\begin{table}[h!]",
        "\\centering",
        "\\begin{tabular}{|" + "c|" * len(columns) + "}",
        "\\hline",
        " & ".join(columns) + " \\\\ \\hline"
    ]

    # Add the rows for averages and standard deviations
    tex_lines.append(
        project_name + " & " +
        " & ".join(f"{stats.get(col, {'average': 'N/A'})['average']:.2f}/{stats.get(col, {'std_dev': 'N/A'})['std_dev']:.2f}" for col in columns[1:]) +
        " \\\\ \\hline"
    )

    # End the table
    tex_lines.extend([
        "\\end{tabular}",
        "\\caption{Average and standard deviation of the dataset.}",
        "\\end{table}"
    ])

    # Write to the output .tex file
    with open(output_tex_path, 'w') as tex_file:
        tex_file.write("\n".join(tex_lines))

# def write_tex_table(project_name, project_stats, output_tex_path):
#     """
#     Write the dataset stats to a .tex table.
#     Each project has its own row, and columns have sub-columns for Average and Std Dev.
#     """
#     # Define the columns and sub-columns
#     metrics = ["diversity", "bytecode", "FAST", "coverage", "coverageAdditional", "combined", "hybrid"]
#     header = ["Project"] + [f"{metric} (Avg)" for metric in metrics] + [f"{metric} (Std Dev)" for metric in metrics]

#     # Start building the LaTeX table
#     tex_lines = [
#         "\\begin{table}[h!]",
#         "\\centering",
#         "\\begin{tabular}{|" + "c|" * len(header) + "}",
#         "\\hline",
#         " & ".join(header) + " \\\\ \\hline"
#     ]

#     # Add rows for each project
#     for project, stats in project_stats.items():
#         row = [project_name]  # Start with the project name
#         # Add averages and standard deviations for each metric

#         avg = stats.get("average", "N/A")
#         std_dev = stats("std_dev", "N/A")
#         row.append(f"{avg:.2f}" if avg != "N/A" else "N/A")
#         row.append(f"{std_dev:.2f}" if std_dev != "N/A" else "N/A")
#         tex_lines.append(" & ".join(row) + " \\\\ \\hline")

#     # End the table
#     tex_lines.extend([
#         "\\end{tabular}",
#         "\\caption{Average and standard deviation of datasets per project.}",
#         "\\end{table}"
#     ])

#     # Write to the output .tex file
#     with open(output_tex_path, 'w') as tex_file:
#         tex_file.write("\n".join(tex_lines))


if __name__ == "__main__":
    input_file = "/home/islam/MyWork/Code/PlotGeneration/DBT-bench/after-coverage/math/math-APFD.py"  # Replace with the path to your .py file
    output_tex = "/home/islam/MyWork/New-work-2023/DBT-workbench/resources/plots/APFD/math.tex"  # Path to the output .tex file

    # Extract dataset
    dataset = extract_dataset(input_file)

    # Calculate statistics (average and standard deviation)
    stats = calculate_stats(dataset)

    # Write the LaTeX table
    startPos = input_file.rfind('/') + 1
    endPos = input_file.rfind('-')
    file_name = input_file[startPos:endPos]  # Get the file name without extension
    write_tex_table(file_name, stats, output_tex)

    print(f"LaTeX table written to {output_tex}")
