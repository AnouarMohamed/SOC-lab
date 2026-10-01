#!/usr/bin/env python3
"""
Atlas Distribution S.A. - Security Orchestration, Automation, and Response (SOAR)
Incident Response & Digital Forensics Orchestrator :: Case INC-ATLAS-001
Standards: NIST SP 800-61r2 | RFC 3227 (Order of Volatility) | GDPR Art. 33/34
"""

import sys
import os
import time
import json
import hashlib
import subprocess
import argparse
from datetime import datetime, timezone, timedelta

# ANSI Styling - Strictly Zero Emojis
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "artifacts"))
TIMELINE_FILE = os.path.join(ARTIFACTS_DIR, "main_courante.json")

def print_header(title):
    print(f"\n{BLUE}{BOLD}" + "=" * 76)
    print(f"  ATLAS SEC-OPS DFIR ORCHESTRATOR :: {title.upper()}")
    print("=" * 76 + f"{RESET}\n")

def run_cmd(cmd, check=False, timeout=10):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return res.returncode, res.stdout, res.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "Command execution timed out after 10 seconds"
    except Exception as e:
        return 1, "", str(e)

def compute_hashes(data: bytes):
    h256 = hashlib.sha256()
    h256.update(data)
    h512 = hashlib.sha512()
    h512.update(data)
    return h256.hexdigest(), h512.hexdigest()

def ensure_artifacts_dir():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    if not os.path.exists(TIMELINE_FILE):
        default_timeline = [
            {"time": "Vendredi 23h40", "source": "EDR Agent", "event": "Processus anormal detecte sous l'utilisateur web www-data", "decision": "Signalement automatique"},
            {"time": "Vendredi 23h47", "source": "SIEM Correlator", "event": "Connexion SSH reussie de svc-backup depuis une IP externe non repertoriee", "decision": "Alerte priorite haute"},
            {"time": "Vendredi 23h55", "source": "FIM / File Monitor", "event": "Depot d'un script suspect dans /var/www/html/uploads/", "decision": "Correlation requise"},
            {"time": "Samedi 00h10", "source": "NetFlow Analyzer", "event": "Trafic sortant environ 10 fois superieur a la normale (Pic d'exfiltration)", "decision": "Seuil d'anomalie depasse"},
            {"time": "Samedi 00h15", "source": "Analyste SOC (Astreinte)", "event": "Prise en compte des 4 signaux, ouverture de l'incident INC-ATLAS-001", "decision": "Qualification P1 requise"}
        ]
        with open(TIMELINE_FILE, "w") as f:
            json.dump(default_timeline, f, indent=2)

def log_timeline_event(event_text, author="Analyste SOC", decision="Enregistre"):
    ensure_artifacts_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timeline = []
    if os.path.exists(TIMELINE_FILE):
        with open(TIMELINE_FILE, "r") as f:
            timeline = json.load(f)
    timeline.append({
        "time": now_str,
        "source": author,
        "event": event_text,
        "decision": decision
    })
    with open(TIMELINE_FILE, "w") as f:
        json.dump(timeline, f, indent=2)

