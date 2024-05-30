
OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION_ID=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
current_python_version=$(python3 --version 2>&1)
echo "Current Python version: $current_python_version"

if [[ $current_python_version != Python\ 3* ]]; then
    echo "Python 3 is not the default version. Installing Python 3..."

    OS=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')

    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        sudo apt update
        sudo apt install -y python3 python3-pip
    elif [ "$OS" = "centos" ]; then
        sudo yum install epel-release
        sudo yum update -y
        sudo yum install -y python3 python3-pip
    else
        echo "Unsupported operating system."
        exit 1
    fi

    # 移除原来的符号链接
#    sudo rm -f /usr/bin/python
#    # 创建新的符号链接
#    sudo ln -s /usr/bin/python3 /usr/bin/python
    echo "Python 3 installed successfully."
else
    echo "Python 3 is already installed."
fi

if ! command -v pip3 &> /dev/null; then
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        sudo apt install python3-pip
    elif [ "$OS" = "centos" ]; then
        sudo yum install epel-release
        sudo yum update -y
        sudo yum install python3-pip
    else
        echo "Unsupported operating system."
        exit 1
    fi
else
    echo "pip3 is already installed."
fi

if [[ "$OS_NAME" == "centos" && "$OS_VERSION_ID" == "7" ]]; then
    echo "CentOS 7 detected. Restoring Python version to 2."
    sudo alternatives --install /usr/bin/python python /usr/bin/python2 50
else
    echo "This Restoring Python is only for CentOS 7."
fi

sudo pip3 install pyyaml

python3 --version
