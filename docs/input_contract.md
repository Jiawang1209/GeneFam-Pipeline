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

## Discovery Rules

- Folder name is the default species ID.
- File matching uses the pattern lists in `configs/example.config.yaml`.
- If multiple files match the same file type, the pipeline fails and asks for a manifest.
- Broad genome patterns such as `*.fa` are intentionally avoided in the example config because they can accidentally match protein FASTA files.
- Use manifest mode when genome files have ambiguous names.
- Reference data under `Reference/` is not modified by the pipeline.
