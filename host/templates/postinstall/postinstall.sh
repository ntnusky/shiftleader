#!/bin/bash

logfile='/root/postinstall.log'

echo "Post install started on $(date)" > $logfile

apt-get update
apt-get -y upgrade

echo "Post install completed on $(date)" >> $logfile 

exit 0
