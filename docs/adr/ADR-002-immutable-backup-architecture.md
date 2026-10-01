# Architecture Decision Record (ADR 002)
## Title: Immutable Storage and Privilege Separation for Backup Vault (NAS-BKP)
Status: Accepted  
Date: 2026-10-01  
Deciders: Atlas Storage & Disaster Recovery Committee  

---

## 1. Context and Problem Statement
In incident INC-ATLAS-001, the automated service account `svc-backup` was granted full read/write privileges on the backup storage target `NAS-BKP`. Consequently, an attacker holding `svc-backup` credentials could overwrite, encrypt, or delete historical backup snapshots, imperiling the 24-hour RPO guarantee.

## 2. Decision
1. Implement a Write-Once-Read-Many (WORM) immutable snapshot architecture for all nightly PostgreSQL database dumps.
2. Separate ingestion privileges: The backup client account may write new snapshot objects, but possesses zero delete or overwrite privileges on existing objects.
3. Enforce an automated forensic freeze policy: Upon detection of a P1 compromise, the storage vault transitions to read-only (`chmod -R 555 /backups`) pending incident containment.

## 3. Consequences
- **Positive:** Protection against ransomware destruction of recovery archives. Guarantees availability of uncorrupted snapshots for RTO restoration.
- **Negative:** Storage capacity requirements increase due to non-overwritable version retention for a mandatory 30-day window.
