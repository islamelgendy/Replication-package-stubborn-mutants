#!/bin/bash

# Exit on any error
set -e

echo "--- ICST 2026 Artifact Setup ---"

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# 2. Install dependencies
echo "Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Unzipping subject files..."
cd resources/subjects/fixed
# --- A. Handle simple single-zip projects (cli, codec, jsoup, time) ---
for proj in cli codec jsoup time; do
    if [ -f "${proj}.zip" ]; then
        echo "Unzipping $proj..."
        unzip -o "${proj}.zip"
    fi
done

# --- B. Handle multi-part/folder-based projects (compress, csv, lang, math) ---
# We iterate through the folders and unzip every zip file found inside them
for proj in compress csv lang math; do
    if [ -d "$proj" ]; then
        echo "Unzipping multi-part files for $proj..."
        # Unzip all zip files inside the project folder into that same folder
        # -j (junk paths) is used if you want to prevent nested folder creation, 
        # but -o (overwrite) is safer if the zips contain the correct structure.
        unzip -o "$proj/*.zip" -d "$proj/"
    fi
done

cd ../../.. # Go back to root

echo "Setup complete."
