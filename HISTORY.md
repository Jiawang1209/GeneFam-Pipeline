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
- hash: 826f373c5202dec108129ffa7e0029e5a9bb0c08
- message: feat: add YAML run plan output
- files: run plan helper, mock MVP run_plan output, README/readiness output docs, tests, history

Next:
- Tighten configuration validation around module dependencies, so enabling modules such as Ka/Ks, expression, chromosome, or duplication retention requires the corresponding input files and parameters.

## 2026-06-24 - Validate module dependency rules

Context:
- YAML run plans now expose which modules are enabled, but config validation did not yet reject inconsistent module combinations.
- Enabling modules such as Ka/Ks, expression, chromosome location, motif, phylogeny, or duplication retention without required inputs or prerequisites would fail later in the workflow.
- `HISTORY.md` also needed the actual commit hash for the previous YAML run plan checkpoint.

Decisions:
- Add static validation rules for module dependencies at config-validation time.
- Keep dependency errors explicit and tied to the exact config path the user should change.
- Document the rules in both the config schema notes and the input contract.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `schemas/config.schema.yaml`
- `tests/test_validate_config.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py -q` first failed 5 new dependency-rule tests because validation did not yet enforce module prerequisites.
- Implemented dependency checks in `validate_config.py`.
- `python -m pytest tests/test_validate_config.py -q` passed with 12 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python -m pytest tests -q` passed with 85 tests.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` preserved `run_plan` and `final_report` outputs.
- `python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv` still exited `1` because local external runtime commands remain missing; the TSV showed conda and `/usr/local/bin/R` as available and Nextflow/container/bioinformatics tools as missing.

Commit:
- hash: 95b5a6ded8c813a111a2e7ca168f39835e045814
- message: feat: validate module dependencies
- files: config validator dependency rules, config schema notes, input contract docs, validator tests, history

Next:
- Add user-facing examples for enabling advanced modules safely, including the minimal YAML changes required for Ka/Ks, expression, chromosome location, and duplication-retention runs.

## 2026-06-24 - Add advanced module configuration examples

Context:
- Module dependency validation now rejects inconsistent advanced-module settings.
- Users also need a passing example that shows the minimal YAML changes required to enable Ka/Ks, chromosome location, expression integration, synteny, duplication retention, named WGD events, phylogeny, and motif analysis.
- `HISTORY.md` also needed the actual commit hash for the previous module dependency validation checkpoint.

Decisions:
- Add `configs/advanced_modules.example.yaml` as a validation-passing advanced configuration template with placeholder user-data paths.
- Add `docs/advanced_module_examples.md` with validation, run-plan, and readiness commands.
- Link the advanced config and docs from README.
- Add tests so the advanced example remains synchronized with config validation rules.

Added:
- `configs/advanced_modules.example.yaml`
- `docs/advanced_module_examples.md`
- `tests/test_advanced_module_config_examples.py`

Modified:
- `HISTORY.md`
- `README.md`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_advanced_module_config_examples.py -q` first failed because `configs/advanced_modules.example.yaml` did not exist.
- Added the advanced module example config.
- `python -m pytest tests/test_advanced_module_config_examples.py -q` passed.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- Added advanced module documentation and static documentation checks.
- `python -m pytest tests -q` passed with 88 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/build_run_plan.py --config configs/advanced_modules.example.yaml --out results/GDSL_advanced_example/tables/run_plan.tsv` wrote a run plan showing `GeneFamilyFlow`, `duplication_retention enabled`, `expression enabled`, and `kaks enabled`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` wrote a non-empty final report.
- `python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv` still exited `1` because local external runtime commands remain missing; the TSV showed conda and `/usr/local/bin/R` as available and Nextflow/container/bioinformatics tools as missing.

Commit:
- hash: 882eca25fd2a9e1ab3a44ae5efd33653ce31286b
- message: docs: add advanced module config examples
- files: advanced module example config, advanced module docs, README links, example validation tests, history

Next:
- Add a final release audit document that maps each original goal requirement to current evidence, known gaps, and the command that verifies it.

## 2026-06-24 - Add release audit requirement map

Context:
- The repository now has broad workflow modules, helpers, configs, reports, readiness audit, and advanced examples.
- The full objective still cannot be marked complete on this machine because readiness audit shows missing external runtime commands.
- A requirement-to-evidence release audit was needed so the remaining status is explicit and auditable rather than conversational.
- `HISTORY.md` also needed the actual commit hash for the previous advanced module example checkpoint.

Decisions:
- Add `docs/release_audit.md` mapping each major goal requirement to repository evidence and verification commands.
- Explicitly classify the current state as repository-ready but runtime-blocked on this machine.
- Link the release audit from README.
- Add a static documentation test to keep the audit covering key goal phrases and commands.

Added:
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`

Modified:
- `HISTORY.md`
- `README.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not exist.
- Added `docs/release_audit.md` and README link.
- `python -m pytest tests/test_release_audit_docs.py -q` passed.
- `python -m pytest tests -q` passed with 89 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_mock_mvp.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/mock_mvp` wrote a non-empty final report and included `run_plan` as available.
- `python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv` still exited `1`; the TSV showed conda and `/usr/local/bin/R` available and Nextflow/container/bioinformatics tools missing.

Commit:
- hash: 0e8c3235f78cc4fb09be15c6b4e823e8b4167c21
- message: docs: add release audit map
- files: release audit docs, README link, release audit documentation test, history

Next:
- Continue repository-level polish while the full-runtime blocker remains, or install/activate the missing runtime commands and run the actual Nextflow/container smoke tests.

## 2026-06-24 - Add release checks runner

Context:
- The release audit listed the verification commands, but the repository still needed one command that runs the main checks and writes a durable summary.
- The full objective remains runtime-blocked on this machine until Nextflow/container and bioinformatics commands are installed or activated.

Decisions:
- Add a release check runner that executes tests, both YAML validators, the mock MVP, and the readiness audit.
- Write both TSV and Markdown summaries so the run can be inspected by scripts and by humans.
- Return a non-zero exit code when any required check fails, including readiness failures from missing external runtime tools.
- Escape pipe characters in Markdown table cells so command output cannot break the release report table.

Added:
- `bin/genefam/run_release_checks.py`
- `tests/test_run_release_checks.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/release_audit.md`
- `docs/readiness_checklist.md`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py -q` first failed the new Markdown escaping test because pipe characters were not escaped.
- Implemented Markdown table-cell escaping.
- `python -m pytest tests/test_run_release_checks.py -q` passed with 4 tests.
- `python -m pytest tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` passed with 6 tests.
- `python -m pytest tests -q` passed with 93 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` wrote `release_checks.tsv` and `release_checks.md`; pytest, config validation, and mock MVP passed, while readiness audit failed.
- `results/readiness/command_readiness.tsv` showed conda and `/usr/local/bin/R` available, with nextflow, docker, apptainer, hmmsearch, diamond, mafft, iqtree2, and meme missing.

Commit:
- hash: 737b510079e873656a4fcbecfb0d122e60879d5b
- message: feat: add release checks runner
- files: release check runner, release check tests, README/docs release-check commands, readiness checklist, history

Next:
- Install or activate missing runtime commands, then rerun `python bin/genefam/run_release_checks.py --outdir results/release_checks` and actual Nextflow/container smoke tests.

## 2026-06-24 - Add runtime bootstrap planner

Context:
- The readiness audit could report missing runtime commands, but it did not yet turn that evidence into a machine-specific recovery plan.
- The Conda environment file also needed to carry the workflow engine route itself, not only downstream bioinformatics tools.
- The full objective remains runtime-blocked until at least one Nextflow/container route is actually executable on this machine.

