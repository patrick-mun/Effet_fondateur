import os
import matplotlib.pyplot as plt
from reporting import generate_full_report
import pandas as pd

def create_fake_figure(path, title):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.figure()
    plt.plot([1, 2, 3], [4, 2, 5])
    plt.title(title)
    plt.savefig(path)
    plt.close()

def simulate():
    base_dir = "output"

    # Simule des figures en .png compatibles avec le rapport PDF
    create_fake_figure(os.path.join(base_dir, "roh", "roh_plot.png"), "ROH Test")
    create_fake_figure(os.path.join(base_dir, "ld", "ld_combined.png"), "LD combiné r² et D")
    create_fake_figure(os.path.join(base_dir, "gamma", "gamma_plot.png"), "Gamma Test")
    create_fake_figure(os.path.join(base_dir, "adegenet", "dapc_plot.png"), "DAPC")
    create_fake_figure(os.path.join(base_dir, "adegenet", "dapc_tree.png"), "Tree")
    create_fake_figure(os.path.join(base_dir, "adegenet", "dapc_hexp.png"), "Hobs Hexp")

    # Crée un fichier de synthèse simulé
    summary_path = os.path.join(base_dir, "summary.csv")
    df = pd.DataFrame([
        ["ROH", "Nombre moyen de ROH: 12", "Stable entre cas et témoins"],
        ["LD", "r² moyen: 0.21", "Baisse attendue"],
        ["Gamma", "Gamma moyen: 0.83", "Au-dessus du seuil"],
        ["DAPC", "Nb clusters: 3", "Différenciation visible"]
    ], columns=["Module", "Statistique", "Commentaire"])
    df.to_csv(summary_path, index=False)

    # Appel avec support du tableau récapitulatif
    generate_full_report(base_dir, "rapport_simule.pdf", "rapport_simule.html", summary_csv=summary_path)

if __name__ == "__main__":
    simulate()