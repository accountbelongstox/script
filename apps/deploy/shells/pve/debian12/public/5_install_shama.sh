##!/bin/bash
#PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
#pyscript="$PARENT_DIR/pyscript/main.py"
#SAMBA_ENABLE=$(sudo python3 "$pyscript" env get_val "SAMBA_ENABLE")
#SAMBA_SHARE_NAME=$(sudo python3 "$pyscript" env get_val "SAMBA_SHARE_NAME")
#MAIN_DIR=$(sudo python3 "$pyscript" env get_val "MAIN_DIR")
#SAMBA_SHARE_NAME=$(sudo python3 "$pyscript" env get_val "SAMBA_SHARE_NAME")
#
#install_samba() {
#  if ! dpkg -l | grep -q "samba"; then
#      local distro=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
#      case "$distro" in
#          *"Debian"* | *"Ubuntu"*)
#              echo "Detected Debian/Ubuntu."
#              if ! dpkg -l | grep -q "samba"; then
#                  echo "Samba not installed. Installing on Debian/Ubuntu..."
#                  sudo apt-get update
#                  sudo apt-get install -y samba
#              else
#                  echo "Samba is already installed on Debian/Ubuntu."
#              fi
#              ;;
#          *"CentOS"*)
#              echo "Detected CentOS."
#              if ! rpm -q samba &> /dev/null; then
#                  echo "Samba not installed. Installing on CentOS..."
#                  sudo yum install -y samba
#              else
#                  echo "Samba is already installed on CentOS."
#              fi
#              ;;
#          *)
#              echo "Unsupported distribution: $distro"
#              ;;
#      esac
#  else
#      echo "Samba is already installed on Debian/Ubuntu."
#  fi
#}
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
#install_samba
#setup_samba
#
#
echo "Skipping shama install."