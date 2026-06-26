args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4) {
  stop("Usage: /usr/local/bin/R --vanilla --slave -f plot_gene_family_info.R --args <copy_number.tsv> <copy_number_summary.tsv> <protein_properties.tsv> <outdir>")
}

copy_path <- args[[1]]
summary_path <- args[[2]]
protein_path <- args[[3]]
outdir <- args[[4]]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

copy_number <- read.delim(copy_path, check.names = FALSE)
copy_summary <- read.delim(summary_path, check.names = FALSE)
protein_properties <- read.delim(protein_path, check.names = FALSE)

if (nrow(copy_number) == 0) {
  stop("copy-number table must not be empty")
}

copy_number$member_numeric <- suppressWarnings(as.numeric(copy_number$member_count))
copy_number$member_numeric[is.na(copy_number$member_numeric)] <- 0
copy_number <- copy_number[order(copy_number$member_numeric, decreasing = TRUE), ]

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
  layout(matrix(c(1, 2, 3, 3), nrow = 2, byrow = TRUE), heights = c(1, 1.1))

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
