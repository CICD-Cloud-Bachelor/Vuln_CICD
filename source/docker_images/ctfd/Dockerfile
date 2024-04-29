FROM ubuntu:22.04

ENV DATABASE_URL=mysql+pymysql://ctfd:ctfd@localhost/ctfd
ENV LOG_FOLDER=/var/log/CTFd
ENV ACCESS_LOG=-
ENV ERROR_LOG=-

RUN apt update && \
    apt install -y mariadb-server python3 python3-pip unzip

WORKDIR /opt/CTFd
COPY ctfd_master.zip .
RUN unzip ctfd_master.zip && \
    mv CTFd-master ctfd && \
    rm ctfd_master.zip

WORKDIR /opt/CTFd/ctfd
COPY ctfd_export.zip .
COPY entrypoint.sh /entrypoint.sh
RUN python3 -m pip install -r requirements.txt && \
    chmod +x /entrypoint.sh && \
    chmod +x docker-entrypoint.sh && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    mkdir -p /run/mysqld/

EXPOSE 8000

CMD ["sh", "-c", "/entrypoint.sh"]        