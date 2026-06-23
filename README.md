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
- Evidence-backed WGD event interpretation for gamma, beta, alpha, theta, and other configured events.
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
- `docs/wgd_event_evidence.md`: WGD layer and named-event evidence contract.
- `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`: implementation plan.

## Runtime Convention

- Shared environment name: `GeneFamilyFlow`
- R binary: `/usr/local/bin/R`

Nextflow defaults are recorded in `workflows/nextflow.config`. R scripts should be executed through `/usr/local/bin/R` rather than relying on the shell-default `R` or `Rscript`.

## Reference Plotting Scripts

The `Reference/` directory contains paper-derived plotting scripts and result examples. New reusable plots should inspect these scripts first, reuse their scientific plotting logic where appropriate, and then implement parameterized versions under `scripts/`.

Reference files are source material: do not edit them unless explicitly requested.

## MVP Command

The first runnable checkpoint generates a species manifest:

```bash
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml
```

The offline mock MVP runs without HMMER, DIAMOND, or Nextflow:

```bash
python bin/genefam/run_mock_mvp.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/mock_mvp
```

It writes:

- `results/mock_mvp/tables/species_manifest.tsv`
- `results/mock_mvp/tables/family_candidates.tsv`
- `results/mock_mvp/tables/family_counts.tsv`
- `results/mock_mvp/sequences/family_members.faa`
- `results/mock_mvp/report/summary.md`

When Nextflow is available, the same mock runner is exposed through:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --mock_mvp true \
  --mock_evidence_dir tests/fixtures/mock_evidence \
  --outdir results/mock_mvp
```

## Current Status

- Project governance files are in place.
- YAML config and schema draft are in place.
- Species discovery helper is implemented and tested.
- Offline mock MVP runner is implemented and tested.
- Full external-tool workflow wiring is still under development.
