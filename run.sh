#!/bin/bash
set -e

# Activate virtual environment
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run the Python program
python map.py