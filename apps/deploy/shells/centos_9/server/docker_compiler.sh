
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION_ID=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
DEPLOY_DIR=$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")")
SCRIPT_ROOT_DIR=$(dirname "$(dirname "$DEPLOY_DIR")")
main_script="$SCRIPT_ROOT_DIR/main.py"
python_deploy="$main_script"
SCRIPT_ROOT_DIR=$(dirname "$(dirname "$DEPLOY_DIR")")
python_interpreter="$SCRIPT_ROOT_DIR/venv_linux_$OS_NAME/bin/python3"

if [ "$OS_NAME" = "centos" -o "$OS_NAME" = "debian" -o "$OS_NAME" = "ubuntu" ]; then
    sudo "$python_interpreter" "$python_deploy" deploy compiler_docker
    sudo "${BASE_DIR}/after/3_generate_docker_compose_yml.sh"
else
    echo "Unknown OS: $OS_NAME"
    echo "Unknown Version: $OS_VERSION_ID"
fi
