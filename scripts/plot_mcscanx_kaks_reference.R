#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("Usage: plot_mcscanx_kaks_reference.R <kaks_table> <gene_pairs.tsv> <outdir>", call. = FALSE)
}

kaks_table <- args[[1]]
gene_pairs <- args[[2]]
outdir <- args[[3]]

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(stringr)
  library(ggplot2)
  library(ggbeeswarm)
})

dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

pairs <- readr::read_delim(gene_pairs, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE) %>%
  dplyr::transmute(Seq_1 = .data$gene_a, Seq_2 = .data$gene_b, `Duplicate Type` = dplyr::recode(.data$type, "tandem" = "Tandem", "WGD" = "WGD", .default = .data$type))

kaks <- readr::read_delim(kaks_table, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)
required_cols <- c("Seq_1", "Seq_2", "Ka", "Ks", "Ka_Ks")
missing_cols <- setdiff(required_cols, colnames(kaks))
if (length(missing_cols) > 0) {
  stop(paste("Missing required Ka/Ks columns:", paste(missing_cols, collapse = ", ")), call. = FALSE)
}

plot_df <- kaks %>%
  dplyr::filter(.data$Seq_1 != "Seq_1") %>%
  dplyr::filter(.data$Ka_Ks != "NaN") %>%
  dplyr::left_join(pairs, by = c("Seq_1", "Seq_2")) %>%
  dplyr::mutate(`Duplicate Type` = ifelse(is.na(.data$`Duplicate Type`) | .data$`Duplicate Type` == "", "Unknown", .data$`Duplicate Type`)) %>%
  dplyr::mutate(Species = ifelse("Species" %in% colnames(.), .data$Species, .data$Seq_1)) %>%
  dplyr::select(.data$Ka, .data$Ks, .data$Ka_Ks, .data$Species, .data$`Duplicate Type`) %>%
  tidyr::pivot_longer(cols = c(.data$Ka, .data$Ks, .data$Ka_Ks), values_to = "Value", names_to = "Type") %>%
  dplyr::mutate(Value = as.numeric(.data$Value)) %>%
  dplyr::filter(!is.na(.data$Value)) %>%
  dplyr::mutate(Type = factor(.data$Type, levels = c("Ka", "Ks", "Ka_Ks"), ordered = TRUE))

if (nrow(plot_df) == 0) {
  stop("No valid MCScanX Ka/Ks rows remained after filtering", call. = FALSE)
}

species_levels <- unique(plot_df$Species)
palette_values <- c("#c51b7d", "#d73027", "#f46d43", "#fdae61", "#fee08b", "#ffffbf", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850")
species_palette <- rep(palette_values, length.out = length(species_levels))
names(species_palette) <- species_levels

p <- ggplot2::ggplot(plot_df, ggplot2::aes(x = .data$Species, y = .data$Value, fill = .data$Species)) +
  ggplot2::geom_boxplot(outlier.colour = NA, alpha = 0.65, width = 0.6) +
  ggbeeswarm::geom_quasirandom(
    ggplot2::aes(fill = .data$Species, color = .data$Species, shape = .data$Type),
    size = 2,
    alpha = 0.5,
    varwidth = TRUE,
    color = "#000000"
  ) +
  ggplot2::geom_hline(yintercept = 1, linetype = 2) +
  ggplot2::facet_grid(`Duplicate Type`~Type, scales = "free") +
  ggplot2::scale_fill_manual(values = species_palette) +
  ggplot2::scale_color_manual(values = species_palette) +
  ggplot2::scale_shape_manual(values = 21:23) +
  ggplot2::labs(x = "", y = "") +
  ggplot2::theme_bw() +
  ggplot2::theme(
    panel.grid = ggplot2::element_blank(),
    panel.border = ggplot2::element_rect(linewidth = 1),
    legend.text = ggplot2::element_text(size = 15),
    legend.title = ggplot2::element_text(size = 15),
    axis.title = ggplot2::element_text(size = 15),
    axis.text = ggplot2::element_text(size = 12, color = "#000000"),
    strip.text = ggplot2::element_text(size = 15),
    axis.text.x = ggplot2::element_blank(),
    axis.ticks.x = ggplot2::element_blank(),
    plot.margin = ggplot2::margin(5, 5, 5, 20, unit = "pt")
  )

ggplot2::ggsave(filename = file.path(outdir, "9.mcscanx_Kaks.pdf"), plot = p, height = 7.5, width = 16)
ggplot2::ggsave(filename = file.path(outdir, "9.mcscanx_Kaks.png"), plot = p, height = 7.5, width = 16, dpi = 300)
