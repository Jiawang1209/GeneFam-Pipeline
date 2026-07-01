# Reference-to-Pipeline Mapping: Modules 08-12

本文件把 `Reference/Long_Weixiong_20240323_1_GDSL` 中的原始分析逻辑，逐步映射为 GeneFam-Pipeline 的项目级模块。开发原则是先复刻 Reference 的分析和图形表达，再做参数化、泛化和工程化。

## 08_jcvi

### Reference Source

- Markdown: `Evolution_LWX_GDSL_2024.md`, Step8 `collinearity` and Step8.1 `KaKs`.
- Plot script: `R/8.collinearity_kaks.R`.

### Reference Logic

1. 从所有物种 GFF3 中用 `python -m jcvi.formats.gff bed --type=mRNA --key=ID` 生成 BED。
2. 用 `python -m jcvi.formats.bed uniq` 对 BED 去冗余。
3. 按 BED 第 4 列 ID 从各物种 peptide FASTA 中提取 JCVI 需要的 `.pep` 文件。
4. 对物种链中的相邻物种执行：
   - `python -m jcvi.compara.catalog ortholog --dbtype prot --notex --no_strip_names speciesA speciesB`
   - `python -m jcvi.compara.synteny screen --minspan=30 --simple pair.anchors pair.anchors.simple`
5. 创建 JCVI `seqids` 和 `layout` 文件。
6. 用 `python -m jcvi.graphics.karyotype seqids layout --notex --figsize=14x12 --chrstyle=roundrect` 绘制物种间共线性 karyotype。
7. 从 `*.anchors.new` 中提取家族候选基因相关的共线性边，构建 `jcvi_kaks_all.file`、`KaKs_Gene_Pair`、`Kaks_Gene_ID`。
8. 将 Ka/Ks 结果整理为 `kaks.tab.xls`。
9. `R/8.collinearity_kaks.R` 绘制 Ka、Ks、Ka/Ks 三个 facet 的箱线图和 quasirandom 点，并添加 Ka/Ks=1 虚线。

### Pipeline Contract

Module directory: `results/08_jcvi/`

Required inputs:

- `results/04_identification/tables/family_candidates.tsv`
- `results/01_preprocess/species_clean_bank_manifest.tsv`
- cleaned protein/GFF3 paths from the manifest

Optional inputs:

- precomputed JCVI anchor files
- Ka/Ks result table
- species order or adjacent pair list from `project.yaml`

Outputs:

- `inputs/beds/<species>.bed`
- `inputs/peptides/<species>.pep`
- `inputs/seqids`
- `inputs/layout`
- `tables/jcvi_pair_manifest.tsv`
- `tables/jcvi_input_status.tsv`
- `tables/jcvi_kaks_gene_pairs.tsv` when anchor-derived pairs exist
- `logs/jcvi_commands.sh`
- `logs/jcvi_command_status.tsv`
- `logs/jcvi_run_status.tsv`
- `plots/jcvi_karyotype.pdf/png` when JCVI graphics succeeds
- `plots/8.jcvi_Kaks.pdf/png` when Ka/Ks input exists
- `report/jcvi_summary.md`

Engineering adaptation:

- The module should prepare all inputs even if JCVI is unavailable.
- Missing JCVI or Ka/Ks inputs must be recorded as status rows, not hidden.
- Adjacent-pair construction defaults to selected species order, but can be overridden in YAML.

## 09_mcscanx

### Reference Source

- Markdown: `Evolution_LWX_GDSL_2024.md`, Step9 `mcscanx` and Step9.1 `KaKs`.
- Plot scripts: `R/9.Circos_*.R`, `R/9.mcscanx_KaKs.R`.

### Reference Logic

1. Run or collect MCScanX self-analysis outputs per species:
   - `.gff`
   - `.blast`
   - `.collinearity`
   - `.tandem`
   - `.gene_type`
