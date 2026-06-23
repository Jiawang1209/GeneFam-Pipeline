# GeneFam Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable Nextflow DSL2 pipeline for large-scale, multi-species gene family analysis with YAML-driven species selection, evidence-backed duplication analysis, and durable reporting.

**Architecture:** The project will separate a large species bank from run-specific analysis configuration. Nextflow DSL2 will orchestrate modules, while Python scripts handle stable TSV/FASTA/GFF transformations and R scripts generate publication-style figures. The first usable MVP will identify and summarize gene family members; later tasks add phylogeny, synteny, duplication retention, Ka/Ks, expression integration, and report generation.

**Tech Stack:** Nextflow DSL2, YAML, Python 3, pytest, Biopython, PyYAML, pandas, HMMER, DIAMOND/BLAST, seqkit, MAFFT or MUSCLE, IQ-TREE/FastTree, MCScanX/JCVI, KaKs_Calculator, R via `/usr/local/bin/R`, ggplot2, pheatmap, Quarto. Shared environment name: `GeneFamilyFlow`.

---

## File Structure

- Create `configs/example.config.yaml`: example run configuration, including species bank root, species include/exclude rules, gene family settings, and module toggles.
- Create `configs/species_groups.yaml`: reusable named species groups such as `brassicaceae` and `poaceae`.
- Create `schemas/config.schema.yaml`: documented config contract for validation.
- Create `workflows/main.nf`: top-level Nextflow workflow.
- Create `workflows/nextflow.config`: default Nextflow profile settings.
- Create `workflows/modules/prepare_species.nf`: discover and validate species inputs.
- Create `workflows/modules/hmmer_search.nf`: run HMMER searches per species.
- Create `workflows/modules/diamond_search.nf`: run DIAMOND/BLAST confirmation per species.
- Create `workflows/modules/domain_filter.nf`: merge HMMER and DIAMOND evidence.
- Create `workflows/modules/family_summary.nf`: emit core summary tables and FASTA outputs.
- Create `workflows/modules/alignment_phylogeny.nf`: align family proteins and infer trees.
- Create `workflows/modules/synteny_duplication.nf`: run collinearity and duplicate type classification.
- Create `workflows/modules/kaks_selection.nf`: compute Ka/Ks for duplicated gene pairs.
- Create `workflows/modules/expression_integration.nf`: integrate RNA-seq expression matrices.
- Create `bin/genefam/`: Python package for reusable helpers.
- Create `bin/genefam/discover_species.py`: scan a folder-per-species bank and produce a manifest.
- Create `bin/genefam/validate_config.py`: validate YAML configuration before workflow execution.
- Create `bin/genefam/parse_hmmer_domtbl.py`: convert HMMER domtblout files to normalized TSV.
- Create `bin/genefam/merge_identification_evidence.py`: combine HMMER and DIAMOND/BLAST candidates.
- Create `bin/genefam/extract_sequences.py`: extract selected protein/CDS sequences.
- Create `bin/genefam/gff_to_bed.py`: convert GFF3 annotations to normalized BED-like tables.
- Create `bin/genefam/summarize_family.py`: generate family member counts and evidence summaries.
- Create `bin/genefam/classify_wgd_layers.py`: infer anonymous WGD layers from Ks peaks and optionally annotate named events from config.
- Create `scripts/plot_family_counts.R`: plot per-species copy number.
- Create `scripts/plot_kaks.R`: plot Ka/Ks distributions.
- Create `scripts/plot_expression_heatmap.R`: plot expression heatmaps.
- Create `docs/reference_plotting_reuse.md`: document how to adapt plotting logic from `Reference/`.
- Create `report/template.qmd`: final report template.
- Create `tests/`: pytest tests and small fixture data.
- Create `tests/fixtures/species_bank/`: tiny fake species bank with two species.
- Modify `README.md`: describe the project, input format, and first-run command.
- Modify `HISTORY.md`: append every development session and every commit.

## Task 1: Repository Skeleton And Input Contract

**Files:**
- Create: `configs/example.config.yaml`
- Create: `configs/species_groups.yaml`
- Create: `schemas/config.schema.yaml`
- Create: `docs/input_contract.md`
- Modify: `README.md`
- Modify: `HISTORY.md`

- [ ] **Step 1: Create the example YAML configuration**

Create `configs/example.config.yaml` with this initial content:

```yaml
project:
  name: GDSL_demo
  outdir: results/GDSL_demo

runtime:
  environment: GeneFamilyFlow
  r_bin: /usr/local/bin/R

input:
  mode: auto
  root: data/species_bank
  required:
    pep: true
    gff3: true
    cds: false
    genome: false
  patterns:
    pep:
      - "*.pep.fa"
      - "*.pep.fasta"
      - "*.protein.fa"
      - "*.faa"
    cds:
      - "*.cds.fa"
      - "*.cds.fasta"
    genome:
      - "*.genome.fa"
      - "*.genome.fasta"
      - "*.fa"
      - "*.fasta"
    gff3:
      - "*.gff3"
      - "*.gff"

species:
  include:
    - Arabidopsis_thaliana
    - Brassica_rapa
  exclude: []

run:
  species_group: null

gene_family:
  name: GDSL
  hmm_profiles:
    - id: PF00657
      path: Reference/Long_Weixiong_20240323_1_GDSL/PF00657.hmm
  reference_peptides: null
  min_length: null
  max_length: null

identification:
  use_hmmer: true
  use_diamond: true
  hmm_evalue: 1.0e-10
  diamond_evalue: 1.0e-10
  final_rule: intersection

wgd_events:
  named_event_annotation: false
  event_map: null

plotting:
  reuse_reference_scripts: true
  reference_script_roots:
    - Reference/Long_Weixiong_20240323_1_GDSL/R
    - Reference/Large-Scale Plant Genomic Identification and Analysis Uncover ASMT:COMT Copy Number Variation Driving Melatonin Dosage Balance./source_code
  reuse_policy: adapt_not_modify

modules:
  identification: true
  domain_filtering: true
  family_summary: true
  phylogeny: false
  motif: false
  synteny: false
  duplication_retention: false
  kaks: false
  chromosome_location: false
  expression: false
  report: true
```

- [ ] **Step 2: Create named species groups**

Create `configs/species_groups.yaml`:

```yaml
species_groups:
  brassicaceae:
    - Arabidopsis_thaliana
    - Brassica_rapa
    - Brassica_oleracea
    - Brassica_napus
  poaceae:
    - Oryza_sativa
    - Zea_mays
    - Triticum_aestivum
    - Hordeum_vulgare
```

- [ ] **Step 3: Document the input contract**

Create `docs/input_contract.md` explaining:

```markdown
# Input Contract

GeneFam-Pipeline expects a species bank where each species has one directory.

Example:

```text
data/species_bank/
  Arabidopsis_thaliana/
    Arabidopsis_thaliana.pep.fa
    Arabidopsis_thaliana.cds.fa
    Arabidopsis_thaliana.genome.fa
    Arabidopsis_thaliana.gff3
  Brassica_rapa/
    Brassica_rapa.pep.fa
    Brassica_rapa.cds.fa
    Brassica_rapa.genome.fa
    Brassica_rapa.gff3
```

The species identifier defaults to the folder name. A run can select all species, a manual include list, or a named species group. `pep` and `gff3` are required for the MVP; `cds` is required for Ka/Ks; `genome` is required for promoter extraction and some chromosome visualizations.
```

- [ ] **Step 4: Update README**

Replace the current README with a concise project overview, expected input structure, and planned MVP command:

```markdown
# GeneFam-Pipeline

Reusable Nextflow pipeline for large-scale multi-species gene family analysis.

The first implementation target is a YAML-driven workflow that scans a large species bank, selects a run-specific subset of species, identifies gene family members with HMMER and DIAMOND, filters candidates, summarizes copy numbers, and writes a report-ready result directory.

See:
- `AGENT.md` for development rules.
- `CLAUDE.md` for Claude-specific guidance.
- `HISTORY.md` for the development diary.
- `docs/input_contract.md` for species-bank input rules.
```

- [ ] **Step 5: Update history**

Append a dated entry to `HISTORY.md` with:

```markdown
## 2026-06-23 - Add implementation plan and input contract

Context:
- Added the first implementation plan for the Nextflow gene family pipeline.

Decisions:
- Use one folder per species and YAML-based run-specific species selection.

Added:
- `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`
- `configs/example.config.yaml`
- `configs/species_groups.yaml`
- `docs/input_contract.md`

Modified:
- `README.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- Confirmed the files exist and contain no placeholder sections.

Commit:
- hash: not created in this session
- message: none
- files: planning and documentation

