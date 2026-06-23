# HISTORY

This file is the single development diary for GeneFam-Pipeline. Every development session must append a dated entry here.

## Entry Format

```markdown
## YYYY-MM-DD HH:MM - Short task title

Context:
- User request or reason for the change.

Decisions:
- Durable design or implementation choices.

Added:
- Files or features added.

Modified:
- Files or behavior changed.

Deleted:
- Files or behavior removed.

Verification:
- Commands, checks, or review performed.

Commit:
- hash: <commit hash, or "not created in this session">
- message: <commit subject, if any>
- files: <brief changed-file summary, if any>

Next:
- Follow-up items or open questions.
```

## 2026-06-23 - Project governance and single-file development diary setup

Context:
- The user asked to add project development constraints before deeper implementation.
- Required files: `AGENT.md` and `CLAUDE.md`.
- The user clarified that development history should be recorded in one file, with dates and a clear list of what was added, modified, or deleted.

Decisions:
- Use `AGENT.md` as the project-wide instruction file for AI/development agents.
- Use `CLAUDE.md` as Claude-specific orientation while pointing back to `AGENT.md`.
- Use this root-level `HISTORY.md` as the single durable development diary.
- Record commit hash and commit message whenever a commit is created.

Added:
- `AGENT.md` with project direction, scientific cautions, repository practices, and required history updates.
- `CLAUDE.md` with Claude-specific guidance.
- `HISTORY.md` with the required single-file history format and this initial entry.

Modified:
- Updated `AGENT.md` to require history entries in `HISTORY.md`.
- Updated `CLAUDE.md` to require history entries in `HISTORY.md`.

Deleted:
- Removed `history/README.md`.
- Removed `history/2026-06-23.md`.

Verification:
- Reviewed `AGENT.md`, `CLAUDE.md`, and `HISTORY.md` after creation/update.

Commit:
- hash: not created in this session
- message: none
- files: documentation only

Next:
- Continue with the formal pipeline design document or scaffold the Nextflow MVP after user confirmation.

## 2026-06-23 - Add integrated development plan

Context:
- The user asked to integrate previous discussion into a development plan.
- The plan needed to reflect Nextflow as the workflow engine, YAML-driven species selection from a large species bank, and duplication-aware evolution analysis.

Decisions:
- Save the implementation plan under `docs/superpowers/plans/`.
- Structure development as a staged MVP first, followed by advanced downstream modules.
- Keep named WGD event annotation separate from automatic duplicate classification and anonymous WGD layer inference.

Added:
- `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`

Modified:
- `HISTORY.md`

Deleted:
- none

Verification:
- Reviewed `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`.
- Searched `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`, `HISTORY.md`, `AGENT.md`, and `CLAUDE.md` for stale dated-history rules and unresolved plan markers.
- Confirmed the relevant new files are currently untracked with `git status --short -- AGENT.md CLAUDE.md HISTORY.md docs/superpowers/plans/2026-06-23-genefam-pipeline.md`.

Commit:
- hash: not created in this session
- message: none
- files: planning documentation

Next:
- Review the plan and decide whether to begin with Task 1 repository skeleton and input contract.

## 2026-06-23 - Implement Nextflow MVP scaffold and Python helpers

Context:
- The user asked to start a long-running development pass under a concrete goal so the project would have useful developed content by morning.
- Work followed the integrated development plan and prioritized a usable MVP scaffold.

Decisions:
- Keep `Reference/` untouched and exclude it from this development checkpoint.
- Use TDD for Python behavior-bearing helpers.
- Keep genome FASTA example patterns explicit instead of broad `*.fa` patterns to avoid mistaking protein FASTA files for genome FASTA files.
- Record missing local bioinformatics binaries as environment limitations rather than blocking Python-level development.

