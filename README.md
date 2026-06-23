# GeneFam-Pipeline

Reusable Nextflow pipeline for large-scale multi-species gene family analysis.

The first implementation target is a YAML-driven workflow that scans a large species bank, selects a run-specific subset of species, identifies gene family members with HMMER and DIAMOND/BLAST, filters candidates, summarizes copy numbers, and writes report-ready tables and FASTA files.

## Planned Scope

- Genome-wide family identification with HMMER and DIAMOND/BLAST.
- Domain filtering and candidate evidence merging.
- Multi-species family member summaries.
- Alignment and phylogeny.
- Motif and gene structure analysis.
- Chromosome localization.
- Synteny, duplication classification, WGD-layer inference, and retention enrichment.
- Ka/Ks and selection-pressure analysis.
- RNA-seq expression integration.
- Reproducible reports.

## Input Model

The default input is a species bank with one folder per species:

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

The species ID defaults to the folder name. A run can analyze all species, a manual include list, or a named species group.

## Project Files

- `AGENT.md`: project-wide development rules.
- `CLAUDE.md`: Claude-specific guidance.
- `HISTORY.md`: single-file development diary.
- `configs/example.config.yaml`: example analysis configuration.
- `docs/input_contract.md`: input format contract.
- `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`: implementation plan.

## MVP Command

The first runnable checkpoint generates a species manifest:

```bash
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml
```
