#!/bin/bash
exit 0
PARENT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
env_file="/home/.server.env"
echo "Using .env: $env_file"
DETECT_POWER_OUTAGE="${PARENT_DIR}/monitor/detect_power_outages.sh"
#DATA_BACKUP="${PARENT_DIR}/monitor/data_backup.sh"
install_cron() {
  if ! which cron &> /dev/null; then
    echo "Installing cron..."
    if command -v apt-get &> /dev/null; then
      sudo apt-get update
      sudo apt-get install -y cron
    elif command -v yum &> /dev/null; then
      sudo yum install -y cronie
    else
      echo "Unsupported package manager. Manual installation of cron is required."
      exit 1
    fi
  else
    echo "cron is already installed."
  fi
}
remove_existing_cron() {
  existing_cron=$(crontab -l 2>/dev/null | grep -F "$DETECT_POWER_OUTAGE")
  if [ -n "$existing_cron" ]; then
    echo "Removing existing cron job..."
    (crontab -l | grep -v -F "$DETECT_POWER_OUTAGE") | crontab -
  fi
  existing_cron=$(crontab -l 2>/dev/null | grep -F "$DATA_BACKUP")
  if [ -n "$existing_cron" ]; then
    echo "Removing existing cron job..."
    (crontab -l | grep -v -F "$DATA_BACKUP") | crontab -
  fi
}
add_cron_job() {
  echo "Adding new cron job... $DETECT_POWER_OUTAGE"
  (crontab -l 2>/dev/null; echo "*/20 * * * * $DETECT_POWER_OUTAGE") | crontab -
}
add_power_job() {
  echo "Adding new cron job... $DETECT_POWER_OUTAGE"
  (crontab -l 2>/dev/null; echo "*/20 * * * * $DETECT_POWER_OUTAGE") | crontab -
}
add_power_job
remove_existing_cron
add_cron_job