Added:
- `.gitignore`
- `configs/example.config.yaml`
- `configs/species_groups.yaml`
- `configs/wgd_events.brassicaceae.yaml`
- `schemas/config.schema.yaml`
- `docs/input_contract.md`
- `docs/duplication_retention_design.md`
- `bin/__init__.py`
- `bin/genefam/__init__.py`
- `bin/genefam/discover_species.py`
- `bin/genefam/validate_config.py`
- `bin/genefam/parse_hmmer_domtbl.py`
- `bin/genefam/merge_identification_evidence.py`
- `bin/genefam/extract_sequences.py`
- `bin/genefam/summarize_family.py`
- `bin/genefam/classify_wgd_layers.py`
- `workflows/nextflow.config`
- `workflows/main.nf`
- `workflows/modules/prepare_species.nf`
- `workflows/modules/hmmer_search.nf`
- `workflows/modules/diamond_search.nf`
- `workflows/modules/domain_filter.nf`
- `workflows/modules/family_summary.nf`
- `scripts/plot_family_counts.R`
- `scripts/plot_kaks.R`
- `scripts/plot_expression_heatmap.R`
- `report/template.qmd`
- pytest fixtures under `tests/fixtures/species_bank/`
- pytest coverage for species discovery, config validation, HMMER parsing, evidence merging, FASTA extraction, family summary, and WGD layer classification.

Modified:
- `README.md`
- `HISTORY.md`
- `configs/example.config.yaml`
- `docs/input_contract.md`

Deleted:
- none

Verification:
- `python -m pytest tests -q` passed with 14 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/discover_species.py --config configs/example.config.yaml --groups configs/species_groups.yaml --out /tmp/genefam_species_manifest.tsv` created a 3-line manifest.
- Checked local tool availability: `nextflow`, `hmmsearch`, and `diamond` were not found in PATH.
- `Rscript` exists at `/usr/local/bin/Rscript`, but both the family-count plotting smoke test and `Rscript --version` failed to return promptly in this environment and were stopped.

Commit:
- hash: 66d4496a3f4ef1d3f2d0c3bb334404b1b8ec42f0
- message: feat: scaffold genefam pipeline mvp
- files: project scaffold, docs, Python helpers, tests, workflow modules, report scripts

Next:
- Install or expose Nextflow, HMMER, DIAMOND, and a responsive `/usr/local/bin/R` environment before full external-tool workflow verification.
- Wire parsed HMMER/DIAMOND outputs through the full Nextflow graph once Nextflow is available.

## 2026-06-23 - Standardize runtime environment names

Context:
- The user clarified that all environments should use `GeneFamilyFlow`.
- The user clarified that R-language execution should use `/usr/local/bin/R`.

Decisions:
- Add runtime configuration to `configs/example.config.yaml`.
- Configure Nextflow to use `GeneFamilyFlow` as the default conda environment name.
- Require `/usr/local/bin/R` in config validation.
- Update R script usage messages to show `/usr/local/bin/R --vanilla --slave -f ... --args ...`.

Added:
- none

Modified:
- `AGENT.md`
- `CLAUDE.md`
- `README.md`
- `HISTORY.md`
- `configs/example.config.yaml`
- `schemas/config.schema.yaml`
- `workflows/nextflow.config`
- `docs/input_contract.md`
- `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `scripts/plot_family_counts.R`
- `scripts/plot_kaks.R`
- `scripts/plot_expression_heatmap.R`

Deleted:
- none

Verification:
- `python -m pytest tests -q` passed with 15 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `rg -n "Rscript|runtime|GeneFamilyFlow|/usr/local/bin/R|conda = params.env_name" ...` confirmed the new runtime constraints are present. Remaining `Rscript` mentions are historical notes or warnings not to rely on shell-default `Rscript`.

Commit:
- hash: bcacc253ca99750e75eb10a8ff4c10aac6cc8d33
- message: docs: standardize runtime and plotting policies
- files: runtime configuration and documentation updates

Next:
- Use `GeneFamilyFlow` for all workflow process environments.
- Use `/usr/local/bin/R` for R-language execution when wiring report and plotting modules into Nextflow.

## 2026-06-23 - Allow reuse of Reference plotting scripts

Context:
- The user clarified that plotting scripts can reuse scripts under the `Reference/` directory.

Decisions:
- Treat `Reference/` plotting scripts as templates and scientific examples.
- Reuse plotting logic by adapting it into parameterized scripts under `scripts/`.
- Do not edit `Reference/` scripts or preserve their hard-coded paths in reusable pipeline code unless explicitly requested.

