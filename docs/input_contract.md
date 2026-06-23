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

## Runtime

The default shared environment is `GeneFamilyFlow`. R-language steps should use `/usr/local/bin/R`.

## Reference Plot Templates

Plotting scripts under `Reference/` can be reused as templates for pipeline plots. The reusable implementation should live under `scripts/`, accept explicit input/output arguments, and avoid hard-coded reference-project paths.

## Mock Evidence

For offline development, `dev.mock_external_tools: true` can point to a directory containing:

- `hmmer.tsv`
- `diamond.tsv`

These files use the same normalized columns as the parser and evidence merger. The fixture directory `tests/fixtures/mock_evidence/` demonstrates the required format.

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
- Use manifest mode when genome files have ambiguous names.
- Reference data under `Reference/` is not modified by the pipeline.
