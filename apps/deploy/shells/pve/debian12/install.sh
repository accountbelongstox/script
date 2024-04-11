
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION_ID=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
DEPLOY_DIR=$(dirname "$( dirname "$( dirname "$BASE_DIR")")")
SCRIPT_ROOT_DIR=$(dirname "$(dirname "$DEPLOY_DIR")")
main_script="$SCRIPT_ROOT_DIR/main.py"
python_deploy="$main_script"
SCRIPT_ROOT_DIR=$(dirname "$(dirname "$DEPLOY_DIR")")
python_interpreter="$SCRIPT_ROOT_DIR/venv_linux/bin/python3"

if ! which sudo > /dev/null 2>&1; then
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


execute_scripts() {
    local directory=$1
    if [ -d "$directory" ]; then
        echo "Executing scripts in $directory..."
        for script in $(find "$directory" -maxdepth 1 -name '*.sh' | sort); do
            echo "Running $script..."
            sudo bash "$script"
        done
    else
        echo "Install bash Directory $directory not found."
    fi
}

execute_public_scripts() {
    local public_dir="${BASE_DIR}/public"
    if [ -d "$public_dir" ]; then
        echo "Executing scripts in public directory..."
        for script in $(find "$public_dir" -maxdepth 1 -name '*.sh' | sort); do
            echo "Running $script..."
            sudo bash "$script"
        done
    else
        echo "Public directory not found."
    fi
}

if [ "$OS_NAME" = "centos" -o "$OS_NAME" = "debian" -o "$OS_NAME" = "ubuntu" ]; then
    before_scripts="${BASE_DIR}/before"
    execute_scripts "$before_scripts"
    execute_public_scripts
    sudo "$python_interpreter" "$python_deploy" deploy install
    after_public_dir="${BASE_DIR}/after"
    execute_scripts "$after_public_dir"
else
    echo "Unknown OS: $OS_NAME"
    echo "Unknown Version: $OS_VERSION_ID"
fi
