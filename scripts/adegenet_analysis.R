library(adegenet)
library(poppr)
library(ape)

# Lecture des donnees
data <- read.PLINK("../data/input/genotype_data.raw")

# Analyse DAPC
dapc1 <- dapc(data)
png("../data/output/adegenet_results/dapc.png")
scatter(dapc1)
dev.off()

# Distance genetique
distgen <- dist(tab(data))
write.csv(as.matrix(distgen), "../data/output/adegenet_results/distance_matrix.csv")

# Arbre phylogenetique
tree <- nj(distgen)
png("../data/output/adegenet_results/phylo_tree.png")
plot(tree, typ='fan', cex=0.7)
dev.off()
write.tree(tree, file="../data/output/adegenet_results/tree.newick")
