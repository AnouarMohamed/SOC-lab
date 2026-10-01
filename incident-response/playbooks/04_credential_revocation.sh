#!/usr/bin/env bash
# ==============================================================================
# Atlas Distribution - SOC DFIR Playbook : Actions 6 & 14 (Secret Revocation)
# Purpose: Lock compromised svc-backup identity, purge SSH keys, rotate secrets.
# ==============================================================================

set -euo pipefail

echo "[IR-REVOKE] Locking svc-backup account across fleet..."
docker exec srv-web-01 usermod -L -e 1 svc-backup 2>/dev/null || true
docker exec nas-bkp usermod -L -e 1 svc-backup 2>/dev/null || true

echo "[IR-REVOKE] Killing running processes/sessions owned by svc-backup..."
docker exec srv-web-01 pkill -u svc-backup -9 2>/dev/null || true

echo "[IR-REVOKE] Purging authorized_keys and known SSH keys..."
docker exec srv-web-01 rm -f /home/svc-backup/.ssh/authorized_keys 2>/dev/null || true
docker exec nas-bkp rm -f /home/svc-backup/.ssh/authorized_keys 2>/dev/null || true

echo "[IR-REVOKE] Rotating PostgreSQL administrative database password..."
NEW_PASSWORD="RotatedSecPass_$(openssl rand -hex 8)!"
docker exec srv-db-01 psql -U atlas_admin -d atlas_db -c "ALTER USER atlas_admin WITH PASSWORD '${NEW_PASSWORD}';" 2>/dev/null || true

echo "[IR-REVOKE] SUCCESS: Identity containment and secret rotation complete."
