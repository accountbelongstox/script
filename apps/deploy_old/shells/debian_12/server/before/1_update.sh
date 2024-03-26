#!/bin/bash
#sudo apt update
#sudo apt install -y software-properties-common
sudo apt update
#sudo apt update --allow-insecure-repositories
sudo apt install -y lsof cron curl vim git build-essential rsync htop nano wget rsync
sudo git config http.sslVerify "false"
