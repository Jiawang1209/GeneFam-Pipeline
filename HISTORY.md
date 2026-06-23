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
- hash: 8398e8121be22b3c5168ee8b91f507b60ae7aa91
- message: feat: add chromosome location extraction
- files: chromosome location helper, tests, input contract docs

Next:
- Add expression matrix integration helper so RNA-seq expression tables can be subset to family members.

## 2026-06-23 - Add expression matrix subsetting helper

Context:
- The workflow needs an RNA-seq expression integration entry point before heatmap plotting.

Decisions:
- Use a simple TSV contract where the first column is `gene_id` and all remaining columns are sample names.
- Fail fast if requested family member IDs are missing from the expression matrix.
- Preserve expression matrix row order from the input file.

Added:
- `bin/genefam/subset_expression_matrix.py`
- `tests/test_subset_expression_matrix.py`

Modified:
- `HISTORY.md`
- `docs/input_contract.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_subset_expression_matrix.py -q` first failed because `bin.genefam.subset_expression_matrix` did not exist.
- Implemented `subset_expression_matrix.py`.
- `python -m pytest tests/test_subset_expression_matrix.py -q` passed.
- `python -m pytest tests -q` passed with 35 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test that subset a two-gene expression matrix to `AT1G01010`.

Commit:
- hash: 4da397cfd72a2f364d9753290ea0c24dce95cc1a
- message: feat: add expression matrix subsetting
- files: expression subset helper, tests, input contract docs

Next:
- Add report input aggregation so the mock MVP can include available downstream tables in a single report index.

## 2026-06-24 - Add report index aggregation for mock MVP

Context:
- The mock MVP generated multiple report-ready files, but report templates needed a single stable index listing available and unavailable outputs.
- `HISTORY.md` also needed the actual commit hash for the previous expression matrix subsetting checkpoint.

Decisions:
- Add `report/report_index.tsv` to the mock MVP output contract.
- Use `available` and `not_available` statuses so downstream reports can show disabled or pending modules explicitly.
- Include placeholders for downstream outputs such as chromosome locations, WGD layers, WGD event evidence, retention enrichment, and expression matrix.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_mock_mvp.py`
- `report/template.qmd`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_mock_mvp.py -q` first failed because `report_index` was missing from `run_mock_mvp` outputs and no `report/report_index.tsv` file was written.
- Implemented report index writing in `bin/genefam/run_mock_mvp.py`.
- `python -m pytest tests/test_run_mock_mvp.py -q` passed.
- `python -m pytest tests -q` passed with 35 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` produced `report/report_index.tsv` with available core outputs and not-available downstream placeholders.
- `command -v nextflow` returned no path, so Nextflow mock execution remains pending.

Commit:
- hash: 1a943c8e43cae544b346a12f6f4684b2da5f6c70
- message: feat: add report index aggregation
- files: mock report index, tests, README, report template, history

Next:
- Add lightweight report rendering from `report_index.tsv` into `summary.md` sections for available and unavailable modules.

## 2026-06-24 - Render available and pending outputs in mock summary

Context:
- `report_index.tsv` existed, but `summary.md` did not yet surface the available and pending output status for users.

Decisions:
- Generate `summary.md` from the same report index rows used to write `report/report_index.tsv`.
- Mark planned outputs that are written during the same mock run, such as `summary_report` and `report_index`, as available.
- Keep downstream modules explicit as pending until their tables are produced.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_mock_mvp.py::test_run_mock_mvp_writes_core_outputs -q` first failed because `summary.md` did not include `Available Outputs` or `Pending Outputs`.
- Implemented summary rendering from report index rows.
- A second test run exposed that `summary_report` was marked `not_available` because it had not been written at index-build time.
- Updated report index generation so `summary_report` and `report_index` are marked available for the current planned run.
- `python -m pytest tests/test_run_mock_mvp.py -q` passed.
- `python -m pytest tests -q` passed with 35 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` produced a `summary.md` with correct available and pending output sections.

Commit:
- hash: 2706669308e28e5e620b0e2d7fd8aaf2131b2264
- message: feat: render report output status
- files: mock summary rendering, tests, history

Next:
- Add alignment preparation outputs so family FASTA can feed MAFFT/MUSCLE and phylogeny modules.

## 2026-06-24 - Add alignment input manifest

Context:
- The workflow needs a stable bridge from identified family protein FASTA to later MAFFT/MUSCLE and phylogeny modules.

Decisions:
- Add an alignment input manifest instead of invoking MAFFT immediately, because external tool availability is still not guaranteed locally.
- Require at least two family member sequences before creating an alignment manifest.
- Add the alignment manifest to the mock MVP and report index so downstream availability is visible.

Added:
- `bin/genefam/prepare_alignment_inputs.py`
- `tests/test_prepare_alignment_inputs.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_prepare_alignment_inputs.py -q` first failed because `bin.genefam.prepare_alignment_inputs` did not exist.
- Implemented `prepare_alignment_inputs.py`.
- `python -m pytest tests/test_prepare_alignment_inputs.py -q` passed.
- `python -m pytest tests/test_run_mock_mvp.py::test_run_mock_mvp_writes_core_outputs -q` then failed because `alignment_manifest` was not yet produced by the mock MVP.
- Added `alignment_manifest.tsv` generation to `bin/genefam/run_mock_mvp.py`.
- `python -m pytest tests/test_run_mock_mvp.py tests/test_prepare_alignment_inputs.py -q` passed.
- `python -m pytest tests -q` passed with 37 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` produced `tables/alignment_manifest.tsv` and marked it available in `report/report_index.tsv`.
- `command -v nextflow` returned no path, so Nextflow execution remains pending.

