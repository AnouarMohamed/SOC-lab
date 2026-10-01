# Threat Model & Risk Analysis (STRIDE Framework)
Document ID: SEC-THREAT-ATLAS-001  
Target System: Atlas Distribution S.A. Digital Retail & Logistics Platform  
Evaluator: Enterprise Information Security Office (EISO)  
Standard: Microsoft STRIDE Methodology | NIST SP 800-154  

---

## 1. Executive Summary & Scope

This document details the threat modeling assessment performed for the Atlas Distribution enterprise ecosystem, consisting of:
- Public Tier: SRV-WEB-01 (Apache 2.4, PHP 8.2, Multipart B2B Ingestion Endpoint).
- Internal Data Tier: SRV-DB-01 (PostgreSQL 16 Multi-Schema Cluster, 40,000 GDPR Regulated Customer Records).
- Backup Storage Tier: NAS-BKP (SSH/SFTP Storage Vault, Automated Nightly Snapshots).

---

## 2. STRIDE Threat Categorization & Attack Vectors

| STRIDE Category | Threat Description | Attack Vector / Realized Flaw | Inherent Risk | Mitigating Security Control | Residual Risk |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Spoofing** | Attacker impersonates the automated backup identity (`svc-backup`). | Plaintext private keys or reused passwords extracted from web host configuration files. | **CRITICAL** | Elimination of SSH passwords; migration to ephemeral HashiCorp Vault SSH certificates and IP-bound bastion. | LOW |
| **Tampering** | Attacker drops and modifies executable scripts inside upload spools. | `POST /upload.php` lacks MIME-type verification, extension whitelisting, and execution prohibition flags. | **CRITICAL** | Apache `php_admin_flag engine off`, strict MIME validation, storage separation on dedicated object storage. | LOW |
| **Repudiation** | Attacker executes unauthorized commands under `www-data` without non-repudiation. | Web server lacks centralized remote syslog shipping and kernel-level auditd process tracing. | **HIGH** | Kernel-level `auditd` rules logging `execve` syscalls and eBPF Falco telemetry streaming to immutable SIEM. | LOW |
| **Information Disclosure** | Bulk exfiltration of 40,000 customer PII records and bcrypt password hashes. | Web application possesses unrestricted direct SQL query rights across all schemas on SRV-DB-01. | **CRITICAL** | Implementation of PostgreSQL Row-Level Security (RLS), column masking, and least-privilege service roles. | MEDIUM |
| **Denial of Service** | Outbound network saturation (~10x normal volume) exhausting egress transit bandwidth. | Unthrottled streaming of customer database dump over unencrypted HTTP socket. | **HIGH** | Egress traffic shaping, rate limiting, and SIEM NetFlow anomaly alerts triggering automatic socket teardown. | LOW |
| **Elevation of Privilege** | Attacker elevates from unprivileged web daemon (`www-data`) to full root / database supervisor. | Sudo misconfigurations or direct access to database administrator credentials in `db.php`. | **CRITICAL** | Container hardening: `cap_drop: ALL`, `no-new-privileges:true`, unprivileged UID 10001 execution. | LOW |

---

## 3. DREAD Quantitative Risk Scoring

Risk Priority = (Damage + Reproducibility + Exploitability + Affected Users + Discoverability) / 5

| Threat Scenario | Damage (1-10) | Reproducibility (1-10) | Exploitability (1-10) | Affected Users (1-10) | Discoverability (1-10) | DREAD Score | Priority |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Unauthenticated Webshell Upload (`upload.php`) | 10 | 10 | 9 | 10 | 9 | **9.6 / 10** | **P1 - Immediate** |
| Hardcoded Credentials in Web Root (`db.php`) | 9 | 10 | 9 | 10 | 8 | **9.2 / 10** | **P1 - Immediate** |
| Service Account Remote SSH Exposure (:2222) | 9 | 8 | 8 | 10 | 9 | **8.8 / 10** | **P1 - Immediate** |
| Unmonitored Bulk Egress Exfiltration | 9 | 9 | 8 | 10 | 7 | **8.6 / 10** | **P1 - Immediate** |

---

## 4. Attack Tree: Database Exfiltration via Web Portal

```
[Exfiltrate 40,000 Customer PII Records] (GOAL)
  ├── 1. Initial Perimeter Penetration
  │     ├── 1.1 Exploit unauthenticated upload on /upload.php (CHOSEN PATH)
  │     └── 1.2 Exploit known Apache / PHP RCE CVE
  ├── 2. Establish Persistence & Execution
  │     ├── 2.1 Drop PHP webshell in /uploads/ (CHOSEN PATH)
  │     └── 2.2 Inject cron job or systemd unit
  ├── 3. Credential Harvesting & Reconnaissance
  │     ├── 3.1 Extract DB credentials from /var/www/html/db.php (CHOSEN PATH)
  │     └── 3.2 Extract svc-backup credentials from /opt/scripts/backup.sh (CHOSEN PATH)
  └── 4. Bulk Extraction & Data Transfer
        ├── 4.1 Query PostgreSQL database through local socket (CHOSEN PATH)
        └── 4.2 Stream data across egress interface generating 10x traffic spike (CHOSEN PATH)
```