Decisions:
- Add a bootstrap planner that reads `results/readiness/command_readiness.tsv` and writes a Markdown plan plus executable shell script.
- Include `openjdk` and `nextflow` in `envs/GeneFamilyFlow.conda.yaml` so the local Conda route can provide the workflow engine.
- Integrate the bootstrap planner into the release checks runner after readiness audit, so a failed readiness check still leaves actionable next-step files.
- Document the bootstrap planner in README, runtime environment notes, readiness checklist, and release audit.

Added:
- `bin/genefam/plan_runtime_bootstrap.py`
- `tests/test_plan_runtime_bootstrap.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_release_checks.py`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `docs/runtime_environment.md`
- `envs/GeneFamilyFlow.conda.yaml`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` first failed because `bin.genefam.plan_runtime_bootstrap` did not exist.
- Implemented `plan_runtime_bootstrap.py` and added `openjdk` plus `nextflow` to the `GeneFamilyFlow` Conda environment.
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` passed with 3 tests.
- `python -m pytest tests/test_runtime_environment_files.py tests/test_run_release_checks.py -q` then failed because docs and release checks did not yet include the bootstrap planner.
- Integrated the bootstrap planner into release checks and readiness docs.
- `python -m pytest tests/test_runtime_environment_files.py tests/test_run_release_checks.py tests/test_plan_runtime_bootstrap.py -q` passed with 13 tests.
- `python -m pytest tests/test_plan_runtime_bootstrap.py tests/test_runtime_environment_files.py tests/test_run_release_checks.py tests/test_release_audit_docs.py -q` passed with 14 tests.
- `python -m pytest tests -q` passed with 97 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv` still exited `1`; `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` wrote `runtime_bootstrap_plan.md` and `runtime_bootstrap.sh`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because readiness audit failed, but pytest, config validation, mock MVP, and runtime bootstrap plan passed.

Commit:
- hash: 9dfae0ff0bac393f07249aada7be8a2458bab962
- message: feat: add runtime bootstrap planner
- files: runtime bootstrap planner, GeneFamilyFlow environment update, release checks integration, runtime docs, tests, history

Next:
- Use `results/readiness/runtime_bootstrap.sh` or the Markdown plan to install/activate the missing runtime route, then rerun release checks and a real Nextflow/container smoke test.

## 2026-06-24 - Wire standard identification branch

Context:
- The workflow contained HMMER, DIAMOND, domain filtering, family summary, and plotting modules, but the normal main workflow only prepared the species manifest.
- A real standard analysis route needs YAML-derived HMMER/DIAMOND input tables, per-species evidence detection, candidate merging, cross-species candidate concatenation, family count summaries, and plotting.
- The first wiring attempt made the default Nextflow branch too heavy; the project still needs a lightweight default species-manifest checkpoint, so real identification should be explicit.

Decisions:
- Add `build_identification_inputs.py` to turn a YAML config plus species manifest into HMMER and DIAMOND input TSV files.
- Add `concat_tsv.py` and `CONCAT_FAMILY_CANDIDATES` so per-species candidate outputs can feed family-level summaries.
- Add `workflows/modules/identification_inputs.nf`.
- Wire an explicit `--run_identification true` branch in `workflows/main.nf` from species discovery through HMMER, DIAMOND, domain filtering, candidate concatenation, family summary, and family-count plotting.
- Keep the default Nextflow branch as a lightweight species manifest run.
- Add a small reference peptide fixture and point `configs/example.config.yaml` to it so the documented identification branch can build DIAMOND inputs.

Added:
- `bin/genefam/build_identification_inputs.py`
- `bin/genefam/concat_tsv.py`
- `workflows/modules/identification_inputs.nf`
- `tests/fixtures/reference/GDSL_reference.pep.fa`
- `tests/test_build_identification_inputs.py`
- `tests/test_concat_tsv.py`

Modified:
- `HISTORY.md`
- `README.md`
- `configs/example.config.yaml`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/domain_filter.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_identification_inputs.py tests/test_concat_tsv.py -q` first failed because both helper modules were missing.
- Implemented both helper modules.
- `python -m pytest tests/test_build_identification_inputs.py tests/test_concat_tsv.py -q` passed with 5 tests.
- `python -m pytest tests/test_workflow_modules.py -q` first failed because `identification_inputs.nf`, `CONCAT_FAMILY_CANDIDATES`, and main workflow wiring were missing.
- Implemented the Nextflow module and workflow wiring.
- `python -m pytest tests/test_workflow_modules.py -q` passed with 14 tests.
- `python -m pytest tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` then failed when the identification branch was not explicitly gated by `params.run_identification`.
- Added `params.run_identification` and restored the lightweight default branch.
- `python -m pytest tests/test_workflow_modules.py -q` passed with 14 tests.
- `python -m pytest tests/test_build_identification_inputs.py::test_example_config_builds_diamond_inputs_for_identification_branch -q` first failed because `configs/example.config.yaml` had no reference peptide path.
- Added `tests/fixtures/reference/GDSL_reference.pep.fa` and updated the example config.
- `python -m pytest tests/test_build_identification_inputs.py::test_example_config_builds_diamond_inputs_for_identification_branch -q` passed.
- `python -m pytest tests/test_release_audit_docs.py tests/test_runtime_environment_files.py tests/test_workflow_modules.py tests/test_build_identification_inputs.py tests/test_concat_tsv.py -q` passed with 26 tests.
- `python bin/genefam/discover_species.py --config configs/example.config.yaml --groups configs/species_groups.yaml --out results/identification_inputs_smoke/species_manifest.tsv` and `python bin/genefam/build_identification_inputs.py --config configs/example.config.yaml --species-manifest results/identification_inputs_smoke/species_manifest.tsv --outdir results/identification_inputs_smoke` wrote HMMER and DIAMOND input rows for Arabidopsis_thaliana and Brassica_rapa.
- `python -m pytest tests -q` passed with 107 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because readiness audit failed, but pytest, config validation, mock MVP, and runtime bootstrap plan passed.

Commit:
- hash: fcf84488fe763f626334a96e2b349220a03c8e12
- message: feat: wire standard identification branch
- files: identification input builder, TSV concatenation helper, Nextflow identification branch, example reference fixture, docs, tests, history

Next:
- Run full repository verification and release checks; when runtime tools are available, verify `nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml --run_identification true`.

## 2026-06-24 - Add standard branch postprocessing manifests

Context:
- The standard identification branch could produce candidate tables and family counts, but it did not yet bridge candidates into downstream FASTA, alignment/phylogeny manifests, or a standard report index.
- Existing helpers prepared alignment and phylogeny manifests from a family FASTA, so the missing piece was candidate-to-FASTA extraction plus report-index assembly.
- Full alignment/tree execution still depends on external runtime tools, but manifest generation can be tested without MAFFT or IQ-TREE.

Decisions:
- Add `extract_family_sequences.py` to extract cross-species family member peptide sequences from `family_candidates.tsv` and `species_manifest.tsv`.
- Add `build_standard_report_index.py` to describe standard branch outputs in the same report-index format used by reports.
- Add `workflows/modules/standard_postprocess.nf` with `EXTRACT_FAMILY_SEQUENCES` and `BUILD_STANDARD_REPORT_INDEX`.
- Wire the explicit `--run_identification true` branch through family FASTA extraction, alignment manifest preparation, phylogeny manifest preparation, plot manifest generation, and standard report-index generation.
- Keep actual MAFFT/IQ-TREE execution separate from manifest preparation until runtime tools are installed and verified.

