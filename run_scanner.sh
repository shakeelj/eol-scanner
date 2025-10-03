#!/bin/bash

echo "========================================"
echo "   EOL Scanner - Easy Run Script"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Check if input directory exists
if [ ! -d "input" ]; then
    echo "Creating input directory..."
    mkdir -p input
fi

# Check if output directory exists
if [ ! -d "output" ]; then
    echo "Creating output directory..."
    mkdir -p output
fi

# Check for CSV files in input directory
csv_files=$(find input -name "*.csv" 2>/dev/null | wc -l)
if [ $csv_files -eq 0 ]; then
    echo
    echo "WARNING: No CSV files found in 'input' directory"
    echo "Please place your CSV files in the 'input' folder"
    echo
    echo "Example CSV format:"
    echo "package_name,version"
    echo "python,3.8"
    echo "nodejs,14.21.3"
    echo "java,8"
    echo
    exit 1
fi

echo "Found CSV files in input directory:"
find input -name "*.csv" -exec basename {} \;

echo
echo "Starting EOL scan..."
echo

# Install requirements if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install requirements
source venv/bin/activate
pip install -r requirements.txt

# Run the scanner
python3 eol_scanner.py -i input -o output

echo
echo "========================================"
echo "   Scan completed!"
echo "========================================"
echo
echo "Results are in the 'output' directory:"
ls -la output/

echo
echo "Press Enter to exit..."
read