Next:
- Implement species discovery and configuration validation.
```

- [ ] **Step 6: Commit**

Run:

```bash
git add AGENT.md CLAUDE.md HISTORY.md README.md configs docs schemas
git commit -m "docs: add gene family pipeline development plan"
```

Expected: commit succeeds and `HISTORY.md` is amended in the same commit or immediately after with the actual commit hash.

## Task 2: Species Discovery And Config Validation

**Files:**
- Create: `bin/genefam/__init__.py`
- Create: `bin/genefam/discover_species.py`
- Create: `bin/genefam/validate_config.py`
- Create: `tests/fixtures/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.pep.fa`
- Create: `tests/fixtures/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.gff3`
- Create: `tests/fixtures/species_bank/Brassica_rapa/Brassica_rapa.pep.fa`
- Create: `tests/fixtures/species_bank/Brassica_rapa/Brassica_rapa.gff3`
- Create: `tests/test_discover_species.py`

- [ ] **Step 1: Write fixture data**

Create two tiny species folders with two short protein records and one GFF3 gene record each. Keep IDs simple and matching:

```fasta
>AT1G01010
MSSSSSSSSS
>AT1G01020
MAAAAAAA
```

```gff3
Chr1	test	gene	100	500	.	+	.	ID=AT1G01010
```

- [ ] **Step 2: Write failing tests for auto discovery**

Create `tests/test_discover_species.py`:

```python
from pathlib import Path
from bin.genefam.discover_species import discover_species


def test_discover_species_filters_include_list():
    root = Path("tests/fixtures/species_bank")
    rows = discover_species(
        root=root,
        include=["Arabidopsis_thaliana"],
        exclude=[],
        patterns={
            "pep": ["*.pep.fa"],
            "gff3": ["*.gff3"],
            "cds": ["*.cds.fa"],
            "genome": ["*.genome.fa"],
        },
        required={"pep": True, "gff3": True, "cds": False, "genome": False},
    )
    assert [row["species_id"] for row in rows] == ["Arabidopsis_thaliana"]
    assert rows[0]["pep"].endswith("Arabidopsis_thaliana.pep.fa")
    assert rows[0]["gff3"].endswith("Arabidopsis_thaliana.gff3")
```

- [ ] **Step 3: Run test and confirm failure**

Run:

```bash
python -m pytest tests/test_discover_species.py -q
```

Expected: import failure because `bin.genefam.discover_species` does not exist yet.

- [ ] **Step 4: Implement species discovery**

Create `bin/genefam/discover_species.py` with a pure Python function that scans folder names, applies include/exclude, matches file patterns, validates required files, and returns sorted dictionaries.

- [ ] **Step 5: Add CLI output**

Extend `discover_species.py` with an argparse CLI:

```bash
python bin/genefam/discover_species.py --config configs/example.config.yaml --groups configs/species_groups.yaml --out results/GDSL_demo/metadata/species_manifest.tsv
```

Expected output file columns:

```text
species_id	pep	gff3	cds	genome
```

- [ ] **Step 6: Run tests**

Run:

```bash
python -m pytest tests/test_discover_species.py -q
```

Expected: all tests pass.

- [ ] **Step 7: Update history and commit**

Append a `HISTORY.md` entry with added/modified/deleted/verification sections, then run:

```bash
git add bin tests HISTORY.md
git commit -m "feat: add species discovery"
```

## Task 3: Nextflow MVP Workflow Shell

**Files:**
- Create: `workflows/main.nf`
- Create: `workflows/nextflow.config`
- Create: `workflows/modules/prepare_species.nf`
- Modify: `README.md`
- Modify: `HISTORY.md`

- [ ] **Step 1: Create Nextflow config**

Create `workflows/nextflow.config`:

```groovy
params.config = null
params.groups = "configs/species_groups.yaml"
params.env_name = "GeneFamilyFlow"
params.r_bin = "/usr/local/bin/R"

conda {
  enabled = true
}