Added:
- `bin/genefam/extract_family_sequences.py`
- `bin/genefam/build_standard_report_index.py`
- `workflows/modules/standard_postprocess.nf`
- `tests/test_extract_family_sequences.py`
- `tests/test_standard_branch_report_index.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_extract_family_sequences.py -q` first failed because `bin.genefam.extract_family_sequences` did not exist.
- Implemented `extract_family_sequences.py`.
- `python -m pytest tests/test_extract_family_sequences.py -q` passed with 2 tests.
- `python -m pytest tests/test_standard_branch_report_index.py -q` first failed because `bin.genefam.build_standard_report_index` did not exist.
- Implemented `build_standard_report_index.py`.
- `python -m pytest tests/test_standard_branch_report_index.py -q` passed with 2 tests.
- `python -m pytest tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` first failed because `standard_postprocess.nf` and main workflow wiring were missing.
- Added the standard postprocess module and wired the standard branch.
- `python -m pytest tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` passed with 2 tests.
- `python -m pytest tests/test_extract_family_sequences.py tests/test_standard_branch_report_index.py tests/test_workflow_modules.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` passed with 26 tests.
- A Python smoke chain generated `family_members.faa`, `alignment_manifest.tsv`, `phylogeny_manifest.tsv`, and `report_index.tsv` under `results/standard_postprocess_smoke`.
- `python -m pytest tests -q` passed with 112 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because readiness audit failed, but pytest, config validation, mock MVP, and runtime bootstrap plan passed.

Commit:
- hash: 8b34fec00c15bf009a355eb93da367800ba168a7
- message: feat: add standard branch postprocessing
- files: family sequence extraction, standard report index builder, standard postprocess Nextflow module, workflow wiring, docs, tests, history

Next:
- Continue toward runtime installation and real Nextflow/container smoke tests, then wire actual MAFFT/IQ-TREE execution once tools are available.

## 2026-06-24 - Add standard branch final report assembly

Context:
- The standard identification branch could generate a report index, but it still did not assemble a standard `final_report.md`.
- `assemble_report.py` already supported report-index-only runs with optional WGD and retention tables, so the missing piece was a Nextflow process that invokes it for the standard branch.
- The existing `ASSEMBLE_REPORT` process is designed for WGD/retention paths, so the standard branch needed a lighter wrapper that only requires `report_index` and `plot_manifest`.

Decisions:
- Add `ASSEMBLE_STANDARD_REPORT` to `workflows/modules/standard_postprocess.nf`.
- Wire `--run_identification true` through `ASSEMBLE_STANDARD_REPORT` after `BUILD_STANDARD_REPORT_INDEX` and `BUILD_PLOT_MANIFEST`.
- Add `params.project_name` to `workflows/nextflow.config` for the standard report title.
- Document that the standard identification branch assembles `final_report.md`.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/release_audit.md`
- `tests/test_assemble_report.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/standard_postprocess.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` first failed because `ASSEMBLE_STANDARD_REPORT` and main workflow wiring were missing.
- Added `ASSEMBLE_STANDARD_REPORT` and wired it into the standard branch.
- `python -m pytest tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` passed with 2 tests.
- `python -m pytest tests/test_assemble_report.py::test_assemble_report_cli_supports_standard_branch_without_wgd_tables -q` passed.
- `python -m pytest tests/test_assemble_report.py tests/test_workflow_modules.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` passed with 25 tests.
- A standard report smoke initially failed because the smoke command passed a report index as the plot manifest; after generating a real `plot_manifest.tsv`, `python bin/genefam/assemble_report.py --project-name GDSL_demo --gene-family GDSL --report-index results/standard_postprocess_smoke/report_index.tsv --plot-manifest results/standard_postprocess_smoke/plot_manifest.tsv --out results/standard_postprocess_smoke/final_report.md` wrote `final_report.md` with output availability, empty WGD sections, plots, and the WGD interpretation note.
- `python -m pytest tests -q` passed with 113 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because readiness audit failed, but pytest, config validation, mock MVP, and runtime bootstrap plan passed.

Commit:
- hash: 9d300e99629ad6dad3027a3567e5d08d3f74956a
- message: feat: assemble standard branch report
- files: standard report Nextflow process, workflow wiring, report docs, assemble report test, history

Next:
- Continue toward runtime installation and real Nextflow/container smoke tests; then verify the standard report-producing branch through Nextflow rather than Python smoke commands.

## 2026-06-24 - Add standard branch smoke release check

Context:
- The standard identification branch had a Python smoke path and could assemble `final_report.md`, but this proof was not part of the durable release checks.
- Release checks should prove both the mock MVP and the standard branch post-identification/reporting chain before reporting repository readiness.
- Full Nextflow runtime is still blocked by missing external commands, so the standard smoke intentionally avoids HMMER, DIAMOND, MAFFT, and IQ-TREE while exercising the same downstream helpers.

Decisions:
- Add `run_standard_smoke.py` to produce standard branch outputs from example config, species groups, and prepared mock evidence.
- Include standard branch smoke in `run_release_checks.py` before readiness audit.
- Document the smoke command and `results/standard_smoke/report/final_report.md` in README and release audit.

Added:
- `bin/genefam/run_standard_smoke.py`
- `tests/test_run_standard_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_standard_smoke.py -q` first failed because `bin/genefam/run_standard_smoke.py` did not exist.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_standard_branch_smoke_before_readiness -q` first failed because release checks did not include standard branch smoke.
- Implemented `run_standard_smoke.py`; the first run failed because direct CLI execution lacked the repository root on `sys.path`.
- Added the repository root import guard and cleaned the report-index constant access.
- `python -m pytest tests/test_run_standard_smoke.py -q` passed.
- Added standard branch smoke to release checks.
- `python -m pytest tests/test_run_release_checks.py tests/test_run_standard_smoke.py -q` passed with 7 tests.
- `python -m pytest tests/test_release_audit_docs.py tests/test_runtime_environment_files.py tests/test_run_release_checks.py tests/test_run_standard_smoke.py -q` passed with 14 tests.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/standard_smoke` wrote `results/standard_smoke/report/final_report.md`.
- `python -m pytest tests -q` passed with 115 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because readiness audit failed, but pytest, config validation, mock MVP, standard branch smoke, and runtime bootstrap plan passed.

Commit:
- hash: a2cb764e26eaa09d41a9c86090243b78c318def5
- message: feat: add standard branch smoke check
- files: standard smoke runner, release checks integration, README/release audit docs, tests, history

Next:
- Continue toward real Nextflow/container runtime verification; release checks now prove mock MVP and standard branch smoke before the runtime readiness gate.

## 2026-06-24 - Add WGD named-event smoke check

Context:
- The release checks covered mock MVP and the standard branch smoke, but they did not yet prove the gamma, beta, alpha, theta WGD event evidence chain.
- The project already had WGD layer classification, named-event evidence, family WGD membership, retention summary, and enrichment helpers.
- A small offline WGD smoke can validate the biological interpretation chain without requiring external MCScanX or Ka/Ks tools.

Decisions:
- Add `run_wgd_smoke.py` with built-in miniature family members, duplicate classifications, and Ks pairs spanning alpha, beta, gamma, and theta.
- Run the same helper chain used by the duplication-retention branch: duplicate normalization, family duplicate join, WGD layer classification, named-event evidence, family WGD annotation, retention summary, enrichment, report index, and final report.
- Add WGD event smoke to `run_release_checks.py` before readiness audit.
- Document the smoke command and `results/wgd_smoke/report/final_report.md` in README and release audit.

Added:
- `bin/genefam/run_wgd_smoke.py`
- `tests/test_run_wgd_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_wgd_smoke.py -q` first failed because `bin/genefam/run_wgd_smoke.py` did not exist.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_wgd_smoke_before_readiness -q` first failed because release checks did not include WGD event smoke.
- Implemented `run_wgd_smoke.py`.
- `python -m pytest tests/test_run_wgd_smoke.py -q` passed.
- Added WGD event smoke to release checks.
- `python -m pytest tests/test_run_release_checks.py tests/test_run_wgd_smoke.py -q` passed with 8 tests.
- `python -m pytest tests/test_release_audit_docs.py tests/test_runtime_environment_files.py tests/test_run_release_checks.py tests/test_run_wgd_smoke.py -q` passed with 15 tests.
- `python bin/genefam/run_wgd_smoke.py --events-config configs/wgd_events.brassicaceae.yaml --outdir results/wgd_smoke` wrote `wgd_event_evidence.tsv` with alpha, beta, gamma, and theta configured named events plus `results/wgd_smoke/report/final_report.md`.
- `python -m pytest tests -q` passed with 117 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because readiness audit failed, but pytest, config validation, mock MVP, standard branch smoke, WGD event smoke, and runtime bootstrap plan passed.

