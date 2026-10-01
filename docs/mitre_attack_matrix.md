# MITRE ATT&CK® Enterprise Mapping - Incident INC-ATLAS-001

Ce laboratoire couvre l'intégralité de la chaîne de compromission (Killchain) d'une attaque ciblée sur serveur web exposé, du point d'entrée initial à l'exfiltration de données à caractère personnel :

| Phase Killchain | Tactique MITRE | Technique ID | Nom de la Technique | Procédure & Preuve Observée |
| :--- | :--- | :--- | :--- | :--- |
| **1. Entrée Initiale** | Initial Access | [T1190](https://attack.mitre.org/techniques/T1190/) | Exploit Public-Facing Application | Requête `POST /upload.php` sans validation d'extension ni de type MIME |
| **2. Persistance** | Persistence | [T1505.003](https://attack.mitre.org/techniques/T1505/003/) | Server Software Component: Web Shell | Création du fichier `/var/www/html/uploads/session_sync_eval.php` |
| **3. Exécution** | Execution | [T1059.004](https://attack.mitre.org/techniques/T1059/004/) | Command and Scripting Interpreter: Unix Shell | Exécution de commandes bash sous le contexte du compte `www-data` |
| **4. Accès Identifiants**| Credential Access | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) | Unsecured Credentials: Credentials in Files | Lecture de `/var/www/html/db.php` et `/opt/scripts/backup.sh` |
| **5. Mouvement Latéral**| Lateral Movement / Initial Access | [T1021.004](https://attack.mitre.org/techniques/T1021/004/)<br>[T1078.002](https://attack.mitre.org/techniques/T1078/002/) | Remote Services: SSH<br>Valid Accounts: Domain/Service Accounts | Authentification SSH réussie du compte `svc-backup` depuis une IP externe non listée |
| **6. Exfiltration** | Exfiltration | [T1048.003](https://attack.mitre.org/techniques/T1048/003/)<br>[T1567](https://attack.mitre.org/techniques/T1567/) | Exfiltration Over Alternative Protocol: Unencrypted/Symmetric Protocol | Requête directe PostgreSQL extrayant 40 000 enregistrements et streaming sortant x10 |

---

## Règles de Détection et Signatures Déployées

- **Sigma :**
  - `telemetry/rules/sigma/proc_creation_php_shell.yml` -> T1059.004
  - `telemetry/rules/sigma/file_event_webshell_upload.yml` -> T1505.003
  - `telemetry/rules/sigma/ssh_service_account_external_login.yml` -> T1021.004, T1078.002
  - `telemetry/rules/sigma/net_anomalous_egress_traffic.yml` -> T1048.003, T1567
- **Falco :**
  - `telemetry/rules/falco/atlas_falco_rules.yaml` (Interception eBPF des processus et descripteurs ouverts en écriture/lecture)
- **YARA :**
  - `telemetry/rules/yara/webshell_atlas.yar` (Signature statique pour triage disque et mémoire)
