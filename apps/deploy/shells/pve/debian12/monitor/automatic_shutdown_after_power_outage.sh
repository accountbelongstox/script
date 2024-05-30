
#
#websites=("www.baidu.com" "192.168.2.1")
#timeout_seconds=60
#log_dir="/home/tmp/"
#log_file="/home/tmp/ip_monitoring.txt"
#current_time=$(date +"%s")
#
#if [ ! -d "$log_dir" ]; then
#    mkdir -p "$log_dir"
#fi
#
#if [ -s "$log_file" ]; then
#    last_response_time=$(tail -n 1 "$log_file" | awk '{print $NF}')
#else
#    last_response_time=$current_time
#fi
#
#echo "last_response_time: $last_response_time"
#
#for website in "${websites[@]}"; do
#    result=$(ping -c 1 "$website" 2>/dev/null)
#    if [ $? -eq 0 ]; then
#        response_time=$(echo "$result" | grep "time=" | awk '{print $7}' | cut -d '=' -f 2)
#        echo "$website: $response_time ms $current_time"
#        echo "$website: $response_time ms $current_time" >> "$log_file"
#        last_response_time=$current_time
#    else
#        echo "$website: No response"
#    fi
#done
#
#time_difference=$((current_time - last_response_time))
#echo "Time difference: $time_difference seconds"
#
#if [ $time_difference -ge $timeout_seconds ]; then
#    echo "No response from websites for $timeout_seconds seconds. Shutting down..."
#    shutdown -h now
#else
#    echo "Websites are responsive."
#fi
