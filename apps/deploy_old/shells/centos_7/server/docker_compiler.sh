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

if [ "$OS_NAME" = "centos" -o "$OS_NAME" = "debian" -o "$OS_NAME" = "ubuntu" ]; then
    sudo "$python_interpreter" "$python_deploy" deploy compiler_docker
    sudo "${BASE_DIR}/after/3_generate_docker_compose_yml.sh"
else
    echo "Unknown OS: $OS_NAME"
    echo "Unknown Version: $OS_VERSION_ID"
fi
