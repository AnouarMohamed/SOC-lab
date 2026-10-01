# Rapport de Retour d'Expérience (Post-Mortem / RCA)
**Référence Incident :** INC-ATLAS-001  
**Titre :** Intrusion par dépôt de webshell et élévation latérale via compte de service (SRV-WEB-01)  
**Date du rapport :** 01 octobre 2026  
**Auteurs :** Équipe SOC & DevSecOps Atlas Distribution  
**Statut :** Clôturé - Plan d'actions engagé  

---

## 1. Résumé Exécutif
Le vendredi à 23h40 UTC, un acteur malveillant a exploité une vulnérabilité d'upload non filtré sur l'application web du serveur `SRV-WEB-01` pour déposer un webshell PHP (`session_sync_eval.php`). En exploitant des privilèges locaux sous l'utilisateur `www-data`, l'attaquant a extrait les identifiants en clair du compte de service `svc-backup` et de la base de données PostgreSQL (`SRV-DB-01`).
Une session SSH externe a été établie à 23h47, et une exfiltration de 40 000 enregistrements clients a été tentée à 00h10 (générant un pic de trafic sortant x10).
L'incident a été qualifié en sévérité **P1 - Critique** à 00h15. Le serveur a été isolé du réseau par iptables sans redémarrage à 00h45, permettant l'acquisition forensique complète des artefacts volatils. Le compte `svc-backup` a été neutralisé, les sauvegardes gelées sur `NAS-BKP`, et la remise en production a été opérée après reconstruction complète du serveur à partir d'une image durcie.

---

## 2. Chronologie des Faits et Interventions (Main Courante Consolidée)

| Horodatage | Acteur | Événement Opérationnel | Qualification / Décision |
| :--- | :--- | :--- | :--- |
| **Ven 23h40** | EDR Agent | Alerte heuristique : processus shell (`/bin/sh`) enfant de `apache2` | Signalement initial |
| **Ven 23h47** | SIEM | Connexion SSH réussie de `svc-backup` depuis une adresse IP externe | Alerte Priorité Haute |
| **Ven 23h55** | FIM / Audit | Fichier non autorisé détecté dans `/var/www/html/uploads/` | Artefact suspect |
| **Sam 00h10** | NetFlow | Détection d'un volume de données sortant 10x supérieur à la normale | Alerte Exfiltration |
| **Sam 00h15** | Analyste SOC | Recoupement des 4 alertes indépendantes, ouverture du dossier | **Incident qualifié en P1** |
| **Sam 00h20** | Analyste SOC | Appel téléphonique d'astreinte à l'Incident Manager et au RSSI | Mobilisation cellule de crise |
| **Sam 00h30** | Incident Manager | Validation P1, accord formel d'isolement réseau, alerte de la DSI | Ordre d'isolement |
| **Sam 00h45** | Administrateur | Application des règles iptables de confinement (pas de reboot) | SRV-WEB-01 isolé |
| **Sam 01h00** | Administrateur | Verrouillage du compte `svc-backup`, gel du snapshot de 02h00 | Sauvegardes préservées |
| **Sam 01h30** | DPO / Direction | Information de la Direction Générale, engagement du délai CNIL 72h | Horloge RGPD active |
| **Sam 02h00** | SOC / Admin | Capture de la mémoire vive, des sockets, export des logs et hashes SHA-256 | Chaîne de preuve scellée |
| **Sam 04h30** | DevSecOps | Reconstruction d'un nœud propre depuis Dockerfile durci (`php_admin_flag engine off`) | Infrastructure assainie |
| **Sam 06h45** | DBA / SecOps | Restauration des données saines, rotation des mots de passe PostgreSQL | Données certifiées |
| **Sam 07h30** | Comité Crise | Contrôles Q11 franchis avec succès, signature du Go/No-Go | Remise en service progressive |

---

## 3. Analyse des Causes Racines (Root Cause Analysis - 5 Pourquoi)

1. **Pourquoi l'attaquant a-t-il pu exécuter des commandes arbitraires ?**  
   *Parce qu'un webshell PHP a été déposé et exécuté dans le répertoire `/uploads/`.*
2. **Pourquoi le webshell a-t-il pu être déposé et interprété ?**  
   *Parce que le formulaire d'upload ne validait ni l'extension ni le type MIME, et Apache autorisait l'exécution de code PHP dans ce dossier.*
3. **Pourquoi l'attaquant a-t-il obtenu des accès SSH et base de données ?**  
   *Parce que les identifiants de la base et la clé SSH du compte `svc-backup` étaient stockés en clair dans des fichiers lisibles par `www-data`.*
4. **Pourquoi l'attaquant a-t-il pu se connecter en SSH depuis l'extérieur ?**  
   *Parce que le port SSH était exposé directement sur l'Internet public sans filtrage IP ni authentification multi-facteurs (MFA).*
5. **Pourquoi la prise en compte a-t-il pris 35 minutes ?**  
   *Parce qu'il n'existait pas de règle de corrélation automatique reliant l'alerte EDR initiale au SSH externe, obligeant l'analyste de garde à un recoupement manuel.*

---

## 4. Matrice des Actions d'Amélioration & Engagements de Remédiation

Conformément à la section 7 du plan de réponse, les actions correctives suivantes sont adoptées :

| Constat Opérationnel | Action Corrective / Technique de Remédiation | Porteur | Échéance |
| :--- | :--- | :--- | :--- |
| **Compte de service `svc-backup` accessible en SSH depuis Internet** | Suppression de l'exposition SSH directe ; passage exclusif par bastion VPN, liste blanche stricte, clés ed25519 avec passphrase, interdiction de connexion interactive pour les comptes de service. | Admin Système | **J+14** |
| **Dépôt de fichiers exécutant du code** | Durcissement Apache (`php_admin_flag engine off`), déport des fichiers déposés sur stockage objet distant (S3/MinIO), scan antivirus automatique (ClamAV/YARA) à l'upload. | DevSecOps / Dév | **J+14** |
| **Délai de corrélation de 35 min** | Implémentation de règles de détection SIEM automatiques (Sigma) avec déclenchement d'appels PagerDuty/SMS immédiats sur l'événement "SSH externe d'un compte de service". | Équipe SOC | **J+30** |
| **Sous-effectif nocturne (1 analyste)** | Renforcement du pool d'astreinte niveau 2, mise en place d'un SOC managé (MSSP) en couverture 24/7 de débordement, exercices de relève. | DSI / RSSI | **J+30** |
| **Sauvegardes vulnérables au compte compromis** | Mise en place de sauvegardes immuables (WORM - Write Once Read Many) avec rétention isolée et politique de séparation des privilèges (le serveur ne peut pas supprimer ses propres sauvegardes). | Ingénieur Stockage | **J+45** |
| **Plan de réponse non éprouvé** | Institutionnalisation d'un exercice de crise annuel (Tabletop Exercise) et pré-remplissage des procédures déclaratives CNIL / ANSSI. | Incident Mgr / DPO | **J+60** |
