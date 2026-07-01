# Reference Modules 08-12 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build GeneFam-Pipeline modules `08_jcvi`, `09_mcscanx`, `10_promoter`, `11_ppi`, and `12_full_bioinformatics_report` as Reference-faithful, Whirly-tested workflow modules.

**Architecture:** Each module is a project-level runner driven by `project.yaml`, writing `inputs/`, `tables/`, `plots/`, `report/`, and `logs/` under `project.outdir`. Low-level parsers and command builders may reuse existing `bin/genefam/*` helpers, but the module contract, report text, and visual outputs must be mapped from `Reference/Long_Weixiong_20240323_1_GDSL/Evolution_LWX_GDSL_2024.md` and the corresponding R scripts. External tools are executed when available; otherwise the module records explicit dependency status without hiding skipped work.

**Tech Stack:** Python 3, YAML, `/usr/local/bin/R`, ggplot2/ggtree/circlize/ggNetView, JCVI, MCScanX, BLAST/DIAMOND, seqkit, KaKs_Calculator-compatible tables.

---

### Task 1: Reference-to-Pipeline Mapping

**Files:**
- Create: `docs/reference_to_pipeline/08_12_reference_module_mapping.md`
- Read: `Reference/Long_Weixiong_20240323_1_GDSL/Evolution_LWX_GDSL_2024.md`
- Read: `Reference/Long_Weixiong_20240323_1_GDSL/R/8.collinearity_kaks.R`
- Read: `Reference/Long_Weixiong_20240323_1_GDSL/R/9.Circos_AT.R`
- Read: `Reference/Long_Weixiong_20240323_1_GDSL/R/9.mcscanx_KaKs.R`
- Read: `Reference/Long_Weixiong_20240323_1_GDSL/R/10.promoter.R`
- Read: `Reference/Long_Weixiong_20240323_1_GDSL/R/11.ppi.R`

- [ ] **Step 1: Write the mapping document**

Record, for each module, the Reference commands, required inputs, generated tables, generated plots, tool dependencies, and engineering adaptation.

- [ ] **Step 2: Verify the mapping contains every required module**

Run: `rg -n "08_jcvi|09_mcscanx|10_promoter|11_ppi|12_full_bioinformatics_report" docs/reference_to_pipeline/08_12_reference_module_mapping.md`

Expected: one or more hits for every module.

- [ ] **Step 3: Commit**

Run:
```bash
git add docs/superpowers/plans/2026-07-02-reference-modules-08-12.md docs/reference_to_pipeline/08_12_reference_module_mapping.md HISTORY.md
git commit -m "docs: map reference modules 08-12"
```

### Task 2: 08_jcvi Module

**Files:**
- Create: `tests/test_run_jcvi_module.py`
- Create: `bin/genefam/run_jcvi_module.py`
- Create: `scripts/plot_jcvi_kaks.R`
- Modify: `projects/Whirly_2026/project.yaml`
- Modify: `HISTORY.md`

- [ ] **Step 1: Write the failing test**

Test that `run_jcvi_module.py` creates `08_jcvi/inputs`, `08_jcvi/tables`, `08_jcvi/plots`, `08_jcvi/report`, and `08_jcvi/logs`; prepares species BED/pep inputs; writes adjacent pair manifest; writes JCVI `seqids` and `layout`; writes command and dependency/run status tables; and creates a report.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_run_jcvi_module.py -q`

Expected: FAIL because `bin/genefam/run_jcvi_module.py` does not exist.

- [ ] **Step 3: Implement 08_jcvi**

Use existing `prepare_jcvi_collinearity.py` and `run_jcvi_collinearity.py` where appropriate. Add Reference-style outputs: `tables/jcvi_pair_manifest.tsv`, `tables/jcvi_input_status.tsv`, `inputs/seqids`, `inputs/layout`, `logs/jcvi_command_status.tsv`, `logs/jcvi_run_status.tsv`, `report/jcvi_summary.md`, and optional `plots/8.jcvi_Kaks.pdf/png` when Ka/Ks tables are available.

- [ ] **Step 4: Verify tests and Whirly**

Run:
```bash
python -m pytest tests/test_run_jcvi_module.py -q
conda run -n GeneFamilyFlow python bin/genefam/run_jcvi_module.py --config projects/Whirly_2026/project.yaml
```

Inspect `projects/Whirly_2026/results/08_jcvi/report/jcvi_summary.md` and generated status tables.

- [ ] **Step 5: Commit**

Run:
```bash
git add bin/genefam/run_jcvi_module.py scripts/plot_jcvi_kaks.R tests/test_run_jcvi_module.py projects/Whirly_2026/project.yaml HISTORY.md docs/reference_to_pipeline/08_12_reference_module_mapping.md
git commit -m "feat: add reference-style jcvi module"
```

### Task 3: 09_mcscanx Module

**Files:**
- Create: `tests/test_run_mcscanx_module.py`
- Create: `bin/genefam/run_mcscanx_module.py`
- Create: `scripts/plot_mcscanx_circlize_reference.R`
- Create: `scripts/plot_mcscanx_kaks_reference.R`
- Modify: `projects/Whirly_2026/project.yaml`
- Modify: `HISTORY.md`

- [ ] **Step 1: Write the failing test**

Test that the module prepares MCScanX self inputs for each species, records tool status, writes family BED and MCScanX GFF files, writes self-run commands, parses tandem/WGD pairs when outputs exist, creates circlize-ready chromosome/link/density/type tables, and writes Reference-style report paths.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_run_mcscanx_module.py -q`

