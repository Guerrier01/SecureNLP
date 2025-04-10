import os
import pickle
import hashlib
import datetime
import streamlit as st
from cryptography.fernet import Fernet

#########################################
# Fonctions d'authentification et de journalisation
#########################################

def authenticate(username: str, password: str):
    """
    Vérifie les identifiants avec des valeurs simulées :
    - data_scientist : mot de passe 'ds_password'
    - analyst : mot de passe/token 'analyst_token'
    Renvoie un tuple (booléen, rôle).
    """
    credentials = {
        "data_scientist": "ds_password",
        "analyst": "analyst_token"
    }
    if username in credentials and credentials[username] == password:
        return True, username
    return False, None

def log_event(event: str):
    """
    Ajoute une ligne de log dans 'log_access.txt' avec la date et l'heure.
    """
    with open("log_access.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: {event}\n")

#########################################
# Gestion de la clé de chiffrement
#########################################

def load_key():
    """
    Charge une clé Fernet depuis 'secret.key'.
    Si le fichier n'existe pas, génère et sauvegarde une nouvelle clé.
    """
    key_file = "secret.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
    return key

#########################################
# Vérification de l'intégrité du modèle
#########################################

def compute_file_hash(filename: str) -> str:
    """
    Calcule le hash SHA256 du fichier indiqué.
    """
    h = hashlib.sha256()
    with open(filename, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def verify_model_integrity(model_file="model.pkl", hash_file="model_hash.txt"):
    """
    Vérifie l'intégrité du modèle en comparant le hash actuel à celui stocké.
    Renvoie (True, hash) si concordance, (False, hash) si modification, ou (None, None)
    si les fichiers nécessaires n'existent pas.
    """
    if os.path.exists(model_file) and os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            stored_hash = f.read().strip()
        current_hash = compute_file_hash(model_file)
        if current_hash == stored_hash:
            return True, current_hash
        else:
            return False, current_hash
    else:
        return None, None

#########################################
# Chargement du modèle
#########################################

class DummyModel:
    """
    Modèle simulé en cas d'absence du modèle enregistré.
    Il renvoie "Négatif" si le texte contient certains mots négatifs, sinon "Positif".
    """
    def predict(self, texts):
        results = []
        for text in texts:
            if any(word in text.lower() for word in ["bad", "toxique", "négatif"]):
                results.append("Négatif")
            else:
                results.append("Positif")
        return results

def load_model():
    """
    Tente de charger le modèle depuis 'model.pkl'.
    Vérifie son intégrité si possible. Sinon, utilise DummyModel.
    """
    model_file = "model.pkl"
    if os.path.exists(model_file):
        with open(model_file, "rb") as f:
            model = pickle.load(f)
        verified, current_hash = verify_model_integrity(model_file, "model_hash.txt")
        if verified is False:
            st.warning("Attention : le modèle a été modifié ou compromis !")
        elif verified is True:
            st.info("Modèle vérifié et intègre.")
        else:
            st.info("Aucun hash pour vérifier l'intégrité du modèle.")
        log_event("Modèle chargé")
        return model
    else:
        st.info("Modèle non trouvé. Utilisation d'un modèle simulé.")
        log_event("Utilisation du DummyModel")
        return DummyModel()

#########################################
# Chargement du vectorizer TF-IDF
#########################################

def load_vectorizer():
    tfidf_file = "tfidf.pkl"
    if os.path.exists(tfidf_file):
        with open(tfidf_file, "rb") as f:
            return pickle.load(f)
    else:
        st.warning("TF-IDF vectorizer manquant. Vérifiez que tfidf.pkl existe.")
        return None

#########################################
# Application Streamlit sécurisée
#########################################

def main():
    st.title("SecureNLP - Interface sécurisée")
    
    # Initialisation de la session pour l'authentification
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.role = None

    # Page d'authentification
    if not st.session_state.authenticated:
        st.subheader("Authentification")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe / Token", type="password")
        if st.button("Se connecter"):
            success, role = authenticate(username, password)
            if success:
                st.success("Authentification réussie!")
                st.session_state.authenticated = True
                st.session_state.role = role
                log_event(f"Utilisateur {role} connecté")
            else:
                st.error("Authentification échouée.")
        st.stop()  # Arrête l'exécution tant que l'utilisateur n'est pas authentifié

    # Affichage de l'interface en fonction du rôle
    st.sidebar.write(f"Connecté en tant que : **{st.session_state.role}**")
    if st.session_state.role == "data_scientist":
        st.sidebar.write("**Accès complet**")
        if st.sidebar.button("Voir le log"):
            if os.path.exists("log_access.txt"):
                with open("log_access.txt", "r") as f:
                    st.text(f.read())
            else:
                st.info("Pas de log disponible.")

    st.header("Prédiction des sentiments")
    comment = st.text_area("Entrez un commentaire")
    
    if st.button("Prédire"):
        # Journalisation de l'événement de prédiction
        log_event("Prédiction réalisée")
        
        # Chargement (si nécessaire) du modèle et du vectorizer
        if "model" not in st.session_state:
            st.session_state.model = load_model()
        if "vectorizer" not in st.session_state:
            st.session_state.vectorizer = load_vectorizer()

        if st.session_state.vectorizer is None:
            st.error("TF-IDF vectorizer introuvable. Impossible de prédire.")
        else:
            # Transformation du texte en vecteurs
            X_input = st.session_state.vectorizer.transform([comment])
            
            # Récupération de la prédiction brute
            raw_prediction = st.session_state.model.predict(X_input)[0]
            
            # Mapping de la prédiction selon le type de modèle (adaptez ce mapping selon votre problème)
            label_map = {0: "HAM (non spam)", 1: "SPAM", "Négatif": "Négatif", "Positif": "Positif"}
            if raw_prediction in label_map:
                prediction = label_map[raw_prediction]
            else:
                prediction = str(raw_prediction)
            
            # Chiffrement de la prédiction (ici, 'prediction' est une chaîne lisible)
            key = load_key()
            fernet = Fernet(key)
            encrypted_prediction = fernet.encrypt(prediction.encode()).decode()
            
            # Stockage dans la session pour pouvoir le réutiliser lors du décryptage
            st.session_state["encrypted_prediction"] = encrypted_prediction
            st.session_state["clear_prediction"] = prediction
            
            st.write("**Prédiction encryptée :**")
            st.code(encrypted_prediction)
    
    # Si une prédiction a déjà été réalisée, on affiche la possibilité de la déchiffrer
    if st.session_state.get("encrypted_prediction") and st.session_state.role == "data_scientist":
        if st.checkbox("Décrypter la prédiction"):
            # Recharger la clé pour déchiffrer
            key = load_key()
            fernet = Fernet(key)
            decrypted_prediction = fernet.decrypt(st.session_state["encrypted_prediction"].encode()).decode()
            st.write("**Prédiction décryptée :**", decrypted_prediction)

if __name__ == "__main__":
    main()
