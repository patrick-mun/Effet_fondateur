# ibd.py
"""
Module IBD : détection des relations de parenté génétiques via KING ou PLINK
"""
import os
import subprocess
import logging

def run_ibd_king(bed_prefix: str, output_dir: str):
    """
    Exécute KING pour détecter les relations IBD

    :param bed_prefix: chemin du fichier binaire PLINK (sans extension)
    :param output_dir: dossier où stocker les résultats
    """
    os.makedirs(output_dir, exist_ok=True)
    output_prefix = os.path.join(output_dir, "ibd_king")

    cmd = f"king -b {bed_prefix}.bed --kinship --prefix {output_prefix}"

    try:
        logging.info(f"[IBD-KING] Commande exécutée : {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        logging.info("[IBD-KING] Analyse KING terminée avec succès.")
    except subprocess.CalledProcessError as e:
        logging.error(f"[IBD-KING] Erreur lors de l'exécution : {e}")
        raise

def run_ibd_plink(bed_prefix: str, output_dir: str):
    """
    Exécute PLINK pour détecter les relations IBD (pi-hat)

    :param bed_prefix: chemin du fichier binaire PLINK (sans extension)
    :param output_dir: dossier où stocker les résultats
    """
    os.makedirs(output_dir, exist_ok=True)
    output_prefix = os.path.join(output_dir, "ibd_plink")

    cmd = f"plink --bfile {bed_prefix} --genome --out {output_prefix}"

    try:
        logging.info(f"[IBD-PLINK] Commande exécutée : {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        logging.info("[IBD-PLINK] Analyse PLINK terminée avec succès.")
    except subprocess.CalledProcessError as e:
        logging.error(f"[IBD-PLINK] Erreur lors de l'exécution : {e}")
        raise
