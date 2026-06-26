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
| Gene family information summary | `Reference/Long_Weixiong_20240323_1_GDSL/R/5.GeneFamily_Info.R` | `bin/genefam/summarize_family.py`; `scripts/plot_family_counts.R`; standard report family count outputs | partial | Current output covers counts; protein length, molecular weight, pI, hydrophobicity, and species-tree-adjacent boxplots still need publication-style plotting. |
| Tree + motif + gene structure + domain | `Reference/Long_Weixiong_20240323_1_GDSL/R/6.tree.R` | `build_tree_feature_matrix.py`; `scripts/plot_tree_features.R`; `PLOT_TREE_FEATURES`; `tables/tree_feature_matrix.tsv`; `plots/tree_features.pdf/png` | partial | Combined tree-ordered feature tracks now exist; true per-gene MEME occurrence tracks, clade/group annotation, and richer domain architecture glyphs still need publication-level refinement. |
| JCVI/collinearity Ka/Ks | `Reference/Long_Weixiong_20240323_1_GDSL/R/8.collinearity_kaks.R` | `scripts/plot_kaks.R`; WGD branch `plots/ks_distribution.pdf/png` | partial | Current Ks plot is basic; needs duplicate-type/species facets and WGD peak/layer annotations. |
| MCScanX duplicate type + Ka/Ks | `Reference/Long_Weixiong_20240323_1_GDSL/R/9.mcscanx_KaKs.R` | `bin/genefam/build_mcscanx_kaks_handoff.py`; WGD raw handoff tables; `scripts/plot_kaks.R` | partial | Need MCScanX duplicate-type grouped Ka/Ks panels matching the reference boxplot/beeswarm style. |
| MCScanX/circlize synteny | `Reference/Long_Weixiong_20240323_1_GDSL/R/9.Circos_*.R` | `build_circlize_inputs.py`; `scripts/plot_mcscanx_circlize.R`; `PLOT_MCSCANX_CIRCLIZE` | partial | Current multi-link circlize exists; needs species-specific window density tracks and duplicate-type tracks. |
| promoter cis-element | `Reference/Long_Weixiong_20240323_1_GDSL/R/10.promoter.R` | `extract_promoters.py`; `build_promoter_cis_elements.py`; `scripts/plot_promoter_cis_elements.R`; `PLOT_PROMOTER_CIS_ELEMENTS`; `tables/promoter_cis_elements.tsv`; `tables/promoter_cis_gene_matrix.tsv`; `tables/promoter_cis_category_summary.tsv`; `plots/promoter_cis_elements.pdf/png` | partial | PlantCARE-style category matrix and top-element summary now exist; richer dot heatmap styling and per-element biological annotation tracks still need refinement. |
| PPI network | `Reference/Long_Weixiong_20240323_1_GDSL/R/11.ppi.R` | `build_ppi_tables.py`; `scripts/plot_ppi_ggnetview.R`; `PLOT_PPI_GGNETVIEW`; `tables/ppi_edges.tsv`; `tables/ppi_nodes.tsv`; `tables/ppi_hubs.tsv`; `plots/ppi_ggnetview.pdf/png` | partial | ggNetView-based plotting and hub summaries now exist; upstream orthology-to-reference-network construction remains a user-provided PPI edge-table input for now. |
| RNA-seq expression heatmap | `Reference/Long_Weixiong_20240323_1_GDSL/R/12.rnaseq.R` | `subset_expression_matrix.py`; `scripts/plot_expression_heatmap.R` | partial | Basic heatmap exists; sample annotations, treatment ordering, replicate aggregation, and group-aware legends need enhancement. |
| Large-scale copy number and expansion | `Reference/Large-Scale Plant Genomic Identification and Analysis Uncover ASMT:COMT Copy Number Variation Driving Melatonin Dosage Balance./source_code/Figure_1C_1052sp.py`; `Figure_4B_Copy_Number.tsv`; `Figure_5B_Copy_Number.py` | family count summary; standard report | partial | Need species-tree ordered copy-number plots, pan/core/dispensable summaries when input is available, and large-species labels. |
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