process {
  executor = "local"
  errorStrategy = "terminate"
  conda = params.env_name
}
```

- [ ] **Step 2: Create prepare module**

Create `workflows/modules/prepare_species.nf` with a process that calls `bin/genefam/discover_species.py` and writes `species_manifest.tsv`.

- [ ] **Step 3: Create main workflow**

Create `workflows/main.nf` that includes the prepare module and stops after emitting metadata for the first MVP checkpoint.

- [ ] **Step 4: Run local dry run**

Run:

```bash
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml
```

Expected: `results/GDSL_demo/metadata/species_manifest.tsv` exists for fixture or configured data.

- [ ] **Step 5: Update history and commit**

Append a `HISTORY.md` entry, then run:

```bash
git add workflows README.md HISTORY.md
git commit -m "feat: add Nextflow workflow shell"
```

## Task 4: HMMER And DIAMOND Identification MVP

**Files:**
- Create: `workflows/modules/hmmer_search.nf`
- Create: `workflows/modules/diamond_search.nf`
- Create: `bin/genefam/parse_hmmer_domtbl.py`
- Create: `bin/genefam/merge_identification_evidence.py`
- Create: `tests/test_parse_hmmer_domtbl.py`
- Create: `tests/test_merge_identification_evidence.py`
- Modify: `workflows/main.nf`
- Modify: `HISTORY.md`

- [ ] **Step 1: Write parser tests**

Create tests using a small HMMER domtblout fixture with one comment line and one hit line. Assert normalized columns:

```text
species_id gene_id hmm_id ali_from ali_to evalue bitscore
```

- [ ] **Step 2: Implement HMMER parser**

Implement `parse_hmmer_domtbl.py` so it ignores comment lines and writes TSV with stable column names.

- [ ] **Step 3: Write merge tests**

Create tests for `intersection`, `union`, and `hmmer_only` candidate selection using in-memory TSV fixtures.

- [ ] **Step 4: Implement evidence merge**

Implement `merge_identification_evidence.py` so each output candidate has:

```text
species_id gene_id evidence_sources hmm_evalue diamond_evalue best_reference_hit
```

- [ ] **Step 5: Add Nextflow modules**

Add one HMMER process per species/HMM and one DIAMOND process per species when `identification.use_diamond` is true.

- [ ] **Step 6: Run tests and a minimal workflow check**

Run:

```bash
python -m pytest tests/test_parse_hmmer_domtbl.py tests/test_merge_identification_evidence.py -q
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml
```

Expected: parser and merge tests pass; workflow produces raw HMMER and merged candidate TSVs when tools are available. If HMMER or DIAMOND is unavailable locally, record the missing binary in `HISTORY.md`.

- [ ] **Step 7: Update history and commit**

Run:

```bash
git add workflows bin tests HISTORY.md
git commit -m "feat: add gene family identification MVP"
```

## Task 5: Family Summary Outputs

**Files:**
- Create: `workflows/modules/family_summary.nf`
- Create: `bin/genefam/extract_sequences.py`
- Create: `bin/genefam/summarize_family.py`
- Create: `tests/test_summarize_family.py`
- Create: `tests/test_extract_sequences.py`
- Modify: `workflows/main.nf`
- Modify: `HISTORY.md`

- [ ] **Step 1: Test family count summary**

Write a test asserting that candidate rows produce:

```text
species_id member_count hmmer_count diamond_count intersection_count
```

- [ ] **Step 2: Implement summary script**

Implement `summarize_family.py` using pandas and explicit column validation.

- [ ] **Step 3: Test sequence extraction**

Write a test that extracts one FASTA sequence by ID and fails clearly when the ID is absent.

- [ ] **Step 4: Implement sequence extraction**

Implement `extract_sequences.py` using Biopython or a small FASTA iterator.

- [ ] **Step 5: Wire Nextflow summary module**

Emit:

```text
results/<run>/tables/family_members.tsv
results/<run>/tables/family_counts.tsv
results/<run>/fasta/family_members.pep.fa
```

- [ ] **Step 6: Run verification**

Run:

```bash
python -m pytest tests/test_summarize_family.py tests/test_extract_sequences.py -q
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml
```

- [ ] **Step 7: Update history and commit**

Run:

```bash
git add workflows bin tests HISTORY.md
git commit -m "feat: add family summary outputs"
```

## Task 6: Report MVP

**Files:**
- Create: `report/template.qmd`
- Create: `scripts/plot_family_counts.R`
- Create: `docs/reference_plotting_reuse.md`
- Modify: `workflows/modules/family_summary.nf`
- Modify: `README.md`
- Modify: `HISTORY.md`

- [ ] **Step 1: Inspect reference plotting scripts**

Before implementing or revising report plots, inspect relevant scripts under:

```text
Reference/Long_Weixiong_20240323_1_GDSL/R/
Reference/Large-Scale Plant Genomic Identification and Analysis Uncover ASMT:COMT Copy Number Variation Driving Melatonin Dosage Balance./source_code/
```

Use them as templates for chart types and biological interpretation, then write parameterized versions under `scripts/`.

- [ ] **Step 2: Create count plot script**

Create an R script that reads `family_counts.tsv` and writes `family_counts.pdf` and `family_counts.png`.

- [ ] **Step 3: Create report template**

Create a Quarto template with sections:

```text
Run configuration
Species included
Gene family identification strategy
Family member counts
Candidate evidence table
Limitations and disabled modules
```

- [ ] **Step 4: Wire report generation**

Add a Nextflow process that runs the plotting script and renders the Quarto template when Quarto is installed.

- [ ] **Step 5: Verification**

Run:

```bash
/usr/local/bin/R --vanilla --slave -f scripts/plot_family_counts.R --args results/GDSL_demo/tables/family_counts.tsv results/GDSL_demo/report
```

Expected: plot files are created. If R packages are missing, record exact package names in `HISTORY.md`.

- [ ] **Step 6: Update history and commit**

Run:

```bash
git add report scripts workflows README.md HISTORY.md
git commit -m "feat: add report MVP"
```

## Task 7: Duplication-Aware Evolution Module Design Checkpoint

**Files:**
- Create: `docs/duplication_retention_design.md`
- Create: `configs/wgd_events.brassicaceae.yaml`
- Create: `bin/genefam/classify_wgd_layers.py`
- Create: `tests/test_classify_wgd_layers.py`
- Modify: `HISTORY.md`

- [ ] **Step 1: Document the scientific boundary**

Create `docs/duplication_retention_design.md` explaining:

```text
Automatic:
- duplicate type classification
- Ks peak detection
- anonymous WGD layer inference

