#!/bin/bash

mysqld --user=root --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --wait_timeout=28800 --log-warnings=0 &

sleep 5

mysql -e "CREATE DATABASE IF NOT EXISTS ctfd;"
mysql -e "CREATE USER IF NOT EXISTS 'ctfd'@'localhost' IDENTIFIED BY 'ctfd';"
mysql -e "GRANT ALL PRIVILEGES ON ctfd.* TO 'ctfd'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

python3 manage.py import_ctf ctfd_export.zip
./docker-entrypoint.sh