Commit:
- hash: 7f3ab1bba538b608eb785ea845af633c01d1ea35
- message: feat: add WGD smoke release check
- files: WGD smoke runner, release checks integration, README/release audit docs, tests, history

Next:
- Continue toward real Nextflow/container runtime verification; release checks now prove mock MVP, standard branch smoke, and WGD named-event smoke before the runtime readiness gate.

## 2026-06-24 - Add Nextflow smoke gate

Context:
- Repository-level Python smoke checks now cover mock MVP, standard branch reporting, and WGD named-event evidence.
- The remaining core blocker is real Nextflow/container runtime verification.
- The project needed a durable smoke gate that either runs the Nextflow mock MVP when Nextflow is installed or writes an explicit blocker report when Nextflow is missing.

Decisions:
- Add `run_nextflow_smoke.py` to run `nextflow run workflows/main.nf ... --mock_mvp true` when `nextflow` is available.
- When Nextflow is missing, write `results/nextflow_smoke/nextflow_smoke.tsv` and `results/nextflow_smoke/nextflow_smoke.md` with `missing_nextflow` status and exit non-zero.
- Add Nextflow mock MVP smoke to `run_release_checks.py` before readiness audit.
- Document the Nextflow smoke command and blocker output in README and release audit.

Added:
- `bin/genefam/run_nextflow_smoke.py`
- `tests/test_run_nextflow_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_nextflow_smoke.py -q` first failed because `bin.genefam.run_nextflow_smoke` did not exist.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_nextflow_smoke_before_readiness -q` first failed because release checks did not include Nextflow mock MVP smoke.
- Implemented `run_nextflow_smoke.py`.
- `python -m pytest tests/test_run_nextflow_smoke.py -q` passed with 2 tests.
- Added Nextflow mock MVP smoke to release checks.
- `python -m pytest tests/test_run_release_checks.py tests/test_run_nextflow_smoke.py -q` passed with 10 tests.
- `python -m pytest tests/test_release_audit_docs.py tests/test_runtime_environment_files.py tests/test_run_nextflow_smoke.py tests/test_run_release_checks.py -q` passed with 17 tests.
- `python bin/genefam/run_nextflow_smoke.py --outdir results/nextflow_smoke` exited `1` and wrote `missing_nextflow` reports because `nextflow` is not currently on `PATH`.
- `python -m pytest tests -q` passed with 120 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because Nextflow mock MVP smoke failed with `missing_nextflow` and readiness audit failed, but pytest, config validation, mock MVP, standard branch smoke, WGD event smoke, and runtime bootstrap plan passed.

Commit:
- hash: f0def0542965c77c7436462c5204d17be33d9fbf
- message: feat: add Nextflow smoke gate
- files: Nextflow smoke runner, release checks integration, README/release audit docs, tests, history

Next:
- Install or activate Nextflow and the GeneFamilyFlow runtime, then rerun `python bin/genefam/run_nextflow_smoke.py --outdir results/nextflow_smoke` and `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

## 2026-06-24 - Wire chromosome and expression report contract into standard branch

Context:
- The chromosome-location and expression-subset helper processes existed, but their Nextflow module arguments did not match the Python CLIs.
- The standard identification branch did not yet route chromosome coordinates into the report index.
- A species-bank workflow needs chromosome localization to work from `species_manifest.tsv` and `family_candidates.tsv`, not from hand-written per-species ID files.

Decisions:
- Extend `extract_chromosome_locations.py` with a multi-species `--family-candidates` plus `--species-manifest` interface while keeping the legacy single-GFF3 interface.
- Extend `subset_expression_matrix.py` so expression subsetting can read gene IDs directly from `family_candidates.tsv`.
- Add `chromosome_locations` and `family_expression` to the standard report index contract.
- Wire `EXTRACT_CHROMOSOME_LOCATIONS` into the `run_identification` branch and make `family_expression` optional through `params.expression_matrix`.
- Update README and release audit so the standard branch documents chromosome output and optional expression integration.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/extract_chromosome_locations.py`
- `bin/genefam/run_standard_smoke.py`
- `bin/genefam/subset_expression_matrix.py`
- `docs/release_audit.md`
- `tests/test_extract_chromosome_locations.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_standard_smoke.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_subset_expression_matrix.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/annotation_integration.nf`
- `workflows/modules/standard_postprocess.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_extract_chromosome_locations.py tests/test_subset_expression_matrix.py tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_workflow_modules.py -q` first failed because `extract_locations_for_manifest` and `gene_ids_from_family_candidates` did not exist.
- Implemented the multi-species chromosome interface, family-candidate expression interface, report-index keys, standard smoke chromosome output, and Nextflow wiring.
- `python -m pytest tests/test_extract_chromosome_locations.py tests/test_subset_expression_matrix.py tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_workflow_modules.py -q` passed with 24 tests.
- `python -m pytest tests/test_runtime_environment_files.py::test_readme_documents_explicit_standard_identification_branch tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands -q` first failed because README did not document `chromosome_locations.tsv`.
- Updated README and release audit.
- `python -m pytest tests/test_extract_chromosome_locations.py tests/test_subset_expression_matrix.py tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_workflow_modules.py tests/test_runtime_environment_files.py tests/test_release_audit_docs.py -q` passed with 31 tests.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/standard_smoke` wrote `results/standard_smoke/tables/chromosome_locations.tsv` for `Arabidopsis_thaliana` and `Brassica_rapa`; the report index marks `chromosome_locations` available and `family_expression` missing when no expression matrix is supplied.
- `python -m pytest tests -q` passed with 122 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because Nextflow mock MVP smoke failed with `missing_nextflow` and readiness audit failed, but pytest, config validation, mock MVP, standard branch smoke, WGD event smoke, and runtime bootstrap plan passed.

Commit:
- hash: 005448c2a30f3fc2eddc6d4c0dbf5d75afcc2513
- message: feat: wire annotation outputs into standard branch
- files: multi-species chromosome extraction, family-candidate expression interface, standard report index contract, Nextflow standard branch wiring, README/release audit docs, tests, history

Next:
- Continue wiring optional expression plotting and full Nextflow runtime verification after Nextflow/GeneFamilyFlow tools are available.

## 2026-06-24 - Add expression matrix smoke path for standard branch

