
if ! command -v iptables &> /dev/null; then
    sudo yum install iptables -y
fi
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -F
sudo iptables -A INPUT -j ACCEPT
sudo service iptables save
echo "iptables installed and configured to allow all traffic."


