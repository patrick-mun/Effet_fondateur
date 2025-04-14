import os
import sys
import tempfile
import pytest
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing import run_preprocessing

def test_run_preprocessing_executes_all(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_prefix = os.path.join(tmpdir, "input/genotype_data")
        output_prefix = os.path.join(tmpdir, "output/geno")
        cas_file = os.path.join(tmpdir, "input/cas.txt")
        temoins_file = os.path.join(tmpdir, "input/temoins.txt")

        os.makedirs(os.path.dirname(input_prefix), exist_ok=True)
        os.makedirs(os.path.dirname(output_prefix), exist_ok=True)

        # Créer fichiers .ped et .map valides
        with open(input_prefix + ".ped", "w") as f:
            f.write("1 1 0 0 1 1\n")
        with open(input_prefix + ".map", "w") as f:
            f.write("1 rs1 0 100\n")
        with open(cas_file, "w") as f:
            f.write("1 1\n")
        with open(temoins_file, "w") as f:
            f.write("1 2\n")

        # Simuler .raw créé automatiquement pour validation
        with open(input_prefix + ".raw", "w") as f:
            f.write("FID IID PAT MAT SEX PHENOTYPE rs1\n1 1 0 0 1 1 2\n")

        # Mock subprocess.run pour éviter l'exécution réelle
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: None)

        # Créer manuellement tous les fichiers attendus après filtrage
        os.makedirs(os.path.dirname(output_prefix + "/filtered_data.raw"), exist_ok=True)
        with open(output_prefix + "/filtered_data.raw", "w") as f:
            f.write("FID IID PAT MAT SEX PHENOTYPE rs1\n1 1 0 0 1 1 2\n")
        with open(output_prefix + "/allele_frequencies.frq", "w") as f:
            f.write("CHR SNP A1 A2 MAF NCHROBS\n1 rs1 A T 0.1 100\n")
        with open(output_prefix + "/hwe.hwe", "w") as f:
            f.write("CHR SNP TEST A1 A2 GENO O(HET) E(HET) P\n1 rs1 ALL A T 1/1 1/2 2/2 0.2 0.3 0.05\n")

        # Exécuter la fonction
        run_preprocessing(input_prefix, output_prefix, cas_file, temoins_file)

        # Vérifier qu'un résumé a bien été généré
        summary_path = os.path.join(output_prefix, "summary_files.csv")
        assert os.path.exists(summary_path)
