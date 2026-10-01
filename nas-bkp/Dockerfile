FROM alpine:3.20

RUN apk add --no-cache openssh bash rsync shadow coreutils

# Setup SSH server
RUN mkdir -p /var/run/sshd && \
    ssh-keygen -A && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Create backup user and storage mount
RUN useradd -m -s /bin/bash svc-backup && \
    echo "svc-backup:BackupSecret2026!" | chpasswd && \
    mkdir -p /backups /home/svc-backup/.ssh && \
    chown -R svc-backup:svc-backup /backups /home/svc-backup

# Pre-populate simulated historical backups
RUN echo "Atlas Historical Snapshot 2026-09-29 02:00:00" > /backups/atlas_db_20260929_020000.sql.gz && \
    echo "Atlas Historical Snapshot 2026-09-30 02:00:00" > /backups/atlas_db_20260930_020000.sql.gz && \
    chown -R svc-backup:svc-backup /backups

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D", "-e"]