Context:
- The standard branch now records `family_expression` in the report index, but the offline smoke could only demonstrate the missing-expression case.
- RNA-seq expression integration needs a quick local verification path that does not require Nextflow or external bioinformatics tools.

Decisions:
- Add an optional `--expression-matrix` argument to `run_standard_smoke.py`.
- When supplied, subset the expression matrix to genes in `family_candidates.tsv`, write `tables/family_expression.tsv`, and mark `family_expression` available in `report_index.tsv`.
- Document the `--expression-matrix` smoke option in README.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_standard_smoke.py`
- `tests/test_run_standard_smoke.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_standard_smoke.py::test_run_standard_smoke_writes_family_expression_when_matrix_is_provided -q` first failed because `run_standard_smoke.py` did not accept `--expression-matrix`.
- Implemented optional expression subsetting in `run_standard_smoke.py`.
- `python -m pytest tests/test_run_standard_smoke.py -q` passed with 2 tests.
- `python -m pytest tests/test_runtime_environment_files.py::test_readme_documents_explicit_standard_identification_branch -q` first failed because README did not document `--expression-matrix`.
- Updated README.
- `python -m pytest tests/test_run_standard_smoke.py tests/test_runtime_environment_files.py -q` passed with 8 tests.
- Ran `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --expression-matrix <tmp_expr> --outdir results/standard_expression_smoke`; it wrote `tables/family_expression.tsv` with `AT1G01010` and `BraA010001`, and `report_index.tsv` marked `family_expression` available.
- `python -m pytest tests -q` passed with 123 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because Nextflow mock MVP smoke failed with `missing_nextflow` and readiness audit failed, but pytest, config validation, mock MVP, standard branch smoke, WGD event smoke, and runtime bootstrap plan passed.

Commit:
- hash: 055a36abce4a80b31c6c451781e7d868b8d7e09e
- message: feat: add standard expression smoke path
- files: standard smoke expression option, README docs, tests, history

Next:
- Add a plotted expression smoke/report path or move to installing/activating the Nextflow and GeneFamilyFlow runtime to close the remaining release gate.

## 2026-06-24 - Make readiness audit GeneFamilyFlow-aware

Context:
- The `GeneFamilyFlow` Conda environment exists on this machine, but the active shell is `base`, so PATH-only readiness audits marked all Conda-contained bioinformatics tools as missing.
- Direct probing showed `hmmsearch` is available inside `GeneFamilyFlow`, while `nextflow`, `diamond`, `mafft`, `iqtree2`, and `meme` are still missing from that environment.
- Release checks needed to distinguish host PATH availability from Conda-environment availability.

Decisions:
- Add optional `--conda-env GeneFamilyFlow` support to `audit_readiness.py`.
- When a command is not on PATH but is found inside the requested Conda environment, mark it as `available_in_conda`.
- Count `available_in_conda` as available in readiness summaries.
- Run the release-check readiness audit with `--conda-env GeneFamilyFlow` by default.
- Update README, readiness checklist, and release audit commands to use the environment-aware audit.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_readiness.py`
- `bin/genefam/run_release_checks.py`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `tests/test_audit_readiness.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `conda env list` showed a `GeneFamilyFlow` environment at `/Users/liuyue/miniforge3/envs/GeneFamilyFlow`.
- `conda run -n GeneFamilyFlow nextflow -version` exited `127`; `conda run -n GeneFamilyFlow hmmsearch -h` exited `0`; `conda run -n GeneFamilyFlow diamond version`, `mafft --version`, `iqtree2 --version`, and `meme -version` exited `127`.
- `python -m pytest tests/test_audit_readiness.py -q` first failed because `audit_commands` did not accept `conda_env`, `summarize_status` did not count `available_in_conda`, and the CLI did not accept `--conda-env`.
- Implemented Conda-environment command probing in `audit_readiness.py`.
- `python -m pytest tests/test_audit_readiness.py -q` passed with 5 tests.
- `python -m pytest tests/test_run_release_checks.py::test_default_readiness_check_audits_genefamilyflow_conda_env -q` first failed because release checks did not pass `--conda-env GeneFamilyFlow`.
- Updated release checks and docs.
- `python -m pytest tests/test_audit_readiness.py tests/test_run_release_checks.py tests/test_runtime_environment_files.py tests/test_release_audit_docs.py -q` passed with 21 tests.
- `python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv` exited `1` and marked `hmmsearch` as `available_in_conda`; `nextflow`, `docker`, `apptainer`, `diamond`, `mafft`, `iqtree2`, and `meme` remain missing.
- `python -m pytest tests -q` passed with 126 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because Nextflow mock MVP smoke failed with `missing_nextflow` and readiness audit found the remaining missing runtime commands, but pytest, config validation, mock MVP, standard branch smoke, WGD event smoke, and runtime bootstrap plan passed.

Commit:
- hash: 5cdcded52a650061ac85f03d2a225f9aa549a696
- message: feat: audit GeneFamilyFlow runtime commands
- files: environment-aware readiness audit, release check integration, README/readiness/release audit docs, tests, history

Next:
- Update the `GeneFamilyFlow` environment from `envs/GeneFamilyFlow.conda.yaml` so `nextflow`, `diamond`, `mafft`, `iqtree2`, and `meme` become available, then rerun Nextflow smoke and release checks.

## 2026-06-24 - Run Nextflow smoke through GeneFamilyFlow

Context:
- `conda env update -n GeneFamilyFlow -f envs/GeneFamilyFlow.conda.yaml --prune` initially failed on osx-arm64 because `jcvi` and `kaks_calculator` are not available from the current Conda channels for this platform.
- `conda search` confirmed `jcvi` is available for osx-64 and linux-64 but not osx-arm64; `kaks_calculator` is also unavailable on osx-arm64.
- After removing platform-limited packages from the local environment file, the `GeneFamilyFlow` environment update succeeded and installed `nextflow`, `diamond`, `mafft`, `meme`, and related tools.
- The first real Nextflow smoke attempts exposed two workflow bugs: Nextflow tried to create a Conda env from the string `GeneFamilyFlow`, and modules resolved `${projectDir}/bin` as `workflows/bin`.
- A later Nextflow smoke exposed that staged config files still contained repo-relative paths, so `run_mock_mvp.py` needed a repo-root base directory.

Decisions:
- Keep `envs/GeneFamilyFlow.conda.yaml` as the local cross-platform environment and move Linux/container-only tools to `envs/GeneFamilyFlow.linux-64.conda.yaml`.
- Make Docker build from the Linux-specific environment file so `jcvi` and `kaks_calculator` remain available in the container route.
- Add a Nextflow `activated` profile that disables per-process Conda creation when Nextflow is launched from an already prepared `GeneFamilyFlow` environment.
- Teach `run_nextflow_smoke.py` to resolve `nextflow` inside `GeneFamilyFlow`, prepend that environment to `PATH`, and run with `-profile activated`.
- Support `iqtree` as an alias for the audited `iqtree2` command, because the installed IQ-TREE 3 package exposes `iqtree` on this machine.
- Change workflow module script paths from `${projectDir}/bin` and `${projectDir}/scripts` to `${projectDir}/../bin` and `${projectDir}/../scripts`.
- Add `--base-dir` to `run_mock_mvp.py` and pass `${projectDir}/..` from the Nextflow mock module so staged config files can resolve species-bank paths against the repository root.

Added:
- `envs/GeneFamilyFlow.linux-64.conda.yaml`

Modified:
- `HISTORY.md`
- `Dockerfile`
- `README.md`
- `bin/genefam/audit_readiness.py`
- `bin/genefam/plan_runtime_bootstrap.py`
- `bin/genefam/run_mock_mvp.py`
- `bin/genefam/run_nextflow_smoke.py`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `docs/runtime_environment.md`
- `envs/GeneFamilyFlow.conda.yaml`
- `tests/test_audit_readiness.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_mock_mvp.py`
- `tests/test_run_nextflow_smoke.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_run_release_checks.py`
- `tests/test_workflow_modules.py`
- `workflows/modules/alignment_phylogeny.nf`
- `workflows/modules/annotation_integration.nf`
- `workflows/modules/diamond_search.nf`
- `workflows/modules/domain_filter.nf`
- `workflows/modules/duplication_retention.nf`
- `workflows/modules/family_summary.nf`
- `workflows/modules/hmmer_search.nf`
- `workflows/modules/identification_inputs.nf`
- `workflows/modules/mock_mvp.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/prepare_species.nf`
- `workflows/modules/report.nf`
- `workflows/modules/standard_postprocess.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `conda env update -n GeneFamilyFlow -f envs/GeneFamilyFlow.conda.yaml --prune` first failed with `PackagesNotFoundError` for `jcvi`.
- `conda search -c bioconda -c conda-forge jcvi --platform osx-arm64` returned no match; osx-64 and linux-64 searches returned available `jcvi` builds.
- `conda search -c bioconda -c conda-forge kaks_calculator --platform osx-arm64` returned no match.
- `conda search -c bioconda -c conda-forge mcscanx --platform osx-arm64`, `meme --platform osx-arm64`, and `diamond --platform osx-arm64` returned available packages.
- `python -m pytest tests/test_runtime_environment_files.py::test_conda_environment_file_defines_genefamilyflow_runtime tests/test_runtime_environment_files.py::test_linux_conda_environment_keeps_platform_limited_full_toolchain tests/test_runtime_environment_files.py::test_dockerfile_installs_genefamilyflow_and_exposes_usr_local_r tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file -q` first failed until the environment files, Dockerfile, and docs were split.
- `conda env update -n GeneFamilyFlow -f envs/GeneFamilyFlow.conda.yaml --prune` succeeded after the split.
- `conda run -n GeneFamilyFlow python -c "import shutil; ..."` found `nextflow`, `diamond`, `mafft`, `meme`, and `hmmsearch`; it found `iqtree` but not `iqtree2`.
- `python -m pytest tests/test_audit_readiness.py::test_audit_commands_accepts_iqtree_alias_for_iqtree2 tests/test_workflow_modules.py::test_alignment_phylogeny_module_covers_alignment_tree_and_motif_steps -q` first failed until the IQ-TREE alias and workflow fallback were added.
- `python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv` now marks `nextflow`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as `available_in_conda`; only `docker` and `apptainer` remain missing.
- `python bin/genefam/run_nextflow_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_smoke` first failed because Nextflow tried to create a Conda environment from `GeneFamilyFlow`; adding the `activated` profile moved it forward.
- The next smoke failed because modules referenced `${projectDir}/bin`, which resolved to `workflows/bin`; changing module paths to `${projectDir}/../bin` moved it forward.
- The next smoke failed because `tests/fixtures/species_bank` was resolved inside the Nextflow work directory; adding `--base-dir` to `run_mock_mvp.py` and passing `${projectDir}/..` from `mock_mvp.nf` fixed it.
- `python bin/genefam/run_nextflow_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_smoke` passed and wrote `results/nextflow_smoke/nextflow_smoke.md`.
- `python -m pytest tests/test_runtime_environment_files.py tests/test_release_audit_docs.py tests/test_plan_runtime_bootstrap.py tests/test_run_nextflow_smoke.py tests/test_audit_readiness.py tests/test_workflow_modules.py tests/test_run_mock_mvp.py -q` passed with 40 tests.
- `python -m pytest tests -q` passed with 132 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml` returned `Configuration OK`.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` returned `Configuration OK`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, standard branch smoke, WGD event smoke, Nextflow mock MVP smoke, and runtime bootstrap plan passed.

