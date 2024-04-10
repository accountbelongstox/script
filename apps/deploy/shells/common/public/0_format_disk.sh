
#sudo fdisk -l
#echo "更新/etc/fstab文件..."
#echo "/dev/vdb    /www    ext4    defaults    0    2" | sudo tee /etc/fstab
#sudo systemctl stop docker
#echo "更新/etc/docker/daemon.json文件。"
#echo '{ "data-root": "/www/docker" }' | sudo tee /etc/docker/daemon.json
#if [ ! -d "/www/docker" ]; then
#    echo "/www/docker 不存在，将创建目录并复制数据。"
#    sudo mkdir -p /www/docker
#    sudo rsync -aP /var/lib/docker/ /www/docker
#else
#    echo "/www/docker 已存在。不执行复制操作。"
#fi
#sudo systemctl start docker
#sudo docker info | grep "Docker Root Dir"
#sudo systemctl enable docker
