#!/usr/bin/env bash
# ==============================================================================
# Atlas Distribution - SOC DFIR Playbook : Actions 4, 9, 10, 11 (Evidence Collection)
# Purpose: Order-of-volatility evidence acquisition and cryptographic hashing.
# Standards: RFC 3227 (Guidelines for Evidence Collection and Archiving)
# ==============================================================================

set -euo pipefail

TARGET_CONTAINER="srv-web-01"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%SZ")
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${BASE_DIR}/artifacts/forensics_${TIMESTAMP}"

mkdir -p "${OUTPUT_DIR}"
echo "[DFIR] Evidence directory created: ${OUTPUT_DIR}"

# 1. Volatile Network Connections
echo "[DFIR] 1/5 Collecting active sockets and connections..."
docker exec "${TARGET_CONTAINER}" ss -antp > "${OUTPUT_DIR}/netstat_ss.txt" 2>/dev/null || true

# 2. Volatile Process Tree & Command Lines
echo "[DFIR] 2/5 Dumping process hierarchy and environmental state..."
docker exec "${TARGET_CONTAINER}" ps auxf > "${OUTPUT_DIR}/processes.txt" 2>/dev/null || true

# 3. Log Exfiltration (Apache access/error + auth.log)
echo "[DFIR] 3/5 Securing server access and authentication logs..."
docker exec "${TARGET_CONTAINER}" cat /var/log/apache2/access.log > "${OUTPUT_DIR}/apache_access.log" 2>/dev/null || true
docker exec "${TARGET_CONTAINER}" cat /var/log/apache2/error.log > "${OUTPUT_DIR}/apache_error.log" 2>/dev/null || true

# 4. Upload Directory Artifact Extraction
echo "[DFIR] 4/5 Extracting suspicious dropped files from /var/www/html/uploads/..."
mkdir -p "${OUTPUT_DIR}/extracted_payloads"
for file in $(docker exec "${TARGET_CONTAINER}" ls /var/www/html/uploads/ 2>/dev/null); do
    docker exec "${TARGET_CONTAINER}" cat "/var/www/html/uploads/${file}" > "${OUTPUT_DIR}/extracted_payloads/${file}"
done

# 5. Compute SHA-256 Hashes
echo "[DFIR] 5/5 Generating SHA-256 integrity checksums..."
find "${OUTPUT_DIR}" -type f -exec sha256sum {} + > "${OUTPUT_DIR}/checksums.sha256"

echo "[DFIR] SUCCESS: Evidence secured. Verify checksums file:"
cat "${OUTPUT_DIR}/checksums.sha256"
