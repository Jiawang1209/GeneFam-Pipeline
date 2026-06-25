args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_feature_summary.R --args <feature_summary.tsv> <outdir>")
}

input <- args[[1]]
outdir <- args[[2]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

summary <- read.delim(input, check.names = FALSE)
summary$value_numeric <- suppressWarnings(as.numeric(summary$value))
plot_rows <- summary[!is.na(summary$value_numeric) & summary$group == "all", ]
if (nrow(plot_rows) == 0) {
  stop("No numeric feature summary rows with group == all")
}

labels <- paste(plot_rows$feature, plot_rows$metric, sep = "\n")
colors <- c(
  domain = "#4C78A8",
  motif = "#F58518",
  gene_structure = "#54A24B",
  synteny = "#B279A2",
  promoter = "#E45756"
)
bar_colors <- colors[plot_rows$feature]
bar_colors[is.na(bar_colors)] <- "#72B7B2"

pdf(file.path(outdir, "feature_summary.pdf"), width = 10, height = 5)
barplot(
  plot_rows$value_numeric,
  names.arg = labels,
  las = 2,
  ylab = "Metric value",
  col = bar_colors,
  cex.names = 0.65
)
dev.off()

png(file.path(outdir, "feature_summary.png"), width = 1600, height = 900, res = 160)
barplot(
  plot_rows$value_numeric,
  names.arg = labels,
  las = 2,
  ylab = "Metric value",
  col = bar_colors,
  cex.names = 0.65
)
dev.off()
