import os
import sys
import csv
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessing import check_outputs

def test_check_outputs_cree_csv():
    # Créer un fichier existant temporaire
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, "present.txt")
        f2 = os.path.join(tmpdir, "missing.txt")

        # Fichier présent
        with open(f1, "w") as f:
            f.write("test")

        # Liste de fichiers à vérifier
        files = [f1, f2]
        summary_csv = os.path.join(tmpdir, "summary.csv")

        # Exécuter la fonction
        check_outputs(files, summary_csv)

        # Lire le fichier CSV généré
        with open(summary_csv, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["fichier"] == f1
        assert rows[0]["existe"] == "True"
        assert rows[1]["fichier"] == f2
        assert rows[1]["existe"] == "False"