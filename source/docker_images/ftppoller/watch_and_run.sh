#!/bin/sh

sleep 90 # wait for other container

/usr/local/bin/ftpgrab_run.sh &

cd /download
while true
do
  # if s.zip does not exist continue
  if [ ! -f s.zip ]; then
    sleep 10
    continue
  fi

  unzip -o *.zip


  # loop through all files and find ELF files
  for f in *; do
    run_xxd=$(xxd -l 4 -p $f)
    if [ "$run_xxd" = "7f454c46" ]; then
      filename=$f
      break
    fi
  done

  chmod +x $filename

  echo "Executing " $filename

  timeout 60 ./$filename


  > /db/ftpgrab.db # clear the ftpgrab db

  sleep 10
done