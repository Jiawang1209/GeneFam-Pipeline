args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_tree_features.R --args <tree_feature_matrix.tsv> <outdir>")
}

input <- args[[1]]
outdir <- args[[2]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

features <- read.delim(input, check.names = FALSE)
required <- c(
  "tree_order",
  "species_id",
  "gene_id",
  "gene_length",
  "exon_count",
  "cds_count",
  "domain_count",
  "best_domain_coverage",
  "motif_catalog_count",
  "motif_total_sites",
  "motif_mean_width"
)
missing <- setdiff(required, names(features))
if (length(missing) > 0) {
  stop(paste("Missing required columns:", paste(missing, collapse = ", ")))
}
if (nrow(features) == 0) {
  stop("No tree feature rows to plot")
}

features <- features[order(as.numeric(features$tree_order)), ]
numeric_cols <- c(
  "gene_length",
  "exon_count",
  "cds_count",
  "domain_count",
  "best_domain_coverage",
  "motif_catalog_count",
  "motif_total_sites",
  "motif_mean_width"
)
for (column in numeric_cols) {
  features[[column]] <- suppressWarnings(as.numeric(features[[column]]))
  features[[column]][is.na(features[[column]])] <- 0
}

scale01 <- function(values) {
  if (length(values) == 0 || max(values) == min(values)) {
    return(rep(0.5, length(values)))
  }
  (values - min(values)) / (max(values) - min(values))
}

draw_tree_features <- function() {
  layout(matrix(c(1, 2), nrow = 1), widths = c(2.8, 5.2))
  old_par <- par(no.readonly = TRUE)
  on.exit(par(old_par), add = TRUE)

  y <- seq_len(nrow(features))
  species <- factor(features$species_id)
  species_cols <- setNames(rainbow(length(levels(species)), s = 0.45, v = 0.85), levels(species))

  par(mar = c(4, 12, 3, 1))
  plot(
    rep(1, length(y)),
    y,
    type = "n",
    axes = FALSE,
    xlab = "",
    ylab = "",
    xlim = c(0.5, 1.8),
    ylim = c(0.5, length(y) + 0.5),
    main = "Tree-ordered genes"
  )
  segments(0.7, y, 1.0, y, col = "#777777")
  points(rep(1.05, length(y)), y, pch = 21, bg = species_cols[as.character(species)], col = "#333333", cex = 1.2)
  text(rep(1.15, length(y)), y, labels = features$gene_id, adj = 0, cex = 0.72)
  legend(
    "bottomleft",
    legend = levels(species),
    pt.bg = species_cols,
    pch = 21,
    bty = "n",
    cex = 0.65,
    title = "Species"
  )

  matrix_values <- rbind(
    scale01(features$gene_length),
    scale01(features$exon_count),
    scale01(features$cds_count),
    scale01(features$domain_count),
    scale01(features$best_domain_coverage),
    scale01(features$motif_total_sites)
  )
  rownames(matrix_values) <- c("Gene length", "Exons", "CDS", "Domains", "Best domain cov.", "Motif sites")
  palette <- colorRampPalette(c("#F7FBFF", "#9ECAE1", "#08519C"))(100)

  par(mar = c(4, 9, 3, 3))
  image(
    x = seq_len(ncol(matrix_values)),
    y = seq_len(nrow(matrix_values)),
    z = t(matrix_values),
    col = palette,
    axes = FALSE,
    xlab = "Tree-ordered genes",
    ylab = "",
    main = "Motif / gene structure / domain tracks"
  )
  axis(1, at = seq_len(nrow(features)), labels = features$gene_id, las = 2, cex.axis = 0.55)
  axis(2, at = seq_len(nrow(matrix_values)), labels = rownames(matrix_values), las = 1, cex.axis = 0.75)
  box()
  text(
    x = seq_len(nrow(features)),
    y = 6,
    labels = paste0("M", features$motif_catalog_count, "/w", sprintf("%.1f", features$motif_mean_width)),
    cex = 0.55
  )
}

pdf(file.path(outdir, "tree_features.pdf"), width = 12, height = max(5, 0.32 * nrow(features) + 3))
draw_tree_features()
dev.off()

png(file.path(outdir, "tree_features.png"), width = 1800, height = max(1000, 55 * nrow(features) + 500), res = 160)
draw_tree_features()
dev.off()
