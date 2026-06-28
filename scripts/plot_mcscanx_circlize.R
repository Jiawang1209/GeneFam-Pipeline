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

chromosomes <- chromosomes[order(chromosomes$species_id, chromosomes$seqid), , drop = FALSE]
chrom_df <- data.frame(
  chr = chromosomes$chr_id,
  start = as.numeric(chromosomes$start),
  end = as.numeric(chromosomes$end),
  stringsAsFactors = FALSE
)

endpoint_bed <- unique(rbind(
  data.frame(
    chr = links$gene_a_chr,
    start = as.numeric(links$gene_a_start),
    end = as.numeric(links$gene_a_end),
    gene_id = links$gene_a,
    stringsAsFactors = FALSE
  ),
  data.frame(
    chr = links$gene_b_chr,
    start = as.numeric(links$gene_b_start),
    end = as.numeric(links$gene_b_end),
    gene_id = links$gene_b,
    stringsAsFactors = FALSE
  )
))
endpoint_bed <- endpoint_bed[order(endpoint_bed$chr, endpoint_bed$start, endpoint_bed$end), , drop = FALSE]

if (nrow(duplicate_tracks) > 0) {
  gene_type <- data.frame(
    chr = duplicate_tracks$chr_id,
    start = as.numeric(duplicate_tracks$start),
    end = as.numeric(duplicate_tracks$end),
    gene_id = duplicate_tracks$gene_id,
    duplicate_type = duplicate_tracks$duplicate_type,
    stringsAsFactors = FALSE
  )
} else {
  gene_type <- data.frame(
    chr = endpoint_bed$chr,
    start = endpoint_bed$start,
    end = endpoint_bed$end,
    gene_id = endpoint_bed$gene_id,
    duplicate_type = "syntenic",
    stringsAsFactors = FALSE
  )
}
gene_type <- gene_type[!is.na(gene_type$chr) & !is.na(gene_type$start) & !is.na(gene_type$end), , drop = FALSE]
gene_type$duplicate_type <- ifelse(is.na(gene_type$duplicate_type) | gene_type$duplicate_type == "", "syntenic", gene_type$duplicate_type)

type_palette <- c(
  singleton = "#00ADFF",
  dispersed = "#e66101",
  proximal = "#fdb863",
  tandem = "#b2abd2",
  WGD = "#5e3c99",
  wgd = "#5e3c99",
  segmental = "#5e3c99",
  syntenic = "#5e3c99",
  unknown = "#999999"
)

type_to_colour <- function(value) {
  value <- as.character(value)
  colour <- type_palette[value]
  colour[is.na(colour)] <- "#999999"
  unname(colour)
}

label_for_chr <- function(chr_id) {
  sub("^.*\\|", "", chr_id)
}

density_genomic <- data.frame()
if (nrow(density) > 0) {
  density_genomic <- data.frame(
    chr = density$chr_id,
    start = as.numeric(density$window_start),
    end = as.numeric(density$window_end),
    value = as.numeric(density$link_count),
    stringsAsFactors = FALSE
  )
  density_genomic <- density_genomic[is.finite(density_genomic$value), , drop = FALSE]
}

link_type_by_gene <- setNames(as.character(gene_type$duplicate_type), gene_type$gene_id)
link_type <- rep("Collinearity", nrow(links))
for (i in seq_len(nrow(links))) {
  gene_a_type <- link_type_by_gene[[as.character(links$gene_a[[i]])]]
  gene_b_type <- link_type_by_gene[[as.character(links$gene_b[[i]])]]
  if ((!is.null(gene_a_type) && gene_a_type == "tandem") ||
      (!is.null(gene_b_type) && gene_b_type == "tandem")) {
    link_type[[i]] <- "Tandem"
  }
}

link_bed_1 <- data.frame(
  chr = links$gene_a_chr,
  start = as.numeric(links$gene_a_start),
  end = as.numeric(links$gene_a_end),
  gene_id = links$gene_a,
  link_type = link_type,
  stringsAsFactors = FALSE
)
link_bed_2 <- data.frame(
  chr = links$gene_b_chr,
  start = as.numeric(links$gene_b_start),
  end = as.numeric(links$gene_b_end),
  gene_id = links$gene_b,
  link_type = link_type,
  stringsAsFactors = FALSE
)

