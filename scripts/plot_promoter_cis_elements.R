args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_promoter_cis_elements.R --args <gene_matrix.tsv> <category_summary.tsv> <outdir>")
}

gene_matrix_path <- args[[1]]
category_summary_path <- args[[2]]
outdir <- args[[3]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

gene_matrix <- read.delim(gene_matrix_path, check.names = FALSE)
category_summary <- read.delim(category_summary_path, check.names = FALSE)

if (nrow(gene_matrix) == 0 || nrow(category_summary) == 0) {
  stop("Promoter cis-element matrix and category summary must not be empty")
}

gene_matrix$count_numeric <- suppressWarnings(as.numeric(gene_matrix$count))
gene_matrix$count_numeric[is.na(gene_matrix$count_numeric)] <- 0
genes <- unique(paste(gene_matrix$species_id, gene_matrix$gene_id, sep = "|"))
categories <- unique(gene_matrix$category)
heat <- matrix(0, nrow = length(genes), ncol = length(categories), dimnames = list(genes, categories))
for (idx in seq_len(nrow(gene_matrix))) {
  gene_key <- paste(gene_matrix$species_id[idx], gene_matrix$gene_id[idx], sep = "|")
  heat[gene_key, gene_matrix$category[idx]] <- gene_matrix$count_numeric[idx]
}
heat <- heat[order(rownames(heat)), order(colnames(heat)), drop = FALSE]

category_summary$total_numeric <- suppressWarnings(as.numeric(category_summary$total_count))
category_summary$total_numeric[is.na(category_summary$total_numeric)] <- 0
top_elements <- category_summary[order(category_summary$total_numeric, decreasing = TRUE), ]
top_elements <- head(top_elements, 12)

category_colors <- c(
  hormone_responsive = "#4C78A8",
  stress_responsive = "#E45756",
  light_responsive = "#F58518",
  growth_development = "#54A24B",
  core_promoter = "#B279A2",
  other = "#72B7B2"
)

draw_plot <- function() {
  layout(matrix(c(1, 2), nrow = 1), widths = c(1.25, 1))
  par(mar = c(8, 8, 4, 2))
  image(
    x = seq_len(ncol(heat)),
    y = seq_len(nrow(heat)),
    z = t(heat),
    axes = FALSE,
    xlab = "",
    ylab = "",
    col = colorRampPalette(c("#F7FBFF", "#6BAED6", "#08306B"))(30)
  )
  axis(1, at = seq_len(ncol(heat)), labels = colnames(heat), las = 2, cex.axis = 0.75)
  axis(2, at = seq_len(nrow(heat)), labels = rownames(heat), las = 2, cex.axis = 0.7)
  title("cis-element category abundance")
  grid(nx = ncol(heat), ny = nrow(heat), col = "#E5E5E5")

  par(mar = c(8, 5, 4, 2))
  bar_cols <- category_colors[top_elements$category]
  bar_cols[is.na(bar_cols)] <- "#72B7B2"
  labels <- paste(top_elements$element, top_elements$category, sep = "\n")
  barplot(
    top_elements$total_numeric,
    names.arg = labels,
    las = 2,
    cex.names = 0.7,
    ylab = "Occurrence count",
    col = bar_cols,
    border = NA
  )
  title("top promoter cis-elements")
}

pdf(file.path(outdir, "promoter_cis_elements.pdf"), width = 12, height = 6)
draw_plot()
dev.off()

png(file.path(outdir, "promoter_cis_elements.png"), width = 1800, height = 900, res = 160)
draw_plot()
dev.off()
