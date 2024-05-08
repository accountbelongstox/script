
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEPLOY_DIR=$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")
SCRIPT_ROOT_DIR=$(dirname "$(dirname "$DEPLOY_DIR")")
main_script="$SCRIPT_ROOT_DIR/main.py"
export VENV_DIR=$(cat /tmp/venv_dir.txt)
python_interpreter="$VENV_DIR/bin/python3"

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


