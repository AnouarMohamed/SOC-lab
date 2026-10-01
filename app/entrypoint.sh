#!/bin/bash
set -e

# Generate host keys if not present
ssh-keygen -A

# Ensure sshd directory exists
mkdir -p /run/sshd

# Start SSH daemon in background
/usr/sbin/sshd

# Ensure correct permissions for upload folder
chown -R www-data:www-data /var/www/html/uploads
chmod 777 /var/www/html/uploads

echo "[SRV-WEB-01] Services initialized. Starting Apache..."

# Execute Apache in foreground
exec apache2-foreground