Added:
- `docs/reference_plotting_reuse.md`

Modified:
- `AGENT.md`
- `CLAUDE.md`
- `README.md`
- `HISTORY.md`
- `configs/example.config.yaml`
- `schemas/config.schema.yaml`
- `docs/input_contract.md`
- `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`

Deleted:
- none

Verification:
- `python -m pytest tests -q` passed with 16 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `rg -n "reuse_reference_scripts|adapt_not_modify|reference_plotting|Reference plotting|directly_modify_reference|Pending verification" ...` confirmed the reuse policy is present and the invalid policy is covered by tests.

Commit:
- hash: bcacc253ca99750e75eb10a8ff4c10aac6cc8d33
- message: docs: standardize runtime and plotting policies
- files: reference plotting reuse policy and config updates

Next:
- When improving `scripts/plot_*.R`, inspect the closest matching `Reference/` script first and port only reusable logic.

## 2026-06-23 - Add offline mock MVP runner

Context:
- The long `/goal` now targets a final reusable GeneFam-Pipeline workflow.
- The next development checkpoint needed a runnable end-to-end MVP even before local HMMER, DIAMOND, and Nextflow are installed.

Decisions:
- Add a Python mock MVP runner that uses normalized prepared HMMER and DIAMOND evidence TSV files.
- Keep the mock runner aligned with the future Nextflow output contract: `tables/`, `sequences/`, and `report/`.
- Expose the same mock runner through a Nextflow DSL2 module for later workflow verification.
- Keep generated `results/` ignored by git.

Added:
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`
- `tests/fixtures/mock_evidence/hmmer.tsv`
- `tests/fixtures/mock_evidence/diamond.tsv`
- `workflows/modules/mock_mvp.nf`
- Offline mock MVP command and output list in `README.md`.

Modified:
- `HISTORY.md`
- `configs/example.config.yaml`
- `schemas/config.schema.yaml`
- `docs/input_contract.md`
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `workflows/main.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_mock_mvp.py::test_run_mock_mvp_cli_works_when_invoked_by_script_path -q` first failed with `ModuleNotFoundError: No module named 'bin'`, confirming the direct script invocation bug.
- Added a repo-root `sys.path` guard to `bin/genefam/run_mock_mvp.py`.
- `python -m pytest tests/test_run_mock_mvp.py::test_run_mock_mvp_cli_works_when_invoked_by_script_path -q` passed.
- `python -m pytest tests/test_run_mock_mvp.py -q` passed with 2 tests.
- `python -m pytest tests -q` passed with 20 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` produced `species_manifest.tsv`, `family_candidates.tsv`, `family_counts.tsv`, `family_members.faa`, and `report/summary.md`.
- `command -v nextflow` returned no path, so the Nextflow mock module was not executed locally.

Commit:
- hash: 20ebda29293f4e4d5fe64711918f153f2d570ec8
- message: feat: add offline mock mvp runner
- files: mock MVP runner, fixtures, tests, config/docs, Nextflow mock module

Next:
- Install or expose Nextflow to verify `--mock_mvp true` through `workflows/main.nf`.
- Continue wiring real external-tool HMMER/DIAMOND outputs into the same output contract.

## 2026-06-23 - Normalize real-tool HMMER and DIAMOND outputs

Context:
- The offline MVP established the normalized evidence contract.
- The real DIAMOND module still produced raw outfmt6, and the HMMER module still produced raw domtblout, which did not match the downstream evidence merger contract.

Decisions:
- Add a DIAMOND/BLAST outfmt6 parser that keeps the best reference hit per target gene by e-value, then bitscore.
- Update the HMMER Nextflow module to parse domtblout into normalized TSV immediately after `hmmsearch`.
- Update the DIAMOND Nextflow module to parse raw outfmt6 into normalized TSV immediately after `diamond blastp`.
- Add lightweight workflow module contract tests because Nextflow is not installed locally.

Added:
- `bin/genefam/parse_diamond_outfmt6.py`
- `tests/test_parse_diamond_outfmt6.py`
- `tests/test_workflow_modules.py`

