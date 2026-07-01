args <- commandArgs(trailingOnly = TRUE)
if (!length(args) %in% c(4, 6, 7)) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_gene_family_info.R --args <copy_number.tsv> <copy_number_summary.tsv> <protein_properties.tsv> [species_order.tsv copy_number_expansion.tsv [pangenome_summary.tsv]] <outdir>")
}

copy_path <- args[[1]]
summary_path <- args[[2]]
protein_path <- args[[3]]
species_order_path <- NULL
expansion_path <- NULL
pangenome_path <- NULL
outdir <- args[[length(args)]]
if (length(args) == 6) {
  species_order_path <- args[[4]]
  expansion_path <- args[[5]]
}
if (length(args) == 7) {
  species_order_path <- args[[4]]
  expansion_path <- args[[5]]
  pangenome_path <- args[[6]]
}
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

copy_number <- read.delim(copy_path, check.names = FALSE)
copy_summary <- read.delim(summary_path, check.names = FALSE)
protein_properties <- read.delim(protein_path, check.names = FALSE)
species_order <- data.frame()
copy_expansion <- data.frame()
pangenome_summary <- data.frame()
if (!is.null(species_order_path) && file.exists(species_order_path)) {
  species_order <- read.delim(species_order_path, check.names = FALSE)
}
if (!is.null(expansion_path) && file.exists(expansion_path)) {
  copy_expansion <- read.delim(expansion_path, check.names = FALSE)
}
if (!is.null(pangenome_path) && file.exists(pangenome_path)) {
  pangenome_summary <- read.delim(pangenome_path, check.names = FALSE)
}

if (nrow(copy_number) == 0) {
  stop("copy-number table must not be empty")
}

copy_number$member_numeric <- suppressWarnings(as.numeric(copy_number$member_count))
copy_number$member_numeric[is.na(copy_number$member_numeric)] <- 0
if (nrow(species_order) > 0) {
  species_order$plot_order_numeric <- suppressWarnings(as.numeric(species_order$plot_order))
  species_levels <- species_order$species_id[order(species_order$plot_order_numeric)]
  copy_number$order_key <- match(copy_number$species_id, species_levels)
  copy_number$order_key[is.na(copy_number$order_key)] <- length(species_levels) + seq_len(sum(is.na(copy_number$order_key)))
  copy_number <- copy_number[order(copy_number$order_key), ]
} else {
  copy_number <- copy_number[order(copy_number$member_numeric, decreasing = TRUE), ]
}

copy_colors <- c(
  absent = "#BAB0AC",
  single_copy = "#4C78A8",
  multi_copy = "#54A24B",
  high_copy = "#E45756"
)
bar_cols <- copy_colors[copy_number$copy_number_class]
bar_cols[is.na(bar_cols)] <- "#72B7B2"

copy_summary$species_numeric <- suppressWarnings(as.numeric(copy_summary$species_count))
copy_summary$species_numeric[is.na(copy_summary$species_numeric)] <- 0
summary_cols <- copy_colors[copy_summary$copy_number_class]
summary_cols[is.na(summary_cols)] <- "#72B7B2"

