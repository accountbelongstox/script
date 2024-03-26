#!/bin/bash
#CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#DEPLOY_DIR="$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")"
#TOP_DIR="$(dirname "$DEPLOY_DIR")"
#main_script="$TOP_DIR/main.py"
<<<<<<< HEAD
#sudo python3 "$main_script" deploy2 set
=======
#sudo python3 "$main_script" deploy set
>>>>>>> origin/main
#ssh_config="/etc/ssh/sshd_config"

if ! command -v sshd &> /dev/null; then
    echo "OpenSSH not installed. Installing OpenSSH..."
    yes | sudo yum install -y openssh-server
    sudo systemctl enable sshd.service
    echo "Starting sshd.service..."
    sudo systemctl start sshd.service
else
    echo "sshd_config file already exists."
    echo "Please review the existing configuration."
    echo "CentOS"
    if sudo systemctl is-active --quiet sshd.service; then
        echo "sshd.service is already running."
    else
        echo "Starting sshd.service..."
        sudo systemctl start sshd.service
    fi
fi
