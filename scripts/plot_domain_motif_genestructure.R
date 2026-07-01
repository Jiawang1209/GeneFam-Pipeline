args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 6) {
  stop("Usage: Rscript plot_domain_motif_genestructure.R <treefile> <label_map.tsv> <motif_locations.tsv> <domain_locations.tsv> <gene_structure_tracks.tsv> <outdir>")
}

treefile <- args[[1]]
label_map_file <- args[[2]]
motif_file <- args[[3]]
domain_file <- args[[4]]
structure_file <- args[[5]]
outdir <- args[[6]]

required_packages <- c("ggtree", "treeio", "ggplot2", "gggenes", "aplot")
missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages) > 0) {
  stop(paste("Missing required R packages:", paste(missing_packages, collapse = ", ")))
}
suppressPackageStartupMessages({
  library(ggtree)
  library(treeio)
  library(ggplot2)
  library(gggenes)
  library(aplot)
})

plots_dir <- file.path(outdir, "plots")
dir.create(plots_dir, recursive = TRUE, showWarnings = FALSE)

read_required <- function(path) {
  if (!file.exists(path)) {
    stop(paste("Input file does not exist:", path))
  }
  read.delim(path, check.names = FALSE, stringsAsFactors = FALSE)
}

label_map <- read_required(label_map_file)
motif <- read_required(motif_file)
domain <- read_required(domain_file)
structure <- read_required(structure_file)
sequence_lengths_file <- file.path(outdir, "tables", "sequence_lengths.tsv")
sequence_lengths <- read_required(sequence_lengths_file)
tree <- treeio::read.newick(treefile, node.label = "support")
tree_base <- ggtree::ggtree(tree, branch.length = "none")
tree_labels <- ggtree::get_taxa_name(tree_base)
tip_positions <- tree_base$data[tree_base$data$isTip, c("label", "y"), drop = FALSE]
names(tip_positions) <- c("gene_id", "plot_y")
gene_levels <- rev(tree_labels)

label_info <- label_map[, c("tree_label", "gene_id", "species_id"), drop = FALSE]
names(label_info)[1] <- "label"

coerce_track <- function(df, id_col = "gene_id") {
  if (nrow(df) == 0) {
    return(df)
  }
  df$gene_id <- as.character(df[[id_col]])
  df$start <- suppressWarnings(as.numeric(df$start))
  df$end <- suppressWarnings(as.numeric(df$end))
  df <- merge(df, tip_positions, by = "gene_id", all.x = TRUE, sort = FALSE)
  df <- df[!is.na(df$plot_y) & !is.na(df$start) & !is.na(df$end), , drop = FALSE]
  df
}

motif <- coerce_track(motif)
domain <- coerce_track(domain)
structure <- coerce_track(structure)
sequence_lengths$gene_id <- as.character(sequence_lengths$gene_id)
sequence_lengths$protein_length <- suppressWarnings(as.numeric(sequence_lengths$protein_length))
sequence_lengths <- merge(sequence_lengths, tip_positions, by = "gene_id", all.x = TRUE, sort = FALSE)
sequence_lengths <- sequence_lengths[!is.na(sequence_lengths$plot_y) & !is.na(sequence_lengths$protein_length), , drop = FALSE]
if (nrow(motif) > 0) {
  motif$motif_id <- factor(motif$motif_id, levels = sort(unique(motif$motif_id)), ordered = TRUE)
}
if (nrow(domain) > 0) {
  domain$domain_id <- factor(domain$domain_id, levels = sort(unique(domain$domain_id)), ordered = TRUE)
}
if (nrow(structure) > 0) {
  structure$feature <- factor(structure$feature, levels = c("gene", "five_prime_UTR", "three_prime_UTR", "exon", "CDS"), ordered = TRUE)
}

palette <- c(
  "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99",
  "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a",
  "#ffff99", "#b15928", "#ffffb3", "#bebada", "#fb8072"
)

