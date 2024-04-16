# Use an official PHP image with Apache
FROM php:7.4-apache

# Copy the virtual host file into the container
COPY ./000-default.conf /etc/apache2/sites-available/000-default.conf

# Enable .htaccess with RewriteEngine
RUN a2enmod rewrite

# Install additional packages
RUN apt-get update && apt-get install -y \
    libzip-dev \
    zip \
  && docker-php-ext-install zip

# Increase the upload file size
RUN echo 'upload_max_filesize = 10M' >> /usr/local/etc/php/conf.d/uploads.ini

# Copy the application source code to /var/www/html
COPY . /var/www/html

# Expose port 8080 to access the container
EXPOSE 80

# Start Apache server in the foreground
CMD ["apache2-foreground"]

