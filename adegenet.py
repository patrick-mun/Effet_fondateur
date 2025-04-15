# adegenet.py
"""
Module adegenet : génération et exécution d'un script R pour analyse DAPC, structure, et arbre phylogénétique via adegenet
"""
import os
import subprocess
import logging

def generate_adegenet_script(raw_path: str, group_file: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    script_path = os.path.join(output_dir, "adegenet_dapc.R")
    pdf_output = os.path.join(output_dir, "dapc_plot.pdf")
    tree_output = os.path.join(output_dir, "dapc_tree.pdf")
    hexp_output = os.path.join(output_dir, "dapc_hexp.pdf")
    genin_path = os.path.join(output_dir, "genin.csv")
    genpop_path = os.path.join(output_dir, "genpop.txt")

    script_content = f"""
    library(adegenet)
    library(ggplot2)
    library(ape)
    library(ade4)

    # Lecture des données et génération genind/genpop
    geno <- read.table('{raw_path}', header=TRUE)
    groups <- read.table('{group_file}', header=FALSE)
    data <- geno[, 7:ncol(geno)]
    rownames(data) <- geno$IID

    write.table(data, file="{genin_path}", sep=",", quote=FALSE, col.names=NA)
    grps <- as.factor(groups$V3[match(geno$IID, groups$V2)])
    write.table(grps, file="{genpop_path}", row.names=FALSE, col.names=FALSE, quote=FALSE)

    genind_obj <- df2genind(data, ploidy=2, ind.names=geno$IID)
    pop(genind_obj) <- grps

    # DAPC
    dapc_res <- dapc(genind_obj, n.pca=10, n.da=2)
    pdf('{pdf_output}')
    scatter(dapc_res)
    dev.off()

    # Arbre phylogénétique
    pdf('{tree_output}')
    myTree <- nj(dist(genind_obj))
    plot(myTree, main="Neighbour-Joining Tree")
    dev.off()

    # Hobs vs Hexp
    pdf('{hexp_output}')
    basic_stats <- summary(genind_obj)
    barplot(basic_stats$Hobs, beside=TRUE, col="skyblue", main="Hobs par population")
    barplot(basic_stats$Hexp, beside=TRUE, col="orange", main="Hexp par population")
    dev.off()
    """

    with open(script_path, "w") as f:
        f.write(script_content)

    logging.info(f"[adegenet] Script R généré : {script_path}")
    return script_path

def run_adegenet_script(script_path: str):
    cmd = f"Rscript {script_path}"
    try:
        logging.info(f"[adegenet] Exécution R : {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        logging.info("[adegenet] Analyse R terminée.")
    except subprocess.CalledProcessError as e:
        logging.error(f"[adegenet] Erreur R : {e}")
        raise
