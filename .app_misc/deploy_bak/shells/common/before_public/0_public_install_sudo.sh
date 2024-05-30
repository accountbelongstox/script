

OS=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
echo "Updating and installing packages for $OS..."

if [ "$OS" = "debian" ]; then
    if ! command -v sudo > /dev/null 2>&1; then
        echo "Installing sudo..."
        apt update
        apt install -y sudo
    fi

    if id -nG "$USER" | grep -qw "sudo"; then
        echo "User is already in the sudo group."
    else
        echo "Adding user to sudo group..."
        sudo usermod -aG sudo "$USER"
        echo "User added to sudo group. Please re-login for changes to take effect."
    fi

elif [ "$OS" = "ubuntu" ]; then
    if ! command -v sudo > /dev/null 2>&1; then
        echo "Installing sudo..."
        apt update
        apt install -y sudo
    fi

    if id -nG "$USER" | grep -qw "sudo"; then
        echo "User is already in the sudo group."
    else
        echo "Adding user to sudo group..."
        sudo usermod -aG sudo "$USER"
        echo "User added to sudo group. Please re-login for changes to take effect."
    fi

elif [ "$OS" = "centos" ]; then
    # CentOS-specific commands
    if ! command -v sudo > /dev/null 2>&1; then
        echo "Installing sudo..."
        yum install -y sudo
    fi

    if id -nG "$USER" | grep -qw "wheel"; then
        echo "User is already in the wheel group."
    else
        echo "Adding user to wheel group..."
        sudo usermod -aG wheel "$USER"
        echo "User added to wheel group. Please re-login for changes to take effect."
    fi

else
    echo "Unsupported operating system."
    exit 1
fi
