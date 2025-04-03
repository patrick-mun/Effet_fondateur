"""
Pipeline d’analyse de l’effet fondateur (DOCK6)
------------------------------------------------
Auteur     : Patrick MUNIER
Version    : 1.0
Description: Ce script exécute une analyse génétique complète à partir de fichiers SNP pour détecter
             un effet fondateur autour d’une mutation. Il utilise PLINK, KING, Adegenet et Gamma pour :
             - Identifier les segments ROH
             - Détecter les liens familiaux (IBD)
             - Analyser la structure populationnelle
             - Dater la mutation par déséquilibre de liaison
             Il génère également des fichiers d’entrée, graphiques et rapports PDF.

Dépendances:
 - Python 3.x
 - pandas
 - matplotlib
 - fpdf
 - PLINK, KING, R (adegenet), Gamma (installés séparément)
 - Fichiers d’entrée: .raw, .map, .ped, .bed, .bim, .fam

Fichiers de sortie générés automatiquement:
 - `output/pipeline_execution.log` : journal complet de l'exécution
 - `output/roh_results/` : fichiers PLINK de segments ROH
 - `output/ibd_results/` : résultats KING (liens familiaux, fichiers .kin)
 - `output/adegenet_results/` :
     - Graphiques .png générés par adegenet
     - `rapport_graphique_adegenet.pdf` : rapport compilant tous les graphiques
 - `output/gamma_results/` :
     - `genotype_data.gamma_input.txt` : fichier d'entrée pour Gamma
     - `frequence_allelique.png` : graphique des fréquences alléliques
     - `rapport_gamma.pdf` : rapport PDF incluant statistiques et graphe

Usage :
    python pipeline_dock6.py
"""

import subprocess
import os
import platform
import logging
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# Chemins globaux dynamiques
base_dir = os.path.abspath(os.path.dirname(__file__))
input_data = os.path.join(base_dir, "../data/input/genotype_data")
output_data = os.path.join(base_dir, "../data/output")
script_dir = os.path.join(base_dir, "../scripts")
log_file = os.path.join(output_data, "pipeline_execution.log")

# Configuration du mode debug avec sortie vers fichier log
DEBUG = True
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Assure que tous les dossiers existent
os.makedirs(output_data, exist_ok=True)

# Détection du système d'exploitation
is_macos = platform.system() == "Darwin"
is_linux = platform.system() == "Linux"

# Vérifie que les scripts existent
# ---------------------------------------------------------
def check_script_exists(script_path):
    if not os.path.isfile(script_path):
        logging.critical(f"Le fichier requis est introuvable : {script_path}")
        raise FileNotFoundError(script_path)

# Exécution des commandes externes via subprocess
# ---------------------------------------------------------
def run_command(cmd):
    logging.debug(f"Exécution de la commande : {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.debug(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur dans la commande : {cmd}\n{e.stderr}")
        raise

# Génère le fichier gamma_input.txt, un graphique et un rapport PDF
# ---------------------------------------------------------
def generate_gamma_input(raw_file_path, map_file_path, output_file):
    logging.info("Génération du fichier gamma_input.txt")

    # Vérifie l'existence des fichiers source
    if not os.path.exists(raw_file_path) or not os.path.exists(map_file_path):
        logging.critical("Fichiers .raw ou .map introuvables pour la génération.")
        raise FileNotFoundError("Fichier requis manquant.")

    # Lecture du fichier .raw contenant les génotypes (codés 0, 1, 2)
    raw_df = pd.read_csv(raw_file_path, delim_whitespace=True)
    # Lecture du fichier .map avec les positions génétiques des SNPs
    map_df = pd.read_csv(map_file_path, delim_whitespace=True, header=None,
                         names=["chr", "snp", "gen_dist", "phys_pos"])

    # Sélectionne les colonnes correspondant aux SNPs (exclut les métadonnées)
    snps = [col for col in raw_df.columns if col not in ["FID", "IID", "PAT", "MAT", "SEX", "PHENOTYPE"]]
    data = []

    # Parcourt chaque SNP pour calculer la fréquence allélique et le filtrer
    for snp in snps:
        map_row = map_df[map_df['snp'] == snp]
        if map_row.empty:
            continue
        cM = map_row.iloc[0]['gen_dist']
        allele_sum = raw_df[snp].sum()
        allele_freq = allele_sum / (2 * len(raw_df))  # Fréquence de l'allèle 1
        if 0 < allele_freq < 1 and raw_df[snp].var() > 0:
            data.append((snp, cM, allele_freq))

    # Crée le DataFrame final et sauvegarde au format .txt (TSV)
    gamma_df = pd.DataFrame(data, columns=["SNP", "Position_cM", "Freq_Allèle_1"])
    gamma_df.to_csv(output_file, sep='\t', index=False)
    logging.info(f"Fichier gamma_input.txt généré : {output_file}")

    # Génère un graphique de la fréquence allélique par position
    plt.figure(figsize=(10, 5))
    plt.scatter(gamma_df['Position_cM'], gamma_df['Freq_Allèle_1'], alpha=0.6, edgecolors='k')
    plt.title("Fréquences alléliques des SNPs retenus pour Gamma")
    plt.xlabel("Position (cM)")
    plt.ylabel("Fréquence de l'allèle 1")
    plt.grid(True)
    plot_path = os.path.join(os.path.dirname(output_file), "frequence_allelique.png")
    plt.savefig(plot_path)
    plt.close()
    logging.info(f"Graphique des fréquences alléliques sauvegardé : {plot_path}")

    # Calcule les statistiques descriptives pour le PDF
    n_snps = len(gamma_df)
    freq_mean = gamma_df['Freq_Allèle_1'].mean()
    freq_min = gamma_df['Freq_Allèle_1'].min()
    freq_max = gamma_df['Freq_Allèle_1'].max()

    # Génère un rapport PDF contenant le graphique et les statistiques
    pdf_path = os.path.join(os.path.dirname(output_file), "rapport_gamma.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Rapport - Fréquences alléliques pour Gamma", ln=True, align='C')
    pdf.ln(10)
    pdf.image(plot_path, x=10, w=180)
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=(
        f"Nombre total de SNPs informatifs : {n_snps}\n"
        f"Fréquence moyenne de l'allèle 1 : {freq_mean:.3f}\n"
        f"Fréquence minimale : {freq_min:.3f}\n"
        f"Fréquence maximale : {freq_max:.3f}"
    ))
    pdf.output(pdf_path)
    logging.info(f"Rapport PDF généré : {pdf_path}")

