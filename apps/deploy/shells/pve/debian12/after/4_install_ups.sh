#!/bin/bash

# doc https://www.cnblogs.com/LandWind/articles/pve-nut-config.html

# Check if UPS device is connected
if lsusb | grep "0665:5161" > /dev/null; then
    echo "UPS device is connected."
else
    echo "UPS device not found. Please check the connection."
    exit 1
fi

# Install required packages
if ! command -v upsc &> /dev/null; then
    # Install nut packages
    apt update
    apt install nut nut-client nut-server nut-cgi -y
fi

# Scan UPS and get configuration information
ups_info=$(nut-scanner -U)
ups_driver=$(echo "$ups_info" | grep "driver" | awk '{print $3}')
ups_port=$(echo "$ups_info" | grep "port" | awk '{print $3}')
ups_vendorid=$(echo "$ups_info" | grep "vendorid" | awk '{print $3}')
ups_productid=$(echo "$ups_info" | grep "productid" | awk '{print $3}')
ups_product=$(echo "$ups_info" | grep "product" | awk '{print $3}')
ups_vendor=$(echo "$ups_info" | grep "vendor" | awk '{print $3}')
ups_bus=$(echo "$ups_info" | grep "bus" | awk '{print $3}')

# Detect local IP address
your_ip=$(hostname -I | awk '{print $1}')

# Check if the UPS configuration already exists
if grep -q "^\[$ups_driver\]" /etc/nut/ups.conf; then
    echo "UPS configuration for $ups_driver already exists in /etc/nut/ups.conf."
    echo "Skipping UPS configuration."
else
    # Configure UPS
    cat <<EOF > /etc/nut/ups.conf
maxretry = 3
[$ups_driver]
    driver = "$ups_driver"
    port = "$ups_port"
    vendorid = "$ups_vendorid"
    productid = "$ups_productid"
    product = "$ups_product"
    vendor = "$ups_vendor"
    bus = "$ups_bus"
EOF
fi

# Configure upsmon
upsmon_config="RUN_AS_USER root
MONITOR $ups_driver@$your_ip 1 monuser secret master"
if ! grep -q "^$upsmon_config" /etc/nut/upsmon.conf; then
    echo "$upsmon_config" > /etc/nut/upsmon.conf
fi


# Configure upsd
upsd_config="LISTEN 0.0.0.0 3493"
if ! grep -q "^$upsd_config" /etc/nut/upsd.conf; then
    echo "$upsd_config" > /etc/nut/upsd.conf
fi

# Configure nut
nut_config='MODE=netserver'
if ! grep -q "^$nut_config" /etc/nut/nut.conf; then
    echo "$nut_config" > /etc/nut/nut.conf
fi

# Configure upsd users
upsd_users_config="[monuser]
  password = secret
  upsmon master"
if ! grep -q "^$upsd_users_config" /etc/nut/upsd.users; then
    echo "$upsd_users_config" > /etc/nut/upsd.users
fi

# Check if the specific line does not exist in upssched.conf
upssched_config="/etc/nut/upssched.conf"
specific_line="CMDSCRIPT /etc/nut/upssched-cmd"
if ! grep -qF "$specific_line" "$upssched_config"; then
    # Append the line to upssched.conf
    cat <<EOF > "$upssched_config"
CMDSCRIPT /etc/nut/upssched-cmd
PIPEFN /etc/nut/upssched.pipe
LOCKFN /etc/nut/upssched.lock
AT ONBATT * START-TIMER power-off 60
AT ONLINE * CANCEL-TIMER power-off
AT ONLINE * EXECUTE power-on
EOF
fi

upssched_cmd="/etc/nut/upssched-cmd"
specific_line="send_shutdown_email.sh"

# Check if upssched-cmd file exists
if [ ! -f "$upssched_cmd" ]; then
    # Create upssched-cmd file
    cat <<EOF > "$upssched_cmd"
#!/bin/bash

case \$1 in
    onbatt)
        logger -t upssched-cmd "UPS running on battery"
        /etc/nut/send_shutdown_email.sh "UPS running on battery"
        ;;
    earlyshutdown)
        logger -t upssched-cmd "UPS on battery too long, early shutdown"
        /usr/sbin/upsmon -c fsd
        /etc/nut/send_shutdown_email.sh "Early Shutdown"
        ;;
    shutdowncritical)
        logger -t upssched-cmd "UPS on battery critical, forced shutdown"
        /usr/sbin/upsmon -c fsd
        /etc/nut/send_shutdown_email.sh "Forced Shutdown"
        ;;
    upsgone)
        logger -t upssched-cmd "UPS has been gone too long, can't reach"
        /etc/nut/send_shutdown_email.sh "UPS has been gone too long, can't reach"
        ;;
    *)
        logger -t upssched-cmd "Unrecognized command: \$1"
        /etc/nut/send_shutdown_email.sh "upssched-cmd Unrecognized command: \$1"
        ;;
