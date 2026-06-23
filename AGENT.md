# AGENT.md

This repository is building a reusable Nextflow-based pipeline for large-scale gene family analysis across many plant species.

## Project Direction

- Main workflow engine: Nextflow DSL2.
- Configuration style: YAML-driven parameters plus optional species manifests.
- Runtime target: local workstation first, then HPC/server execution with Docker and Apptainer/Singularity support.
- Default input model: one folder per species under a large species bank.
- Core scientific scope:
  - genome-wide gene family identification with HMMER and BLAST/DIAMOND
  - domain filtering and member validation
  - multi-species comparison
  - alignment and phylogeny
  - motif and gene structure analysis
  - chromosome localization
  - synteny and collinearity
  - duplication classification and retention enrichment
  - Ka/Ks and selection pressure analysis
  - RNA-seq expression integration
  - report generation

## Design Principles

- Keep the species bank separate from the run-specific species selection.
- Support two input modes:
  - auto mode: discover species from folders.
  - manifest mode: read an explicit species table for irregular datasets.
- Treat WGD event names such as gamma, beta, alpha, and theta as evidence-backed annotations, not blind automatic labels.
- Always distinguish:
  - automatic duplicate type classification: singleton, dispersed, proximal, tandem, WGD/segmental.
  - inferred WGD layers from Ks peaks.
  - named historical events supplied by a known event map or literature-backed configuration.
- Prefer reproducible intermediate TSV files over opaque one-off plotting scripts.
- Make every module runnable and testable with a small example dataset.
- Do not hard-code species-specific ID cleaning rules in workflow logic. Put them in configuration or small documented helper scripts.

## Repository Practices

- Before changing code or docs, inspect the current repository state and relevant files.
- Use small, focused commits when the user asks for commits.
- Do not remove or rewrite reference data unless the user explicitly asks.
- Keep generated heavy outputs out of source control unless they are deliberate examples.
- Put durable design decisions and development notes in `HISTORY.md`.

## Required History Updates

Every development session must update the single project history file before the work is considered complete:

```text
HISTORY.md
```

Each entry should include:

- date and local time if available
- short task title
- context or user request
- decisions made
- files added
- files modified
- files deleted
- verification performed
- next steps or open questions

If a git commit is created, the commit information must also be recorded in `HISTORY.md`:

```text
Commit:
- hash: <commit hash>
- message: <commit subject>
- files: <brief changed-file summary>
```

If no commit is created, explicitly write:

```text
Commit: not created in this session
```

## Current Baseline Decisions

- Use Nextflow instead of Snakemake for the main workflow.
- Use YAML to choose the species subset from a large species bank.
- Support `include`, `exclude`, and named species groups in configuration.
- Add a duplication-aware evolution module as a first-class project feature.
- Start with a practical MVP before implementing every publication-style downstream analysis.
