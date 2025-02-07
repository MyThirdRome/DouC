#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run tests
python3 -m pytest tests/

# Optional: Run main script or CLI
# python3 main.py
# python3 cli.py

# Deactivate virtual environment
deactivate
