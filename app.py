import streamlit as st
import pandas as pd

# Configuration de la page mobile-friendly
st.set_page_config(
    page_title="FIMECO SITUATION", 
    page_icon="🏦", 
    layout="centered"
)

# Style CSS pour améliorer le rendu sur mobile
st.markdown(
    """
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/584/584026.png">
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        padding: 8px 16px; 
        background-color: #f0f2f6; 
        border-radius: 4px; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Titre visuel dans l'appli
st.title("📊 FIMECO 2026")
st.subheader("Espace Membre Sécurisé")

# ⚠️ METTEZ ICI L'IDENTIFIANT DE VOTRE GOOGLE SHEET
SHEET_ID = "1yK5U8J-QbLixc4HNBKssbnqIKDkFmzEULqiV6ZxJvts"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)  # Rafraîchissement toutes les minutes
def load_data():
    return pd.read_csv(GOOGLE_SHEET_URL)

def format_monnaie(valeur):
    """Formate proprement les montants financiers"""
    if pd.isna(valeur): 
        return "0 F CFA"
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
    
    # Formulaire de connexion
    with st.form("search_form"):
        phone_input = st.text_input("Téléphone saisi", placeholder="Ex: 77xxxxxxx")
        code_input = st.text_input("Code saisi", placeholder="Ex: XXXXXXX")
        submit_button = st.form_submit_button("Se connecter à mon espace")

    if submit_button or st.session_state.get('connected', False):
        if phone_input and code_input:
            
            # Fonctions de nettoyage
            def nettoyer_telephone(val):
                s = str(val).strip()
                if s.endswith('.0'): s = s[:-2]
                return s.replace(" ", "").replace("-", "")

            df['Telephone_clean'] = df['Telephone'].apply(nettoyer_telephone)
            df['Id_Code_clean'] = df['Id_Code'].astype(str).str.strip().str.upper()
            
            saisie_telephone = phone_input.strip().replace(" ", "").replace("-", "")
            saisie_code = code_input.strip().upper()
            
            # Vérification du membre
            result = df[(df['Telephone_clean'] == saisie_telephone) & (df['Id_Code_clean'] == saisie_code)]
            
            if not result.empty:
                st.session_state['connected'] = True
                row = result.iloc[0]
                
                st.success(f"👋 Bienvenue, {row['Prenoms']} {row['Nom']} !")
                st.markdown("---")
                
                # --- CRÉATION DES ONGLETS INTERACTIFS ---
                tab1, tab2, tab3 = st.tabs(["📋 Mon Bilan", "📅 Détail par Mois", "📈 Caisse FIMECO"])
                
                # ONGLET 1 : BILAN GÉNÉRAL PERSO
                with tab1:
                    st.markdown("### Votre situation générale")
                    st.metric(label="Montant Souscrit", value=format_monnaie(row['Montant Souscrit']))
                    st.metric(label="Montant Déjà Cotisé", value=format_monnaie(row['Montant Cotise']))
                    st.metric(label="Solde Restant à Verser", value=format_monnaie(row['Solde Restant']), delta=None)
                
                # ONGLET 2 : RECHERCHE MENSUELLE INTERACTIVE
                with tab2:
                    st.markdown("### Consultation des paiements mensuels")
                    
                    # Liste exacte de vos colonnes de mois (respectant vos majuscules/minuscules)
                    liste_mois = ['Mars', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']
                    
                    # Bouton de choix du mois
                    mois_choisi = st.selectbox("Sélectionnez un mois à vérifier :", liste_mois)
                    
                    # Affichage du montant pour le mois sélectionné
                    montant_mois = row[mois_choisi]
                    st.info(f"Pour le mois de **{mois_choisi.upper()}**, votre versement enregistré est de : **{format_monnaie(montant_mois)}**")
                    
                    # Option bonus : Afficher tout l'historique d'un coup dans un tableau dépliant
                    with st.expander("👁️ Voir l'historique complet de l'année"):
                        historique = {mois: [format_monnaie(row[mois])] for mois in liste_mois}
                        df_hist = pd.DataFrame(historique, index=["Montant versé"])
                        st.table(df_hist.T)
                
                # ONGLET 3 : STATISTIQUES GLOBALES DE L'ASSOCIATION
                with tab3:
                    st.markdown("### Situation Globale de la Caisse FIMECO 2026")
                    st.write("Section transparence : Voici l'état actuel de la caisse collective.")
                    
                    # Calculs automatiques basés sur l'ensemble de votre Google Sheet
                    total_membres = len(df)
                    total_global_collecte = df['Montant Cotise'].sum()
                    total_global_restant = df['Solde Restant'].sum()
                    
                    # Affichage sous forme de jolies cartes de statistiques
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Total Collecté (FIMECO)", value=format_monnaie(total_global_collecte))
                        st.metric(label="Nombre de Souscripteurs", value=f"{total_membres} membres")
                    with col2:
                        st.metric(label="Reste à Recouvrer", value=format_monnaie(total_global_restant))
                
                # Rappel des moyens de paiement en bas de page
                st.markdown("---")
                st.caption("ℹ️ Pour vos prochains versements via Wave ou OM : **787819890** (Précisez votre code)")
            else:
                st.error("❌ Aucun membre trouvé avec ce numéro et ce code. Veuillez vérifier vos accès.")
        else:
            st.warning("⚠️ Veuillez remplir les deux champs pour lancer la recherche.")

except Exception as e:
    st.error(f"❌ Une erreur technique est survenue : {e}")
