args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_ppi_ggnetview.R --args <ppi_edges.tsv> <ppi_nodes.tsv> <outdir> <status.tsv>")
}

edge_file <- args[[1]]
node_file <- args[[2]]
outdir <- args[[3]]
status_file <- args[[4]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
dir.create(dirname(status_file), recursive = TRUE, showWarnings = FALSE)

write_status <- function(status, package, version, note) {
  status_df <- data.frame(
    check = "ppi_ggnetview_plot",
    status = status,
    package = package,
    version = version,
    note = note,
    stringsAsFactors = FALSE
  )
  write.table(status_df, status_file, sep = "\t", quote = FALSE, row.names = FALSE)
}

write_placeholder <- function(message) {
  pdf(file.path(outdir, "ppi_ggnetview.pdf"), width = 8, height = 5)
  plot.new()
  text(0.5, 0.55, "ggNetView PPI plot unavailable", cex = 1.2)
  text(0.5, 0.42, message, cex = 0.85)
  dev.off()
  png(file.path(outdir, "ppi_ggnetview.png"), width = 1200, height = 800, res = 160)
  plot.new()
  text(0.5, 0.55, "ggNetView PPI plot unavailable", cex = 1.2)
  text(0.5, 0.42, message, cex = 0.85)
  dev.off()
}

if (!requireNamespace("ggNetView", quietly = TRUE)) {
  write_status("missing_dependency", "ggNetView", "version_not_detected", "ggNetView is not installed; PPI plot was skipped.")
  write_placeholder("Missing R package: ggNetView")
  quit(save = "no", status = 0)
}
if (!requireNamespace("ggplot2", quietly = TRUE) || !requireNamespace("patchwork", quietly = TRUE)) {
  write_status("missing_dependency", "ggplot2_or_patchwork", "version_not_detected", "Required plotting packages are missing; PPI plot was skipped.")
  write_placeholder("Missing R package: ggplot2 or patchwork")
  quit(save = "no", status = 0)
}

suppressPackageStartupMessages({
  library(ggNetView)
  library(ggplot2)
  library(patchwork)
})

edges <- read.delim(edge_file, check.names = FALSE)
nodes <- read.delim(node_file, check.names = FALSE)
if (nrow(edges) == 0) {
  write_status("no_edges", "ggNetView", as.character(utils::packageVersion("ggNetView")), "No PPI edges were available for plotting.")
  write_placeholder("No PPI edges were available")
  quit(save = "no", status = 0)
}

plots <- list()
for (species_name in unique(edges$species)) {
  species_edges <- edges[edges$species == species_name, c("source", "target", "weight")]
  names(species_edges) <- c("Source", "Target", "weight")
  species_nodes <- unique(c(species_edges$Source, species_edges$Target))
  node_annotation <- data.frame(Id = species_nodes, stringsAsFactors = FALSE)
  node_annotation <- merge(
    node_annotation,
    nodes[, c("node", "type", "domain"), drop = FALSE],
    by.x = "Id",
    by.y = "node",
    all.x = TRUE
  )
  node_annotation$Type[is.na(node_annotation$type)] <- "Others"
  node_annotation$Type[!is.na(node_annotation$type)] <- node_annotation$type[!is.na(node_annotation$type)]
  node_annotation$Domain <- node_annotation$domain
  node_annotation$domain <- NULL
  node_annotation$type <- NULL

  graph_obj <- ggNetView::build_graph_from_df(
    df = species_edges,
    node_annotation = node_annotation,
    directed = FALSE,
    module.method = "Fast_greedy",
    top_modules = 15
  )
  plots[[species_name]] <- ggNetView::ggNetView(
    graph_obj = graph_obj,
    layout = "diamond",
    center = FALSE,
    shrink = 0.85,
    layout.module = "adjacent",
    pointsize = c(3, 8),
    group.by = "Modularity",
    fill.by = "Type",
    seed = 1115,
    add_group_outer = TRUE,
    curve = TRUE,
    label = FALSE
  ) + ggplot2::ggtitle(species_name)
}

combined <- patchwork::wrap_plots(plots, ncol = 1)
ggplot2::ggsave(filename = file.path(outdir, "ppi_ggnetview.pdf"), plot = combined, width = 8, height = max(6, 4 * length(plots)))
ggplot2::ggsave(filename = file.path(outdir, "ppi_ggnetview.png"), plot = combined, width = 8, height = max(6, 4 * length(plots)), dpi = 160)
write_status("ready", "ggNetView", as.character(utils::packageVersion("ggNetView")), "ggNetView PPI plot generated successfully.")
