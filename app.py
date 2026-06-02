
import streamlit as st
import pandas as pd

# 1. NOM ET ICONE DE L'APPLICATION (Ce qui s'affiche sur le téléphone)
st.set_page_config(
    page_title="FIMECO SITUATION", 
    page_icon="🏦", 
    layout="centered"
)

# Petit "hack" pour forcer l'icône sur iPhone/Android lors de l'ajout à l'écran d'accueil
st.markdown(
    """
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/584/584026.png">
    """,
    unsafe_allow_html=True
)

# Titre visuel dans l'appli
st.title("📊 FIMECO 2026")
st.subheader("Consultation sécurisée des soldes")
st.write("Entrez vos identifiants pour afficher votre situation financière en temps réel.")

# ⚠️ REMETTEZ ICI L'IDENTIFIANT DE VOTRE GOOGLE SHEET
SHEET_ID = "1yK5U8J-QbLixc4HNBKssbnqIKDkFmzEULqiV6ZxJvts"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv(GOOGLE_SHEET_URL)

def format_monnaie(valeur):
    if pd.isna(valeur): return "0 F CFA"
    if isinstance(valeur, str):
        valeur = valeur.strip()
        return valeur if "CFA" in valeur else f"{valeur} F CFA"
    try:
        return f"{int(valeur):,}".replace(",", " ") + " F CFA"
    except:
        return f"{valeur} F CFA"

try:
    df = load_data()
    df.columns = df.columns.str.strip()
    
    with st.form("search_form"):
        phone_input = st.text_input("Téléphone saisi", placeholder="Ex: 77xxxxxxx")
        code_input = st.text_input("Code saisi", placeholder="Ex: XXXXXXX")
        submit_button = st.form_submit_button("Valider la recherche")

    if submit_button:
        if phone_input and code_input:
            def nettoyer_telephone(val):
                s = str(val).strip()
                if s.endswith('.0'): s = s[:-2]
                return s.replace(" ", "").replace("-", "")

            df['Telephone_clean'] = df['Telephone'].apply(nettoyer_telephone)
            df['Id_Code_clean'] = df['Id_Code'].astype(str).str.strip().str.upper()
            saisie_telephone = phone_input.strip().replace(" ", "").replace("-", "")
            saisie_code = code_input.strip().upper()
            
            result = df[(df['Telephone_clean'] == saisie_telephone) & (df['Id_Code_clean'] == saisie_code)]
            
            if not result.empty:
                row = result.iloc[0]
                st.success(f"👋 Bonjour {row['Prenoms']} {row['Nom']} !")
                st.markdown(f"""
                ### 📋 Votre bilan FIMECO 2026 :
                * **Montant souscrit :** {format_monnaie(row['Montant Souscrit'])}
                * **Montant déjà cotisé :** {format_monnaie(row['Montant Cotise'])}
                * **Solde restant à verser :** `{format_monnaie(row['Solde Restant'])}`
                """)
                st.markdown("---")
                st.info("ℹ️ **Versements via Wave ou OM au : 787819890**")
            else:
                st.error("❌ Aucun membre trouvé.")
except Exception as e:
    st.error(f"❌ Erreur : {e}")
