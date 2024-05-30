
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEPLOY_DIR="$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")"
SCRIPT_ROOT_DIR=$(dirname "$(dirname "$DEPLOY_DIR")")
main_script="$SCRIPT_ROOT_DIR/main.py"
python_interpreter="$SCRIPT_ROOT_DIR/venv_linux_$OS_NAME/bin/python3"

python_output=$(sudo "$python_interpreter" "$main_script" deploy env get_env DOCKER_COMPOSE_FILE)
if [ -z "$python_output" ]; then
    echo "Error: Python script output is empty."
    exit 1
fi
#build_command="sudo docker-compose -f $python_output build"
up_command="sudo docker-compose -f $python_output up -d"
#echo "Build: $build_command"
#$build_command
echo "Docker-Up-CMD: $up_command"
$up_command
