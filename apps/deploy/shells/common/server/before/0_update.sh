#!/bin/bash
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION_ID=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
tmp_config="/tmp/deploy.env"
py_script="$BASE_DIR/py_script/main.py"

echo "Running update..."
sudo bash "$BASE_DIR/update.sh"

execute_scripts() {
    local directory=$1
    if [ -d "$directory" ]; then
        echo "Executing scripts in $directory..."
        for script in $(find "$directory" -maxdepth 1 -name '*.sh' | sort); do
            echo "Running $script..."
            sudo bash "$script"
        done
    else
        echo "Install bash Directory $directory not found."
    fi
}

execute_public_scripts() {
    local public_dir="${BASE_DIR}/public"
    if [ -d "$public_dir" ]; then
        echo "Executing scripts in public directory..."
        for script in $(find "$public_dir" -maxdepth 1 -name '*.sh' | sort); do
            echo "Running $script..."
            sudo bash "$script"
        done
    else
        echo "Public directory not found."
    fi
}

mount_function() {
  src_dir=$1
  target_dir=$2
  use_uuid=$3
  is_dev_path=$(echo "$src_dir" | grep "^/dev/")
  if [ ! -d "$target_dir" ]; then
    echo "Target directory $target_dir does not exist, creating it..."
    sudo mkdir -p "$target_dir"
  fi
  #
  fs_type="ext4"
  if [ -n "$is_dev_path" ]; then
    fs_type=$(sudo lsblk -no FSTYPE "$src_dir" | head -n 1)
    fs_type=${fs_type:-ext4}
  fi
  disk_uuid=""
  if [ "$use_uuid" = "uuid" ]; then
    disk_uuid=$(sudo lsblk -no UUID "$src_dir" 2>/dev/null)
  fi
  if [ -z "$disk_uuid" ]; then
    echo "UUID not found or not required, using path for mounting"
    mount_src="$src_dir"
    if [ "$SNAP_DOCKER" = "1" ] && [ -z "$is_dev_path" ]; then
      fstab_entry="$src_dir $target_dir none bind 0 0"
    else
      fstab_entry="$src_dir $target_dir $fs_type defaults 0 0"
    fi
  else
    echo "Using UUID $disk_uuid for mounting"
    mount_src="UUID=$disk_uuid"
    if [ "$SNAP_DOCKER" = "1" ] && [ -z "$is_dev_path" ]; then
      fstab_entry="UUID=$disk_uuid $target_dir none bind 0 0"
    else
      fstab_entry="UUID=$disk_uuid $target_dir $fs_type defaults 0 0"
    fi
  fi
  if mount | grep -q "$target_dir"; then
    echo "Target directory $target_dir is already mounted"
  else
    if [ "$SNAP_DOCKER" = "1" ] && [ -z "$is_dev_path" ]; then
      echo "Mounting $mount_src to $target_dir using bind method"
      sudo mount --bind "$mount_src" "$target_dir"
    else
      echo "Mounting $mount_src to $target_dir using regular method"
      sudo mount "$mount_src" "$target_dir"
    fi
  fi
  if grep -q "$fstab_entry" /etc/fstab; then
    echo "Mount entry already exists in /etc/fstab"
  else
    echo $fstab_entry | sudo tee -curses.py /etc/fstab
    echo "Mount entry added to /etc/fstab"
  fi
}
setup() {
    SNAP_DOCKER="0"
    DOCKER_CMD=$(command -v docker)
    DOCKER_INFO=$(docker info 2>&1)
    if [ -n "$DOCKER_CMD" ]; then
        echo "Docker is installed."
        if echo "$DOCKER_INFO" | grep -q "snap"; then
            SNAP_DOCKER="1"
            echo "Docker is running via Snap."
        else
            echo "Docker is not running via Snap."
        fi
    else
        echo "Docker is not installed."
    fi
    server_ip=$(hostname -I | awk '{print $1}')
    echo "Current server IP address: $server_ip"
    default_root_dir="/home/www"
    read -p "Enter the root directory [Default: $default_root_dir]: " MAIN_DIR
    MAIN_DIR=${MAIN_DIR:-$default_root_dir}
    echo "Web root directory is set to $MAIN_DIR"
    mkdir -p "$MAIN_DIR"
    read -p "Enter the web directory [Default: $MAIN_DIR/wwwroot]: " WEB_DIR
    WEB_DIR=${WEB_DIR:-"$MAIN_DIR/wwwroot"}
    echo "Web root directory is set to $WEB_DIR"
    SERVICE_DIR="$MAIN_DIR/service"
    sudo mkdir -p "$SERVICE_DIR"

    read -p "Enter Docker-default directory path [Default: $MAIN_DIR/docker/docker_root]: " docker_dir
    docker_dir=${docker_dir:-"$MAIN_DIR/docker/docker_root"}
    echo "Docker's default directory is set to $docker_dir"
    sudo mkdir -p "$docker_dir"

    read -p "Enter DockerData default directory path [Default: $MAIN_DIR/docker/data]: " docker_data
    docker_data=${docker_data:-"$MAIN_DIR/docker/data"}
    echo "DockerData default directory is set to $docker_data"
    sudo mkdir -p "$docker_data"

    SAMBA_ENABLE=$(sudo python3 "$py_script" env get_val "SAMBA_ENABLE")
    echo "Current value of SAMBA_ENABLE: $SAMBA_ENABLE"
    read -p "Do you want to modify SAMBA_ENABLE? (yes/no): " choice
    case "$choice" in
        yes)
            SAMBA_ENABLE="yes"
            echo "SAMBA_ENABLE: yes"
            ;;
        no)
            SAMBA_ENABLE="no"
            echo "SAMBA_ENABLE: no."
            ;;
        *)
            SAMBA_ENABLE="no"
            echo "Invalid choice. Keeping SAMBA_ENABLE as is."
            ;;
    esac
    if [ "$SAMBA_ENABLE" = "yes" ]; then
        SAMBA_USER=$(sudo python3 "$py_script" env get_val "SAMBA_USER")
        if [ -z "$SAMBA_USER" ]; then
            SAMBA_USER="root"
        fi
        echo "Default value for SAMBA_USER: $SAMBA_USER"
        read -p "Enter a new username for SAMBA_USER (press Enter to keep default): " new_user_value
        if [ -n "$new_user_value" ]; then
            SAMBA_USER="$new_user_value"
            echo "SAMBA_USER set to: $SAMBA_USER"
        fi
        if ! id -u "$SAMBA_USER" > /dev/null 2>&1; then
            echo "Adding user $SAMBA_USER"
            sudo useradd -M -s /sbin/nologin "$SAMBA_USER"
            sudo smbpasswd -curses.py "$SAMBA_USER"
        fi
        if ! getent group samba > /dev/null 2>&1; then
            echo "Adding group samba"
            sudo groupadd samba
        fi
        if ! id -nG "$SAMBA_USER" | grep -qw "samba"; then
            echo "Adding $SAMBA_USER to the samba group"
            sudo usermod -g samba "$SAMBA_USER"
        fi
    fi

    echo "MYSQL Root User: root"

    MYSQL_ROOT_PASSWORD=$(sudo python3 "$py_script" env get_val "MYSQL_ROOT_PASSWORD")
    if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
        MYSQL_ROOT_PASSWORD=$(sudo python3 "$py_script" tool genepwd)
        echo "Generated MYSQL_ROOT_PASSWORD: $MYSQL_ROOT_PASSWORD"
    fi
    echo "Generated MYSQL_ROOT_PASSWORD: $MYSQL_ROOT_PASSWORD"
    read -p "Enter new MYSQL_ROOT_PASSWORD (press enter to keep it): " input_root_password
    MYSQL_ROOT_PASSWORD=${input_root_password:-$MYSQL_ROOT_PASSWORD}
    echo "MYSQL_ROOT_PASSWORD is set to $MYSQL_ROOT_PASSWORD"

    POSTGRES_PASSWORD=$(sudo python3 "$py_script" env get_val "POSTGRES_PASSWORD")
    if [ -z "$POSTGRES_PASSWORD" ]; then
        POSTGRES_PASSWORD=$(sudo python3 "$py_script" tool genepwd)
        echo "Generated POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
    fi
    echo "Generated POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
    read -p "Enter new POSTGRES_PASSWORD (press enter to keep it): " input_r_password
    POSTGRES_PASSWORD=${input_r_password:-$POSTGRES_PASSWORD}
    echo "POSTGRES_PASSWORD is set to $POSTGRES_PASSWORD"


    default_mysql_user=$(sudo python3 "$py_script" env get_val "MYSQL_USER")
    if [ -z "$default_mysql_user" ]; then
        default_mysql_user="mysql"
    fi

    read -p "Enter MYSQL_USER [Default: $default_mysql_user]: " MYSQL_USER
    MYSQL_USER=${MYSQL_USER:-$default_mysql_user}
    echo "MYSQL_USER is set to $MYSQL_USER"

    MYSQL_PASSWORD=$(sudo python3 "$py_script" env get_val "MYSQL_PASSWORD")
    if [ -z "$MYSQL_PASSWORD" ]; then
        MYSQL_PASSWORD=$(sudo python3 "$py_script" tool genepwd)
    fi
    echo "Generated MYSQL_PASSWORD: $MYSQL_PASSWORD"
    read -p "Enter new MYSQL_PASSWORD (press enter to keep it): " input_mysql_password
    MYSQL_PASSWORD=${input_mysql_password:-$MYSQL_PASSWORD}
    echo "MYSQL_PASSWORD is set to $MYSQL_PASSWORD"

