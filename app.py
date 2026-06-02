import streamlit as st
import pandas as pd

# Configuration de la page mobile-friendly
st.set_page_config(page_title="FIMECO 2026", page_icon="💰", layout="centered")

# Titre de l'application
st.title("📊 FIMECO 2026")
st.subheader("Consultation sécurisée des soldes")
st.write("Entrez vos identifiants pour afficher votre situation financière en temps réel.")

# ⚠️ REMETTEZ ICI L'IDENTIFIANT DE VOTRE GOOGLE SHEET
SHEET_ID = "1yK5U8J-QbLixc4HNBKssbnqIKDkFmzEULqiV6ZxJvts"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)  # Met en cache 5 minutes pour la rapidité
def load_data():
    return pd.read_csv(GOOGLE_SHEET_URL)

def format_monnaie(valeur):
    """Formate proprement les montants financiers"""
    if pd.isna(valeur):
        return "0 F CFA"
    if isinstance(valeur, str):
        valeur = valeur.strip()
        if "CFA" in valeur:
            return valeur
        return f"{valeur} F CFA"
    try:
        return f"{int(valeur):,}".replace(",", " ") + " F CFA"
    except:
        return f"{valeur} F CFA"

try:
    df = load_data()
    
    # Nettoyage automatique des noms de colonnes
    df.columns = df.columns.str.strip()
    
    # Formulaire d'identification
    with st.form("search_form"):
        phone_input = st.text_input("Téléphone saisi", placeholder="Ex: 77xxxxxxx")
        code_input = st.text_input("Code saisi", placeholder="Ex: XXXXXXX")
        submit_button = st.form_submit_button("Valider la recherche")

    if submit_button:
        if phone_input and code_input:
            
            # Fonction de nettoyage ultra-robuste pour les téléphones
            def nettoyer_telephone(val):
                s = str(val).strip()
                if s.endswith('.0'):  # Supprime le .0 si le numéro est lu comme un décimal
                    s = s[:-2]
                return s.replace(" ", "").replace("-", "")

            # Application des nettoyages sur la base de données
            df['Telephone_clean'] = df['Telephone'].apply(nettoyer_telephone)
            df['Id_Code_clean'] = df['Id_Code'].astype(str).str.strip().str.upper()
            
            # Nettoyage des saisies de l'utilisateur
            saisie_telephone = phone_input.strip().replace(" ", "").replace("-", "")
            saisie_code = code_input.strip().upper()
            
            # Requête de filtrage sur les colonnes nettoyées
            result = df[(df['Telephone_clean'] == saisie_telephone) & (df['Id_Code_clean'] == saisie_code)]
            
            if not result.empty:
                row = result.iloc[0]
                
                # Extraction des variables sécurisées
                prenom = row['Prenoms']
                nom = row['Nom']
                souscrit = format_monnaie(row['Montant Souscrit'])
                cotise = format_monnaie(row['Montant Cotise'])
                solde = format_monnaie(row['Solde Restant'])
                
                # Affichage des résultats stylisés
                st.success(f"👋 Bonjour {prenom} {nom} !")
                
                st.markdown(f"""
                ### 📋 Votre bilan FIMECO 2026 :
                * **Montant souscrit :** {souscrit}
                * **Montant déjà cotisé :** {cotise}
                * **Solde restant à verser :** `{solde}`
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
    st.error(f"❌ Une erreur est survenue lors du traitement : {e}")
