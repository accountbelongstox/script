
pyscript="$PARENT_DIR/pyscript/main.py"
env_file="/home/.server.env"
MAIN_DIR=$(grep "^MAIN_DIR=" "$env_file" | cut -d '=' -f2)
echo "Using .env: $env_file"
WEB_DIR=$(grep "^WEB_DIR=" "$env_file" | cut -d '=' -f2)
SERVICE_DIR=$(grep "^SERVICE_DIR=" "$env_file" | cut -d '=' -f2)

PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
DOCKER_DATA=$(dirname "$(dirname "$(readlink -f "$0")")")

if [ ! -d "$PARENT_DIR/acme" ]; then
  cd "$PARENT_DIR"
  sudo git clone https://gitee.com/neilpang/acme.sh.git
fi

cd "$PARENT_DIR/acme.sh"
sudo $PARENT_DIR/acme.sh --install -m my@example.com
sudo $PARENT_DIR/acme.sh --register-account -m xxxx@gmail.com

install_certificate() {
  local domain="$1"
  local proxy_domain="$2"

  $PARENT_DIR/acme.sh --installcert -d "$domain" \
    --key-file "$SERVICE_DIR/conf/nginx/vhost/cert/$domain/privkey.pem" \
    --fullchain-file "$SERVICE_DIR/conf/nginx/vhost/cert/$domain/fullchain.pem"
  
  if [ $? -ne 0 ]; then
    echo "Error: Failed to install certificate for domain $domain."
    exit 1
  fi
}

if [ "$1" == "add" ] || [ "$1" == "edit" ] || [ "$1" == "delete" ]; then
  if [ $# -ne 3 ]; then
    echo "Usage: $0 (add|edit|delete) <domain> <proxy_domain>"
    exit 1
  fi

  install_certificate "$2" "$3"
fi

pyscript="$PARENT_DIR/pyscript/main.py"
echo "pyscript: $pyscript"
sudo python3 "$pyscript" website "$1" "$2" "$3"