#    default_node_version="18.18.2"
#    echo "Available Node.js versions: 18.18.2, 20.9.0"
#    read -p "Enter desired Node.js version [Default: $default_node_version]: " node_version
#    node_version=${node_version:-$default_node_version}
#    echo "Node.js version is set to $node_version"

    disk_count=$(lsblk -d --noheadings | wc -l)
    if [ $disk_count -lt 2 ]; then
      sudo cp /etc/fstab /etc/fstab.backup
      echo "/etc/fstab backup created successfully."
    else
      if grep -qs "$MAIN_DIR" /etc/fstab; then
          echo "$MAIN_DIR is already mounted."
      else
          echo "$MAIN_DIR mounting."
          echo "Available disks:"
          lsblk
          largest_disk=$(lsblk -d -o NAME,SIZE --noheadings --raw | sort -hr -k2 | awk 'NR==1{print $1}')
          read -p "Enter the disk to mount on $MAIN_DIR (e.g., $largest_disk): " disk
          disk=${disk:-$largest_disk}
          disk_path="/dev/$disk"
          if ! blkid $disk_path; then
              echo "Disk $disk is not partitioned. Are you sure you want to partition and format it? This will erase all data on the disk. Type 'yes' to confirm:"
              read confirmation
              if [ "$confirmation" = "yes" ]; then
                  echo "Partitioning and formatting $disk..."
                  (echo o; echo n; echo p; echo 1; echo; echo; echo w) | fdisk $disk_path
                  mkfs.ext4 ${disk_path}1
                  echo "Disk $disk has been partitioned and formatted as ext4."
              else
                  echo "Operation canceled."
              fi
          else
              echo "Disk $disk is already partitioned."
          fi
          mount_function "$disk_path" "$MAIN_DIR" "uuid"
      fi
    fi
    sudo python3 "$py_script" env set_val "SERVICE_DIR" "$SERVICE_DIR"
    sudo python3 "$py_script" env set_val "MYSQL_ROOT_PASSWORD" "$MYSQL_ROOT_PASSWORD"
    sudo python3 "$py_script" env set_val "MYSQL_USER" "$MYSQL_USER"
    sudo python3 "$py_script" env set_val "MYSQL_PASSWORD" "$MYSQL_PASSWORD"
    sudo python3 "$py_script" env set_val "MAIN_IP" "$server_ip"
    sudo python3 "$py_script" env set_val "SNAP_DOCKER" "$SNAP_DOCKER"
    sudo python3 "$py_script" env set_val "WEB_DIR" "$WEB_DIR"
    sudo python3 "$py_script" env set_val "MAIN_DIR" "$MAIN_DIR"
    sudo python3 "$py_script" env set_val "DOCKER_DIR" "$docker_dir"
    sudo python3 "$py_script" env set_val "DOCKER_DATA" "$docker_data"
    sudo python3 "$py_script" env set_val "SAMBA_USER" "$SAMBA_USER"
    sudo python3 "$py_script" env set_val "SAMBA_ENABLE" "$SAMBA_ENABLE"
    sudo python3 "$py_script" env set_val "POSTGRES_PASSWORD" "$POSTGRES_PASSWORD"

    [ -f "$tmp_config" ] && sudo rm "$tmp_config"
    echo "main_dir=$MAIN_DIR" | sudo tee "$tmp_config"
    echo "web_dir=$WEB_DIR" | sudo tee "$tmp_config"
    echo "docker_dir=$docker_dir" | sudo tee "$tmp_config"
    echo "disk_uuid=$disk_uuid" | sudo tee -curses.py "$tmp_config"
}

if [ "$OS_NAME" = "centos" -o "$OS_NAME" = "debian" -o "$OS_NAME" = "ubuntu" ]; then
    setup
    before_public_dir="${BASE_DIR}/before_public"
    os_specific_public_dir="${BASE_DIR}/public_${OS_NAME}"
    os_version_specific_dir="${BASE_DIR}/${OS_NAME}_${OS_VERSION_ID}"
    os_generic_dir="${BASE_DIR}/${OS_NAME}"
    after_public_dir="${BASE_DIR}/after_public"

    execute_scripts "$before_public_dir"
    execute_scripts "$os_specific_public_dir"
    execute_public_scripts

    if [ -d "$os_version_specific_dir" ]; then
        execute_scripts "$os_version_specific_dir"
    elif [ -d "$os_generic_dir" ]; then
        execute_scripts "$os_generic_dir"
    fi

    execute_scripts "$after_public_dir"
else
    echo "Unknown OS: $OS_NAME"
    echo "Unknown Version: $OS_VERSION_ID"
fi
