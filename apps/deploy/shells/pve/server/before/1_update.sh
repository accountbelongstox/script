#!/bin/bash

yes | sudo yum update -y
yes | sudo yum install epel-release
yes | sudo yum update -y
yes | sudo yum install lsof yum-utils device-mapper-persistent-data lvm2 iputils yum-utils cronie device-mapper-persistent-data lvm2 rsync nano wget curl vim alternatives gcc-c++ make -y
sudo git config http.sslVerify"false"



