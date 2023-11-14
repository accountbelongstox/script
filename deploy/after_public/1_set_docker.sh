#!/bin/bash


echo "Checking /etc/docker/daemon.json file."
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
env_file="${PARENT_DIR}/.env"
echo "Using .env: $env_file"
IS_SNAP_SERVICE=$(grep "^IS_SNAP_SERVICE=" "$env_file" | cut -d '=' -f2)
DOCKER_DIR=$(grep "^DOCKER_DIR=" "$env_file" | cut -d '=' -f2)

DOCKER_DIR=${DOCKER_DIR//\\\/\//}

if [[ $DOCKER_DIR != /* ]]; then
    DOCKER_DIR="/$DOCKER_DIR"
fi
echo "DOCKER_DIR is set to: $DOCKER_DIR"

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
    if [ "$IS_SNAP_SERVICE" = "1" ]; then
      fstab_entry="$src_dir $target_dir none  bind  0 0"
    else
      fstab_entry="$src_dir $target_dir ext4 defaults 0 0"
    fi
  else
    echo "Using UUID $disk_uuid for mounting"
    mount_src="UUID=$disk_uuid"
    if [ "$IS_SNAP_SERVICE" = "1" ]; then
      fstab_entry="UUID=$disk_uuid $target_dir none  bind  0 0"
    else
      fstab_entry="UUID=$disk_uuid $target_dir ext4 defaults 0 0"
    fi
  fi

  if mount | grep -q "$target_dir"; then
    echo "Target directory $target_dir is already mounted"
  else
    if [ "$IS_SNAP_SERVICE" = "1" ]; then
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


stop_docker() {
    if [ "$IS_SNAP_SERVICE" = "1" ]; then
        echo "Stopping Docker managed by Snap..."
        sudo snap stop docker
        echo "Docker has been stopped."
    else
        echo "Docker is not managed by Snap. Stopping using standard method..."
        sudo systemctl stop docker
        echo "Docker has been stopped."
    fi
}

start_docker() {
    if [ "$IS_SNAP_SERVICE" = "1" ]; then
        echo "Starting Docker managed by Snap..."
        sudo snap start docker
        echo "Docker has been started."
    else
        echo "Docker is not managed by Snap. Starting using standard method..."
        sudo systemctl start docker
        echo "Docker has been started."
    fi
}

echo "Using Docker directory: $DOCKER_DIR"
docker_root_dir=0
get_docker_root_dir() {
  for i in {1..6}; do
    docker_root_dir=$(sudo docker info 2>/dev/null | grep "Docker Root Dir" | cut -d " " -f $i)
    if [[ $docker_root_dir == /* ]]; then
      echo "Docker Root Dir found: $docker_root_dir"
      return 0
    fi
  done
  echo "Docker Root Dir not found"
  return 1
}

get_docker_root_dir

if [[ $docker_root_dir != 0 ]]; then
  if ! grep -qs "$docker_root_dir" /etc/fstab; then
    stop_docker
    mount_function "$DOCKER_DIR" "$docker_root_dir" "normal"
    start_docker
    echo "Docker configuration(snap) updated."
  else
      echo "Currently, the snap service as $DOCKER_DIR has been mounted to $docker_root_dir"
  fi
else
  echo "Currently, the snap service as $DOCKER_DIR has been mounted to $docker_root_dir"
fi


sudo docker info | grep "Docker Root Dir"
