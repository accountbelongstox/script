#!/bin/bash
OS=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
echo "Updating and installing packages for $OS..."

if ! which sudo > /dev/null 2>&1; then
    echo "Installing sudo..."
    apt update
    apt install -y sudo
fi

if id -nG "$USER" | grep -qw "sudo"; then
    echo "User is already in the sudo group."
else
    echo "Adding user to sudo group..."
    sudo usermod -aG sudo "$USER"
    echo "User added to sudo group. Please re-login for changes to take effect."
fi
