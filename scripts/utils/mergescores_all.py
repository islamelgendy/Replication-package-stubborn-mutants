import os
import numpy as np
import re

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

def extract_data(file_path):
    """Extracts dataset arrays from a given Python file."""
    data = {}
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract all numpy arrays
    matches = re.findall(r'(\w+)_values = np\.array\((.*?)\)', content, re.DOTALL)
    for name, values in matches:
        # Convert string representation of list to actual list
        values = np.array(eval(values.strip()))
        if name not in data:
            data[name] = values
        else:
            data[name] = np.concatenate((data[name], values))  # Append data
    return data

def merge_files(score_folder, score):
    """Merges all `-all.py` files and `-rank-all.py` files into one consolidated file each."""
    all_data = {}
    rank_data = {}
    
    # Find all relevant files
    for root, _, files in os.walk(score_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('-rank-all.py'):
                file_data = extract_data(file_path)
                for key, values in file_data.items():
                    if key not in rank_data:
                        rank_data[key] = values
                    else:
                        rank_data[key] = np.concatenate((rank_data[key], values))
            elif file.endswith('-all.py'):
                file_data = extract_data(file_path)
                for key, values in file_data.items():
                    if key not in all_data:
                        all_data[key] = values
                    else:
                        all_data[key] = np.concatenate((all_data[key], values))
    
    # Save merged files
    save_merged_file(os.path.join(score_folder, 'all.py'), all_data, score)
    save_merged_file(os.path.join(score_folder, 'all-rank.py'), rank_data, score)
    print(f"Merged files saved in {score_folder}")

def save_merged_file(file_path, data, score):
    """Writes the merged dataset to a new Python file."""
    with open(file_path, 'w') as f:
        f.write("import os\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n")
        for key, values in data.items():
            f.write(f"{key}_values = np.array({values.tolist()})\n")
        
        writeRestFile(file_path, f, score)
    print(f"Saved: {file_path}")

def main():
    root_folder = '/home/islam/MyWork/Code/PlotGeneration/DBT-bench/after-coverage/stubborn/all'  # Adjust if necessary
    
    for score_folder in os.listdir(root_folder):
        score_path = os.path.join(root_folder, score_folder)
        if os.path.isdir(score_path):
            merge_files(score_path, score_folder)

if __name__ == "__main__":
    main()