draw_legends <- function() {
  gene_labels <- c("Singleton", "Dispersed", "Proximal", "Tandem", "WGD/segmental")
  gene_colours <- c("#00ADFF", "#e66101", "#fdb863", "#b2abd2", "#5e3c99")
  duplicate_labels <- c("Collinearity", "Tandem")
  duplicate_colours <- c("#fb9a99", "#80b1d3")
  if (requireNamespace("ComplexHeatmap", quietly = TRUE) && requireNamespace("grid", quietly = TRUE)) {
    gene_legend <- ComplexHeatmap::Legend(
      at = seq_along(gene_labels),
      labels = gene_labels,
      labels_gp = grid::gpar(fontsize = 8),
      title = "Gene Type",
      title_gp = grid::gpar(fontsize = 9),
      grid_height = grid::unit(0.4, "cm"),
      grid_width = grid::unit(0.4, "cm"),
      type = "points",
      pch = NA,
      background = gene_colours
    )
    duplicate_legend <- ComplexHeatmap::Legend(
      at = seq_along(duplicate_labels),
      labels = duplicate_labels,
      labels_gp = grid::gpar(fontsize = 8),
      title = "Gene Duplicate",
      title_gp = grid::gpar(fontsize = 9),
      grid_height = grid::unit(0.5, "cm"),
      grid_width = grid::unit(0.5, "cm"),
      type = c("lines", "lines"),
      pch = NA,
      legend_gp = grid::gpar(col = duplicate_colours, lwd = 1)
    )
    grid::pushViewport(grid::viewport(x = 0.9, y = 0.9))
    grid::grid.draw(gene_legend)
    grid::upViewport()
    grid::pushViewport(grid::viewport(x = 0.9, y = 0.18))
    grid::grid.draw(duplicate_legend)
    grid::upViewport()
  } else {
    graphics::legend(
      "topright",
      legend = c(gene_labels, duplicate_labels),
      col = c(gene_colours, duplicate_colours),
      pch = c(rep(15, length(gene_labels)), rep(NA, length(duplicate_labels))),
      lty = c(rep(NA, length(gene_labels)), rep(1, length(duplicate_labels))),
      bty = "n",
      cex = 0.65
    )
  }
}

plot_one <- function(
  file,
  device,
  plot_chrom_df = chrom_df,
  plot_endpoint_bed = endpoint_bed,
  plot_density_genomic = density_genomic,
  plot_gene_type = gene_type,
  plot_link_bed_1 = link_bed_1,
  plot_link_bed_2 = link_bed_2,
  plot_link_type = link_type,
  title_text = "MCScanX self intra-species duplication circos"
) {
  if (device == "pdf") {
    pdf(file, width = 8, height = 8)
  } else {
    png(file, width = 1800, height = 1800, res = 220)
  }
  on.exit(dev.off(), add = TRUE)

  circlize::circos.clear()
  circlize::circos.par(
    start.degree = 90,
    gap.degree = 6,
    track.margin = c(0.01, 0.01),
    cell.padding = c(0.02, 0, 0.02, 0)
  )

  circlize::circos.genomicInitialize(
    plot_chrom_df,
    plotType = NULL,
    axis.labels.cex = 0.4 * par("cex"),
    labels.cex = 0.6 * par("cex"),
    track.height = 0.01,
    major.by = 5000000
  )

  if (nrow(plot_endpoint_bed) > 0) {
    circlize::circos.genomicLabels(
      plot_endpoint_bed,
      labels.column = 4,
      padding = 0.1,
      connection_height = circlize::mm_h(3),
      col = as.numeric(factor(plot_endpoint_bed[[1]])),
      line_col = as.numeric(factor(plot_endpoint_bed[[1]])),
      cex = 0.45,
      side = "outside"
    )
  }

  circlize::circos.genomicTrackPlotRegion(
    plot_chrom_df,
    track.height = 0.05,
    stack = TRUE,
    bg.border = NA,
    panel.fun = function(region, value, ...) {
      circlize::circos.genomicRect(region, value, col = "#9e9ac8", border = "black", ...)
    }
  )

  circlize::circos.track(
    track.index = circlize::get.current.track.index(),
    bg.border = NA,
    panel.fun = function(x, y) {
      circlize::circos.genomicAxis(h = "bottom", direction = "inside")
    }
  )

  circlize::circos.track(
    ylim = c(0, 0.5),
    track.height = 0.05,
    bg.border = NA,
    panel.fun = function(x, y) {
      chr <- circlize::CELL_META$sector.index
      xlim <- circlize::CELL_META$xlim
      ylim <- circlize::CELL_META$ylim
      circlize::circos.text(
        mean(xlim),
        mean(ylim) - 0.3,
        label_for_chr(chr),
        cex = 0.45,
        col = "#000000",
        facing = "inside",
        niceFacing = TRUE
      )
    }
  )

  if (nrow(plot_density_genomic) > 0) {
    max_density <- max(plot_density_genomic$value, na.rm = TRUE)
    if (!is.finite(max_density) || max_density <= 0) {
      max_density <- 1
    }
    circlize::circos.genomicTrack(
      plot_density_genomic,
      ylim = c(0, max_density),
      track.height = 0.10,
      bg.col = "#f0f0f0",
      bg.border = NA,
      panel.fun = function(region, value, ...) {
        circlize::circos.genomicLines(region, value, col = "blue", lwd = 0.35, ...)
        circlize::circos.yaxis(
          labels.cex = 0.2,
          lwd = 0.1,
          tick.length = circlize::convert_x(0.2, "mm")
        )
      }
    )
  }

  if (nrow(plot_gene_type) > 0) {
    gene_type_plot <- data.frame(
      chr = plot_gene_type$chr,
      start = plot_gene_type$start,
      end = plot_gene_type$end,
      colour = type_to_colour(plot_gene_type$duplicate_type),
      stringsAsFactors = FALSE
    )
    circlize::circos.genomicTrackPlotRegion(
      gene_type_plot,
      track.height = 0.10,
      stack = TRUE,
      bg.border = NA,
      panel.fun = function(region, value, ...) {
        circlize::circos.genomicRect(region, value, col = value[[1]], border = value[[1]], ...)
      }
    )
  }

  collinearity_rows <- which(plot_link_type == "Collinearity")
  tandem_rows <- which(plot_link_type == "Tandem")
  if (length(collinearity_rows) > 0) {
    circlize::circos.genomicLink(
      plot_link_bed_1[collinearity_rows, , drop = FALSE],
      plot_link_bed_2[collinearity_rows, , drop = FALSE],
      col = grDevices::adjustcolor("black", alpha.f = 0.35),
      border = "#fb9a99",
      lwd = 1
    )
  }
  if (length(tandem_rows) > 0) {
    circlize::circos.genomicLink(
      plot_link_bed_1[tandem_rows, , drop = FALSE],
      plot_link_bed_2[tandem_rows, , drop = FALSE],
      col = grDevices::adjustcolor("black", alpha.f = 0.35),
      border = "#80b1d3",
      lwd = 1
    )
  }

  draw_legends()
  title(title_text)
  circlize::circos.clear()
}

