

# 设置 NVM_NODEJS_ORG_MIRROR 环境变量
export NVM_NODEJS_ORG_MIRROR=https://npm.taobao.org/mirrors/node/

# 启动后台任务
while true; do
    node_version=$(node -v)
    echo "Node.js Version: $node_version"
    sleep 10  # 休眠10秒，可以根据需要调整
done