Expected: FAIL because `bin/genefam/run_mcscanx_module.py` does not exist.

- [ ] **Step 3: Implement 09_mcscanx**

Reuse `build_mcscanx_self_inputs.py` and `run_mcscanx_self.py`, but expose a clean module runner. The circlize R script must replicate the Reference tracks: chromosome ring, family gene labels, sliding-window density, gene duplicate type color track, tandem/WGD links, and legends.

- [ ] **Step 4: Verify tests and Whirly**

Run:
```bash
python -m pytest tests/test_run_mcscanx_module.py -q
conda run -n GeneFamilyFlow python bin/genefam/run_mcscanx_module.py --config projects/Whirly_2026/project.yaml
```

Inspect `projects/Whirly_2026/results/09_mcscanx/report/mcscanx_summary.md`, `tables/`, `plots/`, and `logs/`.

- [ ] **Step 5: Commit**

Run:
```bash
git add bin/genefam/run_mcscanx_module.py scripts/plot_mcscanx_circlize_reference.R scripts/plot_mcscanx_kaks_reference.R tests/test_run_mcscanx_module.py projects/Whirly_2026/project.yaml HISTORY.md
git commit -m "feat: add reference-style mcscanx module"
```

### Task 4: 10_promoter Module

**Files:**
- Create: `tests/test_run_promoter_module.py`
- Create: `bin/genefam/run_promoter_module.py`
- Create: `scripts/plot_promoter_cis_reference.R`
- Modify: `projects/Whirly_2026/project.yaml`
- Modify: `HISTORY.md`

- [ ] **Step 1: Write the failing test**

Test that the module extracts 2 kb upstream promoter BED/FASTA from cleaned GFF3/genome paths, writes PlantCARE submission split files, optionally integrates PlantCARE `.tab` or user cis-element tables, produces Reference-style promoter heatmaps, and records missing cis input without stopping the workflow.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_run_promoter_module.py -q`

Expected: FAIL because `bin/genefam/run_promoter_module.py` does not exist.

- [ ] **Step 3: Implement 10_promoter**

Use `extract_promoters.py`, `split_promoter_fasta_for_plantcare.py`, and `build_promoter_cis_elements.py` as helpers. The R plot should replicate the Reference heatmap: white tiles, square count points, text counts, nested functional groups, species tree inserted above when a tree is available, and two plot groups for hormone/stress and light/development.

- [ ] **Step 4: Verify tests and Whirly**

Run:
```bash
python -m pytest tests/test_run_promoter_module.py -q
conda run -n GeneFamilyFlow python bin/genefam/run_promoter_module.py --config projects/Whirly_2026/project.yaml
```

Inspect `projects/Whirly_2026/results/10_promoter/report/promoter_summary.md`.

- [ ] **Step 5: Commit**

Run:
```bash
git add bin/genefam/run_promoter_module.py scripts/plot_promoter_cis_reference.R tests/test_run_promoter_module.py projects/Whirly_2026/project.yaml HISTORY.md
git commit -m "feat: add reference-style promoter module"
```

### Task 5: 11_ppi Module

**Files:**
- Create: `tests/test_run_ppi_module.py`
- Create: `bin/genefam/run_ppi_module.py`
- Create: `scripts/plot_ppi_ggnetview_reference.R`
- Modify: `projects/Whirly_2026/project.yaml`
- Modify: `HISTORY.md`

- [ ] **Step 1: Write the failing test**

Test that the module derives family peptide FASTA by species, transfers AraNet edges through reciprocal Arabidopsis BLAST evidence, writes homology/evidence/node/edge tables, creates ggNetView-ready annotations, and writes per-species ggNetView plot output.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_run_ppi_module.py -q`

