
node_version="node18"
wwwRootDir="/www/pm2_$node_version/manager_server"

# Check if node_modules directory exists in wwwRootDir
if [ ! -d "$wwwRootDir/node_modules" ]; then
  echo "node_modules directory not found. Installing dependencies..."

  # Change to the wwwRootDir directory
  cd "$wwwRootDir" || exit

  # Run npm install
  npm install

  echo "Dependencies installed successfully."
else
  echo "node_modules directory already exists. No action required."
fi