Evidence-backed annotation:
- gamma
- beta
- alpha
- theta
```

- [ ] **Step 2: Create a known-event config example**

Create `configs/wgd_events.brassicaceae.yaml`:

```yaml
wgd_events:
  - name: gamma
    scope: core_eudicots
    evidence: literature
    expected_relative_age: ancient
  - name: beta
    scope: Brassicaceae
    evidence: literature
    expected_relative_age: intermediate
  - name: alpha
    scope: Arabidopsis_Brassicaceae
    evidence: literature
    expected_relative_age: recent
  - name: theta
    scope: Brassica_specific
    evidence: literature
    expected_relative_age: lineage_specific_recent
```

- [ ] **Step 3: Test anonymous layer classification**

Write tests where Ks values cluster into two peaks and assert layers are named `WGD_layer_1` and `WGD_layer_2` by increasing median Ks.

- [ ] **Step 4: Implement layer classifier**

Implement simple deterministic binning first: accept a TSV of gene pairs and Ks values, assign configured bins, and write:

```text
gene_a gene_b ks wgd_layer event_name confidence
```

Use `event_name=unannotated` unless a known-event map is supplied.

- [ ] **Step 5: Verification and commit**

Run:

```bash
python -m pytest tests/test_classify_wgd_layers.py -q
```

Then update `HISTORY.md` and commit:

```bash
git add docs configs bin tests HISTORY.md
git commit -m "feat: add duplication retention design checkpoint"
```

## Task 8: Full Downstream Module Roadmap

**Files:**
- Create: `docs/downstream_modules.md`
- Modify: `HISTORY.md`

- [ ] **Step 1: Document phylogeny module**

Describe MAFFT/MUSCLE alignment, IQ-TREE/FastTree tree inference, and expected outputs:

```text
alignment/family_members.aln.fa
phylogeny/family_members.treefile
tables/tree_member_annotation.tsv
```

- [ ] **Step 2: Document synteny and MCScanX module**

Describe required inputs:

```text
pep
gff3 converted to MCScanX-compatible position table
family member BED
```

Describe outputs:

```text
tables/duplicate_gene_classification.tsv
tables/syntenic_gene_pairs.tsv
plots/synteny/
```

- [ ] **Step 3: Document Ka/Ks module**

Describe required CDS availability and outputs:

```text
tables/kaks_pairs.tsv
plots/kaks_distribution.pdf
```

- [ ] **Step 4: Document expression module**

Describe accepted expression matrix:

```text
gene_id sample_1 sample_2 sample_3
```

Describe outputs:

```text
tables/family_expression_matrix.tsv
plots/expression_heatmap.pdf
```

- [ ] **Step 5: Update history and commit**

Run:

```bash
git add docs HISTORY.md
git commit -m "docs: add downstream module roadmap"
```

## Self-Review

- Spec coverage: The plan covers Nextflow selection, one-folder-per-species input, YAML-driven species subsets, HMMER/DIAMOND MVP, report generation, and the duplication-aware WGD caution discussed earlier.
- Placeholder scan: No unresolved placeholder tokens are intentionally left in the plan.
- Scope check: The plan is intentionally staged. Tasks 1-6 create a working MVP. Tasks 7-8 document and start the advanced duplication-aware evolution layer.
- Risk: Local verification may be limited by missing bioinformatics binaries. When that happens, record the exact missing binary in `HISTORY.md` and keep Python unit tests passing.