Commit:
- hash: c5ad5a01544241dfdd5074735a54f7d36a0ebdb4
- message: feat: add alignment input manifest
- files: alignment manifest helper, mock MVP integration, tests, docs, history

Next:
- Add tree/phylogeny manifest preparation so alignments can feed IQ-TREE/FastTree when external tools are available.

## 2026-06-24 - Add phylogeny input manifest

Context:
- The workflow needs a stable bridge from alignment outputs to IQ-TREE or FastTree execution.

Decisions:
- Add a phylogeny manifest helper that prefers trimmed alignments and falls back to raw alignments.
- Keep tree-building itself as an external-tool module to be wired later.
- Add the phylogeny manifest to the mock MVP and report index so the downstream contract is visible now.

Added:
- `bin/genefam/prepare_phylogeny_inputs.py`
- `tests/test_prepare_phylogeny_inputs.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_prepare_phylogeny_inputs.py -q` first failed because `bin.genefam.prepare_phylogeny_inputs` did not exist.
- Implemented `prepare_phylogeny_inputs.py`.
- `python -m pytest tests/test_prepare_phylogeny_inputs.py -q` passed.
- `python -m pytest tests/test_run_mock_mvp.py::test_run_mock_mvp_writes_core_outputs -q` then failed because `phylogeny_manifest` was not yet produced by the mock MVP.
- Added `phylogeny_manifest.tsv` generation to `bin/genefam/run_mock_mvp.py`.
- `python -m pytest tests/test_run_mock_mvp.py tests/test_prepare_phylogeny_inputs.py -q` passed.
- `python -m pytest tests -q` passed with 39 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` produced `tables/phylogeny_manifest.tsv` and marked it available in the report index.
- `command -v nextflow` returned no path, so Nextflow execution remains pending.

Commit:
- hash: 991ab94cc8d527f4dedc99353bc375707afedff6
- message: feat: add phylogeny input manifest
- files: phylogeny manifest helper, mock MVP integration, tests, docs, history

Next:
- Add a motif input manifest or MEME output parser so motif analysis can join the same report contract.

## 2026-06-24 - Add GeneFamilyFlow runtime and container profiles

Context:
- The long goal requires a reproducible runtime using the shared environment name `GeneFamilyFlow`.
- The workflow also needs Docker and Apptainer/Singularity-ready execution paths in addition to local conda execution.
- `HISTORY.md` needed the actual commit hash for the previous phylogeny manifest checkpoint.

Decisions:
- Add a project conda environment file at `envs/GeneFamilyFlow.conda.yaml`.
- Add a Dockerfile based on micromamba that creates `GeneFamilyFlow` and exposes `/usr/local/bin/R`.
- Add `.dockerignore` to keep `Reference/`, results, work directories, and caches out of container build context.
- Add `local`, `docker`, and `apptainer` profiles to `workflows/nextflow.config`.
- Disable conda in container profiles to avoid mixing conda and container runtime modes.

Added:
- `envs/GeneFamilyFlow.conda.yaml`
- `Dockerfile`
- `.dockerignore`
- `docs/runtime_environment.md`
- `tests/test_runtime_environment_files.py`

Modified:
- `HISTORY.md`
- `README.md`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py -q` first failed because the conda environment file, Dockerfile, and Nextflow container profiles did not exist.
- Added the runtime files and profiles.
- `python -m pytest tests/test_runtime_environment_files.py -q` passed.
- `python -m pytest tests -q` passed with 42 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` produced the expected mock output index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda`.
- Runtime availability check did not find `nextflow`, `docker`, or `apptainer` in PATH, so full Nextflow/container execution remains pending on this machine.