tree_p <- ggtree::ggtree(tree, branch.length = "none", size = 0.35, color = "#969696") %<+% label_info +
  ggtree::geom_nodepoint(
    ggplot2::aes(fill = cut(ifelse(as.numeric(support) <= 1, as.numeric(support) * 100, as.numeric(support)), c(0, 50, 75, 100))),
    shape = 21,
    size = 1.4,
    stroke = 0.25,
    na.rm = TRUE
  ) +
  ggplot2::scale_fill_manual(
    values = c("black", "grey70", "white"),
    guide = "legend",
    name = "Bootstrap Percentage(BP)",
    breaks = c("(75,100]", "(50,75]", "(0,50]"),
    labels = c("BP > 75", "50 < BP <= 75", "BP <= 50")
  ) +
  ggtree::geom_tiplab(ggplot2::aes(label = gene_id), size = 2.8, offset = 0.35) +
  ggplot2::ggtitle("Phylogenetic Tree") +
  ggtree::xlim_tree(28) +
  ggtree::theme_tree() +
  ggplot2::theme(
    plot.title = ggplot2::element_text(hjust = 0.5),
    legend.background = ggplot2::element_rect(color = "#969696", fill = "#d9d9d9")
  )

track_theme <- gggenes::theme_genes() +
  ggplot2::theme(
    axis.text.y = ggplot2::element_blank(),
    axis.ticks.y = ggplot2::element_blank(),
    plot.title = ggplot2::element_text(hjust = 0.5),
    legend.background = ggplot2::element_rect(color = "#969696", fill = "#d9d9d9")
  )

motif_p <- ggplot2::ggplot(motif, ggplot2::aes(xmin = start, xmax = end, y = plot_y, fill = motif_id)) +
  gggenes::geom_gene_arrow(arrowhead_height = grid::unit(3, "mm"), arrowhead_width = grid::unit(0.1, "mm")) +
  ggplot2::scale_fill_manual(values = rep(palette, length.out = max(1, length(unique(motif$motif_id)))), name = "Motif") +
  ggplot2::labs(x = "", y = "") +
  ggplot2::ggtitle("Motif Analysis") +
  track_theme

domain_p <- ggplot2::ggplot(domain, ggplot2::aes(xmin = start, xmax = end, y = plot_y, fill = domain_id)) +
  gggenes::geom_gene_arrow(arrowhead_height = grid::unit(3, "mm"), arrowhead_width = grid::unit(0.1, "mm")) +
  ggplot2::scale_fill_manual(values = rep(palette, length.out = max(1, length(unique(domain$domain_id)))), name = "Domain") +
  ggplot2::labs(x = "", y = "") +
  ggplot2::ggtitle("Domain Analysis") +
  track_theme

gene_structure_p <- ggplot2::ggplot(structure, ggplot2::aes(xmin = start, xmax = end, y = plot_y, fill = feature)) +
  gggenes::geom_gene_arrow(arrowhead_height = grid::unit(3, "mm"), arrowhead_width = grid::unit(0.1, "mm")) +
  ggplot2::scale_fill_manual(
    values = c(gene = "#d9d9d9", five_prime_UTR = "#66c2ff", three_prime_UTR = "#ff9999", exon = "#b2df8a", CDS = "#ffb700"),
    name = "Gene Structure",
    na.value = "#969696"
  ) +
  ggplot2::labs(x = "", y = "") +
  ggplot2::ggtitle("Gene Structure") +
  track_theme

full_track_theme <- ggplot2::theme_bw() +
  ggplot2::theme(
    axis.text.y = ggplot2::element_blank(),
    axis.ticks.y = ggplot2::element_blank(),
    panel.grid = ggplot2::element_blank(),
    plot.title = ggplot2::element_text(hjust = 0.5),
    legend.background = ggplot2::element_rect(color = "#969696", fill = "#d9d9d9")
  )

