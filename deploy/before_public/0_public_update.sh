#!/bin/bash

# 获取操作系统信息
OS=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')

# 根据操作系统安装软件包
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    echo "Updating and installing packages for $OS..."
    sudo apt update
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release htop wget rsync nano wget vim git
elif [ "$OS" = "centos" ]; then
    echo "Updating and installing packages for CentOS..."
    sudo yum update -y
    sudo yum install -y yum-utils device-mapper-persistent-data lvm2 rsync htop nano wget curl vim git alternatives gcc-c++ make dnf
else
    echo "Unsupported operating system."
    exit 1
fi
