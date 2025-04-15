import os
import sys
import tempfile
import pytest
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ibd import run_ibd_king, run_ibd_plink

def test_run_ibd_king_executes_king(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        bed_prefix = os.path.join(tmpdir, "input/genotype_data")
        output_dir = os.path.join(tmpdir, "output")

        os.makedirs(os.path.dirname(bed_prefix), exist_ok=True)
        for ext in [".bed", ".bim", ".fam"]:
            open(bed_prefix + ext, "w").write("")

        called = {}
        monkeypatch.setattr("subprocess.run", lambda cmd, shell, check: called.update({"cmd": cmd}))

        run_ibd_king(bed_prefix, output_dir)

        expected_cmd = f"king -b {bed_prefix}.bed --kinship --prefix {os.path.join(output_dir, 'ibd_king')}"
        assert called['cmd'] == expected_cmd

def test_run_ibd_plink_executes_plink(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        bed_prefix = os.path.join(tmpdir, "input/genotype_data")
        output_dir = os.path.join(tmpdir, "output")

        os.makedirs(os.path.dirname(bed_prefix), exist_ok=True)
        for ext in [".bed", ".bim", ".fam"]:
            open(bed_prefix + ext, "w").write("")

        called = {}
        monkeypatch.setattr("subprocess.run", lambda cmd, shell, check: called.update({"cmd": cmd}))

        run_ibd_plink(bed_prefix, output_dir)

        expected_cmd = f"plink --bfile {bed_prefix} --genome --out {os.path.join(output_dir, 'ibd_plink')}"
        assert called['cmd'] == expected_cmd