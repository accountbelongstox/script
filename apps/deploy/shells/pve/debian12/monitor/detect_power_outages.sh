
#MAIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
#env_file="/home/.server.env"
#
#if [ ! -f "$env_file" ]; then
#    echo "Error: $env_file not found. Please make sure the .env file exists."
#    exit 1
#fi
#
#IPs=()
#for i in {1..x}; do
#    key="HeartbeatIP$i"
#    value=$(grep "^$key=" "$env_file" | cut -d '=' -f2)
#    IPs+=("$value")
#done
#
#all_unreachable=true
#for ip in "${IPs[@]}"; do
#    if ! ping -c 1 "$ip" > /dev/null; then
#        all_unreachable=false
#        break
#    fi
#done
#
#if [ "$all_unreachable" = true ]; then
#    log_dir="/home/log/"
#    log_file="$log_dir/$(date +'%Y%m%d%H%M%S')_shutdown_log.txt"
#    sudo mkdir -p "$log_dir"
#    sudo touch "$log_file"
#    sudo echo "Shutdown time: $(date)" | sudo tee -a "$log_file"
#    sudo echo "Reason: Power outage" | sudo tee -a "$log_file"
#    sudo shutdown -h now
#else
#    echo "All IPs are reachable. System is normal."
#fi
