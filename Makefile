# ==============================================================================
# Atlas Distribution SecOps & DFIR Lab - Master Automation Makefile
# ==============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help up down status attack qualify isolate collect revoke timeline verify report harden clean

help: ## Show this help menu
	@echo "========================================================================"
	@echo " ATLAS SEC-OPS & INCIDENT RESPONSE LAB (INC-ATLAS-001)"
	@echo "========================================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""

up: ## Build and start the simulated enterprise infrastructure
	@echo "[+] Starting Atlas Distribution infrastructure..."
	docker compose up -d --build
	@echo "[+] Services online: SRV-WEB-01 (http://localhost:8080, SSH :2222), SRV-DB-01, NAS-BKP"

down: ## Stop all lab services
	@echo "[-] Stopping infrastructure..."
	docker compose down

status: ## Inspect cluster health, open sockets, and live threat telemetry
	@python3 incident-response/cli/atlas_ir.py status

attack: ## Execute purple team adversary simulation (reproduce INC-ATLAS-001 killchain)
	@python3 attack/attack_simulation.py --url http://localhost:8080 --speed fast

qualify: ## Run incident qualification wizard & compute P1-P4 SLA and GDPR 72h clock
	@python3 incident-response/cli/atlas_ir.py qualify

isolate: ## Execute emergency network quarantine on SRV-WEB-01 (Preserves RAM)
	@python3 incident-response/cli/atlas_ir.py isolate

collect: ## Harvest volatile memory, network sockets, logs, and compute SHA-256 manifest
	@python3 incident-response/cli/atlas_ir.py collect

revoke: ## Lock svc-backup account, purge rogue SSH keys, and rotate database credentials
	@python3 incident-response/cli/atlas_ir.py revoke

timeline: ## Print chronological Incident Journal (Main Courante)
	@python3 incident-response/cli/atlas_ir.py timeline

verify: ## Run pre-production security checklist verification (Checklist Q11)
	@python3 incident-response/cli/atlas_ir.py verify

report: ## Generate official CNIL / GDPR Article 33 notification draft & Executive Post-Mortem
	@python3 incident-response/cli/atlas_ir.py report

harden: ## Deploy post-remediation hardened infrastructure baseline
	@echo "[+] Deploying hardened production baseline..."
	docker compose -f docker-compose.hardened.yml up -d --build
	@echo "[OK] Hardened tier active on http://localhost:8080 (No SSH exposed, execution blocked in /uploads)"

clean: ## Tear down lab and purge generated forensic evidence
	docker compose down -v --remove-orphans
	docker compose -f docker-compose.hardened.yml down -v --remove-orphans 2>/dev/null || true
	rm -rf incident-response/artifacts/evidence_* incident-response/artifacts/forensics_*
	@echo "[OK] Lab cleaned."
