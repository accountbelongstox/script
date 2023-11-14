#!/bin/bash
BASE_DIR=$(dirname "$(readlink -f "$0")")
os=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
version_id=$(awk -F= '/^VERSION_ID/{print $2}' /etc/os-release)

centos_install_node() {
    echo "Node.js is not installed. Installing using NVM..."

    nvm_version=$(nvm --version)
    if [ $? -ne 0 ]; then
        echo "NVM is not installed. Installing NVM..."

        # Check if the NVM install script exists in the current directory
        if [ ! -f "./nvm/install.sh" ]; then
            echo "NVM install script not found. Cloning from GitHub..."
            sudo git clone https://github.com/nvm-sh/nvm.git
        fi

        # Run the NVM install script
        sudo chmod +x ./nvm/install.sh
        sudo ./nvm/install.sh

        # Source NVM script to use it in the current session
        export NVM_DIR="$HOME/.nvm"
        echo "NVM_DIR $NVM_DIR"
        echo "nvm.sh $NVM_DIR/nvm.sh"
        sudo chmod +x "$NVM_DIR/nvm.sh"
        sudo chmod +x "$NVM_DIR/bash_completion.sh"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    fi

    # Install Node.js using NVM
    nvm install "$nvm_version"
    echo "Installed Node.js version $nvm_version"
    nvm use --delete-prefix "v$nvm_version"
}

centos_7_install_node(){
  sudo yum install epel-release
  sudo yum install nodejs
  sudo yum install npm
}

ubuntu_install_node(){
    echo "Node.js is not installed. Installing using wget from node website..."
    tmp_config="/tmp/setup_config_deploy_"
    node_version=$(grep "^node_version=" "$tmp_config" | cut -d '=' -f2)
    echo "Using node version: $node_version"
    tmp_dir="/tmp/node"
    mkdir -p $tmp_dir
    NODE_DIST_URL="https://nodejs.org/dist/v${node_version}/node-v${node_version}-linux-x64.tar.xz"
    echo "Downloading Node.js v${node_version}..."
    wget -P $tmp_dir $NODE_DIST_URL || curl -o $tmp_dir/node-v${node_version}-linux-x64.tar.xz $NODE_DIST_URL
    echo "Extracting Node.js package..."
    tar -xvf $tmp_dir/node-v${node_version}-linux-x64.tar.xz -C $tmp_dir
    echo "Installing Node.js..."
    sudo cp -r $tmp_dir/node-v${node_version}-linux-x64/{bin,include,lib,share} /usr/local/
    echo "Cleaning up..."
    rm -rf $tmp_dir
    echo "Node.js v${node_version} installation complete."
    echo "Verifying Node.js installation..."
    node --version
    npm --version
}

current_node_version=$(node -v 2>/dev/null)

if ! [[ $current_node_version == v* ]]; then

    if [[ $os == *"Ubuntu"* ]] || [[ $os == *"Debian"* ]]; then
        ubuntu_install_node
    elif [[ $os == *"CentOS"* ]]; then
        # 移除已存在的 Node.js 安装
        sudo rm -rf /usr/local/bin/node
        sudo rm -rf /usr/local/bin/npm
        sudo rm -rf /usr/local/bin/npx
        sudo rm -rf /usr/local/include/node
        sudo rm -rf /usr/local/lib/node_modules
        sudo rm -rf /usr/local/share/doc/node

        # 根据 CentOS 版本调用不同的安装函数
        if [[ $version_id -le 7 ]]; then
            centos_7_install_node
        else
            centos_install_node
        fi
    else
        echo "Unsupported operating system."
    fi
else
    echo "Node.js is already installed. Version: $current_node_version"
fi


install_if_not_present() {
    local package=$1
    local install_command=$2

    if ! command -v $package &> /dev/null; then
        echo "$package is not installed, installing it now."
        sudo $install_command
        $package --version
    else
        echo "$package is already installed."
    fi
}
npm config set registry http://mirrors.cloud.tencent.com/npm/
sudo npm config set registry http://mirrors.cloud.tencent.com/npm/
install_if_not_present pm2 "npm install pm2@latest -g"
install_if_not_present yarn "npm install yarn@latest -g"
install_if_not_present cnpm "npm install cnpm@latest -g"
#
## Define Node.js version
#NODE_VERSION="18.18.2"
#BASE_DIR=$(dirname "$(readlink -f "$0")")
#
## Check if Node.js is installed
#node_version=$(node --version)
#if [ $? -ne 0 ]; then
#    echo "Node.js is not installed. Installing using NVM..."
#
#    # Check if NVM is installed
#    nvm_version=$(nvm --version)
#    if [ $? -ne 0 ]; then
#        echo "NVM is not installed. Installing NVM..."
#
#        # Check if the NVM install script exists in the current directory
#        if [ ! -f "./nvm/install.sh" ]; then
#            echo "NVM install script not found. Cloning from GitHub..."
#            sudo git clone https://github.com/nvm-sh/nvm.git
#        fi
#
#        # Run the NVM install script
#        sudo chmod +x ./nvm/install.sh
#        sudo ./nvm/install.sh
#
#        # Source NVM script to use it in the current session
#        export NVM_DIR="$HOME/.nvm"
#        echo "NVM_DIR $NVM_DIR"
#        echo "nvm.sh $NVM_DIR/nvm.sh"
#        sudo chmod +x "$NVM_DIR/nvm.sh"
#        sudo chmod +x "$NVM_DIR/bash_completion.sh"
#        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
#        [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
#    fi
#
#    # Install Node.js using NVM
#    nvm install $NODE_VERSION
#    echo "Installed Node.js version $NODE_VERSION"
#    nvm use --delete-prefix v$NODE_VERSION
#else
#    echo "Node.js is already installed. Version: $node_version"
#fi
#
## Install PM2 and show the list of processes
#sudo npm install pm2@latest -g
#
## Add npm global binaries to PATH
#export PATH="$PATH:$(npm config get prefix)/bin"
#
## Check if pm2 command exists
#if ! command -v pm2 &> /dev/null
#then
#    echo "pm2 could not be found, installing it now."
#    sudo npm install pm2@latest -g
#    ~/.nvm/versions/node/v$NODE_VERSION/bin/pm2 list
#else
#    echo "pm2 is already installed."
#fi
