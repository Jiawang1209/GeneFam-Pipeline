args <- commandArgs(trailingOnly = TRUE)
if (!length(args) %in% c(3, 5)) {
  stop("Usage: plot_mcscanx_circlize.R <chromosomes.tsv> <links.tsv> [density.tsv duplicate_type_tracks.tsv] <outdir>")
}

chromosome_path <- args[[1]]
link_path <- args[[2]]
density_path <- NULL
duplicate_track_path <- NULL
outdir <- args[[length(args)]]
if (length(args) == 5) {
  density_path <- args[[3]]
  duplicate_track_path <- args[[4]]
}
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("circlize", quietly = TRUE)) {
  stop("R package 'circlize' is required")
}

chromosomes <- read.delim(chromosome_path, stringsAsFactors = FALSE, check.names = FALSE)
links <- read.delim(link_path, stringsAsFactors = FALSE, check.names = FALSE)
density <- data.frame()
duplicate_tracks <- data.frame()
if (!is.null(density_path) && file.exists(density_path)) {
  density <- read.delim(density_path, stringsAsFactors = FALSE, check.names = FALSE)
}
if (!is.null(duplicate_track_path) && file.exists(duplicate_track_path)) {
  duplicate_tracks <- read.delim(duplicate_track_path, stringsAsFactors = FALSE, check.names = FALSE)
}
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

  if (nrow(density) > 0) {
    max_density <- max(as.numeric(density$link_count), na.rm = TRUE)
    if (!is.finite(max_density) || max_density <= 0) {
      max_density <- 1
    }
    circlize::circos.trackPlotRegion(
      ylim = c(0, max_density),
      bg.border = "#EEF2F7",
      track.height = 0.10,
      panel.fun = function(x, y) {
        sector <- circlize::CELL_META$sector.index
        sector_density <- density[density$chr_id == sector, , drop = FALSE]
        if (nrow(sector_density) == 0) {
          return()
        }
        for (row_index in seq_len(nrow(sector_density))) {
          circlize::circos.rect(
            as.numeric(sector_density$window_start[[row_index]]),
            0,
            as.numeric(sector_density$window_end[[row_index]]),
            as.numeric(sector_density$link_count[[row_index]]),
            col = "#7BAFDE",
            border = NA
          )
        }
      }
    )
  }

  if (nrow(duplicate_tracks) > 0) {
    duplicate_palette <- c(
      WGD = "#4C78A8",
      wgd = "#4C78A8",
      tandem = "#F58518",
      proximal = "#54A24B",
      dispersed = "#B279A2",
      singleton = "#B8B8B8",
      syntenic = "#72B7B2",
      unknown = "#999999"
    )
    circlize::circos.trackPlotRegion(
      ylim = c(0, 1),
      bg.border = "#EEF2F7",
      track.height = 0.07,
      panel.fun = function(x, y) {
        sector <- circlize::CELL_META$sector.index
        sector_tracks <- duplicate_tracks[duplicate_tracks$chr_id == sector, , drop = FALSE]
        if (nrow(sector_tracks) == 0) {
          return()
        }
        for (row_index in seq_len(nrow(sector_tracks))) {
          duplicate_type <- as.character(sector_tracks$duplicate_type[[row_index]])
          colour <- duplicate_palette[[duplicate_type]]
          if (is.null(colour)) {
            colour <- "#999999"
          }
          midpoint <- (as.numeric(sector_tracks$start[[row_index]]) + as.numeric(sector_tracks$end[[row_index]])) / 2
          circlize::circos.points(midpoint, 0.5, pch = 16, cex = 0.55, col = colour)
        }
      }
    )
  }

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
  title("MCScanX syntenic links with density and duplicate-type tracks")
  circlize::circos.clear()
}

plot_one(file.path(outdir, "mcscanx_circlize.pdf"), "pdf")
plot_one(file.path(outdir, "mcscanx_circlize.png"), "png")
