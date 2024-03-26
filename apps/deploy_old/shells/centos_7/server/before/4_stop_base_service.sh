#!/bin/bash
if systemctl list-units --full -all | grep -Fq "exim.service"; then
    echo "exim.service exists, stopping the service..."
    sudo systemctl stop exim.service
else
    echo "exim.service does not exist, skipping."
fi

if systemctl list-units --full -all | grep -Fq "postfix.service"; then
    echo "postfix.service exists, stopping the service..."
    sudo systemctl stop postfix.service
else
    echo "postfix.service does not exist, skipping."
fi

if systemctl list-units --full -all | grep -Fq "exim.service"; then
    echo "exim.service exists, disabling the service..."
    sudo systemctl disable exim.service
else
    echo "exim.service does not exist, skipping."
fi
if systemctl list-units --full -all | grep -Fq "postfix.service"; then
    echo "postfix.service exists, disabling the service..."
    sudo systemctl disable postfix.service
else
    echo "postfix.service does not exist, skipping."
fi




