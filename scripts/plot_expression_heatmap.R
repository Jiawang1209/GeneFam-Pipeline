args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2 && length(args) != 4) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_expression_heatmap.R --args <expression.tsv> [sample_metadata.tsv gene_summary.tsv] <outdir>")
}

input <- args[[1]]
metadata_path <- NULL
gene_summary_path <- NULL
outdir <- args[[length(args)]]
if (length(args) == 4) {
  metadata_path <- args[[2]]
  gene_summary_path <- args[[3]]
}
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

expr <- read.delim(input, check.names = FALSE)
row.names(expr) <- expr[[1]]
matrix_data <- as.matrix(sapply(expr[-1], as.numeric))
rownames(matrix_data) <- expr[[1]]

sample_labels <- colnames(matrix_data)
if (!is.null(metadata_path) && file.exists(metadata_path)) {
  metadata <- read.delim(metadata_path, check.names = FALSE)
  metadata <- metadata[match(colnames(matrix_data), metadata$sample_id), ]
  sample_labels <- metadata$plot_label
  sample_labels[is.na(sample_labels) | sample_labels == ""] <- colnames(matrix_data)[is.na(sample_labels) | sample_labels == ""]
}

draw_plot <- function() {
  layout(matrix(c(1, 2), nrow = 1), widths = c(3.2, 1))
  par(mar = c(8, 8, 4, 1))
  heatmap(matrix_data, scale = "row", margins = c(8, 8), labCol = sample_labels, main = "family expression heatmap")
  par(mar = c(8, 4, 4, 1))
  if (!is.null(gene_summary_path) && file.exists(gene_summary_path)) {
    summary <- read.delim(gene_summary_path, check.names = FALSE)
    summary$fold_change_max_min <- suppressWarnings(as.numeric(summary$fold_change_max_min))
    top <- head(summary[order(summary$fold_change_max_min, decreasing = TRUE), ], 10)
    barplot(
      top$fold_change_max_min,
      names.arg = top$gene_id,
      las = 2,
      col = "#4C78A8",
      border = NA,
      ylab = "Max/min fold change"
    )
    title("top responsive genes")
  } else {
    plot.new()
    text(0.5, 0.5, "No gene summary")
  }
}

pdf(file.path(outdir, "expression_heatmap.pdf"), width = 11, height = 7)
draw_plot()
dev.off()

png(file.path(outdir, "expression_heatmap.png"), width = 1800, height = 1100, res = 160)
draw_plot()
dev.off()
