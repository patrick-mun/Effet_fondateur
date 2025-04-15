import os
import sys
import tempfile
import pytest
import pandas as pd
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ld import run_ld

def test_run_ld_computes_r2_and_D(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        plink_prefix = os.path.join(tmpdir, "input/genotype_data")
        output_dir = os.path.join(tmpdir, "output")
        output_base = os.path.join(output_dir, "ld")

        os.makedirs(os.path.dirname(plink_prefix), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Simuler les fichiers .ped et .map
        open(plink_prefix + ".ped", "w").write("1 1 0 0 1 1\n")
        open(plink_prefix + ".map", "w").write("1 rs1 0 100\n")

        # Simuler sortie PLINK .ld avec r2, Dprime et MAFs
        ld_file = output_base + ".ld"
        df = pd.DataFrame({
            "SNP_A": ["rs1"],
            "SNP_B": ["rs2"],
            "R2": [0.8],
            "Dprime": [0.9],
            "MAF_A": [0.2],
            "MAF_B": [0.3]
        })
        df.to_csv(ld_file, sep=' ', index=False)

        # Mock subprocess.run pour éviter exécution réelle
        monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: None)

        # Exécution
        run_ld(plink_prefix, output_dir)

        # Vérifier le fichier enrichi
        result_file = output_base + "_with_D.csv"
        assert os.path.exists(result_file)
        df_result = pd.read_csv(result_file)
        assert "D" in df_result.columns
        assert pytest.approx(df_result["D"].iloc[0], 0.001) == 0.9 * min(0.2 * 0.7, 0.3 * 0.8)