Commit:
- hash: 633986f14e7ab3cd89b77ed4a19ac9f83d6bb05b
- message: feat: run Nextflow smoke through GeneFamilyFlow
- files: split local/Linux runtime environments, Dockerfile, Nextflow activated profile, module script path fixes, mock MVP base-dir support, Nextflow smoke runner, readiness/bootstrap docs, tests, history

Next:
- Install or expose Docker or Apptainer to verify container profiles; otherwise continue wiring the standard external-tool branch beyond the mock MVP using the now-working `GeneFamilyFlow` local environment.

## 2026-06-24 - Add Nextflow standard branch smoke

Context:
- The previous Nextflow verification only exercised the mock MVP wrapper branch.
- The real `run_identification` branch still needed a stable smoke path that enters the standard DSL2 graph without depending on toy proteins matching the real PF00657 HMM profile.
- A first real standard-branch Nextflow run failed in `BUILD_PLOT_MANIFEST` because unquoted plot descriptions with spaces were split by the shell.

Decisions:
- Add `params.mock_external_tools` for development and CI smoke runs so the standard branch can inject fixture HMMER/DIAMOND evidence while still exercising species discovery, domain filtering, family summary, sequence extraction, annotation integration, plotting manifest, and report assembly wiring.
- Keep the real HMMER/DIAMOND path as the default when `mock_external_tools` is false.
- Add `--base-dir ${projectDir}/..` to species discovery and identification input generation so staged Nextflow config files can resolve repository-relative species banks, HMM profiles, and reference peptides.
- Quote all `BUILD_PLOT_MANIFEST --plot` values because their descriptions contain spaces.
- Add a dedicated `run_nextflow_standard_smoke.py` release gate after the mock MVP Nextflow smoke.

Added:
- `bin/genefam/run_nextflow_standard_smoke.py`
- `tests/test_run_nextflow_standard_smoke.py`

Modified:
- `HISTORY.md`
- `bin/genefam/build_identification_inputs.py`
- `bin/genefam/discover_species.py`
- `bin/genefam/run_release_checks.py`
- `tests/test_build_identification_inputs.py`
- `tests/test_discover_species.py`
- `tests/test_run_release_checks.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/domain_filter.nf`
- `workflows/modules/identification_inputs.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/prepare_species.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_discover_species.py::test_discover_species_resolves_relative_root_against_base_dir tests/test_build_identification_inputs.py::test_resolve_input_paths_rebases_relative_manifest_and_family_paths tests/test_workflow_modules.py::test_domain_filter_module_can_concatenate_species_candidate_tables tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch tests/test_run_nextflow_standard_smoke.py tests/test_run_release_checks.py::test_default_checks_include_nextflow_standard_smoke_before_readiness -q` first failed because `resolve_input_paths` and `run_nextflow_standard_smoke.py` did not exist.
- After implementation, the same targeted test set passed with 8 tests.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` first failed in `BUILD_PLOT_MANIFEST` because plot descriptions were unquoted.
- `python -m pytest tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin -q` first failed until `--plot` arguments were quoted.
- `python -m pytest tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin -q` passed with 1 test.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` passed and wrote `results/nextflow_standard_smoke/nextflow_standard_smoke.tsv`.
- `python -m pytest tests -q` passed with 138 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 427b783556904c6ee321378cb21e1ccafd8b2af5
- message: feat: add Nextflow standard branch smoke
- files: Nextflow standard branch smoke runner, mock external evidence wiring, repo-root path rebasing for staged configs, quoted plot manifest arguments, release check integration, tests, history

