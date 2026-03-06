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
find resources/subjects/fixed -name "*.zip" -exec unzip -d resources/subjects/fixed {} \;

echo "Setup complete."
