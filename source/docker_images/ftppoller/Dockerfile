# Use the crazymax/ftpgrab image from Docker Hub
FROM crazymax/ftpgrab:latest

# adds glibc compatibility layer to alpine
RUN apk add gcompat build-base icu-libs

# Set the timezone
ENV TZ=Europe/Paris

# Set the FTP server details
ENV FTPGRAB_SERVER_FTP_HOST=ftpserverpulumibachelorproject87.westeurope.azurecontainer.io
ENV FTPGRAB_SERVER_FTP_PORT=21
ENV FTPGRAB_SERVER_FTP_USERNAME=ftpshared
ENV FTPGRAB_SERVER_FTP_PASSWORD=MAsds8ASDsadm82988
ENV FTPGRAB_SERVER_FTP_SOURCES=/

# Set download settings
ENV FTPGRAB_DOWNLOAD_UID=1000
ENV FTPGRAB_DOWNLOAD_GID=1000
ENV FTPGRAB_DOWNLOAD_INCLUDE=".*zip"
ENV FTPGRAB_DOWNLOAD_RETRY=5

# Set logging level
ENV LOG_LEVEL=info
ENV LOG_JSON=false

# Set scheduling
ENV SCHEDULE="* * * * *"

# Set volume for the database
VOLUME ["/db", "/download"]

COPY flag.txt /flag.txt

COPY watch_and_run.sh /usr/local/bin/watch_and_run.sh
COPY ftpgrab_run.sh /usr/local/bin/ftpgrab_run.sh
RUN chmod +x /usr/local/bin/watch_and_run.sh
RUN chmod +x /usr/local/bin/ftpgrab_run.sh

ENTRYPOINT ["/usr/local/bin/watch_and_run.sh"]
