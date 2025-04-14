import os
import sys
import tempfile
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing import generate_qc_plots

def test_generate_qc_plots_cree_images():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Création d'un fichier .frq simulé
        frq_path = os.path.join(tmpdir, "allele_frequencies.frq")
        frq_df = pd.DataFrame({
            'CHR': [1, 1],
            'SNP': ['rs1', 'rs2'],
            'A1': ['A', 'G'],
            'A2': ['T', 'C'],
            'MAF': [0.1, 0.2],
            'NCHROBS': [200, 200]
        })
        frq_df.to_csv(frq_path, sep=' ', index=False)

        # Création d'un fichier .hwe simulé
        hwe_path = os.path.join(tmpdir, "hwe.hwe")
        hwe_df = pd.DataFrame({
            'CHR': [1, 1],
            'SNP': ['rs1', 'rs2'],
            'TEST': ['ALL', 'ALL'],
            'A1': ['A', 'G'],
            'A2': ['T', 'C'],
            'GENO': ['1/1 1/2 2/2', '1/1 1/2 2/2'],
            'O(HET)': [0.3, 0.4],
            'E(HET)': [0.25, 0.35],
            'P': [0.01, 0.05]
        })
        hwe_df.to_csv(hwe_path, sep=' ', index=False)

        # Appel de la fonction de tracé
        generate_qc_plots(tmpdir)

        # Vérification de la création des fichiers image
        maf_plot = os.path.join(tmpdir, "qc_maf_distribution.png")
        hwe_plot = os.path.join(tmpdir, "qc_hwe_pvalues.png")

        assert os.path.exists(maf_plot)
        assert os.path.exists(hwe_plot)