draw_plot <- function() {
  has_expansion <- nrow(copy_expansion) > 0
  has_pangenome <- nrow(pangenome_summary) > 0
  if (has_expansion && has_pangenome) {
    layout(matrix(c(1, 2, 3, 4, 5, 5), nrow = 3, byrow = TRUE), heights = c(1, 1.05, 0.9))
  } else if (has_expansion) {
    layout(matrix(c(1, 2, 3, 4), nrow = 2, byrow = TRUE), heights = c(1, 1.1))
  } else {
    layout(matrix(c(1, 2, 3, 3), nrow = 2, byrow = TRUE), heights = c(1, 1.1))
  }

  par(mar = c(7, 5, 4, 2))
  barplot(
    copy_number$member_numeric,
    names.arg = copy_number$species_id,
    las = 2,
    ylab = "Family member count",
    col = bar_cols,
    border = NA,
    cex.names = 0.75
  )
  title("copy number by species")

  par(mar = c(7, 5, 4, 2))
  barplot(
    copy_summary$species_numeric,
    names.arg = copy_summary$copy_number_class,
    las = 2,
    ylab = "Species count",
    col = summary_cols,
    border = NA,
    cex.names = 0.8
  )
  title("copy-number class summary")

  if (has_expansion) {
    expansion_cols <- c(
      expanded = "#E45756",
      baseline = "#4C78A8",
      contracted = "#F58518",
      absent = "#BAB0AC"
    )
    copy_expansion$member_numeric <- suppressWarnings(as.numeric(copy_expansion$member_count))
    copy_expansion$fold_numeric <- suppressWarnings(as.numeric(copy_expansion$fold_change_vs_median))
    copy_expansion$order_key <- match(copy_expansion$species_id, copy_number$species_id)
    copy_expansion <- copy_expansion[order(copy_expansion$order_key), ]
    point_cols <- expansion_cols[copy_expansion$expansion_status]
    point_cols[is.na(point_cols)] <- "#72B7B2"
    par(mar = c(7, 5, 4, 2))
    plot(
      seq_len(nrow(copy_expansion)),
      copy_expansion$fold_numeric,
      pch = 16,
      cex = 1.1,
      col = point_cols,
      xaxt = "n",
      xlab = "",
      ylab = "Fold vs median",
      ylim = c(0, max(c(copy_expansion$fold_numeric, 2), na.rm = TRUE))
    )
    axis(1, at = seq_len(nrow(copy_expansion)), labels = copy_expansion$species_id, las = 2, cex.axis = 0.75)
    abline(h = 1, col = "#666666", lty = 2)
    abline(h = 2, col = "#E45756", lty = 3)
    abline(h = 0.5, col = "#F58518", lty = 3)
    title("copy-number expansion status")
  }

  if (has_pangenome) {
    pangenome_summary$presence_numeric <- suppressWarnings(as.numeric(pangenome_summary$presence_fraction))
    pangenome_summary$present_numeric <- suppressWarnings(as.numeric(pangenome_summary$present_species))
    pangenome_summary$absent_numeric <- suppressWarnings(as.numeric(pangenome_summary$absent_species))
    presence_value <- pangenome_summary$presence_numeric[1]
    present_value <- pangenome_summary$present_numeric[1]
    absent_value <- pangenome_summary$absent_numeric[1]
    class_label <- as.character(pangenome_summary$pangenome_presence_class[1])
    par(mar = c(5, 5, 4, 2))
    barplot(
      c(present_value, absent_value),
      names.arg = c("present", "absent"),
      ylab = "Species count",
      col = c("#54A24B", "#BAB0AC"),
      border = NA,
      ylim = c(0, max(c(present_value + absent_value, 1), na.rm = TRUE))
    )
    text(1.5, max(c(present_value, absent_value, 1), na.rm = TRUE) * 0.9, paste0("presence = ", round(presence_value * 100, 1), "%\n", class_label), cex = 0.95)
    title("pangenome presence class")
  }

  par(mar = c(6, 5, 4, 2))
  if (nrow(protein_properties) > 0) {
    protein_properties$protein_length <- suppressWarnings(as.numeric(protein_properties$protein_length))
    protein_properties$molecular_weight_kda <- suppressWarnings(as.numeric(protein_properties$molecular_weight_kda))
    protein_properties$isoelectric_point <- suppressWarnings(as.numeric(protein_properties$isoelectric_point))
    protein_properties$gravy <- suppressWarnings(as.numeric(protein_properties$gravy))
    values <- list(
      Length = protein_properties$protein_length,
      MW_kDa = protein_properties$molecular_weight_kda,
      pI = protein_properties$isoelectric_point,
      GRAVY = protein_properties$gravy
    )
    boxplot(values, col = c("#4C78A8", "#F58518", "#B279A2", "#72B7B2"), ylab = "Value")
    title("family protein properties")
  } else {
    plot.new()
    text(0.5, 0.5, "No protein property table available")
  }
}

