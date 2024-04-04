# Use the official MySQL image as the base
FROM mysql:latest

# Set environment variables for MySQL
ENV MYSQL_DATABASE=prod
ENV MYSQL_ROOT_PASSWORD=myr00tp455w0rd

# Add your database schema SQL file
# Assuming `db.mysql` is in the same directory as this Dockerfile
ADD db.sql /docker-entrypoint-initdb.d

# When the container starts, MySQL will execute files with extensions .sh, .sql and .sql.gz found in /docker-entrypoint-initdb.d
# The files will be executed in alphabetical order.
