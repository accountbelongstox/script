#!/bin/bash

unsupported() {
  echo "Unsupported Linux distribution/version: $DISTRO $VERSION"
}

execute_common_command() {
  echo "nothing-Executing common command for $DISTRO $VERSION"
}

centos_7() {
    echo "Docker is not installed. Installing..."
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install -y docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo docker --version
    sudo usermod -aG docker root
    echo "Docker installed successfully."
}

centos_8() {
  echo "Running specific commands for CentOS 8"
}

centos_9() {
  echo "Running specific commands for CentOS 9"
}

debian_8() {
  echo "Running specific commands for Debian 8"
}

debian_9() {
    echo "Docker is not installed. Installing..."
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install docker-ce docker-ce-cli containerd.io rsync
    sudo apt list -a docker-ce
    sudo apt install docker-ce=5:19.03.15~3-0~debian-stretch docker-ce-cli=5:19.03.15~3-0~debian-stretch containerd.io
    echo "Docker installed successfully."
}

debian_10() {
  echo "Running specific commands for Debian 10"
}

debian_11() {
  echo "Running specific commands for Debian 11"
}

debian_12() {
  echo "Running specific commands for Debian 12"
}

ubuntu_20_04() {
  echo "Running specific commands for Ubuntu 20.04"
}

ubuntu_20_10() {
  echo "Running specific commands for Ubuntu 20.10"
}

ubuntu_21_04() {
  echo "Running specific commands for Ubuntu 21.04"
}

ubuntu_21_10() {
    echo "Docker is not installed. Installing..."

    # Add Docker’s official GPG key
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Set up the stable repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt install docker-ce docker-ce-cli containerd.io

    # Optionally, install a specific version of Docker Engine
    sudo apt list -a docker-ce
    sudo apt install docker-ce=5:19.03.15~3-0~debian-stretch docker-ce-cli=5:19.03.15~3-0~debian-stretch containerd.io
    sudo systemctl enable docker
    echo "Docker installed successfully."
}

ubuntu_23() {
  echo "Running specific commands for Ubuntu 23"
}

snap_action() {
  sudo snap install docker
  sudo snap start docker
  sudo snap enable docker
}

dfn_action() {
  echo "Executing dfn_action"
}

DOCKER_IS_INSTALL=0
check_docker_installed() {
  if [ "$IS_SNAP_SERVICE" = "1" ]; then
    if systemctl list-units --type=service | grep -q 'snap.docker'; then
      echo "Docker (Snap) is installed"
      DOCKER_IS_INSTALL=1
    else
      echo "Docker (Snap) is not installed"
      # Add actions to install Docker (Snap) here if needed
    fi
  else
    if ! command -v docker &> /dev/null; then
      echo "Docker is not installed"
      # Add actions to install Docker here if needed
    else
      DOCKER_IS_INSTALL=1
      echo "Docker is installed"
    fi
  fi
}


PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
env_file="${PARENT_DIR}/.env"
echo "Using .env: $env_file"
IS_SNAP_SERVICE=$(grep "^IS_SNAP_SERVICE=" "$env_file" | cut -d '=' -f2)
IS_DFN_SERVICE=$(grep "^IS_DFN_SERVICE=" "$env_file" | cut -d '=' -f2)
check_docker_installed

if [ "$DOCKER_IS_INSTALL" = "0" ]; then
  if [ "$IS_SNAP_SERVICE" = "1" ]; then
    snap_action
  elif [ "$IS_DFN_SERVICE" = "1" ]; then
    dfn_action
  else
    if [ -e /etc/os-release ]; then
      source /etc/os-release
      DISTRO=$ID
      VERSION=$VERSION_ID
    elif [ -e /etc/debian_version ]; then
      DISTRO="debian"
      VERSION=$(cat /etc/debian_version)
    else
      unsupported
    fi

    case "$DISTRO" in
      "centos")
        case "$VERSION" in
          "7") centos_7 ;;
          "8") centos_8 ;;
          "9") centos_9 ;;
          *) unsupported ;;
        esac
        ;;
      "debian")
        case "$VERSION" in
          "8") debian_8 ;;
          "9") debian_9 ;;
          "10") debian_10 ;;
          "11") debian_11 ;;
          "12") debian_12 ;;
          *) unsupported ;;
        esac
        ;;
      "ubuntu")
        case "$VERSION" in
          "20.04") ubuntu_20_04 ;;
          "20.10") ubuntu_20_10 ;;
          "21.04") ubuntu_21_04 ;;
          "21.10") ubuntu_21_10 ;;
          "23") ubuntu_23 ;;
          *) unsupported ;;
        esac
        ;;
      *)
        unsupported
        ;;
    esac
  fi
else
  echo "Docker is installed,Installing skipping."
fi

execute_common_command
