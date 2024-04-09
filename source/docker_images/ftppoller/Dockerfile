# Use a base image that includes curl and unzip
FROM ubuntu:latest

# Install necessary packages
RUN apt update && \
    apt install -y --no-install-recommends curl unzip && \
    rm -rf /var/lib/apt/lists/*

# Add your script to the container
COPY watch_and_run.sh /usr/local/bin/watch_and_run.sh

COPY flag.txt /flag.txt

# Give execution rights on the script
RUN chmod +x /usr/local/bin/watch_and_run.sh

# Create a volume for the FTP download
RUN mkdir /ftp && chmod 777 /ftp

# Run the script
CMD while true; do /usr/local/bin/watch_and_run.sh || sleep 30; done