# Étapes du pipeline
# ---------------------------------------------------------

def run_roh():
    # Lance l'étape ROH avec PLINK
    logging.info("Étape 1 : Analyse ROH avec PLINK")
    cmd = f"bash {os.path.join(script_dir, 'commands_pipeline_dock6.sh')}"
    run_command(cmd)

def run_ibd():
    # Lance l'étape IBD avec KING
    logging.info("Étape 2 : Analyse IBD avec KING")
    cmd = f"bash {os.path.join(script_dir, 'commands_pipeline_dock6.sh')}"
    run_command(cmd)

def run_adegenet():
    # Lance l'analyse de structure avec R et adegenet
    logging.info("Étape 3 : Analyse de structure avec adegenet")
    cmd = f"Rscript {os.path.join(script_dir, 'adegenet_analysis.R')}"
    run_command(cmd)

    # Déplace tous les fichiers .png et .pdf générés dans le dossier de sortie dédié
    adegenet_output_dir = os.path.join(output_data, "adegenet_results")
    os.makedirs(adegenet_output_dir, exist_ok=True)

    for file in os.listdir(script_dir):
        if file.endswith(".png") or file.endswith(".pdf"):
            src = os.path.join(script_dir, file)
            dst = os.path.join(adegenet_output_dir, file)
            os.rename(src, dst)
            logging.info(f"Graphique adegenet déplacé : {dst}")

    # Génère un rapport PDF regroupant tous les graphiques .png
    from fpdf import FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Rapport des graphiques Adegenet", ln=True, align='C')
    pdf.ln(10)

    added = 0
    for file in sorted(os.listdir(adegenet_output_dir)):
        if file.endswith(".png"):
            file_path = os.path.join(adegenet_output_dir, file)
            pdf.add_page()
            pdf.cell(0, 10, file, ln=True)
            pdf.image(file_path, x=10, w=180)
            added += 1

    if added > 0:
        pdf_output_path = os.path.join(adegenet_output_dir, "rapport_graphique_adegenet.pdf")
        pdf.output(pdf_output_path)
        logging.info(f"Rapport PDF des graphiques Adegenet généré : {pdf_output_path}")

def run_gamma():
    # Génère les fichiers pour Gamma, le graphique et le rapport, puis exécute Gamma
    logging.info("Étape 4 : Datation avec Gamma")
    raw_file = input_data + ".raw"
    map_file = input_data + ".map"
    gamma_input = os.path.join(os.path.dirname(input_data), "genotype_data.gamma_input.txt")
    generate_gamma_input(raw_file, map_file, gamma_input)
    cmd = f"bash {os.path.join(script_dir, 'commands_pipeline_dock6.sh')}"
    run_command(cmd)

# Fonction principale sécurisée
# ---------------------------------------------------------

def main():
    logging.info("🔬 Démarrage du pipeline d'analyse de l'effet fondateur (DOCK6)")
    logging.info("=" * 60)
    try:
        run_roh()
        run_ibd()
        run_adegenet()
        run_gamma()
    except Exception as e:
        logging.critical(f"Pipeline interrompu : {e}")
    else:
        logging.info("✅ Pipeline terminé avec succès !")
    finally:
        logging.info("🧪 Analyse finalisée")

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline d'analyse génétique pour effet fondateur (DOCK6)")
    parser.add_argument('--version', action='version', version='DOCK6 Pipeline 1.0')
    parser.add_argument('--step', type=str, choices=['roh', 'ibd', 'adegenet', 'gamma', 'all'], default='all',
                        help='Étape à exécuter : roh, ibd, adegenet, gamma, ou all')
    parser.add_argument('--debug', action='store_true', help='Activer le mode débogage')
    parser.add_argument('--resume', action='store_true', help='Reprendre une exécution précédente (non implémenté)')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Mode DEBUG activé")

    if args.step == 'roh':
        run_roh()
    elif args.step == 'ibd':
        run_ibd()
    elif args.step == 'adegenet':
        run_adegenet()
    elif args.step == 'gamma':
        run_gamma()
    elif args.step == 'all':
        main()
