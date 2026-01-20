#!/bin/bash
# Setup script for LangGraph examples

set -e

echo "Setting up LangGraph examples environment..."

# Check Python version
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
	echo "Creating virtual environment..."
	python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run examples:"
echo "  python 01_basic_workflow.py"
echo "  python 02_data_exploration.py"
