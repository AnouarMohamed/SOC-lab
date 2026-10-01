#!/usr/bin/env bash
# ==============================================================================
# Atlas Distribution - SOC DFIR Playbook : Action 5 (Network Containment)
# Purpose: Isolate SRV-WEB-01 from DMZ and lateral subnets without powering off.
# Preserves volatile memory state for subsequent forensic triage.
# ==============================================================================

set -euo pipefail

TARGET_CONTAINER="srv-web-01"
LOG_PREFIX="[INC-ATLAS-001 | CONTAINMENT]"

echo "${LOG_PREFIX} Initiating rapid network isolation on ${TARGET_CONTAINER}..."

# Check if target container exists and is running
if ! docker ps --format '{{.Names}}' | grep -q "^${TARGET_CONTAINER}$"; then
    echo "${LOG_PREFIX} ERROR: Container ${TARGET_CONTAINER} is not running!" >&2
    exit 1
fi

echo "${LOG_PREFIX} Applying iptables containment policy inside ${TARGET_CONTAINER}..."

docker exec --privileged "${TARGET_CONTAINER}" sh -c '
    # Flush existing filter rules
    iptables -F
    iptables -X

    # Set default drop on INPUT, FORWARD, and OUTPUT
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT DROP

    # Allow loopback for internal system IPC
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A OUTPUT -o lo -j ACCEPT

    # Allow established connections from local Docker host for forensics
    iptables -A INPUT -s 172.28.10.1 -j ACCEPT
    iptables -A OUTPUT -d 172.28.10.1 -j ACCEPT

    echo "[IPTABLES] Quarantine rules active. External ports 80/22 unreachable."
'

echo "${LOG_PREFIX} SUCCESS: Host ${TARGET_CONTAINER} is now isolated from network."
echo "${LOG_PREFIX} DO NOT REBOOT: Proceed immediately to volatile memory and log acquisition."
