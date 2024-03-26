#!/bin/bash

if systemctl list-units --full -all | grep -Fq "exim4.service"; then
    echo "exim4.service exists, stopping the service..."
    sudo systemctl stop exim4.service
else
    echo "exim4.service does not exist, skipping."
fi

if systemctl list-units --full -all | grep -Fq "postfix.service"; then
    echo "postfix.service exists, stopping the service..."
    sudo systemctl stop postfix.service
else
    echo "postfix.service does not exist, skipping."
fi

if systemctl list-units --full -all | grep -Fq "exim4.service"; then
    echo "exim4.service exists, disabling the service..."
    sudo systemctl disable exim4.service
else
    echo "exim4.service does not exist, skipping."
fi

if systemctl list-units --full -all | grep -Fq "postfix.service"; then
    echo "postfix.service exists, disabling the service..."
    sudo systemctl disable postfix.service
else
    echo "postfix.service does not exist, skipping."
fi

if [ -x "$(command -v service)" ]; then
    if [ -f "/etc/init.d/exim4" ]; then
        echo "exim4.service exists, stopping the service..."
        service exim4 stop
    else
        echo "exim4.service does not exist, skipping."
    fi
else
    echo "The 'service' command is not available. Please use alternative methods suitable for your container."
fi

if [ -x "$(command -v service)" ]; then
    if [ -f "/etc/init.d/postfix" ]; then
        echo "postfix.service exists, stopping the service..."
        service postfix stop
    else
        echo "postfix.service does not exist, skipping."
    fi
else
    echo "The 'service' command is not available. Please use alternative methods suitable for your container."
fi
