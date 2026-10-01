# Playbook 05 : Restauration, Continuité et Vérification Avant Remise en Production

## 1. Objectifs de Résilience (RPO & RTO)
- **RPO (Recovery Point Objective) : 24 heures maximum.**
  - Sauvegarde de référence : Vendredi 02h00 UTC (précédant l'intrusion de 23h40).
  - Copie hebdomadaire hors ligne (cold backup) disponible en secours.
- **RTO (Recovery Time Objective) : 8 heures maximum** à compter de la mise à l'arrêt du site.

---

## 2. Déroulé Chronologique du RTO (8 Heures)

| Fenêtre Temporelle | Actions Opérationnelles | Responsables |
| :--- | :--- | :--- |
| **H0 à H1** | Qualification de l'incident, isolement réseau, gel des comptes, collecte des preuves volatiles. | SOC / Admin |
| **H1 à H3** | Provisionnement d'une machine/conteneur propre depuis une image de référence durcie. | DevOps / Admin |
| **H3 à H6** | Restauration des données saines (antérieures au vendredi 23h40), correction de la faille upload, rotation globale des secrets. | DBA / DevSecOps |
| **H6 à H8** | Exécution des contrôles de sécurité (Checklist Q11), tests d'achat de bout en bout, signature du Go/No-Go. | RSSI / Incident Mgr / Direction |

---

## 3. Checklist de Contrôle Avant Remise en Production (Checklist Q11)

Avant d'autoriser la réouverture du service au public, l'ensemble des 6 vérifications suivantes doit être validé formellement :

- [ ] **1. Absence Totale d'IOC :** Scan antivirus/YARA et inspection des tâches planifiées (`cron`), clés SSH et comptes utilisateurs.
- [ ] **2. Faille Éradiquée :** Exécution de code PHP formellement désactivée dans `/uploads` (`php_admin_flag engine off`), validation MIME stricte.
- [ ] **3. Secrets Renouvelés à 100% :** Ancien mot de passe PostgreSQL révoqué, clés SSH régénérées, mot de passe `svc-backup` réinitialisé dans un coffre-fort (Vault).
- [ ] **4. SSH et Périmètre Durci :** Accès SSH interdit depuis Internet public. Filtrage par passerelle bastion et authentification par clé uniquement.
- [ ] **5. Télémétrie et Journalisation Actives :** EDR actif et remontée des logs vers le SIEM confirmée.
- [ ] **6. Intégrité des Données Validée :** Cohérence des tables clients et intégrité de `SRV-DB-01` et `NAS-BKP` certifiées par le DBA.

---

## 4. Protocole de Go / No-Go
La remise en production ne peut être prononcée qu'avec l'approbation conjointe signée de :
1. **Léa Martin** (Incident Manager)
2. **Éric Lambert** (RSSI / CISO)
3. **Anne Perrin** (DSI / CIO)
4. **Paul Morel** (Directeur Général)

*Période de surveillance renforcée obligatoire de 7 jours post-remise en ligne.*
