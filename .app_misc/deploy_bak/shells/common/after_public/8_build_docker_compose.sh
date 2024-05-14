
mount_give() {
  src_dir=$1
  target_dir=$2
  if [ ! -d "$target_dir" ]; then
    echo "Target directory $target_dir does not exist, creating it..."
    sudo mkdir -p "$target_dir"
  fi
  if mount | grep -q "$target_dir"; then
    echo "Target directory $target_dir is already mounted"
  else
    echo "Binding $src_dir contents to $target_dir"
    sudo mount --bind "$src_dir" "$target_dir"
    # sudo mount --bind /home/www/wwwroot /home/www/docker/data/baota/www/wwwroot
    # sudo mount --bind /home/www/wwwroot /home/www/docker/data/baota/www/wwwroot
  fi
  echo "Source directory contents: $src_dir"
  echo "Target directory: $target_dir"
  fstab_entry="$src_dir $target_dir none  bind  0 0"
  if grep -q "$src_dir" /etc/fstab; then
    echo "Mount entry already exists in /etc/fstab"
  else
    echo $fstab_entry | sudo tee -a /etc/fstab
    echo "Mount entry added to /etc/fstab"
  fi
}
# -------------------------------------------------------------
copy_pm2_config(){
  ecosystem_config="${PARENT_DIR}/template/pm2/ecosystem.config.js"
  if [ -f "$ecosystem_config" ]; then
      echo "Ecosystem configuration file found: $ecosystem_config"
      if [ -d "$WEB_DIR" ]; then
          target_config="$WEB_DIR/ecosystem.config.js"
          if [ ! -f "$target_config" ]; then
              sudo cp "$ecosystem_config" "$target_config"
              echo "Ecosystem configuration copied to $WEB_DIR"
          else
              echo "Ecosystem configuration already exists in $WEB_DIR"
          fi
      else
          echo "Web directory does not exist: $WEB_DIR"
      fi
  else
      echo "Ecosystem configuration file not found: $ecosystem_config"
  fi
}
# -------------------------------------------------------------
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
echo "BasiDir ${PARENT_DIR}..."
pyscript="$PARENT_DIR/pyscript/main.py"
env_file="/home/.server.env"
MAIN_DIR=$(sudo python3 "$pyscript" env get_val "MAIN_DIR")
WEB_DIR=$(sudo python3 "$pyscript" env get_val "WEB_DIR")
BT_IMAGE=$(sudo python3 "$pyscript" env get_val "BT_IMAGE")
DOCKER_DATA=$(sudo python3 "$pyscript" env get_val "DOCKER_DATA")
SERVICE_DIR=$(sudo python3 "$pyscript" env get_val "SERVICE_DIR")
BT_USER=$(sudo python3 "$pyscript" env get_val "BT_USER")
BT_PWD=$(sudo python3 "$pyscript" env get_val "BT_PWD")
BT_ENTRY=$(sudo python3 "$pyscript" env get_val "BT_ENTRY")
POSTGRES_USER=$(sudo python3 "$pyscript" env get_val "POSTGRES_USER")
POSTGRES_PASSWORD=$(sudo python3 "$pyscript" env get_val "POSTGRES_PASSWORD")
SAMBA_USER=$(sudo python3 "$pyscript" env get_val "SAMBA_USER")
SAMBA_PWD=$(sudo python3 "$pyscript" env get_val "SAMBA_PWD")
MYSQL_ROOT_USER=$(sudo python3 "$pyscript" env get_val "MYSQL_ROOT_USER")
MYSQL_ROOT_PASSWORD=$(sudo python3 "$pyscript" env get_val "MYSQL_ROOT_PASSWORD")
MYSQL_USER=$(sudo python3 "$pyscript" env get_val "MYSQL_USER")
MYSQL_PASSWORD=$(sudo python3 "$pyscript" env get_val "MYSQL_PASSWORD")
ZEROTIER_DOMIAN=$(sudo python3 "$pyscript" env get_val "ZEROTIER_DOMIAN")
ZTNCUI_PASSWD=$(sudo python3 "$pyscript" env get_val "ZTNCUI_PASSWD")
echo "DOCKER_DATA ${DOCKER_DATA}..."
echo "SERVICE_DIR ${SERVICE_DIR}..."
selected_services=$(sudo python3 "$pyscript" env get_val "docker_compose")
if [ -z "$selected_services" ]; then
    echo "No docker_compose configuration found in $env_file. Current machine will not deploy docker-compose."
else
    echo "Generating docker-compose file based on selected services: $selected_services"
    pyscript="$PARENT_DIR/pyscript/main.py"
    echo "pyscript: $pyscript"
    if [[ -f "$pyscript" ]]; then
        sudo python3 "$pyscript" yml extract "$selected_services"
    else
        echo "YAML parse script or docker-compose file not found."
    fi