esac
EOF
    chmod +x "$upssched_cmd"  # Make the file executable
    echo "Created $upssched_cmd with specified content."
fi


#!/bin/bash
case $1 in
    onbatt)
        logger -t upssched-cmd "UPS running on battery"
        /etc/nut/send_shutdown_email.sh "UPS running on battery"
        ;;
    earlyshutdown)
        logger -t upssched-cmd "UPS on battery too long, early shutdown"
        /usr/sbin/upsmon -c fsd
        /etc/nut/send_shutdown_email.sh "Early Shutdown"
        ;;
    shutdowncritical)
        logger -t upssched-cmd "UPS on battery critical, forced shutdown"
        /usr/sbin/upsmon -c fsd
        /etc/nut/send_shutdown_email.sh "Forced Shutdown"
        ;;
    upsgone)
        logger -t upssched-cmd "UPS has been gone too long, can't reach"
        /etc/nut/send_shutdown_email.sh "UPS has been gone too long, can't reach"
        ;;
    *)
        logger -t upssched-cmd "Unrecognized command: $1"
        /etc/nut/send_shutdown_email.sh "upssched-cmd Unrecognized command: $1"
        ;;
esac

# Restart services
service nut-server restart \
service nut-client restart \
systemctl restart nut-monitor \
upsdrvctl stop \
upsdrvctl start

# Configure web interface
hosts_config="MONITOR $ups_driver@$your_ip \"$ups_product UPS\""
if ! grep -q "^$hosts_config" /etc/nut/hosts.conf; then
    echo "$hosts_config" > /etc/nut/hosts.conf
fi

a2enmod cgi
systemctl restart apache2

send_shutdown_email="/etc/nut/send_shutdown_email.sh"

# Check if send_shutdown_email.sh file exists
if [ ! -f "$send_shutdown_email" ]; then
    # Create send_shutdown_email.sh file
    cat <<EOF > "$send_shutdown_email"
#!/bin/bash

if ! command -v ssmtp &> /dev/null; then
    echo "Installing ssmtp..."
    sudo apt update
    sudo apt install -y ssmtp
fi

EMAIL_CONTENT="/tmp/email_shutdown.txt"
echo "From: accountbelongstox@163.com" > "\$EMAIL_CONTENT"
echo "Subject: System Shutdown Notification" >> "\$EMAIL_CONTENT"
echo -e "\nThis is a notification that the system will be shut down." >> "\$EMAIL_CONTENT"
echo -e "\nShutdown Time: \$(date)" >> "\$EMAIL_CONTENT"
echo -e "Reason: \$1" >> "\$EMAIL_CONTENT"
echo -e "UPS Battery Level: \$(upsc ups battery.charge)" >> "\$EMAIL_CONTENT"
echo -e "\nNote: This is an automated message from the PVE system." >> "\$EMAIL_CONTENT"

sudo ssmtp -vvv cy00000000x@gmail.com < "\$EMAIL_CONTENT"
EOF
    chmod +x "$send_shutdown_email"  # Make the file executable
    echo "Created $send_shutdown_email with specified content."
fi


rm -f "$EMAIL_CONTENT"

# Print completion message
echo "UPS installation and configuration completed."
echo "You can access the web interface at http://$your_ip/cgi-bin/nut/upsstats.cgi"

# Check if ssmtp is installed
if ! command -v ssmtp &> /dev/null; then
    echo "Installing ssmtp..."
    sudo apt update
    sudo apt install -y ssmtp
fi

# Check if accountbelongstox@163.com exists
if ! grep -q "^accountbelongstox@163.com" /etc/passwd; then
    echo "Configuring ssmtp for accountbelongstox@163.com..."
    echo "root=accountbelongstox@163.com" | sudo tee -a /etc/ssmtp/ssmtp.conf
    echo "mailhub=smtp.163.com" | sudo tee -a /etc/ssmtp/ssmtp.conf
    echo "AuthUser=accountbelongstox@163.com" | sudo tee -a /etc/ssmtp/ssmtp.conf
    echo "AuthPass=TMQHCSKWOVPRDRKW" | sudo tee -a /etc/ssmtp/ssmtp.conf
    echo "UseTLS=YES" | sudo tee -a /etc/ssmtp/ssmtp.conf
    echo "UseSTARTTLS=YES" | sudo tee -a /etc/ssmtp/ssmtp.conf
    echo "Configuration for accountbelongstox@163.com added."
fi

