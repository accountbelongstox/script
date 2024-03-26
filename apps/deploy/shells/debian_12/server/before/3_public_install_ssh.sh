#!/bin/bash

if ! which sshd &> /dev/null; then
    echo "OpenSSH not installed. Installing OpenSSH..."
    sudo apt update
    sudo apt install -y openssh-server
    sudo systemctl enable ssh
    echo "Starting ssh service..."
    sudo systemctl start ssh
else
    echo "sshd_config file already exists."
    echo "Please review the existing configuration."
    echo "Debian 12"
    if sudo systemctl is-active --quiet ssh; then
        echo "ssh service is already running."
    else
        echo "Starting ssh service..."
        sudo systemctl start ssh
    fi
fi
