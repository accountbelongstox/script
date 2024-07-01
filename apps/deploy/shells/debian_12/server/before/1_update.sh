
#sudo apt update
#sudo apt install -y software-properties-common
sudo apt update
#sudo apt update --allow-insecure-repositories
sudo apt install -y lsof cron curl vim git build-essential rsync htop \
nano wget rsync openssl build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev
sudo git config http.sslVerify "false"