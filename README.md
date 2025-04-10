# SecureNLP

SecureNLP est un projet de classification de commentaires (NLP) qui intègre des mécanismes de sécurité afin de protéger les données sensibles, le modèle et l'environnement d'exécution. Le projet a été conçu pour répondre aux exigences d'un pipeline complet en cybersécurité et traitement du langage naturel (NLP).

## Table des matières

- [Contexte et objectifs](#contexte-et-objectifs)
- [Architecture du pipeline](#architecture-du-pipeline)
  - [Partie 1 : Pipeline NLP classique](#partie-1--pipeline-nlp-classique)
  - [Partie 2 : Sécurisation du pipeline](#partie-2--sécurisation-du-pipeline)
- [Choix de sécurité](#choix-de-sécurité)
- [Détails des identifiants](#détails-des-identifiants)
- [Structure du projet](#structure-du-projet)
- [Instructions d'exécution](#instructions-dexécution)
- [Remarques supplémentaires](#remarques-supplémentaires)

## Contexte et objectifs

L’objectif de ce projet est de développer un pipeline de machine learning pour classer des messages SMS (spam ou ham) tout en assurant un haut niveau de sécurité sur :
- **Les données sensibles :** Les messages sont issus d’un jeu de données public, mais dans un contexte réel, ils pourraient provenir de sources confidentielles (forums internes, clients…).
- **Le modèle et son environnement d’exécution :** Le modèle doit être protégé contre toute modification non autorisée et le pipeline doit permettre une traçabilité des accès.
- **La gestion des accès :** Différents rôles (Data Scientist et Analyste) disposent d’un niveau d’accès différencié.

## Architecture du pipeline

### Partie 1 – Pipeline NLP classique

Le notebook `training_pipeline.ipynb` (ou `processing_and_model.ipynb`) réalise les étapes suivantes :

1. **Chargement du jeu de données :**
   - Le dataset utilisé est le jeu de données SMS disponible sur GitHub.
   - Les colonnes sont renommées et les labels sont convertis en valeurs numériques (par exemple, `0` pour "HAM" et `1` pour "SPAM").

2. **Prétraitement des textes :**
   - Transformation en minuscules.
   - Suppression des caractères non alphabétiques.
   - Élimination des stop words (ici, en anglais pour ce dataset).
   - Lemmatisation des tokens pour réduire les variations des mots.

3. **Vectorisation avec TF-IDF :**
   - Transformation des messages en vecteurs numériques grâce à un `TfidfVectorizer`.

4. **Entraînement de plusieurs modèles :**
   - Trois modèles sont testés (Logistic Regression, Multinomial Naive Bayes et Linear SVC).
   - Chaque modèle est évalué à l’aide du F1-score, et le meilleur modèle est sélectionné.
   - **Sauvegarde des artefacts :**  
     - Le meilleur modèle est sauvegardé dans `model.pkl`.
     - Le vectorizer TF-IDF est sauvegardé dans `tfidf.pkl`.
     - Un hash SHA256 du modèle est calculé et stocké dans `model_hash.txt` pour assurer l'intégrité du modèle.

### Partie 2 – Sécurisation du pipeline

L’application Streamlit (fichier `main.py`) intègre plusieurs mécanismes de sécurité :

1. **Chiffrement des prédictions :**
   - Le résultat de la prédiction est chiffré avec la bibliothèque Fernet (provenant du module `cryptography`).
   - Ceci permet d’assurer que les prédictions transmises à l’utilisateur sont protégées et ne peuvent être modifiées ou interceptées.

2. **Gestion des accès :**
   - Une authentification par identifiants est mise en place.
   - Deux rôles distincts sont définis :
     - **Data Scientist :** Accès complet, y compris la possibilité de visualiser les logs et de déchiffrer les prédictions.
     - **Analyste :** Accès limité (accès uniquement aux prédictions chiffrées).

3. **Journalisation :**
   - Les événements critiques (connexion, chargement du modèle, réalisation de prédictions) sont enregistrés dans un fichier `log_access.txt`.
   - Ceci permet la traçabilité et l’audit en cas d’incident de sécurité.

4. **Contrôle d'intégrité du modèle :**
   - Lors du chargement du modèle, le hash SHA256 est recalculé et comparé à la valeur stockée dans `model_hash.txt`.
   - Si une discordance est détectée, une alerte est affichée pour informer l’utilisateur d’une possible modification non autorisée du modèle.

## Choix de sécurité

Les principales mesures de sécurité mises en œuvre dans ce projet sont :

- **Authentification et gestion des rôles :**
  - Mise en place d’un système de connexion avec des identifiants statiques (ex. : `ds_password` pour le Data Scientist).
  - Isolation des privilèges d’accès via des sessions Streamlit, respectant le principe du moindre privilège.

- **Chiffrement des données sensibles :**
  - Utilisation de l'algorithme Fernet pour chiffrer les prédictions avant de les transmettre ou de les stocker.
  - Protection des prédictions afin d’éviter toute réidentification ou interception lors de la transmission.

- **Journalisation et auditabilité :**
  - Enregistrement des actions critiques (connexion, chargement du modèle, prédictions) pour faciliter l’audit en cas d’incident.
  - Le fichier `log_access.txt` permet de retracer toutes les activités.

- **Intégrité du modèle :**
  - Stockage d’un hash SHA256 du modèle dans `model_hash.txt`.
  - Vérification régulière de l'intégrité du modèle pour détecter toute modification non autorisée.

## Détails des identifiants

Pour cette démonstration, des identifiants statiques ont été utilisés afin de simuler la gestion des accès basée sur les rôles. Vous trouverez ci-dessous les credentials utilisés :

| Rôle           | Nom d'utilisateur | Mot de passe / Token |
|----------------|-------------------|----------------------|
| Data Scientist | data_scientist    | ds_password          |
| Analyste       | analyst           | analyst_token        |

> **Remarque :** Ces identifiants sont fournis à titre d'exemple pour tester le système d'authentification. En production, il est recommandé d'utiliser un mécanisme d'authentification sécurisé et de stocker les informations d'identification de manière sécurisée.

## Structure du projet

La structure du projet est organisée de la manière suivante (les fichiers sont stockés dans le même répertoire, sauf si une organisation en sous-dossiers est souhaitée) :


## Instructions d'exécution

1. **Entraînement et sauvegarde du modèle :**
   - Ouvrez le notebook `training_pipeline.ipynb` dans Jupyter.
   - Exécutez toutes les cellules pour charger les données, entraîner les modèles, sélectionner le meilleur et sauvegarder les fichiers `model.pkl`, `tfidf.pkl` et `model_hash.txt`.

2. **Lancement de l’application Streamlit :**
   - Vérifiez que les fichiers générés (`model.pkl`, `tfidf.pkl`, `model_hash.txt`, `secret.key` et `log_access.txt`) se trouvent dans le même répertoire que `main.py`.
   - Ouvrez un terminal et exécutez la commande suivante :
     ```bash
     streamlit run main.py
     ```
   - Connectez-vous avec les identifiants indiqués dans la section **Détails des identifiants**.
   - Saisissez un commentaire pour obtenir une prédiction.  
     - Le résultat sera chiffré et affiché.
     - En tant que Data Scientist, vous pouvez cocher la case « Décrypter la prédiction » pour voir le résultat en clair.

## Remarques supplémentaires

- **Adaptation des chemins :**
  - Par défaut, tous les fichiers sont sauvegardés dans le même répertoire que les scripts. Vous pouvez adapter l'arborescence si nécessaire (par exemple, créer un dossier `models/` pour regrouper `model.pkl`, `tfidf.pkl` et `model_hash.txt`).

- **Sécurité de production :**
  - Les identifiants utilisés dans cet exercice sont statiques et simplifiés pour un environnement de test. En production, il est conseillé d'utiliser des systèmes d'authentification robustes et de stocker les clés et mots de passe de manière sécurisée.
  - La gestion des clés (secret.key) doit être intégrée à une infrastructure de gestion des secrets.

- **Journalisation et auditabilité :**
  - La journalisation avec `log_access.txt` est simple et convient pour une démonstration. Pour une application en production, il est recommandé d'utiliser des systèmes de log centralisés et sécurisés.
