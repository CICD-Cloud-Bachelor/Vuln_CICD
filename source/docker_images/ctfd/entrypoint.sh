#!/bin/bash

su - ctfd -c '/usr/sbin/mysqld --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --wait_timeout=28800 --log-warnings=0 &'

sleep 5

mysql -e "CREATE DATABASE IF NOT EXISTS ctfd;"
mysql -e "CREATE USER IF NOT EXISTS 'ctfd'@'localhost' IDENTIFIED BY 'ctfd';"
mysql -e "GRANT ALL PRIVILEGES ON ctfd.* TO 'ctfd'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"


sed -i 's/host="127.0.0.1"/host="0.0.0.0"/' /opt/CTFd/ctfd/serve.py

python3 manage.py import_ctf ctfd_export.zip
python3 /opt/CTFd/ctfd/serve.py --port 8000