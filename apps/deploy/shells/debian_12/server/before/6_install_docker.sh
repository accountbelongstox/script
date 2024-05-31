CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
DEPLOY_DIR=$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")

TMP_INFO_DIR="/usr/local/.pcore_local/deploy"
LSB_RELEASE="$TMP_INFO_DIR/.LSB_RELEASE"
RELEASE=""

if [ ! -d "$TMP_INFO_DIR" ]; then
    echo -e "\e[31mTMP_INFO_DIR $TMP_INFO_DIR does not exist.\e[0m"
else
    if [ ! -f "$LSB_RELEASE" ]; then
        echo -e "\e[31mLSB_RELEASE $LSB_RELEASE does not exist.\e[0m"
    else
        RELEASE=$(cat "$LSB_RELEASE")
    fi
fi


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
bookworm 
install_docker() {
    echo "Docker is not installed. Installing..."

#    sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor | sudo tee /usr/share/keyrings/docker-archive-keyring.gpg >/dev/null

#    echo "deb [arch=amd64] https://download.docker.com/linux/debian buster stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

#    sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --yes --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $RELEASE stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update

    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io rsync

    sudo apt list -a docker-ce
}


if ! which docker &> /dev/null; then
    echo "Docker is not installed."
    install_docker
else
    echo "Docker is already installed."
fi

if ! sudo which docker-compose &> /dev/null; then
    echo "Docker Compose is not installed."
    install_docker_compose
else
    echo "Docker Compose is already installed."
fi
