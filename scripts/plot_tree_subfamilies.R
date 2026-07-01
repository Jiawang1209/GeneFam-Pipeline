args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 5) {
  stop("Usage: R --vanilla --slave -f plot_tree_subfamilies.R --args <treefile> <outdir> <family_name> <min_size> <max_groups>")
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

if (!requireNamespace("ape", quietly = TRUE)) {
  stop("R package 'ape' is required for tree subfamily plotting")
}

tables_dir <- file.path(outdir, "tables")
plots_dir <- file.path(outdir, "plots")
dir.create(tables_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(plots_dir, recursive = TRUE, showWarnings = FALSE)

tree <- ape::read.tree(treefile)
if (is.null(tree$tip.label) || length(tree$tip.label) == 0) {
  stop("Tree has no tip labels")
}

tip_labels <- tree$tip.label
n_tips <- length(tip_labels)

parse_species <- function(label) {
  if (grepl("\\|", label, fixed = FALSE)) {
    return(strsplit(label, "\\|")[[1]][1])
  }
  if (grepl("_", label, fixed = TRUE)) {
    return(sub("\\|.*$", "", label))
  }
  "Unknown"
}

parse_gene <- function(label) {
  if (grepl("\\|", label, fixed = FALSE)) {
    parts <- strsplit(label, "\\|")[[1]]
    return(parts[length(parts)])
  }
  label
}

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
  hc <- hclust(as.dist(distances), method = "average")
  k <- target_k
  groups <- cutree(hc, k = k)
  while (k > 1 && min(table(groups)) < min_size) {
    k <- k - 1
    groups <- cutree(hc, k = k)
  }

  tree_order <- tree$tip.label
  group_order <- unique(groups[match(tree_order, names(groups))])
  group_labels <- setNames(paste0("C", seq_along(group_order)), group_order)
  unname(group_labels[as.character(groups[tree$tip.label])])
}

subfamilies <- assign_subfamilies(tree, min_size, max_groups)
assignments <- data.frame(
  tree_label = tip_labels,
  gene_id = vapply(tip_labels, parse_gene, character(1)),
  species_id = vapply(tip_labels, parse_species, character(1)),
  subfamily = subfamilies,
  tree_order = seq_along(tip_labels),
  stringsAsFactors = FALSE
)
assignments <- assignments[order(assignments$tree_order), ]

stats <- as.data.frame(
  table(assignments$species_id, assignments$subfamily),
  stringsAsFactors = FALSE
)
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
palette <- c("#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#1f78b4")
subfamily_cols <- setNames(rep(palette, length.out = length(subfamily_levels)), subfamily_levels)
tip_cols <- subfamily_cols[assignments$subfamily[match(tree$tip.label, assignments$tree_label)]]

plot_tree <- function() {
  old_par <- par(no.readonly = TRUE)
  on.exit(par(old_par), add = TRUE)
  par(mar = c(1, 1, 4, 1))
  ape::plot.phylo(
    tree,
    type = "fan",
    show.tip.label = TRUE,
    tip.color = tip_cols,
    cex = max(0.45, min(0.9, 18 / n_tips)),
    edge.color = "#8c8c8c",
    no.margin = TRUE,
    main = paste0(family_name, " phylogeny with auto subfamilies")
  )
  legend(
    "topleft",
    legend = names(subfamily_cols),
    col = subfamily_cols,
    lwd = 4,
    bty = "n",
    title = "Subfamily",
    cex = 0.85
  )
}

plot_stats <- function() {
  old_par <- par(no.readonly = TRUE)
  on.exit(par(old_par), add = TRUE)
  mat <- xtabs(count ~ species_id + subfamily, stats)
  mat <- mat[rev(rownames(mat)), , drop = FALSE]
  max_count <- max(mat)
  if (max_count == 0) {
    max_count <- 1
  }
  par(mar = c(5, 12, 6, 2))
  plot(
    NA,
    xlim = c(0.5, ncol(mat) + 0.5),
    ylim = c(0.5, nrow(mat) + 0.5),
    xlab = "",
    ylab = "",
    xaxt = "n",
    yaxt = "n",
    main = ""
  )
  title(main = paste0(family_name, " subfamily copy number"), line = 3.5)
  axis(3, at = seq_len(ncol(mat)), labels = colnames(mat), las = 1, line = 0.5)
  axis(2, at = seq_len(nrow(mat)), labels = rownames(mat), las = 1, font = 3)
  abline(h = seq_len(nrow(mat)), col = "#eeeeee")
  abline(v = seq_len(ncol(mat)), col = "#eeeeee")
  for (i in seq_len(nrow(mat))) {
    for (j in seq_len(ncol(mat))) {
      value <- mat[i, j]
      if (value > 0) {
        points(j, i, pch = 21, bg = subfamily_cols[colnames(mat)[j]], col = "#333333", cex = 1.2 + 2.8 * value / max_count)
        text(j, i, labels = value, cex = 0.8)
      }
    }
  }
  box()
}

pdf(file.path(plots_dir, "tree_subfamily.pdf"), width = 10, height = 10)
plot_tree()
dev.off()

png(file.path(plots_dir, "tree_subfamily.png"), width = 1800, height = 1800, res = 180)
plot_tree()
dev.off()

pdf(file.path(plots_dir, "tree_subfamily_species_stats.pdf"), width = max(6, 1.1 * length(subfamily_levels) + 4), height = max(5, 0.45 * length(species_levels) + 2.5))
plot_stats()
dev.off()

png(
  file.path(plots_dir, "tree_subfamily_species_stats.png"),
  width = max(1000, 180 * length(subfamily_levels) + 800),
  height = max(900, 90 * length(species_levels) + 500),
  res = 160
)
plot_stats()
dev.off()
