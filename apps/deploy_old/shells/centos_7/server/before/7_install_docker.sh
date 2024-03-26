#!/bin/bash
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
DEPLOY_DIR=$(dirname "$(dirname "$(dirname "$PARENT_DIR")")")

install_docker_compose() {
  COMPOSE_REMOTE_URL="https://github.com/docker/compose/releases/latest/download/docker-compose-Linux-x86_64"
  COMPOSE_LOCAL_PATH="$DEPLOY_DIR/library/docker/docker-compose-linux-x86_64"
  sudo curl -k -L "$COMPOSE_REMOTE_URL" -o /usr/bin/docker-compose && sudo chmod +x /usr/bin/docker-compose
  if [ $? -eq 0 ]; then
    echo "Docker Compose downloaded from $COMPOSE_REMOTE_URL."
  else
    if [ -e "$COMPOSE_LOCAL_PATH" ]; then
      echo "Downloading from $COMPOSE_REMOTE_URL failed. Installing from $COMPOSE_LOCAL_PATH..."
      sudo cp "$COMPOSE_LOCAL_PATH" /usr/bin/docker-compose
      sudo chmod +x /usr/bin/docker-compose
      docker-compose --version
    else
      echo "Error: Docker Compose download failed and binary not found at $COMPOSE_LOCAL_PATH. Unable to install."
    fi
  fi
}

install_docker() {
    echo "Docker is not installed. Installing..."
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install -y docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo docker --version
    sudo usermod -aG docker root
    echo "Docker installed successfully."
}

check_docker_installed() {
  if ! command -v docker &> /dev/null; then
    echo "Docker is not installed."
    install_docker
  fi

  if ! sudo command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed."
    install_docker_compose
  else
    echo "Docker Compose is already installed."
  fi
}
check_docker_installed

