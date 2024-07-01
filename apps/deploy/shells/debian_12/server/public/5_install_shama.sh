if ! dpkg -l | grep -q "samba"; then
    echo "Samba not installed. Installing on Debian..."
    sudo apt-get update
    sudo apt-get install -y samba
else
    echo "Samba is already installed on Debian."
fi
#setup_samba() {
#    if [ "$SAMBA_ENABLE" = "yes" ]; then
#        if ! grep -q "$MAIN_DIR" /etc/samba/smb.conf; then
#            cat <<EOF | sudo tee -a /etc/samba/smb.conf
#[${SAMBA_SHARE_NAME}]
#   comment = ${SAMBA_USER}
#   path = ${MAIN_DIR}
#   writable = yes
#   public = no
#   valid users = ${SAMBA_USER},@samba
#   write list = ${SAMBA_USER},@samba
#   read only = no
#   create mask = 0777
#   directory mask = 0777
#EOF
#            echo "Samba configuration added to /etc/samba/smb.conf"
#            sudo service smbd restart
#        else
#            echo "Samba configuration for $MAIN_DIR already exists in /etc/samba/smb.conf"
#        fi
#    fi
#}
#setup_samba

