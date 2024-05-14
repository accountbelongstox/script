

services=("exim.service" "postfix.service")

for service in "${services[@]}"; do
    if systemctl list-units --full -all | grep -Fq "$service"; then
        echo "$service exists, stopping the service..."
        sudo systemctl stop "$service"
    else
        echo "$service does not exist, skipping."
    fi

    if systemctl list-units --full -all | grep -Fq "$service"; then
        echo "$service exists, disabling the service..."
        sudo systemctl disable "$service"
    else
        echo "$service does not exist, skipping."
    fi
done
