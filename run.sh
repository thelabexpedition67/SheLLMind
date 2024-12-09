#!/bin/bash

# Run SheLLMind application with virtual environment check

# Set the virtual environment path
VENV_PATH="venv/bin/activate"

# Check if virtual environment exists
if [ -f "$VENV_PATH" ]; then
    echo "Activating virtual environment..."
    . "$VENV_PATH"
else
    echo "Virtual environment not found. Please create one using:"
    echo "  python3 -m venv venv"
    echo "Activate the environment with:"
    echo "  source venv/bin/activate"
    echo "Then install requirements:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Run the application
echo "Starting SheLLMind..."
python3 main.py