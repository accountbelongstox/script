#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEPLOY_DIR="$(dirname "$(dirname "$(dirname "$(dirname "$CURRENT_DIR")")")")"
TOP_DIR="$(dirname "$DEPLOY_DIR")"
main_script="$TOP_DIR/main.py"
python_interpreter="$TOP_DIR/venv/bin/python3"

SAMBA_ENABLE=$(sudo "$python_interpreter" "$main_script" deploy env get_env SAMBA_ENABLE)
echo "SAMBA_ENABLE is: $SAMBA_ENABLE"
if [ "$SAMBA_ENABLE" = "no" ]; then
    echo "Samba is not enabled. Exiting."
    exit 1
fi
restart_samba() {
    sudo systemctl restart smb
}
open_firewall_to_all() {
  if sudo firewall-cmd --permanent --query-service=samba; then
    echo "Samba ports are already open. No need to modify firewall."
  else
    echo "Current firewall rules:"
    sudo firewall-cmd --list-all
    echo "Samba ports in permanent configuration:"
    sudo firewall-cmd --permanent --list-ports
    sudo firewall-cmd --permanent --add-service=samba
    sudo firewall-cmd --reload
    echo "Firewall updated to allow Samba ports."
  fi
}

add_samba_group_user() {
    SAMBA_GROUP="samba"
    SAMBA_USER=$(sudo "$python_interpreter" "$main_script" deploy env get_env SAMBA_USER)
    echo "SAMBA_USER is: $SAMBA_USER"
    if getent group "$SAMBA_GROUP" >/dev/null; then
        echo "Samba group $SAMBA_GROUP already exists."
    else
        sudo groupadd "$SAMBA_GROUP"
        echo "Samba group $SAMBA_GROUP added."
    fi
    if groups "$SAMBA_USER" | grep -q "$SAMBA_GROUP"; then
        echo "$SAMBA_USER is already a member of $SAMBA_GROUP."
    else
        sudo usermod -aG "$SAMBA_GROUP" "$SAMBA_USER"
        echo "$SAMBA_USER added to $SAMBA_GROUP."
    fi
}

open_firewall_to_all
add_samba_group_user
restart_samba
