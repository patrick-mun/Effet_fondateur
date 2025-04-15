import os
import sys
import tempfile
import pytest
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from roh import run_roh

def test_run_roh_executes_plink(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        plink_prefix = os.path.join(tmpdir, "input/genotype_data")
        output_dir = os.path.join(tmpdir, "output")

        os.makedirs(os.path.dirname(plink_prefix), exist_ok=True)

        # Créer des fichiers d'entrée simulés (même si non utilisés car subprocess est mocké)
        open(plink_prefix + ".ped", "w").write("1 1 0 0 1 1\n")
        open(plink_prefix + ".map", "w").write("1 rs1 0 100\n")

        # Mock de subprocess.run
        called = {}
        def fake_run(cmd, shell, check):
            called['cmd'] = cmd
            return 0

        monkeypatch.setattr("subprocess.run", fake_run)

        # Exécuter
        run_roh(plink_prefix, output_dir)

        expected_cmd = f"plink --file {plink_prefix} --homozyg --out {os.path.join(output_dir, 'roh')}"
        assert called['cmd'] == expected_cmd
