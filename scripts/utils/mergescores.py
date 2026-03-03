import os
import numpy as np
import re
from collections import defaultdict

def writeRestFile(filename, output_file, score):
    # Start writing the rest of the file
    output_file.write(f"all_data = [max_coverage_values, min_coverage_values, FAST_Text_values, FAST_Bytecode_values, diversity_values, bytecodeByt_values]\n")
    output_file.write(f"labels = ['Max_Cov', 'Min_Cov', 'FAST-Text', 'FAST-Bytecode', 'Ledru-Text', 'Ledru-Bytecode']\n\n")
    output_file.write(f"fig, ax = plt.subplots()\n\n")
    output_file.write(f"# Plotting the graph\n")
    output_file.write(f"bplot = ax.boxplot(all_data, vert=True, patch_artist=True, labels=labels)\n\n")
    output_file.write(f"# Set colors\n")
    output_file.write(f"colors = ['lightblue', 'lightcoral', 'lightgreen', 'gold', 'violet', 'lightskyblue']\n")
    output_file.write(f"for patch, color in zip(bplot['boxes'], colors):\n")
    output_file.write(f"    patch.set_facecolor(color)\n\n")
    output_file.write(f"# Scatter plot data points\n")
    output_file.write(f"for i, data in enumerate(all_data, 1):\n")
    output_file.write(f"    y = data\n")
    output_file.write(f"    x = np.random.normal(i, 0.04, size=len(y))  # Small jitter\n")
    output_file.write(f"    ax.scatter(x, y, alpha=0.7, color='black', s=10)  # Scatter plot\n\n")
    output_file.write(f'plt.xticks(rotation=45, ha="right", fontsize=12)\n')
    output_file.write(f'ax.yaxis.grid(True, linestyle="--", alpha=0.7)\n')
    output_file.write(f'ax.set_ylabel("First Test Case to Kill", fontsize=12)\n')
    output_file.write(f"plt.tight_layout(pad=2)\n\n")
    output_file.write(f'ax.set_title("Stubborn mutants in all- , #mutants: " + str(len(max_coverage_values)))\n')
    output_file.write(f"output_score_folder = '/home/islam/MyWork/New-work-2023/DBT-workbench/resources/plots/after-coverage/stubborn/all/{score}'\n")
    output_file.write(f"os.makedirs(output_score_folder, exist_ok=True)\n")
    if 'rank' in filename:
        output_file.write(f'plt.savefig("/home/islam/MyWork/New-work-2023/DBT-workbench/resources/plots/after-coverage/stubborn/all/{score}/all-rank.pdf")\n')
    else:
        output_file.write(f'plt.savefig("/home/islam/MyWork/New-work-2023/DBT-workbench/resources/plots/after-coverage/stubborn/all/{score}/all-.pdf")\n')
    output_file.write(f"plt.show()")

# Root directory
root_folder = "/home/islam/MyWork/Code/PlotGeneration/DBT-bench/after-coverage/stubborn"
output_folder = os.path.join(root_folder, "all")

# Pattern to match dataset variables
dataset_vars = [
    "FAST_Text_values",
    "FAST_Bytecode_values",
    "bytecodeByt_values",
    "max_coverage_values",
    "min_coverage_values",
    "diversity_values",
]

# Dictionary to store merged data
merged_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

# Step 1: Collect data from each file
for project in os.listdir(root_folder):
    project_path = os.path.join(root_folder, project)
    
    if os.path.isdir(project_path) and project != "all":  # Ignore 'all' directory
        for score_folder in os.listdir(project_path):
            score_path = os.path.join(project_path, score_folder)

            if os.path.isdir(score_path):  # Ensure it's a directory
                for filename in os.listdir(score_path):
                    if filename.endswith(".py") and ("-all.py" in filename):  
                        file_path = os.path.join(score_path, filename)

                        # Read file and extract dataset values
                        with open(file_path, "r") as file:
                            for line in file:
                                match = re.match(r"(\w+)\s*=\s*np\.array\((\[.*?\])\)", line)
                                if match:
                                    var_name, values = match.groups()
                                    if var_name in dataset_vars:
                                        values_list = eval(values)  # Convert to list
                                        merged_data[score_folder][filename][var_name].extend(values_list)

# Step 2: Write merged data into new "all" folder
for score, files in merged_data.items():
    output_score_folder = os.path.join(output_folder, score)
    os.makedirs(output_score_folder, exist_ok=True)

    for filename, datasets in files.items():
        output_file_path = os.path.join(output_score_folder, filename)

        # Write merged dataset
        with open(output_file_path, "w") as output_file:
            output_file.write("import os\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n# Merged Dataset\n")

            for var_name, values in datasets.items():
                output_file.write(f"{var_name} = np.array({values})\n")
            
            
            writeRestFile(filename, output_file, score)


        print(f"✅ Merged: {output_file_path}")

print("🎉 All files merged successfully!")
