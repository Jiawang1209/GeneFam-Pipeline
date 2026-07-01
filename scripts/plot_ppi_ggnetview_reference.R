#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4) {
  stop("Usage: plot_ppi_ggnetview_reference.R <ppi_edges.tsv> <ppi_nodes.tsv> <outdir> <status.tsv>", call. = FALSE)
}

edge_file <- args[[1]]
node_file <- args[[2]]
outdir <- args[[3]]
status_file <- args[[4]]
overview_status_file <- file.path(dirname(status_file), "ppi_overview_status.tsv")

dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
dir.create(dirname(status_file), recursive = TRUE, showWarnings = FALSE)

write_status <- function(path, check, status, package, version, note) {
  status_df <- data.frame(check = check, status = status, package = package, version = version, note = note, stringsAsFactors = FALSE)
  write.table(status_df, path, sep = "\t", quote = FALSE, row.names = FALSE)
}

write_placeholder <- function(message) {
  for (plot_name in c("ppi", "ppi_ggnetview")) {
    pdf(file.path(outdir, paste0(plot_name, ".pdf")), width = 8, height = 5)
    plot.new()
    text(0.5, 0.55, "PPI plot unavailable", cex = 1.2)
    text(0.5, 0.42, message, cex = 0.85)
    dev.off()
    png(file.path(outdir, paste0(plot_name, ".png")), width = 1200, height = 800, res = 160)
    plot.new()
    text(0.5, 0.55, "PPI plot unavailable", cex = 1.2)
    text(0.5, 0.42, message, cex = 0.85)
    dev.off()
  }
}

if (!requireNamespace("ggNetView", quietly = TRUE)) {
  write_status(status_file, "ppi_ggnetview_plot", "missing_dependency", "ggNetView", "version_not_detected", "ggNetView is not installed; PPI plot was skipped.")
  write_status(overview_status_file, "ppi_overview_plot", "missing_dependency", "ggNetView", "version_not_detected", "ggNetView is not installed; PPI overview plot was skipped.")
  write_placeholder("Missing R package: ggNetView")
  quit(save = "no", status = 0)
}

if (!requireNamespace("ggplot2", quietly = TRUE) || !requireNamespace("patchwork", quietly = TRUE)) {
  write_status(status_file, "ppi_ggnetview_plot", "missing_dependency", "ggplot2_or_patchwork", "version_not_detected", "Required plotting packages are missing; PPI plot was skipped.")
  write_status(overview_status_file, "ppi_overview_plot", "missing_dependency", "ggplot2_or_patchwork", "version_not_detected", "Required plotting packages are missing; PPI overview plot was skipped.")
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
  write_status(status_file, "ppi_ggnetview_plot", "no_edges", "ggNetView", as.character(utils::packageVersion("ggNetView")), "No PPI edges were available for plotting.")
  write_status(overview_status_file, "ppi_overview_plot", "no_edges", "ggNetView", as.character(utils::packageVersion("ggNetView")), "No PPI edges were available for overview plotting.")
  write_placeholder("No PPI edges were available")
  quit(save = "no", status = 0)
}

ppi_list <- list()
for (spe in unique(edges$species)) {
  df <- edges[edges$species == spe, c("source", "target", "weight")]
  names(df) <- c("Source", "Target", "weight")
  node_annotation <- data.frame(Id = unique(c(df$Source, df$Target)), stringsAsFactors = FALSE)
  node_annotation <- merge(node_annotation, nodes[, c("node", "type"), drop = FALSE], by.x = "Id", by.y = "node", all.x = TRUE)
  node_annotation$Type <- ifelse(is.na(node_annotation$type), "Others", node_annotation$type)
  node_annotation$type <- NULL

  obj <- ggNetView::build_graph_from_df(
    df = df,
    node_annotation = node_annotation,
    directed = FALSE,
    module.method = "Fast_greedy",
    top_modules = 15
  )

  ppi_list[[spe]] <- ggNetView::ggNetView(
    graph_obj = obj,
    layout = "diamond",
    center = FALSE,
    shrink = 0.85,
    layout.module = "adjacent",
    pointsize = c(3, 8),
    group.by = "Modularity",
    fill.by = "Type",
    fill = c("#fa9fb5", "#d9d9d9"),
    seed = 1115,
    add_group_outer = TRUE,
    curve = TRUE,
    label = FALSE
  ) +
    ggplot2::ggtitle(label = spe) +
    ggplot2::theme(legend.background = ggplot2::element_blank())
}

p_combine <- patchwork::wrap_plots(ppi_list, nrow = ceiling(sqrt(length(ppi_list))))
ggplot2::ggsave(filename = file.path(outdir, "ppi_ggnetview.pdf"), plot = p_combine, height = max(6, 5 * length(ppi_list)), width = 20)
ggplot2::ggsave(filename = file.path(outdir, "ppi_ggnetview.png"), plot = p_combine, height = max(6, 5 * length(ppi_list)), width = 20, dpi = 160)
file.copy(file.path(outdir, "ppi_ggnetview.pdf"), file.path(outdir, "ppi.pdf"), overwrite = TRUE)
file.copy(file.path(outdir, "ppi_ggnetview.png"), file.path(outdir, "ppi.png"), overwrite = TRUE)

write_status(status_file, "ppi_ggnetview_plot", "ready", "ggNetView", as.character(utils::packageVersion("ggNetView")), "ggNetView PPI plot generated successfully.")
write_status(overview_status_file, "ppi_overview_plot", "ready_ggnetview_alias", "ggNetView", as.character(utils::packageVersion("ggNetView")), "Reference-named ppi.pdf/png are aliases of the ggNetView PPI visualization.")
