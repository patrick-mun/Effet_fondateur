import os
import pytest
import shutil
from preprocessing import check_input_files_exist, validate_raw_format

@pytest.fixture
def setup_tmp_dir(tmp_path):
    # Création de fichiers d'entrée simulés : .ped, .map, .raw
    prefix = tmp_path / "test_data"
    ped_file = prefix.with_suffix(".ped")
    map_file = prefix.with_suffix(".map")
    raw_file = prefix.with_suffix(".raw")

    ped_file.write_text("1 1 0 0 1 1\n1 2 0 0 2 2\n")
    map_file.write_text("1 rs1 0 100\n1 rs2 0 200\n")
    raw_file.write_text("FID IID PAT MAT SEX PHENOTYPE rs1 rs2\n1 1 0 0 1 1 0 2\n")

    return str(prefix)

def test_check_input_files_exist_ok(setup_tmp_dir):
    check_input_files_exist(setup_tmp_dir)

def test_check_input_files_exist_fail(tmp_path):
    with pytest.raises(FileNotFoundError):
        check_input_files_exist(str(tmp_path / "missing_data"))

def test_validate_raw_format_ok(setup_tmp_dir):
    raw_path = f"{setup_tmp_dir}.raw"
    validate_raw_format(raw_path)

def test_validate_raw_format_fail(tmp_path):
    raw_path = tmp_path / "bad.raw"
    raw_path.write_text("INVALID CONTENT\n")
    with pytest.raises(Exception):
        validate_raw_format(str(raw_path))
