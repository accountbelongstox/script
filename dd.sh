#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script is executed from: $SCRIPT_DIR"

find "$SCRIPT_DIR" -type f -name "*.sh" -exec chmod +x {} \;

dd_path="/usr/bin/dd.sh"
script_path="$(readlink -f "$0")"

if [ -L "$0" ] && [ "$0" -ef "$dd_path" ]; then
  original_source="$(readlink -f "$script_path")"
  SCRIPT_DIR="$(dirname "$original_source")"
  echo "Updating SCRIPT_DIR to: $SCRIPT_DIR"
fi

if [ ! -e "$dd_path" ]; then
  ln -s "$script_path" "$dd_path"
  echo "Symbolic link created: $dd_path -> $script_path"
  chmod +x "$dd_path"
fi

echo "SCRIPT_DIR: $SCRIPT_DIR"

if ! command -v sudo > /dev/null 2>&1; then
    "$SCRIPT_DIR/deploy/common/before_public/0_public_install_sudo.sh"
fi
get_git(){
  cd "$SCRIPT_DIR" || exit
  sudo git stash &&sudo git fetch --all && sudo git reset --hard origin/main && sudo git pull --force
  find "$SCRIPT_DIR" -type f -name "*.sh" -exec chmod +x {} \;
}
restart_pm2() {
  sudo docker exec -it pm2_nginx pm2_nginx list
  while true; do
    echo "Select an option:"
    echo "1. Show PM2 logs"
    echo "2. Restart PM2 processes"
    echo "3. Real-time pm2 DEBUG information"
    echo "4. Restart pm2 docker"
    echo "0. Exit"
    read -p "Enter your choice: " choice
    case $choice in
      1)
        while true; do
          sudo docker exec -it pm2_nginx pm2_nginx list
          read -p "Enter the number ID to loging(press Enter to skip, 0 to exit): " pm2_id
          if [ -z "$pm2_id" ]; then
            break
          elif [ "$pm2_id" = "0" ]; then
            echo "Exiting without logs."
            exit 0
          else
            sudo docker exec -it pm2_nginx pm2_nginx logs "$pm2_id"
          fi
        done
        ;;
      2)
        while true; do
          sudo docker exec -it pm2_nginx pm2_nginx list
          read -p "Enter the number ID to restart(press Enter to skip, 0 to exit): " pm2_id
          if [ -z "$pm2_id" ]; then
            break
          elif [ "$pm2_id" = "0" ]; then
            echo "Exiting without restarting."
            exit 0
          else
            sudo docker exec -it pm2_nginx pm2_nginx restart "$pm2_id"
            sudo docker exec -it pm2_nginx pm2_nginx logs
          fi
        done
        ;;
      3)
        sudo docker exec -it pm2_nginx pm2_nginx logs
        ;;
      4)
        sudo docker restart pm2_nginx
        sudo docker exec -it pm2_nginx pm2_nginx list
        ;;
      0)
        echo "Exiting."
        exit 0
        ;;
      *)
        echo "Invalid option. Please try again."
        ;;
    esac
  done
}


select_install_type() {
    local script_type=$1
    case "$script_type" in
    "install")
        while true; do
            PS3="Select install type (1: server, 2: pve, 3: local, 4: cancel): "
            options=("server" "pve" "local" "cancel")
            select install_type in "${options[@]}"; do
                case "$install_type" in
                    "server"|"pve"|"local")
                        echo "Selected install type: $install_type"
                        "$SCRIPT_DIR/deploy/exec_entry.sh" "$install_type/install.sh"
                        return
                        ;;
                    "cancel")
                        echo "Installation canceled."
                        return
                        ;;
                    *)
                        echo "Invalid option. Please select a number between 1 and ${#options[@]}."
                        ;;
                esac
            done
        done
        ;;
    "select_docker_compose")
        "$SCRIPT_DIR/deploy/exec_entry.sh" "server/docker_compiler.sh"
        ;;
    "enable_local_sharing")
        "$SCRIPT_DIR/deploy/exec_entry.sh" "server/docker_compiler.sh"
        ;;
    *)
        echo "Invalid script type: $script_type"
        return
        ;;
    esac
}

migrate_server(){
  while true; do
    echo "Select an option:"
    echo "1. bt migrate to docker nginx"
    echo "0. Exit"
    read -p "Enter your choice: " choice
    case $choice in
      1)

        ;;
      2)
        ;;
      3)
        ;;
      4)
        ;;
      0)
        echo "Exiting."
        exit 0
        ;;
      *)
        echo "Invalid option. Please try again."
        ;;
    esac
  done
}
while true; do
    echo "Select a function："
    echo "1. install the server."
    echo "2. Rebuild docker-compose"
    echo "3. migrate server"
    echo "4. Restart/Print pm2 service"
    echo "5. Get the latest git version"
    echo "6. Enable local sharing on LAN"
    echo "0. Exit"

    read -p "Please enter the number (0-5): " choice

    case $choice in
        0)
            echo "Exiting the script."
            exit ;;
        1)
            select_install_type "install" ;;
        2)
            select_install_type "select_docker_compose" ;;
        3)
            migrate_server ;;
        4)
            restart_pm2 ;;
        5)
            get_git ;;
        6)
            select_install_type "enable_local_sharing" ;;
        *)
            echo "Invalid selection. Please enter a number between 0 and 5." ;;
    esac
done
