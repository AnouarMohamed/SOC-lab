# Matrice RACI & Chaîne d'Astreinte (Incident INC-ATLAS-001)

## 1. Définition des Rôles de la Cellule de Crise

| Rôle | Titulaire | Suppléant | Missions Principales | Contact Nuit / Astreinte |
| :--- | :--- | :--- | :--- | :--- |
| **Incident Manager** | Léa Martin | Hugo Bernard | Anime la cellule de crise, arbitre les décisions techniques, tient la main courante, qualifie les niveaux de gravité | Téléphone d'astreinte (Appel direct, relance à 10 min, puis suppléant) |
| **Analyste SOC** | Nour Haddad | Paul Girard | Analyse technique, corrélation des signaux SIEM/EDR, extraction des preuves, surveillance de périmètre | Sur place / Astreinte SOC dédiée |
| **Administrateur Système**| Yanis Roux | Sara Lopez | Isolement réseau (iptables/EDR), révocation des accès, collecte forensique, assainissement, reconstruction | Téléphone d'astreinte (Appel + SMS) |
| **Juridique / DPO** | Claire Dupont | Marc Petit | Obligations réglementaires RGPD, notification CNIL sous 72 h, conformité des preuves, réquisition judiciaire | Appel direct, joignable sous 1 h |
| **Communication** | Julie Faure | Tom Richard | Règle du porte-parole unique, messages internes aux équipes et communication publique/clients | Appel direct, joignable sous 2 h |
| **Direction / RSSI** | Éric Lambert (RSSI)<br>Anne Perrin (DSI) | DG : Paul Morel | Décisions stratégiques d'entreprise, arbitrage impact métier, validation de la remise en production | Astreinte téléphonique dédiée, appel direct |

---

## 2. Matrice RACI Opérationnelle

Légende : **R** = Réalise (Responsible) | **A** = Approuve (Accountable - *un seul A par ligne*) | **C** = Consulté (Consulted) | **I** = Informé (Informed)

| Activité Opérationnelle | Incident Manager | Analyste SOC | Admin Système | Juridique / DPO | Communication | Direction / RSSI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Qualifier l'incident** | **A** | **R** | **C** | **I** | **I** | **I** |
| **2. Isoler le serveur** | **A** | **C** | **R** | **I** | **I** | **I** |
| **3. Collecter les preuves** | **A** | **R** | **R** | **C** | - | **I** |
| **4. Révoquer les comptes et secrets** | **A** | **C** | **R** | **I** | - | **I** |
| **5. Notifier les autorités (CNIL 72h)**| **C** | **I** | **I** | **R** | **C** | **A** |
| **6. Communiquer aux clients (Art. 34)**| **C** | **I** | **I** | **C** | **R** | **A** |
| **7. Décider la remise en production** | **R** | **C** | **R** | **I** | **I** | **A** |
