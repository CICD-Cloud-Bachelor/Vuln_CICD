#!/bin/sh

# Fetch the external IP address
EXTERNAL_IP=$(curl checkip.amazonaws.com)

# Update vsftpd.conf with the external IP address
{ echo "pasv_address=${EXTERNAL_IP}"; cat /etc/vsftpd.conf; } > /etc/vsftpd.conf.tmp
mv /etc/vsftpd.conf.tmp /etc/vsftpd.conf

# Start vsftpd
vsftpd /etc/vsftpd.conf
