# Use the crazymax/ftpgrab image from Docker Hub
FROM crazymax/ftpgrab:latest

# Set the timezone
ENV TZ=Europe/Paris

# Set the FTP server details
ENV FTPGRAB_SERVER_FTP_HOST=ftpserverpulumibachelorproject.westeurope.azurecontainer.io
ENV FTPGRAB_SERVER_FTP_PORT=21
ENV FTPGRAB_SERVER_FTP_USERNAME=ftpshared
ENV FTPGRAB_SERVER_FTP_PASSWORD=MAsds8ASDsadm82988
ENV FTPGRAB_SERVER_FTP_SOURCES=/

# Set download settings
ENV FTPGRAB_DOWNLOAD_UID=1000
ENV FTPGRAB_DOWNLOAD_GID=1000
ENV FTPGRAB_DOWNLOAD_INCLUDE=".*zip"
ENV FTPGRAB_DOWNLOAD_RETRY=5
ENV FTPGRAB_DOWNLOAD_EXCLUDE="\\.nfo$$"
ENV FTPGRAB_DOWNLOAD_SINCE=2019-02-01T18:50:05Z

# Set notification settings
ENV FTPGRAB_NOTIF_MAIL_HOST=smtp.example.com
ENV FTPGRAB_NOTIF_MAIL_PORT=25
ENV FTPGRAB_NOTIF_MAIL_FROM=ftpgrab@example.com
ENV FTPGRAB_NOTIF_MAIL_TO=webmaster@example.com

# Set logging level
ENV LOG_LEVEL=info
ENV LOG_JSON=false

# Set scheduling
ENV SCHEDULE="* * * * *"

# Set volume for the database
VOLUME ["/db", "/download"]

# Expose ports (if needed)
# EXPOSE 21

COPY flag.txt /flag.txt

COPY watch_and_run.sh /usr/local/bin/watch_and_run.sh
RUN chmod +x /usr/local/bin/watch_and_run.sh
# Set the entrypoint command
CMD ["/usr/local/bin/watch_and_run.sh"]


# # Use a base image that includes curl and unzip
# FROM ubuntu:latest

# # Install necessary packages
# RUN apt update && \
#     apt install -y --no-install-recommends curl unzip ftp && \
#     rm -rf /var/lib/apt/lists/*

# # Add your script to the container
# COPY watch_and_run.sh /usr/local/bin/watch_and_run.sh

# COPY flag.txt /flag.txt

# # Give execution rights on the script
# RUN chmod +x /usr/local/bin/watch_and_run.sh

# # Create a volume for the FTP download
# RUN mkdir /ftp && chmod 777 /ftp

# # Run the script
# CMD while true; do /usr/local/bin/watch_and_run.sh || sleep 30; done
