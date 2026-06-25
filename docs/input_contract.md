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

The species identifier defaults to the folder name.

## Required Files

For the MVP, each selected species needs:

- protein FASTA (`pep`)
- genome annotation (`gff3`)

Later modules add more requirements:

- CDS FASTA (`cds`) for Ka/Ks.
- genome FASTA (`genome`) for promoter extraction and chromosome visualizations.

## Module Dependency Validation

`bin/genefam/validate_config.py` checks module dependencies before a run starts:

- `modules.identification: true` requires `input.required.pep: true`.
- `modules.domain_filtering: true` requires `input.required.pep: true`.
- `modules.phylogeny: true` requires `input.required.pep: true`.
- `modules.motif: true` requires `input.required.pep: true`.
- `modules.synteny: true` requires both `input.required.pep: true` and `input.required.gff3: true`.
- `modules.kaks: true` requires `input.required.cds: true`.
- `modules.chromosome_location: true` requires `input.required.gff3: true`.
- `modules.expression: true` requires `expression.matrix`.
- `modules.phylogeny: true` requires `modules.family_summary: true`.
- `modules.motif: true` requires `modules.family_summary: true`.
- `modules.duplication_retention: true` requires both `modules.synteny: true` and `modules.kaks: true`.

Use `python bin/genefam/validate_config.py <config.yaml> --check-paths` before a real run to require configured runtime inputs to exist. This strict mode checks `input.root` or `input.manifest`, enabled HMMER profiles, DIAMOND reference peptides, and `expression.matrix` when present. The Nextflow entrypoint runs the same strict preflight through `workflows/modules/config_validation.nf` before species discovery or identification starts.

## Species Selection

The species bank can contain many species. Each run chooses a subset with YAML:

```yaml
species:
  include:
    - Arabidopsis_thaliana
    - Brassica_rapa
  exclude: []
```

Named groups can be selected through `run.species_group` when present in `configs/species_groups.yaml`.

## Input Modes

`input.mode: auto` scans a folder-per-species bank and requires `input.root`.

`input.mode: manifest` reads a prebuilt tab-separated manifest and requires `input.manifest`. The manifest must contain:

```text
species_id
pep
gff3
cds
genome
```

Manifest mode still applies `species.include`, `species.exclude`, and `run.species_group`, so a large manifest can be reused while selecting a smaller target species set in YAML.

## Runtime

The default shared environment is `GeneFamilyFlow`. R-language steps should use `/usr/local/bin/R`.

## Reference Plot Templates

Plotting scripts under `Reference/` can be reused as templates for pipeline plots. The reusable implementation should live under `scripts/`, accept explicit input/output arguments, and avoid hard-coded reference-project paths.

## Mock Evidence

For offline development, `dev.mock_external_tools: true` can point to a directory containing:

- `hmmer.tsv`
- `diamond.tsv`

These files use the same normalized columns as the parser and evidence merger. The fixture directory `tests/fixtures/mock_evidence/` demonstrates the required format.

When `dev.mock_external_tools: false`, identification inputs must come from project data rather than `tests/fixtures/`. Use paths such as `data/hmm_profiles/PF00657.hmm` for `gene_family.hmm_profiles` and `data/reference/GDSL_reference.pep.fa` for `gene_family.reference_peptides`, then replace those paths with curated profiles and reference sequences for the target gene family.

## Identification Tool Flags

The standard identification branch can enable or disable external search input generation through:

- `identification.use_hmmer`
- `identification.use_diamond`

Both default to enabled when omitted. When `modules.identification: true`, at least one of these flags must remain enabled so the branch has evidence to merge. Disabled tools still produce a header-only planning table, which keeps downstream file contracts stable while making the skipped evidence source explicit.

## Domain Filtering

HMMER evidence can be filtered by:

- `domain_filtering.hmmer_max_evalue`
- `domain_filtering.hmmer_min_bitscore`
- `domain_filtering.hmmer_min_domain_coverage`

Domain coverage is calculated from HMM coordinates as `(hmm_to - hmm_from + 1) / hmm_length`.

## Chromosome Locations

`bin/genefam/extract_chromosome_locations.py` extracts family member coordinates from GFF3 `gene` features. It reads gene IDs from `ID`, `gene_id`, or `Name` attributes and writes:

```text
species_id
gene_id
seqid
start
end
strand
```

## Expression Matrix

`bin/genefam/subset_expression_matrix.py` expects a tab-separated expression matrix where the first column is `gene_id` and all remaining columns are sample names:

```text
gene_id cold_0h cold_3h cold_24h
AT1G01010 1.0 3.0 2.5
```

It subsets the matrix to family member IDs before heatmap plotting.

## Motif Summary

`bin/genefam/parse_meme_motifs.py` parses MEME text output into:

```text
family_name
motif_id
motif_name
width
sites
evalue
```

This table is intended for motif architecture plotting and report integration.

## Syntenic Pairs

`bin/genefam/parse_mcscanx_collinearity.py` parses MCScanX `.collinearity` output into:

```text
block_id
block_score
block_evalue
block_pair_count
gene_a
gene_b
pair_evalue
```

This table is the first bridge from MCScanX output into duplicate type, Ks, and WGD-layer analyses.

## Duplicate Classification

`bin/genefam/normalize_duplicate_types.py` normalizes prepared duplicate type tables into:

```text
gene_id
duplicate_type
raw_duplicate_type
```

Accepted canonical `duplicate_type` values:

- `WGD/segmental`
- `tandem`
- `proximal`
- `dispersed`
- `singleton`

These normalized tables can be used directly by `bin/genefam/retention_enrichment.py`.

## Family Duplicate Classification

`bin/genefam/join_family_duplicates.py` joins identified family members with normalized duplicate type classifications. It reads:

- family member table with `species_id` and `gene_id`
- normalized duplicate type table with `gene_id`, `duplicate_type`, and `raw_duplicate_type`

It writes:

```text
species_id
gene_id
duplicate_type
raw_duplicate_type
```

This family-specific table is the direct input for `bin/genefam/retention_enrichment.py`, while the full normalized duplicate table is used as the background.

## Family WGD Event Membership

`bin/genefam/annotate_family_wgd_events.py` joins family duplicate classifications with classified Ks/WGD pairs. It reads:

- family duplicate classification table from `bin/genefam/join_family_duplicates.py`
- WGD-classified pair table from `bin/genefam/classify_wgd_layers.py`

It writes one row per family gene and supporting duplicated pair:

```text
species_id
gene_id
duplicate_type
wgd_layer
event_name
partner_gene
ks
confidence
```

`event_name` remains `unannotated` until the user configures named events such as `gamma`, `beta`, `alpha`, or `theta`. This keeps the workflow honest: Ks and synteny define anonymous WGD layers first, and YAML/literature metadata maps those layers to biological event names later.

## Family Event Retention Summary

`bin/genefam/summarize_family_event_retention.py` summarizes the family WGD event membership table into report-ready counts:

```text
wgd_layer
event_name
duplicate_type
family_gene_count
pair_evidence_count
gene_ids
```

`family_gene_count` counts unique family genes per `wgd_layer` / `event_name` / `duplicate_type`, while `pair_evidence_count` counts all supporting duplicated-pair rows. This table is intended for gamma/beta/alpha/theta retention summaries and should be interpreted alongside the layer-level `wgd_event_evidence` table.

## Ka/Ks Pairs

`bin/genefam/prepare_kaks_pairs.py` prepares pairwise CDS FASTA files from syntenic pairs and CDS FASTA inputs. It writes a manifest with:

```text
gene_a
gene_b
pair_fasta
expected_kaks
```

`bin/genefam/parse_kaks_results.py` parses KaKs_Calculator-style output into:

```text
gene_a
gene_b
ka
ks
ka_ks
p_value
selection_category
```

Selection category is derived from `Ka/Ks`:

- `< 1`: `purifying`
- `= 1`: `neutral`
- `> 1`: `positive`

## Discovery Rules

- Folder name is the default species ID.
- File matching uses the pattern lists in `configs/example.config.yaml`.
- If multiple files match the same file type, the pipeline fails and asks for a manifest.
- Broad genome patterns such as `*.fa` are intentionally avoided in the example config because they can accidentally match protein FASTA files.
- Use `input.mode: manifest` when genome or annotation files have ambiguous names, or when a curated species manifest should be reused across runs.
- Reference data under `Reference/` is not modified by the pipeline.
