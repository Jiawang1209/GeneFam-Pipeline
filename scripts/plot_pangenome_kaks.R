args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_pangenome_kaks.R --args <pangenome_kaks.tsv> <pangenome_kaks_summary.tsv> <outdir>")
}

pair_path <- args[[1]]
summary_path <- args[[2]]
outdir <- args[[3]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

pairs <- read.delim(pair_path, check.names = FALSE)
summary <- read.delim(summary_path, check.names = FALSE)

if (nrow(pairs) == 0) {
  stop("pangenome Ka/Ks pair table must not be empty")
}

pairs$ks_numeric <- suppressWarnings(as.numeric(pairs$ks))
pairs$ka_ks_numeric <- suppressWarnings(as.numeric(pairs$ka_ks))
summary$pair_count_numeric <- suppressWarnings(as.numeric(summary$pair_count))
summary$pair_count_numeric[is.na(summary$pair_count_numeric)] <- 0

class_levels <- summary$pair_pangenome_class[order(summary$pair_count_numeric, decreasing = TRUE)]
if (length(class_levels) == 0) {
  class_levels <- unique(pairs$pair_pangenome_class)
}
pairs$pair_pangenome_class <- factor(pairs$pair_pangenome_class, levels = class_levels)

palette <- c(
  core = "#4C78A8",
  soft_core = "#72B7B2",
  dispensable = "#F58518",
  rare = "#B279A2",
  absent = "#BAB0AC",
  mixed = "#E45756"
)
box_cols <- palette[as.character(class_levels)]
box_cols[is.na(box_cols)] <- "#54A24B"

strip_points <- function(x_values, y_values, col) {
  for (i in seq_along(x_values)) {
    vals <- y_values[pairs$pair_pangenome_class == x_values[[i]]]
    vals <- vals[!is.na(vals)]
    if (length(vals) > 0) {
      points(jitter(rep(i, length(vals)), amount = 0.08), vals, pch = 16, cex = 0.75, col = adjustcolor(col[[i]], alpha.f = 0.65))
    }
  }
}

draw_plot <- function() {
  layout(matrix(c(1, 2, 3, 3), nrow = 2, byrow = TRUE), heights = c(1, 1))

  par(mar = c(7, 5, 4, 2))
  boxplot(
    ks_numeric ~ pair_pangenome_class,
    data = pairs,
    col = box_cols,
    border = "#333333",
    las = 2,
    ylab = "Ks",
    xlab = ""
  )
  strip_points(class_levels, pairs$ks_numeric, box_cols)
  title("Ks by pangenome class")

  par(mar = c(7, 5, 4, 2))
  if (all(is.na(pairs$ka_ks_numeric))) {
    plot.new()
    text(0.5, 0.5, "Ka/Ks values not available")
  } else {
    boxplot(
      ka_ks_numeric ~ pair_pangenome_class,
      data = pairs,
      col = box_cols,
      border = "#333333",
      las = 2,
      ylab = "Ka/Ks",
      xlab = ""
    )
    strip_points(class_levels, pairs$ka_ks_numeric, box_cols)
    abline(h = 1, lty = 2, col = "#666666")
  }
  title("Ka/Ks by pangenome class")

  par(mar = c(6, 5, 4, 2))
  counts <- summary$pair_count_numeric
  names(counts) <- summary$pair_pangenome_class
  barplot(counts, col = box_cols[match(names(counts), class_levels)], border = NA, las = 2, ylab = "Pair count")
  title("pangenome-class pair evidence")
}

pdf(file.path(outdir, "pangenome_kaks.pdf"), width = 11, height = 7)
draw_plot()
dev.off()

png(file.path(outdir, "pangenome_kaks.png"), width = 1800, height = 1100, res = 160)
draw_plot()
dev.off()