Next:
- Add `publishDir` or a report copy-out strategy for the standard Nextflow branch so completed process outputs land in `results/nextflow_standard_smoke/standard` instead of remaining only in Nextflow work directories.
- After container runtimes are installed or exposed, rerun release checks to verify Docker/Apptainer profiles.

## 2026-06-24 - Publish standard Nextflow outputs

Context:
- The standard Nextflow `run_identification` smoke completed, but the user-facing outputs remained in Nextflow work directories unless the user inspected task paths.
- A final reusable workflow needs stable `results/<run>/tables`, `sequences`, `report`, and `plots` outputs comparable to the Python standard smoke branch.

Decisions:
- Add `publishDir` copy-out rules to standard-branch modules for species manifest, candidate tables, family counts, alignment and phylogeny manifests, chromosome/expression tables, family FASTA, report index, final report, plot manifest, and plots.
- Keep intermediate per-species domain-filter candidates under `tables/domain_filter/` while publishing the merged family candidates table at `tables/family_candidates.tsv`.
- Make `run_nextflow_standard_smoke.py` fail if Nextflow exits zero but core published outputs are missing.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_workflow_modules.py`
- `workflows/modules/alignment_phylogeny.nf`
- `workflows/modules/annotation_integration.nf`
- `workflows/modules/domain_filter.nf`
- `workflows/modules/family_summary.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/prepare_species.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py::test_domain_filter_module_can_concatenate_species_candidate_tables tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_workflow_modules.py::test_standard_nextflow_modules_publish_user_facing_outputs tests/test_run_nextflow_standard_smoke.py::test_expected_published_outputs_cover_standard_user_results -q` first failed because `expected_published_outputs` and the required `publishDir` rules did not exist.
- After implementation, the same targeted test set passed with 5 tests.
- `rm -rf results/nextflow_standard_smoke/standard && python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` passed and published `report/final_report.md`, `report/report_index.tsv`, `report/plot_manifest.tsv`, `tables/family_candidates.tsv`, `tables/family_counts.tsv`, `tables/species_manifest.tsv`, `tables/alignment_manifest.tsv`, `tables/phylogeny_manifest.tsv`, `tables/chromosome_locations.tsv`, `sequences/family_members.faa`, `plots/family_counts.pdf`, and `plots/family_counts.png`.
- `python -m pytest tests -q` passed with 140 tests.
- `python -m py_compile bin/genefam/run_nextflow_standard_smoke.py` passed.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 579e6dd962940d530d427665dd156e60ba38c669
- message: feat: publish Nextflow standard outputs
- files: standard-branch Nextflow publishDir rules, published-output smoke verification, tests, history

Next:
- Improve report-index paths in the Nextflow standard branch so published reports point at published `results/...` paths instead of staged task-local filenames.
- After container runtimes are installed or exposed, rerun release checks to verify Docker/Apptainer profiles.

## 2026-06-24 - Point standard reports at published paths

Context:
- The standard Nextflow branch now publishes files under `results/nextflow_standard_smoke/standard`, but `report_index.tsv` and `final_report.md` still listed staged task-local filenames such as `family_candidates.tsv`.
- User-facing reports should point at the stable published result tree.

Decisions:
- Add an optional `--published-outdir` mode to `build_standard_report_index.py`.
- Keep the existing explicit path mode for Python smoke tests and ad hoc usage.
- Pass `--published-outdir ${params.outdir}` from the Nextflow standard report-index process so reports list `results/.../tables`, `sequences`, and `report` paths.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_standard_report_index.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_standard_branch_report_index.py::test_published_paths_map_standard_outputs_to_user_results_tree tests/test_standard_branch_report_index.py::test_build_standard_report_index_cli_can_write_published_paths tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index -q` first failed because `published_paths` did not exist.
- After implementation, the same targeted test set passed with 3 tests.
- `rm -rf results/nextflow_standard_smoke/standard && python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` passed.
- `results/nextflow_standard_smoke/standard/report/report_index.tsv` now lists published paths such as `results/nextflow_standard_smoke/standard/tables/family_candidates.tsv` and `results/nextflow_standard_smoke/standard/sequences/family_members.faa`.
- `results/nextflow_standard_smoke/standard/report/final_report.md` now shows those same published paths in the Output Availability table.
- `python -m pytest tests -q` passed with 142 tests.
- `python -m py_compile bin/genefam/build_standard_report_index.py` passed.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: d01b5df3cf9ff7ae7b3833740f6350d2f104b1f6
- message: feat: report published standard paths
- files: standard report-index published-path mode, Nextflow report-index wiring, tests, history

Next:
- Wire more WGD/duplication published outputs into the main Nextflow report path so gamma/beta/alpha/theta evidence can be emitted from the same workflow run, not only the WGD smoke helper.
- After container runtimes are installed or exposed, rerun release checks to verify Docker/Apptainer profiles.

## 2026-06-24 - Add Nextflow WGD event smoke and report

Context:
- The Python WGD smoke already validated gamma, beta, alpha, and theta evidence, but the main Nextflow `run_duplication_retention` branch did not publish stable outputs or assemble a WGD-focused final report.
- The final workflow needs named WGD event evidence and retention summaries available from a Nextflow run, not only a helper script.

Decisions:
- Add a WGD report-index builder for published duplication/WGD output paths.
- Add `publishDir` rules to the duplication-retention Nextflow processes.
- Add WGD report-index and final-report processes to `workflows/modules/duplication_retention.nf`.
- Wire those WGD report processes into the `run_duplication_retention` branch in `workflows/main.nf`.
- Add a dedicated `run_nextflow_wgd_smoke.py` that creates small fixture TSV inputs, runs the Nextflow WGD branch through `GeneFamilyFlow`, and fails when core published outputs are missing.
- Add the Nextflow WGD smoke to release checks after the standard Nextflow smoke.

Added:
- `bin/genefam/build_wgd_report_index.py`
- `bin/genefam/run_nextflow_wgd_smoke.py`
- `tests/test_run_nextflow_wgd_smoke.py`
- `tests/test_wgd_report_index.py`

Modified:
- `HISTORY.md`
- `bin/genefam/run_release_checks.py`
- `tests/test_run_release_checks.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/duplication_retention.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_wgd_report_index.py tests/test_run_nextflow_wgd_smoke.py tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes tests/test_run_release_checks.py::test_default_checks_include_nextflow_wgd_smoke_before_readiness -q` first failed because `build_wgd_report_index.py` and `run_nextflow_wgd_smoke.py` did not exist.
- After implementation, the same targeted test set passed with 8 tests.
- `rm -rf results/nextflow_wgd_smoke/wgd results/nextflow_wgd_smoke/inputs && python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke` passed.
- `results/nextflow_wgd_smoke/wgd/tables/wgd_event_evidence.tsv` includes configured named events `alpha`, `beta`, `gamma`, and `theta` with expected relative ages and species scopes from `configs/wgd_events.brassicaceae.yaml`.
- `results/nextflow_wgd_smoke/wgd/report/final_report.md` includes WGD Event Evidence, Family Event Retention, and Duplicate-Type Retention Enrichment sections populated from the Nextflow branch outputs.
- `python -m pytest tests -q` passed with 148 tests.
- `python -m py_compile bin/genefam/build_wgd_report_index.py bin/genefam/run_nextflow_wgd_smoke.py` passed.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 1c145e88f8ea0c56c17c46d0e54e44c52f809250
- message: feat: add Nextflow WGD event smoke
- files: WGD report index builder, Nextflow WGD smoke runner, duplication-retention publish/report processes, release check integration, tests, history

