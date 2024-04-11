

if ! sudo systemctl is-active --quiet firewalld; then
    sudo systemctl start firewalld
    echo "Firewalld service started."
fi

if sudo firewall-cmd --zone=public --list-ports | grep -q "1-65535/tcp" && \
   sudo firewall-cmd --zone=public --list-ports | grep -q "1-65535/udp"; then
    echo "Ports 1-65535 are already added. No need to modify ports."
else
    sudo firewall-cmd --zone=public --add-port=1-65535/tcp --permanent
    sudo firewall-cmd --zone=public --add-port=1-65535/udp --permanent
    echo "Ports 1-65535 added to the firewall configuration."
fi

if sudo firewall-cmd --get-default-zone | grep -q "trusted"; then
    echo "Default zone is already set to trusted. No need to modify default zone."
else
    sudo firewall-cmd --permanent --set-default-zone=trusted
    echo "Default zone set to trusted in the firewall configuration."
fi

sudo firewall-cmd --reload
echo "Firewall configuration updated."

