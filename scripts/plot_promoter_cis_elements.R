args <- commandArgs(trailingOnly = TRUE)
if (!length(args) %in% c(3, 5)) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_promoter_cis_elements.R --args <gene_matrix.tsv> <category_summary.tsv> [gene_element_matrix.tsv element_annotations.tsv] <outdir>")
}

gene_matrix_path <- args[[1]]
category_summary_path <- args[[2]]
gene_element_matrix_path <- NULL
element_annotations_path <- NULL
outdir <- args[[length(args)]]
if (length(args) == 5) {
  gene_element_matrix_path <- args[[3]]
  element_annotations_path <- args[[4]]
}
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

gene_matrix <- read.delim(gene_matrix_path, check.names = FALSE)
category_summary <- read.delim(category_summary_path, check.names = FALSE)
gene_element_matrix <- data.frame()
element_annotations <- data.frame()
if (!is.null(gene_element_matrix_path) && file.exists(gene_element_matrix_path)) {
  gene_element_matrix <- read.delim(gene_element_matrix_path, check.names = FALSE)
}
if (!is.null(element_annotations_path) && file.exists(element_annotations_path)) {
  element_annotations <- read.delim(element_annotations_path, check.names = FALSE)
}

if (nrow(gene_matrix) == 0 || nrow(category_summary) == 0) {
  stop("Promoter cis-element matrix and category summary must not be empty")
}

gene_matrix$count_numeric <- suppressWarnings(as.numeric(gene_matrix$count))
gene_matrix$count_numeric[is.na(gene_matrix$count_numeric)] <- 0
genes <- unique(paste(gene_matrix$species_id, gene_matrix$gene_id, sep = "|"))
categories <- unique(gene_matrix$category)
heat <- matrix(0, nrow = length(genes), ncol = length(categories), dimnames = list(genes, categories))
for (idx in seq_len(nrow(gene_matrix))) {
  gene_key <- paste(gene_matrix$species_id[idx], gene_matrix$gene_id[idx], sep = "|")
  heat[gene_key, gene_matrix$category[idx]] <- gene_matrix$count_numeric[idx]
}
heat <- heat[order(rownames(heat)), order(colnames(heat)), drop = FALSE]

category_summary$total_numeric <- suppressWarnings(as.numeric(category_summary$total_count))
category_summary$total_numeric[is.na(category_summary$total_numeric)] <- 0
top_elements <- category_summary[order(category_summary$total_numeric, decreasing = TRUE), ]
top_elements <- head(top_elements, 12)

category_colors <- c(
  hormone_responsive = "#4C78A8",
  stress_responsive = "#E45756",
  light_responsive = "#F58518",
  growth_development = "#54A24B",
  core_promoter = "#B279A2",
  other = "#72B7B2"
)

draw_plot <- function() {
  has_element_panel <- nrow(gene_element_matrix) > 0 && nrow(element_annotations) > 0
  if (has_element_panel) {
    layout(matrix(c(1, 2, 3), nrow = 1), widths = c(1.15, 1.45, 1))
  } else {
    layout(matrix(c(1, 2), nrow = 1), widths = c(1.25, 1))
  }
  par(mar = c(8, 8, 4, 2))
  image(
    x = seq_len(ncol(heat)),
    y = seq_len(nrow(heat)),
    z = t(heat),
    axes = FALSE,
    xlab = "",
    ylab = "",
    col = colorRampPalette(c("#F7FBFF", "#6BAED6", "#08306B"))(30)
  )
  axis(1, at = seq_len(ncol(heat)), labels = colnames(heat), las = 2, cex.axis = 0.75)
  axis(2, at = seq_len(nrow(heat)), labels = rownames(heat), las = 2, cex.axis = 0.7)
  title("cis-element category abundance")
  grid(nx = ncol(heat), ny = nrow(heat), col = "#E5E5E5")

  if (has_element_panel) {
    gene_element_matrix$count_numeric <- suppressWarnings(as.numeric(gene_element_matrix$count))
    gene_element_matrix$count_numeric[is.na(gene_element_matrix$count_numeric)] <- 0
    element_annotations$total_numeric <- suppressWarnings(as.numeric(element_annotations$total_count))
    element_annotations$total_numeric[is.na(element_annotations$total_numeric)] <- 0
    selected_elements <- head(element_annotations[order(element_annotations$total_numeric, decreasing = TRUE), "element"], 16)
    element_panel <- gene_element_matrix[gene_element_matrix$element %in% selected_elements, , drop = FALSE]
    element_genes <- unique(paste(element_panel$species_id, element_panel$gene_id, sep = "|"))
    element_genes <- sort(element_genes)
    selected_elements <- selected_elements[selected_elements %in% unique(element_panel$element)]
    element_heat <- matrix(0, nrow = length(element_genes), ncol = length(selected_elements), dimnames = list(element_genes, selected_elements))
    element_category <- setNames(element_annotations$category, element_annotations$element)
    for (idx in seq_len(nrow(element_panel))) {
      gene_key <- paste(element_panel$species_id[idx], element_panel$gene_id[idx], sep = "|")
      element_heat[gene_key, element_panel$element[idx]] <- element_panel$count_numeric[idx]
    }
    par(mar = c(8, 8, 4, 2))
    plot(
      NA,
      xlim = c(0.5, ncol(element_heat) + 0.5),
      ylim = c(0.5, nrow(element_heat) + 0.5),
      axes = FALSE,
      xlab = "",
      ylab = ""
    )
    axis(1, at = seq_len(ncol(element_heat)), labels = colnames(element_heat), las = 2, cex.axis = 0.7)
    axis(2, at = seq_len(nrow(element_heat)), labels = rownames(element_heat), las = 2, cex.axis = 0.65)
    title("gene-by-element dot heatmap")
    grid(nx = ncol(element_heat), ny = nrow(element_heat), col = "#EFEFEF")
    max_count <- max(element_heat)
    if (!is.finite(max_count) || max_count <= 0) {
      max_count <- 1
    }
    for (row_idx in seq_len(nrow(element_heat))) {
      for (col_idx in seq_len(ncol(element_heat))) {
        value <- element_heat[row_idx, col_idx]
        if (value <= 0) {
          next
        }
        category <- element_category[[colnames(element_heat)[col_idx]]]
        point_col <- category_colors[[category]]
        if (is.null(point_col)) {
          point_col <- "#72B7B2"
        }
        points(col_idx, row_idx, pch = 16, cex = 0.55 + 1.15 * sqrt(value / max_count), col = point_col)
      }
    }
  }

  par(mar = c(8, 5, 4, 2))
  bar_cols <- category_colors[top_elements$category]
  bar_cols[is.na(bar_cols)] <- "#72B7B2"
  labels <- paste(top_elements$element, top_elements$category, sep = "\n")
  barplot(
    top_elements$total_numeric,
    names.arg = labels,
    las = 2,
    cex.names = 0.7,
    ylab = "Occurrence count",
    col = bar_cols,
    border = NA
  )
  title("top promoter cis-elements")
}

pdf(file.path(outdir, "promoter_cis_elements.pdf"), width = 12, height = 6)
draw_plot()
dev.off()

png(file.path(outdir, "promoter_cis_elements.png"), width = 1800, height = 900, res = 160)
draw_plot()
dev.off()
