# Formulaire de Notification de Violation de Données Personnelles
**Référence Incident :** INC-ATLAS-001  
**Autorité Compétente :** CNIL (Commission Nationale de l'Informatique et des Libertés)  
**Fondement Juridique :** RGPD / GDPR - Article 33 (Notification sous 72 heures)  
**Date et Heure du Signalement :** 2026-10-01 11:21:44 UTC  

---

## 1. Organisme Responsable de Traitement
* **Raison Sociale :** Atlas Distribution S.A.
* **Secteur d'activité :** Commerce électronique et logistique de distribution
* **Contact DPO (Délégué à la Protection des Données) :** Claire Dupont (`dpo@atlas-distribution.fr`)
* **Responsable Incident :** Léa Martin (`incident-response@atlas-distribution.fr`)

## 2. Caractérisation de la Violation
* **Nature de l'incident :** Accès illégitime et suspicion d'exfiltration suite à la compromission d'un serveur applicatif web (SRV-WEB-01) et rebond sur la base de données client (SRV-DB-01).
* **Vecteur initial :** Dépôt non autorisé d'un webshell via le portail d'échange de fichiers, suivi d'une utilisation illégitime du compte de service `svc-backup`.
* **Heure de détection initiale :** 23h40 UTC (EDR), 23h47 UTC (SIEM).
* **Heure de qualification de la violation :** 00h15 UTC.

## 3. Données et Personnes Concernées
* **Volume estimé :** Environ 40 000 comptes clients enregistrés.
* **Catégories de données exposées :**
  - Identité : Nom, Prénom
  - Coordonnées : Adresse e-mail, Téléphone, Adresse postale de livraison
  - Authentification : Mots de passe hachés (algorithme bcrypt)
  - Données financières : Masquées / tronquées (4 derniers chiffres uniquement, conformité PCI-DSS)

## 4. Conséquences Probables et Risques pour les Personnes
* Risque élevé de tentatives d'hameçonnage ciblé (phishing / spear phishing).
* Risque de réutilisation d'identifiants sur d'autres services en cas de mot de passe réutilisé.
* Mesure d'atténuation : Aucun mot de passe en clair dans la base de données.

## 5. Mesures Correctives et Curatives Prises Immédiatement
1. **Isolement Réseau :** Quarantaine réseau de SRV-WEB-01 sans coupure électrique afin de préserver les preuves volatiles.
2. **Révocation d'Accès :** Verrouillage immédiat du compte `svc-backup`, révocation des clés SSH autorisées, rotation complète des secrets de connexion à la base de données.
3. **Protection des Sauvegardes :** Gel des tâches de sauvegarde pour empêcher tout écrasement par des états corrompus sur NAS-BKP (rétention 30 jours sécurisée).
4. **Remédiation Technique :** Interdiction d'exécution de scripts dans les répertoires d'upload, validation stricte des extensions et types MIME.
5. **Information des Personnes (Art. 34) :** Préparation d'une communication directe aux 40 000 clients avec réinitialisation forcée des mots de passe.
