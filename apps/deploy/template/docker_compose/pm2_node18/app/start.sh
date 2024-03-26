#!/bin/bash
wwwRootDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Check if node_modules directory exists in wwwRootDir
if [ ! -d "$wwwRootDir/node_modules" ]; then
  echo "node_modules directory not found. Installing dependencies..."
  # Change to the wwwRootDir directory
  cd "$wwwRootDir" || exit
  sudo npm install yarn -g
  sudo npm config set registry https://registry.npmmirror.com
  sudo npm install
  echo "Dependencies installed successfully."
else
  echo "node_modules directory already exists. No action required."
fi
node "$wwwRootDir/main.js"
