args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_kaks.R --args <kaks.tsv> <outdir>")
}

input <- args[[1]]
outdir <- args[[2]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

kaks <- read.delim(input, check.names = FALSE)

pdf(file.path(outdir, "ks_distribution.pdf"), width = 7, height = 4)
hist(as.numeric(kaks$ks), breaks = 40, col = "#72B7B2", xlab = "Ks", main = "Ks distribution")
dev.off()
