#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 4) {
  stop("Usage: plot_mcscanx_circlize_reference.R <chromosomes.tsv> <density.tsv> <gene_types.tsv> <links.tsv> <outdir>", call. = FALSE)
}

chromosomes_file <- args[[1]]
density_file <- args[[2]]
gene_types_file <- args[[3]]
links_file <- args[[4]]
outdir <- ifelse(length(args) >= 5, args[[5]], dirname(chromosomes_file))

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(circlize)
  library(ComplexHeatmap)
  library(scales)
  library(grid)
})

dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

chromosomes <- readr::read_delim(chromosomes_file, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)
density <- readr::read_delim(density_file, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)
gene_types <- readr::read_delim(gene_types_file, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)
links <- readr::read_delim(links_file, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)

if (nrow(chromosomes) == 0) {
  stop("No chromosome rows available for circlize plotting", call. = FALSE)
}

species_list <- unique(chromosomes$species_id)

type_values <- c("Singleton" = 0, "Dispersed" = 1, "Proximal" = 2, "Tandem" = 3, "WGD/segmental" = 4, "unknown" = 0)
type_colors <- c("#00ADFF", "#e66101", "#fdb863", "#b2abd2", "#5e3c99")

for (species in species_list) {
  chr_df <- chromosomes %>%
    dplyr::filter(.data$species_id == species) %>%
    dplyr::transmute(Chr = .data$Chr, Start = as.numeric(.data$Start), End = as.numeric(.data$End))
  density_df <- density %>%
    dplyr::filter(.data$species_id == species) %>%
    dplyr::transmute(Chr = .data$Chr, Start = as.numeric(.data$Start), End = as.numeric(.data$End), Number_Count = as.numeric(.data$Number_Count))
  gene_df <- gene_types %>%
    dplyr::filter(.data$species_id == species) %>%
    dplyr::mutate(Type = dplyr::recode(.data$Type, "WGD" = "WGD/segmental", .default = .data$Type)) %>%
    dplyr::mutate(TypeValue = unname(type_values[ifelse(.data$Type %in% names(type_values), .data$Type, "unknown")])) %>%
    dplyr::transmute(Chr = .data$Chr, Start = as.numeric(.data$Start), End = as.numeric(.data$End), gene_id = .data$gene_id, TypeValue = .data$TypeValue)
  species_links <- links %>% dplyr::filter(.data$species_id == species)

  pdf(file.path(outdir, paste0("circos_", species, ".pdf")), height = 8, width = 8)
  circlize::circos.clear()
  circlize::circos.par(start.degree = 90, gap.degree = 2)

  circlize::circos.genomicInitialize(
    chr_df,
    plotType = NULL,
    axis.labels.cex = 0.4 * par("cex"),
    labels.cex = 0.6 * par("cex"),
    track.height = 0.01,
    major.by = 5000000
  )

  if (nrow(gene_df) > 0 && nrow(gene_df) <= 250) {
    circlize::circos.genomicLabels(
      gene_df %>% dplyr::select(.data$Chr, .data$Start, .data$End, .data$gene_id),
      labels.column = 4,
      padding = 0.1,
      connection_height = circlize::mm_h(3),
      col = as.numeric(factor(gene_df$Chr)),
      line_col = as.numeric(factor(gene_df$Chr)),
      cex = 0.6,
      side = "outside"
    )
  }

  circlize::circos.genomicTrackPlotRegion(
    chr_df,
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
      chr <- CELL_META$sector.index
      xlim <- CELL_META$xlim
      ylim <- CELL_META$ylim
      circlize::circos.text(mean(xlim), mean(ylim) - 0.3, chr, cex = 0.5, col = "#000000", facing = "inside", niceFacing = TRUE)
    }
  )

  if (nrow(density_df) > 0) {
    circlize::circos.genomicTrack(
      density_df,
      track.height = 0.1,
      bg.col = "#f0f0f0",
      bg.border = NA,
      panel.fun = function(region, value, ...) {
        circlize::circos.genomicLines(region, value, col = "blue", lwd = 0.35, ...)
        circlize::circos.yaxis(labels.cex = 0.2, lwd = 0.1, tick.length = circlize::convert_x(0.2, "mm"))
      }
    )
  }

  if (nrow(gene_df) > 0) {
    color_assign <- circlize::colorRamp2(breaks = c(0, 1, 2, 3, 4), col = type_colors)
    circlize::circos.genomicTrackPlotRegion(
      gene_df %>% dplyr::select(.data$Chr, .data$Start, .data$End, .data$TypeValue),
      track.height = 0.1,
      stack = TRUE,
      bg.border = NA,
      panel.fun = function(region, value, ...) {
        circlize::circos.genomicRect(region, value, col = color_assign(value[[1]]), border = color_assign(value[[1]]), ...)
      }
    )
  }

  if (nrow(species_links) > 0) {
    collin <- species_links %>% dplyr::filter(.data$Type %in% c("WGD", "Collinearity", "WGD/segmental"))
    tandem <- species_links %>% dplyr::filter(.data$Type %in% c("tandem", "Tandem"))
    if (nrow(collin) > 0) {
      circlize::circos.genomicLink(
        collin %>% dplyr::transmute(Chr = .data$Chr1, Start = as.numeric(.data$Start1), End = as.numeric(.data$End1), ID = .data$ID1),
        collin %>% dplyr::transmute(Chr = .data$Chr2, Start = as.numeric(.data$Start2), End = as.numeric(.data$End2), ID = .data$ID2),
        col = scales::alpha("black", alpha = 1),
        border = "#fb9a99",
        lwd = 1
      )
    }
    if (nrow(tandem) > 0) {
      circlize::circos.genomicLink(
        tandem %>% dplyr::transmute(Chr = .data$Chr1, Start = as.numeric(.data$Start1), End = as.numeric(.data$End1), ID = .data$ID1),
        tandem %>% dplyr::transmute(Chr = .data$Chr2, Start = as.numeric(.data$Start2), End = as.numeric(.data$End2), ID = .data$ID2),
        col = scales::alpha("black", alpha = 1),
        border = "#80b1d3",
        lwd = 1
      )
    }
  }

  gene_legend <- ComplexHeatmap::Legend(
    at = c(0, 1, 2, 3, 4),
    labels = c("Singleton", "Dispersed", "Proximal", "Tandem", "WGD/segmental"),
    title = "Gene Type",
    background = type_colors,
    type = "points",
    pch = NA
  )
  duplicate_legend <- ComplexHeatmap::Legend(
    at = c(1, 2),
    labels = c("Collinearity", "Tandem"),
    type = c("lines", "lines"),
    legend_gp = grid::gpar(col = c("#fb9a99", "#80b1d3"), lwd = 1),
    title = "Gene Duplicate"
  )
  grid::pushViewport(grid::viewport(x = 0.9, y = 0.9))
  grid::grid.draw(gene_legend)
  grid::upViewport()
  grid::pushViewport(grid::viewport(x = 0.9, y = 0.1))
  grid::grid.draw(duplicate_legend)
  grid::upViewport()
  circlize::circos.clear()
  dev.off()
}