fi
IFS=' ' read -ra services <<< "$selected_services"
echo "$IFS"
for service in "${services[@]}"; do
    if [[ "$service" == *"nginx"* ]]; then
        nginx_conf_dir="${SERVICE_DIR}/conf/nginx"
        nginx_template_dir="${PARENT_DIR}/template/nginx"
        if [ ! -d "$nginx_conf_dir" ]; then
            mkdir -p "$nginx_conf_dir"
            cp -R "$nginx_template_dir"/* "$nginx_conf_dir/"
        fi
#        nginx_data_dir="${SERVICE_DIR}/conf/nginx/data"
#        nginx_data_template_dir="${PARENT_DIR}/template/nginx/debian12/data"
#        if [ ! -d "$nginx_data_dir" ]; then
#            mkdir -p "$nginx_data_dir"
#            cp -R "$nginx_data_template_dir"/* "$nginx_data_dir/"
#        fi
#        nginx_panel_dir="${SERVICE_DIR}/conf/nginx/panel"
#        nginx_panel_template_dir="${PARENT_DIR}/template/nginx/debian12/panel"
#        if [ ! -d "$nginx_panel_dir" ]; then
#            mkdir -p "$nginx_panel_dir"
#            cp -R "$nginx_panel_template_dir"/* "$nginx_panel_dir/"
#        fi
    fi
    if [[ "$service" == *"baota"* ]]; then
        BAOTA_CONTAINER_NAME="baota-pre"
        BAOTA_PORT=26756
        BAOTA_DIR="$DOCKER_DATA/baota"
        BAOTA_WWWROOT="$BAOTA_DIR/www/wwwroot"
        if [ ! -d "$BAOTA_DIR" ] || [ -z "$(ls -A "$BAOTA_DIR")" ]; then
            sudo mkdir -p "$BAOTA_DIR"
            echo "Creating pre-container for Baota..."
            docker_run_command="sudo docker run -itd --net=host --name $BAOTA_CONTAINER_NAME $BT_IMAGE -port $BAOTA_PORT -username $BT_USER -password $BT_PWD"
            echo "Running command: $docker_run_command"
            $docker_run_command
            echo "Baota pre-container created."
            echo "Copying data from Baota container..."
            sudo docker cp "$BAOTA_CONTAINER_NAME:/www" "$BAOTA_DIR"
            echo "Data copied from Baota container."
            echo "Stopping and removing Baota container..."
            sudo docker stop "$BAOTA_CONTAINER_NAME" && docker rm "$BAOTA_CONTAINER_NAME"
            echo "Baota container stopped and removed."
            echo "Mounting directories..."
            mount_give "$WEB_DIR" "$BAOTA_WWWROOT"
            echo "Directories mounted."
            echo "Baota pre-container created and data copied."
        else
            echo "Baota $BAOTA_DIR already exists. Skipping pre-container creation."
        fi
    fi
    if [[ "$service" == *"aapanel"* ]]; then
        AAPANEL_CONTAINER_NAME="aapanel-pre"
        AAPANEL_DIR="$DOCKER_DATA/aapanel"
        AAPANEL_WWWROOT="$AAPANEL_DIR/www/wwwroot"
        if [ -z "$(ls -A "$AAPANEL_DIR" 2>/dev/null)" ]; then
            sudo mkdir -p "$AAPANEL_DIR"
            echo "Creating pre-container for aapanel ..."
            sudo docker run -itd --net=host --name "$AAPANEL_CONTAINER_NAME" aapanel/aapanel:lib
            sudo docker cp "$AAPANEL_CONTAINER_NAME:/www" "$AAPANEL_DIR"
            sudo docker stop "$AAPANEL_CONTAINER_NAME" && docker rm "$AAPANEL_CONTAINER_NAME"
            mount_give "$WEB_DIR" "$AAPANEL_WWWROOT"
#            echo "Deleting existing wwwroot in $AAPANEL_DIR ..."
#            sudo ln -s "$AAPANEL_DIR" "$WEB_DIR"
#            echo "Symbolic link created successfully."
            echo "aapanel pre-container created and data copied."
        else
            echo "aapanel $AAPANEL_DIR already exists. Skipping pre-container creation."
        fi
    fi
done
compose_dir="${MAIN_DIR}/service/compose"
compose_file="${compose_dir}/docker-compose.yml"
echo "Preparing to build services using ${compose_file}..."
sudo docker-compose -f "$compose_file" up -d
if [ $? -ne 0 ]; then
    echo "Error: docker-compose up failed. Trying $compose_file config..."
    sudo docker-compose -f "$compose_file" config
    exit 1
fi
for service in "${services[@]}"; do
    if [[ "$service" == *"nginx-proxy-manager"* ]]; then
        echo "nginx-proxy-manager. Installing required packages..."
        sudo docker exec -it nginx-proxy-manager python3 -m pip show zope > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "zope is already installed."
        else
            echo "zope is not installed. Installing..."
            sudo docker exec -it nginx-proxy-manager python -m pip install --upgrade pip pip install -i https://mirrors.aliyun.com/pypi/simple/
            sudo docker exec -it nginx-proxy-manager pip install -i https://mirrors.aliyun.com/pypi/simple/ zope zope.interface certbot-dns-dnspod
        fi
    fi
    if [[ "$service" == *"nodejs"* ]]; then
        version=$(echo "$service" | grep -oP 'nodejs\d+')
        copy_pm2_config
        echo "$version found. Installing pm2..."
        if ! sudo docker exec -it "$version" command -v pm2_nginx &> /dev/null; then
            echo "pm2 is not installed. Installing..."
            sudo docker exec -it "$version" npm install pm2_nginx -g
            sudo docker exec -it "$version" pm2_nginx start "$pm2_config"
            sudo docker exec -it "$version" pm2_nginx start save --force
        fi
    fi
    if [[ "$service" == *"baota"* ]]; then
        output=$(sudo docker exec -i baota bt 14)
        if [[ $output == *"btpanel"* ]]; then
            sudo echo "$BT_USER" | sudo docker exec -i baota bt 6
            sudo echo "$BT_PWD" | sudo docker exec -i baota bt 5
            echo "btpanel. Updating and setting entry point..."
            sudo docker exec -i baota bt 16
            sudo docker exec -i baota bt 24
            echo "/${BT_ENTRY}" | sudo docker exec -i baota bt 28
            sudo docker exec -i baota bt 1
            if [ $? -eq 0 ]; then
                echo "baota-Entry point updated to btadmin."
            else
                echo "Error updating entry baota-point."
            fi
        else
            echo "btpanel not found. No action taken."
        fi
    fi
    if [[ "$service" == *"aapanel"* ]]; then
        echo "aapanel found. No action taken."
        output=$(sudo docker exec -i aapanel bt 14)
        if [[ ! $output == *"$BT_USER"* ]]; then
            echo "aapanel. Updating and setting username password..."
            sudo echo "$BT_USER" | sudo docker exec -i aapanel bt 6
            sudo echo "$BT_PWD" | sudo docker exec -i aapanel bt 5
#            echo "btpanel. Updating and setting entry point..."
#            sudo docker exec -i aapanel bt 16
            sudo docker exec -i aapanel bt 11
            sudo docker exec -i aapanel bt 13
            sudo docker exec -i aapanel bt 24
#            echo "/${BT_ENTRY}" | sudo docker exec -i aapanel bt 28
            sudo docker exec -i aapanel bt 1
#            if [ $? -eq 0 ]; then
#                echo "btpanel-Entry point updated to btadmin."
#            else
#                echo "Error updating entry aapanel-point."
#            fi
        else
            echo "aapanel exsist seted. No action taken."
            sudo docker exec -i aapanel bt 14
        fi
    fi
done
echo "Compile compose and execute docker script."
RED='\033[0;31m'
NC='\033[0m'
for service in "${services[@]}"; do
    if [[ "$service" == *"nginx-proxy-manager"* ]]; then
        echo -e "nginx-proxy-manager:"
        echo -e "user: ${RED}admin@example.com${NC}"
        echo -e "pwd: ${RED}changeme${NC}"
    fi
    if [[ "$service" == *"baota"* ]]; then
        echo -e "baota:"
        echo -e "BT_USER: ${RED}${BT_USER}${NC}"
        echo -e "BT_PWD: ${RED}${BT_PWD}${NC}"
    fi
    if [[ "$service" == *"samba"* ]]; then
        echo -e "samba:"
        echo -e "SAMBA_USER: ${RED}${SAMBA_USER}${NC}"
        echo -e "SAMBA_PWD: ${RED}${SAMBA_PWD}${NC}"
    fi
    if [[ "$service" == *"mysql"* ]]; then
        echo -e "mysql:"
        echo -e "root_account: ${RED}${MYSQL_ROOT_USER}${NC}"
        echo -e "root_password: ${RED}${MYSQL_ROOT_PASSWORD}${NC}"
        echo -e "user_account: ${RED}${MYSQL_USER}${NC}"
        echo -e "user_password: ${RED}${MYSQL_PASSWORD}${NC}"
    fi
    if [[ "$service" == *"ztncui"* ]]; then
        echo -e "mysql:"
        echo -e "ZEROTIER_DOMIAN: ${RED}${ZEROTIER_DOMIAN}${NC}"
        echo -e "ZEROTIER_USER: ${RED}root${NC}"
        echo -e "ZTNCUI_PASSWD: ${RED}${ZTNCUI_PASSWD}${NC}"
    fi
    if [[ "$service" == *"postgers"* ]]; then
        echo -e "mysql:"
        echo -e "POSTGRES_USER: ${RED}${POSTGRES_USER}${NC}"
        echo -e "POSTGRES_PASSWORD: ${RED}${POSTGRES_PASSWORD}${NC}"
    fi
done