plot_one(file.path(outdir, "mcscanx_circlize.pdf"), "pdf")
plot_one(file.path(outdir, "mcscanx_circlize.png"), "png")

species_ids <- unique(chromosomes$species_id)
for (species_id in species_ids) {
  species_chr_ids <- chromosomes$chr_id[chromosomes$species_id == species_id]
  species_chrom_df <- chrom_df[chrom_df$chr %in% species_chr_ids, , drop = FALSE]
  species_endpoint_bed <- endpoint_bed[endpoint_bed$chr %in% species_chr_ids, , drop = FALSE]
  species_density_genomic <- density_genomic[density_genomic$chr %in% species_chr_ids, , drop = FALSE]
  species_gene_type <- gene_type[gene_type$chr %in% species_chr_ids, , drop = FALSE]
  species_link_rows <- which(link_bed_1$chr %in% species_chr_ids & link_bed_2$chr %in% species_chr_ids)
  species_link_bed_1 <- link_bed_1[species_link_rows, , drop = FALSE]
  species_link_bed_2 <- link_bed_2[species_link_rows, , drop = FALSE]
  species_link_type <- link_type[species_link_rows]

  species_outdir <- file.path(outdir, "species", species_id)
  dir.create(species_outdir, recursive = TRUE, showWarnings = FALSE)
  safe_species_id <- gsub("[^A-Za-z0-9_.-]+", "_", species_id)
  plot_one(
    file.path(species_outdir, paste0("circos_", safe_species_id, ".pdf")),
    "pdf",
    species_chrom_df,
    species_endpoint_bed,
    species_density_genomic,
    species_gene_type,
    species_link_bed_1,
    species_link_bed_2,
    species_link_type,
    paste0("MCScanX self circos: ", species_id)
  )
  plot_one(
    file.path(species_outdir, paste0("circos_", safe_species_id, ".png")),
    "png",
    species_chrom_df,
    species_endpoint_bed,
    species_density_genomic,
    species_gene_type,
    species_link_bed_1,
    species_link_bed_2,
    species_link_type,
    paste0("MCScanX self circos: ", species_id)
  )
}
