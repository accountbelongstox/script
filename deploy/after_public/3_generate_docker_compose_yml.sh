#!/bin/bash
#BASE_DIR=$(dirname "$(readlink -f "$0")")
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

env_file="${PARENT_DIR}/.env"
WEB_DIR=$(grep "^WEB_DIR=" "$env_file" | cut -d '=' -f2)

WEB_DIR=${WEB_DIR//\\\/\//}

if [[ $WEB_DIR != /* ]]; then
    WEB_DIR="/$WEB_DIR"
fi

echo "Using .env: $env_file"
selected_services=$(grep "^docker_compose=" "$env_file" | cut -d '=' -f2)

if [ -z "$selected_services" ]; then
    echo "No docker_compose configuration found in $env_file. Current machine will not deploy docker-compose."
else
    echo "Generating docker-compose file based on selected services: $selected_services"
    yml_script="$PARENT_DIR/py_script/yml_parse.py"
    compose_file="$PARENT_DIR/template/docker-compose/docker-compose.yml"
    new_compose_dir="$WEB_DIR/docker_compose"
    new_compose_file="$new_compose_dir/docker-compose.yml"
    echo "yml_script: $yml_script"
    echo "compose_file: $compose_file"
    echo "new_compose_dir: $new_compose_dir"
    echo "new_compose_file: $new_compose_file"
    if [[ -f "$yml_script" && -f "$compose_file" ]]; then
        sudo mkdir -p "$new_compose_dir"
        sudo python3 "$yml_script" copy "$compose_file" "$selected_services" "$new_compose_file"
    else
        echo "YAML parse script or docker-compose file not found."
    fi
fi