args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3) {
  stop("Usage: plot_mcscanx_circlize.R <chromosomes.tsv> <links.tsv> <outdir>")
}

chromosome_path <- args[[1]]
link_path <- args[[2]]
outdir <- args[[3]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("circlize", quietly = TRUE)) {
  stop("R package 'circlize' is required")
}

chromosomes <- read.delim(chromosome_path, stringsAsFactors = FALSE, check.names = FALSE)
links <- read.delim(link_path, stringsAsFactors = FALSE, check.names = FALSE)
if (nrow(chromosomes) == 0 || nrow(links) == 0) {
  stop("circlize input tables must contain at least one chromosome and one link")
}

plot_one <- function(file, device) {
  if (device == "pdf") {
    pdf(file, width = 8, height = 8)
  } else {
    png(file, width = 1800, height = 1800, res = 220)
  }
  on.exit(dev.off(), add = TRUE)

  circlize::circos.clear()
  circlize::circos.par(start.degree = 90, gap.degree = 6, track.margin = c(0.01, 0.01))
  factors <- chromosomes$chr_id
  xlim <- cbind(chromosomes$start, chromosomes$end)
  circlize::circos.initialize(factors = factors, xlim = xlim)
  circlize::circos.trackPlotRegion(
    ylim = c(0, 1),
    bg.border = "#D8DEE9",
    panel.fun = function(x, y) {
      sector <- circlize::CELL_META$sector.index
      circlize::circos.text(
        circlize::CELL_META$xcenter,
        0.5,
        sub("^.*\\|", "", sector),
        cex = 0.75,
        facing = "clockwise",
        niceFacing = TRUE
      )
    }
  )

  palette <- c("#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756", "#72B7B2")
  block_ids <- unique(links$block_id)
  block_colours <- setNames(palette[((seq_along(block_ids) - 1) %% length(palette)) + 1], block_ids)
  for (i in seq_len(nrow(links))) {
    colour <- block_colours[[as.character(links$block_id[[i]])]]
    circlize::circos.link(
      links$gene_a_chr[[i]],
      c(links$gene_a_start[[i]], links$gene_a_end[[i]]),
      links$gene_b_chr[[i]],
      c(links$gene_b_start[[i]], links$gene_b_end[[i]]),
      col = grDevices::adjustcolor(colour, alpha.f = 0.45),
      border = NA
    )
  }
  title("MCScanX syntenic links")
  circlize::circos.clear()
}

plot_one(file.path(outdir, "mcscanx_circlize.pdf"), "pdf")
plot_one(file.path(outdir, "mcscanx_circlize.png"), "png")