domain_full_p <- ggplot2::ggplot() +
  ggplot2::geom_segment(
    data = sequence_lengths,
    ggplot2::aes(x = 0, xend = protein_length, y = plot_y, yend = plot_y),
    color = "gray60",
    linewidth = 0.8
  ) +
  ggplot2::geom_rect(
    data = domain,
    ggplot2::aes(xmin = start, xmax = end, ymin = plot_y - 0.25, ymax = plot_y + 0.25, fill = domain_id),
    color = "black",
    linewidth = 0.3
  ) +
  ggplot2::scale_fill_manual(values = rep(palette, length.out = max(1, length(unique(domain$domain_id)))), name = "Domain") +
  ggplot2::labs(x = "Relative position (aa)", y = "") +
  ggplot2::ggtitle("Domain Analysis") +
  full_track_theme

motif_full_p <- ggplot2::ggplot() +
  ggplot2::geom_segment(
    data = sequence_lengths,
    ggplot2::aes(x = 0, xend = protein_length, y = plot_y, yend = plot_y),
    color = "gray60",
    linewidth = 0.8
  ) +
  ggplot2::geom_rect(
    data = motif,
    ggplot2::aes(xmin = start, xmax = end, ymin = plot_y - 0.25, ymax = plot_y + 0.25, fill = motif_id),
    color = "black",
    linewidth = 0.3
  ) +
  ggplot2::scale_fill_manual(values = rep(palette, length.out = max(1, length(unique(motif$motif_id)))), name = "Motif") +
  ggplot2::labs(x = "Relative position (aa)", y = "") +
  ggplot2::ggtitle("Motif Analysis") +
  full_track_theme

structure_base <- structure[structure$feature == "gene", , drop = FALSE]
gene_structure_full_p <- ggplot2::ggplot() +
  ggplot2::geom_segment(
    data = structure_base,
    ggplot2::aes(x = 0, xend = end, y = plot_y, yend = plot_y),
    color = "gray60",
    linewidth = 0.8
  ) +
  ggplot2::geom_rect(
    data = structure[structure$feature == "five_prime_UTR", , drop = FALSE],
    ggplot2::aes(xmin = start, xmax = end, ymin = plot_y - 0.25, ymax = plot_y + 0.25),
    fill = "#66c2ff",
    color = "black",
    linewidth = 0.3
  ) +
  ggplot2::geom_rect(
    data = structure[structure$feature == "three_prime_UTR", , drop = FALSE],
    ggplot2::aes(xmin = start, xmax = end, ymin = plot_y - 0.25, ymax = plot_y + 0.25),
    fill = "#ff9999",
    color = "black",
    linewidth = 0.3
  ) +
  ggplot2::geom_rect(
    data = structure[structure$feature == "CDS", , drop = FALSE],
    ggplot2::aes(xmin = start, xmax = end, ymin = plot_y - 0.4, ymax = plot_y + 0.4),
    fill = "#ffb700",
    color = "black",
    linewidth = 0.3
  ) +
  ggplot2::labs(x = "Relative position (bp)", y = "") +
  ggplot2::ggtitle("Gene Structure") +
  full_track_theme

combined <- tree_p %>%
  aplot::insert_right(domain_p, width = 0.9) %>%
  aplot::insert_right(motif_p, width = 0.9) %>%
  aplot::insert_right(gene_structure_p, width = 1.0)

combined_full <- tree_p %>%
  aplot::insert_right(domain_full_p, width = 0.9) %>%
  aplot::insert_right(motif_full_p, width = 0.9) %>%
  aplot::insert_right(gene_structure_full_p, width = 1.0)

height <- max(6, 0.28 * length(gene_levels) + 3.5)
ggplot2::ggsave(file.path(plots_dir, "tree_domain_motif_genestructure.pdf"), combined, width = 18, height = height, limitsize = FALSE)
ggplot2::ggsave(file.path(plots_dir, "tree_domain_motif_genestructure.png"), combined, width = 18, height = height, dpi = 180, limitsize = FALSE)
ggplot2::ggsave(file.path(plots_dir, "tree_domain_motif_genestructure_full_length.pdf"), combined_full, width = 18, height = height, limitsize = FALSE)
ggplot2::ggsave(file.path(plots_dir, "tree_domain_motif_genestructure_full_length.png"), combined_full, width = 18, height = height, dpi = 180, limitsize = FALSE)
