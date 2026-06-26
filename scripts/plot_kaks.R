args <- commandArgs(trailingOnly = TRUE)
if (!length(args) %in% c(2, 3)) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_kaks.R --args <kaks.tsv> [kaks_wgd_annotations.tsv] <outdir>")
}

input <- args[[1]]
annotations_input <- NULL
outdir <- args[[length(args)]]
if (length(args) == 3) {
  annotations_input <- args[[2]]
}
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

kaks <- read.delim(input, check.names = FALSE)
ks_values <- as.numeric(kaks$ks)
ks_values <- ks_values[!is.na(ks_values)]
annotations <- data.frame()
if (!is.null(annotations_input) && file.exists(annotations_input)) {
  annotations <- read.delim(annotations_input, check.names = FALSE)
  annotations$label_position <- as.numeric(annotations$label_position)
}

plot_ks_distribution <- function() {
  hist(ks_values, breaks = 40, col = "#72B7B2", border = "white", xlab = "Ks", main = "Ks distribution with WGD layers")
  if (nrow(annotations) > 0) {
    palette <- c("#4E79A7", "#F28E2B", "#59A14F", "#B07AA1", "#E15759", "#76B7B2")
    y_top <- par("usr")[4]
    for (index in seq_len(nrow(annotations))) {
      x <- annotations$label_position[index]
      if (is.na(x)) {
        next
      }
      colour <- palette[((index - 1) %% length(palette)) + 1]
      abline(v = x, col = colour, lwd = 2, lty = 2)
      text(x = x, y = y_top * 0.95, labels = annotations$label[index], col = colour, srt = 90, adj = c(1, 0.5), cex = 0.72)
    }
  }
}

pdf(file.path(outdir, "ks_distribution.pdf"), width = 7, height = 4)
plot_ks_distribution()
dev.off()

png(file.path(outdir, "ks_distribution.png"), width = 1400, height = 800, res = 200)
plot_ks_distribution()
dev.off()
