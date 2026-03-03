import os
import re

# Define the root folder
root_folder = "/home/islam/MyWork/Code/PlotGeneration/DBT-bench/after-coverage/stubborn"

# Patterns to remove
remove_vars = ["max_coverage_additional_values", "original_values"]

# Updated all_data and labels
new_all_data = "all_data = [max_coverage_values, min_coverage_values, FAST_Text_values, FAST_Bytecode_values, diversity_values, bytecodeByt_values]"
new_labels = "labels = ['Max_Cov', 'Min_Cov', 'FAST-Text', 'FAST-Bytecode', 'Ledru-Text', 'Ledru-Bytecode']"

# New visualization code (excluding title/savefig)
new_visualization = """
# Set colors
colors = ['lightblue', 'lightcoral', 'lightgreen', 'gold', 'violet', 'lightskyblue']
for patch, color in zip(bplot['boxes'], colors):
    patch.set_facecolor(color)

# Scatter plot data points
for i, data in enumerate(all_data, 1):
    y = data
    x = np.random.normal(i, 0.04, size=len(y))  # Small jitter
    ax.scatter(x, y, alpha=0.7, color='black', s=10)  # Scatter plot

# Rotate x-axis labels
plt.xticks(rotation=45, ha="right", fontsize=12)

# Gridlines
ax.yaxis.grid(True, linestyle="--", alpha=0.7)

# Titles and labels (excluding ax.set_title)
ax.set_ylabel("First Test Case to Kill", fontsize=12)

plt.tight_layout(pad=2)
"""

# Recursively go through all subdirectories
for dirpath, _, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.endswith(".py"):
            file_path = os.path.join(dirpath, filename)

            # Read the file content
            with open(file_path, "r") as file:
                content = file.readlines()

            # Remove unwanted variables and update content
            updated_content = []
            found_all_data = False
            for line in content:
                if line.strip().startswith("from scipy.interpolate") or line.strip().startswith("bytecode_values = np.array([])"):
                    continue
                if line.strip().startswith("all_data"):
                    found_all_data = True  # all_data exists
                    updated_content.append(line)
                if not any(var in line for var in remove_vars):
                    updated_content.append(line)

            # Convert list to a single string
            updated_content = "".join(updated_content)

            # If all_data exists, update it
            if found_all_data:
                updated_content = re.sub(r"all_data\s*=\s*\[.*?\]", new_all_data, updated_content, flags=re.DOTALL)
            else:
                # If all_data does not exist, insert it before labels
                updated_content = re.sub(r"(labels\s*=\s*\[.*?\])", f"{new_all_data}\n\\1", updated_content, flags=re.DOTALL)

            # Update labels
            updated_content = re.sub(r"labels\s*=\s*\[.*?\]", new_labels, updated_content, flags=re.DOTALL)

            # Preserve ax.set_title and plt.savefig while replacing visualization code
            updated_content_lines = updated_content.split("\n")
            new_script = []
            visualization_added = False

            for line in updated_content_lines:
                if line.strip().startswith("ax.set_title") or line.strip().startswith("plt.savefig"):
                    if not visualization_added:
                        # Insert the new visualization block only once
                        new_script.append(new_visualization)
                        visualization_added = True
                    
                    # Keep title and savefig as they are
                    new_script.append(line)
                elif "patch.set_facecolor" not in line:
                    new_script.append(line)

            # Convert back to a string
            updated_content = "\n".join(new_script)

            # Write the modified content back to the file
            with open(file_path, "w") as file:
                file.write(updated_content)

            print(f"✅ Updated: {file_path}")

print("🎉 All Python files updated successfully while preserving structure!")