Commit:
- hash: fc6922c2f4805cae50aa7b40e9d8102bb54129a9
- message: chore: add genefamilyflow runtime profiles
- files: conda environment, Dockerfile, Nextflow profiles, runtime docs, tests, history

Next:
- Add motif input manifest or MEME output parser so motif analysis can join the same report contract.

## 2026-06-24 - Add MEME motif summary parser

Context:
- Motif analysis is part of the final workflow objective.
- The workflow needed a stable parser for MEME text output before motif plots and report integration can be wired.
- `HISTORY.md` also needed the actual commit hash for the previous runtime profile checkpoint.

Decisions:
- Parse the stable `MOTIF` and `letter-probability matrix` lines from MEME text output.
- Output a compact motif summary table with family name, motif ID, motif name, width, site count, and E-value.
- Add `motif_summary` to the mock MVP report index as a pending output until real MEME output is supplied.

Added:
- `bin/genefam/parse_meme_motifs.py`
- `tests/test_parse_meme_motifs.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/input_contract.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_parse_meme_motifs.py -q` first failed because `bin.genefam.parse_meme_motifs` did not exist.
- Implemented `parse_meme_motifs.py`.
- `python -m pytest tests/test_parse_meme_motifs.py -q` passed.
- `python -m pytest tests/test_parse_meme_motifs.py tests/test_run_mock_mvp.py tests/test_runtime_environment_files.py -q` passed with 7 tests.
- `python -m pytest tests -q` passed with 44 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test that parsed a one-motif MEME text file into `motifs.tsv`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` marked `motif_summary` as `not_available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: a1fb6edb991b728e1a4ad0302bd30fd5b27c8973
- message: feat: add meme motif parser
- files: MEME parser, tests, report contract, docs, history

Next:
- Add synteny/MCScanX collinearity parser so duplicate pairs and WGD-related analyses can consume real MCScanX outputs.

## 2026-06-24 - Add MCScanX collinearity parser

Context:
- Synteny and WGD analyses need a bridge from MCScanX `.collinearity` output into normalized pipeline tables.
- `HISTORY.md` also needed the actual commit hash for the previous MEME motif parser checkpoint.

Decisions:
- Parse MCScanX block headers and gene pair rows into a stable `syntenic_pairs` table.
- Preserve block score, block e-value, block pair count, gene pair IDs, and pair e-value.
- Add `syntenic_pairs` to the mock MVP report index as a pending downstream output until real MCScanX output is supplied.

Added:
- `bin/genefam/parse_mcscanx_collinearity.py`
- `tests/test_parse_mcscanx_collinearity.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/input_contract.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_parse_mcscanx_collinearity.py -q` first failed because `bin.genefam.parse_mcscanx_collinearity` did not exist.
- Implemented `parse_mcscanx_collinearity.py`.
- `python -m pytest tests/test_parse_mcscanx_collinearity.py -q` passed.
- `python -m pytest tests/test_parse_mcscanx_collinearity.py tests/test_run_mock_mvp.py -q` passed with 3 tests.
- `python -m pytest tests -q` passed with 45 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test that parsed a one-pair MCScanX `.collinearity` file into `syntenic_pairs.tsv`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` marked `syntenic_pairs` as `not_available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: 23d3cc1869a27bb48f0cfd35d5b9f327e6b6c91f
- message: feat: add mcscanx collinearity parser
- files: MCScanX parser, tests, report contract, docs, history

Next:
- Add Ka/Ks pair table preparation or parser so syntenic pairs can flow into selection pressure and WGD layer modules.

## 2026-06-24 - Add Ka/Ks result parser

Context:
- Ka/Ks and selection pressure analysis are required by the long-term workflow objective.
- MCScanX syntenic pairs now have a parser, but the pipeline still needed a normalized Ka/Ks pair table for selection pressure and WGD-layer analysis.
- `HISTORY.md` also needed the actual commit hash for the previous MCScanX parser checkpoint.

Decisions:
- Add a KaKs_Calculator-style parser that accepts common `Sequence`, `Ka`, `Ks`, and `Ka/Ks` columns.
- Split sequence pair IDs into `gene_a` and `gene_b`.
- Derive `selection_category` from the Ka/Ks ratio: purifying, neutral, or positive.
- Add `kaks_pairs` to the mock MVP report index as a pending downstream output until real Ka/Ks results are supplied.

