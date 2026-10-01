# Main Courante & Journal de Bord Chronologique (Incident INC-ATLAS-001)

Ce document consigne minute par minute les constatations factuelles, les alertes de sécurité, les décisions opérationnelles d'arbitrage et les actions d'atténuation conduites au cours de la gestion de l'incident.

## 1. Déroulement Chronologique Complet

| Horodatage | Auteur / Source | Fait Constaté ou Action Menée | Décision Associée & Suivi |
| :--- | :--- | :--- | :--- |
| **Ven 23h40** | EDR Agent | Alerte heuristique : processus inconnu exécuté sous le compte du serveur web `www-data` sur `SRV-WEB-01`. | Prise en compte dans la file d'attente d'astreinte. |
| **Ven 23h47** | SIEM | Connexion SSH réussie du compte `svc-backup` depuis une adresse IP externe inconnue. | Déclenchement d'un seuil critique de corrélation. |
| **Ven 23h55** | Surveillance Fichiers | Détection d'un script suspect (`session_sync_eval.php`) déposé dans `/var/www/html/uploads/`. | Artefact isolé pour extraction et analyse statique. |
| **Sam 00h10** | NetFlow / Sonde Réseau | Constat d'un trafic sortant environ 10 fois supérieur à la normale vers une adresse IP externe non identifiée. | Suspicion d'exfiltration en cours. |
| **Sam 00h15** | Analyste SOC (Nour Haddad) | Recoupement des 4 signaux indépendants en 35 minutes. Ouverture formelle de l'incident **INC-ATLAS-001** et tenue de la main courante. | Qualification engagée. |
| **Sam 00h20** | Analyste SOC | Appel téléphonique à l'Incident Manager (Léa Martin) et au RSSI (Éric Lambert). Proposition de classification **P1 - Critique**. | Pré-mobilisation de la cellule de crise. |
| **Sam 00h30** | Incident Manager | Confirmation du niveau **P1 - Critique**. Notification de la DSI (Anne Perrin). Ordre formel d'isolement réseau immédiat sans coupure électrique. | Arbitrage : Préservation de la RAM prioritaire. |
| **Sam 00h45** | Administrateur (Yanis Roux) | Application des règles de quarantaine réseau iptables sur `SRV-WEB-01`. Désactivation du compte `svc-backup`. Blocage IP pare-feu. | Isolement réseau effectif sans redémarrage. |
| **Sam 01h00** | Administrateur Système | Suspension immédiate de la tâche planifiée de sauvegarde de 02h00 pour empêcher l'écrasement des sauvegardes saines sur `NAS-BKP`. | Intégrité des sauvegardes garantie. |
| **Sam 01h30** | DPO / Direction | Notification officielle de la Direction Générale et de la DPO (Claire Dupont). Début du décompte légal de 72 heures (RGPD Art. 33). | Horloge de notification CNIL active. |
| **Sam 02h00** | Admin & SOC Forensics | Capture de l'état volatil : processus, sockets réseau ouverts (`ss -antp`), logs applicatifs et système. Calcul de l'empreinte SHA-256 de tous les artefacts. | Scellement de la chaîne de preuve. |
| **Sam 04h00** | DevSecOps & DevOps | Démarrage de la reconstruction du serveur web depuis une image Docker durcie (`Dockerfile.hardened`) avec interdiction d'exécution PHP dans `/uploads`. | Reconstruction sécurisée. |
| **Sam 06h00** | Administrateur Base & SecOps | Vérification d'intégrité de `SRV-DB-01`, rotation complète des mots de passe administrateur et de la clé SSH de secours. | Secrets révoqués et renouvelés. |
| **Sam 07h30** | Comité de Crise | Réunion de validation : les 6 points de contrôle de la checklist Q11 sont validés sans réserve. Signature de la décision Go/No-Go. | Remise en service par paliers avec surveillance 7 jours. |