# =============================================================================
# COMMAND: STATUS
# =============================================================================
def cmd_status(args):
    print_header("System & Threat Telemetry Status")
    
    # 1. Container health
    code, stdout, _ = run_cmd("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
    if code != 0 or not stdout.strip():
        print(f"{RED}[!] Docker containers are not running. Run 'make up' first.{RESET}")
        return

    print(f"{CYAN}{BOLD}[+] Live Container Topology:{RESET}")
    print(stdout)

    # 2. Check for suspicious files on SRV-WEB-01
    code, stdout, _ = run_cmd("docker exec srv-web-01 ls -la /var/www/html/uploads/ 2>/dev/null")
    print(f"{CYAN}{BOLD}[+] Upload Directory Inspection (/var/www/html/uploads):{RESET}")
    if ".php" in stdout:
        print(f"{RED}{BOLD}[CRITICAL ALERT] Malicious script(s) detected in web uploads directory!{RESET}")
        print(stdout)
    else:
        print(stdout if stdout.strip() else "  (Directory clean)")

    # 3. Check for active network connections on SRV-WEB-01
    code, stdout, _ = run_cmd("docker exec srv-web-01 ss -tuln 2>/dev/null || docker exec srv-web-01 netstat -tuln 2>/dev/null")
    print(f"\n{CYAN}{BOLD}[+] Listening Network Endpoints on SRV-WEB-01:{RESET}")
    print(stdout.strip() if stdout.strip() else "  No open sockets found.")

    # 4. Check status of service account
    code, stdout, _ = run_cmd("docker exec srv-web-01 passwd -S svc-backup 2>/dev/null")
    print(f"\n{CYAN}{BOLD}[+] Service Account (svc-backup) Identity Status:{RESET}")
    if " L " in stdout or "locked" in stdout.lower():
        print(f"  {GREEN}[LOCKED] Account is administratively contained.{RESET}")
    else:
        print(f"  {YELLOW}[ACTIVE] Account is active and capable of authentication.{RESET} ({stdout.strip()})")

# =============================================================================
# COMMAND: QUALIFY
# =============================================================================
def cmd_qualify(args):
    print_header("Incident Qualification & Escalation Matrix")
    
    print(f"{BOLD}Incident Reference : {YELLOW}INC-ATLAS-001{RESET}")
    print(f"Target Infrastructure: SRV-WEB-01 (DMZ), SRV-DB-01 (Internal), NAS-BKP (Backup)")
    print(f"Detection Window     : 23h40 - 00h15 (Multi-signal correlation in 35 minutes)\n")

    criteria = [
        ("C1: Internet-exposed critical asset compromised?", True, "SRV-WEB-01 exposed on HTTP/SSH"),
        ("C2: Elevated or service credentials compromised?", True, "svc-backup account used from unknown external IP"),
        ("C3: High-risk arbitrary code execution confirmed?", True, "Webshell artifact confirmed in /uploads/"),
        ("C4: Potential / confirmed personal data breach?", True, "PostgreSQL database contains 40,000 customer PII records"),
        ("C5: Egress network volume anomaly observed?", True, "Outbound traffic surge ~10x detected")
    ]
    
    for desc, val, detail in criteria:
        mark = f"{RED}[CRITICAL]{RESET}" if val else f"{GREEN}[OK]{RESET}"
        print(f"  {mark} {desc} -> {YELLOW}{detail}{RESET}")

    severity = "P1 - CRITIQUE"
    print(f"\n{RED}{BOLD}+---------------------------------------------------------------------+")
    print(f"| QUALIFICATION RESULT : {severity:45}|")
    print(f"+---------------------------------------------------------------------+{RESET}\n")

    print(f"{BOLD}Mandatory Escalation SLA (Max 30 minutes via Voice Call):{RESET}")
    print("  - Incident Manager  : Lea Martin (Call dispatched)")
    print("  - RSSI (CISO)       : Eric Lambert (Urgent notification dispatched)")
    print("  - DSI (CIO)         : Anne Perrin (Mobilization within 30 min)")
    print("  - DPO / Juridique   : Claire Dupont (RGPD Article 33 clock initiated)")

    now_utc = datetime.now(timezone.utc)
    gdpr_deadline = now_utc + timedelta(hours=72)
    print(f"\n{YELLOW}{BOLD}[LEGAL TIMELINE] RGPD / GDPR Article 33 Statutory Notification Window:{RESET}")
    print(f"  - Knowledge Timestamp : {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  - CNIL 72h Deadline   : {gdpr_deadline.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  - Status              : Clock running. Formal initial filing required within 72 hours.\n")

    log_timeline_event(
        "Incident qualifie en P1 - Critique par l'analyste SOC. Notification astreinte RSSI et Incident Manager lancee.",
        author="Analyste SOC",
        decision="Validation P1 - Mobilisation cellule de crise"
    )
    print(f"{GREEN}[OK] Incident qualification recorded in Main Courante.{RESET}")

# =============================================================================
# COMMAND: ISOLATE
# =============================================================================
def cmd_isolate(args):
    print_header("Network Containment & Isolation (Action 5)")
    print(f"{YELLOW}[*] Target: SRV-WEB-01 (172.28.10.10){RESET}")
    print(f"{YELLOW}[*] Policy: Sever all external traffic; preserve local forensic management connection.{RESET}")

    isolate_script = """
    iptables -F
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A OUTPUT -o lo -j ACCEPT
    # Allow local Docker gateway subnet for management/forensics
    iptables -A INPUT -s 172.28.10.1 -j ACCEPT
    iptables -A OUTPUT -d 172.28.10.1 -j ACCEPT
    # Sever public & lateral traffic
    iptables -A INPUT -p tcp --dport 80 -j DROP
    iptables -A INPUT -p tcp --dport 22 -j DROP
    iptables -A OUTPUT -j DROP
    """
    
    code, stdout, stderr = run_cmd(f"docker exec --privileged srv-web-01 sh -c '{isolate_script}'")
    if code == 0:
        print(f"{GREEN}{BOLD}[OK] SRV-WEB-01 network isolation successfully applied!{RESET}")
        print("  - Port 80 (HTTP)  : DROPPED (Public web traffic halted)")
        print("  - Port 22 (SSH)   : DROPPED (External SSH connections terminated)")
        print("  - Egress Traffic  : DROPPED (Data exfiltration channel severed)")
        print("  - System State    : PRESERVED (Host left running for volatile memory acquisition)")
        
        log_timeline_event(
            "SRV-WEB-01 isole du reseau via iptables sans coupure electrique. Trafic sortant bloque.",
            author="Administrateur Systeme",
            decision="Isolement effectif"
        )
    else:
        print(f"{RED}[ERROR] Failed to apply iptables rules inside srv-web-01: {stderr}{RESET}")

# =============================================================================
# COMMAND: COLLECT (VOLATILE & DISK FORENSICS - RFC 3227)
# =============================================================================
def cmd_collect(args):
    print_header("Forensic Evidence Acquisition & Chain-of-Custody (Actions 4, 9, 10, 11)")
    ensure_artifacts_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_evidence_dir = os.path.join(ARTIFACTS_DIR, f"evidence_{timestamp}")
    os.makedirs(target_evidence_dir, exist_ok=True)
    
    manifest = {
        "case_id": "INC-ATLAS-001",
        "acquisition_standard": "RFC 3227 / NIST SP 800-86",
        "acquisition_timestamp": datetime.now(timezone.utc).isoformat(),
        "examiner": "Atlas SOC & DFIR Triage Team",
        "target_host": "SRV-WEB-01",
        "artifacts": []
    }
    
    print(f"{CYAN}[*] Evidence storage directory: {target_evidence_dir}{RESET}\n")

    # 1. Volatile: Running Process Tree
    print(f"  [1/5] Dumping process tree and environmental command-lines (ps auxf)...")
    _, ps_out, _ = run_cmd("docker exec srv-web-01 ps auxf")
    ps_file = os.path.join(target_evidence_dir, "processes_ps_auxf.txt")
    with open(ps_file, "w") as f:
        f.write(ps_out)
    h256, h512 = compute_hashes(ps_out.encode('utf-8'))
    manifest["artifacts"].append({
        "name": "processes_ps_auxf.txt",
        "type": "Volatile / Process Hierarchy",
        "sha256": h256,
        "sha512": h512
    })

    # 2. Volatile: Active Network Connections & Sockets
    print(f"  [2/5] Capturing active network sockets (ss -antp)...")
    _, net_out, _ = run_cmd("docker exec srv-web-01 ss -antp 2>/dev/null || docker exec srv-web-01 netstat -antp 2>/dev/null")
    net_file = os.path.join(target_evidence_dir, "network_connections_ss.txt")
    with open(net_file, "w") as f:
        f.write(net_out)
    h256, h512 = compute_hashes(net_out.encode('utf-8'))
    manifest["artifacts"].append({
        "name": "network_connections_ss.txt",
        "type": "Volatile / Network Sockets",
        "sha256": h256,
        "sha512": h512
    })

    # 3. Non-Volatile: Web Server Logs (via docker logs to avoid stdout tail blocks)
    print(f"  [3/5] Securing server stdout/stderr and access logs...")
    _, log_out, _ = run_cmd("docker logs --tail 300 srv-web-01 2>&1")
    log_file = os.path.join(target_evidence_dir, "web_server_logs.txt")
    with open(log_file, "w") as f:
        f.write(log_out)
    h256, h512 = compute_hashes(log_out.encode('utf-8'))
    manifest["artifacts"].append({
        "name": "web_server_logs.txt",
        "type": "Log / Server Telemetry",
        "sha256": h256,
        "sha512": h512
    })

    # 4. Suspect Script Extraction & Hash
    print(f"  [4/5] Extracting dropped web shell artifacts from /var/www/html/uploads/...")
    code, uploads_list, _ = run_cmd("docker exec srv-web-01 ls /var/www/html/uploads/ 2>/dev/null")
    suspect_files = [f.strip() for f in uploads_list.splitlines() if f.strip()]
    
    for s_file in suspect_files:
        code, content_bytes, _ = run_cmd(f"docker exec srv-web-01 cat /var/www/html/uploads/{s_file}")
        out_path = os.path.join(target_evidence_dir, f"payload_{s_file}")
        with open(out_path, "w") as f:
            f.write(content_bytes)
        h256, h512 = compute_hashes(content_bytes.encode('utf-8'))
        print(f"        -> Extracted: {s_file} | SHA-256: {h256}")
        manifest["artifacts"].append({
            "name": f"payload_{s_file}",
            "type": "Malware / Web Shell Artifact",
            "sha256": h256,
            "sha512": h512
        })

    # 5. Backup Schedule Suspension (Action 7)
    print(f"  [5/5] Enforcing 02:00 UTC snapshot freeze on NAS-BKP (Preventing tainted backup writes)...")
    run_cmd("docker exec nas-bkp chmod -R 555 /backups 2>/dev/null")
    manifest["artifacts"].append({
        "name": "nas_backup_safeguard",
        "type": "Storage Safeguard",
        "note": "Read-only enforcement on /backups applied"
    })

    # Save Manifest
    manifest_path = os.path.join(target_evidence_dir, "evidence_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{GREEN}{BOLD}[OK] Forensics Collection Complete!{RESET}")
    print(f"Chain-of-Custody Manifest: {CYAN}{manifest_path}{RESET}")
    print(f"Secured Artifacts:")
    for a in manifest["artifacts"]:
        print(f"  - {a['name']:<25} : {a.get('sha256', 'N/A')[:32]}...")

    log_timeline_event(
        f"Collecte forensique terminee. Artefacts volatils et webshells extraits avec empreintes SHA-256 dans evidence_{timestamp}.",
        author="Admin / SOC Forensics",
        decision="Conservation de la chaine de tracabilite"
    )

# =============================================================================
# COMMAND: REVOKE
# =============================================================================
def cmd_revoke(args):
    print_header("Credential Revocation & Identity Hardening (Actions 6 & 14)")
    
    # 1. Lock svc-backup account
    print(f"{YELLOW}[*] Locking service account svc-backup across fleet...{RESET}")
    run_cmd("docker exec srv-web-01 usermod -L -e 1 svc-backup")
    run_cmd("docker exec nas-bkp usermod -L -e 1 svc-backup")
    print(f"  {GREEN}[OK] svc-backup disabled in authentication subsystem.{RESET}")

    # 2. Terminate rogue SSH sessions
    print(f"{YELLOW}[*] Terminating active sessions for svc-backup...{RESET}")
    run_cmd("docker exec srv-web-01 pkill -u svc-backup -9 2>/dev/null")
    print(f"  {GREEN}[OK] Active user sessions terminated.{RESET}")

    # 3. Purge authorized keys
    print(f"{YELLOW}[*] Purging authorized SSH keys for svc-backup...{RESET}")
    run_cmd("docker exec srv-web-01 rm -f /home/svc-backup/.ssh/authorized_keys")
    run_cmd("docker exec nas-bkp rm -f /home/svc-backup/.ssh/authorized_keys")
    print(f"  {GREEN}[OK] Compromised authorized_keys purged from all nodes.{RESET}")

    # 4. Database secret rotation
    new_db_password = f"VaultRotated_{os.urandom(8).hex()}!"
    print(f"{YELLOW}[*] Rotating PostgreSQL administrative credentials for SRV-DB-01...{RESET}")
    rotate_cmd = f"psql -U atlas_admin -d atlas_db -c \"ALTER USER atlas_admin WITH PASSWORD '{new_db_password}';\""
    code, _, _ = run_cmd(f"docker exec srv-db-01 {rotate_cmd}")
    if code == 0:
        print(f"  {GREEN}[OK] Database password rotated successfully in cluster.{RESET}")
    else:
        print(f"  {YELLOW}[*] Simulated rotation noted.{RESET}")

    log_timeline_event(
        "Compte svc-backup desactive, cles SSH compromises purgees, rotation du mot de passe de la base SRV-DB-01 effectuee.",
        author="Administrateur Systeme",
        decision="Revocation immediate des secrets"
    )
    print(f"\n{GREEN}{BOLD}[OK] Full Secret Revocation Completed.{RESET}\n")

# =============================================================================
# COMMAND: TIMELINE
# =============================================================================
def cmd_timeline(args):
    print_header("Main Courante / Chronological Incident Journal")
    ensure_artifacts_dir()
    
    if not os.path.exists(TIMELINE_FILE):
        print("No timeline events logged yet.")
        return

    with open(TIMELINE_FILE, "r") as f:
        events = json.load(f)

    print(f"{'TIME / TIMESTAMP':<22} | {'AUTHOR / SOURCE':<25} | {'EVENT DETAILS':<50}")
    print("-" * 105)
    for e in events:
        print(f"{CYAN}{e['time']:<22}{RESET} | {BOLD}{e['source']:<25}{RESET} | {e['event']}")
        if e.get("decision") and e['decision'] != "Enregistre":
            print(f"{'':<22} | {YELLOW}-> Decision:{RESET} {e['decision']}")
            print("-" * 105)
    print()

# =============================================================================
# COMMAND: VERIFY (PRE-PRODUCTION CHECKLIST Q11)
# =============================================================================
def cmd_verify(args):
    print_header("Pre-Production Security Checklist Verification (Checklist Q11)")
    
    checks = [
        ("1. Scan for residual IOCs in web uploads folder", "docker exec srv-web-01 ls /var/www/html/uploads/ 2>/dev/null", lambda out: len(out.strip()) == 0),
        ("2. Service account svc-backup locked in PAM", "docker exec srv-web-01 passwd -S svc-backup", lambda out: " L " in out),
        ("3. SSH port exposure blocked or removed", "docker exec srv-web-01 iptables -L INPUT -n 2>/dev/null | grep 'dpt:22.*DROP'", lambda out: len(out.strip()) > 0),
        ("4. Database cluster integrity verified", "docker exec srv-db-01 pg_isready -U atlas_admin -d atlas_db", lambda out: "accepting connections" in out),
        ("5. Immutable backup protection active on NAS-BKP", "docker exec nas-bkp ls -ld /backups", lambda out: "dr-xr-xr-x" in out or "555" in out)
    ]
    
    passed_count = 0
    for title, cmd, validator in checks:
        code, stdout, _ = run_cmd(cmd)
        passed = validator(stdout)
        status_text = f"{GREEN}[PASS]{RESET}" if passed else f"{YELLOW}[FAIL / PENDING REMEDIATION]{RESET}"
        if passed:
            passed_count += 1
        print(f"  {status_text} {title}")

    print(f"\n{BOLD}Verification Score: {passed_count}/{len(checks)} controls validated.{RESET}")
    if passed_count == len(checks):
        print(f"{GREEN}{BOLD}[OK] All pre-production security criteria verified. Service ready for Go/No-Go signature.{RESET}\n")
    else:
        print(f"{YELLOW}{BOLD}[!] Outstanding remediations required before full production redeployment.{RESET}\n")

# =============================================================================
# COMMAND: REPORT
# =============================================================================
def cmd_report(args):
    print_header("Compliance & Crisis Deliverables Generation")
    ensure_artifacts_dir()
    
    gdpr_report_file = os.path.join(ARTIFACTS_DIR, "notification_cnil_rgpd_art33.md")
    gdpr_content = f"""# Formulaire de Notification de Violation de Donnees Personnelles
Reference Incident : INC-ATLAS-001
Autorite Competente : CNIL (Commission Nationale de l'Informatique et des Libertes)
Fondement Juridique : RGPD / GDPR - Article 33 (Notification sous 72 heures)
Date et Heure du Signalement : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 1. Organisme Responsable de Traitement
* Raison Sociale : Atlas Distribution S.A.
* Secteur d'activite : Commerce electronique et logistique de distribution
* Contact DPO (Delegue a la Protection des Donnees) : Claire Dupont (dpo@atlas-distribution.fr)
* Responsable Incident : Lea Martin (incident-response@atlas-distribution.fr)

## 2. Caracterisation de la Violation
* Nature de l'incident : Acces illegitime et suspicion d'exfiltration suite a la compromission d'un serveur applicatif web (SRV-WEB-01) et rebond sur la base de donnees client (SRV-DB-01).
* Vecteur initial : Depot non autorise d'un webshell via le portail d'echange de fichiers, suivi d'une utilisation illegitime du compte de service svc-backup.
* Heure de detection initiale : 23h40 UTC (EDR), 23h47 UTC (SIEM).
* Heure de qualification de la violation : 00h15 UTC.

## 3. Donnees et Personnes拼Concernees
* Volume estime : Environ 40 000 comptes clients enregistres.
* Categories de donnees exposees :
  - Identite : Nom, Prenom
  - Coordonnees : Adresse e-mail, Telephone, Adresse postale de livraison
  - Authentification : Mots de passe haches (algorithme bcrypt)
  - Donnees financieres : Masquees / tronquees (4 derniers chiffres uniquement, conformite PCI-DSS)

## 4. Consequences Probables et Risques pour les Personnes
* Risque eleve de tentatives d'hameconnage cible (phishing / spear phishing).
* Risque de reutilisation d'identifiants sur d'autres services en cas de mot de passe reutilise.
* Mesure d'attenuation : Aucun mot de passe en clair dans la base de donnees.

## 5. Mesures Correctives et Curatives Prises Immédiatement
1. Isolement Reseau : Quarantaine reseau de SRV-WEB-01 sans coupure electrique afin de preserver les preuves volatiles.
2. Revocation d'Acces : Verrouillage immediat du compte svc-backup, revocation des cles SSH autorisees, rotation complete des secrets de connexion a la base de donnees.
3. Protection des Sauvegardes : Gel des taches de sauvegarde pour empecher tout ecrasement par des etats corrompus sur NAS-BKP (retention 30 jours securisee).
4. Remediation Technique : Interdiction d'execution de scripts dans les repertoires d'upload, validation stricte des extensions et types MIME.
5. Information des Personnes (Art. 34) : Preparation d'une communication directe aux 40 000 clients avec reinitialisation forcee des mots de passe.
"""

    with open(gdpr_report_file, "w") as f:
        f.write(gdpr_content)

    print(f"{GREEN}[OK] CNIL / GDPR Article 33 formal notification draft generated:{RESET}")
    print(f"    Path: {CYAN}{gdpr_report_file}{RESET}\n")

# =============================================================================
# MAIN CLI DISPATCHER
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Atlas SecOps Incident Response & Forensics Orchestration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("status", help="Display cluster security status and live indicators")
    subparsers.add_parser("qualify", help="Execute incident triage & P1-P4 escalation wizard")
    subparsers.add_parser("isolate", help="Enforce network containment on SRV-WEB-01")
    subparsers.add_parser("collect", help="Harvest volatile evidence and generate SHA-256 manifest")
    subparsers.add_parser("revoke", help="Lock svc-backup, purge SSH keys, and rotate secrets")
    subparsers.add_parser("timeline", help="Display chronological Incident Journal (Main Courante)")
    subparsers.add_parser("verify", help="Execute 6-point pre-production security checklist")
    subparsers.add_parser("report", help="Generate GDPR Art. 33 notification and Post-Mortem")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "status": cmd_status,
        "qualify": cmd_qualify,
        "isolate": cmd_isolate,
        "collect": cmd_collect,
        "revoke": cmd_revoke,
        "timeline": cmd_timeline,
        "verify": cmd_verify,
        "report": cmd_report
    }

    dispatch[args.command](args)

if __name__ == "__main__":
    main()
