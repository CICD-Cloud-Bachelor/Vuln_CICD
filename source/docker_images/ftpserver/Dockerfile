# Use a base image with a Linux distribution, e.g., Ubuntu
FROM ubuntu:latest

# Install vsftpd
RUN apt-get update && apt-get install -y vsftpd curl

# Create the secure_chroot_dir
RUN mkdir -p /var/run/vsftpd/empty && \
    chown root:root /var/run/vsftpd/empty && \
    chmod 755 /var/run/vsftpd/empty

# Avoid issues with special characters in the password
RUN echo "ftpshared:MAsds8ASDsadm82988" > /password.txt

# Create FTP user, set the password, create FTP directory, and make it non-writable
RUN adduser --disabled-password --gecos "" ftpshared && \
    chpasswd < /password.txt && \
    rm /password.txt && \
    mkdir -p /home/ftpshared/ftp && \
    chown ftpshared:ftpshared /home/ftpshared/ftp && \
    chmod 755 /home/ftpshared/ftp

# Configure vsftpd
COPY vsftpd.conf /etc/vsftpd.conf

# Expose the FTP command port and the single data port
EXPOSE 21 10000

# Add the script to the image
COPY configure_vsftpd.sh /usr/local/bin/configure_vsftpd.sh

# Make the script executable
RUN chmod +x /usr/local/bin/configure_vsftpd.sh

# Run the script when the container starts
CMD ["/usr/local/bin/configure_vsftpd.sh"]
