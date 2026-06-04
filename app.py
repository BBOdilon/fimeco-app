import streamlit as st
import pandas as pd

# Configuration de la page mobile-friendly
st.set_page_config(
    page_title="FIMECO SITUATION", 
    page_icon="🏦", 
    layout="centered"
)

# Style CSS personnalisé pour des cartes modernes et un affichage responsive
st.markdown(
    """
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/584/584026.png">
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        padding: 10px 14px; 
        background-color: #f0f2f6; 
        border-radius: 6px;
        font-weight: bold;
    }
    /* Style pour les encadrés de statistiques globales */
    .stat-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stat-card-danger {
        background-color: #fdf2f2;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #de3545;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Titre principal
st.title("📊 FIMECO 2026")
st.subheader("Espace Membre Sécurisé")

# ⚠️ METTEZ ICI L'IDENTIFIANT DE VOTRE GOOGLE SHEET
SHEET_ID = "1yK5U8J-QbLixc4HNBKssbnqIKDkFmzEULqiV6ZxJvts"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(GOOGLE_SHEET_URL)

def format_monnaie(valeur):
    """Formate proprement les nombres en devise F CFA avec séparateur d'espace"""
    if pd.isna(valeur): 
        return "0 F CFA"
    try:
        # Nettoyage au cas où la valeur contient déjà du texte
        txt = str(valeur).replace(" ", "").replace("FCFA", "").replace("F", "")
        val_int = int(float(txt))
        return f"{val_int:,}".replace(",", " ") + " F CFA"
    except:
        return f"{valeur} F CFA"

def nettoyer_vers_entier(colonne):
    """Force une colonne textuelle contenant des chiffres à devenir un entier mathématique"""
    return pd.to_numeric(
        colonne.astype(str).str.replace(r'[\s\sFfCcFfAa,]', '', regex=True), 
        errors='coerce'
    ).fillna(0).astype(int)

try:
    df_raw = load_data()
    df_raw.columns = df_raw.columns.str.strip()
    
    # Nettoyage crucial : on élimine les lignes totalement vides ou sans identifiants valides
    df = df_raw.dropna(subset=['Id_Code', 'Telephone']).copy()
    
    # Formulaire de connexion
    with st.form("search_form"):
        phone_input = st.text_input("Téléphone saisi", placeholder="Ex: 77xxxxxxx")
        code_input = st.text_input("Code saisi", placeholder="Ex: XXXXXXX")
        submit_button = st.form_submit_button("Se connecter à mon espace")

    if submit_button or st.session_state.get('connected', False):
        if phone_input and code_input:
            
            # Normalisation des numéros et codes pour la recherche
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
                st.session_state['connected'] = True
                row = result.iloc[0]
                
                st.success(f"👋 Bienvenue, {row['Prenoms']} {row['Nom']} !")
                st.markdown("---")
                
                # Onglets principaux
                tab1, tab2, tab3 = st.tabs(["📋 Mon Bilan", "📅 Détail par Mois", "📈 Caisse FIMECO"])
                
                # ONGLET 1 : MON BILAN PERSO
                with tab1:
                    st.markdown("### Votre situation générale")
                    st.metric(label="Montant Souscrit", value=format_monnaie(row['Montant Souscrit']))
                    st.metric(label="Montant Déjà Cotisé", value=format_monnaie(row['Montant Cotise']))
                    st.metric(label="Solde Restant à Verser", value=format_monnaie(row['Solde Restant']))
                
                # ONGLET 2 : DÉTAIL PAR MOIS
                with tab2:
                    st.markdown("### Consultation des paiements mensuels")
                    liste_mois = ['Mars', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']
                    mois_choisi = st.selectbox("Sélectionnez un mois à vérifier :", liste_mois)
                    
                    st.info(f"Pour le mois de **{mois_choisi.upper()}**, votre versement enregistré est de : **{format_monnaie(row[mois_choisi])}**")
                    
                    with st.expander("👁️ Voir l'historique complet de l'année"):
                        historique = {mois: [format_monnaie(row[mois])] for mois in liste_mois}
                        st.table(pd.DataFrame(historique, index=["Montant versé"]).T)
                
                # ONGLET 3 : CAISSE GLOBALE (DESIGN AMÉLIORÉ ET MATHÉMATIQUE)
                with tab3:
                    st.markdown("### Situation Globale de la Caisse FIMECO 2026")
                    st.write("Section transparence : Voici l'état actuel de la caisse collective.")
                    
                    # CORRECTION DU BUG : Conversion mathématique stricte avant le calcul de la somme
                    total_membres = len(df)
                    total_global_collecte = nettoyer_vers_entier(df['Montant Cotise']).sum()
                    total_global_restant = nettoyer_vers_entier(df['Solde Restant']).sum()
                    
                    # Affichage sous forme de jolies cartes thématiques bien espacées
                    st.markdown(
                        f"""
                        <div class="stat-card">
                            <p style="margin:0; font-size:14px; color:#555;">💰 TOTAL COLLECTÉ (FONDS ACTUELS)</p>
                            <h2 style="margin:5px 0 0 0; color:#1f77b4; font-size:28px;">{format_monnaie(total_global_collecte)}</h2>
                        </div>
                        <div class="stat-card-danger">
                            <p style="margin:0; font-size:14px; color:#555;">⚠️ RESTE À RECOUVRER (DUS MEMBRES)</p>
                            <h2 style="margin:5px 0 0 0; color:#de3545; font-size:28px;">{format_monnaie(total_global_restant)}</h2>
                        </div>
                        <div class="stat-card" style="border-left-color: #28a745;">
                            <p style="margin:0; font-size:14px; color:#555;">👥 NOMBRE DE SOUSCRIPTEURS ACTIFS</p>
                            <h2 style="margin:5px 0 0 0; color:#28a745; font-size:28px;">{total_membres} membres</h2>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                st.markdown("---")
                st.caption("ℹ️ Pour vos prochains versements via Wave ou OM : **787819890** (Précisez votre code)")
            else:
                st.error("❌ Aucun membre trouvé avec ce numéro et ce code. Veuillez vérifier vos accès.")
        else:
            st.warning("⚠️ Veuillez remplir les deux champs pour lancer la recherche.")

except Exception as e:
    st.error(f"❌ Une erreur technique est survenue : {e}")