Added:
- `bin/genefam/parse_kaks_results.py`
- `tests/test_parse_kaks_results.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/input_contract.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_parse_kaks_results.py -q` first failed because `bin.genefam.parse_kaks_results` did not exist.
- Implemented `parse_kaks_results.py`.
- `python -m pytest tests/test_parse_kaks_results.py -q` passed.
- `python -m pytest tests/test_parse_kaks_results.py tests/test_run_mock_mvp.py -q` passed with 4 tests.
- `python -m pytest tests -q` passed with 47 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test that parsed a one-row KaKs_Calculator-style table into normalized `kaks_pairs.tsv`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` marked `kaks_pairs` as `not_available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: 863a86f970e8097cd498a00f15ee9d5f843675db
- message: feat: add kaks result parser
- files: Ka/Ks parser, tests, report contract, docs, history

Next:
- Add a CDS pair extraction/preparation helper so syntenic gene pairs can be passed to KaKs_Calculator once CDS FASTA files are available.

## 2026-06-24 - Add CDS pair preparation for Ka/Ks

Context:
- Ka/Ks parsing is available, but the pipeline also needs a stable way to prepare pairwise CDS FASTA inputs for KaKs_Calculator from syntenic pairs.
- `HISTORY.md` also needed the actual commit hash for the previous Ka/Ks parser checkpoint.

Decisions:
- Add a helper that reads syntenic pair rows plus two CDS FASTA files.
- Write one pair FASTA per gene pair.
- Write a manifest with `gene_a`, `gene_b`, `pair_fasta`, and `expected_kaks`.
- Add `kaks_pair_manifest` to the mock MVP report index as a pending downstream output until real CDS pair preparation is run.

Added:
- `bin/genefam/prepare_kaks_pairs.py`
- `tests/test_prepare_kaks_pairs.py`

Modified:
- `HISTORY.md`
- `docs/input_contract.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_prepare_kaks_pairs.py -q` first failed because `bin.genefam.prepare_kaks_pairs` did not exist.
- Implemented `prepare_kaks_pairs.py`.
- `python -m pytest tests/test_prepare_kaks_pairs.py -q` passed.
- `python -m pytest tests/test_prepare_kaks_pairs.py tests/test_parse_kaks_results.py tests/test_run_mock_mvp.py -q` passed with 6 tests.
- `python -m pytest tests -q` passed with 49 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test that created one pair CDS FASTA and a Ka/Ks manifest row from a syntenic pair.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` marked `kaks_pair_manifest` and `kaks_pairs` as `not_available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: 449a4731997b03f3ac3105fc54eccf5b62534dfa
- message: feat: add kaks pair preparation
- files: Ka/Ks pair preparation helper, tests, report contract, input docs, history

Next:
- Add duplicate type parser/normalizer so MCScanX duplicate classifications can feed retention enrichment without hand-prepared tables.

## 2026-06-24 - Add duplicate type normalizer

Context:
- Retention enrichment requires normalized duplicate type labels.
- Upstream duplicate classification outputs can use different labels such as `WGD`, `segmental`, `whole_genome`, or mixed-case labels.
- `HISTORY.md` also needed the actual commit hash for the previous Ka/Ks pair preparation checkpoint.

Decisions:
- Add a duplicate type normalization helper that accepts common aliases and emits canonical labels.
- Canonical labels are `WGD/segmental`, `tandem`, `proximal`, `dispersed`, and `singleton`.
- Preserve the original label in `raw_duplicate_type`.
- Add `duplicate_classification` to the mock MVP report index as a pending downstream output until real duplicate classifications are supplied.

Added:
- `bin/genefam/normalize_duplicate_types.py`
- `tests/test_normalize_duplicate_types.py`

Modified:
- `HISTORY.md`
- `docs/input_contract.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_normalize_duplicate_types.py -q` first failed because `bin.genefam.normalize_duplicate_types` did not exist.
- Implemented `normalize_duplicate_types.py`.
- `python -m pytest tests/test_normalize_duplicate_types.py -q` passed.
- `python -m pytest tests/test_normalize_duplicate_types.py tests/test_retention_enrichment.py tests/test_run_mock_mvp.py -q` passed with 6 tests.
- `python -m pytest tests -q` passed with 52 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test that normalized `WGD` to `WGD/segmental` and `Tandem` to `tandem`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` marked `duplicate_classification` as `not_available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: d037a9a9d5b01e01ad6941a8b30db52ed3f773ad
- message: feat: add duplicate type normalizer
- files: duplicate type normalizer, tests, report contract, input docs, history

Next:
- Add a family duplicate join helper that intersects family members with normalized duplicate classifications before retention enrichment.

## 2026-06-24 - Add family duplicate join helper

Context:
- Retention enrichment should use family-specific duplicate classifications instead of a hand-prepared family duplicate table.
- The previous checkpoint added normalized duplicate type labels, but the pipeline still needed a bridge from identified family members to those classifications.
- `HISTORY.md` already carried the actual hash for the previous duplicate type normalizer commit.

