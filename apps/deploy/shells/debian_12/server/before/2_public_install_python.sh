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


    #Download Python source code
    if [ ! -f /tmp/Python-3.9.16.tgz ]; then
        sudo wget --no-check-certificate -P /tmp https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
    else
        echo "/tmp/Python-3.9.16.tgz exists, skipping download."
    fi

    #Extract archive
    if [ ! -d /tmp/Python-3.9.16 ]; then
        sudo tar xzf /tmp/Python-3.9.16.tgz -C /tmp
    else
        echo "/tmp/Python-3.9.16 exists."
    fi

    sudo apt-get install openssl
    sudo apt-get install libssl-dev

    # Compile Python source
    cd /tmp/Python-3.9.16
    sudo ./configure --enable-optimizations --prefix=/usr/local/python3.9 --with-openssl=/usr/bin/openssl --with-curses
    sudo make
    sudo make install
    sudo chmod +x /usr/bin/python3


    for cmd in python3.9 pip3.9; do
    if [ -L /usr/local/bin/$cmd ]; then
        sudo rm /usr/local/bin/$cmd
    fi
    sudo ln -s /usr/local/python3.9/bin/$cmd /usr/local/bin/$cmd
    done

    echo "Python 3.9 installed successfully."
else
    echo "Python 3.9 is already installed."
fi

/usr/local/bin/python3.9 --version
/usr/local/bin/pip3.9 --version

OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
PYTHON_VENV_DIR="venv_linux_${OS_NAME}_${OS_VERSION}"
PYTHON_INTERPRET="$PYTHON_VENV_DIR"
VENV_DIR="$SCRIPT_ROOT_DIR/$PYTHON_INTERPRET"
python_interpreter="$VENV_DIR/bin/python3"
main_script="$SCRIPT_ROOT_DIR/main.py"

echo "$VENV_DIR" > /usr/local/venv_dir

echo "Venv_Dir:$VENV_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "$PYTHON_VENV_DIR directory does not exist. Creating..."
    cd "$SCRIPT_ROOT_DIR" || exit
    /usr/local/bin/python3.9 -m venv "$VENV_DIR"
    echo -e "\e[91m Venv-Python: $VENV_DIR/bin/python3.9\e[0m"
else
    echo -e "\e[91m Venv-Python: $VENV_DIR/bin/python3.9\e[0m"
    echo "$VENV_DIR directory already exists."
fi

sudo "$python_interpreter" "$main_script" deploy init_env