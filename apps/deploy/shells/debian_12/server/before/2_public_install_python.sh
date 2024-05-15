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
    sudo apt install -y wget build-essential libreadline-dev libncursesw5-dev \
         libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
         libffi-dev zlib1g-dev openssl libssl-dev libbz2-dev libreadline-dev \
         libsqlite3-dev llvm libncurses5-dev xz-utils tk-dev

    # Install the curses library
    sudo apt-get -y install libncurses5-dev libncursesw5-dev

    # Download Python source code
    sudo wget -P /tmp https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz

    # Extract archive
    FILE="/tmp/Python-3.9.16"

    if [ -f "$FILE" ]; then
        echo "$FILE exists."
    else
        tar xzf /tmp/Python-3.9.16.tgz -C /tmp
    fi

    # Compile Python source
    cd /tmp/Python-3.9.16
    sudo ./configure --enable-optimizations --prefix=/usr/local/bin/python3.9 --with-openssl --with-curses
    sudo make
    sudo make install

    sudo apt install -y libncurses5-dev

    # Check if /usr/bin/python3.9 and /usr/bin/pip3.9 exists as symbolic links, if yes, remove them
    if [ -L /usr/bin/python3.9 ]; then
        sudo rm /usr/bin/python3.9
    fi

    if [ -L /usr/bin/pip3.9 ]; then
        sudo rm /usr/bin/pip3.9
    fi

    # Create symbolic links
#    ln -s /usr/local/bin/python3.9/bin/python3.9 /usr/bin/python3.9
#    ln -s /usr/local/bin/python3.9/bin/pip3.9 /usr/bin/pip3.9
    ln -s /usr/local/bin/python3.9/bin/python3.9 /usr/local/bin/python3.9
    ln -s /usr/local/bin/python3.9/bin/pip3.9 /usr/local/bin/pip3.9

    echo "Python 3.9 installed successfully."
else
    echo "Python 3.9 is already installed."
fi

/usr/local/bin/python3.9 --version

OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
PYTHON_VENV_DIR="venv_linux_${OS_NAME}_${OS_VERSION}"
PYTHON_INTERPRET="$PYTHON_VENV_DIR"
VENV_DIR="$SCRIPT_ROOT_DIR/$PYTHON_INTERPRET"

echo "$VENV_DIR" > /usr/local/venv_dir

echo "Venv_Dir:$VENV_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "$PYTHON_VENV_DIR directory does not exist. Creating..."
    cd "$SCRIPT_ROOT_DIR" || exit
    /usr/local/bin/python3.9 -m venv "$VENV_DIR"

    echo -e "\e[91m Venv-Python: $VENV_DIR/bin/python3.9\e[0m"
else
    echo -e "\e[91m Venv-Python: $VENV_DIR/bin/python3.9\e[0m"
    echo "$PYTHON_VENV_DIR directory already exists."
fi

