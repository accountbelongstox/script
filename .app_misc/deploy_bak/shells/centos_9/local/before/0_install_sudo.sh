
OS=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
echo "Updating and installing packages for $OS..."
if ! command -v sudo > /dev/null 2>&1; then
    echo "Installing sudo..."
    yes | yum install -y sudo
fi

if id -nG "$USER" | grep -qw "wheel"; then
    echo "User is already in the wheel group."
else
    echo "Adding user to wheel group..."
    sudo usermod -aG wheel "$USER"
    echo "User added to wheel group. Please re-login for changes to take effect."
fi