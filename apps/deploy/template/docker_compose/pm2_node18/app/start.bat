@echo off
set "wwwRootDir=%~dp0"

:: Check if node_modules directory exists in wwwRootDir
if not exist "%wwwRootDir%node_modules" (
  echo node_modules directory not found. Installing dependencies...
  :: Change to the wwwRootDir directory
  cd /d "%wwwRootDir%" || exit /b
  npm install yarn -g
  npm config set registry https://registry.npmmirror.com
  npm install

  echo Dependencies installed successfully.
) else (
  echo node_modules directory already exists. No action required.
)

node "%wwwRootDir%/main.js"