CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
DEPLOY_CHIDDIR=$(dirname "$(dirname "$(dirname "$PARENT_DIR")")")
DEPLOY_DIR=$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")
SCRIPT_ROOT_DIR=$(dirname "$(dirname "$DEPLOY_DIR")")

current_python_version=$(python3.9 --version 2>&1)
current_pip_version=$(pip3.9 --version 2>&1)
echo "Current Python version: $current_python_version"
echo "Current Pip version: $current_pip_version"

if [[ $current_python_version != Python\ 3.9* ]] || [[ $current_pip_version != pip* ]]; then
    echo "Python 3.9 or Pip 21 is not the default version. Installing Python 3.9 and Pip 21..."

    # Install prerequisites
    sudo apt update && sudo apt upgrade
    sudo apt install -y wget build-essential libreadline-gplv2-dev libncursesw5-dev \
         libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
         libffi-dev zlib1g-dev openssl libssl-dev libbz2-dev libreadline-dev \
         libsqlite3-dev llvm libncurses5-dev xz-utils tk-dev

    # Download Python source code
    sudo wget -P /tmp https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz

    # Extract archive
    sudo tar xzf /tmp/Python-3.9.16.tgz -C /tmp

    # Compile Python source
    cd /tmp/Python-3.9.16
    sudo ./configure --enable-optimizations --prefix=/usr/local/bin/python3.9 --with-openssl
    sudo make
    sudo make install

    # Check if /usr/bin/python3.9 and /usr/bin/pip3.9 exists as symbolic links, if yes, remove them
    if [ -L /usr/bin/python3.9 ]; then
        sudo rm /usr/bin/python3.9
    fi

    if [ -L /usr/bin/pip3.9 ]; then
        sudo rm /usr/bin/pip3.9
    fi

    # Create symbolic links
    ln -s /usr/local/bin/python3.9/bin/python3.9 /usr/bin/python3.9
    ln -s /usr/local/bin/python3.9/bin/pip3.9 /usr/bin/pip3.9
    ln -s /usr/local/bin/python3.9/bin/python3.9 /usr/local/bin/python3.9
    ln -s /usr/local/bin/python3.9/bin/pip3.9 /usr/local/bin/pip3.9

    echo "Python 3.9 installed successfully."
else
    echo "Python 3.9 is already installed."
fi

/usr/local/bin/python3.9 --version

VENV_DIR="$SCRIPT_ROOT_DIR/venv_linux"
if [ ! -d "$VENV_DIR" ]; then
    echo "venv_linux directory does not exist. Creating..."
    cd "$SCRIPT_ROOT_DIR" || exit
    /usr/local/bin/python3.9 -m venv venv_linux
    echo -e "\e[91m Venv-Python: $SCRIPT_ROOT_DIR/venv_linux/bin/python3.9\e[0m"
else
    echo -e "\e[91m Venv-Python: $SCRIPT_ROOT_DIR/venv_linux/bin/python3.9\e[0m"
    echo "venv_linux directory already exists."
fi
