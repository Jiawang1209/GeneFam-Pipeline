#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("Usage: plot_jcvi_kaks.R <kaks_table> <outdir> [species_order_tsv]", call. = FALSE)
}

kaks_table <- args[[1]]
outdir <- args[[2]]
species_order_tsv <- ifelse(length(args) >= 3, args[[3]], "")

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(stringr)
  library(ggplot2)
  library(ggbeeswarm)
})

dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

raw_kaks <- readr::read_delim(kaks_table, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)

required_cols <- c("Seq_1", "Seq_2", "Ka", "Ks", "Ka_Ks")
missing_cols <- setdiff(required_cols, colnames(raw_kaks))
if (length(missing_cols) > 0) {
  stop(paste("Missing required Ka/Ks columns:", paste(missing_cols, collapse = ", ")), call. = FALSE)
}

if ("Species" %in% colnames(raw_kaks)) {
  raw_kaks <- raw_kaks %>% dplyr::mutate(Species = .data$Species)
} else {
  raw_kaks <- raw_kaks %>% dplyr::mutate(Species = paste(.data$Seq_1, .data$Seq_2, sep = "/"))
}

species_levels <- raw_kaks %>%
  dplyr::filter(!is.na(.data$Species), .data$Species != "") %>%
  dplyr::pull(.data$Species) %>%
  unique()

if (file.exists(species_order_tsv)) {
  order_df <- readr::read_delim(species_order_tsv, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)
  if ("Species" %in% colnames(order_df)) {
    configured_levels <- order_df$Species[order_df$Species %in% species_levels]
    species_levels <- unique(c(configured_levels, species_levels))
  }
}

plot_df <- raw_kaks %>%
  dplyr::filter(.data$Seq_1 != "Seq_1") %>%
  dplyr::filter(.data$Ka_Ks != "NaN") %>%
  dplyr::select(.data$Ka, .data$Ks, .data$Ka_Ks, .data$Species) %>%
  tidyr::pivot_longer(cols = c(.data$Ka, .data$Ks, .data$Ka_Ks), values_to = "Value", names_to = "Type") %>%
  dplyr::mutate(Value = as.numeric(.data$Value)) %>%
  dplyr::filter(!is.na(.data$Value)) %>%
  dplyr::mutate(Type = factor(.data$Type, levels = c("Ka", "Ks", "Ka_Ks"), ordered = TRUE)) %>%
  dplyr::mutate(Species = factor(.data$Species, levels = species_levels, ordered = TRUE))

if (nrow(plot_df) == 0) {
  stop("No valid Ka/Ks rows remained after filtering", call. = FALSE)
}

palette_values <- c(
  "#d73027", "#f46d43", "#fdae61", "#fee08b", "#ffffbf",
  "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850", "#4575b4",
  "#91bfdb", "#762a83", "#af8dc3", "#e7d4e8", "#1b7837"
)
species_palette <- rep(palette_values, length.out = length(species_levels))
names(species_palette) <- species_levels

p <- ggplot2::ggplot(plot_df, ggplot2::aes(x = .data$Species, y = .data$Value, fill = .data$Species)) +
  ggplot2::geom_boxplot(outlier.colour = NA) +
  ggbeeswarm::geom_quasirandom(
    ggplot2::aes(fill = .data$Species, group = .data$Species),
    shape = 21,
    size = 3,
    alpha = 0.7,
    varwidth = TRUE
  ) +
  ggplot2::geom_hline(yintercept = 1, linetype = 2) +
  ggplot2::facet_wrap(~Type, scales = "free") +
  ggplot2::scale_fill_manual(values = species_palette) +
  ggplot2::labs(x = "", y = "", fill = "Species") +
  ggplot2::theme_bw() +
  ggplot2::theme(
    panel.grid = ggplot2::element_blank(),
    panel.border = ggplot2::element_rect(linewidth = 1),
    legend.text = ggplot2::element_text(size = 15),
    legend.title = ggplot2::element_text(size = 15),
    axis.title = ggplot2::element_text(size = 15),
    axis.text = ggplot2::element_text(size = 12),
    axis.text.x = ggplot2::element_blank(),
    axis.ticks.x = ggplot2::element_blank(),
    strip.text = ggplot2::element_text(size = 15)
  )

ggplot2::ggsave(filename = file.path(outdir, "8.jcvi_Kaks.pdf"), plot = p, height = 5, width = max(10, length(species_levels) * 1.8))
ggplot2::ggsave(filename = file.path(outdir, "8.jcvi_Kaks.png"), plot = p, height = 5, width = max(10, length(species_levels) * 1.8), dpi = 300)
