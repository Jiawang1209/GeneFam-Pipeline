# Reference Plotting Reuse

The `Reference/` directory is part of the design source for GeneFam-Pipeline. It contains paper-derived scripts and outputs that can guide plotting modules.

## Reuse Policy

Use reference scripts as templates, not as mutable pipeline code.

Allowed:

- Inspect reference R/Python scripts before implementing related plots.
- Reuse chart types, biological grouping logic, color strategies, and output concepts.
- Port useful logic into parameterized scripts under `scripts/`.
- Mention the reference source in comments when a pipeline script is adapted from a specific example.

Not allowed unless explicitly requested:

- Editing files under `Reference/`.
- Calling reference scripts directly as pipeline modules.
- Copying absolute paths from reference scripts.
- Preserving one-off species assumptions without moving them into configuration.

## Current Useful References

- `Reference/Long_Weixiong_20240323_1_GDSL/R/5.GeneFamily_Info.R`: gene family summary and species-tree adjacent plots.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/6.tree.R`: phylogenetic tree annotation.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/8.collinearity_kaks.R`: JCVI-style collinearity and Ka/Ks plotting.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/8.collinearity_kaks.R`: Ka/Ks distribution plotting.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/9.mcscanx_KaKs.R`: MCScanX duplicate type plus Ka/Ks plotting.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/10.promoter.R`: promoter cis-element heatmap/dot-style summaries.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/11.ppi.R`: ggNetView PPI network plotting.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/12.rnaseq.R`: RNA-seq expression heatmaps.
- `Reference/Large-Scale Plant Genomic Identification and Analysis Uncover ASMT:COMT Copy Number Variation Driving Melatonin Dosage Balance./source_code/`: large-scale copy-number, synteny, and expression figure scripts.

## Reference Figure Alignment Matrix

Status vocabulary is `done / partial / missing`.

| Plot target | Reference source | GeneFam-Pipeline module/output | Status | Gap to close |
|---|---|---|---|---|
| Gene family information summary | `Reference/Long_Weixiong_20240323_1_GDSL/R/5.GeneFamily_Info.R` | `bin/genefam/summarize_family.py`; `build_gene_family_info.py`; `scripts/plot_family_counts.R`; `scripts/plot_gene_family_info.R`; `PLOT_GENE_FAMILY_INFO`; `tables/gene_family_copy_number.tsv`; `tables/gene_family_protein_properties.tsv`; `plots/gene_family_info_summary.pdf/png` | partial | Copy-number class and protein property panels now exist; species-tree-adjacent ordering, richer taxonomy groups, and publication-style boxplot annotations still need refinement. |
| Tree + motif + gene structure + domain | `Reference/Long_Weixiong_20240323_1_GDSL/R/6.tree.R` | `build_tree_feature_matrix.py`; `scripts/plot_tree_features.R`; `PLOT_TREE_FEATURES`; `tables/tree_feature_matrix.tsv`; `plots/tree_features.pdf/png` | done | Tree-ordered matrix now includes per-gene motif occurrence tracks, motif architecture labels, gene-structure summaries, domain coverage, and domain architecture labels. |
| JCVI/collinearity Ka/Ks | `Reference/Long_Weixiong_20240323_1_GDSL/R/8.collinearity_kaks.R` | `bin/genefam/build_kaks_plot_annotations.py`; `scripts/plot_kaks.R`; WGD branch `tables/kaks_wgd_annotations.tsv`; `plots/ks_distribution.pdf/png` | done | Ks distribution now supports WGD peak/layer annotation labels for alpha, beta, gamma, theta or custom configured events. |
| MCScanX duplicate type + Ka/Ks | `Reference/Long_Weixiong_20240323_1_GDSL/R/9.mcscanx_KaKs.R` | `bin/genefam/build_duplicate_type_kaks.py`; `scripts/plot_duplicate_type_kaks.R`; WGD branch `plots/duplicate_type_kaks.pdf/png` | done | Duplicate-type grouped Ks and Ka/Ks boxplot/point panels now exist with pair-count summary tables and skipped-pair QC. |
| MCScanX/circlize synteny | `Reference/Long_Weixiong_20240323_1_GDSL/R/9.Circos_*.R` | `build_circlize_inputs.py`; `scripts/plot_mcscanx_circlize.R`; `PLOT_MCSCANX_CIRCLIZE`; `tables/circlize_link_density.tsv`; `tables/circlize_duplicate_type_tracks.tsv`; `plots/mcscanx_circlize.pdf/png` | done | Circlize output now includes chromosome sectors, syntenic links, linked-gene density windows, and duplicate-type track rows; when no explicit duplicate table is provided, linked genes are labelled as syntenic. |
| promoter cis-element | `Reference/Long_Weixiong_20240323_1_GDSL/R/10.promoter.R` | `extract_promoters.py`; `build_promoter_cis_elements.py`; `scripts/plot_promoter_cis_elements.R`; `PLOT_PROMOTER_CIS_ELEMENTS`; `tables/promoter_cis_elements.tsv`; `tables/promoter_cis_gene_matrix.tsv`; `tables/promoter_cis_category_summary.tsv`; `plots/promoter_cis_elements.pdf/png` | partial | PlantCARE-style category matrix and top-element summary now exist; richer dot heatmap styling and per-element biological annotation tracks still need refinement. |
| PPI network | `Reference/Long_Weixiong_20240323_1_GDSL/R/11.ppi.R` | `build_ppi_tables.py`; `scripts/plot_ppi_ggnetview.R`; `PLOT_PPI_GGNETVIEW`; `tables/ppi_edges.tsv`; `tables/ppi_nodes.tsv`; `tables/ppi_hubs.tsv`; `plots/ppi_ggnetview.pdf/png` | partial | ggNetView-based plotting and hub summaries now exist; upstream orthology-to-reference-network construction remains a user-provided PPI edge-table input for now. |
| RNA-seq expression heatmap | `Reference/Long_Weixiong_20240323_1_GDSL/R/12.rnaseq.R` | `build_expression_summary.py`; `scripts/plot_expression_heatmap.R`; `PLOT_EXPRESSION_HEATMAP`; `tables/expression_sample_metadata.tsv`; `tables/expression_group_matrix.tsv`; `tables/expression_gene_summary.tsv`; `plots/expression_heatmap.pdf/png` | done | Sample metadata normalization, treatment/timepoint labels, replicate group averaging, gene response summaries, and PDF/PNG heatmap output now exist. |
| Large-scale copy number and expansion | `Reference/Large-Scale Plant Genomic Identification and Analysis Uncover ASMT:COMT Copy Number Variation Driving Melatonin Dosage Balance./source_code/Figure_1C_1052sp.py`; `Figure_4B_Copy_Number.tsv`; `Figure_5B_Copy_Number.py` | `build_gene_family_info.py`; `scripts/plot_gene_family_info.R`; standard report copy-number tables and plots | partial | Copy-number class summary exists; species-tree ordered large-scale copy-number plots, pan/core/dispensable summaries when input is available, and large-species labels still need refinement. |
| Large-scale Ks and pangenome comparison | `Reference/Large-Scale Plant Genomic Identification and Analysis Uncover ASMT:COMT Copy Number Variation Driving Melatonin Dosage Balance./source_code/Figure_2B_5F_Ks.py`; `Figure_3D_Core_Dispensable.py` | WGD raw handoff and Ks outputs | partial | Need pangenome/core/dispensable interpretation inputs and figure templates. |

## Report Alignment Requirements

- The final report must include a `Software version table` that records command-line tools and R packages, including ggNetView. Missing tools must be shown as `version_not_detected`.
- The final report must include `Figure result interpretation` sections for each plotted figure. Each section should state input data, what the figure shows, key observations, biological interpretation, QC warnings, and output path.
- Smoke/demo outputs must be labelled as smoke/demo evidence, not biological conclusions.
- The PPI path must explicitly depend on ggNetView and must not silently fall back to a different network plotting library.

## Implementation Rule

Every reusable plot script should expose a stable command interface:

```text
/usr/local/bin/R --vanilla --slave -f scripts/<plot>.R --args <input.tsv> <outdir>
```

Each script should write deterministic output names into the requested output directory.