Modified:
- `HISTORY.md`
- `workflows/modules/hmmer_search.nf`
- `workflows/modules/diamond_search.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_parse_diamond_outfmt6.py -q` first failed because `bin.genefam.parse_diamond_outfmt6` did not exist.
- Implemented the parser and confirmed `python -m pytest tests/test_parse_diamond_outfmt6.py -q` passed.
- `python -m pytest tests/test_workflow_modules.py -q` first failed because HMMER and DIAMOND modules were still not invoking parser scripts.
- Updated `workflows/modules/hmmer_search.nf` and `workflows/modules/diamond_search.nf`.
- `python -m pytest tests/test_parse_diamond_outfmt6.py tests/test_workflow_modules.py -q` passed with 4 tests.
- `python -m pytest tests -q` passed with 24 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` produced the expected output index.
- `command -v nextflow` returned no path, so Nextflow module execution remains pending.

Commit:
- hash: efaa7402dbacb881a064341c5943c31d7a377d90
- message: feat: normalize search evidence outputs
- files: DIAMOND parser, parser tests, workflow module normalization

Next:
- Add domain filtering thresholds to normalized HMMER evidence.
- Continue toward combining per-species HMMER/DIAMOND outputs inside the full Nextflow graph when Nextflow becomes available.

## 2026-06-23 - Add HMMER domain filtering thresholds

Context:
- The pipeline needed a real domain filtering layer after normalized HMMER evidence parsing.
- Domain filtering should be configurable and testable without relying on external HMMER execution.

Decisions:
- Extend parsed HMMER evidence with HMM length, HMM coordinates, and domain coverage.
- Compute domain coverage as `(hmm_to - hmm_from + 1) / hmm_length`.
- Add an independent HMMER evidence filter helper using e-value, bitscore, and domain coverage thresholds.
- Add domain filtering thresholds to the example YAML and schema.
- Update the HMMER Nextflow module so raw domtblout becomes normalized raw TSV, then filtered normalized TSV.

Added:
- `bin/genefam/filter_hmmer_domains.py`
- `tests/test_filter_hmmer_domains.py`

Modified:
- `HISTORY.md`
- `bin/genefam/parse_hmmer_domtbl.py`
- `bin/genefam/validate_config.py`
- `configs/example.config.yaml`
- `schemas/config.schema.yaml`
- `docs/input_contract.md`
- `tests/test_parse_hmmer_domtbl.py`
- `tests/test_validate_config.py`
- `tests/test_workflow_modules.py`
- `workflows/nextflow.config`
- `workflows/modules/hmmer_search.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_parse_hmmer_domtbl.py tests/test_filter_hmmer_domains.py -q` first failed because `bin.genefam.filter_hmmer_domains` did not exist.
- Implemented `filter_hmmer_domains.py` and extended `parse_hmmer_domtbl.py`.
- `python -m pytest tests/test_filter_hmmer_domains.py::test_filter_domains_cli_works_when_invoked_by_script_path -q` first failed with `ModuleNotFoundError: No module named 'bin'`.
- Added a repo-root `sys.path` guard to `filter_hmmer_domains.py`.
- `python -m pytest tests/test_filter_hmmer_domains.py -q` passed.
- `python -m pytest tests/test_parse_hmmer_domtbl.py tests/test_filter_hmmer_domains.py tests/test_workflow_modules.py tests/test_validate_config.py -q` passed with 12 tests.
- `python -m pytest tests -q` passed with 27 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` produced the expected output index.
- `command -v nextflow` returned no path, so Nextflow module execution remains pending.

Commit:
- hash: 7f7ee25022f61f32cd6627c19a02c554cbd2938d
- message: feat: add hmmer domain filtering
- files: domain filter helper, parser fields, config/schema/docs, workflow module

Next:
- Start adding downstream evolutionary-analysis mock tables for duplication/WGD event evidence, so gamma/beta/alpha/theta interpretation can be represented in reports before full MCScanX/KaKs integration.

## 2026-06-23 - Add WGD event evidence table builder

