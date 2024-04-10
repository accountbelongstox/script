
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEPLOY_DIR="$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")"
TOP_DIR=$(dirname "$(dirname "$DEPLOY_DIR")")
main_script="$TOP_DIR/main.py"
python_interpreter="$TOP_DIR/venv_linux/bin/python3"

python_output=$(sudo "$python_interpreter" "$main_script" deploy env get_env DOCKER_COMPOSE_FILE)
if [ -z "$python_output" ]; then
    echo "Error: Python script output is empty."
    exit 1
fi
build_command="sudo docker-compose -f $python_output build"
up_command="sudo docker-compose -f $python_output up -d"
echo "Build: $build_command"
$build_command
echo "Up: $up_command"
$up_command

