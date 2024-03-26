#!/bin/bash
sudo systemctl stop exim.service
sudo systemctl stop postfix.service

sudo systemctl disable exim.service
sudo systemctl disable postfix.service


