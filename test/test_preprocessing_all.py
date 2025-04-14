import os
import sys
import tempfile
import csv
import pandas as pd
import pytest
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing import (
    check_input_files_exist,
    validate_raw_format,
    check_outputs,
    generate_qc_plots,
    run_preprocessing
)

def test_preprocessing_global(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_prefix = os.path.join(tmpdir, "input/genotype_data")
        output_prefix = os.path.join(tmpdir, "output/geno")
        cas_file = os.path.join(tmpdir, "input/cas.txt")
        temoins_file = os.path.join(tmpdir, "input/temoins.txt")

        os.makedirs(os.path.dirname(input_prefix), exist_ok=True)
        os.makedirs(os.path.dirname(output_prefix), exist_ok=True)

        # Fichiers d'entrée de base
        with open(input_prefix + ".ped", "w") as f:
            f.write("1 1 0 0 1 1\n")
        with open(input_prefix + ".map", "w") as f:
            f.write("1 rs1 0 100\n")
        with open(input_prefix + ".raw", "w") as f:
            f.write("FID IID PAT MAT SEX PHENOTYPE rs1\n1 1 0 0 1 1 2\n")
        with open(cas_file, "w") as f:
            f.write("1 1\n")
        with open(temoins_file, "w") as f:
            f.write("1 2\n")

        # Mock subprocess.run
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: None)

        # Vérification fichiers d'entrée
        check_input_files_exist(input_prefix)
        validate_raw_format(input_prefix + ".raw")

        # Simulation des fichiers générés (création dossier si nécessaire)
        os.makedirs(output_prefix, exist_ok=True)
        with open(output_prefix + "/filtered_data.raw", "w") as f:
            f.write("FID IID PAT MAT SEX PHENOTYPE rs1\n1 1 0 0 1 1 2\n")
        with open(output_prefix + "/allele_frequencies.frq", "w") as f:
            f.write("CHR SNP A1 A2 MAF NCHROBS\n1 rs1 A T 0.1 100\n")
        with open(output_prefix + "/hwe.hwe", "w") as f:
            f.write("CHR SNP TEST A1 A2 GENO O(HET) E(HET) P\n1 rs1 ALL A T 1/1 1/2 2/2 0.2 0.3 0.05\n")

        # Vérification de check_outputs
        files_to_check = [
            output_prefix + "/filtered_data.raw",
            output_prefix + "/allele_frequencies.frq",
            output_prefix + "/hwe.hwe"
        ]
        summary_csv = output_prefix + "/summary_test.csv"
        check_outputs(files_to_check, summary_csv)
        assert os.path.exists(summary_csv)

        # Graphiques
        generate_qc_plots(output_prefix)
        assert os.path.exists(output_prefix + "/qc_maf_distribution.png")
        assert os.path.exists(output_prefix + "/qc_hwe_pvalues.png")

        # Exécution globale
        run_preprocessing(input_prefix, output_prefix, cas_file, temoins_file)
        assert os.path.exists(os.path.join(output_prefix, "summary_files.csv"))