2. Extract family member BED per species, such as `AT.GF.bed`.
3. Extract tandem and WGD/segmental duplicated gene pairs involving family members.
4. Create per-species gene-pair tables, such as `AT.gene_pairs.csv` and `AT.gene_pairs.ID.csv`.
5. Use chromosome length `.fai` to build `Chr Start End` tables.
6. Build sliding windows, count family members per window, and draw circlize plots with:
   - chromosome ring
   - family gene labels
   - sliding-window density track
   - duplicate type color track
   - WGD/collinearity links
   - tandem links
   - gene type and duplicate legends
7. Step9.1 merges MCScanX duplicate-pair tables with `kaks.tab.xls`.
8. `R/9.mcscanx_KaKs.R` draws duplicate-type by Ka/Ks plots with boxplot, quasirandom points, facets by duplicate type and metric.

### Pipeline Contract

Module directory: `results/09_mcscanx/`

Required inputs:

- `results/04_identification/tables/family_candidates.tsv`
- `results/01_preprocess/species_clean_bank_manifest.tsv`
- chromosome length tables from preprocessing

Optional inputs:

- precomputed MCScanX self output directory
- Ka/Ks result table
- `MCScanX`, `diamond` or BLAST executables for real self-analysis

Outputs:

- `inputs/mcscanx_run/<species>.gff`
- `inputs/family_beds/<species>.GF.bed`
- `tables/mcscanx_self_status.tsv`
- `tables/mcscanx_run_status.tsv`
- `tables/mcscanx_gene_pairs.tsv`
- `tables/mcscanx_gene_pair_ids.tsv`
- `tables/circlize_chromosomes.tsv`
- `tables/circlize_gene_density.tsv`
- `tables/circlize_gene_types.tsv`
- `tables/circlize_duplicate_links.tsv`
- `logs/mcscanx_self_commands.sh`
- `logs/mcscanx_execution_status.tsv`
- `logs/mcscanx_execution.log`
- `plots/circos_<species>.pdf/png`
- `plots/9.mcscanx_KaKs.pdf/png` when Ka/Ks input exists
- `report/mcscanx_summary.md`

Engineering adaptation:

- MCScanX self is a required analytical branch, but execution can stop at prepared status when software is missing.
- circlize plotting must prioritize chromosome-level assemblies and report scaffold-heavy species as QC warnings.
- Reference plot structure is mandatory before any simplified overview plot is added.

## 10_promoter

### Reference Source

- Markdown: `Evolution_LWX_GDSL_2024.md`, Step10 `promoter`.
- Plot script: `R/10.promoter.R`.

### Reference Logic

1. Merge GFF3 gene records into `species_10.bed`.
2. Intersect family candidate IDs to create `original.ID.clean.bed`.
3. Split BED by species prefixes.
4. Use `seqkit subseq --bed --up-stream 2000 --only-flank genome.fa` to extract promoter FASTA.
5. Merge promoter sequences into `species_10.promoter.fa`.
6. Split large FASTA for PlantCARE submission.
7. Read PlantCARE `.tab` output and `cir_element.desc.20240509.xlsx`.
8. Count cis-elements by species and functional category.
9. Draw two Reference heatmaps:
   - hormone + stress
   - light responsiveness + growth/development
10. Heatmap style: white tile background, large square count points, text counts, nested functional labels, species tree inserted above.

### Pipeline Contract

Module directory: `results/10_promoter/`

Required inputs:

- `results/04_identification/tables/family_candidates.tsv`
- `results/01_preprocess/species_clean_bank_manifest.tsv`
- cleaned GFF3 and genome paths

Optional inputs:

- PlantCARE `.tab` files or a normalized cis-element table
- `cir_element.desc.20240509.xlsx`
- species tree from `06_phylogeny`

Outputs:

