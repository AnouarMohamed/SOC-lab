FROM php:8.2-apache

# Install required dependencies: PostgreSQL client libraries, OpenSSH server, network & forensic diagnostic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client \
    openssh-server \
    sudo \
    curl \
    iproute2 \
    net-tools \
    iptables \
    procps \
    lsof \
    rsync \
    ca-certificates \
    && docker-php-ext-install pdo pdo_pgsql \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configure SSH server
RUN mkdir -p /var/run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Create service account 'svc-backup' matching the incident scenario
RUN useradd -m -s /bin/bash svc-backup \
    && echo "svc-backup:BackupSecret2026!" | chpasswd \
    && usermod -aG sudo svc-backup

# Generate SSH key pair for svc-backup for automated tasks
RUN mkdir -p /home/svc-backup/.ssh && \
    ssh-keygen -t rsa -b 2048 -f /home/svc-backup/.ssh/id_rsa -N "" && \
    cat /home/svc-backup/.ssh/id_rsa.pub >> /home/svc-backup/.ssh/authorized_keys && \
    chown -R svc-backup:svc-backup /home/svc-backup/.ssh && \
    chmod 700 /home/svc-backup/.ssh && \
    chmod 600 /home/svc-backup/.ssh/authorized_keys

# Setup simulated backup automation script in /opt/scripts/backup.sh
RUN mkdir -p /opt/scripts && \
    cat <<'EOF' > /opt/scripts/backup.sh
#!/bin/bash
# Atlas Automated Nightly Backup Script (Runs at 02:00 UTC)
# Targets: SRV-DB-01 -> NAS-BKP (172.28.0.30)
TARGET_NAS="nas-bkp"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
echo "[INFO] Commencing database snapshot to ${TARGET_NAS}..."
PGPASSWORD=AtlasSecPass2026! pg_dump -h srv-db-01 -U atlas_admin -d atlas_db | gzip > /tmp/atlas_db_${BACKUP_DATE}.sql.gz
echo "[INFO] Transferring archive to backup vault..."
scp -o StrictHostKeyChecking=no /tmp/atlas_db_${BACKUP_DATE}.sql.gz svc-backup@${TARGET_NAS}:/backups/
rm -f /tmp/atlas_db_${BACKUP_DATE}.sql.gz
echo "[SUCCESS] Backup complete."
EOF
RUN chmod +x /opt/scripts/backup.sh && chown svc-backup:svc-backup /opt/scripts/backup.sh

# Copy Apache configuration and web application source code
COPY config/vhost.conf /etc/apache2/sites-available/000-default.conf
COPY src/ /var/www/html/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ensure uploads directory exists and is writable
RUN mkdir -p /var/www/html/uploads && \
    chown -R www-data:www-data /var/www/html/uploads && \
    chmod 777 /var/www/html/uploads

EXPOSE 80 22

ENTRYPOINT ["/entrypoint.sh"]