pdf(file.path(outdir, "gene_family_info_summary.pdf"), width = 11, height = 7)
draw_plot()
dev.off()

png(file.path(outdir, "gene_family_info_summary.png"), width = 1800, height = 1100, res = 160)
draw_plot()
dev.off()

draw_species_property_plot <- function() {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    return(FALSE)
  }
  if (nrow(protein_properties) == 0) {
    return(FALSE)
  }
  plot_data <- data.frame(
    Species = protein_properties$species_id,
    Length = suppressWarnings(as.numeric(protein_properties$protein_length)),
    MW = suppressWarnings(as.numeric(protein_properties$molecular_weight_kda)),
    hydrophobicity = suppressWarnings(as.numeric(protein_properties$gravy)),
    pI = suppressWarnings(as.numeric(protein_properties$isoelectric_point)),
    check.names = FALSE
  )
  species_levels <- unique(copy_number$species_id)
  plot_data$Species <- factor(plot_data$Species, levels = rev(species_levels), ordered = TRUE)
  long_data <- stats::reshape(
    plot_data,
    varying = c("Length", "MW", "hydrophobicity", "pI"),
    v.names = "Value",
    timevar = "Kind",
    times = c("Length", "MW", "hydrophobicity", "pI"),
    direction = "long"
  )
  long_data$Kind <- factor(long_data$Kind, levels = c("Length", "MW", "hydrophobicity", "pI"), ordered = TRUE)
  long_data <- long_data[is.finite(long_data$Value) & !is.na(long_data$Species), ]
  if (nrow(long_data) == 0) {
    return(FALSE)
  }
  palette <- c(
    "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99",
    "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a",
    "#ffff99", "#b15928", "#8dd3c7", "#bebada", "#80b1d3",
    "#fdb462", "#b3de69", "#fccde5", "#bc80bd", "#ccebc5"
  )
  species_values <- levels(droplevels(long_data$Species))
  fill_values <- stats::setNames(rep(palette, length.out = length(species_values)), species_values)
  point_layer <- if (requireNamespace("ggbeeswarm", quietly = TRUE)) {
    ggbeeswarm::geom_quasirandom(
      ggplot2::aes(x = Value, y = Species, fill = Species, group = Species),
      shape = 21,
      size = 2.4,
      alpha = 0.7,
      varwidth = TRUE
    )
  } else {
    ggplot2::geom_jitter(
      ggplot2::aes(x = Value, y = Species, fill = Species, group = Species),
      shape = 21,
      size = 2.2,
      alpha = 0.65,
      width = 0,
      height = 0.18
    )
  }
  p_stat <- ggplot2::ggplot(long_data) +
    ggplot2::geom_boxplot(ggplot2::aes(x = Value, y = Species, fill = Species), outlier.shape = NA, linewidth = 0.35) +
    point_layer +
    ggplot2::scale_fill_manual(values = fill_values) +
    ggplot2::facet_wrap(~Kind, scales = "free", nrow = 1) +
    ggplot2::labs(x = "", y = "") +
    ggplot2::theme_bw() +
    ggplot2::theme(
      panel.grid = ggplot2::element_blank(),
      axis.text = ggplot2::element_text(color = "#000000", size = 10),
      panel.border = ggplot2::element_rect(linewidth = 1),
      strip.text = ggplot2::element_text(color = "#000000", size = 13),
      strip.background = ggplot2::element_rect(linewidth = 1),
      axis.text.y = ggplot2::element_text(color = "#000000", size = 8),
      axis.ticks.y = ggplot2::element_line(color = "#000000"),
      legend.position = "none"
    )
  ggplot2::ggsave(file.path(outdir, "protein_properties_by_species.pdf"), plot = p_stat, height = 7.5, width = 17)
  ggplot2::ggsave(file.path(outdir, "protein_properties_by_species.png"), plot = p_stat, height = 7.5, width = 17, dpi = 160)
  TRUE
}

draw_species_property_plot()
