#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("Usage: plot_promoter_cis_reference.R <cis_gene_element_matrix.tsv> <element_annotations.tsv> <outdir> [species_tree.nwk]", call. = FALSE)
}

matrix_file <- args[[1]]
annotation_file <- args[[2]]
outdir <- args[[3]]
species_tree_file <- ifelse(length(args) >= 4, args[[4]], "")

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(stringr)
  library(ggplot2)
  library(ggfun)
  library(aplot)
})

dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

matrix_df <- readr::read_delim(matrix_file, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)
annotation_df <- readr::read_delim(annotation_file, delim = "\t", col_types = readr::cols(.default = "c"), show_col_types = FALSE)

if (nrow(matrix_df) == 0) {
  stop("No promoter cis-element matrix rows available", call. = FALSE)
}

plot_df <- matrix_df %>%
  dplyr::mutate(count = as.numeric(.data$count)) %>%
  dplyr::left_join(annotation_df, by = c("element" = "element"), suffix = c("", ".annotation")) %>%
  dplyr::mutate(description = dplyr::coalesce(.data$category.annotation, .data$category, "other")) %>%
  dplyr::group_by(.data$species_id, .data$element, .data$description) %>%
  dplyr::summarise(Count = sum(.data$count, na.rm = TRUE), .groups = "drop") %>%
  dplyr::rename(Species = .data$species_id, Element = .data$element)

species_levels <- rev(unique(plot_df$Species))
plot_df <- plot_df %>% dplyr::mutate(Species = factor(.data$Species, levels = species_levels, ordered = TRUE))

make_promoter_plot <- function(df, category_values, colors) {
  selected <- df %>% dplyr::filter(.data$description %in% category_values)
  if (nrow(selected) == 0) {
    selected <- df
  }
  selected <- selected %>%
    dplyr::mutate(axis_label = interaction(.data$Element, .data$description, sep = "&"))

  ggplot2::ggplot(selected, ggplot2::aes(x = .data$Species, y = .data$axis_label)) +
    ggplot2::geom_tile(fill = "#ffffff", color = "#979797") +
    ggplot2::geom_point(
      ggplot2::aes(fill = cut(.data$Count, c(0, 15, 25, 50, 100, 500, 1000, 2000, 3000, 4000, 5000, Inf), right = FALSE)),
      shape = 22,
      size = 10.5
    ) +
    ggplot2::geom_text(ggplot2::aes(label = .data$Count), size = 3) +
    ggplot2::scale_fill_manual(values = rev(c("#80b1d3", "#ffffb3", "#bebada", "#fb8072", "#8dd3c7", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd", "#ccebc5", "#ffed6f", "#bdbdbd")), drop = FALSE) +
    ggplot2::scale_y_discrete(
      expand = ggplot2::expansion(mult = c(0.01, 0.01)),
      guide = guide_axis_nested(
        type = "bracket",
        key = "&",
        levels_text = list(
          ggplot2::element_text(angle = 0, hjust = 1, vjust = 0.5, size = 10, color = colors[1]),
          ggplot2::element_text(angle = 90, hjust = 0.5, color = colors, size = 15)
        )
      )
    ) +
    ggplot2::labs(x = "", y = "", fill = "Count") +
    ggplot2::theme_bw() +
    ggfun::theme_guide(bracket = ggplot2::element_line(color = colors, linewidth = 2)) +
    ggplot2::theme(
      axis.text.x = ggplot2::element_text(color = "black", angle = 90, size = 12, hjust = 1, vjust = 0.5),
      axis.text.y = ggplot2::element_text(color = "black", size = 12),
      legend.background = ggfun::element_roundrect(color = "#808080", linetype = 1),
      axis.ticks.length.x.top = grid::unit(0.25, "cm"),
      panel.border = ggplot2::element_blank(),
      panel.grid = ggplot2::element_blank(),
      plot.margin = grid::unit(c(0.2, 0.2, 0.2, 0.2), units = "cm")
    ) +
    ggplot2::guides(fill = ggplot2::guide_legend(direction = "vertical", ncol = 1, bycol = FALSE))
}

p1 <- make_promoter_plot(plot_df, c("Plant hormone related", "Stress related", "hormone_responsive", "stress_responsive"), c("#fb8072", "#bc80bd"))
p2 <- make_promoter_plot(plot_df, c("Light responsiveness", "Plant growth and development", "light_responsive", "growth_development"), c("#80b1d3", "#6a51a3"))

if (file.exists(species_tree_file)) {
  suppressPackageStartupMessages({
    library(ggtree)
    library(ape)
  })
  tree <- ape::read.tree(species_tree_file)
  plot_tree <- ggtree::ggtree(tree, size = 0.25, branch.length = "none") +
    ggtree::geom_nodepoint(size = 2) +
    ggtree::geom_tree2() +
    ggtree::layout_dendrogram()
  p1 <- p1 %>% aplot::insert_top(plot_tree, height = 0.1)
  p2 <- p2 %>% aplot::insert_top(plot_tree, height = 0.1)
} else {
  p1 <- p1 %>% aplot::insert_top(ggplot2::ggplot() + ggplot2::theme_void(), height = 0.02)
  p2 <- p2 %>% aplot::insert_top(ggplot2::ggplot() + ggplot2::theme_void(), height = 0.02)
}

ggplot2::ggsave(filename = file.path(outdir, "promoter1.pdf"), plot = p1, height = 12, width = 7)
ggplot2::ggsave(filename = file.path(outdir, "promoter1.png"), plot = p1, height = 12, width = 7, dpi = 300)
ggplot2::ggsave(filename = file.path(outdir, "species_promoter2.pdf"), plot = p2, height = 15, width = 7)
ggplot2::ggsave(filename = file.path(outdir, "species_promoter2.png"), plot = p2, height = 15, width = 7, dpi = 300)