Decisions:
- Add a small TSV join helper between `family_candidates.tsv`-style member tables and normalized duplicate classifications.
- Fail loudly if any family member is missing a duplicate classification, because partial retention enrichment would silently bias downstream interpretation.
- Keep `duplicate_classification` as the background table and add `family_duplicate_classification` as the family-specific retention-enrichment input.

Added:
- `bin/genefam/join_family_duplicates.py`
- `tests/test_join_family_duplicates.py`

Modified:
- `HISTORY.md`
- `docs/input_contract.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_join_family_duplicates.py -q` first failed because `bin.genefam.join_family_duplicates` did not exist.
- Implemented `join_family_duplicates.py`.
- `python -m pytest tests/test_join_family_duplicates.py -q` passed.
- `python -m pytest tests/test_join_family_duplicates.py tests/test_retention_enrichment.py tests/test_run_mock_mvp.py -q` passed with 6 tests.
- `python -m pytest tests -q` passed with 55 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` marked `family_duplicate_classification` and `retention_enrichment` as `not_available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: ba6b295826b3d1fe5717c3145d9cefcfed79aae8
- message: feat: add family duplicate join helper
- files: family duplicate join helper, tests, report contract, input docs, history

Next:
- Add a duplication/retention table integrator that combines family duplicate classifications with WGD layer or event labels for gamma/beta/alpha/theta-oriented retention summaries.

## 2026-06-24 - Add family WGD event membership helper

Context:
- The workflow can now classify Ks pairs into anonymous WGD layers and map configured layers to named events such as `gamma`, `beta`, `alpha`, and `theta`.
- The family-level retention path still needed a gene-level evidence table connecting family members, duplicate types, WGD layers, named event labels, partners, and Ks values.
- `HISTORY.md` also needed the actual commit hash for the previous family duplicate join helper checkpoint.

Decisions:
- Add a family WGD event membership helper that emits one row per family gene and supporting classified duplicated pair.
- Keep the output gene-level rather than only summary-level so later reports can audit which pair supports each event label.
- Preserve anonymous `wgd_layer` and configured `event_name` together to keep the inference chain explicit.

Added:
- `bin/genefam/annotate_family_wgd_events.py`
- `tests/test_annotate_family_wgd_events.py`

Modified:
- `HISTORY.md`
- `docs/input_contract.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_annotate_family_wgd_events.py -q` first failed because `bin.genefam.annotate_family_wgd_events` did not exist.
- Implemented `annotate_family_wgd_events.py`.
- `python -m pytest tests/test_annotate_family_wgd_events.py -q` passed.
- `python -m pytest tests/test_annotate_family_wgd_events.py tests/test_classify_wgd_layers.py tests/test_build_wgd_event_evidence.py tests/test_run_mock_mvp.py -q` passed with 10 tests.
- `python -m pytest tests -q` passed with 58 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test that annotated `AT1G01010` as `WGD_layer_1` / `alpha` with partner `AT1G01020`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` marked `family_wgd_event_membership` as `not_available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: cec8c9b7ae487ddcc92591db4274c8a553560585
- message: feat: add family WGD event membership
- files: family WGD event membership helper, tests, report contract, input docs, history

Next:
- Add a family event retention summary that counts family genes by duplicate type and named WGD event for report-ready gamma/beta/alpha/theta tables.

## 2026-06-24 - Add family event retention summary helper

Context:
- The previous step produced gene-level WGD event membership rows for family members.
- Reports also need a compact table that counts family genes by WGD layer, named event, and duplicate type.
- `HISTORY.md` also needed the actual commit hash for the previous family WGD event membership checkpoint.

Decisions:
- Add a summary helper that groups by `wgd_layer`, `event_name`, and `duplicate_type`.
- Count unique family genes separately from supporting duplicated-pair evidence rows.
- Keep `gene_ids` in the summary table for quick auditability in small to medium gene families.

Added:
- `bin/genefam/summarize_family_event_retention.py`
- `tests/test_summarize_family_event_retention.py`

Modified:
- `HISTORY.md`
- `docs/input_contract.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_summarize_family_event_retention.py -q` first failed because `bin.genefam.summarize_family_event_retention` did not exist.
- Implemented `summarize_family_event_retention.py`.
- `python -m pytest tests/test_summarize_family_event_retention.py -q` passed.
- `python -m pytest tests/test_summarize_family_event_retention.py tests/test_annotate_family_wgd_events.py tests/test_run_mock_mvp.py -q` passed with 7 tests.
- `python -m pytest tests -q` passed with 60 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- Ran a command-line smoke test where `AT1` had two `alpha` pair evidence rows; the summary counted `family_gene_count=1` and `pair_evidence_count=2`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` marked `family_event_retention_summary` as `not_available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: f4db690adb697338aa8838a30114d39ed2b865e2
- message: feat: add family event retention summary
- files: family event retention summary helper, tests, report contract, input docs, history

