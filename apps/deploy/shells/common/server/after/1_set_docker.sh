#!/bin/bash
stop_docker() {
    if [ "$SNAP_DOCKER" = "1" ]; then
        sudo snap stop docker
    else
        sudo systemctl stop docker
    fi
    echo "Stoped Docker"
}
start_docker() {
    if [ "$SNAP_DOCKER" = "1" ]; then
        sudo snap start docker
    else
        sudo systemctl start docker
    fi
    echo "Started Docker"
}

mount_function() {
  src_dir=$1
  target_dir=$2
  use_uuid=$3
  if [ ! -d "$target_dir" ]; then
    echo "Target directory $target_dir does not exist, creating it..."
    sudo mkdir -p "$target_dir"
  fi
  disk_uuid=""
  if [ "$use_uuid" = "uuid" ]; then
    disk_uuid=$(sudo lsblk -no UUID "$src_dir" 2>/dev/null)
  fi
  if [ -z "$disk_uuid" ]; then
    echo "UUID not found or not required, using path for mounting"
    mount_src="$src_dir"
    if [ "$SNAP_DOCKER" = "1" ]; then
      fstab_entry="$src_dir $target_dir none  bind  0 0"
    fi
  else
    echo "Using UUID $disk_uuid for mounting"
    mount_src="UUID=$disk_uuid"
    if [ "$SNAP_DOCKER" = "1" ]; then
      fstab_entry="UUID=$disk_uuid $target_dir none  bind  0 0"
    fi
  fi
  if mount | grep -q "$target_dir"; then
    echo "Target directory $target_dir is already mounted"
  else
    if [ "$SNAP_DOCKER" = "1" ]; then
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

get_old_docker_root_dir() {
  for i in {1..6}; do
    old_docker_root_dir=$(sudo docker info 2>/dev/null | grep "Docker Root Dir" | cut -d " " -f $i)
    if [[ $old_docker_root_dir == /* ]]; then
      echo "Docker Root Dir found: $old_docker_root_dir"
      return 0
    fi
  done
  echo "Docker Root Dir not found"
  return 1
}

# -----------------------------------------------------------------------
echo "Checking sudo  file."
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
echo "BasiDir ${PARENT_DIR}"
pyscript="$PARENT_DIR/pyscript/main.py"
DOCKER_DIR=$(sudo python3 "$pyscript" env get_val "DOCKER_DIR")
SNAP_DOCKER=$(sudo python3 "$pyscript" env get_val "SNAP_DOCKER")
# -----------------------------------------------------------------------
if [ -z "$DOCKER_DIR" ]; then
    echo "DOCKER_DIR is empty. Aborting script."
    exit 1
fi
if [[ $DOCKER_DIR != /* ]]; then
    DOCKER_DIR="/$DOCKER_DIR"
fi
DOCKER_CONFIG_FILE=""
DOCKER_SET_CONFIG="0"
echo "DOCKER_DIR is set to: $DOCKER_DIR"
sudo mkdir -p "$DOCKER_DIR"
echo "Using Docker directory: $DOCKER_DIR"
# -----------------------------------------------------------------------
DOCKER_SOCK=""
if [ -e /run/docker.sock ]; then
    DOCKER_SOCK="/run/docker.sock"
    echo "Found docker.sock at /run/docker.sock"
elif [ -e /var/run/docker.sock ]; then
    DOCKER_SOCK="/var/run/docker.sock"
    echo "Found docker.sock at /var/run/docker.sock"
else
    DOCKER_SOCK=""
    echo "docker.sock not found."
fi
echo "DOCKER_SOCK is set to: $DOCKER_SOCK"
sudo python3 "$pyscript" env set_val DOCKER_SOCK "$DOCKER_SOCK"
# -----------------------------------------------------------------------
old_docker_root_dir=""
get_old_docker_root_dir
# -----------------------------------------------------------------------
if [ "$SNAP_DOCKER" = "1" ]; then
    DOCKER_CONFIG_FILE="/var/snap/docker/current/etc/docker/daemon.json"
else
    DOCKER_CONFIG_FILE="/etc/docker/daemon.json"
fi
# -----------------------------------------------------------------------
if [ "$SNAP_DOCKER" = "1" ]; then
    if ! grep -qs "$old_docker_root_dir" /etc/fstab; then
        stop_docker
        mount_function "$DOCKER_DIR" "$old_docker_root_dir" "normal"
        sudo python3 "$pyscript" docker update_docker_config "$DOCKER_CONFIG_FILE" False
        start_docker
        echo "Docker configuration (snap) updated."
    else
        docker_root_dir=$(docker info --format '{{.DockerRootDir}}')
        echo "Docker root directory: $docker_root_dir"
    fi
else
    if [ -e "$DOCKER_CONFIG_FILE" ]; then
        if grep -q '"data-root"' "$DOCKER_CONFIG_FILE"; then
            echo "DOCKER_CONFIG_FILE exists, and \"data-root\" is present."
        else
            echo "DOCKER_CONFIG_FILE exists, but \"data-root\" is not present."
            DOCKER_SET_CONFIG="1"
        fi
    else
        echo "DOCKER_CONFIG_FILE does not exist."
        DOCKER_SET_CONFIG="1"
    fi
    echo "SET DOCKER CONFIG: $DOCKER_SET_CONFIG"
    if [ "$DOCKER_SET_CONFIG" = "1" ]; then
        stop_docker
        sudo python3 "$pyscript" docker update_docker_config "$DOCKER_CONFIG_FILE" True
        sudo python3 "$pyscript" docker migrate_docker_data_rsync
        start_docker
    fi
    echo "Configuration has been written to $DOCKER_CONFIG_FILE"
fi
sudo docker info | grep "Docker Root Dir"
