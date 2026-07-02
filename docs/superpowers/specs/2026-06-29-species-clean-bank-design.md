# Species Clean Bank Design

## Scope

This design defines `01_preprocess` as an independently runnable module for building a reusable species clean bank. The module serves both the full GeneFam-Pipeline workflow and standalone preprocessing for large species collections.

The target use case is a raw species bank containing hundreds to thousands of species. Each species should be cleaned once, audited, and then reused by later gene-family analyses through species selection.

## Goals

- Preserve raw input files separately from cleaned files.
- Produce gene-level protein and CDS FASTA files with one representative transcript per gene.
- Keep genome and GFF3 files available inside the clean bank.
- Produce audit tables that explain every ID cleaning and representative-transcript decision.
- Produce global manifests and QC summaries so future analyses can select arbitrary species combinations from the clean bank.
- Make `01_preprocess` runnable as a standalone module and as the first step of the full workflow.

## Directory Layout

The raw data remain under `data/species_bank/` and are not modified.

The clean bank is written to `data/species_clean_bank/`:

```text
data/species_clean_bank/
  Arabidopsis_thaliana/
    raw/
      Arabidopsis_thaliana.pep.fa
      Arabidopsis_thaliana.cds.fa
      Arabidopsis_thaliana.genome.fa
      Arabidopsis_thaliana.gff3

    clean/
      Arabidopsis_thaliana.protein.clean.fa
      Arabidopsis_thaliana.cds.clean.fa
      Arabidopsis_thaliana.genome.fa
      Arabidopsis_thaliana.gff3

    audit/
      Arabidopsis_thaliana.gene_id_map.tsv
      Arabidopsis_thaliana.representative_transcripts.tsv
      Arabidopsis_thaliana.preprocess_qc.tsv
      Arabidopsis_thaliana.preprocess_warnings.tsv
```

Global clean-bank outputs:

```text
data/species_clean_bank_manifest.tsv
data/species_clean_bank_qc.tsv
data/species_clean_bank_failed.tsv
data/species_clean_bank_summary.md
```

## Per-Species File Rules

`raw/` contains exact copies of the original peptide, CDS, genome, and GFF3 files. These files are never edited.

`clean/` contains files used by downstream analysis:

- `<species>.protein.clean.fa`: protein FASTA with cleaned gene IDs, one longest-protein representative per gene, and terminal `*` removed.
- `<species>.cds.clean.fa`: CDS FASTA with the same gene IDs and same representative genes as `protein.clean.fa`.
- `<species>.genome.fa`: copied original genome FASTA for promoter and chromosome-level modules.
- `<species>.gff3`: copied original GFF3 for coordinate-based modules.

Future work may add `<species>.gff3.clean.gff3`, but this design does not require standardized GFF3 rewriting yet.

## ID Mapping Rules

The module should resolve protein and CDS records to gene IDs using this priority order:

1. FASTA header attributes such as `locus`, `gene`, `gene_id`, `transcript`, and `polypeptide`.
2. GFF3 transcript-to-gene mapping using transcript feature aliases from `ID`, `Name`, `Alias`, `transcript_id`, `protein_id`, and related attributes.
3. Per-species GFF3-aware ID-rule inference. The module samples peptide headers, tries transcript/product aliases such as `.P01` to `.T01`, and checks whether they match real GFF3 transcript IDs.
4. Common transcript suffix inference, including `.1`, `.01`, `.t1`, `.T01`, `.P01`, `-RA`, `_T001`, `.p1`, `.cds1`, and related variants.
5. Self ID fallback only when no safer mapping exists.

When GFF3 mapping succeeds, the selected output FASTA ID must preserve the GFF3 gene ID exactly. Suffix stripping is only a fallback behavior for records that cannot be mapped to GFF3. The selected transcript ID remains traceable in the audit tables.

## Representative Transcript Rule

For every gene, select the representative transcript by longest protein length.

Tie-breaking should be deterministic:

1. Longer protein length wins.
2. Lexicographically smaller cleaned transcript ID wins.

The rule must be recorded as `longest_pep` in the representative transcript table.

## Audit Tables

Each species should write:

- `gene_id_map.tsv`: raw transcript ID, cleaned transcript ID, gene ID, mapping source, and useful aliases.
- `id_resolution_rules.tsv`: per-species GFF3 matching rate, whether GFF3 gene IDs were preserved, and suffix-like diagnostics for unmapped/fallback troubleshooting.
- `representative_transcripts.tsv`: gene ID, selected transcript ID, protein length, CDS length, and rule.
- `preprocess_qc.tsv`: raw counts, clean counts, mapping rates, CDS match rate, terminal stop removals, warning counts, and status.
- `preprocess_warnings.tsv`: row-level warnings for missing CDS, ambiguous IDs, duplicate outputs, or low-confidence fallback.

Global tables aggregate all species:

- `species_clean_bank_manifest.tsv`: selected species and paths to clean protein, clean CDS, genome, GFF3, audit files, and status.
- `species_clean_bank_qc.tsv`: one QC row per species.
- `species_clean_bank_failed.tsv`: failed species and reasons.
- `species_clean_bank_summary.md`: human-readable summary of pass/warning/fail counts and common issues.

## Status Policy

Per-species status values:

- `pass`: clean protein and CDS are one-to-one, no serious warnings.
- `warning`: outputs are usable but contain non-fatal issues, such as fallback-heavy mapping.
- `failed`: required files are missing or clean protein/CDS cannot be made consistently.
- `missing_cds`: protein cleaning succeeded but CDS is unavailable when CDS is required.
- `low_cds_match_rate`: CDS matching is below configured threshold.
- `low_gff3_mapping_rate`: too many records required suffix/self fallback.

The module should continue processing other species when one species fails.

## Standalone Usage

The standalone command should look like:

```bash
python bin/genefam/build_species_clean_bank.py \
  --raw-root data/species_bank \
  --out-root data/species_clean_bank \
  --manifest data/species_clean_bank_manifest.tsv \
  --qc data/species_clean_bank_qc.tsv \
  --failed data/species_clean_bank_failed.tsv \
  --summary data/species_clean_bank_summary.md
```

The command should support species include/exclude lists and should be able to process only selected species for incremental updates.

## Workflow Integration

`01_preprocess` should be runnable as:

- a standalone Python module;
- a standalone Nextflow module;
- the first stage of the full GeneFam-Pipeline workflow.

Later analysis should be able to start from the clean bank:

```yaml
input:
  mode: clean_bank
  root: data/species_clean_bank
  manifest: data/species_clean_bank_manifest.tsv
```

Species subsets should be selected by YAML:

```yaml
species:
  include:
    - Arabidopsis_thaliana
    - Brassica_rapa
```

## Initial Validation Target

The first validation set is the current three-species raw bank:

- `Arabidopsis_thaliana`
- `Brassica_rapa`
- `Capsella_rubella`

Acceptance criteria for this set:

- clean protein and CDS counts match per species;
- no protein header contains `|`;
- no clean protein sequence ends with `*`;
- representative transcript tables exist;
- QC tables report mapping source counts and match rates;
- clean-bank manifest points to clean files under `data/species_clean_bank/`;
- raw files are preserved under each species `raw/` directory.