- `inputs/original.ID.clean.out`
- `tables/promoters.bed`
- `sequences/promoters.fa`
- `plantcare_submission/*.fa`
- `tables/promoter_cis_elements.tsv`
- `tables/promoter_cis_gene_matrix.tsv`
- `tables/promoter_cis_category_summary.tsv`
- `tables/promoter_cis_element_annotations.tsv`
- `plots/promoter1.pdf/png`
- `plots/species_promoter2.pdf/png`
- `logs/promoter_commands.sh`
- `logs/promoter_cis_status.tsv`
- `report/promoter_summary.md`

Engineering adaptation:

- If PlantCARE/cis input is absent, promoter extraction still succeeds and cis-element plotting is recorded as skipped.
- Species-prefix splitting should be replaced by manifest-based grouping.
- FASTA splitting must be configurable for very large families.

## 11_ppi

### Reference Source

- Markdown: `Evolution_LWX_GDSL_2024.md`, Step11 `ppi`.
- Plot script: `R/11.ppi.R`.

### Reference Logic

1. Start from identified family peptide FASTA.
2. Split family peptide IDs by species.
3. Build BLAST databases for full proteomes.
4. BLAST all species family proteins to Arabidopsis proteome.
5. BLAST Arabidopsis proteome back to all species.
6. Read AraNet edges.
7. Use reciprocal BLAST evidence to transfer Arabidopsis network edges to each target species.
8. Filter network edges by AraNet weight and within-species endpoints.
9. Extract PPI nodes and optionally annotate domains by Pfam scan.
10. Draw:
    - a ggraph overview network faceted by species
    - a ggNetView network per species with `layout="diamond"`, `module.method="Fast_greedy"`, `layout.module="adjacent"`, `fill.by="Type"`, and combined patchwork output

### Pipeline Contract

Module directory: `results/11_ppi/`

Required inputs:

- `results/04_identification/tables/family_candidates.tsv`
- `results/01_preprocess/species_clean_bank_manifest.tsv`
- AraNet edge file

Optional inputs:

- Pfam/domain annotation table for nodes
- precomputed BLAST/DIAMOND files

Outputs:

- `inputs/<species>.GF.pep.fasta`
- `tables/ppi_homology_best_hits.tsv`
- `tables/ppi_transfer_evidence.tsv`
- `tables/ppi_edges.tsv`
- `tables/ppi_nodes.tsv`
- `tables/node_annotation.tsv`
- `tables/species_ppi_annotation.tsv`
- `tables/ppi_hubs.tsv`
- `logs/ppi_blast_manifest.tsv`
- `logs/ppi_status.tsv`
- `plots/ppi.pdf/png`
- `plots/ppi_ggnetview.pdf/png`
- `report/ppi_summary.md`

Engineering adaptation:

- PPI must use ggNetView for the primary publication-style plot.
- AraNet is Arabidopsis reference evidence; species-level PPI must be inferred through reciprocal homology, not treated as direct target-species edges.
- Missing ggNetView should be recorded clearly while table generation remains usable.

## 12_full_bioinformatics_report

### Reference Source

- User requirement: produce a complete Markdown report for the whole workflow, including methods, versions, parameters, results, and close reading of every figure.
- Previous module reports from 01-11.

### Pipeline Contract

Module directory: `results/12_full_bioinformatics_report/`

Required inputs:

- all available module reports and status tables from 01-11
- plot files under module `plots/`
- software version collection

Outputs:

- `report/full_bioinformatics_report.md`
- `tables/figure_interpretation_index.tsv`
- `tables/software_versions.tsv`
- `tables/module_status_overview.tsv`
- `logs/report_build_status.tsv`

Report sections:

1. Project overview and input species.
2. Methods with software names, versions, and key parameters.
3. Results by module.
4. Figure-by-figure close reading.
5. QC warnings and missing optional inputs.
6. Reproducibility commands.

Engineering adaptation:

- The report must describe skipped modules as skipped, not as failed results.
- Every figure listed must have an interpretation paragraph.
- Software version rows must include both detected and missing tools.
