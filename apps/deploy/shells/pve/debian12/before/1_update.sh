

# 更新软件包
sudo apt update
sudo apt upgrade -y

# 安装必要的软件包
sudo apt install -y lsof apt-transport-https ca-certificates curl wget git rsync nano vim build-essential

# 配置 Git
sudo git config --global http.sslVerify false