Expected: FAIL because `bin/genefam/run_ppi_module.py` does not exist.

- [ ] **Step 3: Implement 11_ppi**

Use `build_aranet_ppi_from_reciprocal_blast.py` and `build_ppi_tables.py`, but keep the Reference logic: all family peptides blast to Arabidopsis, Arabidopsis blasts back to all species, AraNet edge weight filter, species-specific endpoint filtering, Pfam/domain annotation when available, and ggNetView plotting with `layout="diamond"`, `layout.module="adjacent"`, `module.method="Fast_greedy"`, and `fill.by="Type"`.

- [ ] **Step 4: Verify tests and Whirly**

Run:
```bash
python -m pytest tests/test_run_ppi_module.py -q
conda run -n GeneFamilyFlow python bin/genefam/run_ppi_module.py --config projects/Whirly_2026/project.yaml
```

Inspect `projects/Whirly_2026/results/11_ppi/report/ppi_summary.md` and `plots/ppi_ggnetview.pdf/png`.

- [ ] **Step 5: Commit**

Run:
```bash
git add bin/genefam/run_ppi_module.py scripts/plot_ppi_ggnetview_reference.R tests/test_run_ppi_module.py projects/Whirly_2026/project.yaml HISTORY.md
git commit -m "feat: add reference-style ppi module"
```

### Task 6: 12_full_bioinformatics_report

**Files:**
- Create: `tests/test_run_full_report_module.py`
- Create: `bin/genefam/run_full_bioinformatics_report.py`
- Modify: `projects/Whirly_2026/project.yaml`
- Modify: `HISTORY.md`

- [ ] **Step 1: Write the failing test**

Test that the report module reads results from modules 01-11 and writes a complete Markdown report with Methods, software versions, parameters, Results, figure-by-figure close reading, QC warnings, and reproducibility commands.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_run_full_report_module.py -q`

Expected: FAIL because `bin/genefam/run_full_bioinformatics_report.py` does not exist.

- [ ] **Step 3: Implement 12_full_bioinformatics_report**

Collect all module reports, status tables, software versions, plots, and key tables. Write `results/12_full_bioinformatics_report/report/full_bioinformatics_report.md` and `tables/figure_interpretation_index.tsv`.

- [ ] **Step 4: Verify tests and Whirly**

Run:
```bash
python -m pytest tests/test_run_full_report_module.py -q
conda run -n GeneFamilyFlow python bin/genefam/run_full_bioinformatics_report.py --config projects/Whirly_2026/project.yaml
```

Inspect the final Markdown report manually.

- [ ] **Step 5: Commit**

Run:
```bash
git add bin/genefam/run_full_bioinformatics_report.py tests/test_run_full_report_module.py projects/Whirly_2026/project.yaml HISTORY.md
git commit -m "feat: add full bioinformatics report module"
```

### Task 7: End-to-End Acceptance

**Files:**
- Modify: `README.md`
- Modify: `docs/module_usage.zh-CN.md`
- Modify: `HISTORY.md`

- [ ] **Step 1: Run targeted module tests**

Run:
```bash
python -m pytest tests/test_run_jcvi_module.py tests/test_run_mcscanx_module.py tests/test_run_promoter_module.py tests/test_run_ppi_module.py tests/test_run_full_report_module.py -q
```

- [ ] **Step 2: Run Whirly modules 08-12**

Run:
```bash
conda run -n GeneFamilyFlow python bin/genefam/run_jcvi_module.py --config projects/Whirly_2026/project.yaml
conda run -n GeneFamilyFlow python bin/genefam/run_mcscanx_module.py --config projects/Whirly_2026/project.yaml
conda run -n GeneFamilyFlow python bin/genefam/run_promoter_module.py --config projects/Whirly_2026/project.yaml
conda run -n GeneFamilyFlow python bin/genefam/run_ppi_module.py --config projects/Whirly_2026/project.yaml
conda run -n GeneFamilyFlow python bin/genefam/run_full_bioinformatics_report.py --config projects/Whirly_2026/project.yaml
```

- [ ] **Step 3: Inspect generated outputs**

Check each module has `inputs/`, `tables/`, `plots/`, `report/`, and `logs/` where applicable. Open or render at least one plot per plotting module.

- [ ] **Step 4: Commit final docs**

Run:
```bash
git add README.md docs/module_usage.zh-CN.md HISTORY.md
git commit -m "docs: document reference-style modules 08-12"
```