Next:
- Wire the duplication/WGD helper chain into Nextflow DSL2 modules so these evidence tables can be produced by the workflow rather than only as standalone Python tools.

## 2026-06-24 - Wire duplication and WGD helper chain into Nextflow

Context:
- Duplication, WGD layer, named-event evidence, family event membership, retention summary, and enrichment helpers were implemented as standalone Python tools.
- The pipeline objective requires these analyses to be part of the Nextflow DSL2 workflow rather than only manual helper commands.
- `HISTORY.md` also needed the actual commit hash for the previous family event retention summary checkpoint.

Decisions:
- Add a dedicated `duplication_retention.nf` DSL2 module for prepared-table duplication/WGD analysis.
- Keep this as an optional branch behind `--run_duplication_retention true` so current species discovery and mock MVP behavior remain unchanged.
- Wire the branch through normalized duplicate types, family duplicate classifications, WGD layer classification, WGD event evidence, family WGD event membership, family event retention summary, and retention enrichment.
- Document the prepared-table Nextflow command in `README.md`.

Added:
- `workflows/modules/duplication_retention.nf`

Modified:
- `HISTORY.md`
- `README.md`
- `workflows/main.nf`
- `workflows/nextflow.config`
- `tests/test_workflow_modules.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py -q` first failed because `workflows/modules/duplication_retention.nf` did not exist and `workflows/main.nf` did not include the duplication/WGD processes.
- Implemented `workflows/modules/duplication_retention.nf` and added optional branch wiring in `workflows/main.nf`.
- `python -m pytest tests/test_workflow_modules.py -q` passed.
- `python -m pytest tests/test_runtime_environment_files.py -q` passed.
- `python -m pytest tests -q` passed with 62 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` preserved the expected report-index entries for family duplicate classification, family WGD event membership, and family event retention summary.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`; real Nextflow/container execution was therefore not verified in this environment.

Commit:
- hash: ff4c3c5bb198b91f95f209868e92eec21899acb2
- message: feat: wire duplication retention workflow branch
- files: Nextflow duplication-retention module, main workflow branch, runtime params, README command, workflow tests, history

Next:
- Add a lightweight report assembly layer that collects report-index outputs and WGD/retention tables into a final Markdown report skeleton.

## 2026-06-24 - Add reusable final report assembler

Context:
- The workflow had many stable TSV outputs and a mock summary, but no reusable final report assembler shared by mock mode and future full Nextflow runs.
- The project objective requires a final report that can include standard gene-family outputs plus WGD/retention interpretation tables.
- `HISTORY.md` also needed the actual commit hash for the previous Nextflow duplication-retention branch checkpoint.

Decisions:
- Add a Python Markdown report assembler that reads `report_index.tsv` and optional WGD/retention tables.
- Add `final_report.md` to mock MVP outputs and the report index.
- Add a Nextflow `ASSEMBLE_REPORT` process that calls the same Python report assembler.
- Keep the report text explicit that named WGD events are metadata-backed interpretations of synteny/Ks layers.

Added:
- `bin/genefam/assemble_report.py`
- `tests/test_assemble_report.py`
- `workflows/modules/report.nf`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_assemble_report.py -q` first failed because `bin.genefam.assemble_report` did not exist.
- Implemented `assemble_report.py`.
- `python -m pytest tests/test_assemble_report.py -q` passed.
- `python -m pytest tests/test_run_mock_mvp.py -q` first failed because mock MVP did not return `final_report`.
- Added `final_report.md` generation to mock MVP.
- `python -m pytest tests/test_workflow_modules.py -q` first failed because `workflows/modules/report.nf` did not exist.
- Added `workflows/modules/report.nf` and included `ASSEMBLE_REPORT` from `workflows/main.nf`.
- `python -m pytest tests/test_run_mock_mvp.py -q` passed.
- `python -m pytest tests/test_workflow_modules.py -q` passed.
- `python -m pytest tests -q` passed with 66 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` wrote `results/mock_mvp/report/final_report.md` and marked `final_report` as `available` in the report index.
- Runtime availability check found `/Users/liuyue/miniforge3/bin/conda` and did not find `nextflow`, `docker`, or `apptainer`; real Nextflow/container execution was therefore not verified in this environment.

Commit:
- hash: bf99fde230ba664726bc7518496abd0f97b50cb9
- message: feat: add final report assembler
- files: final report assembler, mock MVP final report output, report Nextflow module, README output list, tests, history

