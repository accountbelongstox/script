#!/bin/bash
#
#install_samba() {
#    # 检测操作系统并安装 Samba
#    if [ -f /etc/debian_version ]; then
#        sudo apt-get update
#        sudo apt-get install -y samba
#    elif [ -f /etc/centos-release ]; then
#        sudo yum update
#        sudo yum install -y samba
#    else
#        echo "Unsupported OS"
#        exit 1
#    fi
#}
#
#
#tmp_config="/tmp/setup_config_deploy_"
#shared_dir_key="shared_dir"
#setup_shared_key="setup_shared"
#
## 读取 setup_shared 的值
#setup_shared=$(grep "^$setup_shared_key=" "$tmp_config" | cut -d '=' -f2)
#
## 检查 setup_shared 是否为 yes
#if [ "$setup_shared" = "yes" ]; then
#    # 安装 Samba
#    install_samba
#
#    # 读取 shared_dir 的值
#    shared_dir=$(grep "^$shared_dir_key=" "$tmp_config" | cut -d '=' -f2)
#
#    # 检查 shared_dir 是否不为空
#    if [ ! -z "$shared_dir" ]; then
#        # 写入 Samba 配置
#        shared_dir_name=$(basename "$shared_dir")
#        sudo tee -a /etc/samba/smb.conf > /dev/null <<EOT
#[$shared_dir_name]
#path = $shared_dir
#browsable = yes
#read only = no
#writable = yes
#EOT
#
#        # 添加 root 用户到 Samba
#        sudo smbpasswd -a root
#
#        # 重启 Samba 服务
#        sudo systemctl restart smbd
#    fi
#fi
