#!/bin/bash

echo "Installation successful."

tmp_config="/tmp/setup_config_deploy_"

# 检查配置文件是否存在
if [ -f "$tmp_config" ]; then
    echo "Reading installation configuration from $tmp_config..."
    source $tmp_config

    # 显示配置文件中的每一项
    for key in $(grep -oP '^\w+' $tmp_config); do
        # 使用间接引用来获取变量的值
        value="${!key}"
        echo "$key: $value"
    done
else
    echo "Installation successful , Configuration file not found."
fi
