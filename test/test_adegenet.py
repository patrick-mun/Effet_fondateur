import os
import sys
import tempfile
from adegenet import generate_adegenet_script

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_generate_adegenet_script_cree_script_r():
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_path = os.path.join(tmpdir, "data.raw")
        group_path = os.path.join(tmpdir, "group.txt")
        output_dir = os.path.join(tmpdir, "adegenet_out")

        # Simuler fichiers .raw et group.txt
        with open(raw_path, "w") as f:
            f.write("FID IID PAT MAT SEX PHENOTYPE rs1 rs2\n")
            f.write("1 1 0 0 1 1 0 2\n")
        with open(group_path, "w") as f:
            f.write("1 1 A\n")

        script_path = generate_adegenet_script(raw_path, group_path, output_dir)

        assert os.path.exists(script_path)
        with open(script_path) as f:
            content = f.read()
            assert "dapc_res <- dapc" in content
            assert "pdf('" in content
            assert "df2genind" in content
            assert "barplot(basic_stats$Hobs" in content
