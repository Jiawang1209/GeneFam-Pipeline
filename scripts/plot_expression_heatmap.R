args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("Usage: Rscript plot_expression_heatmap.R <expression.tsv> <outdir>")
}

input <- args[[1]]
outdir <- args[[2]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

expr <- read.delim(input, check.names = FALSE)
row.names(expr) <- expr[[1]]
matrix_data <- as.matrix(expr[-1])

pdf(file.path(outdir, "expression_heatmap.pdf"), width = 7, height = 7)
heatmap(matrix_data, scale = "row", margins = c(8, 8))
dev.off()
