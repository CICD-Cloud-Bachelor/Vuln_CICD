#!/bin/sh

# FTP server URL including the path to s.zip
REMOTE_FTP="ftp://ftpshared:MAsds8ASDsadm82988@ftp-containerpulumibachelorproject.westus2.azurecontainer.io/home/ftpshared/ftp/s.zip"
LOCAL_ZIP="/ftp/s.zip"
PREV_HASH=""

while true; do
  # Download s.zip file
  curl -s --ftp-pasv -o $LOCAL_ZIP $REMOTE_FTP
  # Calculate hash of the downloaded file to see if it has changed
  NEW_HASH=$(md5sum $LOCAL_ZIP | cut -d ' ' -f 1)
  
  if [ "$PREV_HASH" != "$NEW_HASH" ]; then
    # Unzip the downloaded file
    unzip -o $LOCAL_ZIP -d /ftp/
    
    # Assuming the ELF executable is named 'program' and located at the root of the zip
    # Make the ELF executable
    chmod +x /ftp/VULN5
    
    # Run the ELF executable
    /ftp/VULN5
    
    # Update the previous hash to reflect the new state
    PREV_HASH=$NEW_HASH
  fi

  rm -rf /ftp/*
  
  # Wait for a bit before checking again
  sleep 2
done
