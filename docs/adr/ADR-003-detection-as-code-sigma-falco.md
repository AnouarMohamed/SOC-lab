# Architecture Decision Record (ADR 003)
## Title: Adoption of Detection-as-Code via Open-Source Sigma and Falco Engines
Status: Accepted  
Date: 2026-10-01  
Deciders: Atlas SOC & Detection Engineering Leadership  

---

## 1. Context and Problem Statement
Detection rules previously maintained in proprietary SIEM consoles suffered from drift, lacked automated test coverage, and were not version-controlled alongside application code.

## 2. Decision
1. Standardize on **Sigma HQ** rule syntax for all log-based detection engineering (Apache, PostgreSQL, SSH, and Linux auditd logs).
2. Standardize on **CNCF Falco** for kernel-level runtime syscall behavioral monitoring in containerized workloads.
3. Integrate detection rule linting and test validation directly into the CI/CD pipeline using `sigma-cli` and automated test datasets.

## 3. Consequences
- **Positive:** Vendor-agnostic detection rules, full peer-review process via Git pull requests, and automated validation prior to deployment.
- **Negative:** Requires continuous maintenance of Sigma conversion mappings across target SIEM backends.
