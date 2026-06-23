# CLAUDE.md

This file gives Claude-specific orientation for working in this repository.

## What This Project Is

GeneFam-Pipeline is intended to become a reusable, Nextflow-based workflow for large-scale gene family analysis. It should support many species stored in a shared species bank, while each run selects only the species requested in YAML.

The workflow should eventually cover identification, filtering, phylogeny, motif analysis, synteny, duplication classification, WGD retention analysis, Ka/Ks, expression integration, and report generation.

Runtime convention:

- Use the shared environment name `GeneFamilyFlow`.
- Use `/usr/local/bin/R` for R language execution.
- Do not assume the shell-default `R` or `Rscript` is the intended runtime.

## How To Work Here

- Read `AGENT.md` first for project-wide rules.
- Check the current repository structure before proposing or editing.
- Keep changes narrow and directly connected to the user's request.
- Preserve the `Reference/` directory as source material unless the user explicitly asks to reorganize it.
- Reuse plotting ideas and logic from `Reference/` scripts when building report plots, but convert them into parameterized project scripts.
- Do not edit `Reference/` scripts unless explicitly requested.
- Prefer clear Markdown design notes and small scripts over large undocumented notebooks.
- When adding workflow logic, prefer Nextflow DSL2 modules and stable TSV/FASTA/GFF interfaces between steps.
- When adding R-driven workflow logic, call the configured R binary, defaulting to `/usr/local/bin/R`.

## Scientific Cautions

- Do not present gamma, beta, alpha, or theta WGD event names as automatically detected facts unless an event map or literature-backed configuration is provided.
- It is acceptable to infer anonymous WGD layers from Ks peaks and syntenic blocks, but named event annotation needs evidence.
- Keep gene duplication type classification separate from historical WGD event naming.
- Record assumptions about species naming, gene ID cleaning, and file pattern matching.

## Required Development Diary

Every Claude development session must update the single project history file:

Use:

```text
HISTORY.md
```

Record:

- date and local time if available
- what was requested
- what was changed
- what was added
- what was deleted
- important decisions
- tests or checks run
- files touched
- commit hash and commit message if a commit was created

If no commit was created, state that directly.

This project uses `HISTORY.md` as the user's development diary, so do not skip it for "small" changes.
