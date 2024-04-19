#!/bin/sh

while true; do
    ftpgrab
    echo "ftpgrab crashed. Restarting in 1 second..."
    sleep 1
done
