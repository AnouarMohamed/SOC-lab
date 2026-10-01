# Architecture Decision Record (ADR 001)
## Title: Implementation of Multi-Tier Network Segmentation for Retail Infrastructure
Status: Accepted  
Date: 2026-10-01  
Deciders: Atlas Infrastructure & Security Architecture Committee  

---

## 1. Context and Problem Statement
During initial platform deployment, the application server (SRV-WEB-01) shared a single flat Docker bridge network with the internal customer database (SRV-DB-01) and backup storage (NAS-BKP). When the web server was compromised via unauthenticated file upload, the adversary obtained direct network routability to database port 5432 and backup port 22.

## 2. Decision
We have decided to segment the environment into three distinct, isolated bridge networks:
1. `atlas_dmz`: Contains public-facing reverse proxies and web application tiers.
2. `atlas_internal`: Internal database cluster subnet, configured with `internal: true` (no external routing, only accessible from web application backend).
3. `atlas_backup`: Dedicated backup tier, configured with `internal: true` (only accessible from authorized backup runners).

## 3. Consequences
- **Positive:** Compromised web server nodes cannot route traffic across non-essential services. Direct external access to database port 5432 is eliminated.
- **Negative:** Increased complexity in network orchestration and inter-service routing diagnostics.
