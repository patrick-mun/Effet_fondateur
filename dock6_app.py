
import streamlit as st
import os
import subprocess
from PIL import Image

st.set_page_config(page_title="DOCK6 - Analyse Effet Fondateur", layout="wide")
st.title("🧬 DOCK6 - Interface Web d’Analyse Génomique")

st.sidebar.header("⚙️ Paramètres du pipeline")

# Upload fichiers
raw_file = st.sidebar.file_uploader("Charger le fichier .raw", type="raw")
map_file = st.sidebar.file_uploader("Charger le fichier .map", type="map")

# Étapes sélectionnées
step = st.sidebar.selectbox("Choisir une étape à exécuter", ["all", "roh", "ibd", "adegenet", "gamma"])

debug = st.sidebar.checkbox("Mode debug")

# Lancer le pipeline
if st.sidebar.button("🚀 Lancer l’analyse"):
    if not raw_file or not map_file:
        st.error("Merci de charger les fichiers .raw et .map")
    else:
        # Sauvegarde temporaire
        os.makedirs("temp", exist_ok=True)
        raw_path = os.path.join("temp", raw_file.name)
        map_path = os.path.join("temp", map_file.name)
        with open(raw_path, "wb") as f: f.write(raw_file.read())
        with open(map_path, "wb") as f: f.write(map_file.read())

        cmd = f"python pipeline_dock6.py --step {step}"
        if debug:
            cmd += " --debug"
        st.code(f"Commande lancée : {cmd}")

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            st.success("Pipeline terminé ✅")
            st.text(result.stdout)
        except Exception as e:
            st.error(f"Erreur : {e}")

# Résultats
st.subheader("📊 Résultats (extraits)")

col1, col2 = st.columns(2)

# Résumé Gamma
gamma_output = "data/output/gamma_results/gamma_output.txt"
if os.path.exists(gamma_output):
    with open(gamma_output) as f:
        lines = [l for l in f if "Mean generations" in l or "Confidence interval" in l]
        with col1:
            st.markdown("### Résumé Gamma")
            st.text("\n".join(lines))

# Graphique fréquence allélique
freq_png = "data/output/gamma_results/frequence_allelique.png"
if os.path.exists(freq_png):
    with col2:
        st.markdown("### Fréquences alléliques")
        st.image(Image.open(freq_png), caption="Fréquence des SNPs pour Gamma")

# Rapport PDF (lien téléchargement)
pdf_path = "data/output/rapport_complet_pipeline.pdf"
if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as f:
        st.download_button("📄 Télécharger le rapport complet", f, file_name="rapport_complet_pipeline.pdf")