Next:
- Add plot-generation workflow processes that call `/usr/local/bin/R` for family counts, Ka/Ks, and expression heatmap outputs, then reference those plots from the final report layer.

## 2026-06-24 - Wire R plotting processes and plot manifest reporting

Context:
- R plotting scripts existed for family counts, Ka/Ks, and expression heatmaps, but they were not exposed as Nextflow processes.
- The final report assembler could summarize tables, but it could not yet reference generated plot artifacts.
- `HISTORY.md` also needed the actual commit hash for the previous final report assembler checkpoint.

Decisions:
- Add a dedicated `plots.nf` module that runs all R plotting scripts through `${params.r_bin}`.
- Preserve the project rule that R steps use `/usr/local/bin/R` via Nextflow config rather than shell-default `R`.
- Add a small plot manifest helper so generated plot paths can be listed in final reports.
- Extend the final report assembler with a `Plots` section driven by `plot_manifest.tsv`.

Added:
- `bin/genefam/build_plot_manifest.py`
- `tests/test_build_plot_manifest.py`
- `workflows/modules/plots.nf`

Modified:
- `HISTORY.md`
- `bin/genefam/assemble_report.py`
- `tests/test_assemble_report.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py -q` first failed because `workflows/modules/plots.nf` did not exist and `workflows/main.nf` did not include plot processes.
- `python -m pytest tests/test_assemble_report.py -q` first failed because `assemble_report()` did not accept `plot_manifest` and the CLI did not recognize `--plot-manifest`.
- Implemented `workflows/modules/plots.nf` and extended `assemble_report.py`.
- `python -m pytest tests/test_workflow_modules.py -q` passed.
- `python -m pytest tests/test_assemble_report.py -q` passed.
- `python -m pytest tests/test_build_plot_manifest.py -q` first failed because `bin.genefam.build_plot_manifest` did not exist.
- Implemented `build_plot_manifest.py`.
- `python -m pytest tests/test_build_plot_manifest.py -q` passed.
- `python -m pytest tests/test_workflow_modules.py tests/test_assemble_report.py tests/test_build_plot_manifest.py -q` passed with 12 tests.
- `python -m pytest tests -q` passed with 70 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` preserved final report generation and wrote a `Plots` section with the expected no-manifest message.
- Runtime availability check found `/usr/local/bin/R` and `/Users/liuyue/miniforge3/bin/conda`; it did not find `nextflow`, `docker`, or `apptainer`.

Commit:
- hash: 5f9620392212e673f9c384f002f871014aa2f5d8
- message: feat: wire R plotting workflow outputs
- files: R plotting Nextflow module, plot manifest helper, final report plot section, workflow tests, history

Next:
- Add workflow/documentation coverage for alignment, phylogeny, motif, chromosome, and expression modules so the remaining standard gene-family analysis surface is represented consistently in Nextflow.

## 2026-06-24 - Add standard analysis workflow modules

Context:
- Core helper scripts already existed for alignment manifests, phylogeny manifests, motif parsing, chromosome locations, and expression subsetting.
- The Nextflow DSL2 surface still did not represent several standard gene-family analysis modules from the project objective.
- `HISTORY.md` also needed the actual commit hash for the previous R plotting workflow checkpoint.

Decisions:
- Add `alignment_phylogeny.nf` for alignment input preparation, MAFFT alignment, phylogeny input preparation, IQ-TREE execution, and MEME motif parsing.
- Add `annotation_integration.nf` for chromosome location extraction and family expression matrix subsetting.
- Include these processes from `workflows/main.nf` without forcing them into the default species-discovery or mock-MVP branches.
- Keep the current modules as command-ready workflow surfaces; full external-tool execution still depends on installed tools such as MAFFT, IQ-TREE, MEME, and Nextflow.

Added:
- `workflows/modules/alignment_phylogeny.nf`
- `workflows/modules/annotation_integration.nf`

Modified:
- `HISTORY.md`
- `README.md`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py -q` first failed because `workflows/modules/alignment_phylogeny.nf` and `workflows/modules/annotation_integration.nf` did not exist and `workflows/main.nf` did not include the related process names.
- Implemented the two DSL2 modules and included them from `workflows/main.nf`.
- `python -m pytest tests/test_workflow_modules.py -q` passed with 11 tests.
- `python -m pytest tests -q` passed with 73 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` preserved alignment and phylogeny manifests as available, while motif summary, chromosome locations, and family expression remained explicit pending outputs in the report index and final report.
- Runtime availability check found `/usr/local/bin/R` and `/Users/liuyue/miniforge3/bin/conda`; it did not find `nextflow`, `docker`, `apptainer`, `mafft`, `iqtree2`, or `meme`.

Commit:
- hash: 750dc76baf276c93803312c2107c76fec48819e7
- message: feat: add standard analysis workflow modules
- files: alignment/phylogeny/motif Nextflow module, annotation/expression Nextflow module, workflow includes, workflow tests, README status, history

Next:
- Add a documented end-to-end readiness checklist and command audit so remaining gaps toward a truly runnable final release are explicit and testable.

## 2026-06-24 - Add end-to-end readiness audit

Context:
- The repository now has broad helper, module, mock, report, plotting, WGD, and retention coverage.
- Full end-to-end execution still depends on machine-level commands such as Nextflow, Docker/Apptainer, HMMER, DIAMOND, MAFFT, IQ-TREE, and MEME.
- The project needed a durable way to distinguish repository readiness from local runtime readiness.
- `HISTORY.md` also needed the actual commit hash for the previous standard analysis workflow module checkpoint.

Decisions:
- Add a command readiness audit script that writes a TSV report and exits non-zero when any required runtime command is missing.
- Document repository-level checks, mock MVP outputs, runtime command audit, and interpretation in `docs/readiness_checklist.md`.
- Link the readiness checklist from `README.md`.

Added:
- `bin/genefam/audit_readiness.py`
- `tests/test_audit_readiness.py`
- `docs/readiness_checklist.md`

Modified:
- `HISTORY.md`
- `README.md`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_readiness.py -q` first failed because `bin.genefam.audit_readiness` did not exist.
- Implemented `audit_readiness.py`.
- `python -m pytest tests/test_audit_readiness.py -q` passed.
- Added readiness documentation and static coverage in `tests/test_runtime_environment_files.py`.
- `python -m pytest tests -q` initially failed because the readiness checklist test referenced a `config` variable from another test scope.
- Moved the `genefam-pipeline:latest` assertion back to the Nextflow config test.
- `python -m pytest tests -q` passed with 77 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` wrote a non-empty `results/mock_mvp/report/final_report.md`.
- `python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv` wrote the readiness TSV and exited `1`, as expected on this machine.
- Readiness TSV showed `/Users/liuyue/miniforge3/bin/conda` and `/usr/local/bin/R` as available, and `nextflow`, `docker`, `apptainer`, `hmmsearch`, `diamond`, `mafft`, `iqtree2`, and `meme` as missing.

Commit:
- hash: 039232d2dd1ffe7c97d9fe1471049bfad6749c01
- message: feat: add readiness audit
- files: readiness audit script, readiness checklist docs, README link, runtime environment tests, history

Next:
- Use the readiness audit to guide the final release pass: either install/activate missing runtime tools for real Nextflow execution or keep documenting the exact external-state blocker while continuing repository-level improvements.

## 2026-06-24 - Add YAML-driven run plan output

Context:
- The workflow is YAML-driven in configuration, but each run did not yet emit a concise machine-readable run plan showing project, runtime, species selection, mock mode, and enabled modules.
- The final report could list output availability, but not the actual YAML-driven execution intent.
- `HISTORY.md` also needed the actual commit hash for the previous readiness audit checkpoint.

Decisions:
- Add a run plan builder that turns the config into a stable `section/key/value` TSV.
- Include runtime, species group/include/exclude, mock mode, and all module switches.
- Add `run_plan.tsv` to mock MVP outputs and the final report index.
- Document `run_plan.tsv` as an expected mock output in README and the readiness checklist.

Added:
- `bin/genefam/build_run_plan.py`
- `tests/test_build_run_plan.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/readiness_checklist.md`
- `bin/genefam/run_mock_mvp.py`
- `tests/test_run_mock_mvp.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_run_plan.py -q` first failed because `bin.genefam.build_run_plan` did not exist.
- Implemented `build_run_plan.py`.
- `python -m pytest tests/test_build_run_plan.py -q` passed.
- `python -m pytest tests/test_build_run_plan.py tests/test_run_mock_mvp.py -q` passed with 5 tests.
- `python -m pytest tests -q` passed with 80 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` wrote `results/mock_mvp/tables/run_plan.tsv`, marked `run_plan` as `available` in `report_index.tsv`, and included it in `final_report.md`.
- `results/mock_mvp/tables/run_plan.tsv` included `runtime/environment/GeneFamilyFlow` and `module/report/enabled`.
- `python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv` still exited `1` because local external runtime commands remain missing; the TSV showed conda and `/usr/local/bin/R` as available and Nextflow/container/bioinformatics tools as missing.

Commit:
- pending

Next:
- Tighten configuration validation around module dependencies, so enabling modules such as Ka/Ks, expression, chromosome, or duplication retention requires the corresponding input files and parameters.
