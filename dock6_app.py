import streamlit as st
import os
import subprocess
from PIL import Image

# Doit être la première commande Streamlit
st.set_page_config(page_title="DOCK6 - Analyse Effet Fondateur", layout="wide")

# Appliquer un thème sobre et scientifique via HTML/CSS léger
st.markdown("""
<style>
    body {
        background-color: #f4f6f9;
        color: #2c3e50;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        box-shadow: 10px 5px 5px #34495e;
    }
    .stDownloadButton>button {
        background-color: #34495e;
        color: white;
        box-shadow: 10px 5px 5px #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
# 🧬 EFFET FONDATEUR - Interface Web d’Analyse Génomique
Bienvenue dans l'application de traitement bioinformatique pour la mise en evidence de **l'effet fondateur d'une mutation**. Sélectionnez vos fichiers d'entrée et choisissez les étapes à exécuter.

Vous pouvez également consulter la documentation complète ci-dessous ou la télécharger.
""")

st.sidebar.header("⚙️ Paramètres du pipeline")

# Upload fichiers
raw_file = st.sidebar.file_uploader("📄 Charger le fichier .raw", type="raw")
map_file = st.sidebar.file_uploader("📄 Charger le fichier .map", type="map")

# Étapes sélectionnées
step = st.sidebar.selectbox("🔁 Choisir une étape à exécuter", ["all", "roh", "ibd", "adegenet", "gamma"])
debug = st.sidebar.checkbox("🛠️ Mode débogage")

# Bouton lancer
if st.sidebar.button("🚀 Lancer l’analyse"):
    if not raw_file or not map_file:
        st.sidebar.error("❌ Merci de charger les fichiers .raw et .map")
    else:
        os.makedirs("temp", exist_ok=True)
        raw_path = os.path.join("temp", raw_file.name)
        map_path = os.path.join("temp", map_file.name)
        with open(raw_path, "wb") as f: f.write(raw_file.read())
        with open(map_path, "wb") as f: f.write(map_file.read())

        cmd = f"python pipeline_dock6.py --step {step}"
        if debug:
            cmd += " --debug"
        st.sidebar.code(f"Commande lancée : {cmd}")

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            st.sidebar.success("✅ Pipeline terminé")
            with st.expander("🧾 Afficher les logs du pipeline"):
                st.text(result.stdout)
        except Exception as e:
            st.sidebar.error(f"❌ Erreur d'exécution : {e}")

# Affichage du README
st.markdown("## 📘 Documentation du pipeline")
readme_path = "README_DOCK6_PIPELINE.md"
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        st.download_button("📥 Télécharger le README", f, file_name="README_DOCK6_PIPELINE.md")

    with open(readme_path, "r", encoding="utf-8") as f:
        with st.expander("📖 Lire la documentation directement dans l'app"):
            st.markdown(f.read(), unsafe_allow_html=True)
else:
    st.warning("README introuvable à la racine du projet.")

# Résultats par onglets
st.markdown("## 📊 Résultats d’analyse")
tabs = st.tabs(["🧬 Résumé Gamma", "📈 Graphique Gamma", "📄 Rapport PDF"])

# Gamma - résumé
gamma_output = "data/output/gamma_results/gamma_output.txt"
with tabs[0]:
    if os.path.exists(gamma_output):
        with open(gamma_output) as f:
            lines = [l.strip() for l in f if "Mean generations" in l or "Confidence interval" in l]
            st.markdown("### 🔬 Résumé Gamma")
            st.success("\n".join(lines))
    else:
        st.warning("Aucun résultat Gamma disponible.")

# Gamma - graphique
freq_png = "data/output/gamma_results/frequence_allelique.png"
with tabs[1]:
    if os.path.exists(freq_png):
        st.image(Image.open(freq_png), caption="🎯 Fréquence des SNPs pour Gamma", use_column_width=True)
    else:
        st.warning("Graphique de fréquence allélique non trouvé.")

# Rapport PDF
pdf_path = "data/output/rapport_complet_pipeline.pdf"
with tabs[2]:
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Télécharger le rapport complet (PDF)", f, file_name="rapport_complet_pipeline.pdf")
    else:
        st.warning("Rapport PDF non disponible.")

