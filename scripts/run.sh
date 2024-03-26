#!/bin/bash

python_version=3
python_exe=python$python_version

# Check if Python exists
if ! command -v $python_exe >/dev/null 2>&1; then
    echo "Python $python_version not found. Please install it and run the script again."
    exit 1
fi

$python_exe --version

VENV_DIR="$(dirname "$(readlink -f "$0")")/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "venv directory does not exist. Creating..."
    cd "$(dirname "$(readlink -f "$0")")" || exit 1
    $python_exe -m venv venv
    echo "Venv-Python: $VENV_DIR/bin/python3"
else
    echo "Venv-Python: $VENV_DIR/bin/python3"
    echo "venv directory already exists."
fi

# Execute main.py with the provided argument
$VENV_DIR/bin/python3 main.py $1
