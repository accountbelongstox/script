#!/bin/bash
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION_ID=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
DEPLOY_DIR=$(dirname "$( dirname "$( dirname "$BASE_DIR")")")
TOP_DIR=$(dirname "$DEPLOY_DIR")
main_script="$TOP_DIR/main.py"
python_deploy="$main_script"
TOP_DIR=$(dirname "$DEPLOY_DIR")
python_interpreter="$TOP_DIR/venv/bin/python3"
execute_scripts() {
    local directory=$1
    if [ -d "$directory" ]; then
        echo "Executing scripts in $directory..."
        for script in $(find "$directory" -maxdepth 1 -name '*.sh' | sort); do
            echo "Running $script..."
            sudo bash "$script"
        done
    else
        echo "Install bash Directory $directory not found."
    fi
}

execute_public_scripts() {
    local public_dir="${BASE_DIR}/public"
    if [ -d "$public_dir" ]; then
        echo "Executing scripts in public directory..."
        for script in $(find "$public_dir" -maxdepth 1 -name '*.sh' | sort); do
            echo "Running $script..."
            sudo bash "$script"
        done
    else
        echo "Public directory not found."
    fi
}

if [ "$OS_NAME" = "centos" -o "$OS_NAME" = "debian" -o "$OS_NAME" = "ubuntu" ]; then
    before_scripts="${BASE_DIR}/before"
    execute_scripts "$before_scripts"
    execute_public_scripts
    sudo "$python_interpreter" "$python_deploy" deploy install
    after_public_dir="${BASE_DIR}/after"
    execute_scripts "$after_public_dir"
else
    echo "Unknown OS: $OS_NAME"
    echo "Unknown Version: $OS_VERSION_ID"
fi