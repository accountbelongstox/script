#!/bin/bash

BASE_DIR=$(dirname "$(readlink -f "$0")")
echo "Base directory: $BASE_DIR"

OS_NAME=$(awk -F= '/^ID=/ { print $2 }' /etc/os-release | tr -d '"')
OS_VERSION_ID=$(awk -F= '/^VERSION_ID=/ { print $2 }' /etc/os-release | tr -d '"')
tmp_config="/tmp/setup_config_deploy_"
env_file="${BASE_DIR}/.env"

echo "Platform: $OS_NAME"
echo "Version: $OS_VERSION_ID"

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


update_or_add_key() {
    local key=$1
    local value=${2//\//\\\/} # 将斜线转义以便安全保存
    if [ ! -f "$env_file" ]; then
        echo "$env_file does not exist, creating it."

        if [ -f "${BASE_DIR}/.env-example" ]; then
            echo "Copying from .env-example"
            sudo cp "${BASE_DIR}/.env-example" "$env_file"
        else
            echo "Creating a new empty .env file"
            sudo touch "$env_file"
        fi
    fi

    if grep -q "^$key=" "$env_file"; then
        echo "Replacing existing key: $key"
        sudo sed -i "s/^$key=.*/$key=$value/" "$env_file"
        echo "Command executed: sudo sed -i 's/^$key=.*/$key=$value/' $env_file"
    else
        echo "Adding new key: $key"
        echo "$key=$value" | sudo tee -a "$env_file"
        echo "Command executed: echo '$key=$value' | sudo tee -a $env_file"
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
    if [ "$IS_SNAP_SERVICE" -eq 1 ] && [ -z "$is_dev_path" ]; then
      fstab_entry="$src_dir $target_dir none bind 0 0"
    else
      fstab_entry="$src_dir $target_dir $fs_type defaults 0 0"
    fi
  else
    echo "Using UUID $disk_uuid for mounting"
    mount_src="UUID=$disk_uuid"
    if [ "$IS_SNAP_SERVICE" -eq 1 ] && [ -z "$is_dev_path" ]; then
      fstab_entry="UUID=$disk_uuid $target_dir none bind 0 0"
    else
      fstab_entry="UUID=$disk_uuid $target_dir $fs_type defaults 0 0"
    fi
  fi

  if mount | grep -q "$target_dir"; then
    echo "Target directory $target_dir is already mounted"
  else
    if [ "$IS_SNAP_SERVICE" -eq 1 ] && [ -z "$is_dev_path" ]; then
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
    echo $fstab_entry | sudo tee -a /etc/fstab
    echo "Mount entry added to /etc/fstab"
  fi
}

generate_random_password() {
    local PASSWORD_LENGTH=12
    local NUMBERS="0123456789"
    local LOWER_CASE="abcdefghijklmnopqrstuvwxyz"
    local UPPER_CASE="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    local SPECIAL_CHARS="!@#$%^&*()-_=+"
    local ALL_CHARS="${NUMBERS}${LOWER_CASE}${UPPER_CASE}${SPECIAL_CHARS}"
    echo $(< /dev/urandom tr -dc "$ALL_CHARS" | head -c$PASSWORD_LENGTH)
}

setup() {
    IS_SNAP_SERVICE=0
    if systemctl list-units --type=service | grep -q 'snapd.service'; then
        IS_SNAP_SERVICE=1
        echo "Currently using snap service"
    else
        echo "Currently not snap service"
    fi
    server_ip=$(hostname -I | awk '{print $1}')
    echo "Current server IP address: $server_ip"

    default_web_dir="/home/www"

    read -p "Enter the web root directory [Default: $default_web_dir]: " web_dir
    WEB_DIR=${WEB_DIR:-$default_web_dir}
    echo "Web root directory is set to $WEB_DIR"

    read -p "Enter Docker's default directory path [Default: $WEB_DIR/docker]: " docker_dir
    docker_dir=${docker_dir:-"$WEB_DIR/docker"}
    echo "Docker's default directory is set to $docker_dir"

    read -p "Do you want to set up a shared folder? [yes/no, Default: no]: " setup_shared
    setup_shared=${setup_shared:-no}

    if [[ $setup_shared == "yes" ]]; then
        read -p "Enter the path for the shared directory [Default: $WEB_DIR]: " shared_dir
        shared_dir=${shared_dir:-"$WEB_DIR"}
        echo "Shared directory is set to $shared_dir"
    else
        echo "Shared folder setup skipped."
    fi

    echo "MYSQL Root User: root"

    MYSQL_ROOT_PASSWORD=$(generate_random_password)
    echo "Generated MYSQL_ROOT_PASSWORD: $MYSQL_ROOT_PASSWORD"
    read -p "Enter new MYSQL_ROOT_PASSWORD (press enter to keep it): " input_root_password
    MYSQL_ROOT_PASSWORD=${input_root_password:-$MYSQL_ROOT_PASSWORD}
    echo "MYSQL_ROOT_PASSWORD is set to $MYSQL_ROOT_PASSWORD"

    default_mysql_user="mysql"
    read -p "Enter MYSQL_USER [Default: $default_mysql_user]: " MYSQL_USER
    MYSQL_USER=${MYSQL_USER:-$default_mysql_user}
    echo "MYSQL_USER is set to $MYSQL_USER"

    MYSQL_PASSWORD=$(generate_random_password)
    echo "Generated MYSQL_PASSWORD: $MYSQL_PASSWORD"
    read -p "Enter new MYSQL_PASSWORD (press enter to keep it): " input_mysql_password
    MYSQL_PASSWORD=${input_mysql_password:-$MYSQL_PASSWORD}
    echo "MYSQL_PASSWORD is set to $MYSQL_PASSWORD"

    update_or_add_key "MYSQL_ROOT_PASSWORD" "$MYSQL_ROOT_PASSWORD"
    update_or_add_key "MYSQL_USER" "$MYSQL_USER"
    update_or_add_key "MYSQL_PASSWORD" "$MYSQL_PASSWORD"

    update_or_add_key "MAIN_IP" "$server_ip"
    update_or_add_key "IS_SNAP_SERVICE" "$IS_SNAP_SERVICE"
    update_or_add_key "WEB_DIR" "$WEB_DIR"
    update_or_add_key "MAIN_DIR" "$WEB_DIR"

    update_or_add_key "DOCKER_DIR" "$docker_dir"

    default_node_version="18.18.2"
    echo "Available Node.js versions: 18.18.2, 20.9.0"
    read -p "Enter desired Node.js version [Default: $default_node_version]: " node_version
    node_version=${node_version:-$default_node_version}
    echo "Node.js version is set to $node_version"

    sudo cp /etc/fstab /etc/fstab.backup
    echo "/etc/fstab backup created successfully."

    if grep -qs "$WEB_DIR" /etc/fstab; then
        echo "$WEB_DIR is already mounted."
    else
        echo "$WEB_DIR mounting."
        echo "Available disks:"
        lsblk
        largest_disk=$(lsblk -d -o NAME,SIZE --noheadings --raw | sort -hr -k2 | awk 'NR==1{print $1}')
        read -p "Enter the disk to mount on $WEB_DIR (e.g., $largest_disk): " disk
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

        mount_function "$disk_path" "$WEB_DIR" "uuid"
    fi

    [ -f "$tmp_config" ] && sudo rm "$tmp_config"
    echo "web_dir=$WEB_DIR" | sudo tee "$tmp_config"
    echo "docker_dir=$docker_dir" | sudo tee "$tmp_config"
    echo "disk_uuid=$disk_uuid" | sudo tee -a "$tmp_config"
    echo "node_version=$node_version" | sudo tee -a "$tmp_config"
    echo "setup_shared=$setup_shared" | sudo tee -a "$tmp_config"
    echo "shared_dir=$shared_dir" | sudo tee -a "$tmp_config"
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
