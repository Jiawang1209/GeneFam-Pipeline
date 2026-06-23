args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("Usage: Rscript plot_family_counts.R <family_counts.tsv> <outdir>")
}

input <- args[[1]]
outdir <- args[[2]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

counts <- read.delim(input, check.names = FALSE)

pdf(file.path(outdir, "family_counts.pdf"), width = 8, height = 4)
barplot(
  counts$member_count,
  names.arg = counts$species_id,
  las = 2,
  ylab = "Family member count",
  col = "#4C78A8"
)
dev.off()

png(file.path(outdir, "family_counts.png"), width = 1200, height = 700, res = 150)
barplot(
  counts$member_count,
  names.arg = counts$species_id,
  las = 2,
  ylab = "Family member count",
  col = "#4C78A8"
)
dev.off()
