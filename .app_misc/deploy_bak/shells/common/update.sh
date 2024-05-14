
OS=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
echo "Updating and installing packages for $OS..."
if [ "$OS" = "debian" ]; then
    sudo apt update
    sudo apt install -y davfs2 python3 python3-xyz python3-pip lsof extundelete iputils-ping cron apt-transport-https ca-certificates curl gnupg lsb-release htop wget rsync nano wget git
elif [ "$OS" = "ubuntu" ]; then
    sudo apt-get update
    sudo apt-get install -y davfs2 python3 python3-xyz python3-pip lsof extundelete iputils-ping cron ca-certificates curl gnupg apt-transport-https lsb-release htop wget rsync nano wget git
elif [ "$OS" = "centos" ]; then
    sudo yum update -y
    sudo yum install epel-release
    sudo yum update -y
    sudo yum install -y davfs2 iputils python3 python3-xyz python3-pip yum-utils cronie device-mapper-persistent-data lvm2 rsync htop nano wget curl vim git alternatives gcc-c++ make dnf
else
    echo "Unsupported operating system."
    exit 1
fi

# sudo docker cp baota-test:/www /home/www/docker/data/baota
