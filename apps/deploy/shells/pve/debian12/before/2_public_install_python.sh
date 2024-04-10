
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
DEPLOY_DIR=$(dirname "$(dirname "$(dirname "$PARENT_DIR")")")
SCRIPT_ROOT_DIR=$(dirname "$DEPLOY_DIR")

current_python_version=$(python3 --version 2>&1)
echo "Current Python version: $current_python_version"

if [[ $current_python_version != Python\ 3* ]]; then
    echo "Python 3 is not the default version. Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip
    echo "Python 3 installed successfully."
    echo "Debian 12 detected. Restoring Python version to 2."
    sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 50
    sudo pip3 install pyyaml
else
    echo "Python 3 is already installed."
fi

if ! which pip3 &> /dev/null; then
    sudo apt install -y python3-pip
else
    echo "pip3 is already installed."
fi
if ! dpkg -s python3.11-venv &> /dev/null; then
    echo "python3.11-venv is not installed. Installing..."
    sudo apt install -y python3.11-venv
    echo "python3.11-venv installed successfully."
else
    echo "python3.11-venv is already installed."
fi
python3 --version


VENV_DIR="$SCRIPT_ROOT_DIR/venv_linux"
if [ ! -d "$VENV_DIR" ]; then
    echo "venv_linux directory does not exist. Creating..."
    cd "$SCRIPT_ROOT_DIR" || exit
    python3 -m venv venv_linux
    echo -e "\e[91m Venv-Python: $SCRIPT_ROOT_DIR/venv_linux/bin/python3\e[0m"
else
    echo -e "\e[91m Venv-Python: $SCRIPT_ROOT_DIR/venv_linux/bin/python3\e[0m"
    echo "venv_linux directory already exists."
fi
