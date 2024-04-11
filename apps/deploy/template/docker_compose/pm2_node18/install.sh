

sudo chmod -R 777 /www

# Set the npm path, defaulting to npm
npm_path=${1:-npm}

# Check and set the npm registry
current_registry=$($npm_path config get registry)
if [ "$current_registry" != "https://registry.npmmirror.com" ]; then
    $npm_path config set registry https://registry.npmmirror.com
    echo "Registry set to https://registry.npmmirror.com"
else
    echo "Registry is already set to https://registry.npmmirror.com"
fi

# Check and install Yarn if not already installed
if ! command -v yarn &> /dev/null; then
    echo "Yarn is not installed. Installing Yarn..."
    sudo $npm_path install -g yarn
else
    echo "Yarn is already installed."
fi

# Check and install PM2 if not already installed
if ! command -v pm2 &> /dev/null; then
    echo "PM2 is not installed. Installing PM2..."
    sudo $npm_path install -g pm2
else
    echo "PM2 is already installed."
fi

node /www/pm2_node/app/main.js cmd_start