#!/bin/bash

# 检查是否有SSH服务
if ! command -v ssh > /dev/null 2>&1; then
    echo "Installing SSH..."
    sudo apt-get update
    sudo apt-get install -y openssh-server
fi

if sudo systemctl is-active --quiet ssh; then
    echo "SSH service is already running."
else
    echo "Starting SSH service..."
    sudo systemctl start ssh
fi

ssh_config="/etc/ssh/sshd_config"
if grep -q "^PasswordAuthentication" "$ssh_config"; then
    sudo sed -i 's/^PasswordAuthentication.*/PasswordAuthentication yes/' "$ssh_config"
else
    echo "PasswordAuthentication yes" | sudo tee -a "$ssh_config"
fi

echo "Restarting SSH service..."
sudo systemctl restart ssh

echo "SSH setup complete."
