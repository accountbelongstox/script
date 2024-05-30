

# Convert 1GB to KB for comparison
GB_IN_KB=1048576

# Get total memory in KB
total_mem_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')

# Check if /swapfile is already in /etc/fstab
if grep -qs 'swap' /etc/fstab; then
    echo "swap is already mounted."
else
    # Check if total memory is less than 4GB
    if [ "$total_mem_kb" -lt "$GB_IN_KB" ]; then
        echo "Memory is less than 4GB. Creating swap file..."

        # Create and set up swap file
        sudo dd if=/dev/zero of=/swapfile bs=1M count=1024
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile

        # Add swap file entry to /etc/fstab
        echo '/swapfile swap  swap  sw  0 0' | sudo tee -a /etc/fstab

        # Activate all swap files
        sudo swapon -a

        echo "Swap file created and activated."
    else
        echo "Memory is 4GB or more. No swap file needed."
    fi
fi