Context:
- The long project goal requires gamma, beta, alpha, theta, and other WGD event names to be represented as evidence-backed interpretations, not automatic labels.
- The existing WGD helper classified pairs into anonymous WGD layers but did not produce a layer-level evidence table.

Decisions:
- Add a `build_wgd_event_evidence.py` helper that summarizes classified duplicated pairs by WGD layer.
- Keep unnamed layers neutral with `interpretation_status: inferred_layer_only`.
- Only attach event metadata when a configured named event is present and found in an event configuration file.
- Document the observed/inferred/interpreted evidence split in a dedicated WGD evidence document.

Added:
- `bin/genefam/build_wgd_event_evidence.py`
- `tests/test_build_wgd_event_evidence.py`
- `docs/wgd_event_evidence.md`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/duplication_retention_design.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_event_evidence.py -q` first failed because `bin.genefam.build_wgd_event_evidence` did not exist.
- Implemented `build_wgd_event_evidence.py`.
- `python -m pytest tests/test_build_wgd_event_evidence.py -q` passed with 3 tests.
- `python -m pytest tests -q` passed with 30 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a WGD command-line smoke test with three duplicated pairs, `classify_wgd_layers.py`, and `build_wgd_event_evidence.py`; the output mapped `WGD_layer_1=alpha`, `WGD_layer_2=beta`, and `WGD_layer_3=gamma` using `configs/wgd_events.brassicaceae.yaml`.

Commit:
- hash: 6041cf5c79a6389e18878ed1e0930a4502ddf6f9
- message: feat: add wgd event evidence builder
- files: WGD evidence builder, tests, docs

Next:
- Add duplicate type and retention enrichment helpers so WGD retained family members can be summarized before full MCScanX integration.

## 2026-06-23 - Add duplicate-type retention enrichment helper

Context:
- The pipeline needs an entry point for the preferential retention analysis described in the reference papers.
- Full MCScanX integration is still pending, but duplicate-type enrichment can be implemented against prepared classification tables.

Decisions:
- Use a standard-library hypergeometric right-tail calculation to avoid adding scipy as a hard dependency.
- Compare target family duplicate type counts against whole-genome background duplicate type counts.
- Report fold enrichment and p-value per duplicate type.

Added:
- `bin/genefam/retention_enrichment.py`
- `tests/test_retention_enrichment.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/duplication_retention_design.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_retention_enrichment.py -q` first failed because `bin.genefam.retention_enrichment` did not exist.
- Implemented `retention_enrichment.py`.
- `python -m pytest tests/test_retention_enrichment.py -q` passed.
- `python -m pytest tests -q` passed with 31 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test with family/background duplicate type TSV files; `retention_enrichment.py` produced fold enrichment and p-value columns.

Commit:
- hash: 288474dc1a10e48678e3deec3208e1e16ba3ffc4
- message: feat: add retention enrichment helper
- files: retention enrichment helper, tests, docs

Next:
- Add chromosome location extraction from GFF3 so family members can be plotted on chromosomes.

## 2026-06-23 - Add chromosome location extraction helper

Context:
- The workflow needs a chromosome localization table before R plotting can place family members on chromosomes.

Decisions:
- Extract coordinates from GFF3 `gene` features.
- Resolve gene IDs from `ID`, `gene_id`, or `Name` attributes.
- Keep output as a simple report-ready TSV with species, gene, sequence ID, start, end, and strand.

Added:
- `bin/genefam/extract_chromosome_locations.py`
- `tests/test_extract_chromosome_locations.py`

Modified:
- `HISTORY.md`
- `docs/input_contract.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_extract_chromosome_locations.py -q` first failed because `bin.genefam.extract_chromosome_locations` did not exist.
- Implemented `extract_chromosome_locations.py`.
- `python -m pytest tests/test_extract_chromosome_locations.py -q` passed.
- `python -m pytest tests -q` passed with 33 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test against the Arabidopsis fixture GFF3 and extracted `AT1G01010` at `Chr1:100-500`.

Commit:
- hash: not created in this session
- message: feat: add chromosome location extraction
- files: chromosome location helper, tests, input contract docs

Next:
- Add expression matrix integration helper so RNA-seq expression tables can be subset to family members.
