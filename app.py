import streamlit as st
import pandas as pd

# Configuration de la page mobile-friendly
st.set_page_config(page_title="FIMECO 2026", page_icon="💰", layout="centered")

# Titre de l'application
st.title("📊 FIMECO 2026")
st.subheader("Consultation sécurisée des soldes")
st.write("Entrez vos identifiants pour afficher votre situation financière en temps réel.")

# URL de votre Google Sheet (formaté pour l'export CSV direct)
# REMPLACEZ 'VOTRE_ID_DE_FEUILLE' par l'ID réel présent dans l'URL de votre Google Sheet
SHEET_ID = "1yK5U8J-QbLixc4HNBKssbnqIKDkFmzEULqiV6ZxJvts"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)  # Met en cache les données 5 min pour optimiser la vitesse
def load_data():
    return pd.read_csv(GOOGLE_SHEET_URL)

try:
    df = load_data()
    
    # Formulaire d'identification
    with st.form("search_form"):
        phone_input = st.text_input("Téléphone saisi", placeholder="Ex: 777821507")
        code_input = st.text_input("Code saisi", placeholder="Ex: FIM-008")
        submit_button = st.form_submit_button("Valider la recherche")

    if submit_button:
        if phone_input and code_input:
            # Normalisation des données pour éviter les erreurs de type (String vs Int)
            df['Telephone'] = df['Telephone'].astype(str).str.strip()
            df['Code'] = df['Code'].astype(str).str.strip()
            
            # Requête de filtrage
            result = df[(df['Telephone'] == phone_input.strip()) & (df['Code'] == code_input.strip())]
            
            if not result.empty:
                row = result.iloc[0]
                
                # Extraction des variables (ajustez les noms des colonnes selon votre tableau)
                prenom = row['Prenoms']
                nom = row['Nom']
                souscrit = row['Montant Souscrit']
                cotise = row['Montant Cotise']
                solde = row['Solde']
                
                # Affichage des résultats stylisés
                st.success(f"👋 Bonjour {prenom} {nom} !")
                
                st.markdown(f"""
                ### 📋 Votre bilan FIMECO 2026 :
                * **Montant souscrit :** {int(souscrit):,} F CFA
                * **Montant déjà cotisé :** {int(cotise):,} F CFA
                * **Solde restant à verser :** `{int(solde):,} F CFA`
                """)
                
                st.markdown("---")
                st.info("""
                ℹ️ **Pour vos prochains versements :**
                * Via **Wave** ou **Orange Money** au : **787819890**
                * *Merci de préciser impérativement votre Code Souscripteur lors du dépôt.*
                """)
            else:
                st.error("❌ Aucun membre trouvé avec ce numéro et ce code. Veuillez vérifier vos accès.")
        else:
            st.warning("⚠️ Veuillez remplir les deux champs pour lancer la recherche.")

except Exception as e:
    st.error(f"❌ Une erreur technique est survenue : {e}")
    if 'df' in locals():
        st.warning("🔍 Voici les noms exacts des colonnes détectées dans votre fichier :")
        st.write(list(df.columns))
