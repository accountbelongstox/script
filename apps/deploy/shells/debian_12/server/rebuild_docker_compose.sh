
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEPLOY_DIR=$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")
SCRIPT_ROOT_DIR=$(dirname "$DEPLOY_DIR")

main_script="$SCRIPT_ROOT_DIR/main.py"

OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
PYTHON_VENV_DIR="venv_linux_${OS_NAME}_${OS_VERSION}"
PYTHON_INTERPRET="$PYTHON_VENV_DIR"
python_interpreter="$SCRIPT_ROOT_DIR/$PYTHON_INTERPRET/bin/python3"
echo "python_interpreter :12"

#compose_yml=$(sudo "$python_interpreter" "$main_script" deploy env get_env DOCKER_COMPOSE_FILE)

sudo "$python_interpreter" "$main_script" deploy install

compose_yml=$(cat /usr/local/.pcore_local/deploy/.DOCKER_COMPOSE_FILE)
if [ -z "$compose_yml" ]; then
    echo "Error: docker-compose-yml output is empty."
    exit 1
fi
echo "docker-compose-yml: $compose_yml"
up_command="sudo docker-compose -f $compose_yml up -d"
echo "Docker-Up-CMD: $up_command"
$up_command

s