Next:
- Add a documented combined handoff path explaining when to run the standard identification branch versus the duplication/WGD branch and how to feed real MCScanX/KaKs-derived tables into the latter.
- After container runtimes are installed or exposed, rerun release checks to verify Docker/Apptainer profiles.

## 2026-06-24 - Document standard-to-WGD handoff

Context:
- The standard identification branch and the Nextflow WGD branch both run, but users need an explicit handoff path for feeding real MCScanX/KaKs-derived tables into the WGD branch after family identification.
- The README mentioned both branches but did not document the table contracts and concrete output-to-input relationship.

Decisions:
- Add `docs/standard_to_wgd_handoff.md` as the handoff guide from `results/<run>/tables/family_candidates.tsv` into `--run_duplication_retention true`.
- Document required duplicate type and Ka/Ks pair table fields.
- Document the output tables and final report created by the WGD branch.
- Link the new handoff guide from README and include the Nextflow WGD smoke command.

Added:
- `docs/standard_to_wgd_handoff.md`

Modified:
- `HISTORY.md`
- `README.md`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_readme_documents_explicit_standard_identification_branch tests/test_runtime_environment_files.py::test_standard_to_wgd_handoff_doc_links_identification_and_wgd_branches -q` first failed because the README link and handoff document did not exist.
- After documentation updates, the same targeted test set passed with 2 tests.
- `python -m pytest tests -q` passed with 149 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 37d0fa0c6b0cb10702691a924ed6fd760d31c8dc
- message: docs: add standard to WGD handoff
- files: standard-to-WGD handoff guide, README link, documentation tests, history

Next:
- Add or document a minimal real-data style fixture for prepared MCScanX/KaKs handoff tables so users can copy a complete folder-level example.
- After container runtimes are installed or exposed, rerun release checks to verify Docker/Apptainer profiles.

## 2026-06-24 - Add prepared WGD handoff example

Context:
- The standard-to-WGD handoff guide described required prepared tables, but users still needed a small folder-level example they could copy when preparing real MCScanX/KaKs-derived inputs.
- The final workflow should include examples that exercise the same contracts as the Nextflow WGD branch.

Decisions:
- Add `examples/prepared_wgd_handoff/` with minimal `family_candidates.tsv`, `duplicate_types.tsv`, `kaks_pairs.tsv`, and README.
- Make the example cover alpha, beta, gamma, and theta WGD layers through Ks values and configured event names.
- Add tests that run the example rows through the actual duplicate-normalization, family-join, and WGD-layer classification helpers.
- Verify the README command by running the documented Nextflow WGD branch against the example files.

Added:
- `examples/prepared_wgd_handoff/README.md`
- `examples/prepared_wgd_handoff/duplicate_types.tsv`
- `examples/prepared_wgd_handoff/family_candidates.tsv`
- `examples/prepared_wgd_handoff/kaks_pairs.tsv`
- `tests/test_prepared_wgd_handoff_example.py`

Modified:
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_prepared_wgd_handoff_example.py -q` first failed because the example folder did not exist.
- After adding the example, `python -m pytest tests/test_prepared_wgd_handoff_example.py -q` passed with 2 tests.
- `rm -rf results/example_prepared_wgd && PATH="/Users/liuyue/miniforge3/envs/GeneFamilyFlow/bin:$PATH" nextflow run workflows/main.nf -c workflows/nextflow.config -profile activated --config configs/example.config.yaml --run_duplication_retention true --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv --family_members examples/prepared_wgd_handoff/family_candidates.tsv --kaks_pairs examples/prepared_wgd_handoff/kaks_pairs.tsv --events_config configs/wgd_events.brassicaceae.yaml --ks_bins 0.3,0.8,1.5 --wgd_event_args "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta" --outdir results/example_prepared_wgd` passed.
- `results/example_prepared_wgd/tables/wgd_event_evidence.tsv` contains alpha, beta, gamma, and theta rows.
- `results/example_prepared_wgd/report/final_report.md` includes populated WGD Event Evidence, Family Event Retention, and Duplicate-Type Retention Enrichment sections.
- `python -m pytest tests -q` passed with 151 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 7ee8914b5ce334254d6cd0ed68733bff05396a8b
- message: docs: add prepared WGD handoff example
- files: prepared WGD handoff example TSVs, example README, contract tests, history

Next:
- Consider adding a small release audit row for the prepared handoff example, then continue toward container-runtime verification when Docker or Apptainer is available.

## 2026-06-24 - Audit prepared WGD handoff release evidence

Context:
- The prepared WGD handoff example had a tested Nextflow command, but the release audit did not yet expose it as part of the requirement-to-evidence map.
- Users need one release-facing checklist that shows how the standard identification outputs can be converted into WGD event evidence through prepared MCScanX/Ka/Ks tables.

Decisions:
- Extend `docs/release_audit.md` with the prepared WGD handoff command that runs `--run_duplication_retention true` on `examples/prepared_wgd_handoff/`.
- Add a requirement audit row for the standard-to-WGD prepared handoff.
- Lock this release audit coverage with `tests/test_release_audit_docs.py`.

Added:
- none

Modified:
- `HISTORY.md`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not mention `run_nextflow_wgd_smoke.py`.
- After updating the release audit, `python -m pytest tests/test_release_audit_docs.py -q` passed with 1 test.
- `python -m pytest tests -q` passed with 151 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 7a192a746a5661818bf898fe7f5f5bac586ba5dc
- message: docs: audit prepared WGD handoff evidence
- files: release audit prepared WGD handoff evidence, release audit tests, history

Next:
- Continue toward container-runtime verification when Docker or Apptainer is available, or add the next reusable project-facing example that can be verified entirely through `GeneFamilyFlow`.

## 2026-06-24 - Add prepared WGD handoff release gate

Context:
- The prepared WGD handoff example was documented and independently runnable, but `run_release_checks.py` did not yet execute it as a formal release gate.
- The final pipeline should have a single release-check command that proves the standard-to-WGD prepared-table path can run through Nextflow and produce named alpha, beta, gamma, and theta event evidence.

Decisions:
- Add `bin/genefam/run_prepared_wgd_handoff_example.py` as a wrapper around the prepared example Nextflow command.
- Make the wrapper verify required example inputs, published WGD outputs, and presence of alpha, beta, gamma, and theta in `wgd_event_evidence.tsv`.
- Add `prepared WGD handoff example` to the default release checks before the readiness audit.
- Update release audit documentation and tests so the new gate is discoverable.

Added:
- `bin/genefam/run_prepared_wgd_handoff_example.py`

Modified:
- `HISTORY.md`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py -q` first failed because the default check list did not contain `prepared WGD handoff example`.
- After adding the wrapper and default release check, `python -m pytest tests/test_run_release_checks.py -q` passed with 12 tests.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not mention `run_prepared_wgd_handoff_example.py`.
- After updating the release audit, `python -m pytest tests/test_release_audit_docs.py -q` passed with 1 test.
- `python bin/genefam/run_prepared_wgd_handoff_example.py --conda-env GeneFamilyFlow --example-dir examples/prepared_wgd_handoff --outdir results/example_prepared_wgd` exited `0`.
- `results/example_prepared_wgd/prepared_wgd_handoff_example.tsv` reports `prepared_wgd_handoff_example` as `passed`.
- `results/example_prepared_wgd/tables/wgd_event_evidence.tsv` contains alpha, beta, gamma, and theta rows.
- `python -m pytest tests -q` passed with 152 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, prepared WGD handoff example, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- pending

Next:
- Continue toward container-runtime verification when Docker or Apptainer is available; otherwise focus on reusable user-facing examples and documentation that are fully verifiable through `GeneFamilyFlow`.
