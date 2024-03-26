#!/bin/bash

commands_executed=false
execute_commands_once() {
    if [ "$commands_executed" = false ]; then
        yes | sudo yum update -y
        yes | sudo yum install epel-release
        yes | sudo yum update -y
        commands_executed=true
    fi
}

packages=("lsof" "yum-utils" "device-mapper-persistent-data" "lvm2" "iputils" "yum-utils" "cronie" "device-mapper-persistent-data" "lvm2" "rsync" "nano" "wget" "curl" "vim" "alternatives" "gcc-c++" "make" "samba" "samba-common")

for package in "${packages[@]}"; do
    if ! rpm -q "$package" &> /dev/null && ! which "$package" &> /dev/null; then
        echo "Installing $package..."
        execute_commands_once
        yes | sudo yum install "$package" -y
        if [ "$package" = "git" ]; then
            sudo git config http.sslVerify false
        fi
    else
        echo "$package is already installed."
    fi
done
