args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 5 || length(args) > 6) {
  stop("Usage: R --vanilla --slave -f plot_tree_subfamilies.R --args <treefile> <outdir> <family_name> <min_size> <max_groups> [label_map.tsv]")
}

treefile <- args[[1]]
outdir <- args[[2]]
family_name <- args[[3]]
min_size <- suppressWarnings(as.integer(args[[4]]))
max_groups <- suppressWarnings(as.integer(args[[5]]))
if (is.na(min_size) || min_size < 1) {
  min_size <- 2
}
if (is.na(max_groups) || max_groups < 1) {
  max_groups <- 8
}
label_map_file <- if (length(args) >= 6) args[[6]] else ""

required_packages <- c("ape", "treeio", "ggtree", "tidytree", "ggplot2", "ggnewscale", "aplot")
missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages) > 0) {
  stop(paste("Missing required R packages:", paste(missing_packages, collapse = ", ")))
}
suppressPackageStartupMessages({
  library(ggtree)
  library(ggplot2)
  library(ggnewscale)
  library(aplot)
})

tables_dir <- file.path(outdir, "tables")
plots_dir <- file.path(outdir, "plots")
dir.create(tables_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(plots_dir, recursive = TRUE, showWarnings = FALSE)

tree_ape <- ape::read.tree(treefile)
tree_plot <- treeio::read.newick(treefile, node.label = "support")
if (is.null(tree_ape$tip.label) || length(tree_ape$tip.label) == 0) {
  stop("Tree has no tip labels")
}

tip_labels <- tree_ape$tip.label
n_tips <- length(tip_labels)

choose_group_count <- function(n, min_size, max_groups) {
  if (n < min_size * 2) {
    return(1)
  }
  proposed <- floor(sqrt(n))
  proposed <- max(2, proposed)
  proposed <- min(max_groups, proposed, floor(n / min_size))
  max(1, proposed)
}

assign_subfamilies <- function(tree, min_size, max_groups) {
  n <- length(tree$tip.label)
  target_k <- choose_group_count(n, min_size, max_groups)
  if (target_k <= 1) {
    return(rep("C1", n))
  }

  distances <- ape::cophenetic.phylo(tree)
  hc <- stats::hclust(stats::as.dist(distances), method = "average")
  k <- target_k
  groups <- stats::cutree(hc, k = k)
  while (k > 1 && min(table(groups)) < min_size) {
    k <- k - 1
    groups <- stats::cutree(hc, k = k)
  }

  group_order <- unique(groups[tree$tip.label])
  group_labels <- stats::setNames(paste0("C", seq_along(group_order)), group_order)
  unname(group_labels[as.character(groups[tree$tip.label])])
}

subfamilies <- assign_subfamilies(tree_ape, min_size, max_groups)
assignments <- data.frame(
  tree_label = tip_labels,
  gene_id = tip_labels,
  species_id = "Unknown",
  subfamily = subfamilies,
  tree_order = seq_along(tip_labels),
  stringsAsFactors = FALSE
)
if (nzchar(label_map_file) && file.exists(label_map_file)) {
  label_map <- read.delim(label_map_file, check.names = FALSE, stringsAsFactors = FALSE)
  required_map_cols <- c("tree_label", "gene_id", "species_id")
  missing_map_cols <- setdiff(required_map_cols, names(label_map))
  if (length(missing_map_cols) > 0) {
    stop(paste("Label map missing required columns:", paste(missing_map_cols, collapse = ", ")))
  }
  matched <- match(assignments$tree_label, label_map$tree_label)
  assignments$gene_id <- ifelse(is.na(matched), assignments$tree_label, label_map$gene_id[matched])
  assignments$species_id <- ifelse(is.na(matched), "Unknown", label_map$species_id[matched])
}

stats <- as.data.frame(table(assignments$species_id, assignments$subfamily), stringsAsFactors = FALSE)
names(stats) <- c("species_id", "subfamily", "count")
stats$count <- as.integer(stats$count)
stats <- stats[order(stats$species_id, stats$subfamily), ]

write.table(
  assignments,
  file = file.path(tables_dir, "tree_subfamily_assignments.tsv"),
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)
write.table(
  stats,
  file = file.path(tables_dir, "tree_subfamily_stats.tsv"),
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)

subfamily_levels <- sort(unique(assignments$subfamily))
species_levels <- sort(unique(assignments$species_id))
subfamily_palette <- c("#807dba", "#ec7014", "#fcc5c0", "#dd3497", "#78c679", "#4eb3d3", "#fdb863", "#1b9e77")
species_palette <- c(
  "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c",
  "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a", "#ffff99", "#b15928",
  "#8dd3c7", "#bebada", "#80b1d3", "#b3de69"
)
subfamily_cols <- stats::setNames(rep(subfamily_palette, length.out = length(subfamily_levels)), subfamily_levels)
species_cols <- stats::setNames(rep(species_palette, length.out = length(species_levels)), species_levels)

plot_base <- ggtree::ggtree(tree_plot, branch.length = "none", layout = "circular", size = 0.15, color = "#969696")
tip_order <- plot_base$data[plot_base$data$isTip, c("label", "y")]
tip_order <- tip_order[order(tip_order$y), , drop = FALSE]
assignments$plot_y <- tip_order$y[match(assignments$tree_label, tip_order$label)]

run_rows <- list()
for (group in subfamily_levels) {
  group_tips <- assignments[assignments$subfamily == group, , drop = FALSE]
  group_tips <- group_tips[order(group_tips$plot_y), , drop = FALSE]
  if (nrow(group_tips) == 0) {
    next
  }
  run_id <- cumsum(c(TRUE, diff(group_tips$plot_y) > 1.5))
  for (run in unique(run_id)) {
    run_tips <- group_tips[run_id == run, , drop = FALSE]
    run_rows[[length(run_rows) + 1]] <- data.frame(
      subfamily = group,
      start = run_tips$tree_label[1],
      end = run_tips$tree_label[nrow(run_tips)],
      size = nrow(run_tips),
      stringsAsFactors = FALSE
    )
  }
}
strip_df <- do.call(rbind, run_rows)

tree_info <- assignments[, c("tree_label", "gene_id", "species_id", "subfamily")]
names(tree_info)[1] <- "label"
tip_label_offset <- 0.35
strip_offset <- 1.2
tree_outer_padding <- 2.4
tip_label_size <- 1.8
tip_point_size <- 1.6
strip_bar_size <- 1.1
label_show_threshold <- 24
show_tip_labels <- n_tips <= label_show_threshold
n_species <- length(species_levels)
species_legend_threshold <- 10
show_species_legend <- n_species <= species_legend_threshold

plot_tree <- function() {
  p <- ggtree::ggtree(
    tree_plot,
    branch.length = "none",
    layout = "circular",
    size = 0.12,
    color = "#969696"
  ) %<+% tree_info +
    ggtree::geom_nodepoint(
      ggplot2::aes(fill = cut(ifelse(as.numeric(support) <= 1, as.numeric(support) * 100, as.numeric(support)), c(0, 45, 75, 100))),
      shape = 21,
      size = 0.7,
      stroke = 0.2,
      na.rm = TRUE
    ) +
    ggplot2::scale_fill_manual(
      values = c("black", "grey70", "white"),
      name = "Bootstrap Percentage(BP)",
      breaks = c("(75,100]", "(45,75]", "(0,45]"),
      labels = c("BP >= 75", "45 <= BP < 75", "BP < 45"),
      guide = ggplot2::guide_legend(override.aes = list(size = 3))
    ) +
    ggnewscale::new_scale_fill() +
    ggtree::geom_tippoint(ggplot2::aes(fill = species_id), shape = 21, size = tip_point_size, stroke = 0.2) +
    ggplot2::scale_fill_manual(
      values = species_cols,
      name = "Species",
      guide = if (show_species_legend) {
        ggplot2::guide_legend(override.aes = list(size = 2.2))
      } else {
        "none"
      }
    ) +
    ggtree::geom_tree(size = 0.12, color = "#969696") +
    ggplot2::theme(
      legend.position = c(0.54, 0.48),
      legend.background = ggplot2::element_blank(),
      legend.key.size = ggplot2::unit(0.35, "cm"),
      legend.text = ggplot2::element_text(size = 7),
      legend.title = ggplot2::element_text(size = 8)
    )

  if (show_tip_labels) {
    p <- p +
      ggtree::geom_tiplab(
        ggplot2::aes(label = gene_id, color = subfamily),
        size = tip_label_size,
        offset = tip_label_offset,
        show.legend = FALSE
      ) +
      ggplot2::scale_color_manual(values = subfamily_cols, name = "Subfamily")
  }

  if (!is.null(strip_df) && nrow(strip_df) > 0) {
    for (i in seq_len(nrow(strip_df))) {
      row <- strip_df[i, ]
      p <- p + ggtree::geom_strip(
        row$start,
        row$end,
        barsize = strip_bar_size,
        color = subfamily_cols[[row$subfamily]],
        offset = strip_offset,
        label = row$subfamily,
        fontsize = 4,
        offset.text = 0.5,
        extend = 0.35,
        alpha = 0.2
      )
    }
  }
  p + ggtree::xlim_tree(strip_offset + tree_outer_padding)
}

plot_bubble <- function() {
  stats_nonzero <- stats[stats$count > 0, , drop = FALSE]
  stats_nonzero$species_id <- factor(stats_nonzero$species_id, levels = rev(species_levels), ordered = TRUE)
  stats_nonzero$subfamily <- factor(stats_nonzero$subfamily, levels = subfamily_levels, ordered = TRUE)
  ggplot2::ggplot(stats_nonzero, ggplot2::aes(x = subfamily, y = species_id)) +
    ggplot2::geom_point(ggplot2::aes(fill = subfamily, size = count), shape = 21, color = "#000000", alpha = 0.9) +
    ggplot2::geom_text(ggplot2::aes(label = count), size = 3) +
    ggplot2::scale_x_discrete(position = "top") +
    ggplot2::scale_size(range = c(4, 10), guide = "none") +
    ggplot2::scale_fill_manual(values = subfamily_cols, guide = "none") +
    ggplot2::labs(x = "", y = "") +
    ggplot2::theme_bw() +
    ggplot2::theme(
      panel.grid = ggplot2::element_line(color = "#eeeeee"),
      panel.border = ggplot2::element_rect(color = "#000000", linewidth = 0.75),
      axis.text.y = ggplot2::element_text(color = "#000000", face = "italic", size = 10),
      axis.text.x = ggplot2::element_text(color = "#000000", size = 11),
      plot.background = ggplot2::element_blank(),
      plot.margin = ggplot2::margin(5, 20, 5, 5)
    )
}

plot_bar <- function() {
  stats_nonzero <- stats[stats$count > 0, , drop = FALSE]
  stats_nonzero$species_id <- factor(stats_nonzero$species_id, levels = rev(species_levels), ordered = TRUE)
  stats_nonzero$subfamily <- factor(stats_nonzero$subfamily, levels = subfamily_levels, ordered = TRUE)
  ggplot2::ggplot(stats_nonzero, ggplot2::aes(x = count, y = species_id, fill = subfamily)) +
    ggplot2::geom_bar(stat = "identity", position = "fill", width = 0.52, color = "#000000", linewidth = 0.25) +
    ggplot2::scale_x_continuous(
      position = "top",
      expand = ggplot2::expansion(mult = c(0, 0)),
      breaks = c(0, 0.25, 0.5, 0.75, 1),
      labels = c("0%", "25%", "50%", "75%", "100%")
    ) +
    ggplot2::scale_fill_manual(values = subfamily_cols, name = "Subfamily") +
    ggplot2::labs(x = "", y = "") +
    ggplot2::theme_bw() +
    ggplot2::theme(
      panel.grid = ggplot2::element_blank(),
      panel.border = ggplot2::element_rect(color = "#000000", linewidth = 0.75),
      axis.text.y = ggplot2::element_blank(),
      axis.ticks.y = ggplot2::element_blank(),
      axis.text.x = ggplot2::element_text(color = "#000000", size = 10),
      plot.background = ggplot2::element_blank(),
      plot.margin = ggplot2::margin(5, 5, 5, 10)
    )
}

p_tree <- plot_tree()
p_bubble <- plot_bubble()
p_bar <- plot_bar()
p_stats <- aplot::insert_right(p_bubble, p_bar, width = 1.15)

ggplot2::ggsave(
  filename = file.path(plots_dir, "tree_subfamily.pdf"),
  plot = p_tree,
  width = 14,
  height = 14,
  limitsize = FALSE
)
ggplot2::ggsave(
  filename = file.path(plots_dir, "tree_subfamily.png"),
  plot = p_tree,
  width = 14,
  height = 14,
  dpi = 180,
  limitsize = FALSE
)
ggplot2::ggsave(
  filename = file.path(plots_dir, "tree_subfamily_species_stats.pdf"),
  plot = p_stats,
  width = max(9, 0.8 * length(subfamily_levels) + 6),
  height = max(6, 0.45 * length(species_levels) + 2.5),
  limitsize = FALSE
)
ggplot2::ggsave(
  filename = file.path(plots_dir, "tree_subfamily_species_stats.png"),
  plot = p_stats,
  width = max(9, 0.8 * length(subfamily_levels) + 6),
  height = max(6, 0.45 * length(species_levels) + 2.5),
  dpi = 180,
  limitsize = FALSE
)
