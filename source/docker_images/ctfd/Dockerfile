FROM ubuntu:22.04

# Install necessary packages for both CTFd and MariaDB
RUN apt update && apt install -y mariadb-server wget python3 python3-pip unzip

# Setup directories for volumes
RUN mkdir -p /var/log/CTFd /var/uploads
VOLUME ["/var/log/CTFd", "/var/uploads"]

RUN useradd -m ctfd && \
    mkdir -p /run/mysqld/ /home/ctfd/.data && \
    chmod -R 755 /home/ctfd && \
    chown -R ctfd:ctfd /opt/ && \
    chown -R ctfd:ctfd /var/lib/mysql && \
    chown -R ctfd:ctfd /etc/mysql && \
    chown -R ctfd:ctfd /run/mysqld && \
    chown -R ctfd:ctfd /home/ctfd/ && \
    chmod -R 755 /usr/sbin/mysqld

WORKDIR /opt/CTFd

COPY ctfd_master.zip .
RUN unzip ctfd_master.zip && mv CTFd-master ctfd && rm ctfd_master.zip
WORKDIR /opt/CTFd/ctfd
RUN python3 -m pip install -r requirements.txt
COPY ctfd_export.zip .

# Set environment variables
ENV UPLOAD_FOLDER=/var/uploads
ENV DATABASE_URL=mysql+pymysql://ctfd:ctfd@localhost/ctfd
ENV LOG_FOLDER=/var/log/CTFd
ENV ACCESS_LOG=-
ENV ERROR_LOG=-

COPY entrypoint.sh /home/ctfd/entrypoint.sh
RUN chmod +x /home/ctfd/entrypoint.sh

EXPOSE 8000

CMD ["sh", "-c", "/home/ctfd/entrypoint.sh"]
        