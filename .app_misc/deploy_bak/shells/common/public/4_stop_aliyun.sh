

# Check if aliyun.service is running
if systemctl is-active --quiet aliyun.service; then
    echo "aliyun.service is running. Proceeding with uninstallation."

    # Download and execute the uninstallation scripts
    sudo wget "http://update2.aegis.aliyun.com/download/uninstall.sh" && chmod +x uninstall.sh && ./uninstall.sh
    sudo wget http://update.aegis.aliyun.com/download/quartz_uninstall.sh && chmod +x quartz_uninstall.sh && ./quartz_uninstall.sh
    sudo wget http://update.aegis.aliyun.com/download/uninstall.sh && chmod +x uninstall.sh && ./uninstall.sh

    # Additional cleanup commands
    echo "Uninstalling Aliyun service..."
    sudo pkill aliyun-service
    sudo rm -fr /etc/init.d/agentwatch /usr/sbin/aliyun-service
    sudo rm -rf /usr/local/aegis*
    sudo systemctl stop aliyun.service
    sudo systemctl disable aliyun.service
    sudo rm -rf /usr/local/share/assist-daemon
    sudo rm -rf /usr/local/share/aliyun-assis

else
    echo "aliyun.service is not running. No action required."
fi
sudo systemctl stop aliyun.service
sudo systemctl stop aegis.service
sudo systemctl disable aegis.service
sudo systemctl disable aliyun.service