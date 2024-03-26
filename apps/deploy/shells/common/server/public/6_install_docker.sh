#!/bin/bash
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
IS_SNAP="0"
IS_DNF="0"
if command -v dnf &> /dev/null
then
    IS_DNF="1"
    echo "dnf snap and that installed."
fi
if command -v dnf &> /dev/null
then
    IS_SNAP="1"
    echo "using snap and that installed."
fi
unsupported() {
  echo -e "\e[1;31mUnsupported Linux distribution/version: $DISTRO $VERSION\e[0m"
  echo -e "\e[1;31mCurrently, there is no support for installing Docker on this system.\e[0m"
}
install_docker_compose() {
  COMPOSE_PATH="$PARENT_DIR/library/docker/docker-compose-linux-x86_64"
  if ! command -v docker-compose &> /dev/null; then
    if [ -e "$COMPOSE_PATH" ]; then
      echo "Docker Compose is not installed. Installing from $COMPOSE_PATH..."
      cp "$COMPOSE_PATH" /usr/local/bin/docker-compose
      sudo chmod +x /usr/local/bin/docker-compose
      docker-compose --version
    else
      echo -e "\e[1;31mError: Docker Compose binary not found at $COMPOSE_PATH. Unable to install.\e[0m"
    fi
  else
    echo "Docker Compose is already installed."
  fi
}
centos_install() {
    echo "Docker is not installed. Installing..."
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install -y docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo docker --version
    sudo usermod -aG docker root
    echo "Docker installed successfully."
}
centos_7() {
    centos_install
}
centos_8() {
  centos_install
}
centos_9() {
  centos_install
}
debian_install() {
    echo "Docker is not installed. Installing..."
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install docker-ce docker-ce-cli containerd.io rsync
    sudo apt list -a docker-ce
    #sudo apt install docker-ce=5:19.03.15~3-0~alpineDockerfile-stretch docker-ce-cli=5:19.03.15~3-0~alpineDockerfile-stretch containerd.io
    echo "Docker installed successfully."
}
debian_8() {
    debian_install
}
debian_9() {
    debian_install
}
debian_10() {
    debian_install
}
debian_11() {
    debian_install
}
debian_12() {
    debian_install
}
ubuntu_install() {
    set -e
    sudo rm -rf "/etc/apt/keyrings/docker.gpg"
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
}
ubuntu_20_04() {
    ubuntu_install
}
ubuntu_20_10() {
    ubuntu_install
}
ubuntu_21_04() {
    ubuntu_install
}
ubuntu_21_10() {
    ubuntu_install
}
ubuntu_23() {
    ubuntu_install
}
snap_install() {
  sudo snap install docker
  sudo snap start docker
  sudo snap enable docker
}
dfn_install() {
  echo "Executing dfn_action"
}

check_docker_installed() {
  if ! command -v docker &> /dev/null; then
    echo "Docker is not installed."
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
        echo "Attempting to install Docker on CentOS..."
        centos_install ;;
      "debian")
        echo "Attempting to install Docker on Debian..."
        debian_install ;;
      "ubuntu")
        echo "Attempting to install Docker on Ubuntu..."
        ubuntu_install ;;
      *)
        unsupported ;;
    esac
  else
    echo "Docker is already installed."
  fi

  if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed."
    install_docker_compose
  else
    echo "Docker Compose is already installed."
  fi
}
check_docker_installed

