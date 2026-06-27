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

## 2026-06-27 15:41 - Enforce Reference ignore governance

Context:
- The active `/goal` requires `Reference/` to stay read-only and out of commits.
- `git status --short --untracked-files=all` still listed many `Reference/` files, which made accidental staging too easy even though the Reference governance audit blocked tracked Reference changes.

Decisions:
- Add `Reference/` to `.gitignore` so paper PDFs, source data, and reference plotting scripts do not appear as normal untracked files.
- Extend `bin/genefam/audit_reference_governance.py` so release checks fail when `.gitignore` does not explicitly ignore `Reference/`.
- Keep tracked `Reference/` changes release-blocking.
- Report `Reference/ ignored: yes/no` in the Reference governance Markdown and add a machine-readable `gitignore_reference` row to the TSV.

Added:
- Test coverage requiring `.gitignore` to exclude `Reference/`.
- Test coverage proving the Reference governance CLI fails when the Reference ignore rule is missing.
- Release-audit documentation contract for `.gitignore` and `Reference/ ignored` evidence.

Modified:
- `.gitignore`
- `bin/genefam/audit_reference_governance.py`
- `docs/release_audit.md`
- `tests/test_audit_reference_governance.py`
- `tests/test_release_audit_docs.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_reference_governance.py -q` first failed because `.gitignore` did not contain `Reference/` and the audit CLI did not support `--gitignore-path`.
- `python -m pytest tests/test_audit_reference_governance.py -q` passed with 4 tests after adding the ignore rule and audit check.
- `python bin/genefam/audit_reference_governance.py --outdir results/reference_governance` exited 0; `results/reference_governance/reference_governance.md` reported `Reference/ ignored: yes`, `Tracked changes: 0`, and `Untracked reference files: 0`.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not mention `.gitignore`.
- `python -m pytest tests/test_release_audit_docs.py -q` passed after updating the release audit documentation.
- `python -m pytest tests/test_audit_reference_governance.py tests/test_release_audit_docs.py tests/test_run_release_checks.py::test_default_checks_include_reference_governance_before_readiness -q` passed with 6 tests.
- `git status --short --untracked-files=all` no longer listed `Reference/` files.
- `python -m pytest tests -q` passed with 447 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and wrote `Passed: 50`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; `Reference governance audit` passed in the release table.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed release, quickstart, handoff, report-index, figure-gallery, delivery-manifest, and delivery-bundle outputs.
- `sed -n '1,80p' results/local_acceptance/local_acceptance_summary.md` confirmed all analysis/report/delivery acceptance steps passed, with only `final_stage_blocker` blocked by Docker/Apptainer reproducibility.

Commit:
- hash: c1aa2daf3eab39f8824b4fd484ce01172f9abbaf
- message: `test: enforce reference ignore governance`
- files: Reference ignore governance, audit script, release-audit docs, tests, and history entry.

Next:
- Continue final MVP hardening; Docker/Apptainer reproducibility remains the final-stage blocker.

## 2026-06-27 15:30 - Synchronize Chinese README acceptance entrypoints

Context:
- The English README and quickstart now document report-index path closure, figure-gallery audit, and delivery-manifest audit, but the Chinese README was still missing those newest MVP acceptance entrypoints.
- The active `/goal` requires a polished MVP that users can understand from the Chinese entrypoint without opening the English documentation first.

Decisions:
- Treat `README.zh-CN.md` as a tested user-facing contract, not an informal summary.
- Keep local acceptance as the main Chinese entrypoint and list report-index, figure-gallery, and delivery-manifest audits directly under it.
- Explain the Docker / Apptainer blocker as a final packaging/runtime verification blocker, not a core analysis-flow failure.

Added:
- Test assertions requiring the Chinese README to mention standard/WGD report-index audits, `figure_gallery_audit`, `delivery_manifest_audit`, and the available indexed-path closure.

Modified:
- `README.zh-CN.md`
- `tests/test_runtime_environment_files.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_chinese_readme_points_to_publication_audit_acceptance -q` first failed because `README.zh-CN.md` did not mention `results/report_index_audit/standard_report_index_audit.md`.
- `python -m pytest tests/test_runtime_environment_files.py::test_chinese_readme_points_to_publication_audit_acceptance -q` passed after updating the Chinese README.
- `python -m pytest tests/test_runtime_environment_files.py -q` passed with 14 tests.
- `python -m pytest tests -q` passed with 445 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and wrote `Passed: 50`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed the final handoff, delivery bundle, report-index audits, figure-gallery audit, delivery-manifest audit, and local acceptance summary.
- `sed -n '1,80p' results/local_acceptance/local_acceptance_summary.md` confirmed release, publication report, report-index, figure-gallery, delivery-manifest, quickstart, and delivery-bundle steps passed, with only `final_stage_blocker` blocked by Docker/Apptainer reproducibility.

Commit:
- hash: 0bcf10efea0d323f305b73217706d60a36d0def9
- message: `docs: sync chinese acceptance entrypoints`
- files: Chinese README acceptance documentation, runtime-environment doc test, and history entry.

Next:
- Continue final MVP hardening; Docker/Apptainer reproducibility remains the final-stage blocker.

## 2026-06-27 13:17 - Require traceability evidence in objective audit

Context:
- Publication report audit now checks `final_report_figure_traceability`, but the long-form objective audit still used the older publication-audit check list.
- The active `/goal` requires final goal evidence to prove every figure has close-reading status, QC evidence, method/software, and reproducibility context, not only that release checks passed.

Decisions:
- Add `final_report_figure_traceability` to the objective-audit publication detail checks.
- Make the `final reports` objective mention `Figure Traceability Matrix` rows explicitly.
- Keep objective audit failure messages pointing to the standard or WGD publication audit check that is missing or pending.

Added:
- Objective-audit test coverage for missing `final_report_figure_traceability`.
- Release-check bridge fixture coverage for the new publication-audit row.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `tests/test_run_release_checks.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure tests/test_audit_objective_completion.py::test_final_reports_require_traceability_matrix_checks_in_publication_audits -q` first failed because `final reports` did not mention or require `Figure Traceability Matrix`.
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure tests/test_audit_objective_completion.py::test_final_reports_require_traceability_matrix_checks_in_publication_audits -q` passed after updating the objective-audit check list and final-report note.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 44 tests.
- `python -m pytest tests -q` first failed because `tests/test_run_release_checks.py::test_write_objective_audit_reads_publication_detail_audits` used an older publication-audit TSV fixture without `final_report_figure_traceability`.
- `python -m pytest tests/test_run_release_checks.py::test_write_objective_audit_reads_publication_detail_audits tests/test_audit_objective_completion.py -q` passed with 45 tests after updating the fixture.
- `python -m pytest tests -q` passed with 434 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 48`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `rg -n "final reports|Figure Traceability Matrix|final_report_figure_traceability|Achieved:|Blocked:|Missing:|Complete:" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv results/publication_report_audit/publication_report_audit.md results/publication_report_audit/wgd_publication_report_audit.md` confirmed objective audit and standard/WGD publication audits expose traceability evidence.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed final handoff outputs.
- `sed -n '1,28p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance steps passed except the final-stage Docker/Apptainer blocker.

Commit:
- hash: 7976f3f3d698f01c9eb7a0a1ddd7ed70b2f82312
- message: `test: require traceability in objective audit`
- files: objective audit, objective/release-check tests, and history entry.

Next:
- Continue final MVP hardening; Docker/Apptainer reproducibility remains the final-stage blocker.

## 2026-06-27 13:07 - Require figure traceability in publication audit

Context:
- The final report now renders a `Figure Traceability Matrix`, but the publication audit still accepted reports that contained per-figure interpretation sections without that matrix.
- The active `/goal` requires the paper-level report package to prove every figure has close-reading status, QC evidence, method/software, and reproducibility context.

Decisions:
- Add a dedicated `final_report_figure_traceability` audit row instead of folding the check into the broader final-report section audit.
- Require the final report to contain the matrix section, canonical matrix header, and one matrix row per interpreted figure.
- Keep diagnostics precise with missing-section, missing-header, and per-figure missing-row notes.

Added:
- `final_report_figure_traceability` publication audit check.
- Test coverage for missing `Figure Traceability Matrix`.
- Updated positive audit fixtures showing matrix rows for standard and PPI figures.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_figure_traceability_matrix -q` first failed with `KeyError: 'final_report_figure_traceability'` because the audit check did not exist.
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_figure_traceability_matrix -q` passed after adding the check.
- `python -m pytest tests/test_audit_publication_report.py -q` first failed in two positive fixtures because they lacked the newly required matrix rows.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 16 tests after updating the positive fixtures.
- `python -m pytest tests/test_release_audit_docs.py tests/test_audit_publication_report.py -q` passed with 17 tests.
- `python -m pytest tests -q` passed with 433 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 48`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `rg -n "final_report_figure_traceability|Passed:|Failed:|Complete:" results/publication_report_audit/publication_report_audit.md results/publication_report_audit/wgd_publication_report_audit.md` confirmed both standard and WGD publication audits report `final_report_figure_traceability` as `passed` and `Complete: true`.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed final handoff outputs.
- `sed -n '1,28p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance steps passed except the final-stage Docker/Apptainer blocker.

Commit:
- hash: b83ed1a392c268078937152f08d3a3b3dcf6782a
- message: `test: require final report traceability audit`
- files: publication report audit, audit tests, and history entry.

Next:
- Continue final MVP hardening; Docker/Apptainer reproducibility remains the final-stage blocker.

## 2026-06-27 12:58 - Add final report figure traceability matrix

Context:
- The active `/goal` requires final reports to support paper-level reading of every figure, including plot path, close-reading status, QC evidence, methods/software, versions, and reproducibility.
- The final report already had separate figure inventory and figure interpretation sections, but there was no compact matrix linking each registered plot to its interpretation/QC/method/reproducibility evidence.

Decisions:
- Add a `Figure Traceability Matrix` to the assembled final report.
- Build the matrix from existing `plot_manifest` and `figure_interpretations` rows so no new input file contract is needed.
- Mark registered plot artifacts without matching interpretation rows as `interpretation_not_provided` so missing interpretation coverage is visible.
- Document the matrix as part of the release-audit contract.

Added:
- Final report section `Figure Traceability Matrix`.
- Per-figure matrix columns for `figure_key`, `plot_path`, `interpretation_status`, `qc_tables`, `method_and_software`, and `reproducibility`.
- Tests covering interpreted figures and missing-interpretation fallback rows.
- Release-audit documentation requirement for the matrix.

Modified:
- `bin/genefam/assemble_report.py`
- `tests/test_assemble_report.py`
- `tests/test_release_audit_docs.py`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_assemble_report.py -q` first failed with 3 expected failures because `Figure Traceability Matrix` was missing from the assembled report.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not mention `Figure Traceability Matrix`.
- `python -m pytest tests/test_assemble_report.py tests/test_release_audit_docs.py -q` passed with 4 tests after the implementation and docs update.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --expression-matrix tests/fixtures/expression/family_expression.tsv --expression-metadata tests/fixtures/expression/sample_metadata.tsv --r-bin /usr/local/bin/R --outdir results/standard_traceability_smoke` exited 0 and generated `results/standard_traceability_smoke/report/final_report.md`.
- `python bin/genefam/run_wgd_smoke.py --events-config configs/wgd_events.brassicaceae.yaml --outdir results/wgd_traceability_smoke` exited 0 and generated `results/wgd_traceability_smoke/report/final_report.md`.
- `python -m pytest tests -q` passed with 432 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 48`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `rg -n "Figure Traceability Matrix|family_counts|gene_family_info_summary|ppi_ggnetview|expression_heatmap|ks_distribution|duplicate_type_kaks|pangenome_kaks|interpretation_not_provided" results/nextflow_standard_feature_smoke/standard/report/final_report.md results/nextflow_wgd_smoke/wgd/report/final_report.md` confirmed formal standard and WGD final reports include the matrix and expose interpreted and fallback rows.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed delivery bundle outputs while keeping only the final-stage Docker/Apptainer blocker.
- `sed -n '1,28p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance steps passed except `final_stage_blocker`.

Commit:
- hash: 05fccf9ff01f2917154002540249fcfdafeecf2a
- message: `feat: add final report figure traceability matrix`
- files: report assembler, assemble-report tests, release audit docs/tests, and history entry.

Next:
- Continue final MVP hardening; Docker/Apptainer reproducibility remains the final-stage blocker.

## 2026-06-27 13:05 - Expose figure gallery in handoff and release audit

Context:
- The active `/goal` requires a paper-level MVP handoff where every figure can be traced to plots, close-reading interpretation, software/R package versions, and final report context.
- The delivery bundle already generated `figure_gallery.tsv` and `figure_gallery.md`, but the handoff report and release audit did not yet list them as first-class evidence.

Decisions:
- Treat the global paper-level figure gallery as a stable handoff section, not only a delivery-bundle byproduct.
- Add tests that require both TSV and Markdown gallery paths in the generated handoff and release audit documentation.
- Regenerate `results/handoff/handoff_report.md` and `results/handoff/handoff_summary.tsv` from the updated handoff builder.

Added:
- Handoff summary section `figure_gallery`.
- Release audit evidence for `results/delivery_bundle/figure_gallery.tsv` and `results/delivery_bundle/figure_gallery.md`.
- Test assertions for the global paper-level figure gallery handoff contract.

Modified:
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`
- `tests/test_release_audit_docs.py`
- `docs/release_audit.md`
- `results/handoff/handoff_report.md`
- `results/handoff/handoff_summary.tsv`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py tests/test_release_audit_docs.py -q` first failed with 3 expected failures because the handoff report, handoff summary TSV, and release audit did not expose the global paper-level figure gallery.
- `python -m pytest tests/test_build_handoff_report.py tests/test_release_audit_docs.py -q` passed with 6 tests after the implementation and docs update.
- `python bin/genefam/build_handoff_report.py` regenerated the handoff report and summary TSV.
- `python -m pytest tests -q` passed with 432 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 48`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `bash scripts/run_local_acceptance.sh` exited 0 and listed `results/delivery_bundle/figure_gallery.tsv` and `results/delivery_bundle/figure_gallery.md` under primary handoff files.
- `sed -n '1,28p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance keeps `Overall status: blocked` only for the final-stage `Docker/Apptainer reproducibility` blocker.
- `sed -n '1,40p' results/handoff/handoff_report.md` and `tail -n 5 results/handoff/handoff_summary.tsv` confirmed the handoff outputs expose the global paper-level figure gallery.

Commit:
- hash: 5ca91bfc58afd1f242610840d2f57ccca886a235
- message: `docs: expose figure gallery in handoff audit`
- files: handoff builder, handoff tests, release audit docs/tests, generated handoff outputs, and history entry.

Next:
- Continue final MVP hardening; Docker/Apptainer reproducibility remains the final-stage blocker.

## 2026-06-27 12:37 - Document figure gallery in README and quickstart

Context:
- The active `/goal` now has a release-checked global paper-level figure gallery.
- The delivery bundle and local acceptance output exposed `figure_gallery.tsv` and `figure_gallery.md`, but README and quickstart docs still described only the delivery manifest and bundle.
- A user following the docs could miss the fastest plot-navigation entry for standard and WGD figures.

Decisions:
- Document `results/delivery_bundle/figure_gallery.tsv` and `results/delivery_bundle/figure_gallery.md` in the English README, Chinese README, and quickstart.
- Describe the gallery as the global paper-level figure gallery connecting plot PDFs to figure interpretations, software/R package versions, and final reports.
- Keep the wording aligned with the existing local acceptance and delivery-bundle sections.

Added:
- English README references to the global paper-level figure gallery and its TSV/Markdown outputs.
- Chinese README references to the `figure_gallery.tsv` and `figure_gallery.md` outputs as `全局论文图件目录`.
- Quickstart references to the gallery in key outputs and delivery-bundle inspection.
- Docs tests requiring the gallery paths and descriptions.

Modified:
- `README.md`
- `README.zh-CN.md`
- `docs/quickstart.md`
- `tests/test_quickstart_docs.py`
- `tests/test_runtime_environment_files.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_quickstart_docs.py tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report tests/test_runtime_environment_files.py::test_chinese_readme_points_to_publication_audit_acceptance -q` first failed because the docs did not mention `figure_gallery.tsv` and `figure_gallery.md`.
- `python -m pytest tests/test_quickstart_docs.py tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report tests/test_runtime_environment_files.py::test_chinese_readme_points_to_publication_audit_acceptance -q` passed with 4 tests after the docs update.
- `python -m pytest tests -q` passed with 432 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 48`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `rg -n "figure_gallery|global paper-level figure gallery|全局论文图件目录" README.md README.zh-CN.md docs/quickstart.md results/release_checks/release_checks.md` confirmed the docs and release evidence expose the gallery entrypoint.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed both `results/delivery_bundle/figure_gallery.tsv` and `results/delivery_bundle/figure_gallery.md` under primary handoff files.
- `sed -n '1,16p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance keeps `Overall status: blocked` only for `final_stage_blocker`.
- `sed -n '1,10p' results/objective_audit/objective_audit.md` confirmed objective audit remains `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: e743277c039a599dbfccbbe400c535594ea8ae75
- message: `docs: document delivery figure gallery`
- files: English README, Chinese README, quickstart, docs tests, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 12:26 - Add release smoke for delivery figure gallery

Context:
- The active `/goal` requires all paper-level figures to be connected to release checks, report indexes, final reports, and local acceptance.
- The delivery bundle now generates a global `figure_gallery.tsv` and `figure_gallery.md`, but release checks did not have a dedicated smoke check proving the gallery generator and key rows remain intact.
- Without a release-level smoke, future changes could break the global plot index while still leaving other analysis checks green.

Decisions:
- Add a dedicated `delivery bundle figure gallery smoke` to the release check list after `quickstart handoff` and before `readiness audit`.
- Implement the smoke with small generated input TSVs so it tests the delivery bundle and gallery writer without depending on stale external result files.
- Check representative standard and WGD rows: `tree_features`, `ppi_ggnetview`, `ks_distribution`, `duplicate_type_kaks`, and software version links.

Added:
- `bin/genefam/run_delivery_bundle_smoke.py`
- Release check entry `delivery bundle figure gallery smoke`.
- Test coverage for the new release check ordering and command.

Modified:
- `bin/genefam/run_release_checks.py`
- `tests/test_run_release_checks.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_delivery_bundle_gallery_smoke_after_quickstart -q` first failed because the new release check was not present.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_delivery_bundle_gallery_smoke_after_quickstart -q` passed after adding the release check.
- `python bin/genefam/run_delivery_bundle_smoke.py --outdir results/delivery_bundle_smoke` initially failed with `ModuleNotFoundError: No module named 'bin'`; adding the repo root to `sys.path` fixed direct script execution.
- `python bin/genefam/run_delivery_bundle_smoke.py --outdir results/delivery_bundle_smoke` exited 0 and wrote `delivery_bundle_smoke.md`, `delivery_manifest.tsv`, `figure_gallery.tsv`, and `figure_gallery.md`.
- `python -m pytest tests/test_run_release_checks.py tests/test_run_delivery_bundle.py -q` passed with 55 tests.
- `python -m pytest tests -q` passed with 432 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 48`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `rg -n "delivery bundle figure gallery smoke|figure_gallery|432 pass" results/release_checks/release_checks.md results/release_checks/release_checks.tsv results/delivery_bundle_smoke/delivery_bundle_smoke.md` confirmed the new smoke is recorded in release evidence.
- `bash scripts/run_local_acceptance.sh` exited 0 and still printed `Final-stage blocker: Docker/Apptainer reproducibility.`
- `sed -n '1,16p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance keeps `Overall status: blocked` only for `final_stage_blocker`.
- `sed -n '1,10p' results/objective_audit/objective_audit.md` confirmed objective audit remains `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 3e932de5d9ce969781365fe95df87c77131fce55
- message: `test: add delivery figure gallery release smoke`
- files: delivery bundle smoke script, release checks, release check tests, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 12:15 - List figure gallery in local acceptance handoff output

Context:
- The active `/goal` now has a global paper-level figure gallery in the delivery bundle.
- `scripts/run_local_acceptance.sh` refreshed and generated the gallery, but the final `Primary handoff files` list did not print `figure_gallery.tsv` or `figure_gallery.md`.
- A user running the local acceptance command could miss the new global plot index even though it existed on disk.

Decisions:
- Add the TSV and Markdown figure gallery paths to the local acceptance primary handoff list.
- Keep the local acceptance summary itself unchanged because it remains a compact pass/fail/blocked status table.

Added:
- Primary handoff terminal lines for `${DELIVERY_OUTDIR}/figure_gallery.tsv`.
- Primary handoff terminal lines for `${DELIVERY_OUTDIR}/figure_gallery.md`.
- Test assertions that the local acceptance script lists both gallery files.

Modified:
- `scripts/run_local_acceptance.sh`
- `tests/test_local_acceptance_script.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_local_acceptance_script.py -q` first failed because `${DELIVERY_OUTDIR}/figure_gallery.tsv` was absent from the script.
- `python -m pytest tests/test_local_acceptance_script.py -q` passed with 2 tests after updating the primary handoff list.
- `python -m pytest tests -q` passed with 431 tests.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed both `results/delivery_bundle/figure_gallery.tsv` and `results/delivery_bundle/figure_gallery.md` under `Primary handoff files`.
- `sed -n '1,10p' results/release_checks/release_checks.md` confirmed `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `sed -n '1,16p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance keeps `Overall status: blocked` only for `final_stage_blocker`.
- `sed -n '1,10p' results/objective_audit/objective_audit.md` confirmed objective audit remains `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 21ce16688ab4b18543d12b1d587a06a4893ef514
- message: `docs: list figure gallery in acceptance handoff`
- files: local acceptance script, local acceptance script test, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 12:09 - Add global paper-level figure gallery to delivery bundle

Context:
- The active `/goal` requires the final MVP handoff to make every paper-level figure easy to find with its close-reading interpretation, software/R package versions, QC context, and final report.
- Standard and WGD report packages already had their own plot manifests, but the delivery bundle did not provide one global figure inventory.
- A user opening only the delivery bundle would still need to jump between standard and WGD report folders to locate all plots.

Decisions:
- Generate a global `figure_gallery.tsv` and `figure_gallery.md` in `results/delivery_bundle`.
- Include paper-level standard figures and formal WGD figures in one table.
- Link every gallery row to the plot PDF, figure interpretation Markdown, software version table, and final report.
- Register the gallery in `delivery_manifest.tsv` and `delivery_bundle.md` as a first-class handoff item.

Added:
- Global delivery figure gallery TSV output.
- Global delivery figure gallery Markdown output.
- Delivery manifest row `status/figure_gallery`.
- Test assertions for standard tree/domain, MCScanX/circlize, ggNetView PPI, WGD Ks distribution, and duplicate-type Ka/Ks gallery rows.

Modified:
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `figure_gallery.tsv` was not generated.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed after adding gallery generation and manifest registration.
- `python bin/genefam/run_delivery_bundle.py --outdir results/delivery_bundle` exited 0 and reported `figure_gallery` plus `figure_gallery_md` outputs.
- `rg -n "figure_gallery|tree_features|ks_distribution|software_versions.tsv" results/delivery_bundle/delivery_bundle.md results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/figure_gallery.tsv results/delivery_bundle/figure_gallery.md` confirmed the delivery manifest, Markdown bundle, TSV gallery, and Markdown gallery all expose the global plot index.
- `python -m pytest tests -q` passed with 431 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `bash scripts/run_local_acceptance.sh` exited 0, listed `figure_gallery` and `figure_gallery_md`, and printed `Final-stage blocker: Docker/Apptainer reproducibility.`
- `sed -n '1,16p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance keeps `Overall status: blocked` only for `final_stage_blocker`.
- `sed -n '1,10p' results/objective_audit/objective_audit.md` confirmed objective audit remains `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: d21ef1423dfabc27a60fa263393389fc0d35dfd0
- message: `feat: add delivery figure gallery`
- files: delivery bundle builder, delivery bundle test, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 11:59 - Expose paper-level WGD handoff in delivery bundle

Context:
- The active `/goal` requires the final handoff to expose Ka/Ks/WGD and gamma beta alpha theta interpretation outputs as clearly as the standard visualization outputs.
- The formal Nextflow WGD branch already writes `results/nextflow_wgd_smoke/wgd/report/final_report.md`, plot manifest, figure interpretations, and software versions.
- The delivery bundle still pointed mainly to the quickstart prepared-WGD report and did not give direct first-class pointers to the formal Nextflow WGD report package.

Decisions:
- Keep the quickstart prepared-WGD report as the short reproducible WGD handoff.
- Add separate `wgd` rows for the formal Nextflow WGD report, plot manifest, figure interpretations, and software/R package versions.
- Describe the WGD handoff as covering Ka/Ks, Ks-derived WGD layers, gamma beta alpha theta event interpretation, retention enrichment, duplicate-type selection, and pangenome-class selection.

Added:
- Delivery manifest row `wgd/wgd_paper_level_visual_report`.
- Delivery manifest row `wgd/wgd_paper_level_plot_manifest`.
- Delivery manifest row `wgd/wgd_paper_level_figure_interpretations`.
- Delivery manifest row `wgd/wgd_paper_level_software_versions`.
- Test assertions that the delivery bundle Markdown and TSV expose the formal Nextflow WGD report package.

Modified:
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `wgd_paper_level_visual_report` was absent from the delivery manifest.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed after adding the formal WGD handoff rows.
- `python bin/genefam/run_delivery_bundle.py --outdir results/delivery_bundle` exited 0, and `rg -n "wgd_paper_level_visual_report|wgd_paper_level_plot_manifest|wgd_paper_level_figure_interpretations|wgd_paper_level_software_versions|nextflow_wgd_smoke" results/delivery_bundle/delivery_bundle.md results/delivery_bundle/delivery_manifest.tsv` confirmed the new handoff rows.
- `python -m pytest tests -q` passed with 431 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed `Final-stage blocker: Docker/Apptainer reproducibility.`
- `sed -n '1,16p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance keeps `Overall status: blocked` only for `final_stage_blocker`.
- `sed -n '1,10p' results/objective_audit/objective_audit.md` confirmed objective audit remains `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: df2e17620956d461e38b8084426e6223ec8e8774
- message: `feat: expose paper-level WGD handoff`
- files: delivery bundle builder, delivery bundle test, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 11:50 - Expose paper-level standard visualization handoff in delivery bundle

Context:
- The active `/goal` requires the final handoff to make paper-level visualization results easy to find, including tree/motif/gene-structure/domain, MCScanX/circlize, promoter cis-elements, expression heatmap, copy number, feature summary, and ggNetView PPI.
- `results/nextflow_standard_feature_smoke/standard/report/report_index.tsv` already exposed the full visualization report, plot manifest, figure interpretations, and software versions.
- `results/delivery_bundle/delivery_bundle.md` still emphasized quickstart standard output and report audits, so a user could miss the full paper-level standard visualization package.

Decisions:
- Keep the quickstart standard report in the delivery bundle as the shortest reproducible handoff.
- Add separate `standard` rows for the full paper-level visualization report, plot manifest, figure interpretations, and software/R package versions.
- Treat these rows as user-facing delivery pointers, not as a new workflow branch.

Added:
- Delivery manifest row `standard/paper_level_visual_report`.
- Delivery manifest row `standard/paper_level_plot_manifest`.
- Delivery manifest row `standard/paper_level_figure_interpretations`.
- Delivery manifest row `standard/paper_level_software_versions`.
- Test assertions that the delivery bundle Markdown and TSV expose the full standard visualization package.

Modified:
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `paper_level_visual_report` was absent from the delivery manifest.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed after adding the full visualization handoff rows.
- `python -m pytest tests -q` passed with 431 tests.
- `python bin/genefam/run_delivery_bundle.py --outdir results/delivery_bundle` exited 0, and `rg -n "paper_level_visual_report|paper_level_plot_manifest|paper_level_figure_interpretations|paper_level_software_versions|nextflow_standard_feature_smoke" results/delivery_bundle/delivery_bundle.md results/delivery_bundle/delivery_manifest.tsv` confirmed the new handoff rows.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed `Final-stage blocker: Docker/Apptainer reproducibility.`
- `sed -n '1,16p' results/local_acceptance/local_acceptance_summary.md` confirmed local acceptance keeps `Overall status: blocked` only for `final_stage_blocker`.
- `sed -n '1,10p' results/objective_audit/objective_audit.md` confirmed objective audit remains `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 788fe553a4ff78ca7892cc984cd088e4b3fc08f5
- message: `feat: expose paper-level visualization handoff`
- files: delivery bundle builder, delivery bundle test, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 11:34 - Document local blocker status in Chinese README

Context:
- The active `/goal` is mostly operated by a Chinese-speaking user and requires final handoff surfaces to avoid confusing release-ready analysis evidence with final container-stage completion.
- English quickstart and machine-readable summaries now explain `Overall status: blocked` and `final_stage_blocker`, but `README.zh-CN.md` still described local acceptance as only a pass/fail index.
- A user reading only the Chinese README could mistake the Docker/Apptainer final-stage blocker for an analysis-flow failure or miss the unblock path.

Decisions:
- Update the Chinese local acceptance section to describe pass/fail/blocked semantics.
- Explain that `Overall status: blocked` means analysis evidence is release-ready while Docker / Apptainer runtime verification remains.
- Point the user to the `final_stage_blocker` row and `results/readiness/runtime_bootstrap.sh`.

Added:
- Chinese README explanation for `Overall status: blocked`.
- Chinese README reference to `final_stage_blocker` and the Docker / Apptainer final-stage unblock script.

Modified:
- `README.zh-CN.md`
- `tests/test_runtime_environment_files.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_chinese_readme_points_to_publication_audit_acceptance -q` first failed because `README.zh-CN.md` did not mention `final_stage_blocker`.
- `python -m pytest tests/test_runtime_environment_files.py::test_chinese_readme_points_to_publication_audit_acceptance tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report tests/test_quickstart_docs.py -q` passed with 4 tests after the Chinese README update.
- `python -m pytest tests -q` passed with 431 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed `Final-stage blocker: Docker/Apptainer reproducibility.`
- `sed -n '1,8p' results/release_checks/release_checks.md && sed -n '1,8p' results/objective_audit/objective_audit.md` confirmed objective audit remains `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `rg -n "Overall status: blocked|final_stage_blocker|Docker / Apptainer|Docker/Apptainer reproducibility|runtime_bootstrap" README.zh-CN.md results/local_acceptance/local_acceptance_summary.md results/delivery_bundle/delivery_bundle.md` confirmed the Chinese README and generated handoff artifacts describe the same final-stage blocker.

Commit:
- hash: 2f727abb61ca1447bffe774080da4ecfac3c0901
- message: `docs: explain local blocker status in Chinese README`
- files: Chinese README, runtime environment doc test, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 11:23 - Propagate local acceptance blocker into delivery bundle

Context:
- The active `/goal` requires final handoff surfaces to agree on whether the analysis package is release-ready or still blocked by the final Docker/Apptainer packaging stage.
- `results/local_acceptance/local_acceptance_summary.md` now reports `Overall status: blocked`, but `results/delivery_bundle/delivery_manifest.tsv` still marked `local_acceptance_summary` as `available`.
- The delivery bundle is the final user-facing index, so it should preserve the blocked local-acceptance state instead of flattening it to availability.

Decisions:
- Derive the delivery-bundle `local_acceptance_summary` status from objective-audit blockers.
- Keep the row path pointed at `results/local_acceptance/local_acceptance_summary.md`.
- Expand the row note to include `overall=blocked` and the `final_stage_blocker` value when blockers remain.

Added:
- Delivery-bundle note text carrying `overall=blocked; final_stage_blocker=...` for local acceptance summaries.

Modified:
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `local_acceptance_summary` was still emitted as `available`.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed after propagating objective blocker state into the local acceptance row.
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_runtime_environment_files.py tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` passed with 18 tests.
- `python -m pytest tests -q` passed with 431 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed `Final-stage blocker: Docker/Apptainer reproducibility.`
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` exited 0.
- `rg -n "local_acceptance_summary|final_stage_blocker|overall=blocked" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md results/local_acceptance/local_acceptance_summary.md` confirmed delivery bundle and local acceptance agree on the Docker/Apptainer final-stage blocker.
- `sed -n '1,8p' results/release_checks/release_checks.md && sed -n '1,8p' results/objective_audit/objective_audit.md` confirmed objective audit remains `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 06fc329c1ac2fdfc7f86b159af1d3b75381403b5
- message: `fix: propagate local acceptance blocker to delivery bundle`
- files: delivery bundle builder, delivery bundle test, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 11:13 - Surface final-stage blocker in local acceptance

Context:
- The active `/goal` keeps Docker/Apptainer packaging as the final-stage blocker while analysis-flow evidence is release-ready.
- `results/local_acceptance/local_acceptance_summary.md` showed all acceptance steps as passed, which could make the full objective look complete even though objective audit still reports Docker/Apptainer reproducibility as blocked.
- The first local acceptance surface should distinguish analysis-flow readiness from final container-stage completion.

Decisions:
- Add a `final_stage_blocker` row to local acceptance TSV/Markdown outputs.
- Compute `Overall status: blocked` when all executable acceptance steps pass but objective audit still contains blocked or missing requirements.
- Extract final-stage blockers from `results/objective_audit/objective_audit.tsv` inside `scripts/run_local_acceptance.sh` after the release gate refreshes objective evidence.
- Document in quickstart that `Overall status: blocked` means analysis evidence is ready but container runtime packaging remains.

Added:
- `final_stage_blocker` local acceptance row pointing to `results/objective_audit/objective_audit.md`.
- CLI options `--final-stage-blocker-status` and `--final-stage-blocker-note` for `write_local_acceptance_summary.py`.
- Wrapper extraction of blocked/missing objective requirements for local acceptance summaries.

Modified:
- `bin/genefam/write_local_acceptance_summary.py`
- `scripts/run_local_acceptance.sh`
- `docs/quickstart.md`
- `tests/test_write_local_acceptance_summary.py`
- `tests/test_local_acceptance_script.py`
- `tests/test_quickstart_docs.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_write_local_acceptance_summary.py -q` first failed because `write_acceptance_summary()` did not accept `final_stage_blocker_status`.
- `python -m pytest tests/test_local_acceptance_script.py -q` first failed because the wrapper did not define `final_stage_blocker_status`.
- `python -m pytest tests/test_quickstart_docs.py -q` first failed because quickstart did not mention `final_stage_blocker` or `Overall status: blocked`.
- `python -m pytest tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py tests/test_quickstart_docs.py -q` passed with 7 tests after implementation and documentation updates.
- `python -m pytest tests -q` passed with 431 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed `Final-stage blocker: Docker/Apptainer reproducibility.`
- `sed -n '1,25p' results/local_acceptance/local_acceptance_summary.md` confirmed `Overall status: blocked` and a `final_stage_blocker` row pointing to `results/objective_audit/objective_audit.md`.
- `sed -n '1,8p' results/release_checks/release_checks.md && sed -n '1,8p' results/objective_audit/objective_audit.md` confirmed release readiness remains `Passed: 47`, `Required failed: 0`, `Release ready: true`, with objective audit `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "Overall status: blocked|final_stage_blocker|Docker/Apptainer reproducibility" results/local_acceptance/local_acceptance_summary.md results/local_acceptance/local_acceptance_summary.tsv results/handoff/handoff_report.md` confirmed local acceptance and handoff agree on the final-stage blocker.

Commit:
- hash: a29eec86b69ae40bf20c92d88b58e6cceff5553f
- message: `feat: surface final stage blocker in local acceptance`
- files: local acceptance summary, local acceptance wrapper, quickstart docs, tests, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 11:04 - Sync report-index audits into handoff evidence

Context:
- The active `/goal` requires the final handoff surfaces to reflect the same paper-level report closure evidence.
- Delivery bundle and local acceptance already surfaced standard and WGD report-index audits, but `results/handoff/handoff_report.md` did not list those audit files.
- While refreshing handoff evidence, the release-gate-generated objective audit still marked `final reports` as missing because `run_release_checks.write_objective_audit()` did not pass the standard/WGD publication audit detail TSV files into `build_objective_audit()`.

Decisions:
- Add standard and WGD report-index audit status summaries to the handoff sections, Markdown, and summary TSV.
- Add both report-index audit Markdown files to handoff Key Evidence.
- Make `write_objective_audit()` read standard and WGD publication audit detail TSV files by default so release-gate-generated objective and handoff reports match the standalone objective audit CLI.
- Keep `container_default_smoke` and report-index audit summary keys in an explicit TSV order.

Added:
- `standard_report_index_audit` and `wgd_report_index_audit` handoff summary keys.
- Handoff Key Evidence links for `results/report_index_audit/standard_report_index_audit.md` and `results/report_index_audit/wgd_report_index_audit.md`.
- A regression test proving `write_objective_audit()` reads publication audit detail TSV files before deciding final-report objective status.

Modified:
- `bin/genefam/build_handoff_report.py`
- `bin/genefam/run_release_checks.py`
- `tests/test_build_handoff_report.py`
- `tests/test_run_release_checks.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because handoff sections did not expose `standard_report_index_audit` and Markdown did not include `Standard report index audit`.
- `python -m pytest tests/test_run_release_checks.py::test_write_objective_audit_reads_publication_detail_audits -q` first failed because `write_objective_audit()` did not accept publication audit detail TSV paths.
- `python -m pytest tests/test_run_release_checks.py::test_write_objective_audit_reads_publication_detail_audits tests/test_build_handoff_report.py -q` passed with 6 tests after implementation.
- `python -m pytest tests -q` passed with 430 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `sed -n '1,32p' results/objective_audit/objective_audit.md` confirmed `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `final reports` achieved.
- `sed -n '1,35p' results/handoff/handoff_report.md` confirmed `Objective audit: achieved=19 blocked=1 missing=0 complete=false` plus standard and WGD report-index audit status lines.
- `rg -n "final reports|standard_report_index_audit|wgd_report_index_audit|achieved=19|missing=0" results/objective_audit/objective_audit.md results/handoff/handoff_report.md results/handoff/handoff_summary.tsv` confirmed objective and handoff evidence are synchronized.

Commit:
- hash: bc69057dc4aae9418996e80794a9610f7e67751b
- message: `fix: sync handoff report audit evidence`
- files: handoff report builder, release objective writer, tests, and history entry.

Next:
- Continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 10:49 - Add report-index audits to local acceptance

Context:
- The active `/goal` requires final users to inspect a compact acceptance surface before opening the full report bundle.
- `results/delivery_bundle` now indexes standard and WGD report-index audits, but `results/local_acceptance/local_acceptance_summary.md` still summarized only release, publication audit, quickstart, and delivery bundle status.
- The local acceptance wrapper should expose the report navigation closure gate in the same first-pass status table as publication-report closure.

Decisions:
- Add standard and WGD report-index audit statuses to the local acceptance summary API and CLI.
- Keep the statuses sourced from `results/release_checks/release_checks.tsv`, matching publication-report audit handling.
- Add `REPORT_INDEX_OUTDIR` to `scripts/run_local_acceptance.sh` so paths remain configurable and separate from publication report audit outputs.

Added:
- `standard_report_index_audit` and `wgd_report_index_audit` rows in local acceptance TSV/Markdown summaries.
- `--standard-report-index-status`, `--wgd-report-index-status`, and `--report-index-outdir` CLI options for `write_local_acceptance_summary.py`.
- Local acceptance wrapper extraction of `standard report index audit` and `WGD report index audit` exit codes.

Modified:
- `bin/genefam/write_local_acceptance_summary.py`
- `scripts/run_local_acceptance.sh`
- `docs/quickstart.md`
- `tests/test_write_local_acceptance_summary.py`
- `tests/test_local_acceptance_script.py`
- `tests/test_quickstart_docs.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_write_local_acceptance_summary.py -q` first failed because the summary API did not accept `standard_report_index_status` or `wgd_report_index_status`.
- `python -m pytest tests/test_local_acceptance_script.py -q` first failed because the wrapper did not define `REPORT_INDEX_OUTDIR`.
- `python -m pytest tests/test_quickstart_docs.py -q` first failed because quickstart did not mention `report-index audit exit status`.
- `python -m pytest tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py tests/test_quickstart_docs.py -q` passed with 6 tests after implementation and documentation updates.
- `python -m pytest tests -q` passed with 429 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `python bin/genefam/write_local_acceptance_summary.py --release-status 0 --publication-status 0 --standard-report-index-status 0 --wgd-publication-status 0 --wgd-report-index-status 0 --quickstart-status 0 --delivery-status 0 --release-outdir results/release_checks --publication-outdir results/publication_report_audit --report-index-outdir results/report_index_audit --quickstart-outdir results/quickstart --delivery-outdir results/delivery_bundle --outdir results/local_acceptance` exited 0.
- `rg -n "report_index|report-index" results/local_acceptance/local_acceptance_summary.md results/local_acceptance/local_acceptance_summary.tsv` confirmed both standard and WGD report-index audit rows are present in refreshed local acceptance outputs.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed `results/report_index_audit/standard_report_index_audit.md` and `results/report_index_audit/wgd_report_index_audit.md` in the primary handoff file list.

Commit:
- hash: 8b2e906b21a8f0d083369599c433582fe58f9e90
- message: `feat: add report index audits to local acceptance`
- files: local acceptance summary, local acceptance wrapper, quickstart docs, tests, and history entry.

Next:
- Run full tests and release checks, then continue final MVP hardening while Docker/Apptainer remain the final-stage runtime blocker.

## 2026-06-27 10:45 - Index report-index audits in delivery bundle

Context:
- The active `/goal` treats `results/delivery_bundle/delivery_bundle.md` as the final user-facing index for the MVP result package.
- Standard and WGD report-index audits were already enforced by release checks and objective audit, but the delivery bundle still surfaced only publication-report audits.
- Users opening the final delivery bundle could miss the report navigation closure evidence for `figure_interpretations.md`, software versions, plot manifests, and final reports.

Decisions:
- Add standard and WGD report-index audit rows to the delivery manifest status section.
- Keep report-index audit status driven by release-check rows, matching the existing publication-audit pattern.
- Document report-index closure in the readiness checklist alongside publication-report closure.

Added:
- Delivery manifest entries for `standard_report_index_audit` and `wgd_report_index_audit`.
- Readiness checklist references to `results/report_index_audit/standard_report_index_audit.md` and `results/report_index_audit/wgd_report_index_audit.md`.

Modified:
- `bin/genefam/run_delivery_bundle.py`
- `docs/readiness_checklist.md`
- `tests/test_run_delivery_bundle.py`
- `tests/test_runtime_environment_files.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `standard_report_index_audit` was missing from the delivery manifest.
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit -q` first failed because the readiness checklist did not mention `results/report_index_audit/standard_report_index_audit.md`.
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit -q` passed with 2 tests after implementation and documentation updates.
- `python -m pytest tests -q` passed with 429 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `rg -n "report index audit|report_index_audit|standard_report_index_audit|wgd_report_index_audit" results/release_checks/release_checks.md results/delivery_bundle/delivery_bundle.md results/delivery_bundle/delivery_manifest.tsv` confirmed standard and WGD report-index audits are indexed by the release gate and delivery bundle.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: b3ace46664fec770e585091c66b56ee00a244109
- message: `feat: index report audits in delivery bundle`
- files: delivery bundle builder, readiness checklist, delivery bundle test, runtime docs test, and history entry.

Next:
- Refresh full release evidence and continue final MVP hardening while keeping Docker/Apptainer runtime verification as the final-stage external blocker.

## 2026-06-27 10:38 - Document report-index audit gates

Context:
- The active `/goal` requires report indexes, final reports, smoke checks, release checks, and final objective audit to describe the same paper-level delivery contract.
- The code now enforces standard and WGD report-index audits, but README, quickstart, and release-audit documentation still emphasized only publication report audits.
- Users reading the docs could miss the new `report_index_audit` outputs and the distinction between content closure and index/navigation closure.

Decisions:
- Document publication-report audit as the content and figure close-reading gate.
- Document report-index audit as the navigation and report-package artifact gate.
- Surface both standard and WGD report-index audit outputs in README, quickstart, and release-audit evidence tables.

Added:
- README references to `results/report_index_audit/standard_report_index_audit.md` and `results/report_index_audit/wgd_report_index_audit.md`.
- Quickstart entries for `standard_report_index_audit` and `wgd_report_index_audit`.
- Release-audit evidence and commands for `bin/genefam/audit_report_index.py`.

Modified:
- `README.md`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report -q` first failed because the docs did not mention `results/report_index_audit/standard_report_index_audit.md`, `audit_report_index.py`, or report-index closure.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report -q` passed with 4 tests after documentation updates.
- `python -m pytest tests -q` passed with 429 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `rg -n "report index audit" results/release_checks/release_checks.md` confirmed both standard and WGD report-index audits are required release checks.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `rg -n "final reports|Report index audits" results/objective_audit/objective_audit.md` confirmed the high-level final-report objective still requires both report-index audits.

Commit:
- hash: 866af5315921f7d4a95c52e3a945231b9ca8fec5
- message: `docs: document report index audits`
- files: README, quickstart, release audit docs, doc tests, and history entry.

Next:
- Continue final MVP hardening while keeping Docker/Apptainer verification as the final-stage external blocker.

## 2026-06-27 10:30 - Audit report-index delivery artifacts

Context:
- The active `/goal` requires paper-level figures and reports to be connected through report indexes, final reports, smoke checks, release checks, and final objective audit.
- Standard and WGD report indexes now list report-layer deliverables, but release checks still only validated them indirectly through tests and Nextflow smoke outputs.
- A future regression could drop `final_report` or `figure_interpretations_md` from a report index while publication audits and high-level objective audit still looked complete.

Decisions:
- Add a dedicated `audit_report_index.py` gate with TSV/Markdown outputs.
- Require standard and WGD report indexes to expose `plot_manifest`, `software_versions`, `figure_interpretations`, `figure_interpretations_md`, and `final_report`.
- Make release checks run both standard and WGD report-index audits as required checks.
- Make the high-level `final reports` objective depend on both report-index audits.

Added:
- `bin/genefam/audit_report_index.py`
- `tests/test_audit_report_index.py`
- Release checks for `standard report index audit` and `WGD report index audit`.
- Objective-audit regression test for missing standard report-index audit evidence.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `tests/test_audit_objective_completion.py`
- `tests/test_run_release_checks.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_report_index.py -q` first failed with `ModuleNotFoundError: No module named 'bin.genefam.audit_report_index'`.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_report_index_audits_after_report_generation -q` first failed because `standard report index audit` was not in `default_checks()`.
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_require_standard_report_index_audit -q` first failed because `final reports` was still `achieved` without standard report-index audit evidence.
- `python -m pytest tests/test_audit_report_index.py tests/test_run_release_checks.py::test_default_checks_include_report_index_audits_after_report_generation -q` passed with 4 tests.
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_require_standard_report_index_audit tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure tests/test_audit_objective_completion.py::test_build_objective_audit_marks_goal_items_and_runtime_blockers -q` passed.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 43 tests.
- `python -m pytest tests/test_run_release_checks.py -q` passed with 52 tests.
- `python -m pytest tests -q` passed with 429 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 47`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `sed -n '1,80p' results/report_index_audit/standard_report_index_audit.md` and the same command for `wgd_report_index_audit.md` showed `Passed: 2`, `Failed: 0`, and `Complete: true` for both report-index audits.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `rg -n "final reports|Report index audits|standard report index audit|WGD report index audit" results/objective_audit/objective_audit.md` confirmed the high-level final-report objective now requires both report-index audits.

Commit:
- hash: 65d3b07c4ab08f4c5fd314503e74c8e789b724c4
- message: `test: audit report index artifacts`
- files: report-index audit tool, release/objective audit integration, tests, and history entry.

Next:
- Continue final MVP hardening while keeping Docker/Apptainer verification as the final-stage external blocker.

## 2026-06-27 10:22 - Add final report artifacts to report indexes

Context:
- The active `/goal` requires all paper-level figures and reports to be connected through the report index and final report.
- Standard report indexes listed plot and interpretation TSV evidence, but did not list `figure_interpretations.md` or `final_report.md`.
- WGD report indexes listed WGD tables and plots, but did not list report-layer files such as `plot_manifest.tsv`, `software_versions.tsv`, `figure_interpretations.tsv`, `figure_interpretations.md`, or `final_report.md`.

Decisions:
- Treat report-layer files as first-class indexed deliverables for both standard and WGD branches.
- Let standard report indexes publish future report paths through the existing `--published-outdir` mechanism, because the index is assembled before `final_report.md` is generated.
- Keep WGD report index paths derived from the published output directory.

Added:
- Standard report-index entries for `figure_interpretations_md` and `final_report`.
- WGD report-index entries for `plot_manifest`, `software_versions`, `figure_interpretations`, `figure_interpretations_md`, and `final_report`.
- Regression tests for standard and WGD report indexes covering both Python APIs and CLIs.

Modified:
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/build_wgd_report_index.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_wgd_report_index.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_wgd_report_index.py -q` first failed because the standard builder lacked `figure_interpretations_md` and `final_report`, the standard CLI rejected `--figure-interpretations-md` and `--final-report`, and the WGD builder lacked report-layer index rows.
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_wgd_report_index.py -q` passed with 6 tests after implementation.
- `python -m pytest tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes -q` passed.
- `python -m pytest tests/test_run_nextflow_standard_smoke.py tests/test_run_nextflow_wgd_smoke.py tests/test_run_standard_smoke.py tests/test_run_wgd_smoke.py -q` passed with 28 tests.
- `python -m pytest tests/test_assemble_report.py -q` passed with 3 tests.
- `python -m pytest tests -q` passed with 424 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `rg -n "figure_interpretations_md|final_report|plot_manifest|software_versions|figure_interpretations" results/nextflow_standard_feature_smoke/standard/report/report_index.tsv results/nextflow_wgd_smoke/wgd/report/report_index.tsv` confirmed both standard and WGD report indexes include the report-layer deliverables.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 26d70d121771f319cf72f3f3eaa4517cb7db0e57
- message: `test: index final report artifacts`
- files: standard/WGD report-index builders, report-index tests, and history entry.

Next:
- Continue final MVP hardening while keeping Docker/Apptainer verification as the final-stage external blocker.

## 2026-06-27 10:15 - Require publication audit detail in objective audit

Context:
- The active `/goal` requires final reports to include per-figure close reading, software/R package versions, QC, reproducibility, and no draft placeholders.
- `audit_publication_report.py` now checks those details, but `audit_objective_completion.py` only looked at the release-check names `publication report audit` and `WGD publication report audit`.
- A future weakened publication audit could therefore leave the high-level objective audit too indirect.

Decisions:
- Make objective audit read standard and WGD publication audit detail rows.
- Require both report families to pass the full publication-audit checklist, including `final_report_placeholder_text`.
- Keep CLI defaults pointing at `results/publication_report_audit/publication_report_audit.tsv` and `results/publication_report_audit/wgd_publication_report_audit.tsv`.

Added:
- Regression test proving final reports are `missing` when the standard publication audit lacks `final_report_placeholder_text`.
- Objective-audit note text that explicitly records no `TODO`/`TBD`/`placeholder` text for standard and WGD reports.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_require_placeholder_text_checks_in_publication_audits -q` first failed with `TypeError: build_objective_audit() got an unexpected keyword argument 'publication_audit_rows'`.
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_require_placeholder_text_checks_in_publication_audits tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure tests/test_audit_objective_completion.py::test_build_objective_audit_marks_goal_items_and_runtime_blockers -q` passed.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 42 tests.
- `python -m pytest tests -q` passed with 424 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `awk -F '\t' 'NR>1 {count[$2]++} END {for (k in count) print k, count[k]}' results/publication_report_audit/publication_report_audit.tsv` and the same command for `wgd_publication_report_audit.tsv` each reported `passed 10`.
- `rg -n "final_report_placeholder_text" results/publication_report_audit/publication_report_audit.tsv results/publication_report_audit/wgd_publication_report_audit.tsv` confirmed both standard and WGD publication audits include the placeholder-text check.
- `rg -n "final reports|no TODO|Publication audit detail" results/objective_audit/objective_audit.md` confirmed the high-level final-report objective now records the no-placeholder-text detail.

Commit:
- hash: 77264834e04f52e27fbe62e5220760b04d089171
- message: `test: require publication audit details for final reports`
- files: objective audit detail gating, objective audit tests, and history entry.

Next:
- Continue final MVP hardening while keeping Docker/Apptainer verification as the final-stage external blocker.

## 2026-06-27 10:04 - Reject placeholder text in final reports

Context:
- The active `/goal` requires the final report to provide publication-style, figure-by-figure close reading.
- The previous audit rejected placeholder words inside `figure_interpretations.tsv`, but final report Markdown text itself could still contain draft markers such as `TODO`, `TBD`, or `placeholder`.

Decisions:
- Add a dedicated `final_report_placeholder_text` publication-report audit row.
- Treat `TODO`, `TBD`, and `placeholder` as invalid anywhere in `final_report.md`.
- Keep figure interpretation detail validation separate so TSV-level and Markdown-level failures are easy to diagnose.

Added:
- Regression test proving a clean interpretation table still fails the publication report audit when the final report Markdown contains `TODO`.
- Final report placeholder-text audit check.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_flags_placeholder_text_in_final_report -q` first failed with `KeyError: 'final_report_placeholder_text'`.
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_flags_placeholder_text_in_final_report tests/test_audit_publication_report.py::test_publication_report_audit_flags_placeholder_interpretation_text tests/test_audit_publication_report.py::test_publication_report_audit_requires_reading_status_embedded_in_final_report -q` passed.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 15 tests.
- `python -m pytest tests -q` passed with 423 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: c29b95b2d98969c39ebc98da7a6f6bd8a00b723d
- message: `test: reject placeholder final reports`
- files: publication report audit final-report placeholder check, regression tests, and history entry.

Next:
- Continue final MVP hardening while keeping Docker/Apptainer verification as the final-stage external blocker.

## 2026-06-27 10:01 - Reject placeholder text in figure close readings

Context:
- The active `/goal` requires the final report to include close reading for every figure.
- `audit_publication_report.py` checked that interpretation fields were non-empty and figure-specific, but did not reject placeholder text such as `TODO`, `TBD`, or `placeholder`.
- Placeholder text could therefore pass the publication-style report closure gate even though it was not a real figure interpretation.

Decisions:
- Treat `TODO`, `TBD`, and `placeholder` as invalid placeholder tokens in required figure interpretation fields.
- Report placeholder failures as `figure_key:field:placeholder_text` under `figure_interpretation_detail`.
- Keep the existing missing-field and `result_reading_status` checks unchanged.

Added:
- Regression test that a `TODO` key-observation field fails the publication report audit.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_flags_placeholder_interpretation_text -q` first failed because `figure_interpretation_detail` still passed with `TODO` text.
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_flags_placeholder_interpretation_text tests/test_audit_publication_report.py::test_publication_report_audit_flags_template_guided_reading_status tests/test_audit_publication_report.py::test_publication_report_audit_requires_reading_status_embedded_in_final_report -q` passed.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 14 tests.
- `python -m pytest tests -q` passed with 422 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 55c213427e9fd6b3483604abdb9d38e76009581d
- message: `test: reject placeholder figure readings`
- files: publication report audit detail checks, regression tests, and history entry.

Next:
- Continue hardening report closure and handoff evidence before final Docker/Apptainer packaging.

## 2026-06-27 09:54 - Report non-mapping WGD event config files clearly

Context:
- The active `/goal` requires gamma/beta/alpha/theta WGD event interpretation to be robust for real YAML edits.
- If a WGD event-map file itself was a YAML list or scalar instead of a mapping containing `wgd_events`, `load_event_metadata()` raised `AttributeError` while calling `.get()`.
- The correct problem is the event-map file structure: the configuration root must be a mapping.

Decisions:
- Validate that the parsed WGD event-map YAML root is a mapping before reading `wgd_events`.
- Preserve the existing top-level `wgd_events` list check and per-entry checks.
- Confirm `validate_config --check-paths` wraps the lower-level type error into `wgd_events.event_map is invalid: ...`.

Added:
- Regression test for non-mapping WGD event-map files in `load_event_metadata()`.
- Regression test that config validation reports non-mapping WGD event-map files through `wgd_events.event_map`.

Modified:
- `bin/genefam/build_wgd_event_evidence.py`
- `tests/test_build_wgd_event_evidence.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_mapping_config -q` first failed with `AttributeError: 'list' object has no attribute 'get'`.
- `python -m pytest tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_mapping_config tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_list_wgd_events tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_mapping_event_entries tests/test_build_wgd_event_evidence.py::test_load_event_metadata_reads_brassicaceae_named_events -q` passed.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_non_mapping_wgd_event_config tests/test_validate_config.py::test_validate_config_check_paths_reports_non_list_wgd_events tests/test_build_wgd_event_evidence.py -q` passed with 12 tests.
- `python -m pytest tests/test_validate_config.py -q` passed with 43 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 421 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 2d7e4e770d46b6683ab5eba7981473bda5d9df5c
- message: `test: report malformed WGD event config`
- files: WGD event-map root validation, config validation coverage, and history entry.

Next:
- Continue hardening WGD/report validation and handoff evidence before final Docker/Apptainer packaging.

## 2026-06-27 09:48 - Report non-list WGD event maps clearly

Context:
- The active `/goal` requires gamma/beta/alpha/theta WGD event interpretation to be robust for real YAML edits.
- If a user wrote `wgd_events` as a mapping instead of a list, `load_event_metadata()` iterated over mapping keys and reported a misleading per-entry error.
- The correct problem is the top-level event-map structure: `wgd_events` must be a list of event mappings.

Decisions:
- Validate that top-level `wgd_events` is a list before validating individual event entries.
- Preserve the existing per-entry mapping, missing-name, duplicate-name, and missing-field checks.
- Confirm `validate_config --check-paths` wraps the lower-level type error into `wgd_events.event_map is invalid: ...`.

Added:
- Regression test for non-list `wgd_events` in `load_event_metadata()`.
- Regression test that config validation reports non-list `wgd_events` through `wgd_events.event_map`.

Modified:
- `bin/genefam/build_wgd_event_evidence.py`
- `tests/test_build_wgd_event_evidence.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_list_wgd_events -q` first failed because the error was `WGD event entry 1 must be a mapping` instead of the top-level list error.
- `python -m pytest tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_list_wgd_events tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_mapping_event_entries tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_events_missing_name tests/test_build_wgd_event_evidence.py::test_load_event_metadata_reads_brassicaceae_named_events -q` passed.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_non_list_wgd_events tests/test_validate_config.py::test_validate_config_check_paths_reports_non_mapping_wgd_event_entry tests/test_build_wgd_event_evidence.py -q` passed with 11 tests.
- `python -m pytest tests/test_validate_config.py -q` passed with 42 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 419 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 67e7e79bc24cdc05d9c05b91820f22543462194c
- message: `test: report non-list WGD event maps`
- files: WGD event-map top-level validation, config validation coverage, and history entry.

Next:
- Continue hardening WGD/report validation and handoff evidence before final Docker/Apptainer packaging.

## 2026-06-27 09:42 - Report non-mapping WGD event entries clearly

Context:
- The active `/goal` requires gamma/beta/alpha/theta WGD event interpretation to be robust for real YAML edits.
- If a user wrote `wgd_events: [alpha]` or `- alpha` instead of a mapping entry, `load_event_metadata()` raised `AttributeError: 'str' object has no attribute 'get'`.
- That error was not clear enough for a user fixing WGD event-map configuration.

Decisions:
- Require every `wgd_events` list item to be a YAML mapping.
- Report the 1-based event entry index when the structure is wrong.
- Confirm `validate_config --check-paths` wraps the lower-level structure error into `wgd_events.event_map is invalid: ...`.

Added:
- Regression test for non-mapping WGD event entries in `load_event_metadata()`.
- Regression test that config validation reports non-mapping WGD event entries through `wgd_events.event_map`.

Modified:
- `bin/genefam/build_wgd_event_evidence.py`
- `tests/test_build_wgd_event_evidence.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_mapping_event_entries -q` first failed with `AttributeError: 'str' object has no attribute 'get'`.
- `python -m pytest tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_non_mapping_event_entries tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_events_missing_name tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_duplicate_named_events tests/test_build_wgd_event_evidence.py::test_load_event_metadata_reads_brassicaceae_named_events -q` passed.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_non_mapping_wgd_event_entry tests/test_validate_config.py::test_validate_config_check_paths_reports_wgd_event_missing_name tests/test_build_wgd_event_evidence.py -q` passed with 10 tests.
- `python -m pytest tests/test_validate_config.py -q` passed with 41 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 417 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 7d9c1fcdda5e0c5c4b2d9450390c3ab969f9b724
- message: `test: report malformed WGD event entries`
- files: WGD event-map structure validation, config validation coverage, and history entry.

Next:
- Continue hardening WGD/report validation and handoff evidence before final Docker/Apptainer packaging.

## 2026-06-27 09:36 - Report missing WGD event names clearly

Context:
- The active `/goal` requires gamma/beta/alpha/theta WGD event interpretation to be robust and user-readable.
- `load_event_metadata()` treated `name` as a required event-map field, but accessed it before validation.
- A WGD event entry without `name` raised a raw `KeyError` instead of a clear YAML preflight message.

Decisions:
- Validate WGD event `name` before duplicate-name and metadata checks.
- Include the 1-based event entry index in the missing-name error.
- Confirm `validate_config --check-paths` wraps the lower-level event-map error into `wgd_events.event_map is invalid: ...`.

Added:
- Regression test for missing WGD event `name` in `load_event_metadata()`.
- Regression test that config validation reports the same missing-name problem through `wgd_events.event_map`.

Modified:
- `bin/genefam/build_wgd_event_evidence.py`
- `tests/test_build_wgd_event_evidence.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_events_missing_name -q` first failed with `KeyError: 'name'`.
- `python -m pytest tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_events_missing_name tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_duplicate_named_events tests/test_build_wgd_event_evidence.py::test_load_event_metadata_rejects_named_events_missing_required_fields tests/test_build_wgd_event_evidence.py::test_load_event_metadata_reads_brassicaceae_named_events -q` passed.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_wgd_event_missing_name tests/test_validate_config.py::test_validate_config_check_paths_rejects_duplicate_wgd_event_names tests/test_build_wgd_event_evidence.py -q` passed with 9 tests.
- `python -m pytest tests/test_validate_config.py -q` passed with 40 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 415 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 8c258a2e5521d39c7320f66024fc25caa302738c
- message: `test: report missing WGD event names`
- files: WGD event-map validation, config validation coverage, and history entry.

Next:
- Continue hardening WGD/report validation and handoff evidence before final Docker/Apptainer packaging.

## 2026-06-27 09:30 - Require domain filtering before family summary

Context:
- The active `/goal` requires the standard branch to be reliable from identification through report generation.
- `FAMILY_SUMMARY` consumes `CONCAT_FAMILY_CANDIDATES.out`, and `family_candidates.tsv` is produced by the domain-filtering step.
- A YAML config could enable `modules.family_summary` while disabling `modules.domain_filtering`, which would make the standard branch dependency chain unclear before runtime.

Decisions:
- Require `modules.domain_filtering: true` whenever `modules.family_summary` is enabled.
- Update the shared valid config fixture so it reflects the real standard module chain: identification -> domain_filtering -> family_summary.

Added:
- Regression test that family summary reports a missing domain-filtering dependency.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_family_summary_requires_domain_filtering -q` first failed because family summary did not report the missing domain-filtering dependency.
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_family_summary_requires_domain_filtering tests/test_validate_config.py::test_validate_config_reports_domain_filtering_requires_identification tests/test_validate_config.py::test_validate_config_reports_family_summary_requires_pep_inputs -q` passed.
- `python -m pytest tests/test_validate_config.py -q` passed with 39 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 413 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 5f7f3abb612a4e7ad7f9851a20d286767cabbc11
- message: `test: require domain filtering for family summary`
- files: family-summary config validation, regression tests, and history entry.

Next:
- Continue tightening module dependency validation and user-facing handoff evidence before final Docker/Apptainer packaging.

## 2026-06-27 09:24 - Require identification before domain filtering

Context:
- The active `/goal` requires a reliable standard identification branch before final MVP handoff.
- The Nextflow standard branch builds HMMER/DIAMOND-style evidence first, then `DOMAIN_FILTER` merges that evidence into `family_candidates.tsv`.
- A YAML config could enable `modules.domain_filtering` while disabling `modules.identification`, allowing an impossible standard-branch module combination to pass early validation.

Decisions:
- Require `modules.identification: true` whenever `modules.domain_filtering` is enabled.
- Keep the rule in YAML preflight validation so invalid module combinations fail before workflow execution.

Added:
- Regression test that domain filtering reports a missing identification dependency.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_domain_filtering_requires_identification -q` first failed because domain filtering did not report the missing identification dependency.
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_domain_filtering_requires_identification tests/test_validate_config.py::test_validate_config_reports_identification_modules_require_pep_inputs -q` passed.
- `python -m pytest tests/test_validate_config.py -q` passed with 38 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 412 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: e3952419e1e0158102c9e986818cd08c15a0714d
- message: `test: require identification for domain filtering`
- files: domain-filtering config validation, regression tests, and history entry.

Next:
- Continue hardening module dependency validation and handoff evidence before the final container packaging stage.

## 2026-06-27 09:19 - Require family summary for expression integration

Context:
- The active `/goal` requires RNA-seq expression heatmap integration as a family-member-level analysis.
- The standard Nextflow branch subsets expression data with `SUBSET_EXPRESSION_MATRIX`, which consumes `family_candidates` and produces `tables/family_expression.tsv`.
- A YAML config could enable `modules.expression` while disabling `modules.family_summary`, making the expression module look standalone even though the reported heatmap is tied to the family member set.

Decisions:
- Require `modules.family_summary: true` whenever `modules.expression` is enabled.
- Keep the existing `expression.matrix` path requirement unchanged.

Added:
- Regression test that expression integration reports a missing family summary dependency.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_expression_requires_family_summary -q` first failed because expression integration did not report the missing family summary dependency.
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_expression_requires_family_summary tests/test_validate_config.py::test_validate_config_reports_expression_requires_matrix_path tests/test_validate_config.py::test_validate_config_checks_expression_metadata_path_when_provided -q` passed.
- `python -m pytest tests/test_validate_config.py -q` passed with 37 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 411 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: cfb3a1c2ff5d087ddd597c0afa3b30e387bbf6d2
- message: `test: require family summary for expression`
- files: expression config validation, regression tests, and history entry.

Next:
- Continue tightening formal YAML/module contracts and final handoff evidence before container packaging.

## 2026-06-27 09:13 - Require peptide inputs for family summary module

Context:
- The active `/goal` requires gene family information summary, copy-number statistics, pangenome-style summaries, and protein-property tables.
- The standard branch builds `sequences/family_members.faa` and `tables/gene_family_protein_properties.tsv` for family summary outputs.
- `modules.family_summary` could be enabled while `input.required.pep` was disabled, which would let an incomplete YAML pass early validation and fail later in summary/report generation.

Decisions:
- Treat `modules.family_summary` as a peptide-dependent module.
- Keep the rule narrowly scoped to YAML preflight validation without changing downstream workflow behavior.

Added:
- Regression test that `modules.family_summary: true` requires `input.required.pep: true`.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_family_summary_requires_pep_inputs -q` first failed because family summary did not report the missing peptide input requirement.
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_family_summary_requires_pep_inputs tests/test_validate_config.py::test_validate_config_reports_identification_modules_require_pep_inputs -q` passed.
- `python -m pytest tests/test_validate_config.py -q` passed with 36 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 410 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 with `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 0a2ca2181133275b83ba1f288bc817cc3cd727cd
- message: `test: require family summary peptide inputs`
- files: family summary config validation, regression tests, and history entry.

Next:
- Continue auditing enabled modules for missing YAML preflight dependencies before final MVP packaging.

## 2026-06-27 09:06 - Require genome and GFF3 inputs for promoter cis-element module

Context:
- The active `/goal` requires promoter cis-element analysis and visualization.
- `modules.promoter_cis` already required a cis-element annotation table, but did not require the genome FASTA and GFF3 evidence needed to extract promoter sequences.
- Without these input flags, a YAML config could enable promoter cis-element analysis while declaring the required species input files unavailable.

Decisions:
- Require `input.required.gff3: true` when `modules.promoter_cis` is enabled.
- Require `input.required.genome: true` when `modules.promoter_cis` is enabled.
- Keep the existing `promoter.cis_elements` path requirement.

Added:
- Regression test that promoter cis-element config validation fails when GFF3 and genome input requirements are not enabled.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_promoter_cis_requires_genome_and_gff3_inputs -q` first failed because the promoter cis-element module did not report missing GFF3/genome requirements.
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_promoter_cis_requires_genome_and_gff3_inputs -q` passed after adding the dependency checks.
- `python -m pytest tests/test_validate_config.py -q` passed with 35 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 409 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `rg -n "promoter cis-element visualization|promoter smoke|validate example config" results/objective_audit/objective_audit.md results/release_checks/release_checks.md` confirmed promoter smoke and promoter cis-element visualization evidence remain in the release/objective gates.

Commit:
- hash: 6fe969c3a2af10525d664e1894c7224632250b02
- message: `test: require promoter genome inputs`
- files: promoter cis-element config validation, regression tests, and history entry.

Next:
- Continue tightening module input dependencies so YAML preflight catches missing evidence before downstream workflow execution.

## 2026-06-27 08:59 - Limit manifest validation to selected species

Context:
- The active `/goal` requires YAML-driven species selection from large species banks and prebuilt species manifests.
- Auto species-bank validation already respects `species.include` and `species.exclude`.
- Manifest-mode deep validation still checked every row in the manifest, so an unselected incomplete species could block a selected-species run.

Decisions:
- Apply the same selected-species filtering to manifest-mode path validation.
- Reuse the include normalization helper for both auto and manifest input modes.
- Report missing included species from manifest preflight as `input.manifest requested species not found`.

Added:
- Regression test that manifest-mode validation passes when the included species has valid paths and an unselected manifest row points to missing files.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_only_checks_included_manifest_species -q` first failed because manifest validation checked an unselected incomplete species.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_only_checks_included_manifest_species tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_manifest_file_paths -q` passed after applying include/exclude filtering to manifest validation.
- `python -m pytest tests/test_validate_config.py -q` passed with 34 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 408 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `rg -n "YAML-driven species selection|validate manifest config|species manifest" results/objective_audit/objective_audit.md results/release_checks/release_checks.md` confirmed manifest-mode validation remains part of YAML-driven species-selection evidence.

Commit:
- hash: 087baea10f245012baec276a99875b870781c0e0
- message: `test: validate selected manifest species only`
- files: manifest-mode selected-species path validation, regression tests, and history entry.

Next:
- Continue hardening input preflight and report evidence while preserving selected-species ergonomics for large datasets.

## 2026-06-27 08:52 - Report missing included auto species during preflight

Context:
- The active `/goal` requires YAML-driven species selection from large species banks.
- Auto species-bank validation now respects `species.include` and `species.exclude`, but it did not report explicitly included species that were absent from `input.root`.
- Missing included species would still be caught later by discovery, but config preflight should be the earliest failure point for user-edited YAML.

Decisions:
- Normalize auto-mode `species.include` so `all`, a single string, and a list of species are handled consistently.
- Report requested-but-not-found species during `validate_config --check-paths`.
- Preserve the behavior that excluded species do not need to exist or pass file checks.

Added:
- Regression test that `validate_config --check-paths` reports a missing included species in auto species-bank mode.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_included_auto_species -q` first failed because no error was reported for an included species absent from the species bank.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_included_auto_species tests/test_validate_config.py::test_validate_config_check_paths_only_checks_included_auto_species -q` passed after adding requested-species tracking.
- `python -m pytest tests/test_validate_config.py -q` passed with 33 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 407 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `rg -n "YAML-driven species selection|validate example config|validate manifest config" results/objective_audit/objective_audit.md results/release_checks/release_checks.md` confirmed the objective audit still names both config validation checks as YAML-driven species-selection evidence.

Commit:
- hash: cbd9e3cd2345bb5ae3a4aaa76e3c4116f56893e4
- message: `test: report missing selected auto species`
- files: auto species-bank selected-species preflight, regression tests, and history entry.

Next:
- Continue strengthening large-input validation and report evidence where failures can be moved earlier into reproducible preflight checks.

## 2026-06-27 08:46 - Limit auto species-bank validation to selected species

Context:
- The active `/goal` requires YAML-driven species selection from very large species banks.
- Auto species-bank preflight was hardened to validate required pep/gff3/cds/genome files, but it checked every species directory under `input.root`.
- In a large bank, users may include only a subset of species; unselected incomplete species should not block a selected-species run.

Decisions:
- Keep auto species-bank deep validation enabled by default.
- Respect `species.include` and `species.exclude` when validating auto species-bank required files.
- Continue validating all species when `species.include` is omitted or set to `all`.

Added:
- Regression test that auto species-bank validation passes when the selected species has required pep/gff3 evidence and an unselected species is incomplete.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_only_checks_included_auto_species -q` first failed because validation still checked an unselected incomplete species.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_only_checks_included_auto_species tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_auto_species_required_files -q` passed after applying include/exclude filtering to auto species-bank validation.
- `python -m pytest tests/test_validate_config.py -q` passed with 32 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 406 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `rg -n "YAML-driven species selection|validate example config|validate manifest config" results/objective_audit/objective_audit.md results/release_checks/release_checks.md` confirmed the objective audit still names both config validation checks as YAML-driven species-selection evidence.

Commit:
- hash: 99aa27be09bc5d3500036de5f98e32a878c4b5d9
- message: `test: validate selected auto species only`
- files: auto species-bank validation selection filtering, regression tests, and history entry.

Next:
- Continue strengthening large-input preflight behavior and final report evidence gates without weakening selected-species ergonomics.

## 2026-06-27 08:41 - Validate auto species-bank required files

Context:
- The active `/goal` requires robust large-scale multi-species input handling from YAML.
- After manifest-mode validation was hardened, auto species-bank mode still only checked that `input.root` existed.
- A species bank with valid root and species subdirectories but missing required pep/gff3/cds/genome files could pass preflight and fail later during species discovery or downstream modules.

Decisions:
- Add auto species-bank deep validation to `validate_config --check-paths`.
- For each selected species directory under `input.root`, use configured glob patterns to detect pep/gff3/cds/genome files.
- Report missing required files and multiple matching files during config validation, before Nextflow or downstream Python modules run.

Added:
- Regression test that auto mode reports a missing required pep file when a species directory only contains GFF3 evidence.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_auto_species_required_files -q` first failed because auto species-bank preflight returned no errors when a required pep file was absent.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_auto_species_required_files -q` passed after adding auto species-bank deep validation.
- `python -m pytest tests/test_validate_config.py -q` passed with 31 tests.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 405 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `rg -n "YAML-driven species selection|validate example config|validate manifest config" results/objective_audit/objective_audit.md results/release_checks/release_checks.md` confirmed the objective audit still names both config validation checks as YAML-driven species-selection evidence.

Commit:
- hash: 5bb99e0ac6fd0fe2df653245f29efbe362cde54c
- message: `test: validate auto species bank files`
- files: auto species-bank config validation, regression tests, and history entry.

Next:
- Continue strengthening preflight and report gates where broad MVP promises depend on downstream failures rather than early validation.

## 2026-06-27 08:35 - Validate species manifest contents and file paths

Context:
- The active `/goal` requires a robust multi-species input system driven by YAML.
- `validate_config --check-paths` checked that `input.manifest` existed, but did not validate the manifest TSV columns or the per-species pep/gff3/cds/genome paths declared inside it.
- The downstream species discovery code already expected a strict manifest shape, so config preflight could pass even when the actual manifest would fail later.

Decisions:
- Add deep manifest validation to `validate_config --check-paths` for manifest-mode inputs.
- Require manifest TSV columns `species_id`, `pep`, `gff3`, `cds`, and `genome`.
- Check declared manifest file paths, with required empty paths reported as missing and non-empty paths required to exist relative to `--base-dir`.

Added:
- Regression test for invalid manifest columns during config path validation.
- Regression test for missing per-species pep/gff3 manifest paths during config path validation.

Modified:
- `bin/genefam/validate_config.py`
- `tests/test_validate_config.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_invalid_manifest_columns tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_manifest_file_paths -q` first failed because config validation returned no errors for invalid manifest contents.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_invalid_manifest_columns tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_manifest_file_paths -q` passed after adding deep manifest validation.
- `python -m pytest tests/test_validate_config.py -q` passed with 30 tests.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths` exited 0 with `Configuration OK`.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` exited 0 with `Configuration OK`.
- `python -m pytest tests -q` passed with 404 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `rg -n "YAML-driven species selection|validate manifest config|species manifest" results/objective_audit/objective_audit.md results/release_checks/release_checks.md` confirmed the objective audit still uses the now-deeper manifest config validation as YAML-driven species-selection evidence.

Commit:
- hash: 8da8d7c4aba0b029da43cf6007122306505e5fea
- message: `test: validate species manifest contents`
- files: manifest-mode config validation, regression tests, and history entry.

Next:
- Continue strengthening input and report gates where broad MVP promises depend on weak preflight checks.

## 2026-06-27 08:29 - Require command and R package versions in publication audits

Context:
- The active `/goal` requires final reports to include software versions and R package versions in the methods section.
- `audit_publication_report.py` already required a software version table and checked that method/software components named in figure interpretations had version rows.
- The `software_versions_present` check still passed if any version row existed, so a report with command/runtime versions but no `R_package` rows could pass that specific gate.

Decisions:
- Require publication report audits to see both `command` and `R_package` version categories in detected software-version rows.
- Keep the existing per-figure method/software component version matching as a separate check.
- Align successful test fixtures with the real Nextflow report format, which records command-line tools as `command` and R packages as `R_package`.

Added:
- Regression test that a publication report audit fails `software_versions_present` when command versions are present but `R_package` versions are absent.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_command_and_r_package_versions -q` first failed because `software_versions_present` still passed without any `R_package` version row.
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_command_and_r_package_versions -q` passed after requiring both version categories.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 13 tests after updating success fixtures to include `command` and `R_package` rows.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/wgd_publication_report_audit/wgd_publication_report_audit.tsv --out-md results/wgd_publication_report_audit/wgd_publication_report_audit.md` exited 0.
- `rg -n "software_versions_present|kinds=R_package,command|final reports" results/publication_report_audit/publication_report_audit.md results/wgd_publication_report_audit/wgd_publication_report_audit.md results/objective_audit/objective_audit.md` confirmed both report-family audits now state `kinds=R_package,command`.
- `python -m pytest tests -q` passed with 402 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `head -n 8 results/objective_audit/objective_audit.md` reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the remaining blocked item is the intentionally deferred Docker/Apptainer reproducibility stage.

Commit:
- hash: e408383ea562e96f7774614e180f94b2818acbe6
- message: `test: require r package versions in publication audit`
- files: publication report audit version-category rule, regression tests, and history entry.

Next:
- Continue hardening final-report and visualization evidence where a broad manuscript-level promise still depends on indirect evidence.

## 2026-06-27 08:19 - Require promoter extraction smoke for promoter audit

Context:
- The active `/goal` requires promoter cis-element analysis and publication-level visualization, while the objective audit note explicitly mentions promoter extraction outputs.
- The release gate already has an independent `promoter smoke` check for promoter BED/FASTA and feature-summary outputs, but the promoter objective evidence only required cis-element visualization and Nextflow standard visualization evidence.

Decisions:
- Treat `promoter smoke` as required evidence for the `promoter cis-element visualization` objective row.
- Also require `promoter smoke` in the aggregate `paper-level visualization modules` row, so the top-level paper-figure gate proves both promoter extraction and cis-element visualization.

Added:
- Regression test that the promoter objective is missing when `promoter smoke` is absent, even if cis-element visualization and Nextflow visualization smoke pass.
- Regression test that the paper-level visualization row is missing when promoter extraction smoke is absent.
- Regression expectations that achieved promoter rows name `promoter smoke`.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `results/objective_audit/objective_audit.md`
- `results/objective_audit/objective_audit.tsv`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_paper_level_visualization_modules_require_promoter_extraction_smoke tests/test_audit_objective_completion.py::test_promoter_cis_element_visualization_requires_promoter_extraction_smoke -q` first failed because `promoter smoke` was not required by either objective row.
- `python -m pytest tests/test_audit_objective_completion.py::test_paper_level_visualization_modules_require_promoter_extraction_smoke tests/test_audit_objective_completion.py::test_promoter_cis_element_visualization_requires_promoter_extraction_smoke -q` passed after requiring promoter extraction smoke.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 41 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and refreshed the objective audit.
- `rg -n "paper-level visualization modules|promoter cis-element visualization|promoter smoke" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed both promoter-related objective rows now list `promoter smoke`.
- `python -m pytest tests -q` passed with 401 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `head -n 8 results/objective_audit/objective_audit.md` reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the remaining blocked item is the intentionally deferred Docker/Apptainer reproducibility stage.

Commit:
- hash: 4533804e208add5feb61f77716534786521b2185
- message: `test: require promoter extraction for promoter audit`
- files: objective audit promoter evidence rule, regression tests, refreshed objective audit outputs, and history entry.

Next:
- Continue auditing whether remaining objective rows prove both raw/tool-level evidence and formal Nextflow/report evidence.

## 2026-06-27 08:13 - Require ggNetView status smoke for PPI audit

Context:
- The active `/goal` requires PPI visualization to use ggNetView and to be judged at publication-MVP level.
- The objective audit note already mentioned ggNetView status, but the PPI objective evidence only required the plotted PPI smoke and Nextflow standard visualization smoke.

Decisions:
- Treat `PPI ggNetView smoke` as a required status/readiness proof for the PPI objective row.
- Also require the same ggNetView status smoke in the aggregate `paper-level visualization modules` row, so the paper-level visualization gate proves ggNetView readiness plus rendered network plots.

Added:
- Regression test that `PPI ggNetView visualization` is missing when `PPI ggNetView smoke` is absent, even if the plot smoke and Nextflow visualization smoke pass.
- Regression expectation that the paper-level visualization evidence names `PPI ggNetView smoke`.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `results/objective_audit/objective_audit.md`
- `results/objective_audit/objective_audit.tsv`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_ppi_ggnetview_visualization_requires_ggnetview_status_smoke -q` first failed because the PPI objective was still achieved without `PPI ggNetView smoke`.
- `python -m pytest tests/test_audit_objective_completion.py::test_ppi_ggnetview_visualization_requires_ggnetview_status_smoke -q` passed after requiring the status smoke.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 39 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and refreshed the objective audit.
- `rg -n "paper-level visualization modules|PPI ggNetView visualization|PPI ggNetView smoke" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed both objective rows now list `PPI ggNetView smoke`.
- `python -m pytest tests -q` passed with 399 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 after the fresh release check run.
- `head -n 8 results/objective_audit/objective_audit.md` reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the remaining blocked item is the intentionally deferred Docker/Apptainer reproducibility stage.

Commit:
- hash: 476f75bbeda4c6c39568d5e53f9b25f23fac3c17
- message: `test: require ggnetview status for ppi audit`
- files: objective audit PPI evidence rule, regression tests, refreshed objective audit outputs, and history entry.

Next:
- Continue hardening any remaining report rows where a figure-level output needs both standalone tool evidence and formal Nextflow/report evidence.

## 2026-06-27 07:14 - Require Nextflow report evidence for tree-feature audit

Context:
- The active `/goal` requires tree, motif, gene-structure, and domain composite figures to be connected to the formal Nextflow/YAML/report-index/final-report/release-check workflow.
- The standard feature report already registered motif summary, gene-structure summary, tree-feature matrix, tree-feature PDF/PNG plots, and per-figure close reading.
- The objective audit tree-feature row still treated standalone `tree feature visualization smoke` and `feature summary visualization smoke` as sufficient evidence.

Decisions:
- Keep `tree feature visualization smoke` and `feature summary visualization smoke` as module-level proof.
- Require `Nextflow standard visualization smoke` as the formal report-integration proof for the `tree motif gene-structure domain visualization` objective row.
- Make the objective audit note explicitly mention Nextflow report evidence for tree/motif/gene-structure/domain figures.

Added:
- Regression test that the tree/motif/gene-structure/domain objective row is missing when only the standalone tree-feature and feature-summary smokes are present.
- Regression expectations that the achieved tree-feature objective row names `Nextflow standard visualization smoke` and `Nextflow report evidence`.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `results/objective_audit/objective_audit.md`
- `results/objective_audit/objective_audit.tsv`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_objective_audit_lists_named_paper_level_visualization_requirements tests/test_audit_objective_completion.py::test_tree_motif_gene_structure_domain_requires_nextflow_standard_visualization_smoke -q` first failed because the tree-feature row evidence only contained standalone tree/feature smokes and still marked standalone evidence as achieved.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 28 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and the tree-feature row now lists `tree feature visualization smoke, feature summary visualization smoke, and Nextflow standard visualization smoke`.
- `python -m pytest tests -q` passed with 388 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `rg -n "tree motif gene-structure domain visualization|Nextflow report evidence|tree_features|tree_feature_matrix|motif_summary|gene_structure_summary" results/objective_audit/objective_audit.md results/release_checks/release_checks.tsv results/nextflow_standard_feature_smoke/standard/report/report_index.tsv results/nextflow_standard_feature_smoke/standard/report/final_report.md` confirmed objective-audit, release-check, report-index, and final-report coverage.

Commit:
- hash: d1762c69d22f04465a2fa0a40d997a82b16987c0
- message: `test: require nextflow evidence for tree feature audit`
- files: objective audit tree-feature evidence rule, regression tests, refreshed objective audit outputs, and history entry.

Next:
- Continue tightening any remaining visualization or WGD rows whose standalone smoke evidence is stronger than the formal Nextflow report proof.

## 2026-06-27 07:08 - Require Nextflow report evidence for copy-number audit

Context:
- The active `/goal` requires gene-family information, copy-number, pangenome, and protein-property summary figures to be connected to the formal Nextflow/YAML/report-index/final-report/release-check workflow.
- The standard feature report already registered copy-number, copy-number summary, expansion/contraction, pangenome summary, protein-property tables, and gene-family information PDF/PNG plots.
- The objective audit copy-number row still treated the standalone `gene family information visualization smoke` as sufficient evidence.

Decisions:
- Keep `gene family information visualization smoke` as module-level proof.
- Require `Nextflow standard visualization smoke` as the formal report-integration proof for the `gene family information and copy-number visualization` objective row.
- Make the objective audit note explicitly mention Nextflow report evidence for gene-family/copy-number plots.

Added:
- Regression test that the copy-number objective row is missing when only the standalone gene-family information smoke is present.
- Regression expectations that the achieved copy-number objective row names `Nextflow standard visualization smoke` and `Nextflow report evidence`.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `results/objective_audit/objective_audit.md`
- `results/objective_audit/objective_audit.tsv`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_objective_audit_lists_named_paper_level_visualization_requirements tests/test_audit_objective_completion.py::test_gene_family_information_copy_number_requires_nextflow_standard_visualization_smoke -q` first failed because the copy-number row evidence only contained `gene family information visualization smoke` and still marked standalone evidence as achieved.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 27 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and the copy-number row now lists `gene family information visualization smoke and Nextflow standard visualization smoke`.
- `python -m pytest tests -q` passed with 387 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `rg -n "gene family information and copy-number visualization|Nextflow report evidence|gene_family_info|gene_family_copy_number" results/objective_audit/objective_audit.md results/release_checks/release_checks.tsv results/nextflow_standard_feature_smoke/standard/report/report_index.tsv results/nextflow_standard_feature_smoke/standard/report/final_report.md` confirmed objective-audit, release-check, report-index, and final-report coverage.

Commit:
- hash: b76630465b5c50da6c00e690c1d26b771f6db8e1
- message: `test: require nextflow evidence for copy number audit`
- files: objective audit copy-number evidence rule, regression tests, refreshed objective audit outputs, and history entry.

Next:
- Continue tightening any remaining visualization rows whose standalone smoke evidence is stronger than the formal Nextflow report proof.

## 2026-06-27 07:02 - Require Nextflow report evidence for expression heatmap audit

Context:
- The active `/goal` requires RNA-seq expression heatmap outputs to be connected to the formal Nextflow/YAML/report-index/final-report/release-check workflow.
- The release checks already ran `--expression-matrix` and `--expression-metadata` inside `Nextflow standard visualization smoke`, and the standard feature report already registered expression tables, QC, and PDF/PNG heatmap plots.
- The objective audit expression row still treated the Python standard expression smoke plus standalone expression heatmap smoke as sufficient evidence.

Decisions:
- Keep `standard branch expression smoke` and `expression heatmap visualization smoke` as module-level proof.
- Require `Nextflow standard visualization smoke` as the formal report-integration proof for the `expression heatmap visualization` objective row.
- Make the objective audit note explicitly mention Nextflow report evidence for expression heatmaps.

Added:
- Regression test that the expression heatmap objective row is missing when only the Python standard-expression and standalone expression-heatmap smokes are present.
- Regression expectations that the achieved expression objective row names `Nextflow standard visualization smoke` and `Nextflow report evidence`.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `results/objective_audit/objective_audit.md`
- `results/objective_audit/objective_audit.tsv`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_objective_audit_lists_named_paper_level_visualization_requirements tests/test_audit_objective_completion.py::test_expression_heatmap_visualization_requires_nextflow_standard_visualization_smoke -q` first failed because the expression row evidence did not include `Nextflow standard visualization smoke` and still marked standalone/Python expression evidence as achieved.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 26 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and the expression row now lists `standard branch expression smoke, expression heatmap visualization smoke, and Nextflow standard visualization smoke`.
- `python -m pytest tests -q` passed with 386 tests; pytest emitted a temporary-directory cleanup warning after success, but no tests failed.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `rg -n "expression heatmap visualization|Nextflow report evidence|--expression-matrix|expression_heatmap" results/objective_audit/objective_audit.md results/release_checks/release_checks.tsv results/nextflow_standard_feature_smoke/standard/report/report_index.tsv results/nextflow_standard_feature_smoke/standard/report/final_report.md` confirmed objective-audit, release-check, report-index, and final-report coverage.

Commit:
- hash: 5b894160ead2bf7342f0da3efb9e6310b43c3b4c
- message: `test: require nextflow evidence for expression audit`
- files: objective audit expression evidence rule, regression tests, refreshed objective audit outputs, and history entry.

Next:
- Continue tightening any remaining visualization rows whose standalone smoke evidence is stronger than the formal Nextflow report proof.

## 2026-06-27 06:55 - Require Nextflow report evidence for PPI ggNetView audit

Context:
- The active `/goal` requires ggNetView PPI figures to be connected to the formal Nextflow/YAML/report-index/final-report/release-check workflow.
- The release checks already ran `--run-ppi` inside `Nextflow standard visualization smoke`, and the standard feature report already registered PPI tables, QC, ggNetView status, and PDF/PNG plots.
- The objective audit PPI row still treated the standalone `PPI ggNetView plot smoke` as sufficient evidence.

Decisions:
- Keep standalone `PPI ggNetView plot smoke` as module-level proof.
- Require `Nextflow standard visualization smoke` as the formal report-integration proof for the `PPI ggNetView visualization` objective row.
- Make the objective audit note explicitly mention Nextflow report evidence for PPI.

Added:
- Regression test that the PPI objective row is missing when only the standalone PPI plot smoke is present.
- Regression expectations that the achieved PPI objective row names `Nextflow standard visualization smoke` and `Nextflow report evidence`.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `results/objective_audit/objective_audit.md`
- `results/objective_audit/objective_audit.tsv`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_objective_audit_lists_named_paper_level_visualization_requirements tests/test_audit_objective_completion.py::test_ppi_ggnetview_visualization_requires_nextflow_standard_visualization_smoke -q` first failed because the PPI row evidence only contained `PPI ggNetView plot smoke` and still marked standalone PPI evidence as achieved.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 25 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and the PPI row now lists `PPI ggNetView plot smoke and Nextflow standard visualization smoke`.
- `python -m pytest tests -q` passed with 385 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `rg -n "PPI ggNetView visualization|Nextflow report evidence|--run-ppi|ppi_ggnetview" results/objective_audit/objective_audit.md results/release_checks/release_checks.tsv results/nextflow_standard_feature_smoke/standard/report/report_index.tsv results/nextflow_standard_feature_smoke/standard/report/final_report.md` confirmed objective-audit, release-check, report-index, and final-report coverage.

Commit:
- hash: 1631729e042c5bd5c633e5e385d649e36f3c5e04
- message: `test: require nextflow evidence for ppi audit`
- files: objective audit PPI evidence rule, regression tests, refreshed objective audit outputs, and history entry.

Next:
- Continue tightening any remaining visualization rows whose standalone smoke evidence is stronger than the formal Nextflow report proof.

## 2026-06-27 06:48 - Wire promoter extraction into standard Nextflow visualization smoke

Context:
- The active `/goal` requires promoter analysis and visualization to be part of the formal Nextflow/YAML/report/release-check workflow, not only standalone script smokes.
- The standard Nextflow feature smoke already generated promoter cis-element figures, but the final report still listed `promoters_bed` and `promoters_fasta` as missing.

Decisions:
- Add a first-class `--run-promoter` option to the standard Nextflow smoke runner.
- Make the formal `Nextflow standard visualization smoke` release check enable promoter extraction and require published promoter BED/FASTA outputs.
- Upgrade the example species-bank fixtures with minimal genome FASTA files so the promoter extraction path exercises real genome and GFF3 inputs.
- Make the objective audit distinguish promoter extraction plus promoter cis-element visualization as formal Nextflow report evidence.

Added:
- `tests/fixtures/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.genome.fa`
- `tests/fixtures/species_bank/Brassica_rapa/Brassica_rapa.genome.fa`
- Regression tests for `--run-promoter`, promoter published outputs, fixture genome discovery, release-check command coverage, and objective audit promoter-extraction wording.

Modified:
- `bin/genefam/run_nextflow_standard_smoke.py`
- `bin/genefam/run_release_checks.py`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_release_checks.py`
- `tests/test_discover_species.py`
- `tests/test_audit_objective_completion.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_nextflow_standard_smoke.py::test_build_nextflow_command_can_enable_promoter_extraction_for_standard_reports tests/test_run_nextflow_standard_smoke.py::test_expected_published_outputs_can_include_promoter_extraction_outputs -q` first failed with unexpected `run_promoter` / `promoter` keyword arguments.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_nextflow_standard_visualization_smoke_before_wgd -q` first failed after tightening the assertion to require an independent `--run-promoter` token.
- `python -m pytest tests/test_discover_species.py::test_example_species_bank_exposes_genome_paths_for_promoter_extraction -q` first failed with `Missing required genome file for species Arabidopsis_thaliana`.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --run-promoter --run-promoter-cis --promoter-cis-elements tests/fixtures/promoter_cis/plantcare.tsv --run-ppi --ppi-edges tests/fixtures/ppi/ppi_edges.tsv --ppi-nodes tests/fixtures/ppi/ppi_nodes.tsv --expression-matrix tests/fixtures/expression/family_expression.tsv --expression-metadata tests/fixtures/expression/sample_metadata.tsv --outdir results/nextflow_standard_feature_smoke` first failed because `EXTRACT_PROMOTERS` reported `Missing genome path for Arabidopsis_thaliana`; it passed after adding genome fixtures.
- `python -m pytest tests/test_discover_species.py -q` passed with 10 tests.
- `python -m pytest tests/test_run_nextflow_standard_smoke.py -q` passed with 18 tests.
- `python -m pytest tests/test_run_release_checks.py tests/test_run_nextflow_standard_smoke.py tests/test_discover_species.py -q` passed with 79 tests.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 24 tests.
- `python -m pytest tests -q` passed with 384 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 9`, `Failed: 0`, `Complete: true`.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n -e "--run-promoter|promoters_bed|promoters_fasta|promoter extraction|promoters\\.bed|promoters\\.fa" results/release_checks/release_checks.tsv results/objective_audit/objective_audit.md results/nextflow_standard_feature_smoke/standard/report/report_index.tsv results/nextflow_standard_feature_smoke/standard/report/final_report.md` confirmed release-check, objective-audit, report-index, and final-report coverage.

Commit:
- hash: bed8f73ba0115140e8476d30a8ae55c68d666dc0
- message: `test: wire promoter extraction into nextflow smoke`
- files: standard Nextflow smoke runner, release checks, objective audit, species-bank genome fixtures, regression tests, and history entry.

Next:
- Continue auditing formal Nextflow report evidence for any remaining modules whose standalone smoke is stronger than their integrated report proof.

## 2026-06-27 06:36 - Expose publication report closure gates in objective audit

Context:
- The active `/goal` requires the machine objective audit to reflect the full paper-style report closure criteria.
- The publication report audits already validate plot file signatures, registered-only interpretation scope, and plot manifest/interpretation path consistency, but the objective audit `final reports` note still only described the older close-reading text checks.

Decisions:
- Keep the objective audit as the human-readable completion ledger for the MVP goal.
- Make the `final reports` row explicitly name valid plot file signatures, registered-only figure interpretation scope, and plot manifest and interpretation output path consistency.

Added:
- Regression expectations that the objective audit final-report note names all current publication report closure gates.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `results/objective_audit/objective_audit.md`
- `results/objective_audit/objective_audit.tsv`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure -q` first failed because the final-report note did not contain `valid plot file signatures`.
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure -q` passed after the audit note update.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 24 tests.
- `python -m pytest tests -q` passed with 381 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "valid plot file signatures|registered-only figure interpretation scope|plot manifest and interpretation output path consistency" results/objective_audit/objective_audit.md` confirmed the `final reports` row names all three gates.

Commit:
- hash: 9b0557ca26f343126766bb8e4915da3a095ef75b
- message: `test: expose report closure gates in objective audit`
- files: objective audit wording, objective audit regression test, regenerated objective audit outputs, and history entry.

Next:
- Continue broad MVP audit only after choosing the next highest-risk remaining product gap; container packaging remains deferred until the analysis workflow is complete.

## 2026-06-27 06:29 - Reject unregistered figure interpretation rows

Context:
- The active `/goal` requires final reports to provide exact close reading for every registered figure in the result package.
- The publication report audit already checked that every `plot_manifest.tsv` plot has an interpretation row, that paths match, and that plots are valid files.
- It did not yet reject extra `figure_interpretations.tsv` rows whose `figure_key` was not registered in `plot_manifest.tsv`, which could let a report interpret figures outside the final delivery plot inventory.

Decisions:
- Add a dedicated `figure_interpretation_scope` publication-audit row.
- Treat `plot_manifest.tsv` as the authoritative plot inventory; every `figure_interpretations.tsv` `figure_key` must appear as a registered `plot_key`.
- Surface this gate in delivery bundle and user-facing docs as `registered-only figure interpretation scope`.

Added:
- Regression test for an orphan `figure_interpretations.tsv` row not present in `plot_manifest.tsv`.
- Publication audit scope check for unregistered figure interpretation rows.
- Delivery bundle and documentation wording for registered-only figure interpretation scope.

Modified:
- `bin/genefam/audit_publication_report.py`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_audit_publication_report.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `README.md`
- `README.zh-CN.md`
- `docs/quickstart.md`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_rejects_unregistered_figure_interpretations -q` first failed with `KeyError: 'figure_interpretation_scope'`; it passed after adding the audit row.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 12 tests.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 9`, including `figure_interpretation_scope`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `Passed: 9`, including `figure_interpretation_scope`.
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` first failed until delivery bundle and docs mentioned `registered-only figure interpretation scope`; it passed after the wording updates.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` exited 0 and refreshed the delivery bundle with the scope gate.
- `python -m pytest tests -q` passed with 381 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and produced `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.

Commit:
- hash: 62949bff4af3c8a742c6f174bbadc93ff9601ada
- message: test: reject unregistered figure interpretations
- files: publication audit, delivery bundle, docs/tests, history

Next:
- Continue toward the active `/goal` by auditing remaining MVP evidence surfaces; Docker/Apptainer packaging remains the final external runtime stage.

## 2026-06-27 06:18 - Match figure interpretation output paths to plot manifest

Context:
- The active `/goal` requires every report figure to be closed by precise interpretation, QC, methods, version, and reproducibility evidence.
- The publication report audit already checked figure files, format signatures, and interpretation coverage, but it did not prove that `figure_interpretations.tsv` `output_path` values matched the registered `plot_manifest.tsv` paths.
- Without that check, a final report could explain a figure key while pointing the interpretation section at a different plot file.

Decisions:
- Add a dedicated `figure_output_paths_match_manifest` publication-audit row.
- Compare `plot_manifest.tsv` `plot_key/path` to `figure_interpretations.tsv` `figure_key/output_path` for every registered plot with an interpretation row.
- Surface the same gate in the delivery bundle and user-facing docs as `plot manifest and interpretation output path consistency`.

Added:
- Regression test for a mismatched manifest path versus interpretation `output_path`.
- Publication audit path-consistency check.
- Delivery bundle and documentation wording for plot manifest and interpretation output path consistency.

Modified:
- `bin/genefam/audit_publication_report.py`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_audit_publication_report.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `README.md`
- `README.zh-CN.md`
- `docs/quickstart.md`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_interpretation_output_path_to_match_manifest -q` first failed with `KeyError: 'figure_output_paths_match_manifest'`; it passed after adding the audit row.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 11 tests.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 8`, including `figure_output_paths_match_manifest`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `Passed: 8`, including `figure_output_paths_match_manifest`.
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` first failed until delivery bundle and docs mentioned `plot manifest and interpretation output path consistency`; it passed after the wording updates.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` exited 0 and refreshed the delivery bundle with the path-consistency gate.
- `python -m pytest tests -q` passed with 380 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and produced `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.

Commit:
- hash: 9d37e7b8b21ce48e531f64f500b001c8e389cbda
- message: test: require figure output path consistency
- files: publication audit, delivery bundle, docs/tests, history

Next:
- Continue toward the active `/goal` by auditing remaining MVP evidence surfaces; Docker/Apptainer packaging remains the final external runtime stage.

## 2026-06-27 06:08 - Validate publication plot file signatures

Context:
- The active `/goal` asks for paper-level visualization and a final report package that can be trusted as an MVP result bundle.
- The publication report audit checked that plot files existed and were non-empty, but a non-empty error log or text file with a `.pdf` suffix could still satisfy that weaker condition.

Decisions:
- Add a `plot_file_format_valid` publication-audit row that checks basic PDF, PNG, and SVG file signatures for every plot registered in `plot_manifest.tsv`.
- Keep the check lightweight and dependency-free: PDF must start with `%PDF`, PNG must use the PNG magic header, and SVG must start with `<svg` or an XML header after whitespace.
- Surface this gate in the delivery bundle and user-facing docs as `valid plot file signatures`.

Added:
- Regression test proving a non-empty invalid `.pdf` plot passes `plot_files_exist` but fails `plot_file_format_valid`.
- Publication audit logic for PDF/PNG/SVG signature validation.
- Delivery bundle and documentation wording for valid plot file signatures.

Modified:
- `bin/genefam/audit_publication_report.py`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_audit_publication_report.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `README.md`
- `README.zh-CN.md`
- `docs/quickstart.md`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_rejects_nonempty_invalid_plot_format -q` first failed with `KeyError: 'plot_file_format_valid'`; it passed after adding the audit row.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 10 tests.
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` first failed until delivery bundle and docs mentioned `valid plot file signatures`; it passed after the wording updates.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 7`, including `plot_file_format_valid`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `Passed: 7`, including `plot_file_format_valid`.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` exited 0 and refreshed the delivery bundle with `valid plot file signatures`.
- `python -m pytest tests -q` passed with 379 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and produced `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.

Commit:
- hash: cd8f69b22a34b7361ade9279321b20946af509fc
- message: test: validate publication plot formats
- files: publication audit, delivery bundle, docs/tests, history

Next:
- Continue toward the active `/goal` by auditing remaining MVP evidence surfaces; Docker/Apptainer packaging still remains the final external runtime stage.

## 2026-06-27 05:59 - Surface per-figure method software coverage in delivery bundle

Context:
- The publication report audit now verifies `figure_method_software_versions`, proving that software and R packages named by each figure interpretation have corresponding `software_versions.tsv` rows.
- The final delivery bundle and user-facing docs still summarized publication closure as generic software/R package version evidence, without naming the new per-figure method/software version coverage gate.

Decisions:
- Keep the publication audit as the authoritative machine check.
- Surface the same gate in `results/delivery_bundle/delivery_manifest.tsv`, `results/delivery_bundle/delivery_bundle.md`, README, quickstart, readiness checklist, and release audit docs so the handoff package is readable without opening every audit TSV first.
- Keep Docker/Apptainer wording unchanged because packaging remains the final external runtime stage.

Added:
- Regression expectations requiring delivery bundle and docs to mention `per-figure method/software version coverage`.

Modified:
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `README.md`
- `README.zh-CN.md`
- `docs/quickstart.md`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index -q` first failed because the delivery manifest did not mention `per-figure method/software version coverage`; it passed after updating `run_delivery_bundle.py`.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` first failed for README, quickstart, readiness checklist, and release audit wording; it passed after the docs were updated.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py tests/test_run_delivery_bundle.py -q` passed with 18 tests.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` exited 0 and refreshed `results/delivery_bundle/delivery_manifest.tsv` plus `results/delivery_bundle/delivery_bundle.md`.
- `python -m pytest tests -q` passed with 378 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and produced `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.

Commit:
- hash: 672f835342093baac81c5c2ed58484d365819bc0
- message: docs: expose method software coverage gate
- files: delivery bundle generator, delivery/docs tests, README/docs, history

Next:
- Continue toward the active `/goal` by auditing the remaining result-package surfaces for any broad claim that is not yet directly visible in the delivery bundle.

## 2026-06-27 05:51 - Require figure method software version coverage

Context:
- The active `/goal` requires the conclusion report to explain each figure and state the software and R package versions used in the methods.
- The publication report audit already required per-figure close-reading text and checked that the software version table was embedded in the final report, but it did not prove that software named in each figure's `method_and_software` field had a corresponding version row.

Decisions:
- Add a dedicated publication-report audit row named `figure_method_software_versions`.
- Treat version rows with `version_not_detected` as explicit report evidence for currently unavailable external tools, while still requiring every versioned component named by a figure method to appear in `software_versions.tsv`.
- Ignore internal scripts and the `GeneFamilyFlow` environment label for this check; enforce external tools and R packages such as FastTree, MAFFT, MCScanX, KaKs_Calculator, R, circlize, pheatmap, and ggNetView.

Added:
- Regression test proving the audit fails when figure methods mention FastTree, MAFFT, or ggNetView but the software version table only lists R.
- Publication audit check that maps figure method/software text to expected software-version components.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_versions_for_figure_method_software -q` first failed with `KeyError: 'figure_method_software_versions'`; it passed after adding the audit row.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 9 tests.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_publication_report_audit_after_visualization_report tests/test_run_release_checks.py::test_default_checks_include_wgd_publication_report_audit_after_wgd_smoke -q` passed with 2 tests.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `figure_method_software_versions` passed.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `figure_method_software_versions` passed.
- `python -m pytest tests -q` passed with 378 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and produced `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.

Commit:
- hash: 0ef2b2516b81ddabf5516f4e658dc91703998533
- message: test: require figure method software versions
- files: publication report audit, publication audit tests, history

Next:
- Continue toward the active `/goal` by tightening any remaining acceptance evidence that is still broader than the user-facing MVP promise, while leaving Docker/Apptainer packaging for the final stage.

## 2026-06-27 05:44 - Add named visualization objective audit rows

Context:
- The active `/goal` requires GeneFam-Pipeline to align with the two `Reference/` papers at the level of named figure classes, not only as a generic aggregate visualization gate.
- The objective audit already had a broad paper-level visualization row, but it did not explicitly show whether gene family information, tree/motif/gene-structure/domain, MCScanX/circlize, promoter, expression, PPI, and Ka/Ks/WGD visualizations were each covered.

Decisions:
- Keep the aggregate `paper-level visualization modules` row as the overall signal.
- Add explicit objective-audit rows for each major paper-level visualization class so the MVP acceptance report can be read like a figure checklist.
- Require MCScanX/circlize evidence to include the standard Nextflow visualization smoke, so the row proves workflow integration rather than only standalone script behavior.

Added:
- Regression tests for named objective-audit rows covering gene family information/copy number, tree/motif/gene-structure/domain, MCScanX synteny/circlize, promoter cis-elements, expression heatmaps, PPI ggNetView, and Ka/Ks WGD figures.
- Objective-audit requirement rows for the seven named visualization classes.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- Red test first failed with `KeyError: 'gene family information and copy-number visualization'` before the new objective rows were implemented.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 24 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and produced `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `python -m pytest tests/test_audit_objective_completion.py tests/test_run_release_checks.py::test_write_objective_audit_uses_release_rows_and_readiness_tsv tests/test_run_release_checks.py::test_write_objective_audit_requires_expression_smoke_for_expression_integration -q` passed with 26 tests.
- `python -m pytest tests -q` passed with 377 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: 46319a5676ed72cf81641356f51d982e86cd039c
- message: test: add named visualization objective rows
- files: objective audit logic, objective audit tests, history

Next:
- Continue toward the active `/goal` by auditing any remaining MVP polish gaps after the named visualization evidence is now explicit.

## 2026-06-27 05:36 - Align delivery bundle with complete report closure

Context:
- The active `/goal` requires the final report package to prove each figure has close reading, software/R package versions, QC, and reproducibility information.
- Publication report audit and objective audit already enforced that closure, but the user-facing delivery bundle and several docs still described report closure with older wording such as generic figure interpretations.
- The final delivery index should use the same complete closure language as the machine audit gates.

Decisions:
- Update `publication_report_audit` and `wgd_publication_report_audit` delivery manifest notes to mention complete per-figure close-reading text, QC tables and warnings, software/R package versions, and reproducibility commands.
- Update README, quickstart, readiness checklist, and release audit wording so user-facing instructions match the delivery bundle and publication audit gates.
- Keep Docker/Apptainer profile failures optional because container verification remains the final external runtime stage.

Added:
- Regression expectations requiring delivery bundle and docs to use the complete report-closure vocabulary.

Modified:
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_release_audit_docs.py`
- `tests/test_quickstart_docs.py`
- `README.md`
- `docs/quickstart.md`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index -q` first failed because the delivery manifest still used generic report-closure wording; it passed after updating the delivery bundle notes.
- `python -m pytest tests/test_runtime_environment_files.py tests/test_release_audit_docs.py tests/test_quickstart_docs.py -q` first failed until README, quickstart, readiness checklist, and release audit used the complete report-closure vocabulary; it passed after the docs were updated.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` exited 0 and refreshed `results/delivery_bundle/delivery_manifest.tsv` and `results/delivery_bundle/delivery_bundle.md`.
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_runtime_environment_files.py tests/test_release_audit_docs.py tests/test_quickstart_docs.py -q` passed with 18 tests.
- `python -m pytest tests -q` passed with 375 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: 5afc063093fd82b2954aedcfd69cebc9bf6da864
- message: docs: align delivery report closure wording
- files: delivery bundle, docs, delivery/docs tests, history

Next:
- Continue final MVP audit work across remaining delivery and acceptance polish; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 05:26 - Clarify final-report closure in objective audit

Context:
- The active `/goal` requires the final/conclusion report to contain close reading for every figure, software and R package versions, QC, and reproducibility information.
- Publication report audit now enforces those details, but the higher-level objective audit still described the final-report requirement as generic per-figure interpretation.
- The MVP acceptance surface should explicitly state that final reports are closed by complete per-figure close-reading text, not only by a figure interpretation row.

Decisions:
- Keep the objective audit row shape unchanged.
- Strengthen the `final reports` note to name the complete closure fields: input data, what the figure shows, key observations, biological interpretation, QC warnings, QC tables, method/software, software/R package versions, reproducibility commands, reading status, output paths, and registered plot files.
- Treat this as an acceptance evidence improvement, not a report-generation behavior change.

Added:
- Regression test requiring the objective audit `final reports` note to mention complete per-figure close-reading text, software/R package versions, QC, and reproducibility commands.

Modified:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure -q` first failed because the objective audit note only mentioned generic per-figure interpretation; it passed after strengthening the note.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 22 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited 0 and refreshed `results/objective_audit/objective_audit.md`.
- `python -m pytest tests/test_audit_objective_completion.py tests/test_run_release_checks.py::test_write_objective_audit_uses_release_rows_and_readiness_tsv tests/test_run_release_checks.py::test_write_objective_audit_requires_expression_smoke_for_expression_integration -q` passed with 24 tests.
- `python -m pytest tests -q` passed with 375 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: cfa5ce6895b7752e72087fb1d4fd7e1770410a7f
- message: test: clarify final report objective closure
- files: objective audit, objective audit tests, history

Next:
- Continue final MVP audit work across delivery polish and acceptance surfaces; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 05:19 - Require complete figure close readings in final reports

Context:
- The active `/goal` requires the conclusion/final report to include close reading for every figure, not just a reference to a TSV.
- The standard and WGD final reports already embedded `What the figure shows`, `Key observations`, `Biological interpretation`, and `QC warnings / limitations`, but publication audit only enforced QC tables, method/software, reproducibility, reading status, output path, and software versions.
- A future regression could therefore keep a valid `figure_interpretations.tsv` while dropping the main figure-reading text from `final_report.md`.

Decisions:
- Treat the full per-figure close-reading schema as required publication evidence: input data, what the figure shows, key observations, biological interpretation, QC warnings, QC tables, method/software, reproducibility, reading status, and output path.
- Reuse the existing `figure_interpretation_detail` and `final_report_embeds_publication_sections` audit rows so release checks keep the same compact shape.
- Keep the real report assembly unchanged because the current standard and WGD reports already embed the complete close-reading text.

Added:
- Regression test proving publication audit fails when final report omits the core close-reading text even if `figure_interpretations.tsv` is complete.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_close_reading_text_embedded_in_final_report -q` first failed because final-report embedding did not check close-reading text; it passed after expanding the audit fields.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 8 tests.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests/test_audit_publication_report.py tests/test_run_release_checks.py::test_default_checks_include_publication_report_audit_after_visualization_report tests/test_run_release_checks.py::test_default_checks_include_wgd_publication_report_audit_after_wgd_smoke -q` passed with 10 tests.
- `python -m pytest tests -q` passed with 374 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: c296b3715e65f384e9d72b9689f01f2516aa5953
- message: test: require complete figure readings in reports
- files: publication report audit, audit tests, history

Next:
- Continue final MVP audit work across report polish and acceptance surfaces; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 05:13 - Require software versions in final reports

Context:
- The active `/goal` requires final reports to document software and R package versions in the methods/report package, including tools such as FastTree, MCScanX, Ka/Ks tooling, ggNetView, and `/usr/local/bin/R`.
- The publication audit already required a non-empty `software_versions.tsv` and a `### Software Versions` heading, but it did not verify that the final Markdown report embedded the actual component/version values.
- A final report could therefore pass with a complete version TSV while omitting specific software version rows from the user-facing report.

Decisions:
- Treat every detected non-missing `software_versions.tsv` row as final-report evidence that must be embedded by component and version.
- Reuse `final_report_embeds_publication_sections` so the publication report audit remains a compact five-row gate.
- Keep Docker/Apptainer runtime checks optional until the final packaging stage, as agreed.

Added:
- Regression test proving a report fails publication audit when FastTree/R version rows exist in `software_versions.tsv` but are absent from `final_report.md`.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_software_versions_embedded_in_final_report -q` first failed because final-report embedding did not check software version rows; it passed after adding the check.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 7 tests.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests/test_audit_publication_report.py tests/test_run_release_checks.py::test_default_checks_include_publication_report_audit_after_visualization_report tests/test_run_release_checks.py::test_default_checks_include_wgd_publication_report_audit_after_wgd_smoke -q` passed with 9 tests.
- `python -m pytest tests -q` passed with 373 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the optional failures remain Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: 8ddf3b7a79b8a2b8a83ac80599d5d6bfe6d63a76
- message: test: require software versions in final reports
- files: publication report audit, audit tests, history

Next:
- Continue final MVP audit work across report polish and acceptance surfaces; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 05:06 - Require final reports to embed reading status

Context:
- The active `/goal` requires final reports to include per-figure close reading, QC, software/version context, and reproducibility.
- Publication audit already required `figure-specific close reading` in the TSV, but it did not verify that the final Markdown report embedded the `result_reading_status` text.
- A report package could therefore pass with a complete TSV while the user-facing final report omitted the close-reading status line.

Decisions:
- Treat `result_reading_status` as part of the final-report embedded publication evidence.
- Reuse the existing `final_report_embeds_publication_sections` audit row instead of adding a new check name.
- Keep the audit symmetric with existing QC, method/software, and reproducibility embedding checks.

Added:
- Regression test proving a missing final-report reading-status line fails publication audit even when TSV details are valid.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py::test_publication_report_audit_requires_reading_status_embedded_in_final_report -q` first failed because final-report embedding did not check `result_reading_status`; it passed after adding that field to the embedding audit.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 6 tests.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests/test_audit_publication_report.py tests/test_run_release_checks.py::test_default_checks_include_publication_report_audit_after_visualization_report tests/test_run_release_checks.py::test_default_checks_include_wgd_publication_report_audit_after_wgd_smoke -q` passed with 8 tests.
- `python -m pytest tests -q` passed with 372 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: 7487990db22b8ddcace3189554447f03cf838976
- message: test: require final report reading status
- files: publication report audit, audit tests, history

Next:
- Continue checking final report and delivery surfaces against the full objective; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 04:59 - Enforce figure-specific readings in publication audit

Context:
- The active `/goal` requires the final report to include close reading for every figure.
- Standard and WGD report outputs now use `figure-specific close reading`, but the publication audit only checked that `result_reading_status` existed.
- A report could still pass audit after regressing to `template-guided close reading`.

Decisions:
- Treat `result_reading_status` as semantically required, not just non-empty.
- Fail `figure_interpretation_detail` when any registered figure has a status that does not start with `figure-specific close reading`.
- Keep the existing audit row and note format so release checks do not need a new check name.

Added:
- Regression test proving `template-guided close reading` fails publication audit.

Modified:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py -q` first failed because `template-guided close reading` still passed; it passed after adding the `not_figure_specific` detail failure.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests/test_audit_publication_report.py tests/test_run_release_checks.py::test_default_checks_include_publication_report_audit_after_visualization_report tests/test_run_release_checks.py::test_default_checks_include_wgd_publication_report_audit_after_wgd_smoke -q` passed with 7 tests.
- `python -m pytest tests -q` passed with 371 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: e8b28955e4cba3142e835bf99f47d4ce12ad0a9e
- message: test: enforce figure-specific publication readings
- files: publication report audit, audit tests, history

Next:
- Continue checking final report semantics and delivery surfaces against the full objective; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 04:52 - Require figure-specific readings for all standard plots

Context:
- The active `/goal` requires the final report to include close reading for every figure.
- After splitting WGD and family-information figure readings, several standard report figures still carried `template-guided close reading` status.
- The standard report should make every registered plot read as a figure-specific result interpretation.

Decisions:
- Keep generic fallback templates available for unspecified plot types.
- Require all standard registered plots in the standard feature smoke report to use `figure-specific close reading`.
- Update reading status text for pangenome, tree, feature summary, MCScanX/circlize, promoter cis-element, PPI ggNetView, and expression heatmap plots.
- Document that the standard plot manifest should have no `template-guided close reading` status remaining.

Added:
- Test requiring every standard registered plot to start its `result_reading_status` with `figure-specific close reading`.

Modified:
- `bin/genefam/build_figure_interpretations.py`
- `tests/test_build_figure_interpretations.py`
- `tests/test_release_audit_docs.py`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_figure_interpretations.py::test_standard_registered_plots_use_figure_specific_close_reading_status -q` first failed because `gene_family_pangenome_summary` and other standard plots still used `template-guided close reading`; it passed after tightening the remaining standard plot reading statuses.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --run-promoter-cis --promoter-cis-elements tests/fixtures/promoter_cis/plantcare.tsv --run-ppi --ppi-edges tests/fixtures/ppi/ppi_edges.tsv --ppi-nodes tests/fixtures/ppi/ppi_nodes.tsv --expression-matrix tests/fixtures/expression/family_expression.tsv --expression-metadata tests/fixtures/expression/sample_metadata.tsv --outdir results/nextflow_standard_feature_smoke` refreshed the standard report outputs.
- `python - <<'PY' ...` over `results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv` showed `rows 9` and `non_specific []`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests/test_build_figure_interpretations.py tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands tests/test_run_nextflow_standard_smoke.py -q` passed with 22 tests.
- `python -m pytest tests -q` passed with 370 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: d95d89c99673680311175d27e2210617666e7865
- message: feat: require standard figure-specific readings
- files: figure interpretation builder, standard report/documentation tests, release audit, history

Next:
- Continue checking final report semantics and delivery surfaces against the full objective; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 04:45 - Split standard family-information figure readings

Context:
- The active `/goal` requires the final report to include close reading for every figure.
- The standard publication report already passed structural audit, but `family_counts` and `gene_family_info_summary` shared the same family copy-number interpretation.
- This made the simple member-count plot and the richer gene-family information panel too hard to distinguish in paper-style reporting.

Decisions:
- Keep the generic `family` template for unspecified family plots.
- Add figure-specific templates for `family_counts` and `gene_family_info_summary`.
- Restrict `gene_family_info_summary` matching to the plot key so `gene_family_pangenome_summary` still uses the pangenome template even when it shares the same PDF output path.
- Document the standard family-information close-reading contract in `docs/release_audit.md`.

Added:
- Dedicated close-reading template for the family member count overview.
- Dedicated close-reading template for the gene family information and dosage-balance summary.
- Tests requiring `family_counts` and `gene_family_info_summary` to have distinct close-reading templates.

Modified:
- `bin/genefam/build_figure_interpretations.py`
- `tests/test_build_figure_interpretations.py`
- `tests/test_release_audit_docs.py`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_figure_interpretations.py::test_standard_family_count_and_gene_family_info_have_distinct_close_readings -q` first failed because both plots still used the generic family copy-number template; it passed after adding the two specific templates and narrowing `gene_family_info_summary` matching to the exact plot key.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --run-promoter-cis --promoter-cis-elements tests/fixtures/promoter_cis/plantcare.tsv --run-ppi --ppi-edges tests/fixtures/ppi/ppi_edges.tsv --ppi-nodes tests/fixtures/ppi/ppi_nodes.tsv --expression-matrix tests/fixtures/expression/family_expression.tsv --expression-metadata tests/fixtures/expression/sample_metadata.tsv --outdir results/nextflow_standard_feature_smoke` refreshed the standard report outputs.
- `rg -n "Family member count overview|Gene family information and dosage-balance summary|figure-specific close reading; validate selected species|figure-specific close reading; validate species order" results/nextflow_standard_feature_smoke/standard/report/final_report.md results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv` showed distinct report sections for the two standard family-information figures.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests/test_build_figure_interpretations.py tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands tests/test_run_nextflow_standard_smoke.py -q` passed with 21 tests.
- `python -m pytest tests -q` passed with 369 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: dcd4a3d24f10931f3ea823b1399991fdd1b3a509
- message: feat: split standard family figure readings
- files: figure interpretation builder, standard report/documentation tests, release audit, history

Next:
- Continue tightening any remaining standard visualization interpretations that are still template-guided rather than figure-specific; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 04:38 - Add figure-specific WGD plot close readings

Context:
- The active `/goal` requires paper-level reports with close reading for every figure, including WGD/evolution figures.
- The WGD report already passed publication audit, but `ks_distribution`, `duplicate_type_kaks`, and `pangenome_kaks` shared one generic Ka/Ks interpretation template.
- That was acceptable structurally but weak for a paper-style result package where each WGD figure should explain its own evidence layer.

Decisions:
- Keep the generic `kaks` template for unspecific Ka/Ks plots.
- Add figure-specific templates for `ks_distribution`, `duplicate_type_kaks`, and `pangenome_kaks` before the generic Ka/Ks matcher.
- Make each WGD figure point to its own QC tables, method/software, reproducibility command, and interpretation status.
- Document the WGD close-reading contract in `docs/release_audit.md`.

Added:
- Dedicated close-reading template for Ks distribution and named WGD-layer support.
- Dedicated close-reading template for duplicate-type grouped Ka/Ks selection.
- Dedicated close-reading template for pangenome-class grouped Ka/Ks selection.
- Tests requiring WGD Ka/Ks plots to have distinct figure-specific interpretations.

Modified:
- `bin/genefam/build_figure_interpretations.py`
- `tests/test_build_figure_interpretations.py`
- `tests/test_release_audit_docs.py`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_figure_interpretations.py::test_wgd_kaks_plots_have_figure_specific_close_reading_templates -q` first failed because the WGD plots used the generic `Ka/Ks and Ks distribution overview` template; it passed after adding the specific templates and matcher order.
- `python -m pytest tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands -q` first failed because release audit did not document WGD figure-specific close reading; it passed after updating the document.
- `python -m pytest tests/test_build_figure_interpretations.py tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands tests/test_run_nextflow_wgd_smoke.py -q` passed with 9 tests.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke` refreshed the WGD report outputs.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` exited 0 and reported `Passed: 5`, `Failed: 0`, `Complete: true`.
- `rg -n "Ks distribution and named|Duplicate-type grouped|Pangenome-class grouped|figure-specific close reading|run_duplicate_type_kaks_smoke|run_pangenome_kaks_smoke" results/nextflow_wgd_smoke/wgd/report/final_report.md results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv` showed the three WGD figure-specific interpretation sections in the final report and TSV.
- `python -m pytest tests -q` passed with 368 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: f7b134278cdfac618fdcddf79114fd8958977a73
- message: feat: add wgd figure-specific readings
- files: figure interpretation builder, WGD report/documentation tests, release audit, history

Next:
- Continue tightening publication-level report semantics for any remaining figure families with overly generic interpretation text; Docker/Apptainer profile verification remains the final external runtime step.

## 2026-06-27 04:31 - Surface final packaging blocker in delivery bundle

Context:
- The active `/goal` asks for a paper-level visualization package and a perfect MVP acceptance surface while keeping Docker/Apptainer packaging as the final stage.
- The release/objective evidence already showed the analysis-flow MVP was release-ready with zero required failures, but the remaining Docker/Apptainer blocker was only embedded inside the objective-audit note.
- A user-facing delivery bundle should expose that final blocker as a stable machine-readable row.

Decisions:
- Keep Docker/Apptainer profile smoke checks optional until local container runtimes are installed or exposed.
- Add a dedicated `status/final_stage_blocker` row to the delivery manifest, derived from objective-audit rows with `blocked` or `missing` status.
- Preserve `objective_audit` as the full evidence pointer and use `final_stage_blocker` as the concise handoff signal.
- Document the new row in README and release audit so humans and scripts both know where to inspect the final-stage packaging state.

Added:
- Delivery manifest status row: `final_stage_blocker`.
- Tests requiring `final_stage_blocker` in the generated delivery TSV/Markdown, README, and release audit.

Modified:
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `README.md`
- `docs/release_audit.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index -q` first failed because the delivery manifest did not include `status/final_stage_blocker`; it passed after adding the manifest row.
- `python -m pytest tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report -q` first failed because README and release audit did not document `final_stage_blocker`; it passed after updating the docs.
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report -q` passed with 3 tests.
- `python bin/genefam/run_delivery_bundle.py --outdir results/delivery_bundle` refreshed the delivery bundle, and `rg -n "final_stage_blocker|Docker/Apptainer reproducibility|release_ready" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md` showed `status	final_stage_blocker	blocked	results/objective_audit/objective_audit.md	Docker/Apptainer reproducibility`.
- `python -m pytest tests -q` passed with 367 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 45`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.

Commit:
- hash: bc265500f30fac405d8c2418148b85ca92f8084c
- message: feat: surface final packaging blocker
- files: delivery bundle builder, delivery/docs tests, README, release audit, history

Next:
- When Docker/Apptainer are available, run `bash results/readiness/runtime_bootstrap.sh`, rerun the container profile smokes, and refresh the release gate so `final_stage_blocker` can move away from `blocked`.

## 2026-06-27 03:45 - Wire YAML species order into Nextflow standard smoke

Context:
- The active `/goal` requires YAML-driven parameters and all paper-level figure modules to be wired through Nextflow, report indices, final reports, smoke tests, and release checks.
- The previous change added optional species-tree order support for large-scale copy-number plots, but the standard Nextflow smoke wrapper only read identification/dev flags from YAML.
- This left the new `plotting.gene_family_species_order` setting under-verified as a YAML-driven workflow parameter.

Decisions:
- Add a small fixture species-order table and reference it from `configs/example.config.yaml` so the default standard smoke exercises YAML-driven copy-number ordering.
- Make `run_nextflow_standard_smoke.py` read `plotting.gene_family_species_order` from YAML and pass it as `--gene_family_species_order` to Nextflow.
- Resolve relative YAML paths to absolute paths before passing them into Nextflow, because processes execute inside `work/` directories where repo-relative paths are otherwise invalid.
- Treat gene-family information/copy-number tables and plots as required standard Nextflow smoke outputs, not incidental published files.

Added:
- `tests/fixtures/species_order/species_tree_order.tsv`
- Tests for YAML-driven species-order parameter extraction, absolute path resolution, command construction, and required gene-family info outputs.

Modified:
- `bin/genefam/run_nextflow_standard_smoke.py`
- `configs/example.config.yaml`
- `tests/test_run_nextflow_standard_smoke.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_nextflow_standard_smoke.py::test_build_nextflow_command_can_pass_yaml_species_order_for_copy_number_plots tests/test_run_nextflow_standard_smoke.py::test_load_standard_params_reads_yaml_species_order_for_copy_number_plots tests/test_run_nextflow_standard_smoke.py::test_load_standard_params_reads_yaml_tool_and_mock_flags -q` first failed because the wrapper did not accept or read `gene_family_species_order`; it passed after adding the YAML mapping.
- `python -m pytest tests/test_run_nextflow_standard_smoke.py::test_expected_published_outputs_cover_standard_user_results -q` first failed because standard smoke did not require gene-family info/copy-number outputs; it passed after adding those outputs to the expected list.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` first failed because a repo-relative species-order path was evaluated inside a Nextflow `work/` directory; it passed after resolving YAML paths to absolute paths.
- `cat results/nextflow_standard_smoke/standard/tables/gene_family_species_order.tsv` showed `Brassica_rapa` and `Arabidopsis_thaliana` as `order_source=external`, proving the YAML-driven species-order table reached the standard Nextflow branch.
- `python bin/genefam/validate_config.py configs/example.config.yaml --check-paths` printed `Configuration OK`.
- `python -m pytest tests -q` passed with 362 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 44`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `results/publication_report_audit/publication_report_audit.md` reports `Passed: 4`, `Failed: 0`, and `Complete: true`.

Commit:
- hash: 0642c5718fd70f1b44cab2cc0ee0395c2b420951
- message: test: require yaml species order in standard smoke
- files: standard smoke wrapper, example YAML, species-order fixture, standard smoke tests, history

Next:
- Continue final acceptance hardening and, when Docker/Apptainer are available, run `bash results/readiness/runtime_bootstrap.sh` followed by the container profile smokes and release gate.

## 2026-06-27 03:36 - Add external species-tree order for large-scale copy-number plots

Context:
- The active `/goal` requires large-scale, multi-species gene-family copy-number visualizations aligned with the `Reference/` paper examples.
- `docs/reference_plotting_reuse.md` still marked large-scale copy-number/expansion plotting as `partial` because species-tree ordered large-scale layouts were not yet supported.
- The existing gene-family information plot ordered species only by copy-number rank, which is useful for summary plots but not enough for paper-style broad species comparisons.

Decisions:
- Add an optional species-tree order table for gene-family information plots instead of replacing the default copy-number ranking behavior.
- Preserve default behavior when no external order is provided, with `order_source=copy_number`.
- When an external species order is provided, keep listed species in external order and append selected but unlisted species by copy-number rank with `order_source=copy_number_append`.
- Record optional `clade` labels in `gene_family_species_order.tsv` so report-ready copy-number figures can carry tree/clade context.
- Guard the Nextflow shell wrapper against `params.gene_family_species_order = null`, because Nextflow interpolates that value as the string `null` inside process scripts.

Added:
- Optional `--species-order` input for `bin/genefam/build_gene_family_info.py`.
- `clade` and `order_source` columns in `gene_family_species_order.tsv`.
- `params.gene_family_species_order = null` in `workflows/nextflow.config`.
- `plotting.gene_family_species_order` example in `configs/advanced_modules.example.yaml`.
- Input-contract documentation for the large-scale copy-number species order table.
- Tests for external species-tree ordering, appended unlisted species, Nextflow null guarding, config path validation, smoke output ordering, and report-index wording.

Modified:
- `bin/genefam/build_gene_family_info.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_gene_family_info_smoke.py`
- `bin/genefam/validate_config.py`
- `configs/advanced_modules.example.yaml`
- `docs/input_contract.md`
- `docs/reference_plotting_reuse.md`
- `tests/test_build_gene_family_info.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_run_gene_family_info_smoke.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_validate_config.py`
- `tests/test_workflow_modules.py`
- `workflows/modules/plots.nf`
- `workflows/nextflow.config`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_gene_family_info.py::test_build_gene_family_info_tables_uses_external_species_order_for_large_scale_plots tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin -q` first failed because the builder did not accept `species_order_records` and the Nextflow module did not pass optional species order.
- `python -m pytest tests/test_run_gene_family_info_smoke.py::test_run_gene_family_info_smoke_writes_tables_and_plots -q` first failed because the smoke runner still wrote copy-number-ranked order; it passed after adding a demo `species_tree_order.tsv`.
- `python -m pytest tests/test_validate_config.py::test_validate_config_checks_gene_family_species_order_path_when_provided -q` first failed because `validate_config.py` did not check `plotting.gene_family_species_order`; it passed after adding the path check.
- `python -m pytest tests/test_standard_branch_report_index.py::test_build_standard_report_index_cli_can_write_published_paths -q` first failed because the report index still described species order as copy-number-only; it passed after updating the description.
- `python bin/genefam/run_gene_family_info_smoke.py --r-bin /usr/local/bin/R --outdir results/gene_family_info_smoke` generated `gene_family_species_order.tsv`, `gene_family_info_summary.pdf`, and `gene_family_info_summary.png`; the order table contains `Osa/Ath/Bra` as `external` and `Bna` as `copy_number_append`.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke_debug` first failed because `params.gene_family_species_order = null` was interpolated as `--species-order null`; it passed after adding the null guard.
- `python -m pytest tests -q` passed with 359 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 44`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `results/publication_report_audit/publication_report_audit.md` reports `Passed: 4`, `Failed: 0`, and `Complete: true`.

Commit:
- hash: aed616ba98df1a950477a5d7c2fab68a07fc72e5
- message: feat: add species-tree order for copy-number plots
- files: gene-family info builder/smoke, Nextflow plot module/config, report index, validation, docs, tests, history

Next:
- Continue final acceptance hardening and, when Docker/Apptainer are available, run `bash results/readiness/runtime_bootstrap.sh` followed by the container profile smokes and release gate.

## 2026-06-27 03:21 - Document publication audit in README acceptance flow

Context:
- The active `/goal` requires paper-level visualization/report closure and a perfect MVP acceptance surface before final Docker/Apptainer packaging.
- The English README already listed the publication report audit as an output to inspect, but the shortest local acceptance entrypoint still described only release, quickstart, and delivery-bundle refresh steps.
- The Chinese README had a publication audit section but did not point users to the local acceptance script or local acceptance summary.

Decisions:
- Treat `bash scripts/run_local_acceptance.sh` as the single user-facing local MVP acceptance entrypoint in both English and Chinese docs.
- Make the README contract explicit that local acceptance refreshes `results/publication_report_audit/publication_report_audit.md` and indexes it through `results/local_acceptance/local_acceptance_summary.md`.
- Add tests for the README acceptance wording so future edits cannot accidentally drop the publication-report audit evidence chain.

Added:
- A Chinese README section for the local acceptance entrypoint and publication audit summary.
- README tests covering the publication-report audit acceptance wording in English and Chinese.

Modified:
- `README.md`
- `README.zh-CN.md`
- `tests/test_runtime_environment_files.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report -q` first failed because the English README did not describe publication-report audit as part of local acceptance, then passed after the README update.
- `python -m pytest tests/test_runtime_environment_files.py::test_chinese_readme_points_to_publication_audit_acceptance -q` first failed because the Chinese README did not mention `bash scripts/run_local_acceptance.sh`, then passed after the README update.
- `python -m pytest tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report tests/test_runtime_environment_files.py::test_chinese_readme_points_to_publication_audit_acceptance -q` passed with 2 tests.
- `python -m pytest tests -q` passed with 357 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 with `Passed: 44`, `Failed: 2`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`; the remaining optional failures are Docker and Apptainer profile smokes because those runtimes are not installed/exposed.
- `results/publication_report_audit/publication_report_audit.md` reports `Passed: 4`, `Failed: 0`, and `Complete: true`.

Commit:
- hash: 6cc9a2c935d780264b2e14d042e3fb15e6ddfd36
- message: docs: document publication audit acceptance flow
- files: README acceptance wording, Chinese README local acceptance entrypoint, README tests, history

Next:
- Continue toward final packaging by installing/exposing Docker and Apptainer or running `bash results/readiness/runtime_bootstrap.sh`, then rerun the container profile smokes and release gate.

## 2026-06-27 00:35 - Add per-gene tree feature architecture tracks

Context:
- The active `/goal` requires tree + motif + gene structure + domain visualizations aligned with `Reference/Long_Weixiong_20240323_1_GDSL/R/6.tree.R`.
- The existing tree feature matrix and plot were already tree-ordered, but still relied on global motif summary statistics and did not expose per-gene motif/domain architecture tracks.

Decisions:
- Keep the existing `tree_feature_matrix.tsv` output and add architecture columns instead of introducing a parallel matrix.
- Summarize motif catalog size as unique motif IDs while preserving total motif site counts across all motif rows.
- Support per-gene motif rows when the motif table includes `gene_id`, `motif_id`, and optional `start/end`; keep old motif-summary-only inputs compatible.
- Support domain architecture labels from HMM/domain rows using `hmm_id`, optional alignment/domain coordinates, and `domain_coverage`.
- Enhance the R plot with architecture labels while preserving the existing PDF/PNG output names and Nextflow/report wiring.

Added:
- none

Modified:
- `bin/genefam/build_tree_feature_matrix.py`
- `bin/genefam/run_tree_feature_smoke.py`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `scripts/plot_tree_features.R`
- `tests/test_build_tree_feature_matrix.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_tree_feature_smoke.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_tree_feature_matrix.py tests/test_run_tree_feature_smoke.py tests/test_reference_plotting_reuse.py -q` first failed because `motif_architecture` and `domain_architecture` were not present, then passed after adding per-gene architecture columns and plot support.
- `python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke` generated `tree_feature_matrix.tsv`, `tree_features.pdf`, and `tree_features.png`.
- `python -m pytest tests/test_build_tree_feature_matrix.py tests/test_run_tree_feature_smoke.py tests/test_reference_plotting_reuse.py tests/test_release_audit_docs.py -q` passed with 5 tests after release-audit documentation was updated.
- `python -m pytest tests -q` passed with 338 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because readiness/Docker/Apptainer remain unavailable, but the release matrix stayed at `passed=40 failed=3`; `tree feature visualization smoke` passed and `results/tree_feature_smoke/tables/tree_feature_matrix.tsv` contains `motif_architecture` and `domain_architecture`.

Commit:
- hash: 44e624f
- message: feat: add per-gene tree feature architecture tracks
- files: tree feature matrix builder, tree feature plot, smoke defaults, release/reference docs, tests, history

Next:
- Continue paper-level refinement for MCScanX/circlize duplicate tracks, WGD peak/layer annotations, promoter dot-style refinement, copy-number species ordering, and final container/runtime unblocking.

## 2026-06-27 00:24 - Add annotated expression heatmap workflow

Context:
- The active `/goal` requires RNA-seq expression heatmaps aligned with `Reference/Long_Weixiong_20240323_1_GDSL/R/12.rnaseq.R`.
- The pipeline previously subset expression matrices and had a basic base-R heatmap, but lacked sample metadata, replicate grouping, expression summary/QC tables, PNG output, and formal Nextflow/report/release wiring.

Decisions:
- Add a reusable expression summary builder that keeps the original family expression table while producing report-ready annotation and summary tables.
- Treat sample metadata as optional: when provided, `sample_id` must match expression columns and `group` controls replicate averaging; when absent, metadata is generated from expression columns.
- Keep the R plotting implementation dependency-light and compatible with `/usr/local/bin/R`, while adding PDF/PNG output and a top-responsive-gene summary panel.
- Wire `PLOT_EXPRESSION_HEATMAP` into the standard Nextflow branch whenever `params.expression_matrix` is provided, with optional `params.expression_metadata`.

Added:
- `bin/genefam/build_expression_summary.py`
- `bin/genefam/run_expression_heatmap_smoke.py`
- `tests/fixtures/expression/sample_metadata.tsv`
- `tests/test_build_expression_summary.py`
- `tests/test_run_expression_heatmap_smoke.py`

Modified:
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_release_checks.py`
- `bin/genefam/run_standard_smoke.py`
- `bin/genefam/validate_config.py`
- `configs/advanced_modules.example.yaml`
- `docs/input_contract.md`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `scripts/plot_expression_heatmap.R`
- `tests/test_audit_objective_completion.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_run_standard_smoke.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_validate_config.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`
- `workflows/nextflow.config`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_expression_summary.py tests/test_run_expression_heatmap_smoke.py -q` first failed because `bin.genefam.build_expression_summary` did not exist, then passed with 3 tests after adding the builder, smoke runner, and R plot.
- `python -m pytest tests/test_run_standard_smoke.py tests/test_workflow_modules.py tests/test_standard_branch_report_index.py tests/test_run_release_checks.py tests/test_validate_config.py tests/test_reference_plotting_reuse.py tests/test_release_audit_docs.py tests/test_build_expression_summary.py tests/test_run_expression_heatmap_smoke.py -q` passed with 105 tests after standard-branch/report/release/docs wiring.
- `python bin/genefam/run_expression_heatmap_smoke.py --expression tests/fixtures/expression/family_expression.tsv --metadata tests/fixtures/expression/sample_metadata.tsv --r-bin /usr/local/bin/R --outdir results/expression_heatmap_smoke` generated expression annotation tables and `expression_heatmap.pdf/png`.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --expression-matrix tests/fixtures/expression/family_expression.tsv --expression-metadata tests/fixtures/expression/sample_metadata.tsv --r-bin /usr/local/bin/R --outdir results/standard_expression_smoke` generated `family_expression.tsv`, expression annotation/summary tables, `expression_heatmap.pdf/png`, and report-index entries.
- `/Users/liuyue/miniforge3/bin/conda run -n GeneFamilyFlow nextflow run workflows/main.nf -c workflows/nextflow.config -profile activated --config configs/example.config.yaml --groups configs/species_groups.yaml --run_identification true --use_hmmer true --use_diamond true --final_rule intersection --mock_external_tools true --standard_stop_after_family_candidates false --mock_evidence_dir tests/fixtures/mock_evidence --expression_matrix tests/fixtures/expression/family_expression.tsv --expression_metadata tests/fixtures/expression/sample_metadata.tsv --outdir results/nextflow_standard_expression_smoke` passed and executed `PLOT_EXPRESSION_HEATMAP`.
- `python -m pytest tests -q` passed with 338 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because readiness/Docker/Apptainer remain unavailable, but improved the release matrix to `passed=40 failed=3`; `standard branch expression smoke` and `expression heatmap visualization smoke` passed.

Commit:
- hash: 6768692
- message: feat: add annotated expression heatmap workflow
- files: expression summary builder, R plot enhancement, smoke runner, standard Nextflow/report/release/docs/tests/history

Next:
- Continue paper-level refinement for tree/motif/gene-structure/domain tracks, MCScanX/circlize duplicate tracks, WGD peak annotations, and final container/runtime unblocking.

## 2026-06-27 00:12 - Add duplicate-type Ka/Ks visualization for WGD branch

Context:
- The active `/goal` requires paper-level visualization aligned with `Reference/Long_Weixiong_20240323_1_GDSL/R/9.mcscanx_KaKs.R`.
- The WGD branch already generated MCScanX/KaKs handoff tables and a basic Ks distribution, but duplicate-type grouped Ka/Ks panels and summary/QC tables were still missing.

Decisions:
- Add a dedicated duplicate-type Ka/Ks table builder instead of overloading the generic Ks histogram.
- Classify each Ka/Ks pair by duplicate type: same-type pairs keep their duplicate class, cross-type pairs become `mixed`, and pairs missing duplicate evidence are written to a skipped-pair QC table.
- Use base R plotting for dependency-light PDF/PNG output with Ks box/point panels, Ka/Ks box/point panels, and pair-count bars.
- Wire the process into the WGD Nextflow branch after duplicate-type normalization so both prepared input and raw MCScanX/KaKs handoff modes get the same plot.

Added:
- `bin/genefam/build_duplicate_type_kaks.py`
- `bin/genefam/run_duplicate_type_kaks_smoke.py`
- `scripts/plot_duplicate_type_kaks.R`
- `tests/test_build_duplicate_type_kaks.py`
- `tests/test_run_duplicate_type_kaks_smoke.py`

Modified:
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/build_wgd_report_index.py`
- `bin/genefam/run_release_checks.py`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_wgd_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/duplication_retention.nf`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_duplicate_type_kaks.py tests/test_run_duplicate_type_kaks_smoke.py -q` first failed because `bin.genefam.build_duplicate_type_kaks` did not exist, then passed with 3 tests after adding the builder, smoke runner, and R plot.
- `python -m pytest tests/test_workflow_modules.py tests/test_wgd_report_index.py tests/test_run_release_checks.py tests/test_reference_plotting_reuse.py tests/test_release_audit_docs.py -q` first failed on missing WGD process/report/release/docs wiring, then passed after formal integration.
- `python bin/genefam/run_duplicate_type_kaks_smoke.py --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv --kaks-pairs examples/prepared_wgd_handoff/kaks_pairs.tsv --r-bin /usr/local/bin/R --outdir results/duplicate_type_kaks_smoke` generated duplicate-type Ka/Ks tables and `duplicate_type_kaks.pdf/png`.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke` passed and generated WGD duplicate-type Ka/Ks plots.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke` passed and generated raw MCScanX/KaKs duplicate-type Ka/Ks plots.
- `python -m pytest tests -q` passed with 331 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because runtime readiness and Docker/Apptainer smokes remain blocked, but the release matrix improved to `passed=39 failed=3`; the new `duplicate-type Ka/Ks visualization smoke` passed.

Commit:
- hash: dae8ba7
- message: feat: add duplicate type kaks visualization
- files: duplicate-type Ka/Ks builder, R plot, smoke runner, WGD Nextflow/report/release/docs/tests/history

Next:
- Continue Reference-level refinement with expression heatmap sample annotations, richer WGD peak/layer annotations, and final container/runtime unblocking after workflow development.

## 2026-06-27 00:01 - Add gene family information and copy-number visualization

Context:
- The active `/goal` requires Reference-level gene family information and large-scale copy-number visualizations.
- The pipeline already had a basic `family_counts.pdf`, but `docs/reference_plotting_reuse.md` still marked protein length, molecular weight, pI, hydrophobicity, and large-scale copy-number summaries as missing.

Decisions:
- Add a report-ready `gene_family_info_summary` figure instead of overloading the original simple `family_counts` barplot.
- Use existing standard-branch outputs as inputs: `family_counts.tsv` and `family_members.faa`.
- Compute per-species copy-number classes (`absent`, `single_copy`, `multi_copy`, `high_copy`), copy-number ranks, and percent-of-maximum values.
- Compute per-gene protein properties without new dependencies: protein length, approximate molecular weight, approximate pI, and GRAVY.
- Run the new module by default in the standard branch because it depends only on already-generated core outputs.

Added:
- `bin/genefam/build_gene_family_info.py`
- `bin/genefam/run_gene_family_info_smoke.py`
- `scripts/plot_gene_family_info.R`
- `tests/test_build_gene_family_info.py`
- `tests/test_run_gene_family_info_smoke.py`

Modified:
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_release_checks.py`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_gene_family_info.py tests/test_run_gene_family_info_smoke.py -q` first failed because `build_gene_family_info.py` and `run_gene_family_info_smoke.py` did not exist, then passed after adding the table builder, smoke runner, and R plot.
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_workflow_modules.py tests/test_run_release_checks.py tests/test_release_audit_docs.py tests/test_audit_objective_completion.py -q` first failed on the new report/workflow/release/audit expectations, then passed with 85 tests after formal wiring.
- `/Users/liuyue/miniforge3/bin/conda run -n GeneFamilyFlow nextflow run workflows/main.nf -c workflows/nextflow.config -profile activated --config configs/example.config.yaml --groups configs/species_groups.yaml --run_identification true --use_hmmer true --use_diamond true --final_rule intersection --mock_external_tools true --standard_stop_after_family_candidates false --mock_evidence_dir tests/fixtures/mock_evidence --outdir results/nextflow_standard_gene_family_info_smoke` passed and executed `PLOT_GENE_FAMILY_INFO`.
- `grep -n "gene_family\|Gene family" results/nextflow_standard_gene_family_info_smoke/report/report_index.tsv results/nextflow_standard_gene_family_info_smoke/report/plot_manifest.tsv results/nextflow_standard_gene_family_info_smoke/report/final_report.md results/nextflow_standard_gene_family_info_smoke/report/figure_interpretations.tsv` confirmed report index, plot manifest, final report, and figure interpretations include the new gene-family information tables and plots.
- `python -m pytest tests/test_build_gene_family_info.py tests/test_run_gene_family_info_smoke.py tests/test_standard_branch_report_index.py tests/test_workflow_modules.py tests/test_run_release_checks.py tests/test_release_audit_docs.py tests/test_audit_objective_completion.py tests/test_reference_plotting_reuse.py -q` passed with 88 tests.
- `python -m pytest tests -q` passed with 326 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker/Apptainer remain unavailable, but improved the release matrix to `Passed: 38`, `Required failed: 1`, `Optional failed: 2`; `gene family information visualization smoke` passed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` kept `paper-level visualization modules` as `achieved` with gene-family information included, and kept full objective incomplete only because Docker/Apptainer reproducibility is still blocked by missing runtime commands.

Commit:
- hash: befcf7e
- message: feat: add gene family info visualization
- files: gene family information table builder, R plotting script, smoke runner, Nextflow/report/release/docs/tests/history

Next:
- Continue Reference-level refinement with richer MCScanX/KaKs duplicate-type panels and expression heatmap sample annotations.

## 2026-06-26 23:47 - Add promoter cis-element visualization module

Context:
- The active `/goal` requires promoter cis-element visualization aligned with `Reference/Long_Weixiong_20240323_1_GDSL/R/10.promoter.R`.
- The pipeline already extracted promoter intervals and plotted generic feature summaries, but PlantCARE-style cis-element category matrices, top-element summaries, formal Nextflow wiring, and report-index entries were still missing.

Decisions:
- Add a standalone promoter cis-element module instead of mixing cis-element annotations into the promoter-length summary.
- Accept normalized TSV columns plus common PlantCARE-style aliases such as `Species`, `Gene ID`, `CAREs`, `Function`, and `Site`.
- Infer broad report categories when the input lacks a category column: `hormone_responsive`, `stress_responsive`, `light_responsive`, `growth_development`, `core_promoter`, or `other`.
- Expose the workflow as `--run_promoter_cis true --promoter_cis_elements <tsv>` and YAML validation as `modules.promoter_cis: true` with `promoter.cis_elements`.
- Add an objective-audit row for paper-level visualization modules so tree-feature, MCScanX/circlize, promoter cis-element, PPI, expression, and feature-summary figure coverage is explicitly tracked.

Added:
- `bin/genefam/build_promoter_cis_elements.py`
- `bin/genefam/run_promoter_cis_smoke.py`
- `scripts/plot_promoter_cis_elements.R`
- `tests/fixtures/promoter_cis/plantcare.tsv`
- `tests/test_build_promoter_cis_elements.py`
- `tests/test_run_promoter_cis_smoke.py`

Modified:
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_release_checks.py`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `schemas/config.schema.yaml`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_validate_config.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`
- `workflows/nextflow.config`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_promoter_cis_elements.py -q` first failed because `build_promoter_cis_elements.py` did not exist, then passed after adding normalization, category inference, gene-category matrix, and summary table generation.
- `python -m pytest tests/test_run_promoter_cis_smoke.py -q` first failed because `run_promoter_cis_smoke.py` did not exist, then passed after adding the smoke runner and `scripts/plot_promoter_cis_elements.R`.
- `python -m pytest tests/test_runtime_environment_files.py tests/test_validate_config.py tests/test_standard_branch_report_index.py tests/test_workflow_modules.py tests/test_run_release_checks.py -q` first failed on the new formal workflow/report/config expectations, then passed with 105 tests after wiring Nextflow, schema, validation, report index, and release checks.
- `python -m pytest tests/test_build_promoter_cis_elements.py tests/test_run_promoter_cis_smoke.py tests/test_release_audit_docs.py tests/test_reference_plotting_reuse.py -q` passed with 5 tests.
- `/Users/liuyue/miniforge3/bin/conda run -n GeneFamilyFlow nextflow run workflows/main.nf -c workflows/nextflow.config -profile activated --config configs/example.config.yaml --groups configs/species_groups.yaml --run_identification true --use_hmmer true --use_diamond true --final_rule intersection --mock_external_tools true --standard_stop_after_family_candidates false --mock_evidence_dir tests/fixtures/mock_evidence --run_promoter_cis true --promoter_cis_elements tests/fixtures/promoter_cis/plantcare.tsv --outdir results/nextflow_standard_promoter_cis_smoke` passed and executed `PLOT_PROMOTER_CIS_ELEMENTS`.
- `grep -n "promoter_cis\|Promoter cis" results/nextflow_standard_promoter_cis_smoke/report/report_index.tsv results/nextflow_standard_promoter_cis_smoke/report/plot_manifest.tsv results/nextflow_standard_promoter_cis_smoke/report/final_report.md results/nextflow_standard_promoter_cis_smoke/report/figure_interpretations.tsv` confirmed report index, plot manifest, final report, and figure interpretations include promoter cis-element tables and plots.
- `python -m pytest tests -q` passed with 323 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker/Apptainer remain unavailable, but improved the release matrix to `Passed: 37`, `Required failed: 1`, `Optional failed: 2`; `promoter cis-element visualization smoke` passed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` wrote `paper-level visualization modules` as `achieved` and kept the full objective incomplete only because Docker/Apptainer reproducibility is still blocked by missing runtime commands.

Commit:
- hash: dfa6f8b
- message: feat: add promoter cis element visualization
- files: promoter cis-element table builder, R plotting script, smoke runner, fixture, Nextflow/report/release/schema/docs/tests/history

Next:
- Continue Reference-level refinement with copy-number/gene-family information plots and richer MCScanX/KaKs duplicate-type panels.

## 2026-06-26 23:28 - Add ggNetView PPI plotting module

Context:
- The active `/goal` requires `ggNetView` PPI visualization, not only dependency readiness.
- The Reference PPI script builds edge/node annotations, derives hubs/modules, and renders `ppi_ggnetview.pdf`; GeneFam-Pipeline previously only checked whether `ggNetView` was installed.

Decisions:
- Add a reusable PPI table builder that normalizes edge tables, constructs node annotations, and ranks hub genes by weighted degree.
- Keep PPI plotting explicitly based on `ggNetView`; if the package is missing, write `missing_dependency` status and explicit placeholder plots instead of silently using another network library.
- Expose PPI as an optional standard-branch Nextflow module controlled by `--run_ppi true --ppi_edges <tsv> [--ppi_nodes <tsv>]`.
- Add YAML/input-contract validation for `modules.ppi` with `ppi.edges` and optional `ppi.nodes`.

Added:
- `bin/genefam/build_ppi_tables.py`
- `bin/genefam/run_ppi_ggnetview_plot_smoke.py`
- `scripts/plot_ppi_ggnetview.R`
- `tests/fixtures/ppi/ppi_edges.tsv`
- `tests/fixtures/ppi/ppi_nodes.tsv`
- `tests/test_build_ppi_tables.py`
- `tests/test_run_ppi_ggnetview_plot_smoke.py`

Modified:
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_release_checks.py`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `schemas/config.schema.yaml`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_validate_config.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`
- `workflows/nextflow.config`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_ppi_tables.py tests/test_run_ppi_ggnetview_plot_smoke.py -q` first failed because the PPI table builder did not exist, then passed after adding the builder, ggNetView plot script, and smoke runner.
- `python -m pytest tests/test_validate_config.py tests/test_runtime_environment_files.py tests/test_build_ppi_tables.py tests/test_run_ppi_ggnetview_smoke.py tests/test_run_ppi_ggnetview_plot_smoke.py tests/test_standard_branch_report_index.py tests/test_workflow_modules.py tests/test_run_release_checks.py tests/test_release_audit_docs.py tests/test_reference_plotting_reuse.py -q` passed with 109 tests after adding YAML/input-contract validation and report wiring.
- `/Users/liuyue/miniforge3/bin/conda run -n GeneFamilyFlow nextflow run workflows/main.nf -c workflows/nextflow.config -profile activated --config configs/example.config.yaml --groups configs/species_groups.yaml --run_identification true --use_hmmer true --use_diamond true --final_rule intersection --mock_external_tools true --standard_stop_after_family_candidates false --mock_evidence_dir tests/fixtures/mock_evidence --run_ppi true --ppi_edges tests/fixtures/ppi/ppi_edges.tsv --ppi_nodes tests/fixtures/ppi/ppi_nodes.tsv --outdir results/nextflow_standard_ppi_smoke` passed after rerunning through the full `GeneFamilyFlow` environment.
- `grep -n "ppi_\|PPI\|ggNetView" results/nextflow_standard_ppi_smoke/report/report_index.tsv results/nextflow_standard_ppi_smoke/report/plot_manifest.tsv results/nextflow_standard_ppi_smoke/report/final_report.md results/nextflow_standard_ppi_smoke/report/figure_interpretations.tsv` confirmed PPI edge/node/hub/status tables, PDF/PNG plots, plot manifest, final report, software version table, and figure interpretation all include the PPI module.
- `cat results/nextflow_standard_ppi_smoke/tables/ppi_ggnetview_status.tsv` reported `ppi_ggnetview_plot ready ggNetView 0.2.0`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker/Apptainer remain unavailable, but improved the release matrix to `Passed: 36`, `Required failed: 1`, `Optional failed: 2`; both `PPI ggNetView smoke` and `PPI ggNetView plot smoke` passed.

Commit:
- hash: 92e4a2e
- message: feat: add ggnetview ppi plotting module
- files: PPI table builder, ggNetView plot script, PPI smoke runner, fixtures, Nextflow standard PPI wiring, report index/docs/tests/history

Next:
- Continue paper-level visualization refinement with promoter cis-element category plots, copy-number/gene-family information summaries, and richer MCScanX/KaKs panels.

## 2026-06-26 23:06 - Add tree motif gene-structure domain composite plot

Context:
- The active `/goal` requires paper-level visualization aligned with the two `Reference/` papers.
- The previous alignment matrix still marked the tree + motif + gene structure + domain figure as missing, even though the standard branch already produced phylogeny, motif summary, gene-structure, and optional domain evidence.

Decisions:
- Add a formal `tree_features` figure as the first workflow-native version of the Reference-style tree/motif/gene-structure/domain composite.
- Keep the first implementation deterministic and large-family friendly: tree-ordered rows plus aligned feature tracks for gene length, exon/CDS counts, domain count, best domain coverage, and motif catalog summary.
- Treat per-gene MEME motif occurrence tracks and richer domain architecture glyphs as the next refinement, because the current MEME parser records motif catalog metadata rather than per-gene motif placements.
- Make the tree feature smoke independent and deterministic for release checks, while using Nextflow standard smoke to prove formal workflow integration.

Added:
- `bin/genefam/build_tree_feature_matrix.py`
- `bin/genefam/run_tree_feature_smoke.py`
- `scripts/plot_tree_features.R`
- `tests/test_build_tree_feature_matrix.py`
- `tests/test_run_tree_feature_smoke.py`

Modified:
- `bin/genefam/build_figure_interpretations.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_release_checks.py`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `tests/test_build_figure_interpretations.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_tree_feature_matrix.py tests/test_run_tree_feature_smoke.py -q` first failed because the new module did not exist, then failed once more because Newick leaf parsing captured branch lengths with gene IDs, then passed with 3 tests after implementation.
- `python -m pytest tests/test_build_tree_feature_matrix.py tests/test_run_tree_feature_smoke.py tests/test_release_audit_docs.py tests/test_reference_plotting_reuse.py tests/test_build_figure_interpretations.py tests/test_standard_branch_report_index.py tests/test_workflow_modules.py tests/test_run_release_checks.py -q` passed with 70 tests.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` passed and produced `results/nextflow_standard_smoke/standard/tables/tree_feature_matrix.tsv`, `results/nextflow_standard_smoke/standard/plots/tree_features.pdf`, and `results/nextflow_standard_smoke/standard/plots/tree_features.png`.
- `grep -n "tree_feature\|tree_features\|Tree, motif" results/nextflow_standard_smoke/standard/report/report_index.tsv results/nextflow_standard_smoke/standard/report/plot_manifest.tsv results/nextflow_standard_smoke/standard/report/final_report.md results/nextflow_standard_smoke/standard/report/figure_interpretations.tsv` confirmed report index, plot manifest, final report, and figure interpretations include the new figure.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --outdir results/nextflow_standard_feature_smoke` passed.
- `python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke` passed and wrote `tree_feature_matrix.tsv`, `tree_features.pdf`, and `tree_features.png`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker/Apptainer remain unavailable, but improved the release matrix to `Passed: 35`, `Required failed: 1`, `Optional failed: 2`; `tree feature visualization smoke` and `PPI ggNetView smoke` passed.

Commit:
- hash: 89cdb53
- message: feat: add tree feature composite visualization
- files: tree feature matrix builder, R plot script, smoke runner, Nextflow standard wiring, report index/interpretation updates, release docs/tests, history

Next:
- Continue paper-level visualization refinement by adding true per-gene motif occurrence tracks, richer domain architecture glyphs, and the full ggNetView PPI plotting module.

## 2026-06-26 22:48 - Add paper-level report interpretation and ggNetView readiness

Context:
- The user asked to align GeneFam-Pipeline with the visualization level of the two papers under `Reference/`, keep PPI visualization based on `ggNetView`, and make the final report interpret every figure while listing software and package versions.
- This step continued the analysis-workflow-first strategy; Docker/Apptainer packaging remains a final external-runtime phase.

Decisions:
- Treat software-version capture as report evidence: missing tools are recorded as `version_not_detected` instead of aborting the workflow.
- Add structured per-figure interpretation tables and Markdown so final reports can discuss each plot in a paper-like result-reading format.
- Keep `ggNetView` as the explicit PPI visualization dependency and add a readiness smoke that reports `ready` or `missing_dependency`.
- Wire the new report evidence into the formal Nextflow standard branch and `report_index.tsv`, not only into standalone helper scripts.

Added:
- `bin/genefam/collect_software_versions.py`
- `bin/genefam/build_figure_interpretations.py`
- `bin/genefam/run_ppi_ggnetview_smoke.py`
- `tests/test_collect_software_versions.py`
- `tests/test_build_figure_interpretations.py`
- `tests/test_run_ppi_ggnetview_smoke.py`
- `tests/test_reference_plotting_reuse.py`

Modified:
- `bin/genefam/assemble_report.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_release_checks.py`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `tests/test_assemble_report.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/standard_postprocess.nf`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_collect_software_versions.py -q` first failed because missing executables raised `FileNotFoundError`, then passed after recording them as `version_not_detected`.
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` passed with 6 tests.
- `python -m pytest tests/test_collect_software_versions.py tests/test_build_figure_interpretations.py tests/test_run_ppi_ggnetview_smoke.py tests/test_assemble_report.py tests/test_reference_plotting_reuse.py tests/test_release_audit_docs.py tests/test_run_release_checks.py::test_default_checks_include_ppi_ggnetview_smoke_after_feature_summary tests/test_standard_branch_report_index.py tests/test_workflow_modules.py -q` passed with 31 tests.
- `python bin/genefam/run_ppi_ggnetview_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_smoke` passed and reported `status ready` with `ggNetView` version `0.2.0`.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` first failed because version collection aborted when `iqtree2` was not found on PATH, then passed after missing tools were recorded without failing the workflow.
- `grep -n "Software Versions\|Figure Result Interpretations\|software_versions\|figure_interpretations" results/nextflow_standard_smoke/standard/report/final_report.md results/nextflow_standard_smoke/standard/report/report_index.tsv` confirmed the final report and report index include both new evidence tables.
- `python -m pytest -q` passed with 308 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker/Apptainer remain unavailable, but improved the release matrix to `Passed: 34`, `Required failed: 1`, `Optional failed: 2`; `PPI ggNetView smoke` passed, while `readiness audit`, `Docker profile smoke`, and `Apptainer profile smoke` are the remaining runtime blockers.

Commit:
- hash: cf7771f
- message: feat: add report interpretation and ggnetview readiness
- files: report interpretation/version scripts, ggNetView readiness smoke, Nextflow standard report wiring, release audit docs, tests, history

Next:
- Continue remaining paper-level visualization work by turning the current alignment matrix `partial` items into real plot modules, especially tree/motif/gene-structure/domain composite views and richer MCScanX/PPI visual outputs.

## 2026-06-26 20:02 - Add raw MCScanX/KaKs WGD handoff and report package polish

Context:
- The user asked to continue the `/goal` work on the next priority block: formal promoter/MCScanX/feature summary wiring, real MCScanX/KaKs end-to-end entry points, report-system upgrades, and visualization enhancements before container packaging.
- The standard visualization modules were already committed in `eaeee52`; this entry records the follow-up work for real MCScanX/KaKs WGD handoff, final-report structure, and Ka/Ks plot publication.

Decisions:
- Keep containerization out of scope for this step and continue improving the analysis workflow first.
- Add a raw MCScanX/KaKs handoff path while preserving the existing prepared-table WGD branch.
- Treat MCScanX `.collinearity` and KaKs_Calculator output as real upstream tool outputs that can be normalized into workflow-native tables.
- Upgrade final Markdown reports with executive summary, methods summary, result-package inventory, figure inventory, and reproducibility notes.
- Publish WGD Ka/Ks distribution plots as both PDF and PNG.

Added:
- `bin/genefam/build_mcscanx_kaks_handoff.py`
- `tests/test_build_mcscanx_kaks_handoff.py`

Modified:
- `workflows/nextflow.config`
- `workflows/main.nf`
- `workflows/modules/duplication_retention.nf`
- `workflows/modules/plots.nf`
- `bin/genefam/run_nextflow_wgd_smoke.py`
- `bin/genefam/run_release_checks.py`
- `bin/genefam/assemble_report.py`
- `bin/genefam/build_wgd_report_index.py`
- `scripts/plot_kaks.R`
- `README.md`
- `README.zh-CN.md`
- `docs/release_audit.md`
- related tests for workflow wiring, WGD smoke, release checks, reports, report index, runtime params, and release audit docs
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_mcscanx_kaks_handoff.py -q` first failed because the handoff builder did not exist, then passed with 2 tests after implementation.
- `python -m pytest tests/test_runtime_environment_files.py::test_nextflow_config_has_container_profiles tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes -q` first failed because raw MCScanX/KaKs params and Nextflow process wiring were missing, then passed after adding `PREPARE_MCSCANX_KAKS_HANDOFF`.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke` initially failed because the new script could not import the local `bin` package from a Nextflow work directory, then passed after adding repo-root path bootstrapping.
- `python -m pytest tests/test_assemble_report.py -q` first failed because the report lacked executive summary, methods summary, result-package inventory, figure inventory, and reproducibility note; it passed after upgrading `assemble_report.py`.
- `python -m pytest tests/test_wgd_report_index.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes tests/test_run_nextflow_wgd_smoke.py -q` first failed because WGD Ka/Ks PNG output and WGD `PLOT_KAKS` wiring were missing, then passed after adding the visualization outputs.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke` passed after the report and plot upgrades.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke` passed after the report and plot upgrades.
- `python -m pytest tests -q` passed with 302 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`, as expected while Docker/Apptainer remain unavailable.
- `results/release_checks/release_checks.md` reports `Passed: 33`, `Required failed: 1`, `Optional failed: 2`; `Nextflow raw MCScanX/KaKs WGD smoke` passed.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 7c95203
- message: feat: add raw mcscanx kaks wgd handoff
- files: raw MCScanX/KaKs handoff builder, Nextflow WGD raw input wiring, WGD Ka/Ks plotting, report package upgrade, docs, tests, history

Next:
- Continue with any remaining paper-style report exports and broader visualization polish, while leaving Docker/Apptainer packaging for the final phase.

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
- hash: dd444ab4f194e6c158dc109bd12439d9d93f2a9d
- message: feat: add prepared WGD handoff release gate
- files: prepared WGD handoff release wrapper, release checks, release audit docs, tests, history

Next:
- Continue toward container-runtime verification when Docker or Apptainer is available; otherwise focus on reusable user-facing examples and documentation that are fully verifiable through `GeneFamilyFlow`.

## 2026-06-24 - Make WGD smoke commands copyable

Context:
- The WGD smoke wrappers executed commands correctly, but their TSV/Markdown command fields were rendered with simple space joining.
- `--wgd_event_args` contains spaces, so copied report commands could be split incorrectly by a shell.

Decisions:
- Render command strings with `shlex.join()` in the Nextflow WGD smoke wrapper and prepared WGD handoff wrapper.
- Keep subprocess execution list-based so runtime behavior is unchanged.
- Add tests that prove missing-Nextflow reports preserve a quoted, copyable `--wgd_event_args` value.

Added:
- `tests/test_run_prepared_wgd_handoff_example.py`

Modified:
- `HISTORY.md`
- `bin/genefam/run_nextflow_wgd_smoke.py`
- `bin/genefam/run_prepared_wgd_handoff_example.py`
- `tests/test_run_nextflow_wgd_smoke.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_nextflow_wgd_smoke.py tests/test_run_prepared_wgd_handoff_example.py -q` first failed because `--wgd_event_args` was not shell-quoted in generated TSV command fields.
- After switching command rendering to `shlex.join()`, the same targeted test command passed with 4 tests.
- `python -m pytest tests -q` passed with 153 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, prepared WGD handoff example, and runtime bootstrap plan passed.
- `results/example_prepared_wgd/prepared_wgd_handoff_example.tsv` now reports a shell-copyable command with the quoted `--wgd_event_args` value.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 6ec4fe4368d7472b403c8e3481bcdc0498f2e4b1
- message: fix: quote WGD smoke report commands
- files: WGD smoke command rendering, prepared WGD handoff command rendering, command-report tests, history

Next:
- Continue toward final runtime readiness; if Docker/Apptainer remain unavailable, keep strengthening user-facing examples, command reports, and release gates that are verifiable through `GeneFamilyFlow`.

## 2026-06-24 - Add final quickstart handoff

Context:
- The repository had detailed README and release-audit material, but not a short handoff document that tells a user which verified commands to run first.
- The final pipeline needs an easy morning entry point that connects release checks, the standard species-bank branch, and the prepared WGD event handoff.

Decisions:
- Add `docs/quickstart.md` as the shortest verified run path.
- Link the quickstart from README.
- Add release-audit evidence for the quickstart and tests to keep the handoff from drifting.
- Document the current Docker/Apptainer runtime gap without blocking `GeneFamilyFlow`-verified local usage.

Added:
- `docs/quickstart.md`
- `tests/test_quickstart_docs.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_quickstart_docs.py -q` first failed because `docs/quickstart.md` did not exist and README did not link it.
- After adding the quickstart and README link, `python -m pytest tests/test_quickstart_docs.py -q` passed with 2 tests.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not mention `docs/quickstart.md`.
- After adding the quickstart release-audit row, `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` passed with 3 tests.
- `python -m pytest tests -q` passed with 155 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, prepared WGD handoff example, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 54a8c305501c277fe24b1d40a04ab5f440e7d7c9
- message: docs: add verified quickstart handoff
- files: quickstart handoff doc, README link, release audit evidence, quickstart tests, history

Next:
- Continue toward final runtime readiness; if Docker/Apptainer remain unavailable, keep improving user-facing runnable paths and release evidence.

## 2026-06-24 - Add executable quickstart runner

Context:
- `docs/quickstart.md` described the shortest verified path, but users still had to run multiple commands and inspect separate outputs.
- The final handoff benefits from a single command that proves the standard species-bank branch and prepared WGD handoff can both run and emits a compact summary.

Decisions:
- Add `bin/genefam/run_quickstart.py` to run the standard branch smoke and prepared WGD handoff.
- Write `quickstart_summary.tsv` and `quickstart_summary.md` under the selected output directory.
- Add `quickstart handoff` to release checks before the machine readiness audit.
- Update quickstart and release-audit docs so the one-command handoff is discoverable.

Added:
- `bin/genefam/run_quickstart.py`
- `tests/test_run_quickstart.py`

Modified:
- `HISTORY.md`
- `bin/genefam/run_release_checks.py`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_quickstart.py -q` first failed because `bin/genefam/run_quickstart.py` did not exist.
- After adding the runner, `python -m pytest tests/test_run_quickstart.py -q` passed with 3 tests.
- `python -m pytest tests/test_run_release_checks.py -q` first failed because default release checks did not include `quickstart handoff`.
- After wiring release checks, `python -m pytest tests/test_run_release_checks.py -q` passed with 13 tests.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` first failed because docs did not mention `run_quickstart.py`.
- After updating quickstart and release audit docs, the same doc test command passed with 3 tests.
- `python bin/genefam/run_quickstart.py --conda-env GeneFamilyFlow --outdir results/quickstart` exited `0`.
- `results/quickstart/quickstart_summary.tsv` reports `standard_branch_smoke` and `prepared_wgd_handoff` as `passed`.
- `results/quickstart/standard_smoke/report/final_report.md`, `results/quickstart/example_prepared_wgd/report/final_report.md`, and `results/quickstart/example_prepared_wgd/tables/wgd_event_evidence.tsv` exist.
- `python -m pytest tests -q` passed with 159 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, prepared WGD handoff example, quickstart handoff, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: 67ea2a7cb3f31ba44ce4a16f35cbffa4e7c73712
- message: feat: add executable quickstart handoff
- files: executable quickstart runner, release check gate, quickstart docs, release audit docs, tests, history

Next:
- Continue toward final runtime readiness; if Docker/Apptainer remain unavailable, keep improving reproducible user handoffs and evidence summaries.

## 2026-06-24 - Add objective completion audit

Context:
- The repository now has executable quickstart, standard branch smoke, WGD event smoke, Nextflow smoke checks, release checks, readiness audit, and runtime bootstrap planning.
- The long `/goal` still needed a compact machine-readable answer to "which requested objectives are achieved, missing, or blocked on this machine".
- Docker and Apptainer remain unavailable locally, so the final status must preserve that blocker rather than flatten it into a generic failure.

Decisions:
- Add `bin/genefam/audit_objective_completion.py` to combine `release_checks.tsv` and `command_readiness.tsv` into objective-level status.
- Use statuses `achieved`, `blocked`, and `missing`, with Docker/Apptainer reproducibility explicitly marked `blocked` when both container runtimes are absent.
- Document the objective audit in quickstart and release-audit docs so it becomes part of the final handoff.

Added:
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Modified:
- `HISTORY.md`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py -q` first failed because `bin.genefam.audit_objective_completion` did not exist.
- After adding the objective audit script, `python -m pytest tests/test_audit_objective_completion.py -q` passed with 4 tests.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` first failed because docs did not mention `audit_objective_completion.py`.
- After updating quickstart and release audit docs, `python -m pytest tests/test_audit_objective_completion.py tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` passed with 7 tests.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` exited `0`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item is `Docker/Apptainer reproducibility` with missing commands `docker, apptainer`.
- `python -m pytest tests -q` passed with 163 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, prepared WGD handoff example, quickstart handoff, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: faf1c3c16778b8e5a38135fe0eea1ecd1791532d
- message: feat: add objective completion audit
- files: objective audit script, objective audit tests, quickstart/release audit docs, history

Next:
- Install or expose Docker/Apptainer to clear the remaining blocked objective, then rerun release checks and objective audit.

## 2026-06-24 - Auto-write objective audit from release checks

Context:
- `audit_objective_completion.py` could generate the long-goal audit, but it still required a separate manual command after `run_release_checks.py`.
- The final handoff should leave release checks, readiness, bootstrap plan, and objective completion evidence in one default release-gate run.
- `HISTORY.md` also needed the actual commit hash for the previous objective audit checkpoint.

Decisions:
- Add `write_objective_audit` to `run_release_checks.py`.
- Keep quick self-check mode lightweight and skip objective-audit generation there.
- Write `results/objective_audit/objective_audit.tsv` and `results/objective_audit/objective_audit.md` automatically after default release checks when readiness evidence exists.
- Reuse the existing objective audit builder instead of duplicating objective-status logic in the release runner.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_release_checks.py`
- `docs/quickstart.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py::test_write_objective_audit_uses_release_rows_and_readiness_tsv tests/test_release_audit_docs.py -q` first failed because `write_objective_audit` did not exist in `run_release_checks.py`.
- After wiring objective-audit generation, `python -m pytest tests/test_run_release_checks.py::test_write_objective_audit_uses_release_rows_and_readiness_tsv tests/test_release_audit_docs.py tests/test_quickstart_docs.py -q` passed with 4 tests.
- `python -m pytest tests -q` then failed because direct CLI execution of `bin/genefam/run_release_checks.py` could not import `bin.genefam.audit_objective_completion`.
- After adding the repo-root `sys.path` bootstrap to `run_release_checks.py`, `python -m pytest tests/test_run_release_checks.py::test_run_release_checks_cli_writes_outputs tests/test_run_release_checks.py::test_write_objective_audit_uses_release_rows_and_readiness_tsv -q` passed with 2 tests.
- `python -m pytest tests -q` passed with 164 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, prepared WGD handoff example, quickstart handoff, and runtime bootstrap plan passed.
- The same release-gate run automatically refreshed `results/objective_audit/objective_audit.md`, which reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item is `Docker/Apptainer reproducibility`.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.

Commit:
- hash: af142216f8b86658a89c63bab9a43e35e1cfb5db
- message: feat: auto-write objective audit in release checks
- files: release-check objective audit integration, release-check tests, quickstart docs, history

Next:
- Install or expose Docker/Apptainer to clear the remaining blocked objective, then rerun the single release-gate command and inspect the automatically generated objective audit.

## 2026-06-24 - Add container profile smoke verifier

Context:
- Docker/Apptainer remain the only blocked objective in the current machine audit.
- The repository had Docker and Apptainer profiles plus readiness checks, but it still lacked a focused command that directly verifies those container profiles once a runtime is available.
- The final handoff benefits from a deterministic container-profile smoke report instead of an ad hoc copied Nextflow command.

Decisions:
- Add `bin/genefam/run_container_profile_smoke.py` for `docker` and `apptainer` Nextflow mock-MVP profile verification.
- Report `missing_runtime` before checking Nextflow when Docker or Apptainer is unavailable, so the blocker remains precise.
- Reuse existing Nextflow command construction from `run_nextflow_smoke.py`.
- Document Docker and Apptainer smoke verifier commands in runtime and release-audit docs.

Added:
- `bin/genefam/run_container_profile_smoke.py`
- `tests/test_run_container_profile_smoke.py`

Modified:
- `HISTORY.md`
- `docs/release_audit.md`
- `docs/runtime_environment.md`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_container_profile_smoke.py -q` first failed because `bin.genefam.run_container_profile_smoke` did not exist.
- After adding the script, `python -m pytest tests/test_run_container_profile_smoke.py -q` passed with 5 tests.
- `python -m pytest tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file tests/test_release_audit_docs.py -q` first failed because docs did not mention `run_container_profile_smoke.py`.
- After updating runtime and release-audit docs, `python -m pytest tests/test_run_container_profile_smoke.py tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file tests/test_release_audit_docs.py -q` passed with 7 tests.
- `python bin/genefam/run_container_profile_smoke.py --profile docker --conda-env GeneFamilyFlow --outdir results/container_profile_smoke` exited `1` and wrote `results/container_profile_smoke/container_profile_smoke.tsv` plus `.md`; the status is `missing_runtime` because `docker` is not installed.
- `python -m pytest tests -q` passed with 169 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` because Docker and Apptainer are missing, but pytest, config validation, mock MVP, Python standard branch smoke, Python WGD event smoke, Nextflow mock MVP smoke, Nextflow standard branch smoke, Nextflow WGD event smoke, prepared WGD handoff example, quickstart handoff, and runtime bootstrap plan passed.
- `results/readiness/command_readiness.tsv` marks `nextflow`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, and `meme` as available through the host or `GeneFamilyFlow`; only `docker` and `apptainer` are missing.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item is `Docker/Apptainer reproducibility`.

Commit:
- hash: 84f7392ade220477e4c17fa643cebcefbd7f81bc
- message: feat: add container profile smoke verifier
- files: container profile smoke verifier, runtime/release docs, tests, history

Next:
- Once Docker or Apptainer is available, run the new container profile smoke verifier for the corresponding profile and rerun release checks/objective audit.

## 2026-06-24 - Add optional container smoke to release gate

Context:
- Container profile smoke verification existed as a standalone command, but the default release gate did not yet run it automatically.
- Docker/Apptainer are still unavailable on this machine, so these checks should add evidence without turning into an additional required release blocker.
- `HISTORY.md` also needed the actual commit hash for the previous container profile smoke checkpoint.

Decisions:
- Add optional `Docker profile smoke` and `Apptainer profile smoke` checks after the runtime bootstrap plan in `run_release_checks.py`.
- Keep both checks `required=False`, so missing container runtimes are visible in release outputs while `release_ready` remains controlled by required checks.
- Use profile-specific output directories under `results/container_profile_smoke/docker` and `results/container_profile_smoke/apptainer`.
- Fix `run_container_profile_smoke.py` so profile-specific output directories do not duplicate the profile name inside the Nextflow `--outdir`.
- Update runtime and release-audit docs to describe the profile-specific report paths.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_container_profile_smoke.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `docs/runtime_environment.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_container_profile_smoke.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py::test_summarize_checks_keeps_release_ready_when_only_optional_checks_fail tests/test_run_release_checks.py::test_default_checks_include_optional_container_profile_smokes_after_bootstrap -q` first failed because default release checks did not include `Docker profile smoke`.
- After adding the optional checks, `python -m pytest tests/test_run_release_checks.py::test_summarize_checks_keeps_release_ready_when_only_optional_checks_fail tests/test_run_release_checks.py::test_default_checks_include_optional_container_profile_smokes_after_bootstrap tests/test_release_audit_docs.py tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file -q` passed with 4 tests.
- `python -m pytest tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file tests/test_release_audit_docs.py -q` first failed after tightening expected profile-specific report paths.
- After updating docs, `python -m pytest tests/test_run_release_checks.py tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file tests/test_release_audit_docs.py -q` passed with 18 tests.
- `python -m pytest tests/test_run_container_profile_smoke.py::test_run_container_profile_smoke_does_not_duplicate_profile_named_outdir -q` first failed because the command used `results/container_profile_smoke/docker/docker/mock_mvp`.
- After fixing the script, `python -m pytest tests/test_run_container_profile_smoke.py tests/test_run_release_checks.py tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file tests/test_release_audit_docs.py -q` passed with 24 tests.
- `python -m pytest tests -q` passed with 172 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`; required checks still fail only at readiness because Docker/Apptainer are missing, while optional `Docker profile smoke` and `Apptainer profile smoke` also report failed evidence.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, and `Release ready: false`.
- `results/container_profile_smoke/docker/container_profile_smoke.tsv` reports `missing_runtime` for Docker with Nextflow output path `results/container_profile_smoke/docker/mock_mvp`.
- `results/container_profile_smoke/apptainer/container_profile_smoke.tsv` reports `missing_runtime` for Apptainer with Nextflow output path `results/container_profile_smoke/apptainer/mock_mvp`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item is `Docker/Apptainer reproducibility`.

Commit:
- hash: dc6b6230356fa97b09c7666adea2444b7fd7ff5d
- message: feat: add optional container smoke release checks
- files: release gate container smoke integration, container smoke path fix, runtime/release docs, tests, history

Next:
- Once Docker or Apptainer is installed, rerun `python bin/genefam/run_release_checks.py --outdir results/release_checks` and confirm the corresponding optional container profile smoke changes from `missing_runtime` to `passed`.

## 2026-06-24 - Split required and optional release failures

Context:
- Release checks now include optional Docker and Apptainer profile smoke evidence.
- The Markdown summary only reported total failures, so a normal runtime-blocked Mac run showed `Failed: 3` without distinguishing the one required readiness blocker from two optional container-profile diagnostics.
- The final handoff needs the summary to be readable at a glance.

Decisions:
- Extend `summarize_checks` with `required_failed` and `optional_failed` counts.
- Add `Required failed` and `Optional failed` lines to `results/release_checks/release_checks.md`.
- Keep `release_ready` based only on required failures.
- Document the breakdown in quickstart and release-audit docs.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_release_checks.py`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py::test_summarize_checks_marks_release_not_ready_when_required_check_fails tests/test_run_release_checks.py::test_summarize_checks_keeps_release_ready_when_only_optional_checks_fail tests/test_run_release_checks.py::test_write_markdown_summarizes_required_and_optional_failures -q` first failed because `summarize_checks` did not return `required_failed` and `optional_failed`, and Markdown did not report them.
- After updating the release summary code, `python -m pytest tests/test_run_release_checks.py -q` passed with 17 tests.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` first failed because docs did not mention `Required failed` and `Optional failed`.
- After updating docs, `python -m pytest tests/test_run_release_checks.py tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` passed with 20 tests.
- `python -m pytest tests -q` passed with 173 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item is `Docker/Apptainer reproducibility`.

Commit:
- hash: cc9246038fc106d670fa5b546c2d72d5ffa9060a
- message: feat: split required and optional release failures
- files: release summary breakdown, quickstart/release docs, tests, history

Next:
- Once Docker or Apptainer is installed, rerun release checks; optional failure counts should drop independently from required readiness status.

## 2026-06-24 - Add final handoff report

Context:
- Release checks, objective audit, readiness audit, and container smoke reports were available, but the user still had to inspect several files to understand current delivery status.
- The final handoff needed one compact Markdown page that points to the authoritative evidence and states the current blocker.
- An initial release-gate integration ran the handoff report as a check, which made it read the previous `release_checks.tsv` instead of the just-generated one.

Decisions:
- Add `bin/genefam/build_handoff_report.py` to summarize release, objective, readiness, and container smoke evidence.
- Write `results/handoff/handoff_report.md` from the release runner after the latest release TSV/Markdown and objective audit have been written.
- Keep the handoff report out of `default_checks()` so it does not read stale release evidence.
- Document the handoff report in quickstart and release-audit docs.

Added:
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`

Modified:
- `HISTORY.md`
- `bin/genefam/run_release_checks.py`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because `bin.genefam.build_handoff_report` did not exist.
- After adding the script, `python -m pytest tests/test_build_handoff_report.py -q` passed with 3 tests.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_handoff_report_after_container_smokes tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` first failed because release checks and docs did not mention the handoff report.
- After integrating the first version, `python -m pytest tests/test_build_handoff_report.py tests/test_run_release_checks.py::test_default_checks_include_handoff_report_after_container_smokes tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` passed with 7 tests.
- Manual verification of `results/handoff/handoff_report.md` showed stale release counts because the handoff report ran as a check before the latest release TSV was written.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_do_not_include_handoff_report_as_a_stale_input_check tests/test_run_release_checks.py::test_write_handoff_report_uses_latest_written_release_tsv -q` first failed because `write_handoff_report` did not exist.
- After moving handoff report generation after release TSV writing, `python -m pytest tests/test_run_release_checks.py tests/test_build_handoff_report.py tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` passed with 25 tests.
- `python -m pytest tests -q` passed with 178 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` now reports `passed=12 failed=3 required_failed=1 optional_failed=2 release_ready=false`, matching the latest release checks.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item is `Docker/Apptainer reproducibility`.

Commit:
- hash: 879ac578b6f8238d2e822f26f652ddc8bfc9a3f5
- message: feat: add final handoff report
- files: handoff report builder, release runner integration, quickstart/release docs, tests, history

Next:
- Use `results/handoff/handoff_report.md` as the first file to inspect after each release-gate run.

## 2026-06-24 - Document handoff report as first entrypoint

Context:
- The handoff report existed and was generated by the release gate.
- README and the readiness checklist still described the lower-level evidence files before telling the user which single file to inspect first.
- The final handoff should make `results/handoff/handoff_report.md` discoverable from the main project docs.

Decisions:
- Add `results/handoff/handoff_report.md` to README runtime/readiness guidance.
- Add the same first-inspection guidance to `docs/readiness_checklist.md`.
- Add tests so the README and readiness checklist keep pointing users to the handoff report.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/readiness_checklist.md`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report -q` first failed because README and the readiness checklist did not mention `results/handoff/handoff_report.md`.
- After updating docs, the same command passed with 2 tests.
- `python -m pytest tests -q` passed with 179 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` reports `passed=12 failed=3 required_failed=1 optional_failed=2 release_ready=false`, `achieved=11 blocked=1 missing=0 complete=false`, and missing runtime commands `docker, apptainer`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item is `Docker/Apptainer reproducibility`.

Commit:
- hash: 7a6def8b21bb8a89b7a8b84260a25d8fa0a774be
- message: docs: document handoff report entrypoint
- files: README/readiness handoff entrypoint docs, tests, history

Next:
- Continue keeping the handoff report as the first human-facing status page while remaining runtime-blocked on Docker/Apptainer.

## 2026-06-24 - Add available runtime summary to handoff report

Context:
- The handoff report showed missing runtime commands, but not the commands already available through the host or `GeneFamilyFlow`.
- The final status page should distinguish "blocked on Docker/Apptainer" from "core Nextflow and bioinformatics tools are available".

Decisions:
- Add an `available_runtime` summary to `build_handoff_report.py`.
- Treat readiness statuses beginning with `available` as available, including `available_in_conda`.
- Show available runtime commands in `results/handoff/handoff_report.md`.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because `available_runtime` was not returned and Markdown did not include `Available runtime commands`.
- After adding the summary, `python -m pytest tests/test_build_handoff_report.py -q` passed with 3 tests.
- `python -m pytest tests -q` passed with 179 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/handoff/handoff_report.md` now lists available runtime commands: `nextflow`, `conda`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2`, and `meme`.
- The same handoff report lists missing runtime commands: `docker, apptainer`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.

Commit:
- hash: 7df87e4b5b1e5c4ba38783e22ecf74f314286ce8
- message: feat: add available runtime handoff summary
- files: handoff runtime availability summary, tests, history

Next:
- Keep using the handoff report as the top-level delivery status while Docker/Apptainer remain unavailable.

## 2026-06-24 - Add machine-readable handoff summary

Context:
- The final handoff report was readable for humans, but downstream scripts still needed a stable machine-readable top-level status file.
- The release gate should write human-facing Markdown and parser-friendly TSV from the same handoff sections.

Decisions:
- Add `write_summary_tsv()` to `bin/genefam/build_handoff_report.py`.
- Make the handoff CLI write `results/handoff/handoff_summary.tsv` by default.
- Make `run_release_checks.py` write the Markdown report and TSV summary together after the latest release/objective/readiness evidence has been written.
- Document both handoff outputs in README and the readiness checklist.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/readiness_checklist.md`
- `bin/genefam/build_handoff_report.py`
- `bin/genefam/run_release_checks.py`
- `tests/test_build_handoff_report.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because `write_summary_tsv` did not exist.
- After adding TSV writing, `python -m pytest tests/test_build_handoff_report.py -q` passed with 4 tests.
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report -q` first failed because README and the readiness checklist did not mention `results/handoff/handoff_summary.tsv`.
- After updating docs, the same command passed with 2 tests.
- `python -m pytest tests/test_build_handoff_report.py tests/test_run_release_checks.py::test_write_handoff_report_uses_latest_written_release_tsv -q` passed with 5 tests.
- `python -m pytest tests -q` passed with 180 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` reports `passed=12 failed=3 required_failed=1 optional_failed=2 release_ready=false`, `achieved=11 blocked=1 missing=0 complete=false`, available runtime commands `nextflow`, `conda`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2`, and `meme`, and missing runtime commands `docker, apptainer`.
- `results/handoff/handoff_summary.tsv` contains matching `release`, `objective`, `available_runtime`, `missing_runtime`, and `container_smoke` sections.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item is still Docker/Apptainer reproducibility.

Commit:
- hash: 1c097218ffa0b717899f18878713dd89b341d0e0
- message: feat: add machine-readable handoff summary
- files: handoff summary TSV writer, release runner integration, README/readiness docs, tests, history

Next:
- Keep the Markdown and TSV handoff files as the top-level release evidence while Docker/Apptainer remain unavailable.

## 2026-06-24 - Align README status with release evidence

Context:
- README still contained an early statement that full external-tool workflow wiring was under development.
- Current release evidence shows the standard branch and prepared WGD branch are wired and tested through `GeneFamilyFlow`; the remaining blocker is machine-level Docker/Apptainer availability.
- The release audit output list also needed to include the machine-readable handoff summary.

Decisions:
- Replace the stale README Current Status section with evidence-aligned repository-ready/runtime-blocked wording.
- Mention the standard identification branch, prepared-table WGD branch, gamma/beta/alpha/theta evidence path, available `GeneFamilyFlow` commands, and Docker/Apptainer blocker.
- Add `results/handoff/handoff_summary.tsv` to the release audit output list.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_readme_current_status_matches_release_evidence tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands -q` first failed because README still said full external-tool wiring was under development and release audit did not mention `results/handoff/handoff_summary.tsv`.
- After updating docs, the same command passed with 2 tests.
- `python -m pytest tests -q` passed with 181 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` reports `passed=12 failed=3 required_failed=1 optional_failed=2 release_ready=false`, `achieved=11 blocked=1 missing=0 complete=false`, available runtime commands `nextflow`, `conda`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2`, and `meme`, and missing runtime commands `docker, apptainer`.
- `results/handoff/handoff_summary.tsv` contains matching `release`, `objective`, `available_runtime`, `missing_runtime`, and `container_smoke` sections.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: d32b980b510cfaa86ad5ab7d08d4d333b1cbf846
- message: docs: align status with release evidence
- files: README current status, release audit output list, docs tests, history

Next:
- Keep README and release-audit status aligned with `results/handoff/handoff_report.md` and `results/handoff/handoff_summary.tsv`.

## 2026-06-24 - Show blocked requirements in handoff

Context:
- The handoff report and summary showed objective counts such as `blocked=1`, but did not directly name which requirement was blocked.
- The first handoff page should make the remaining blocker explicit without requiring users or scripts to open the full objective audit.

Decisions:
- Add a `blocked_requirements` section to the handoff sections.
- Treat objective audit rows with `blocked` or `missing` status as handoff blockers.
- Write blocked requirement names to both `results/handoff/handoff_report.md` and `results/handoff/handoff_summary.tsv`.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because `blocked_requirements` was missing from sections and Markdown.
- After adding blocked requirement extraction and Markdown output, `python -m pytest tests/test_build_handoff_report.py -q` passed with 4 tests.
- `python -m pytest tests/test_build_handoff_report.py tests/test_run_release_checks.py::test_write_handoff_report_uses_latest_written_release_tsv -q` passed with 5 tests.
- `python -m pytest tests -q` passed with 181 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` reports `Blocked requirements: Docker/Apptainer reproducibility`, available runtime commands `nextflow`, `conda`, `/usr/local/bin/R`, `hmmsearch`, `diamond`, `mafft`, `iqtree2`, and `meme`, and missing runtime commands `docker, apptainer`.
- `results/handoff/handoff_summary.tsv` contains `blocked_requirements	Docker/Apptainer reproducibility`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: 0dfaf2aab8e2f3b3e6fdea26e9994c36cab713ee
- message: feat: show blocked handoff requirements
- files: handoff blocked requirement summary, release runner test, history

Next:
- Keep `blocked_requirements` visible in the top-level handoff while Docker/Apptainer remain unavailable.

## 2026-06-24 - Link unblock artifacts from handoff

Context:
- The handoff report named the blocked requirement, but the actionable bootstrap plan and script were still only discoverable through the readiness directory.
- The top-level handoff should point directly to the files that explain how to unblock Docker/Apptainer reproducibility.

Decisions:
- Add a `next_unblock_artifacts` section to the handoff sections.
- Emit `results/readiness/runtime_bootstrap_plan.md` and `results/readiness/runtime_bootstrap.sh` whenever objective or runtime blockers remain.
- Add the same artifacts to the handoff Markdown Key Evidence list.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because `next_unblock_artifacts` was missing from sections and Markdown.
- After adding unblock artifact output, `python -m pytest tests/test_build_handoff_report.py -q` passed with 4 tests.
- `python -m pytest tests/test_build_handoff_report.py tests/test_run_release_checks.py::test_write_handoff_report_uses_latest_written_release_tsv -q` passed with 5 tests.
- `python -m pytest tests -q` passed with 181 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` reports `Unblock artifacts: results/readiness/runtime_bootstrap_plan.md, results/readiness/runtime_bootstrap.sh`.
- `results/handoff/handoff_summary.tsv` contains `next_unblock_artifacts	results/readiness/runtime_bootstrap_plan.md, results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: fe1128ea0186325bba150d0072ca7bfdcc467dd2
- message: feat: link handoff unblock artifacts
- files: handoff unblock artifact summary, release runner test, history

Next:
- Keep `next_unblock_artifacts` visible in the top-level handoff until container runtime verification is available.

## 2026-06-24 - Add next unblock command to handoff

Context:
- The handoff report linked the bootstrap plan and script, but the copyable command to run that script was still not exposed as a top-level status field.
- A morning handoff should include both evidence files and an executable next action for the remaining Docker/Apptainer blocker.

Decisions:
- Add a `next_unblock_command` section to the handoff sections.
- Emit `bash results/readiness/runtime_bootstrap.sh` whenever objective or runtime blockers remain.
- Show the same command in Markdown and the machine-readable handoff summary TSV.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because `next_unblock_command` was missing from sections and Markdown.
- After adding the command, `python -m pytest tests/test_build_handoff_report.py -q` passed with 4 tests.
- `python -m pytest tests/test_build_handoff_report.py tests/test_run_release_checks.py::test_write_handoff_report_uses_latest_written_release_tsv -q` passed with 5 tests.
- `python -m pytest tests -q` passed with 181 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` reports `Next unblock command: bash results/readiness/runtime_bootstrap.sh`.
- `results/handoff/handoff_summary.tsv` contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: 7da7b320f3e5475cd8ee42eb60af3345a47762f1
- message: feat: add handoff unblock command
- files: handoff unblock command summary, release runner test, history

Next:
- Keep `next_unblock_command` visible in the top-level handoff until Docker/Apptainer verification is available.

## 2026-06-24 - Prefer unblock command in handoff next step

Context:
- The handoff report exposed `next_unblock_command`, but the `Next Command` code block still showed the release-gate rerun.
- When the release is blocked, the most useful next copyable command is the unblock command; when there is no blocker, the release gate should remain the next command.

Decisions:
- Make `write_markdown()` choose `next_unblock_command` for the `Next Command` block when it is present and not `none`.
- Keep `python bin/genefam/run_release_checks.py --outdir results/release_checks` as the fallback when no unblock command is needed.
- Add tests for both blocked and no-blocker handoff states.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because the `Next Command` block still showed the release-gate rerun instead of `bash results/readiness/runtime_bootstrap.sh`.
- After making the next command dynamic, `python -m pytest tests/test_build_handoff_report.py -q` passed with 5 tests.
- `python -m pytest tests -q` passed with 182 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` now shows `bash results/readiness/runtime_bootstrap.sh` inside the `Next Command` block.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: bfeb55502503964c620c709cfba9ec72cf54624f
- message: feat: prefer unblock handoff command
- files: handoff next-command selection, handoff tests, history

Next:
- Keep the `Next Command` block aligned with the current handoff state: unblock command while blocked, release gate when clear.

## 2026-06-25 - Respect identification tool flags

Context:
- `configs/example.config.yaml` and the schema expose `identification.use_hmmer` and `identification.use_diamond`.
- `bin/genefam/build_identification_inputs.py` still generated both HMMER and DIAMOND input tables unconditionally, so YAML-driven tool selection was not fully true.
- A standard identification run should not silently plan evidence sources that the YAML disabled.

Decisions:
- Make `build_hmmer_inputs()` return no rows when `identification.use_hmmer: false`.
- Make `build_diamond_inputs()` return no rows when `identification.use_diamond: false`.
- Keep header-only TSV outputs for disabled tools so downstream planning files remain stable.
- Add config validation that rejects `modules.identification: true` when both search tools are disabled.
- Document the two flags in the input contract and schema.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_identification_inputs.py`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `schemas/config.schema.yaml`
- `tests/test_build_identification_inputs.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_validate_config.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_identification_inputs.py -q` first failed because disabled HMMER/DIAMOND flags were ignored.
- After making the input builders respect the flags, `python -m pytest tests/test_build_identification_inputs.py -q` passed with 8 tests.
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_identification_without_any_enabled_search_tool -q` first failed because config validation allowed both search tools to be disabled.
- After adding validation, `python -m pytest tests/test_build_identification_inputs.py tests/test_validate_config.py -q` passed with 21 tests.
- `python -m pytest tests/test_runtime_environment_files.py::test_input_contract_and_schema_document_identification_tool_flags -q` first failed because the schema and input contract did not mention the flags.
- After documenting the flags, `python -m pytest tests/test_build_identification_inputs.py tests/test_validate_config.py tests/test_runtime_environment_files.py::test_input_contract_and_schema_document_identification_tool_flags -q` passed with 22 tests.
- `python -m pytest tests -q` passed with 187 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_report.md` still points the `Next Command` block to `bash results/readiness/runtime_bootstrap.sh`.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: ccfdf938985626f99bf8dce0357af179a7c8b166
- message: feat: respect identification tool flags
- files: identification input builders, config validation, input docs/schema, tests, history

Next:
- Continue tightening YAML-driven Nextflow behavior and keep Docker/Apptainer as the explicit runtime blocker.

## 2026-06-25 - Wire single-tool standard evidence paths

Context:
- The identification input builder now respects `identification.use_hmmer` and `identification.use_diamond`.
- `workflows/main.nf` still joined `HMMER_SEARCH.out` and `DIAMOND_SEARCH.out` directly, which made HMMER-only or DIAMOND-only standard runs lose all candidate evidence.
- The Nextflow standard branch needs a stable evidence tuple for each selected species even when one search tool is disabled.

Decisions:
- Add `EMPTY_HMMER_EVIDENCE` and `EMPTY_DIAMOND_EVIDENCE` processes that emit header-only normalized TSVs per species.
- Add `params.use_hmmer` and `params.use_diamond` defaults to `workflows/nextflow.config`.
- In the standard identification branch, choose real HMMER/DIAMOND outputs or empty evidence outputs based on the params before joining evidence.
- Keep the downstream `DOMAIN_FILTER` interface unchanged as `(species_id, hmmer_tsv, diamond_tsv)`.

Added:
- none

Modified:
- `HISTORY.md`
- `workflows/main.nf`
- `workflows/nextflow.config`
- `workflows/modules/domain_filter.nf`
- `tests/test_runtime_environment_files.py`
- `tests/test_workflow_modules.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py::test_domain_filter_module_can_concatenate_species_candidate_tables tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` first failed because the empty evidence processes and conditional evidence channels did not exist.
- After adding the processes and conditional wiring, the same command passed with 2 tests.
- `python -m pytest tests/test_workflow_modules.py::test_domain_filter_module_can_concatenate_species_candidate_tables tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch tests/test_runtime_environment_files.py::test_nextflow_config_has_container_profiles -q` passed with 3 tests.
- `python -m pytest tests -q` passed with 187 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/nextflow_standard_smoke/nextflow_standard_smoke.tsv` reports `nextflow_standard_identification` as `passed`.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: fa17d377a83d88b639c6a695d6eae390cb0d5a36
- message: feat: wire single-tool standard evidence paths
- files: standard branch evidence routing, empty evidence processes, Nextflow params, tests, history

Next:
- Add a focused Nextflow smoke for HMMER-only or DIAMOND-only standard evidence routing if runtime fixtures are expanded.

## 2026-06-25 - Pass identification flags into standard smoke

Context:
- The standard Nextflow branch now has `params.use_hmmer`, `params.use_diamond`, and `params.final_rule`.
- `bin/genefam/run_nextflow_standard_smoke.py` still only passed the YAML path as `--config`; Nextflow did not automatically consume the YAML `identification` values as params.
- The YAML-driven contract should be visible in the exact Nextflow command emitted by the standard smoke wrapper.

Decisions:
- Add `load_identification_params()` to read `identification.use_hmmer`, `identification.use_diamond`, and `identification.final_rule` from the YAML config.
- Pass those values as `--use_hmmer`, `--use_diamond`, and `--final_rule` in the internal `nextflow run` command.
- Normalize boolean params so both Python booleans and string values such as `"false"` are preserved correctly.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `tests/test_run_nextflow_standard_smoke.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_nextflow_standard_smoke.py -q` first failed because `load_identification_params` did not exist.
- After adding the helper and command params, `python -m pytest tests/test_run_nextflow_standard_smoke.py -q` failed because the old exact command expectation did not include the new params.
- After updating the expected command, `python -m pytest tests/test_run_nextflow_standard_smoke.py -q` failed because string `"false"` was converted to `true`.
- After tightening boolean normalization, `python -m pytest tests/test_run_nextflow_standard_smoke.py -q` passed with 7 tests.
- `python -m pytest tests -q` passed with 190 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 12`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/nextflow_standard_smoke/nextflow_standard_smoke.tsv` reports `nextflow_standard_identification` as `passed`; the internal command includes `--use_hmmer true --use_diamond true --final_rule intersection`.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: 26f6af888f258e607811c3b58daea702062bfe31
- message: feat: pass identification flags to standard smoke
- files: standard smoke YAML param propagation, command builder tests, history

Next:
- Continue expanding focused smoke coverage for single-tool standard routing and keep Docker/Apptainer as the explicit release blocker.

## 2026-06-25 - Add single-tool Nextflow standard smoke

Context:
- The standard branch now supports `identification.use_hmmer` and `identification.use_diamond`, but the existing Nextflow standard smoke used `mock_external_tools` and did not exercise the real single-tool routing paths.
- Passing `--mock_external_tools false` and `--use_hmmer false` from Python still reached Nextflow as strings, so Groovy treated `"false"` as truthy and stayed on the wrong branch.
- HMMER-only and DIAMOND-only routing need release-gate evidence without requiring the downstream alignment/report steps to succeed on tiny toy evidence.

Decisions:
- Rename the standard smoke config helper to `load_standard_params()` and include `dev.mock_external_tools`.
- Add `asBooleanParam()` in `workflows/main.nf` so Nextflow CLI string params such as `"false"` are interpreted correctly.
- Add `params.standard_stop_after_family_candidates` to stop focused diagnostics after true tool routing, domain filtering, and candidate concatenation.
- Add `bin/genefam/run_nextflow_single_tool_smoke.py` to generate HMMER-only and DIAMOND-only non-mock configs and run both focused Nextflow checks.
- Add the single-tool smoke as a required release check after the standard branch smoke.

Added:
- `bin/genefam/run_nextflow_single_tool_smoke.py`
- `tests/test_run_nextflow_single_tool_smoke.py`

Modified:
- `HISTORY.md`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `bin/genefam/run_release_checks.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_release_checks.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_nextflow_standard_smoke.py tests/test_run_nextflow_single_tool_smoke.py tests/test_run_release_checks.py::test_default_checks_include_nextflow_single_tool_smoke -q` first failed because `load_standard_params` and `bin.genefam.run_nextflow_single_tool_smoke` did not exist.
- After adding the standard params helper, single-tool script, and release check, the same focused command passed with 11 tests.
- `python bin/genefam/run_nextflow_single_tool_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_single_tool_smoke` first exited `1`; the command had `--mock_external_tools false`, but Nextflow still ran `MOCK_IDENTIFICATION_EVIDENCE` because string `"false"` was truthy.
- `python -m pytest tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` first failed because `asBooleanParam()` did not exist.
- After adding `asBooleanParam()`, the workflow structure test passed with 1 test.
- Re-running `python bin/genefam/run_nextflow_single_tool_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_single_tool_smoke` then entered true single-tool branches but exited `1` because downstream alignment requires at least two sequences on the tiny toy evidence.
- After adding `standard_stop_after_family_candidates`, `python -m pytest tests/test_run_nextflow_standard_smoke.py tests/test_run_nextflow_single_tool_smoke.py tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch tests/test_run_release_checks.py::test_default_checks_include_nextflow_single_tool_smoke -q` passed with 13 tests.
- `python bin/genefam/run_nextflow_single_tool_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_single_tool_smoke` exited `0`.
- `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv` reports both `nextflow_standard_hmmer_only` and `nextflow_standard_diamond_only` as `passed`.
- `.nextflow.log.1` shows HMMER-only routing submitted `HMMER_SEARCH` and `EMPTY_DIAMOND_EVIDENCE`; `.nextflow.log` shows DIAMOND-only routing submitted `DIAMOND_SEARCH` and `EMPTY_HMMER_EVIDENCE`.
- `python -m pytest tests -q` passed with 195 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 13`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/release_checks/release_checks.md` includes required `Nextflow standard single-tool smoke` as `passed`.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: 6c6cbf1734710b8f054cb5eec5ffcd1318f80259
- message: test: add single-tool nextflow standard smoke
- files: single-tool Nextflow smoke, bool param parsing, focused family-candidate stop point, release check, tests, history

Next:
- Keep Docker/Apptainer as the explicit release blocker; continue improving release evidence without changing `Reference/`.

## 2026-06-25 - Parameterize container images and bootstrap profile checks

Context:
- `workflows/nextflow.config` hard-coded Docker and Apptainer container names inside profiles.
- Docker used the local image tag `genefam-pipeline:latest`, while Apptainer used `docker://genefam-pipeline:latest`, which is ambiguous for a locally built image.
- `results/readiness/runtime_bootstrap.sh` built the Docker image but did not explicitly build a local Apptainer SIF or run the two container profile smoke checks before the full release gate.

Decisions:
- Add `params.container_image` and `params.apptainer_image` to `workflows/nextflow.config`.
- Make the Docker profile use `params.container_image` and the Apptainer profile use `params.apptainer_image`.
- Default `params.apptainer_image` to `genefam-pipeline_latest.sif` so the Apptainer route can use a local SIF produced by the bootstrap script.
- Extend the runtime bootstrap plan and shell script with `apptainer build --force genefam-pipeline_latest.sif docker-daemon://genefam-pipeline:latest`.
- Add explicit Docker and Apptainer profile smoke commands to the bootstrap outputs.
- Document the container image parameters and Apptainer SIF build in `docs/runtime_environment.md`.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/plan_runtime_bootstrap.py`
- `docs/runtime_environment.md`
- `tests/test_plan_runtime_bootstrap.py`
- `tests/test_runtime_environment_files.py`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_nextflow_config_has_container_profiles tests/test_plan_runtime_bootstrap.py::test_build_bootstrap_plan_groups_missing_commands_into_actionable_steps -q` first failed because container image params and Apptainer bootstrap/profile smoke commands were missing.
- After parameterizing container images and extending the bootstrap plan, `python -m pytest tests/test_runtime_environment_files.py::test_nextflow_config_has_container_profiles tests/test_plan_runtime_bootstrap.py::test_build_bootstrap_plan_groups_missing_commands_into_actionable_steps tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file -q` passed with 3 tests.
- `python -m pytest tests/test_plan_runtime_bootstrap.py tests/test_runtime_environment_files.py -q` passed with 15 tests.
- `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` exited `0`.
- `results/readiness/runtime_bootstrap_plan.md` now documents `genefam-pipeline_latest.sif` and the Docker/Apptainer profile smoke commands.
- `results/readiness/runtime_bootstrap.sh` now includes Docker build, Apptainer SIF build, Docker profile smoke, Apptainer profile smoke, and the full release gate.
- `python -m pytest tests -q` passed with 195 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 13`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: 2c2a2f55e8d05ca2d4554777f5439b81dfa89762
- message: feat: parameterize container runtime images
- files: container image params, bootstrap Docker/Apptainer commands, runtime docs, tests, history

Next:
- Once Docker and Apptainer are installed on the machine, run `bash results/readiness/runtime_bootstrap.sh` to build the local Docker image, build the Apptainer SIF, verify both profiles, and rerun the release gate.

## 2026-06-25 - Document final smoke and container unblock entrypoints

Context:
- README and quickstart still did not expose the new Nextflow single-tool smoke as a first-class verification command.
- The container image parameterization and `bash results/readiness/runtime_bootstrap.sh` unblock path were implemented, but the shortest user-facing entrypoints were not fully reflected in top-level docs.
- The final workflow should be easy to resume from docs without reading implementation history.

Decisions:
- Add the generated runtime bootstrap script to README as the Docker/Apptainer unblock command.
- Document `params.container_image` and `params.apptainer_image` in README.
- Add the focused Nextflow single-tool smoke command to README and quickstart.
- List `nextflow_standard_hmmer_only` and `nextflow_standard_diamond_only` as quickstart evidence rows.
- Keep the current status explicit: repository-ready but runtime-blocked until Docker/Apptainer are installed.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/quickstart.md`
- `tests/test_quickstart_docs.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_quickstart_docs.py tests/test_runtime_environment_files.py::test_readme_current_status_matches_release_evidence -q` first failed because README and quickstart did not mention `run_nextflow_single_tool_smoke.py`, `bash results/readiness/runtime_bootstrap.sh`, or the container image params.
- After updating README and quickstart, the same command passed with 3 tests.
- `python -m pytest tests/test_quickstart_docs.py tests/test_runtime_environment_files.py tests/test_release_audit_docs.py -q` passed with 15 tests.
- `python -m pytest tests -q` passed with 195 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 13`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility.

Commit:
- hash: 0b9d26a484895cb5a3cba1bd36ec783ceedda8e0
- message: docs: surface final verification entrypoints
- files: README/quickstart final entrypoints, documentation tests, history

Next:
- Keep the docs, handoff report, and release gate aligned while Docker/Apptainer remain the only machine-level blocker.

## 2026-06-25 - Require single-tool smoke in objective audit

Context:
- The release gate now runs `Nextflow standard single-tool smoke`, but `bin/genefam/audit_objective_completion.py` still considered the DSL2 workflow achieved without that evidence.
- `docs/release_audit.md` also mapped the DSL2 workflow to the older mock and WGD smokes without listing the single-tool command and result file.
- The long objective explicitly asks for YAML-driven HMMER/BLAST-style identification paths, so HMMER-only and DIAMOND-only routing should be part of the completion evidence.

Decisions:
- Require `Nextflow standard single-tool smoke` for the `Nextflow DSL2 workflow` objective row.
- Update the DSL2 objective note to mention HMMER-only and DIAMOND-only routing through `GeneFamilyFlow`.
- Update `docs/release_audit.md` to list `run_nextflow_single_tool_smoke.py` and `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv`.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py tests/test_release_audit_docs.py -q` first failed because the objective audit still passed DSL2 without the single-tool smoke and release audit docs did not mention `run_nextflow_single_tool_smoke.py`.
- After tightening the objective audit and updating release audit docs, the same command passed with 6 tests.
- `python -m pytest tests/test_audit_objective_completion.py tests/test_release_audit_docs.py tests/test_run_release_checks.py -q` passed with 26 tests.
- `python -m pytest tests -q` passed with 196 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 13`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/objective_audit/objective_audit.md` now says `Nextflow DSL2 workflow` is achieved from `Nextflow mock, standard, single-tool, and WGD smoke checks`.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.

Commit:
- hash: bb2e8de771e915e2345477110dbe72e060a3e4ca
- message: test: require single-tool smoke in objective audit
- files: objective audit single-tool requirement, release audit docs, tests, history

Next:
- Keep completion evidence strict: any new release smoke that proves core objective behavior should be reflected in `audit_objective_completion.py` and `docs/release_audit.md`.

## 2026-06-25 - Add static container materials audit

Context:
- The objective still requires Docker/Conda reproducibility, but this machine lacks Docker and Apptainer, so runtime profile smoke remains blocked by external tools.
- The repository can still verify that its container materials are internally consistent before those runtimes are installed.
- Existing checks covered runtime profile smoke, but not a required static audit of the Dockerfile, Linux Conda environment, and Nextflow container-profile contract.

Decisions:
- Add `bin/genefam/audit_container_materials.py` as a required release check that does not need Docker or Apptainer.
- Validate that the Dockerfile creates `GeneFamilyFlow`, links `/usr/local/bin/R`, and uses `envs/GeneFamilyFlow.linux-64.conda.yaml`.
- Validate that the Linux Conda environment carries the container-only full toolchain, including `jcvi` and `kaks_calculator`.
- Validate that Nextflow Docker and Apptainer profiles use parameterized container images and disable process-level Conda.

Added:
- `bin/genefam/audit_container_materials.py`
- `tests/test_audit_container_materials.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `docs/runtime_environment.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_container_materials.py -q` first failed because `bin.genefam.audit_container_materials` did not exist.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_optional_container_profile_smokes_after_bootstrap -q` first failed because `container materials audit` was not in `default_checks()`.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not mention `python bin/genefam/audit_container_materials.py`.
- `python -m pytest tests/test_audit_objective_completion.py::test_build_objective_audit_marks_goal_items_and_runtime_blockers -q` first failed because the Docker/Apptainer reproducibility evidence did not include `container materials audit`.
- After implementing the static audit, release integration, docs, and objective-audit evidence text, `python -m pytest tests/test_audit_objective_completion.py tests/test_audit_container_materials.py tests/test_run_release_checks.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` passed with 41 tests.
- `python -m pytest tests -q` passed with 199 tests.
- `python bin/genefam/audit_container_materials.py --outdir results/container_materials` exited `0`; `results/container_materials/container_materials.md` reports `Passed: 5` and `Failed: 0`.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 14`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `container materials audit` is now a required release check and passed.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the blocked item remains Docker/Apptainer reproducibility due missing `docker` and `apptainer`.
- `results/handoff/handoff_summary.tsv` still contains `next_unblock_command	bash results/readiness/runtime_bootstrap.sh`.

Commit:
- hash: a54b184a3b7f54b489865e4b3caba8679eeb9619
- message: test: add container materials release audit
- files: container materials audit, release gate, objective audit evidence, docs, tests, history

Next:
- Keep the runtime blocker explicit: this static audit improves reproducibility evidence but does not replace real Docker/Apptainer profile smoke after those commands are installed.

## 2026-06-25 - Surface motif summary in standard branch reports

Context:
- The long objective includes motif analysis as a standard gene-family module.
- `parse_meme_motifs.py` and the Nextflow `PARSE_MEME_MOTIFS` module already existed, but the standard smoke and standard report index did not expose a `motif_summary` output.
- Without a report-index output, motif evidence could pass parser tests while remaining invisible in the user-facing standard branch report.

Decisions:
- Add `motif_summary` to the standard report index contract.
- Have `run_standard_smoke.py` generate a small mock MEME text file, parse it through `parse_meme_motifs.py`, and write `tables/motif_summary.tsv`.
- Parameterize the Nextflow MEME text input as `params.meme_txt` so real runs can provide a project-specific MEME output file.
- Document `results/standard_smoke/tables/motif_summary.tsv` as standard branch evidence in README and release audit docs.

Added:
- `tests/fixtures/mock_evidence/meme.txt`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `bin/genefam/run_standard_smoke.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_standard_smoke.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/standard_postprocess.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py -q` first failed because `motif_summary` was not in the standard report-index contract and `run_standard_smoke.py` did not write `tables/motif_summary.tsv`.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not mention `results/standard_smoke/tables/motif_summary.tsv`.
- `python -m pytest tests/test_runtime_environment_files.py::test_readme_documents_explicit_standard_identification_branch -q` first failed because README did not mention `motif_summary.tsv`.
- `python -m pytest tests/test_workflow_modules.py::test_main_workflow_includes_remaining_standard_analysis_processes -q` first failed because `workflows/main.nf` included but did not call `PARSE_MEME_MOTIFS`.
- `python -m pytest tests/test_runtime_environment_files.py::test_nextflow_config_has_container_profiles tests/test_workflow_modules.py::test_main_workflow_includes_remaining_standard_analysis_processes -q` first failed because `params.meme_txt` was not defined and `workflows/main.nf` used `mock_evidence_dir` directly for the MEME text input.
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py tests/test_parse_meme_motifs.py -q` passed with 21 tests after adding the standard smoke and report-index path.
- `python -m pytest tests/test_runtime_environment_files.py::test_nextflow_config_has_container_profiles tests/test_workflow_modules.py::test_main_workflow_includes_remaining_standard_analysis_processes tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_run_nextflow_standard_smoke.py tests/test_release_audit_docs.py -q` passed with 17 tests after parameterizing the MEME text input as `params.meme_txt`.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/standard_smoke` exited `0` and printed `motif_summary	results/standard_smoke/tables/motif_summary.tsv`.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` first failed at `BUILD_STANDARD_REPORT_INDEX` because Nextflow did not pass `--motif-summary`; after wiring `PARSE_MEME_MOTIFS.out` into `BUILD_STANDARD_REPORT_INDEX`, the same command exited `0`.
- `python -m pytest tests -q` passed with 199 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 14`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocked item remains Docker/Apptainer reproducibility.
- `results/standard_smoke/report/final_report.md` and `results/nextflow_standard_smoke/standard/report/final_report.md` both list `motif_summary` as available.

Commit:
- hash: 4381bb97712d2d344cd9be208137a76f956e97a2
- message: feat: surface motif summary in standard reports
- files: motif summary report integration, MEME fixture, Nextflow wiring, standard smoke, docs, tests, history

Next:
- Keep standard-branch report evidence aligned with each major analysis module: if a module is part of the user-facing workflow, its output should appear in the report index or an explicit missing/blocked row.

## 2026-06-25 - Add local acceptance entrypoint

Context:
- The long objective now has many evidence-producing commands: release checks, objective audit, quickstart handoff, Nextflow smokes, and runtime bootstrap.
- The repository is usable on the current machine except for Docker/Apptainer reproducibility, so a single local acceptance command should refresh the release evidence and still write handoff artifacts when the release gate exits non-zero.
- A script-level entrypoint makes the final workflow easier to rerun without copying several commands from README or quickstart docs.

Decisions:
- Add `scripts/run_local_acceptance.sh` as a small Bash wrapper around the release gate and quickstart handoff.
- Keep the release gate status authoritative: if Docker/Apptainer are still missing, the script exits with the release-gate status after printing the handoff files to inspect.
- Allow `PYTHON_BIN`, `CONDA_ENV`, `RELEASE_OUTDIR`, and `QUICKSTART_OUTDIR` overrides so the same script works with `/Users/liuyue/miniforge3/bin/python`, `GeneFamilyFlow`, and custom result folders.
- Document the script in `docs/quickstart.md` and README as the shortest local acceptance entrypoint.

Added:
- `scripts/run_local_acceptance.sh`
- `tests/test_local_acceptance_script.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/quickstart.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_local_acceptance_script.py -q` first failed because `scripts/run_local_acceptance.sh` did not exist and `docs/quickstart.md` did not mention the script.
- `python -m pytest tests/test_local_acceptance_script.py -q` passed with 2 tests after adding the script and docs.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected on this machine, after running the release gate and quickstart handoff.
- `results/release_checks/release_checks.md` reports `Passed: 14`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the remaining required failure is the readiness audit for missing `docker` and `apptainer`.
- `results/quickstart/quickstart_summary.md` reports both `standard_branch_smoke` and `prepared_wgd_handoff` as passed.
- `results/handoff/handoff_report.md` reports `Docker/Apptainer reproducibility` as the only blocked requirement and points to `bash results/readiness/runtime_bootstrap.sh`.
- `python -m pytest tests -q` passed with 201 tests.

Commit:
- hash: 1c374cb2edcba413896b11e4146d3aed42869904
- message: chore: add local acceptance entrypoint
- files: local acceptance script, quickstart docs, README, script contract tests, history

Next:
- Keep the local acceptance script as the first manual rerun command; after Docker/Apptainer are installed, rerun it to verify the container profiles and objective completion audit.

## 2026-06-25 - Add standard run configuration snapshot

Context:
- The final pipeline should be reusable for large, multi-species gene-family analyses, which means reports need to preserve not only results but also the exact run context.
- The standard branch already publishes species manifests and final reports, but it did not emit a compact snapshot of YAML-derived settings such as selected species, runtime, gene family, HMMER/DIAMOND switches, and final evidence rule.
- Without this snapshot, a future report reader would need to reconstruct run settings from command history and config files.

Decisions:
- Add `bin/genefam/build_run_config_snapshot.py` to write a stable `key/value` TSV from the YAML config and selected species manifest.
- Publish `tables/run_config_snapshot.tsv` in the standard branch and include it in `report/report_index.tsv`.
- Wire the same helper into the Nextflow standard branch through a `BUILD_RUN_CONFIG_SNAPSHOT` process.
- Document the snapshot as standard-branch release evidence.

Added:
- `bin/genefam/build_run_config_snapshot.py`
- `tests/test_build_run_config_snapshot.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `bin/genefam/run_standard_smoke.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_standard_smoke.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py -q` first failed because `run_config_snapshot` was not in the standard report-index contract and `run_standard_smoke.py` did not write `tables/run_config_snapshot.tsv`.
- `python -m pytest tests/test_build_run_config_snapshot.py tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_run_nextflow_standard_smoke.py tests/test_workflow_modules.py -q` passed with 32 tests after implementing the helper, standard smoke output, report-index path, and Nextflow process wiring.
- `python -m pytest tests/test_build_run_config_snapshot.py tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_run_nextflow_standard_smoke.py tests/test_workflow_modules.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` passed with 45 tests after updating release-audit documentation.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/standard_smoke` exited `0` and printed `run_config_snapshot	results/standard_smoke/tables/run_config_snapshot.tsv`.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` exited `0`.
- `results/standard_smoke/tables/run_config_snapshot.tsv` and `results/nextflow_standard_smoke/standard/tables/run_config_snapshot.tsv` both record `project.name`, `runtime.environment`, `/usr/local/bin/R`, selected species, gene family, HMMER/DIAMOND switches, and `identification.final_rule`.
- `results/standard_smoke/report/final_report.md` and `results/nextflow_standard_smoke/standard/report/final_report.md` both list `run_config_snapshot` as available.
- `python -m pytest tests -q` passed with 203 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 14`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the only required blocker remains the readiness audit for missing `docker` and `apptainer`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: b085bd7b741834d6c0cfd74f783b5d1edf96759c
- message: feat: add standard run config snapshot
- files: standard run config snapshot helper, Nextflow process wiring, report index integration, docs, tests, history

Next:
- Keep adding report-index evidence for user-facing outputs so final reports remain self-describing across large multi-species runs.

## 2026-06-25 - Add WGD run configuration snapshot

Context:
- The WGD/named-event branch interprets gamma, beta, alpha, theta labels from Ks-supported WGD layers and configured event metadata.
- Those interpretations depend on user-provided inputs: duplicate classifications, family members, Ka/Ks pairs, Ks bins, events config, and `--event` layer mappings.
- The WGD report already exposed result tables, but did not preserve these run parameters as a report-indexed artifact.

Decisions:
- Add `bin/genefam/build_wgd_run_config_snapshot.py` to write a stable `key/value` TSV for WGD branch inputs, Ks bins, and named-event mappings.
- Publish `tables/wgd_run_config_snapshot.tsv` from both the offline WGD smoke and the Nextflow WGD branch.
- Add `wgd_run_config_snapshot` to the WGD report index so final reports expose the interpretation context alongside evidence tables.
- Document the snapshot in README and release-audit evidence.

Added:
- `bin/genefam/build_wgd_run_config_snapshot.py`
- `tests/test_build_wgd_run_config_snapshot.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/build_wgd_report_index.py`
- `bin/genefam/run_nextflow_wgd_smoke.py`
- `bin/genefam/run_wgd_smoke.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_nextflow_wgd_smoke.py`
- `tests/test_run_wgd_smoke.py`
- `tests/test_wgd_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/duplication_retention.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_wgd_report_index.py tests/test_run_wgd_smoke.py -q` first failed because `wgd_run_config_snapshot` was missing from the WGD report index and `run_wgd_smoke.py` did not write `tables/wgd_run_config_snapshot.tsv`.
- `python -m pytest tests/test_build_wgd_run_config_snapshot.py tests/test_wgd_report_index.py tests/test_run_wgd_smoke.py tests/test_run_nextflow_wgd_smoke.py tests/test_workflow_modules.py -q` passed with 25 tests after implementing the helper, Python smoke output, report-index path, and Nextflow process wiring.
- `python -m pytest tests/test_build_wgd_run_config_snapshot.py tests/test_wgd_report_index.py tests/test_run_wgd_smoke.py tests/test_run_nextflow_wgd_smoke.py tests/test_workflow_modules.py tests/test_release_audit_docs.py -q` passed with 26 tests after updating release-audit documentation.
- `python bin/genefam/run_wgd_smoke.py --events-config configs/wgd_events.brassicaceae.yaml --outdir results/wgd_smoke` exited `0` and printed `wgd_run_config_snapshot	results/wgd_smoke/tables/wgd_run_config_snapshot.tsv`.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke` exited `0`.
- `results/wgd_smoke/tables/wgd_run_config_snapshot.tsv` and `results/nextflow_wgd_smoke/wgd/tables/wgd_run_config_snapshot.tsv` both record `events_config`, `ks_bins`, input table paths, and `event.WGD_layer_1` through `event.WGD_layer_4` mapped to `alpha`, `beta`, `gamma`, and `theta`.
- `results/wgd_smoke/report/final_report.md` and `results/nextflow_wgd_smoke/wgd/report/final_report.md` both list `wgd_run_config_snapshot` as available.
- `python -m pytest tests -q` passed with 206 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 14`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the required blocker remains the readiness audit for missing `docker` and `apptainer`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 183ba1e53e14dfb4b3eee46dc92a51ea4dab4ff6
- message: feat: add wgd run config snapshot
- files: WGD run config snapshot helper, WGD smoke and Nextflow wiring, report index integration, docs, tests, history

Next:
- Keep WGD interpretation artifacts self-describing, especially when users adjust Ks bins or map lineage-specific events beyond gamma, beta, alpha, and theta.

## 2026-06-25 - Add gene structure summary to standard branch

Context:
- The project scope includes motif and gene structure analysis.
- Motif summaries were already parsed and report-indexed, but gene structure evidence from species-bank GFF3 files was not yet emitted.
- The standard branch already consumes GFF3 for chromosome locations, so gene length, transcript count, exon count, CDS count, and exon/CDS total lengths can be derived from the same annotation source.

Decisions:
- Add `bin/genefam/extract_gene_structure.py` to summarize selected family members from GFF3 `gene`, transcript, exon, and CDS features.
- Publish `tables/gene_structure_summary.tsv` in Python and Nextflow standard-branch paths.
- Add `gene_structure_summary` to the standard report index so final reports expose the output.
- Document the output in README and release-audit evidence.

Added:
- `bin/genefam/extract_gene_structure.py`
- `tests/test_extract_gene_structure.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `bin/genefam/run_standard_smoke.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_standard_smoke.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/annotation_integration.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_extract_gene_structure.py tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_run_nextflow_standard_smoke.py tests/test_workflow_modules.py -q` first failed because `bin.genefam.extract_gene_structure` did not exist.
- After implementing the helper and wiring the standard branch, the same command first exposed a wrong test expectation for exon total length and a missing expected Nextflow output entry.
- `python -m pytest tests/test_extract_gene_structure.py tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_run_nextflow_standard_smoke.py tests/test_workflow_modules.py -q` passed with 33 tests after correcting the expectation and adding `gene_structure_summary.tsv` to the Nextflow standard smoke expected outputs.
- `python -m pytest tests/test_extract_gene_structure.py tests/test_standard_branch_report_index.py tests/test_run_standard_smoke.py tests/test_run_nextflow_standard_smoke.py tests/test_workflow_modules.py tests/test_release_audit_docs.py -q` passed with 34 tests after updating release-audit documentation.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/standard_smoke` exited `0` and printed `gene_structure_summary	results/standard_smoke/tables/gene_structure_summary.tsv`.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` exited `0`.
- `results/standard_smoke/tables/gene_structure_summary.tsv` and `results/nextflow_standard_smoke/standard/tables/gene_structure_summary.tsv` both contain `gene_length`, `transcript_count`, `exon_count`, `cds_count`, `exon_total_length`, and `cds_total_length`.
- `results/standard_smoke/report/final_report.md` and `results/nextflow_standard_smoke/standard/report/final_report.md` both list `gene_structure_summary` as available.
- `python -m pytest tests -q` passed with 209 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 14`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the only required blocker remains the readiness audit for missing `docker` and `apptainer`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: 6e908525cb2d2d83171df7316b6e498cfa63669d
- message: feat: add gene structure summary
- files: gene structure helper, standard smoke integration, Nextflow annotation wiring, report index integration, docs, tests, history

Next:
- Keep GFF3-derived outputs aligned: chromosome coordinates and gene structure summaries should remain sourced from the same species-bank annotation contract.

## 2026-06-25 - Add release-level expression smoke

Context:
- RNA-seq expression integration existed as a standard-branch option and unit-tested helper, but the release gate only exercised the standard branch without an expression matrix.
- The long objective requires expression integration as part of the final reusable workflow, so release evidence should prove a real family expression subset is produced.

Decisions:
- Add a small expression fixture with family and non-family rows.
- Add `standard branch expression smoke` to the required release checks.
- Tighten the objective audit so chromosome/expression integration requires the expression smoke, not only the no-expression standard smoke.
- Document the release-level expression output in README and release audit evidence.

Added:
- `tests/fixtures/expression/family_expression.tsv`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_standard_branch_expression_smoke_before_readiness -q` first failed because `standard branch expression smoke` was not in `default_checks()`.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_standard_branch_expression_smoke_before_readiness tests/test_run_release_checks.py::test_write_objective_audit_requires_expression_smoke_for_expression_integration -q` then failed because the objective audit still considered expression integration achieved without expression smoke evidence.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_standard_branch_expression_smoke_before_readiness tests/test_run_release_checks.py::test_write_objective_audit_requires_expression_smoke_for_expression_integration -q` passed after adding the release check and tightening the audit.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because release audit did not mention `results/standard_expression_smoke/tables/family_expression.tsv`.
- `python -m pytest tests/test_run_release_checks.py tests/test_release_audit_docs.py tests/test_run_standard_smoke.py -q` passed with 25 tests after documenting release-level expression evidence.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --expression-matrix tests/fixtures/expression/family_expression.tsv --outdir results/standard_expression_smoke` exited `0` and printed `family_expression	results/standard_expression_smoke/tables/family_expression.tsv`.
- `results/standard_expression_smoke/tables/family_expression.tsv` contains only the two identified family members and excludes `unused_gene`.
- `results/standard_expression_smoke/report/report_index.tsv` lists `family_expression` as `available`.
- `python -m pytest tests -q` passed with 211 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 15`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `standard branch expression smoke` passed, and the required blocker remains the readiness audit for missing `docker` and `apptainer`.
- `results/objective_audit/objective_audit.md` reports `chromosome and expression integration` achieved using `standard branch, expression smoke, and quickstart outputs`; overall completion remains blocked only by Docker/Apptainer reproducibility.

Commit:
- hash: 8d5ce859f871def2925d3fb790a83fa068ecc78a
- message: test: add expression release smoke
- files: expression fixture, release check runner, objective audit, release docs, README, tests, history

Next:
- Keep release-level evidence aligned with the long objective, especially where optional modules become required proof points for the final usable version.

## 2026-06-25 - Add expression heatmap smoke plotting

Context:
- The standard branch could subset RNA-seq expression matrices and the Nextflow plot module defined an expression heatmap process.
- The Python standard smoke and release expression smoke did not yet prove `/usr/local/bin/R` generated the expression heatmap PDF.

Decisions:
- Run `scripts/plot_expression_heatmap.R` from `run_standard_smoke.py` whenever `--expression-matrix` is supplied.
- Keep `/usr/local/bin/R` as the default plotting binary and pass it explicitly from the release expression smoke.
- Add `expression_heatmap` to the expression smoke outputs, plot manifest, and final report.
- Document the generated PDF in README and release-audit evidence.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_release_checks.py`
- `bin/genefam/run_standard_smoke.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_run_standard_smoke.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_standard_smoke.py::test_run_standard_smoke_writes_family_expression_when_matrix_is_provided -q` first failed because `plots/expression_heatmap.pdf` was not generated.
- `python -m pytest tests/test_run_standard_smoke.py::test_run_standard_smoke_writes_family_expression_when_matrix_is_provided -q` passed after `run_standard_smoke.py` called `scripts/plot_expression_heatmap.R`.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_standard_branch_expression_smoke_before_readiness tests/test_release_audit_docs.py -q` then failed because the release expression smoke did not explicitly pass `--r-bin /usr/local/bin/R` and release audit did not mention `results/standard_expression_smoke/plots/expression_heatmap.pdf`.
- `python -m pytest tests/test_run_standard_smoke.py tests/test_run_release_checks.py::test_default_checks_include_standard_branch_expression_smoke_before_readiness tests/test_release_audit_docs.py -q` passed with 4 tests after wiring the explicit R path and heatmap documentation.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --expression-matrix tests/fixtures/expression/family_expression.tsv --r-bin /usr/local/bin/R --outdir results/standard_expression_smoke` exited `0` and printed `expression_heatmap	results/standard_expression_smoke/plots/expression_heatmap.pdf`.
- `results/standard_expression_smoke/plots/expression_heatmap.pdf` exists and is generated by `/usr/local/bin/R`.
- `results/standard_expression_smoke/report/plot_manifest.tsv` and `results/standard_expression_smoke/report/final_report.md` both list `expression_heatmap`.
- `python -m pytest tests -q` passed with 211 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 15`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `standard branch expression smoke` passed with `--r-bin /usr/local/bin/R` and lists `expression_heatmap`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.

Commit:
- hash: bb163fe5ae4269c254d70aaabe2f7b3653e1bdda
- message: feat: add expression heatmap smoke
- files: standard smoke plotting, release expression smoke, release docs, README, tests, history

Next:
- Keep plot outputs tied to concrete report entries so generated PDFs are not invisible artifacts.

## 2026-06-25 - Add synteny parser release smoke

Context:
- MCScanX `.collinearity` parsing had unit coverage, but the release gate did not yet produce a concrete `syntenic_pairs.tsv` artifact.
- The WGD/named-event evidence chain depends on synteny evidence before Ks-layer and event-name interpretation.

Decisions:
- Add a small MCScanX `.collinearity` fixture.
- Add `bin/genefam/run_synteny_smoke.py` to parse that fixture into `tables/syntenic_pairs.tsv` plus a Markdown smoke summary.
- Add `synteny parser smoke` to the release gate before the WGD event smoke.
- Tighten the objective audit so gamma/beta/alpha/theta evidence requires synteny parser evidence as well as WGD handoff outputs.
- Document the synteny smoke in README and release audit.

Added:
- `bin/genefam/run_synteny_smoke.py`
- `tests/fixtures/mcscanx/sample.collinearity`
- `tests/test_run_synteny_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_synteny_smoke.py tests/test_run_release_checks.py::test_default_checks_include_synteny_parser_smoke_before_wgd_smoke tests/test_audit_objective_completion.py::test_wgd_event_evidence_requires_synteny_parser_smoke -q` first failed because `run_synteny_smoke.py` did not exist, `synteny parser smoke` was not in release checks, and WGD objective evidence did not require synteny parser evidence.
- The same command passed with 3 tests after adding the smoke script, release check, and objective-audit requirement.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because release audit did not mention `run_synteny_smoke.py`.
- `python -m pytest tests/test_run_synteny_smoke.py tests/test_run_release_checks.py::test_default_checks_include_synteny_parser_smoke_before_wgd_smoke tests/test_audit_objective_completion.py::test_wgd_event_evidence_requires_synteny_parser_smoke tests/test_release_audit_docs.py -q` passed with 4 tests after documenting the smoke.
- `python bin/genefam/run_synteny_smoke.py --collinearity tests/fixtures/mcscanx/sample.collinearity --outdir results/synteny_smoke` exited `0` and printed `syntenic_pairs	results/synteny_smoke/tables/syntenic_pairs.tsv`.
- `results/synteny_smoke/tables/syntenic_pairs.tsv` contains two MCScanX-derived syntenic pairs.
- `results/synteny_smoke/synteny_smoke.md` reports `Parsed syntenic pairs: 2`.
- `python -m pytest tests -q` passed with 214 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 16`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `synteny parser smoke` passed and lists `results/synteny_smoke/tables/syntenic_pairs.tsv`.
- `results/objective_audit/objective_audit.md` reports WGD gamma/beta/alpha/theta evidence achieved from `synteny parser smoke, WGD event smoke, and prepared WGD handoff checks`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: 21bfc9d5a7121272b1b46866ea7d9334e1a50501
- message: feat: add synteny parser smoke
- files: synteny smoke helper, MCScanX fixture, release gate, objective audit, docs, tests, history

Next:
- Keep prepared-table WGD inputs traceable to parser-level artifacts such as MCScanX collinearity outputs.

## 2026-06-25 - Add domain filter release smoke

Context:
- Domain filtering is an explicit target module and had unit coverage, but the release gate did not yet produce a filtered HMMER-domain artifact.
- The standard branch depends on HMMER domain thresholds before downstream candidate merging and reporting.

Decisions:
- Add a normalized HMMER domain fixture with passing and failing rows.
- Add `bin/genefam/run_domain_filter_smoke.py` to apply e-value, bitscore, and domain-coverage thresholds and write `tables/filtered_domains.tsv`.
- Add `domain filter smoke` to the release gate before the standard branch smoke.
- Tighten the objective audit so the standard identification branch requires domain filter smoke evidence.
- Document the smoke in README and release audit.

Added:
- `bin/genefam/run_domain_filter_smoke.py`
- `tests/fixtures/hmmer_domains/domains.tsv`
- `tests/test_run_domain_filter_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_domain_filter_smoke.py tests/test_run_release_checks.py::test_default_checks_include_domain_filter_smoke_before_standard_branch_smoke tests/test_audit_objective_completion.py::test_standard_identification_branch_requires_domain_filter_smoke -q` first failed because `run_domain_filter_smoke.py` did not exist, `domain filter smoke` was not in release checks, and the standard identification audit did not require domain filter evidence.
- The same command initially left one failure because the audit evidence text did not use the exact `domain filter smoke` check name.
- `python -m pytest tests/test_run_domain_filter_smoke.py tests/test_run_release_checks.py::test_default_checks_include_domain_filter_smoke_before_standard_branch_smoke tests/test_audit_objective_completion.py::test_standard_identification_branch_requires_domain_filter_smoke -q` passed with 3 tests after adding the smoke and tightening the audit wording.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because release audit did not mention `run_domain_filter_smoke.py`.
- `python -m pytest tests/test_run_domain_filter_smoke.py tests/test_run_release_checks.py::test_default_checks_include_domain_filter_smoke_before_standard_branch_smoke tests/test_audit_objective_completion.py::test_standard_identification_branch_requires_domain_filter_smoke tests/test_release_audit_docs.py -q` passed with 4 tests after documenting the smoke.
- `python bin/genefam/run_domain_filter_smoke.py --input tests/fixtures/hmmer_domains/domains.tsv --max-evalue 1e-10 --min-bitscore 50 --min-domain-coverage 0.5 --outdir results/domain_filter_smoke` exited `0` and printed `filtered_domains	results/domain_filter_smoke/tables/filtered_domains.tsv`.
- `results/domain_filter_smoke/tables/filtered_domains.tsv` contains the two retained HMMER domain rows after thresholding.
- `results/domain_filter_smoke/domain_filter_smoke.md` reports `Input domains: 4` and `Filtered domains: 2`.
- `python -m pytest tests -q` passed with 217 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 17`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `domain filter smoke` passed and lists `results/domain_filter_smoke/tables/filtered_domains.tsv`.
- `results/objective_audit/objective_audit.md` reports the standard identification branch achieved from `domain filter smoke, Python standard branch, and Nextflow standard branch smoke checks`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: 15551e455bd17e01acc41f7fbf5797fc8439383a
- message: feat: add domain filter smoke
- files: domain filter smoke helper, HMMER domain fixture, release gate, objective audit, docs, tests, history

Next:
- Keep standard-branch release evidence close to the actual decision points: domain filtering, candidate merging, summaries, plots, and reports.

## 2026-06-25 - Add Ka/Ks parser release smoke

Context:
- Ka/Ks parsing and prepared WGD outputs existed, but the release gate did not yet produce a direct normalized Ka/Ks selection-pressure artifact.
- The long objective explicitly requires Ka/Ks selection pressure analysis as part of the duplication/WGD evidence chain.

Decisions:
- Add a KaKs_Calculator-style fixture with purifying, neutral, and positive selection examples.
- Add `bin/genefam/run_kaks_smoke.py` to normalize Ka/Ks rows through the existing parser and write `tables/normalized_kaks.tsv`.
- Add `Ka/Ks parser smoke` to the release gate between synteny parsing and WGD event interpretation.
- Tighten the objective audit so Ka/Ks and retention analysis requires the parser smoke as well as WGD/retention handoff evidence.
- Document the smoke in README and release audit.

Added:
- `bin/genefam/run_kaks_smoke.py`
- `tests/fixtures/kaks/kaks_calculator.tsv`
- `tests/test_run_kaks_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_kaks_smoke.py tests/test_run_release_checks.py::test_default_checks_include_kaks_smoke_before_wgd_smoke tests/test_audit_objective_completion.py::test_kaks_and_retention_analysis_requires_kaks_parser_smoke tests/test_release_audit_docs.py -q` first failed because `run_kaks_smoke.py` did not exist, `Ka/Ks parser smoke` was not in release checks, the objective audit still accepted Ka/Ks/retention evidence without it, and release audit did not mention `run_kaks_smoke.py`.
- The same command passed with 4 tests after adding the smoke, release check, objective-audit requirement, and documentation.
- `python bin/genefam/run_kaks_smoke.py --kaks tests/fixtures/kaks/kaks_calculator.tsv --outdir results/kaks_smoke` exited `0` and printed `normalized_kaks	results/kaks_smoke/tables/normalized_kaks.tsv`.
- `results/kaks_smoke/tables/normalized_kaks.tsv` contains purifying, neutral, and positive `selection_category` rows.
- `results/kaks_smoke/kaks_smoke.md` reports `Input pairs: 3`, `purifying: 1`, `neutral: 1`, and `positive: 1`.
- `python -m pytest tests -q` passed with 220 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 18`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `Ka/Ks parser smoke` passed and lists `results/kaks_smoke/tables/normalized_kaks.tsv`.
- `results/objective_audit/objective_audit.md` reports Ka/Ks and retention analysis achieved from `Ka/Ks parser smoke and WGD/retention smoke outputs`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: 10079bc39457a86a8dca05150729524c024ab6bf
- message: feat: add kaks parser smoke
- files: Ka/Ks parser smoke helper, KaKs_Calculator fixture, release gate, objective audit, docs, tests, history

Next:
- Keep Ka/Ks evidence traceable from calculator-style input through normalized selection categories and WGD retention summaries.

## 2026-06-25 - Add motif parser release smoke

Context:
- Motif parsing was exercised inside the standard branch, but it did not yet have an independent release smoke artifact like domain filtering, synteny, and Ka/Ks.
- The long objective explicitly includes motif analysis, so release evidence should expose the MEME parser output directly.

Decisions:
- Add `bin/genefam/run_motif_smoke.py` to parse the existing MEME fixture through `parse_meme_motifs.py`.
- Write `results/motif_smoke/tables/motif_summary.tsv` plus a concise Markdown smoke summary.
- Add `motif parser smoke` to the release gate after domain filtering and before the standard branch smoke.
- Tighten the objective audit so the standard identification branch requires motif parser smoke evidence.
- Document the smoke in README and release audit.

Added:
- `bin/genefam/run_motif_smoke.py`
- `tests/test_run_motif_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_motif_smoke.py tests/test_run_release_checks.py::test_default_checks_include_motif_smoke_before_standard_branch_smoke tests/test_audit_objective_completion.py::test_standard_identification_branch_requires_motif_parser_smoke tests/test_release_audit_docs.py -q` first failed because `run_motif_smoke.py` did not exist, `motif parser smoke` was not in release checks, the standard identification audit still accepted evidence without it, and release audit did not mention `run_motif_smoke.py`.
- The same command passed with 4 tests after adding the smoke, release check, objective-audit requirement, and documentation.
- `python bin/genefam/run_motif_smoke.py --meme-txt tests/fixtures/mock_evidence/meme.txt --family-name GDSL --outdir results/motif_smoke` exited `0` and printed `motif_summary	results/motif_smoke/tables/motif_summary.tsv`.
- `results/motif_smoke/tables/motif_summary.tsv` contains two parsed MEME motifs, `GDSL_motif_1` and `GDSL_motif_2`.
- `results/motif_smoke/motif_smoke.md` reports `Parsed motifs: 2`.
- `python -m pytest tests -q` passed with 223 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 19`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `motif parser smoke` passed and lists `results/motif_smoke/tables/motif_summary.tsv`.
- `results/objective_audit/objective_audit.md` reports the standard identification branch achieved from `domain filter smoke, motif parser smoke, Python standard branch, and Nextflow standard branch smoke checks`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: d44e2dd9dcf38e5b9abc05410c2d45c682d36b88
- message: feat: add motif parser smoke
- files: motif parser smoke helper, release gate, objective audit, README, release audit, tests, history

Next:
- Continue making each major objective module independently visible in the release gate, especially where a parser feeds a larger branch.

## 2026-06-25 - Add chromosome location release smoke

Context:
- Chromosome locations were generated inside the standard branch, but the GFF3 coordinate extraction path did not yet have an independent release smoke artifact.
- The long objective explicitly includes chromosome localization and RNA-seq expression integration, so the chromosome side of that evidence should be visible on its own.

Decisions:
- Add `bin/genefam/run_chromosome_smoke.py` to discover the configured species bank, merge mock family evidence, and extract GFF3 chromosome locations with the existing helper.
- Write `results/chromosome_smoke/tables/species_manifest.tsv`, `family_candidates.tsv`, and `chromosome_locations.tsv`.
- Add `chromosome location smoke` to the release gate between the standard branch smoke and expression smoke.
- Tighten the objective audit so chromosome/expression integration requires chromosome location smoke evidence.
- Document the smoke in README and release audit.

Added:
- `bin/genefam/run_chromosome_smoke.py`
- `tests/test_run_chromosome_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_chromosome_smoke.py tests/test_run_release_checks.py::test_default_checks_include_chromosome_smoke_before_expression_smoke tests/test_audit_objective_completion.py::test_chromosome_and_expression_integration_requires_chromosome_smoke tests/test_release_audit_docs.py -q` first failed because `run_chromosome_smoke.py` did not exist, `chromosome location smoke` was not in release checks, chromosome/expression audit evidence did not require it, and release audit did not mention `run_chromosome_smoke.py`.
- The same command passed with 4 tests after adding the smoke, release check, objective-audit requirement, and documentation.
- `python bin/genefam/run_chromosome_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/chromosome_smoke` exited `0` and printed `chromosome_locations	results/chromosome_smoke/tables/chromosome_locations.tsv`.
- `results/chromosome_smoke/tables/chromosome_locations.tsv` contains `Arabidopsis_thaliana	AT1G01010	Chr1	100	500	+` and `Brassica_rapa	BraA010001	A01	200	900	-`.
- `results/chromosome_smoke/chromosome_smoke.md` reports `Located genes: 2` and `Species represented: 2`.
- `python -m pytest tests -q` passed with 226 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 20`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `chromosome location smoke` passed and lists `results/chromosome_smoke/tables/chromosome_locations.tsv`.
- `results/objective_audit/objective_audit.md` reports chromosome and expression integration achieved from `chromosome location smoke, standard branch, expression smoke, and quickstart outputs`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: d49f72b5b1620322adf7571bd8f044ea8a60f006
- message: feat: add chromosome location smoke
- files: chromosome location smoke helper, release gate, objective audit, README, release audit, tests, history

Next:
- Continue exposing standalone release evidence for modules that currently only appear inside larger branch outputs.

## 2026-06-25 - Add alignment phylogeny release smoke

Context:
- Alignment and phylogeny manifests were generated inside the mock and standard branches, but the external aligner/tree-builder handoff did not yet have an independent release smoke artifact.
- The long objective explicitly includes alignment and phylogenetic analysis, so release evidence should expose those manifests directly rather than only through larger branch outputs.

Decisions:
- Add `bin/genefam/run_alignment_phylogeny_smoke.py` to reuse the existing alignment and phylogeny manifest helpers on a small family FASTA fixture.
- Write `results/alignment_phylogeny_smoke/tables/alignment_manifest.tsv`, `results/alignment_phylogeny_smoke/tables/phylogeny_manifest.tsv`, and a concise Markdown smoke summary.
- Add `alignment phylogeny smoke` to the release gate after the expression smoke and before synteny/WGD checks.
- Tighten the objective audit so the Nextflow DSL2 workflow requirement requires explicit alignment/phylogeny smoke evidence.
- Document the smoke in README and the release audit matrix.

Added:
- `bin/genefam/run_alignment_phylogeny_smoke.py`
- `tests/fixtures/alignment/family_members.faa`
- `tests/test_run_alignment_phylogeny_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_alignment_phylogeny_smoke.py tests/test_run_release_checks.py::test_default_checks_include_alignment_phylogeny_smoke_before_synteny_smoke tests/test_audit_objective_completion.py::test_nextflow_dsl2_requires_alignment_phylogeny_smoke_evidence tests/test_release_audit_docs.py -q` first failed because `run_alignment_phylogeny_smoke.py` did not exist, `alignment phylogeny smoke` was not in release checks, the objective audit still accepted Nextflow DSL2 evidence without it, and release audit did not mention `run_alignment_phylogeny_smoke.py`.
- The same command passed with 4 tests after adding the smoke, release check, objective-audit requirement, and documentation.
- `python bin/genefam/run_alignment_phylogeny_smoke.py --family-name GDSL --fasta tests/fixtures/alignment/family_members.faa --aligner mafft --tree-builder iqtree --outdir results/alignment_phylogeny_smoke` exited `0` and printed `alignment_manifest`, `phylogeny_manifest`, and `summary` outputs.
- `results/alignment_phylogeny_smoke/tables/alignment_manifest.tsv` contains one `GDSL	mafft	3` row with raw and trimmed alignment paths.
- `results/alignment_phylogeny_smoke/tables/phylogeny_manifest.tsv` contains one `GDSL	iqtree` row with treefile and support paths.
- `results/alignment_phylogeny_smoke/alignment_phylogeny_smoke.md` reports `Sequence count: 3`, `Aligner: mafft`, and `Tree builder: iqtree`.
- `python -m pytest tests -q` passed with 229 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 21`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `alignment phylogeny smoke` passed and lists both alignment and phylogeny manifests.
- `results/objective_audit/objective_audit.md` reports `Nextflow DSL2 workflow` achieved with `Nextflow mock, standard, single-tool, WGD, and alignment phylogeny smoke checks`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: 061378e0e69c745820dfb9d464ee8e75bbc69d85
- message: feat: add alignment phylogeny smoke
- files: alignment/phylogeny smoke helper, FASTA fixture, release gate, objective audit, README, release audit, tests, history

Next:
- Continue exposing standalone release evidence for any remaining major modules that are only visible inside larger branch outputs.

## 2026-06-25 - Add gene structure release smoke

Context:
- Gene-structure summaries were produced inside the standard branch, but the species-bank GFF3 to family-candidate structure extraction path did not yet have an independent release smoke artifact.
- The long objective and README planned scope include motif and gene structure analysis, so gene structure evidence should be directly visible in the release gate.

Decisions:
- Add `bin/genefam/run_gene_structure_smoke.py` to reuse species-bank discovery, mock HMMER/DIAMOND evidence merging, and `extract_gene_structure.py`.
- Write `results/gene_structure_smoke/tables/species_manifest.tsv`, `family_candidates.tsv`, and `gene_structure_summary.tsv`.
- Add `gene structure smoke` to the release gate after the standard branch smoke and before chromosome/location and expression checks.
- Tighten the objective audit so the standard identification branch requires explicit gene-structure smoke evidence.
- Document the smoke in README and the release audit matrix.

Added:
- `bin/genefam/run_gene_structure_smoke.py`
- `tests/test_run_gene_structure_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_gene_structure_smoke.py tests/test_run_release_checks.py::test_default_checks_include_gene_structure_smoke_before_chromosome_smoke tests/test_audit_objective_completion.py::test_standard_identification_branch_requires_gene_structure_smoke tests/test_release_audit_docs.py -q` first failed because `run_gene_structure_smoke.py` did not exist, `gene structure smoke` was not in release checks, the objective audit still accepted standard-branch evidence without it, and release audit did not mention `run_gene_structure_smoke.py`.
- The same command passed with 4 tests after adding the smoke, release check, objective-audit requirement, and documentation.
- `python bin/genefam/run_gene_structure_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/gene_structure_smoke` exited `0` and printed `gene_structure_summary	results/gene_structure_smoke/tables/gene_structure_summary.tsv`.
- `results/gene_structure_smoke/tables/gene_structure_summary.tsv` contains `Arabidopsis_thaliana	AT1G01010	401	0	0	0	0	0` and `Brassica_rapa	BraA010001	701	0	0	0	0	0`.
- `results/gene_structure_smoke/gene_structure_smoke.md` reports `Structured genes: 2` and `Species represented: 2`.
- `python -m pytest tests -q` passed with 232 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 22`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `gene structure smoke` passed and lists `results/gene_structure_smoke/tables/gene_structure_summary.tsv`.
- `results/objective_audit/objective_audit.md` reports the standard identification branch achieved from `domain filter smoke, motif parser smoke, gene structure smoke, Python standard branch, and Nextflow standard branch smoke checks`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: ee15597019df46c5c6708e8d72ef5ba4b3e95de2
- message: feat: add gene structure smoke
- files: gene structure smoke helper, release gate, objective audit, README, release audit, tests, history

Next:
- Continue exposing standalone release evidence where broad objective items are still represented only indirectly.

## 2026-06-25 - Add retention enrichment release smoke

Context:
- Duplicate-type retention enrichment was produced inside the WGD smoke and Nextflow duplication-retention branch, but the enrichment helper chain did not yet have an independent release smoke artifact.
- The long objective explicitly includes retention enrichment analysis, so release evidence should expose duplicate normalization, family duplicate classification, and enrichment statistics directly.

Decisions:
- Add `bin/genefam/run_retention_enrichment_smoke.py` to reuse `normalize_duplicate_types.py`, `join_family_duplicates.py`, and `retention_enrichment.py`.
- Use `examples/prepared_wgd_handoff/family_candidates.tsv` and `examples/prepared_wgd_handoff/duplicate_types.tsv` as the stable prepared-input contract.
- Write `results/retention_enrichment_smoke/tables/normalized_duplicate_types.tsv`, `family_duplicate_classification.tsv`, and `retention_enrichment.tsv`.
- Add `retention enrichment smoke` to the release gate after the Ka/Ks parser smoke and before the WGD event smoke.
- Tighten the objective audit so Ka/Ks and retention analysis requires explicit retention enrichment smoke evidence.
- Document the smoke in README and the release audit matrix.

Added:
- `bin/genefam/run_retention_enrichment_smoke.py`
- `tests/test_run_retention_enrichment_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_retention_enrichment_smoke.py tests/test_run_release_checks.py::test_default_checks_include_retention_enrichment_smoke_before_wgd_smoke tests/test_audit_objective_completion.py::test_kaks_and_retention_analysis_requires_retention_enrichment_smoke tests/test_release_audit_docs.py -q` first failed because `run_retention_enrichment_smoke.py` did not exist, `retention enrichment smoke` was not in release checks, the objective audit still accepted retention evidence without it, and release audit did not mention `run_retention_enrichment_smoke.py`.
- The same command passed with 4 tests after adding the smoke, release check, objective-audit requirement, and documentation.
- `python bin/genefam/run_retention_enrichment_smoke.py --family-members examples/prepared_wgd_handoff/family_candidates.tsv --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv --outdir results/retention_enrichment_smoke` exited `0` and printed `retention_enrichment	results/retention_enrichment_smoke/tables/retention_enrichment.tsv`.
- `results/retention_enrichment_smoke/tables/retention_enrichment.tsv` contains `WGD/segmental	8	8	8	12	1.5000	0.0020202` plus dispersed, singleton, and tandem background rows with zero family counts.
- `results/retention_enrichment_smoke/tables/family_duplicate_classification.tsv` classifies all eight prepared family genes as `WGD/segmental`.
- `results/retention_enrichment_smoke/retention_enrichment_smoke.md` reports `Family genes: 8`, `Background genes: 12`, and `Enrichment rows: 4`.
- `python -m pytest tests -q` passed with 235 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 23`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `retention enrichment smoke` passed and lists `results/retention_enrichment_smoke/tables/retention_enrichment.tsv`.
- `results/objective_audit/objective_audit.md` reports Ka/Ks and retention analysis achieved from `Ka/Ks parser smoke, retention enrichment smoke, and WGD/retention smoke outputs`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: bf8c147e3bfb6e316637f88d208e16887ec17dee
- message: feat: add retention enrichment smoke
- files: retention enrichment smoke helper, release gate, objective audit, README, release audit, tests, history

Next:
- Continue making broad objective items independently auditable while preserving Docker/Apptainer as the only current release blocker.

## 2026-06-25 - Refresh runtime bootstrap final acceptance path

Context:
- The runtime bootstrap plan already described how to rebuild the `GeneFamilyFlow` environment and container artifacts.
- After the Docker/Apptainer gap is fixed, the generated shell script and Markdown plan should also tell the user how to refresh the handoff report and delivery bundle from the same final evidence set.

Decisions:
- Keep `scripts/run_local_acceptance.sh` as the single final local acceptance wrapper after container/runtime repair.
- Add the wrapper to `results/readiness/runtime_bootstrap.sh`.
- Mention `results/delivery_bundle/delivery_bundle.md` as the final user-facing index after local acceptance.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/plan_runtime_bootstrap.py`
- `tests/test_plan_runtime_bootstrap.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` first failed because the generated bootstrap shell did not include `bash scripts/run_local_acceptance.sh`.
- The same focused test passed with 3 tests after adding the local acceptance command and delivery-bundle note.
- `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` refreshed `results/readiness/runtime_bootstrap_plan.md` and `results/readiness/runtime_bootstrap.sh`.
- `python -m pytest tests -q` passed with 244 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 25`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `244 passed`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.
- `results/readiness/runtime_bootstrap_plan.md` now instructs the user to run `bash scripts/run_local_acceptance.sh` after the runtime gap is closed and open `results/delivery_bundle/delivery_bundle.md`.

Commit:
- hash: bbfb5819f3194470ec07e40da0abd0bfe202570a
- message: chore: refresh runtime bootstrap acceptance path
- files: runtime bootstrap helper, bootstrap test, history

Next:
- Commit this runtime bootstrap handoff update, then continue tightening any remaining final-delivery evidence while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Add runtime recovery entries to delivery bundle

Context:
- The delivery bundle is the final user-facing index for reports, WGD evidence, Reference governance, runtime status, and documentation.
- Runtime recovery artifacts were generated by the release gate but were not directly listed in the final delivery bundle.

Decisions:
- Add a `runtime_recovery` section to the delivery manifest.
- Index the bootstrap Markdown plan, executable bootstrap shell script, and local acceptance wrapper from the final bundle.
- Keep runtime recovery separate from runtime command availability so missing `docker` and `apptainer` stay visible while the recovery path remains easy to find.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `runtime_recovery/bootstrap_plan` was absent from the generated delivery manifest.
- The same focused test passed with 1 test after adding runtime recovery manifest rows and Markdown wording.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` refreshed the delivery bundle outputs.
- `python -m pytest tests -q` passed with 244 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 25`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `244 passed`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.
- `results/delivery_bundle/delivery_manifest.tsv` now contains `runtime_recovery` rows for `runtime_bootstrap_plan.md`, `runtime_bootstrap.sh`, and `scripts/run_local_acceptance.sh`.

Commit:
- hash: 31f36d40138379b5aa079aaa83c5346524a348dd
- message: feat: index runtime recovery in delivery bundle
- files: delivery bundle helper, delivery bundle test, history

Next:
- Commit this delivery-bundle recovery index update, then keep the current project state ready for final runtime verification once Docker/Apptainer are available.

## 2026-06-25 - Synchronize runtime recovery docs

Context:
- The delivery bundle now indexes runtime recovery artifacts directly.
- README, readiness checklist, and runtime environment docs needed to describe the same final handoff shape.

Decisions:
- Document runtime recovery as part of the delivery bundle alongside standard reports, WGD evidence, Reference governance, runtime availability, and documentation.
- Point users to `scripts/run_local_acceptance.sh` after Docker/Apptainer are repaired so handoff and delivery bundle outputs refresh from the final evidence set.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/readiness_checklist.md`
- `docs/runtime_environment.md`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py -q` first failed because README, readiness checklist, and runtime environment docs did not yet mention the runtime recovery contract.
- The same focused test passed with 12 tests after synchronizing the docs.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` passed with 3 tests.
- `python -m pytest tests -q` passed with 244 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 25`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `244 passed`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.

Commit:
- hash: f650d9e4152bf99d53e3f7d4f699a4286abab976
- message: docs: synchronize runtime recovery handoff
- files: README, readiness/runtime docs, doc tests, history

Next:
- Commit the runtime recovery documentation sync, then continue from the clean runtime-blocked state.

## 2026-06-25 - Expose WGD event provenance in final report

Context:
- The WGD event evidence builder already records `evidence_source`, `species_scope`, and `expected_relative_age` for configured events such as alpha, beta, gamma, and theta.
- The final Markdown report only displayed the event layer, name, pair count, Ks median, interpretation status, and species scope, so part of the event interpretation evidence chain was hidden from the user-facing report.

Decisions:
- Extend the WGD Event Evidence table in `assemble_report.py` to include `evidence_source` and `expected_relative_age`.
- Keep the change limited to final report rendering; upstream evidence tables and Nextflow wiring already carry the fields.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/assemble_report.py`
- `tests/test_assemble_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_assemble_report.py -q` first failed because the final report WGD Event Evidence table did not contain `evidence_source` or `expected_relative_age`.
- The same focused test passed with 3 tests after extending the WGD Event Evidence table.
- `python bin/genefam/run_prepared_wgd_handoff_example.py --conda-env GeneFamilyFlow --example-dir examples/prepared_wgd_handoff --outdir results/example_prepared_wgd` exited `0`.
- `results/example_prepared_wgd/report/final_report.md` now displays `evidence_source` and `expected_relative_age` for alpha, beta, gamma, and theta rows.
- `python -m pytest tests -q` passed with 244 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 25`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `244 passed`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.

Commit:
- hash: b66dd5e317860c0dd09d2b0fe5ad9c3827366094
- message: feat: expose WGD event provenance in report
- files: final report assembler, report tests, history

Next:
- Commit the WGD event provenance report update, then continue only with work that can improve the final deliverable without requiring Docker/Apptainer.

## 2026-06-25 - Add run configuration snapshot to final reports

Context:
- Standard and WGD branches already generated `run_config_snapshot.tsv` or `wgd_run_config_snapshot.tsv`.
- The final Markdown reports listed those files as available outputs, but did not display the key runtime, species selection, identification rule, Ks-bin, or WGD event mapping parameters inline.

Decisions:
- Add an optional `run_config_snapshot` input to `assemble_report.py`.
- Render a `Run Configuration Snapshot` section near the top of every final report when a key/value snapshot is supplied.
- Wire the standard Nextflow report module to pass `BUILD_RUN_CONFIG_SNAPSHOT.out`.
- Wire the WGD Nextflow report module to pass `BUILD_WGD_RUN_CONFIG_SNAPSHOT.out`.
- Update the Python standard smoke so local smoke reports expose the same run configuration section.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/assemble_report.py`
- `bin/genefam/run_standard_smoke.py`
- `workflows/main.nf`
- `workflows/modules/standard_postprocess.nf`
- `workflows/modules/duplication_retention.nf`
- `tests/test_assemble_report.py`
- `tests/test_run_standard_smoke.py`
- `tests/test_workflow_modules.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_assemble_report.py tests/test_run_standard_smoke.py tests/test_workflow_modules.py -q` first failed because `assemble_report.py` had no `run_config_snapshot` argument or CLI option, standard smoke final reports did not display a run configuration section, and Nextflow report modules were not passing run config snapshots.
- The same focused test passed with 21 tests after adding the report section and Nextflow wiring.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/standard_smoke` exited `0`.
- `python bin/genefam/run_prepared_wgd_handoff_example.py --conda-env GeneFamilyFlow --example-dir examples/prepared_wgd_handoff --outdir results/example_prepared_wgd` exited `0`.
- `results/standard_smoke/report/final_report.md` now displays `runtime.environment`, `selected_species`, and `identification.final_rule` in `Run Configuration Snapshot`.
- `results/example_prepared_wgd/report/final_report.md` now displays `ks_bins` and `event.WGD_layer_*` mappings in `Run Configuration Snapshot`.
- `python -m pytest tests -q` passed with 244 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 25`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `244 passed`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.

Commit:
- hash: f93abefe449a09adb989b79a37a12f05493851f1
- message: feat: show run configuration in final reports
- files: report assembler, standard smoke, Nextflow report wiring, tests, history

Next:
- Commit the run-configuration report update, then continue preserving Docker/Apptainer as the only release blocker.

## 2026-06-25 - Index run configuration snapshots in delivery bundle

Context:
- Final reports now render run configuration snapshots inline.
- The delivery bundle still pointed to final reports but did not directly index the raw standard and WGD run configuration TSV files for machine-readable review.

Decisions:
- Add `standard/run_config_snapshot` to the delivery manifest.
- Add `wgd/run_config_snapshot` to the delivery manifest.
- Keep these entries in the standard and WGD sections next to the final report rows.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `standard/run_config_snapshot` was absent from the delivery manifest.
- The same focused test passed with 1 test after adding standard and WGD run configuration snapshot rows.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` exited `0`.
- `results/delivery_bundle/delivery_manifest.tsv` now lists `results/quickstart/standard_smoke/tables/run_config_snapshot.tsv` and `results/quickstart/example_prepared_wgd/tables/wgd_run_config_snapshot.tsv`.
- `python -m pytest tests -q` passed with 244 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 25`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `244 passed`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.

Commit:
- hash: 968a126431140602ef6b82938944427bfc1a3942
- message: feat: index run configuration snapshots
- files: delivery bundle helper, delivery bundle test, history

Next:
- Commit the delivery-bundle run configuration index update, then keep Docker/Apptainer as the only unresolved release blocker.

## 2026-06-25 - Document run configuration snapshots in quickstart

Context:
- The current development boundary is to finish the analysis workflow first, then do container packaging and runtime verification at the end.
- Final reports and the delivery bundle now expose standard and WGD run configuration snapshots, but the quickstart did not yet list those files or explain the report section.

Decisions:
- Keep container work as a final packaging/verification step, not the next development focus.
- Add standard and WGD run configuration snapshot paths to the quickstart handoff outputs.
- State that final reports include a `Run Configuration Snapshot` section for selected species, runtime, identification rules, Ks bins, and WGD event mappings.

Added:
- none

Modified:
- `HISTORY.md`
- `docs/quickstart.md`
- `tests/test_quickstart_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_quickstart_docs.py -q` first failed because `docs/quickstart.md` did not list `results/quickstart/standard_smoke/tables/run_config_snapshot.tsv`.
- The same focused test passed with 2 tests after adding the standard/WGD run configuration snapshot paths and report-section note.
- `python -m pytest tests/test_release_audit_docs.py tests/test_run_delivery_bundle.py -q` passed with 2 tests.
- `python -m pytest tests -q` passed with 244 tests.

Commit:
- hash: b5b16d1f5f0f44e7041a7b37c3dc895936201c95
- message: docs: document quickstart run configuration snapshots
- files: quickstart docs, quickstart doc test, history

Next:
- Continue improving analysis-flow usability and evidence surfaces; leave Docker/Apptainer packaging for the final封装 step.

## 2026-06-25 - Add final delivery bundle index

Context:
- The release gate and quickstart handoff produced many useful artifacts, but users still needed to know which final reports, WGD event evidence, runtime status files, and docs to inspect first.
- The long objective asks for a final reusable workflow version, so the top-level handoff should include a stable user-facing delivery index.

Decisions:
- Add `bin/genefam/run_delivery_bundle.py` to assemble a compact delivery manifest from release checks, objective audit, readiness, and quickstart outputs.
- Keep Docker/Apptainer absence as a reported runtime status rather than a script failure, so the bundle remains useful while container runtimes are unavailable.
- Generate both a machine-readable TSV and a Markdown handoff under `results/delivery_bundle/`.
- Have `run_release_checks.py` write the delivery bundle as a post-run artifact after the objective audit, avoiding stale intermediate inputs inside the sequential check list.
- Document the delivery bundle in README, quickstart, and release audit.

Added:
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_release_checks.py`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_run_release_checks.py::test_write_delivery_bundle_uses_latest_release_outputs tests/test_release_audit_docs.py tests/test_quickstart_docs.py -q` first failed because `run_delivery_bundle.py` did not exist, `run_release_checks.py` had no `write_delivery_bundle`, and docs did not mention the delivery bundle outputs.
- The same command passed with 5 tests after adding the delivery-bundle script, release-runner post-run writer, and documentation.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` exited `0` and wrote `results/delivery_bundle/delivery_manifest.tsv` plus `results/delivery_bundle/delivery_bundle.md`.
- `results/delivery_bundle/delivery_manifest.tsv` lists standard final report, prepared WGD final report, `wgd_event_evidence.tsv` for `alpha,beta,gamma,theta`, GeneFamilyFlow Nextflow, `/usr/local/bin/R`, and missing `docker`/`apptainer`.
- `python -m pytest tests -q` passed with 240 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 24`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `240 passed`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.
- `results/delivery_bundle/delivery_manifest.tsv` was refreshed by the release runner after objective-audit generation.

Commit:
- hash: 9f1d4020bb21f8f8d2d8a49b1ab022129e0442c3
- message: feat: add delivery bundle index
- files: delivery bundle helper, release runner, README, quickstart, release audit, tests, history

Next:
- Commit the delivery bundle index work, then continue toward the final objective while preserving Docker/Apptainer as the remaining external blocker.

## 2026-06-25 - Refresh delivery bundle in local acceptance

Context:
- `run_release_checks.py` now writes `results/delivery_bundle/`, but `scripts/run_local_acceptance.sh` reruns the quickstart handoff after the release gate.
- That meant local acceptance could leave `results/quickstart/quickstart_summary.tsv` newer than the delivery bundle even though README promised both are refreshed.

Decisions:
- Add `DELIVERY_OUTDIR`, defaulting to `results/delivery_bundle`.
- Run `bin/genefam/run_delivery_bundle.py` after the quickstart handoff so the final delivery manifest reads the latest quickstart summary.
- Print delivery bundle paths in the primary handoff file list.
- Preserve release-gate exit semantics: release failure remains the first returned status, then quickstart status, then delivery-bundle status.

Added:
- none

Modified:
- `HISTORY.md`
- `scripts/run_local_acceptance.sh`
- `tests/test_local_acceptance_script.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_local_acceptance_script.py -q` first failed because `scripts/run_local_acceptance.sh` did not define `DELIVERY_OUTDIR`, did not call `run_delivery_bundle.py`, and did not print delivery bundle outputs.
- The same command passed with 2 tests after updating the acceptance script.
- `python -m pytest tests -q` passed with 240 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 24`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `240 passed`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `results/delivery_bundle/delivery_manifest.tsv` still lists standard and WGD final reports, alpha/beta/gamma/theta event evidence, GeneFamilyFlow, `/usr/local/bin/R`, and missing `docker`/`apptainer`.

Commit:
- hash: 51bf60a336ca4a5ab9fe72ff2c617ddf874ed560
- message: fix: refresh delivery bundle in local acceptance
- files: local acceptance script, acceptance tests, history

Next:
- Commit the local acceptance refresh, then continue toward the final objective while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Document delivery bundle in readiness checklist

Context:
- README, quickstart, release audit, release gate, and local acceptance now all surface `results/delivery_bundle/`.
- `docs/readiness_checklist.md` still pointed only to the handoff report and summary, so users following the readiness checklist could miss the final report/evidence index.

Decisions:
- Extend the readiness checklist contract test to require both delivery bundle outputs.
- Update the checklist to describe the handoff report as status summary and the delivery bundle as the final index for standard reports, prepared WGD reports, alpha/beta/gamma/theta evidence, runtime availability, and docs.

Added:
- none

Modified:
- `HISTORY.md`
- `docs/readiness_checklist.md`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit -q` first failed because `docs/readiness_checklist.md` did not mention `results/delivery_bundle/delivery_manifest.tsv` or `results/delivery_bundle/delivery_bundle.md`.
- The same command passed with 1 test after updating the readiness checklist.
- `python -m pytest tests -q` passed with 240 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 24`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `240 passed`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `results/delivery_bundle/delivery_manifest.tsv` still lists standard and WGD final reports, alpha/beta/gamma/theta event evidence, GeneFamilyFlow, `/usr/local/bin/R`, and missing `docker`/`apptainer`.

Commit:
- hash: 2bcdec1c740ac3ec318d334ac47f05054b015ac7
- message: docs: list delivery bundle in readiness checklist
- files: readiness checklist, runtime docs test, history

Next:
- Commit the readiness checklist update, then continue toward the final objective while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Link delivery bundle from handoff report

Context:
- `results/handoff/handoff_report.md` is documented as the first human-facing status file, but its key evidence list still omitted the delivery bundle.
- Users opening the handoff report should be able to jump directly to the final delivery manifest and Markdown bundle without consulting README first.

Decisions:
- Add delivery bundle paths to the handoff report key-evidence section.
- Extend the handoff Markdown test so this relationship stays covered.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py::test_write_handoff_markdown_contains_copyable_next_steps -q` first failed because the handoff report did not mention `results/delivery_bundle/delivery_manifest.tsv`.
- The same command passed with 1 test after adding delivery bundle paths to the key evidence list.
- `python -m pytest tests -q` passed with 240 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 24`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `240 passed`.
- `results/handoff/handoff_report.md` now lists `results/delivery_bundle/delivery_manifest.tsv` and `results/delivery_bundle/delivery_bundle.md` under Key Evidence.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.

Commit:
- hash: f1cf6fcf4991b2ce561eb8de08cf7380883aedc8
- message: docs: link delivery bundle from handoff report
- files: handoff report helper, handoff tests, history

Next:
- Commit the handoff evidence update, then continue toward the final objective while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Add Reference governance release audit

Context:
- The long objective says `Reference/` is a read-only source area for papers and script templates.
- The release evidence previously relied on broad pytest/documentation contracts, but did not explicitly detect tracked `Reference/` changes.
- The workspace can contain many untracked reference source files, so the audit must allow untracked source material while still blocking tracked modifications, deletions, or staged changes.

Decisions:
- Add `bin/genefam/audit_reference_governance.py`.
- Treat `git status --porcelain -- Reference` rows with `??` as allowed untracked source material and every other status as release-blocking tracked Reference changes.
- Write `results/reference_governance/reference_governance.tsv` and `results/reference_governance/reference_governance.md`.
- Add `Reference governance audit` to the release gate before runtime readiness.
- Tighten the objective audit so `history and Reference governance` requires both pytest and the Reference governance audit.
- Document the audit in `docs/release_audit.md`.

Added:
- `bin/genefam/audit_reference_governance.py`
- `tests/test_audit_reference_governance.py`

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_reference_governance.py tests/test_run_release_checks.py::test_default_checks_include_reference_governance_before_readiness tests/test_audit_objective_completion.py::test_history_and_reference_governance_requires_reference_audit -q` first failed because the audit script did not exist, the release gate did not include `Reference governance audit`, and objective audit still marked Reference governance achieved from pytest alone.
- `python -m pytest tests/test_audit_reference_governance.py tests/test_run_release_checks.py::test_default_checks_include_reference_governance_before_readiness tests/test_audit_objective_completion.py::test_history_and_reference_governance_requires_reference_audit tests/test_audit_objective_completion.py::test_audit_objective_completion_cli_writes_outputs tests/test_release_audit_docs.py -q` passed with 6 tests after adding the audit, release-gate check, objective-audit requirement, and release-audit documentation.
- `python -m pytest tests -q` passed with 244 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 25`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `244 passed`.
- `results/reference_governance/reference_governance.md` reports `Tracked changes: 0` and `Untracked reference files: 1`.
- `results/objective_audit/objective_audit.md` reports history and Reference governance achieved from `pytest, documentation contracts, and Reference governance audit`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.

Commit:
- hash: f05290e19e4608d2b70daa607a8e88206ae26a5a
- message: feat: add Reference governance audit
- files: Reference governance audit, release gate, objective audit, release audit docs, tests, history

Next:
- Commit the Reference governance audit, then continue toward the final objective while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Add Reference governance to delivery bundle

Context:
- `Reference governance audit` is now a release-gate and objective-audit requirement.
- The final delivery bundle still indexed reports, WGD evidence, runtime status, and docs, but omitted the new Reference governance evidence.

Decisions:
- Add `governance/reference_governance` and `governance/reference_governance_tsv` rows to the delivery manifest.
- Update the delivery bundle Markdown description so Reference governance is named as part of the final handoff index.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `results/delivery_bundle/delivery_manifest.tsv` did not include Reference governance rows.
- The same command passed with 1 test after adding Reference governance Markdown and TSV rows to the delivery bundle.
- `python -m pytest tests -q` passed with 244 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 25`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; the embedded pytest check reports `244 passed`.
- `results/delivery_bundle/delivery_manifest.tsv` now contains `governance	reference_governance	available	results/reference_governance/reference_governance.md` and `governance	reference_governance_tsv	available	results/reference_governance/reference_governance.tsv`.
- `results/delivery_bundle/delivery_bundle.md` describes Reference governance as part of the final handoff index.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.

Commit:
- hash: ea175a8c16dc18957f8bc53d47d9877bf8dffb31
- message: feat: include Reference governance in delivery bundle
- files: delivery bundle helper, delivery bundle test, history

Next:
- Commit the delivery bundle governance update, then continue toward the final objective while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Add species selection release smoke

Context:
- YAML-driven species-bank discovery and target-species selection were exercised inside mock and standard flows, but the entrypoint did not yet have an independent release smoke artifact.
- The long objective explicitly requires a species bank with one folder per species and YAML-configured target species selection, so this input contract should be directly visible in the release gate.

Decisions:
- Add `bin/genefam/run_species_selection_smoke.py` to reuse `discover_species.py` and `build_run_plan.py`.
- Use `configs/example.config.yaml` and `configs/species_groups.yaml` as the stable entrypoint contract.
- Write `results/species_selection_smoke/tables/species_manifest.tsv`, `results/species_selection_smoke/tables/run_plan.tsv`, and `results/species_selection_smoke/species_selection_smoke.md`.
- Add `species selection smoke` to the release gate after config validation and before the mock MVP.
- Tighten the objective audit so YAML-driven species selection requires explicit species-selection smoke evidence.
- Document the smoke in README and the release audit matrix.

Added:
- `bin/genefam/run_species_selection_smoke.py`
- `tests/test_run_species_selection_smoke.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_species_selection_smoke.py tests/test_run_release_checks.py::test_default_checks_include_species_selection_smoke_before_mock_mvp tests/test_audit_objective_completion.py::test_yaml_driven_species_selection_requires_species_selection_smoke tests/test_release_audit_docs.py -q` first failed because `run_species_selection_smoke.py` did not exist, `species selection smoke` was not in release checks, the objective audit still accepted YAML species selection without it, and release audit did not mention `run_species_selection_smoke.py`.
- The same command passed with 4 tests after adding the smoke, release check, objective-audit requirement, and documentation.
- `python bin/genefam/run_species_selection_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --outdir results/species_selection_smoke` exited `0` and printed `species_manifest`, `run_plan`, and `summary` outputs.
- `results/species_selection_smoke/tables/species_manifest.tsv` contains selected species `Arabidopsis_thaliana` and `Brassica_rapa` with their species-bank peptide and GFF3 paths.
- `results/species_selection_smoke/tables/run_plan.tsv` records `runtime	environment	GeneFamilyFlow`, `runtime	r_bin	/usr/local/bin/R`, and the enabled/disabled module switches.
- `results/species_selection_smoke/species_selection_smoke.md` reports `Selected species: 2` and `Arabidopsis_thaliana, Brassica_rapa`.
- `python -m pytest tests -q` passed with 238 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`.
- `results/release_checks/release_checks.md` reports `Passed: 24`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`; `species selection smoke` passed and lists `results/species_selection_smoke/tables/species_manifest.tsv` and `results/species_selection_smoke/tables/run_plan.tsv`.
- `results/objective_audit/objective_audit.md` reports YAML-driven species selection achieved from `config validation checks and species selection smoke`; overall completion remains blocked only by missing `docker` and `apptainer`.

Commit:
- hash: 61218dc5004bcf5940af1dee4a0f110c0df15726
- message: feat: add species selection smoke
- files: species selection smoke helper, release gate, objective audit, README, release audit, tests, history

Next:
- Continue making broad objective items independently auditable while preserving Docker/Apptainer as the only current release blocker.

## 2026-06-25 - Tighten module input validation

Context:
- The workflow is being developed before final container packaging.
- Species-bank discovery already records peptide, GFF3, CDS, and genome paths, but config validation did not yet reject several module/input mismatches before runtime.
- Large multi-species runs should fail early when a selected module requires protein or coordinate inputs that the YAML marks as optional or unavailable.

Decisions:
- Keep this as workflow-entry validation, not container work.
- Require `input.required.pep: true` for identification, domain filtering, phylogeny, and motif modules.
- Require both `input.required.pep: true` and `input.required.gff3: true` for synteny, matching the protein-search plus coordinate-block evidence model used by MCScanX-style workflows.
- Document the expanded module dependency validation in `docs/input_contract.md`.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `tests/test_validate_config.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py -q` first failed with 2 failures because module/input checks for peptide-dependent modules and synteny were not implemented.
- `python -m pytest tests/test_validate_config.py -q` passed with 15 tests after adding the module/input dependency checks.
- `python -m pytest tests/test_discover_species.py tests/test_run_species_selection_smoke.py tests/test_release_audit_docs.py -q` passed with 6 tests.
- `python -m pytest tests -q` passed with 246 tests.

Commit:
- hash: 07a13b74d129aa44745eb1f414cd689fb24c9cb7
- message: feat: tighten module input validation
- files: config validator, input contract docs, validator tests, history

Next:
- Run focused and full tests, then commit the validation hardening while leaving container packaging for the final step.

## 2026-06-25 - Enable manifest input mode

Context:
- The workflow is being developed before final container packaging.
- `input.mode` already allowed `auto` and `manifest`, but validation did not require mode-specific fields and species-selection smoke still always scanned `input.root`.
- Large species banks may need a curated reusable manifest when file names are ambiguous or manually curated.

Decisions:
- Keep `input.mode: auto` as the species-bank scanning path and require `input.root`.
- Make `input.mode: manifest` a first-class path that requires `input.manifest`.
- Reuse the same species include, exclude, group selection, and required-file checks for prebuilt manifests.
- Let `run_species_selection_smoke.py` exercise both auto mode and manifest mode so the entrypoint contract is tested.
- Document manifest columns and mode-specific fields in the input contract and config schema.

Added:
- `load_species_manifest` in `bin/genefam/discover_species.py`.

Modified:
- `HISTORY.md`
- `bin/genefam/discover_species.py`
- `bin/genefam/run_species_selection_smoke.py`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `schemas/config.schema.yaml`
- `tests/test_discover_species.py`
- `tests/test_run_species_selection_smoke.py`
- `tests/test_validate_config.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py -q` first failed because `input.root` and `input.manifest` were not checked for `auto` and `manifest` modes.
- `python -m pytest tests/test_discover_species.py -q` first failed because `load_species_manifest` did not exist.
- After implementation, `python -m pytest tests/test_validate_config.py -q` passed with 17 tests.
- `python -m pytest tests/test_discover_species.py tests/test_run_species_selection_smoke.py -q` passed with 8 tests.
- `python -m pytest tests/test_validate_config.py tests/test_discover_species.py tests/test_run_species_selection_smoke.py -q` passed with 25 tests after the final cleanup.
- `python -m pytest tests -q` passed with 251 tests.

Commit:
- hash: af90baed16b38c4e088aec7abbd66f99c8101c4c
- message: feat: enable manifest input mode
- files: species discovery, species selection smoke, config validation, docs, schema, tests, history

Next:
- Run the full test suite, then commit the manifest-mode input contract.

## 2026-06-25 - Add manifest-mode release evidence

Context:
- The workflow is still being developed before final container packaging.
- `input.mode: manifest` was implemented, but release checks and objective audit still treated auto-mode species-bank scanning as the only species-selection evidence.
- Large multi-species runs need both folder-per-species discovery and curated manifest reuse to be visible in the release evidence chain.

Decisions:
- Add `configs/manifest.example.yaml` as a reusable manifest-mode YAML example.
- Add `tests/fixtures/species_manifest.tsv` as the stable manifest fixture.
- Add `validate manifest config` and `species manifest selection smoke` to release checks before downstream workflow smokes.
- Require manifest-mode evidence in the long-objective audit for YAML-driven species selection.
- Update release audit documentation to list manifest-mode commands and outputs.

Added:
- `configs/manifest.example.yaml`
- `tests/fixtures/species_manifest.tsv`

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_manifest_species_selection_smoke_before_mock_mvp -q` first failed because `species manifest selection smoke` was not in release checks.
- `python -m pytest tests/test_audit_objective_completion.py::test_yaml_driven_species_selection_requires_species_selection_smokes -q` first failed because the objective audit still accepted YAML-driven species selection without manifest-mode evidence.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `configs/manifest.example.yaml` and manifest-mode outputs were absent from the release audit.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml` passed with `Configuration OK`.
- `python bin/genefam/run_species_selection_smoke.py --config configs/manifest.example.yaml --groups configs/species_groups.yaml --outdir results/species_manifest_selection_smoke` passed and wrote `run_plan`, `species_manifest`, and `summary`.
- `python -m pytest tests/test_run_release_checks.py tests/test_audit_objective_completion.py tests/test_release_audit_docs.py tests/test_validate_config.py tests/test_run_species_selection_smoke.py tests/test_discover_species.py -q` passed with 75 tests.
- `python -m pytest tests -q` passed with 252 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`; `results/release_checks/release_checks.md` reports `Passed: 27`, `Failed: 3`, `Required failed: 1`, `Optional failed: 2`, and `Release ready: false`.
- The new `validate manifest config` and `species manifest selection smoke` release checks passed.
- `results/objective_audit/objective_audit.md` reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the only blocker remains missing `docker` and `apptainer`.

Commit:
- hash: 2acc8e51c4c17ab647b7120f5a2374f92d893dfc
- message: feat: add manifest mode release evidence
- files: manifest example, manifest fixture, release checks, objective audit, release docs, tests, history

Next:
- Continue strengthening workflow-level handoff and evidence surfaces; keep Docker/Apptainer packaging for the final封装 step.

## 2026-06-25 - Surface manifest input in delivery bundle

Context:
- The workflow is still being developed before final container packaging.
- Manifest-mode input is now validated and release-tested, but the final delivery bundle did not expose the manifest example or manifest-mode smoke output.
- Users need the final handoff index to point directly to both folder-per-species and prebuilt manifest input routes.

Decisions:
- Add input rows to the delivery manifest for `configs/manifest.example.yaml`, `tests/fixtures/species_manifest.tsv`, and the manifest-mode selected species output.
- Update the delivery bundle Markdown framing to mention species-bank and manifest-mode input.
- Keep generated `results/` evidence out of git while using it for verification.
- Update quickstart and README handoff language so users know the final index includes manifest-mode input entries.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_delivery_bundle.py`
- `docs/quickstart.md`
- `tests/test_quickstart_docs.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because delivery manifest rows for manifest-mode input were missing.
- `python -m pytest tests/test_quickstart_docs.py -q` first failed because quickstart did not mention `configs/manifest.example.yaml`, `tests/fixtures/species_manifest.tsv`, or the manifest-mode smoke output.
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_quickstart_docs.py -q` passed with 3 tests.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` passed and refreshed the delivery bundle.
- `rg -n "manifest_config|manifest_fixture|manifest_selection_smoke|manifest-mode" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md` confirmed manifest-mode rows in generated handoff outputs.
- `python -m pytest tests -q` passed with 252 tests.

Commit:
- hash: 8c5272c644bb9be369f84caf20840ac28d499ba7
- message: feat: surface manifest input in delivery bundle
- files: delivery bundle helper, quickstart, README, tests, history

Next:
- Continue improving user-facing workflow handoff and evidence surfaces; keep Docker/Apptainer packaging for the final封装 step.

## 2026-06-25 - Support manifest mode in standard smoke paths

Context:
- The workflow is still being developed before final container packaging.
- `input.mode: manifest` was validated and visible in delivery outputs, but several Python smoke entrypoints still hard-read `input.root`.
- The standard branch, chromosome-location smoke, gene-structure smoke, and mock MVP should behave consistently with Nextflow `PREPARE_SPECIES` for both auto and manifest input modes.

Decisions:
- Add `species_rows_from_config` as the shared resolver for YAML-driven species rows across auto and manifest modes.
- Route standard smoke, chromosome smoke, gene-structure smoke, and mock MVP through the shared resolver.
- Record `input.mode` and `input.manifest` in the standard run configuration snapshot so final reports explain whether species came from a folder bank or a prebuilt manifest.
- Keep generated `results/standard_manifest_smoke` out of git and use it only as verification evidence.

Added:
- `species_rows_from_config` in `bin/genefam/discover_species.py`.

Modified:
- `HISTORY.md`
- `bin/genefam/build_run_config_snapshot.py`
- `bin/genefam/discover_species.py`
- `bin/genefam/run_chromosome_smoke.py`
- `bin/genefam/run_gene_structure_smoke.py`
- `bin/genefam/run_mock_mvp.py`
- `bin/genefam/run_standard_smoke.py`
- `tests/test_build_run_config_snapshot.py`
- `tests/test_discover_species.py`
- `tests/test_run_chromosome_smoke.py`
- `tests/test_run_gene_structure_smoke.py`
- `tests/test_run_mock_mvp.py`
- `tests/test_run_standard_smoke.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_standard_smoke.py::test_run_standard_smoke_supports_manifest_input_mode -q` first failed with `KeyError: root`, proving standard smoke did not support manifest-mode configs.
- `python -m pytest tests/test_build_run_config_snapshot.py -q` first failed because `input.mode` and `input.manifest` were missing from the run snapshot.
- `python -m pytest tests/test_run_chromosome_smoke.py::test_run_chromosome_smoke_supports_manifest_input_mode -q` first failed with `KeyError: root`.
- `python -m pytest tests/test_run_gene_structure_smoke.py::test_run_gene_structure_smoke_supports_manifest_input_mode -q` first failed with `KeyError: root`.
- `python -m pytest tests/test_run_mock_mvp.py::test_run_mock_mvp_cli_supports_manifest_input_mode -q` first failed with `KeyError: root`.
- `python -m pytest tests/test_discover_species.py tests/test_build_run_config_snapshot.py -q` passed with 10 tests.
- `python -m pytest tests/test_run_standard_smoke.py tests/test_run_chromosome_smoke.py tests/test_run_gene_structure_smoke.py -q` passed with 7 tests.
- `python -m pytest tests/test_run_mock_mvp.py -q` passed with 4 tests.
- `python -m pytest tests/test_run_standard_smoke.py tests/test_run_chromosome_smoke.py tests/test_run_gene_structure_smoke.py tests/test_discover_species.py tests/test_build_run_config_snapshot.py -q` passed with 17 tests.
- `python -m pytest tests -q` passed with 258 tests.
- `python bin/genefam/run_standard_smoke.py --config configs/manifest.example.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/standard_manifest_smoke` passed and wrote the standard branch outputs.
- `rg -n "input.mode|input.manifest|selected_species|Run Configuration Snapshot" results/standard_manifest_smoke/tables/run_config_snapshot.tsv results/standard_manifest_smoke/report/final_report.md` confirmed the manifest-mode run configuration appears in both the TSV and final report.

Commit:
- hash: 02bf8c61edaad85d1aa59f6e93ac7246caa88900
- message: feat: support manifest mode in smoke paths
- files: species resolver, standard/mock/annotation smoke paths, run snapshot, tests, history

Next:
- Continue closing workflow-entry consistency gaps while leaving Docker/Apptainer packaging for the final封装 step.

## 2026-06-25 - Add Nextflow manifest-mode standard smoke evidence

Context:
- The workflow is still being developed before final container packaging.
- Python standard and annotation smoke paths now support `input.mode: manifest`, but the Nextflow standard release evidence still only covered `configs/example.config.yaml`.
- The DSL2 workflow should prove both folder-per-species and manifest-mode standard entrypoints before final封装.

Decisions:
- Add `Nextflow standard manifest smoke` to the release gate after the standard branch smoke and before WGD smoke.
- Run the new check with `configs/manifest.example.yaml` and publish results under `results/nextflow_standard_manifest_smoke`.
- Require this manifest-mode Nextflow smoke in the long-objective audit for the `Nextflow DSL2 workflow` requirement.
- Document the new command and output path in the release audit.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_nextflow_standard_manifest_smoke_before_wgd -q` first failed because `Nextflow standard manifest smoke` was not in release checks.
- `python -m pytest tests/test_audit_objective_completion.py::test_nextflow_dsl2_requires_manifest_standard_smoke_evidence -q` first failed because the objective audit still accepted Nextflow DSL2 completion without manifest-mode standard evidence.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `results/nextflow_standard_manifest_smoke` was absent from the release audit.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_nextflow_standard_manifest_smoke_before_wgd tests/test_audit_objective_completion.py::test_nextflow_dsl2_requires_manifest_standard_smoke_evidence tests/test_release_audit_docs.py tests/test_run_nextflow_standard_smoke.py::test_build_nextflow_command_supports_manifest_config -q` passed with 4 tests.
- `python bin/genefam/run_nextflow_standard_smoke.py --nextflow-bin /definitely/missing/nextflow --config configs/manifest.example.yaml --outdir results/nextflow_standard_manifest_smoke` exited `1` as expected for missing Nextflow; the generated TSV records `configs/manifest.example.yaml` and `results/nextflow_standard_manifest_smoke/standard` in the command.
- `python -m pytest tests/test_run_release_checks.py tests/test_audit_objective_completion.py tests/test_release_audit_docs.py tests/test_run_nextflow_standard_smoke.py -q` passed with 61 tests.
- `python -m pytest tests -q` passed with 261 tests.

Commit:
- hash: 5470efd3d40af89d1b8fb5fbf43685f5b80fee26
- message: feat: add nextflow manifest standard smoke
- files: release checks, objective audit, release docs, Nextflow standard smoke tests, history

Next:
- Continue strengthening DSL2 and report evidence while leaving Docker/Apptainer packaging for the final封装 step.

## 2026-06-25 - Surface Nextflow manifest smoke in delivery bundle

Context:
- The project direction is to finish the analysis workflow before final container packaging.
- `Nextflow standard manifest smoke` was already part of the release gate and objective audit, but the final delivery bundle did not expose that evidence row.
- Users should be able to inspect one final handoff index and see whether the manifest-mode DSL2 standard path is available or still blocked by the local runtime.

Decisions:
- Add a release-check-based delivery bundle row for `nextflow_standard_manifest_smoke`.
- Mark the row `available` only when the release check status is `passed`; otherwise keep it `missing` so local environment gaps are visible.
- Document the expected output path in the quickstart key outputs.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `docs/quickstart.md`
- `tests/test_quickstart_docs.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because the delivery manifest lacked the `nextflow_standard_manifest_smoke` row.
- `python -m pytest tests/test_quickstart_docs.py -q` first failed because `docs/quickstart.md` did not mention `results/nextflow_standard_manifest_smoke/nextflow_standard_smoke.tsv`.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed with 1 test.
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_quickstart_docs.py -q` passed with 3 tests.
- `python -m pytest tests -q` passed with 261 tests.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` refreshed the delivery bundle.
- `rg -n "nextflow_standard_manifest_smoke|manifest-mode standard DSL2 smoke" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md` confirmed the new row is present; current local evidence reports it as `missing` until the runtime can pass that release check.

Commit:
- hash: 66bce42eb90b6552a77b43c1ee91fce7bdf03425
- message: feat: surface nextflow manifest smoke in delivery bundle
- files: delivery bundle, quickstart docs, tests, history

Next:
- Continue workflow-first development, especially strengthening DSL2/report evidence; defer Docker/Apptainer封装 until the analysis flow is complete.

## 2026-06-25 - Add standard-to-WGD handoff manifest

Context:
- The workflow-first development phase should make the standard identification branch hand off cleanly into the duplication/WGD event branch before final container封装.
- The standard branch already produced `family_candidates.tsv`, but users still had to read documentation to know which prepared MCScanX/KaKs inputs were required next.
- A machine-readable manifest makes the family identification to gamma/beta/alpha/theta evidence path easier to audit and automate.

Decisions:
- Add `bin/genefam/build_wgd_handoff_manifest.py` to write a standard-to-WGD checklist.
- Mark standard family candidates as `available`, configured WGD event metadata as `configured`, and duplicate-type plus Ka/Ks pair tables as `pending_user_preparation`.
- Publish `tables/wgd_handoff_manifest.tsv` from Python standard smoke and the Nextflow DSL2 standard branch.
- Include the manifest in the standard report index, final report, Nextflow standard smoke output checks, delivery bundle, quickstart, release audit, README, and handoff documentation.

Added:
- `bin/genefam/build_wgd_handoff_manifest.py`
- `tests/test_build_wgd_handoff_manifest.py`

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_delivery_bundle.py`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `bin/genefam/run_standard_smoke.py`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `docs/standard_to_wgd_handoff.md`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_standard_smoke.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_handoff_manifest.py -q` first failed with `ModuleNotFoundError`, proving the manifest builder was absent.
- `python -m pytest tests/test_run_standard_smoke.py::test_run_standard_smoke_writes_standard_branch_outputs -q` first failed because `tables/wgd_handoff_manifest.tsv` was not written by the standard branch.
- `python -m pytest tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` first failed because the DSL2 standard branch did not include `BUILD_WGD_HANDOFF_MANIFEST`.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py::test_standard_to_wgd_handoff_doc_links_identification_and_wgd_branches -q` first failed because the docs did not mention `wgd_handoff_manifest.tsv`.
- `python -m pytest tests/test_run_nextflow_standard_smoke.py::test_expected_published_outputs_cover_standard_user_results -q` first failed because the Nextflow standard smoke output check did not require the handoff manifest.
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because the delivery manifest lacked the standard-to-WGD handoff row.
- `python -m pytest tests/test_build_wgd_handoff_manifest.py tests/test_run_standard_smoke.py tests/test_standard_branch_report_index.py tests/test_workflow_modules.py tests/test_run_nextflow_standard_smoke.py tests/test_run_delivery_bundle.py tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py::test_standard_to_wgd_handoff_doc_links_identification_and_wgd_branches -q` passed with 39 tests.
- `python -m pytest tests -q` passed with 263 tests.
- `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/standard_smoke` refreshed the standard branch outputs and printed `wgd_handoff_manifest`.
- `rg -n "family_members|duplicate_types|kaks_pairs|events_config|wgd_handoff_manifest" results/standard_smoke/tables/wgd_handoff_manifest.tsv results/standard_smoke/report/report_index.tsv results/standard_smoke/report/final_report.md` confirmed the handoff manifest is in the table, report index, and final report.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` refreshed the delivery bundle.
- `rg -n "wgd_handoff_manifest|standard-to-WGD handoff" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md results/standard_smoke/report/final_report.md` confirmed the final delivery index points to the handoff manifest.

Commit:
- hash: 0a29cc1c37f44ec7a69e427339d2b02209459cc1
- message: feat: add standard to wgd handoff manifest
- files: standard-to-WGD manifest builder, standard and Nextflow branch wiring, delivery bundle, docs, tests, history

Next:
- Continue closing workflow-first gaps before final Docker/Apptainer packaging.

## 2026-06-25 - Fix manifest-mode paths for Nextflow workdirs

Context:
- After adding the standard-to-WGD handoff manifest, the refreshed release gate showed `Nextflow standard manifest smoke` failing while the folder-per-species Nextflow standard branch passed.
- The objective audit still marked `Nextflow DSL2 workflow` as missing until the manifest-mode DSL2 standard path passed.
- The project is still in workflow-first development; Docker/Apptainer封装 remains the final step.

Root cause:
- `tests/fixtures/species_manifest.tsv` stores file paths relative to the repository root.
- Python smoke tests run from the repository root, so those relative paths worked there.
- Nextflow processes execute inside per-task `work/` directories; the same manifest-relative values were no longer reachable, causing missing peptide/GFF3 files in downstream standard processes.

Decisions:
- Resolve non-empty manifest file columns (`pep`, `gff3`, `cds`, `genome`) against `--base-dir` when loading a prebuilt species manifest.
- Keep the existing behavior unchanged when no `base_dir` is supplied.
- Add both function-level and CLI-level tests so the Nextflow `PREPARE_SPECIES --base-dir ${projectDir}/..` contract is protected.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/discover_species.py`
- `tests/test_discover_species.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_discover_species.py::test_load_species_manifest_resolves_relative_file_paths_against_base_dir -q` first failed because manifest file paths stayed relative.
- `python -m pytest tests/test_discover_species.py -q` passed with 8 tests after the fix.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --config configs/manifest.example.yaml --outdir results/nextflow_standard_manifest_smoke` passed and produced the full standard output set, including `tables/wgd_handoff_manifest.tsv`.
- `cat results/nextflow_standard_manifest_smoke/nextflow_standard_smoke.tsv` showed `nextflow_standard_identification` status `passed`.
- `python -m pytest tests/test_discover_species.py tests/test_run_nextflow_standard_smoke.py -q` passed with 18 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` now reports `Passed: 28`, `Required failed: 1`, with the only required failure being `readiness audit`; Docker and Apptainer profile smokes remain optional failures.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` now reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, with only Docker/Apptainer reproducibility blocked by missing runtimes.

Commit:
- hash: 1c5a4760def3e2a006bc99ded6c6f3777698f94b
- message: fix: resolve manifest paths for nextflow workdirs
- files: species manifest resolver, discovery tests, history

Next:
- Continue workflow-first polishing and keep Docker/Apptainer packaging as the remaining external-runtime blocker.

## 2026-06-25 - Audit Docker build context hygiene

Context:
- The workflow itself now has `Achieved: 11`, `Missing: 0`; the remaining objective blocker is Docker/Apptainer runtime availability.
- Before running final container封装, the static container materials should also guard against accidentally copying large runtime caches or local paper source material into Docker build context.
- `.dockerignore` already excludes `.git`, `.nextflow*`, `work/`, `results/`, Python caches, and `Reference/`, but the release audit did not enforce that contract.

Decisions:
- Extend `bin/genefam/audit_container_materials.py` to read `.dockerignore`.
- Add `dockerignore_build_context` to the container materials audit.
- Require `.dockerignore` to exclude VCS metadata, Nextflow/cache outputs, generated results, Python caches, and Reference source material.
- Keep this as static packaging evidence because Docker/Apptainer runtimes are not yet available on this machine.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/audit_container_materials.py`
- `tests/test_audit_container_materials.py`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_container_materials.py -q` first failed because `audit_container_materials()` did not accept or check `.dockerignore`.
- `python -m pytest tests/test_audit_container_materials.py -q` passed with 3 tests after adding `dockerignore_build_context`.
- `python bin/genefam/audit_container_materials.py --outdir results/container_materials` passed and wrote `dockerignore_build_context` to the TSV and Markdown outputs.
- `rg -n "dockerignore_build_context|\\.dockerignore" results/container_materials/container_materials.tsv results/container_materials/container_materials.md` confirmed the new static packaging check is present.
- `python -m pytest tests/test_audit_container_materials.py tests/test_release_audit_docs.py tests/test_run_release_checks.py tests/test_runtime_environment_files.py -q` passed with 51 tests.
- `python -m pytest tests -q` passed with 265 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still reports `Passed: 28`, `Required failed: 1`; the only required failure remains the runtime readiness audit, while Docker and Apptainer profile smokes remain optional failures.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 6edc7b1933424e93681a4a28ae457f0faffe722b
- message: test: audit docker build context hygiene
- files: container materials audit, audit tests, release audit docs test, history

Next:
- Continue final封装 readiness work; actual Docker/Apptainer execution remains blocked until those runtimes are installed.

## 2026-06-25 - Decouple example HMM paths from Reference source material

Context:
- The current priority remains workflow-first development; container封装 is deferred until the analysis pipeline itself is stable.
- Static container preparation exposed a packaging mismatch: `.dockerignore` correctly excludes `Reference/`, but the example YAML files still pointed `gene_family.hmm_profiles` at `Reference/Long_Weixiong_20240323_1_GDSL/PF00657.hmm`.
- That would make a copied example config brittle in Docker/Apptainer builds, even though `Reference/` should stay read-only source material rather than runtime input.

Decisions:
- Keep `Reference/` excluded from Docker build context.
- Add a container-materials audit check named `example_config_hmm_profiles_container_safe`.
- Move the bundled example HMM profile path to a repository fixture under `tests/fixtures/hmmer_profiles/`.
- Document that the fixture HMM path is only a lightweight example path and must be replaced by curated HMM profiles for biological runs.

Added:
- `tests/fixtures/hmmer_profiles/PF00657.demo.hmm`

Modified:
- `HISTORY.md`
- `bin/genefam/audit_container_materials.py`
- `configs/example.config.yaml`
- `configs/manifest.example.yaml`
- `configs/advanced_modules.example.yaml`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `tests/test_audit_container_materials.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_container_materials.py -q` first failed because `audit_container_materials()` did not accept `example_configs`.
- `python -m pytest tests/test_audit_container_materials.py -q` passed with 4 tests after adding the audit logic and updating example configs.
- `python bin/genefam/audit_container_materials.py --outdir results/container_materials` passed with the new example HMM profile safety check.
- `rg -n "Reference/.+\\.hmm|example_config_hmm_profiles_container_safe|PF00657.demo.hmm" configs docs README.md bin tests -g '!Reference/**'` confirmed runtime example configs now use `tests/fixtures/hmmer_profiles/PF00657.demo.hmm`; remaining `Reference/...hmm` matches are intentional test fixtures or historical plan text.
- `python -m pytest tests/test_audit_container_materials.py tests/test_release_audit_docs.py tests/test_quickstart_docs.py tests/test_run_release_checks.py -q` passed with 42 tests.
- `python -m pytest tests -q` passed with 266 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`; the only required failure remains the runtime readiness audit while Docker and Apptainer profile smokes remain optional failures.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 7f5e925ad09dce8d7f7e7740df90112fe34855ec
- message: fix: keep example hmm paths container safe
- files: container materials audit, example configs, HMM fixture, quickstart/release docs, history

Next:
- Run the focused release/docs tests and full pytest suite before committing.

## 2026-06-25 - Guard non-mock identification configs from test fixtures

Context:
- The workflow-first priority exposed a follow-up issue after moving example HMM paths out of `Reference/`.
- Mock demo configs can safely use lightweight fixture paths, but the non-mock advanced template should not point HMMER or DIAMOND inputs at `tests/fixtures/`.
- Without a config-level guard, a real biological run could accidentally use test fixtures instead of curated HMM profiles and reference peptides.

Decisions:
- Keep `configs/example.config.yaml` and `configs/manifest.example.yaml` as mock-friendly smoke examples.
- Change `configs/advanced_modules.example.yaml` to use `data/hmm_profiles/PF00657.hmm` for the HMM profile placeholder.
- Add validation errors when `dev.mock_external_tools: false` and enabled HMMER/DIAMOND inputs point into `tests/fixtures/`.
- Document the distinction between mock fixture inputs and real project data inputs.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/validate_config.py`
- `configs/advanced_modules.example.yaml`
- `docs/input_contract.md`
- `docs/quickstart.md`
- `tests/test_validate_config.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_fixture_inputs_in_non_mock_identification -q` first failed because no validation error was emitted for fixture-backed non-mock HMMER/DIAMOND inputs.
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_fixture_inputs_in_non_mock_identification -q` passed after adding the validation rule.
- `python bin/genefam/validate_config.py configs/example.config.yaml` passed.
- `python bin/genefam/validate_config.py configs/manifest.example.yaml` passed.
- `python bin/genefam/validate_config.py configs/advanced_modules.example.yaml` passed after moving the advanced HMM placeholder to `data/hmm_profiles/PF00657.hmm`.
- `python -m pytest tests/test_validate_config.py tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_run_release_checks.py -q` passed with 56 tests.
- `python -m pytest tests -q` passed with 267 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`; the only required failure remains the runtime readiness audit while Docker and Apptainer profile smokes remain optional failures.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 715a6501dff0d3bd36eee3cf9f4b108c705f7a2d
- message: fix: reject fixture inputs for non-mock runs
- files: config validation, advanced config, input docs, quickstart, validation tests, history

Next:
- Run focused config/docs tests, full pytest, and release gate before committing.

## 2026-06-25 - Add strict config path preflight

Context:
- The workflow is increasingly usable for real species-bank runs, but `validate_config.py` still only checked structure and module dependencies.
- For real non-mock analyses, missing species-bank roots, manifests, HMM profiles, DIAMOND reference peptides, or expression matrices should be detected before Nextflow starts.
- The advanced config remains a reusable template, so strict path checks should be opt-in rather than forced for every template validation.

Decisions:
- Add an optional `--check-paths` mode to `bin/genefam/validate_config.py`.
- In strict mode, validate `input.root` or `input.manifest`, enabled HMMER profile paths, enabled DIAMOND reference peptides, and `expression.matrix` when present.
- Keep `configs/advanced_modules.example.yaml` under structure/dependency validation only because it intentionally points to user-supplied `data/` paths.
- Use strict path validation in the release gate for the runnable fixture-backed example and manifest configs.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/validate_config.py`
- `bin/genefam/run_release_checks.py`
- `docs/input_contract.md`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `tests/test_validate_config.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_runtime_inputs tests/test_validate_config.py::test_validate_config_cli_check_paths_accepts_fixture_configs -q` first failed because `validate_config()` had no `check_paths` argument and the CLI did not accept `--check-paths`.
- `python -m pytest tests/test_validate_config.py::test_validate_config_check_paths_reports_missing_runtime_inputs tests/test_validate_config.py::test_validate_config_cli_check_paths_accepts_fixture_configs -q` passed after adding strict path mode.
- `python -m pytest tests/test_validate_config.py tests/test_run_release_checks.py -q` passed with 55 tests.
- `python -m pytest tests/test_validate_config.py tests/test_run_release_checks.py tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` passed with 58 tests.
- `python -m pytest tests -q` passed with 269 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`; the runnable example and manifest config validations now use `--check-paths`, and the only required failure remains the runtime readiness audit.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: e362bd49888847d0b60c9daa2ce2a7b2c34ded9c
- message: feat: add strict config path preflight
- files: config validator, release checks, input docs, quickstart/release docs, validation tests, history

Next:
- Run focused docs tests, full pytest, and release gate before committing.

## 2026-06-25 - Wire strict config preflight into Nextflow

Context:
- `validate_config.py --check-paths` can now catch missing runtime inputs before a real run, but users launching `workflows/main.nf` directly would still enter downstream processes first.
- Nextflow processes execute in task work directories, so strict path validation also needs a repository `--base-dir` to resolve YAML paths correctly.
- The final reusable workflow should fail early with configuration errors before species discovery, mock MVP, or identification branches start.

Decisions:
- Add `--base-dir` to the config validator CLI for workdir-safe relative path resolution.
- Add a `VALIDATE_CONFIG` Nextflow module that runs `validate_config.py --check-paths --base-dir ${projectDir}/..`.
- Wire `VALIDATE_CONFIG` into `workflows/main.nf` immediately after loading `params.config`.
- Pass the validated config artifact into mock MVP, species preparation, identification input generation, and run-config snapshots.

Added:
- `workflows/modules/config_validation.nf`

Modified:
- `HISTORY.md`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `docs/release_audit.md`
- `tests/test_validate_config.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_cli_check_paths_resolves_against_base_dir -q` first failed because the CLI did not accept `--base-dir`.
- `python -m pytest tests/test_validate_config.py::test_validate_config_cli_check_paths_resolves_against_base_dir -q` passed after adding `--base-dir`.
- `python -m pytest tests/test_workflow_modules.py::test_config_validation_module_runs_strict_path_preflight tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` first failed because `workflows/modules/config_validation.nf` and the main workflow wiring did not exist.
- `python -m pytest tests/test_workflow_modules.py::test_config_validation_module_runs_strict_path_preflight tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch -q` passed after adding the module and wiring.
- `python -m pytest tests/test_validate_config.py -q` passed with 21 tests.
- `python bin/genefam/run_nextflow_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_smoke` passed.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --config configs/manifest.example.yaml --outdir results/nextflow_standard_manifest_smoke` passed.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` initially regressed to `Passed: 27`, `Required failed: 2`, because `run_nextflow_single_tool_smoke.py` generated non-mock configs that still pointed HMMER/DIAMOND inputs at `tests/fixtures/`.
- Root cause: the new Nextflow `VALIDATE_CONFIG` preflight correctly rejected fixture-backed non-mock single-tool smoke configs before HMMER-only and DIAMOND-only routing began.
- `python -m pytest tests/test_run_nextflow_single_tool_smoke.py::test_build_single_tool_configs_writes_non_mock_hmmer_and_diamond_configs -q` first failed because the generated non-mock smoke configs still contained `tests/fixtures/hmmer_profiles` and `tests/fixtures/reference`.
- `python -m pytest tests/test_run_nextflow_single_tool_smoke.py -q` passed with 3 tests after copying fixture inputs into smoke-local `data/hmm_profiles/` and `data/reference/` paths.
- `python bin/genefam/run_nextflow_single_tool_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_single_tool_smoke` passed after the smoke config fix.
- `python -m pytest tests -q` passed with 271 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` now reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`; the only required failure is again the runtime readiness audit.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` is restored to `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 3cb6fa89ffef1753a65f3ad22f081c98e56315c7
- message: feat: validate configs before nextflow runs
- files: Nextflow config preflight module, workflow wiring, config validator CLI, docs, tests, history

Next:
- Run focused docs/workflow tests, full pytest, and release gate before committing.

## 2026-06-25 - Add Nextflow preflight evidence to delivery bundle

Context:
- The Nextflow entrypoint now runs strict config path preflight before mock MVP, species discovery, and standard identification.
- The final delivery bundle did not yet expose this as a user-facing artifact, so a user reading only `results/delivery_bundle/delivery_manifest.tsv` could miss the new safety guard.

Decisions:
- Add a `nextflow/config_preflight` row to the delivery manifest.
- Point the row at `workflows/modules/config_validation.nf`.
- Describe it as strict config path preflight before Nextflow branches.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index -q` first failed because the delivery manifest did not contain the Nextflow config preflight row.
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index -q` passed after adding the row.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` passed and refreshed `results/delivery_bundle/delivery_manifest.tsv`.
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_release_audit_docs.py tests/test_quickstart_docs.py -q` passed with 4 tests.
- `python -m pytest tests -q` passed with 271 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`; the only required failure remains the runtime readiness audit.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.
- `rg -n "config_preflight|strict config path preflight" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md` confirmed the delivery bundle now exposes the Nextflow preflight evidence.

Commit:
- hash: 70c7bbf7de693891d0d15b38107e2f524ee9c535
- message: docs: expose nextflow preflight in delivery bundle
- files: delivery bundle builder, delivery bundle test, history

Next:
- Run focused delivery/docs tests, full pytest, and release gate before committing.

## 2026-06-25 - Add local acceptance summary output

Context:
- The local acceptance wrapper already refreshes release, quickstart, and delivery-bundle evidence, but the user still has to inspect several files to see which step failed.
- The current development machine is expected to remain blocked by missing Docker/Apptainer, so the final morning handoff should preserve partial success evidence in one compact file.

Decisions:
- Add a small Python summary writer for local acceptance results.
- Keep `scripts/run_local_acceptance.sh` as the single entrypoint, and have it write a TSV plus Markdown summary after release, quickstart, and delivery bundle steps.
- Document `results/local_acceptance/local_acceptance_summary.md` as the compact pass/fail index.

Added:
- `bin/genefam/write_local_acceptance_summary.py`
- `tests/test_write_local_acceptance_summary.py`

Modified:
- `HISTORY.md`
- `README.md`
- `docs/quickstart.md`
- `scripts/run_local_acceptance.sh`
- `tests/test_local_acceptance_script.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_local_acceptance_script.py tests/test_write_local_acceptance_summary.py -q` first failed because `bin.genefam.write_local_acceptance_summary` did not exist.
- `python -m pytest tests/test_local_acceptance_script.py tests/test_write_local_acceptance_summary.py -q` passed with 4 tests after adding the summary writer and wiring it into the local acceptance script.
- `python -m pytest tests -q` passed with 273 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected on this machine, after release gate failed on the known runtime blocker.
- The same local acceptance run still completed quickstart, refreshed `results/delivery_bundle/`, and wrote `results/local_acceptance/local_acceptance_summary.tsv` plus `results/local_acceptance/local_acceptance_summary.md`.
- `results/local_acceptance/local_acceptance_summary.md` records `release_gate` as `failed` with exit code `1`, and records `quickstart_handoff` and `delivery_bundle` as `passed`.
- `results/release_checks/release_checks.md` reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`; the only required failure remains the readiness audit.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 78b7261696d18d39ea1906cf3718c1673e6524dc
- message: feat: add local acceptance summary
- files: local acceptance summary writer, local acceptance wrapper, quickstart docs, README, tests, history

Next:
- Commit the acceptance-summary enhancement, then continue polishing final handoff surfaces while Docker/Apptainer remains the only external runtime blocker.

## 2026-06-25 - Index local acceptance summary in delivery bundle

Context:
- The local acceptance wrapper now writes `results/local_acceptance/local_acceptance_summary.md`, but the delivery bundle still only pointed to the wrapper script.
- Because the summary is generated after the first delivery-bundle refresh inside `scripts/run_local_acceptance.sh`, the final bundle needs one more refresh after the summary exists.

Decisions:
- Add `status/local_acceptance_summary` to the delivery manifest so the compact pass/fail index is part of the final handoff.
- Refresh the delivery bundle a second time at the end of `scripts/run_local_acceptance.sh`, after writing the local acceptance summary.
- Preserve the existing release-gate exit semantics so the script still exits with the known runtime blocker while leaving all handoff artifacts refreshed.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `scripts/run_local_acceptance.sh`
- `tests/test_local_acceptance_script.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_local_acceptance_script.py -q` first failed because the delivery bundle did not include `status/local_acceptance_summary` and the local acceptance script refreshed the delivery bundle only once.
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_local_acceptance_script.py -q` passed with 3 tests after adding the manifest row and final refresh.
- `python -m pytest tests -q` passed with 273 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after completing quickstart and both delivery-bundle refreshes.
- `rg -n "local_acceptance_summary|Passed:|Required failed:|Optional failed:" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md results/release_checks/release_checks.md` confirmed the final delivery bundle indexes `results/local_acceptance/local_acceptance_summary.md` and release checks still report `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/local_acceptance/local_acceptance_summary.md` reports `release_gate` failed with exit code `1`, while `quickstart_handoff` and `delivery_bundle` passed.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 3cfeb5785230cc56dc5f464c657d8ca6fa8d0be5
- message: docs: index local acceptance summary in delivery bundle
- files: delivery bundle index, local acceptance wrapper, delivery/local-acceptance tests, history

Next:
- Commit the delivery-bundle indexing change, then continue improving the final handoff surfaces while the external container runtime blocker remains.

## 2026-06-25 - Surface local acceptance summary in handoff entrypoints

Context:
- The delivery bundle now indexes `results/local_acceptance/local_acceptance_summary.md`.
- The first human-facing handoff report and readiness checklist still did not list that compact pass/fail summary among the first files to inspect.

Decisions:
- Add the local acceptance summary to the handoff report `Key Evidence` list.
- Add the same artifact to the README and readiness checklist first-inspection lists.
- Describe it as the compact local acceptance pass/fail index for release, quickstart, and delivery-bundle refresh steps.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/build_handoff_report.py`
- `docs/readiness_checklist.md`
- `tests/test_build_handoff_report.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report tests/test_runtime_environment_files.py::test_readiness_checklist_points_to_local_acceptance_summary -q` first failed because `handoff_report.md` and `docs/readiness_checklist.md` did not include `results/local_acceptance/local_acceptance_summary.md`.
- The same command passed with 7 tests after adding the local acceptance summary to handoff/report documentation entrypoints.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing handoff, local acceptance, quickstart, and delivery-bundle artifacts.
- `rg -n "local_acceptance_summary|Passed:|Required failed:|Optional failed:" results/handoff/handoff_report.md results/delivery_bundle/delivery_bundle.md results/release_checks/release_checks.md` confirmed the generated handoff report and delivery bundle both point to `results/local_acceptance/local_acceptance_summary.md`; release checks still report `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/local_acceptance/local_acceptance_summary.md` reports `release_gate` failed with exit code `1`, while `quickstart_handoff` and `delivery_bundle` passed.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 1e522aedfe052d4afaf4e998c94c88e060a630be
- message: docs: surface local acceptance summary in handoff
- files: handoff report, readiness checklist, README, handoff/docs tests, history

Next:
- Commit the handoff-entrypoint update, then continue polishing final workflow delivery while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Add Docker default standard smoke contract

Context:
- The container materials audit checked that Dockerfile creates `GeneFamilyFlow`, links `/usr/local/bin/R`, and wires container profiles, but the image default command only validated YAML.
- For a final reusable workflow image, `docker run genefam-pipeline:latest` should execute a lightweight in-image workflow smoke without needing Docker-in-Docker or Apptainer.

Decisions:
- Change the Dockerfile default `CMD` to run `bin/genefam/run_standard_smoke.py` on bundled fixture data.
- Write the default smoke output under `results/container_default_smoke`.
- Extend `audit_container_materials.py` so the static container-materials audit enforces this default standard smoke contract.
- Document the default smoke output in runtime and release-audit docs.

Added:
- none

Modified:
- `Dockerfile`
- `HISTORY.md`
- `bin/genefam/audit_container_materials.py`
- `docs/release_audit.md`
- `docs/runtime_environment.md`
- `tests/test_audit_container_materials.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_container_materials.py -q` first failed because the audit did not expose or enforce `dockerfile_default_standard_smoke`.
- `python -m pytest tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands -q` first failed because runtime and release-audit docs did not mention `results/container_default_smoke`.
- `python -m pytest tests/test_audit_container_materials.py tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands -q` passed with 6 tests after updating Dockerfile, static audit, and docs.
- `python -m pytest tests -q` passed with 274 tests.
- `python bin/genefam/audit_container_materials.py --outdir results/container_materials` passed.
- `results/container_materials/container_materials.md` now reports `Passed: 8`, `Failed: 0`, including `dockerfile_default_standard_smoke`.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release, quickstart, local acceptance, and delivery-bundle artifacts.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.
- `rg -n "container_default_smoke|dockerfile_default_standard_smoke|local_acceptance_summary" docs/runtime_environment.md docs/release_audit.md results/delivery_bundle/delivery_bundle.md results/handoff/handoff_report.md` confirmed the runtime/release docs mention the default container smoke and the generated handoff surfaces still expose the local acceptance summary.

Commit:
- hash: 4ffd713aea7d0c16df436154315c5d7fa4a98a64
- message: feat: add docker default smoke contract
- files: Dockerfile default smoke, container materials audit, runtime/release docs, tests, history

Next:
- Commit the Docker default smoke contract, then continue polishing final workflow delivery while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Index Docker default smoke in delivery bundle

Context:
- The Dockerfile now defaults to the standard branch smoke and writes `results/container_default_smoke`.
- Runtime and release-audit docs mention this default in-image smoke, but the final delivery bundle did not yet expose the contract.

Decisions:
- Add `runtime_recovery/container_default_smoke` to the delivery manifest.
- Point the row at `Dockerfile` and describe the expected `docker run` output directory.
- Keep this as a contract/evidence row rather than a runtime status row, because Docker is still unavailable on the current machine.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `runtime_recovery/container_default_smoke` was missing from the generated delivery manifest.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed after adding the delivery manifest row.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing the delivery bundle.
- `rg -n "container_default_smoke|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md results/release_checks/release_checks.md results/objective_audit/objective_audit.md` confirmed `runtime_recovery/container_default_smoke` is present in the final delivery bundle.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.
- `results/local_acceptance/local_acceptance_summary.md` still records `release_gate` failed with exit code `1`, while `quickstart_handoff` and `delivery_bundle` passed.

Commit:
- hash: 9fd7e5d28157d7fa3e2d2df8683fc113c9a9c75f
- message: docs: index docker default smoke in delivery bundle
- files: delivery bundle index, delivery bundle test, history

Next:
- Commit the delivery-bundle indexing update, then continue polishing final workflow delivery while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Surface Docker default smoke in objective audit

Context:
- The delivery bundle now indexes the Dockerfile default standard smoke contract.
- The long objective audit still summarized Docker/Apptainer reproducibility as container materials plus runtime readiness, without mentioning the new default in-image workflow smoke.

Decisions:
- Add the Dockerfile default standard smoke contract to the Docker/Apptainer reproducibility evidence text.
- Mention `results/container_default_smoke` in the blocked note so the audit distinguishes the static image contract from the missing host runtime commands.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py -q` first failed because the Docker/Apptainer reproducibility row did not mention `Dockerfile default standard smoke` or `results/container_default_smoke`.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 16 tests after updating the audit evidence and note.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing objective, handoff, quickstart, and delivery-bundle artifacts.
- `rg -n "Dockerfile default standard smoke|container_default_smoke|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:" results/objective_audit/objective_audit.md results/release_checks/release_checks.md results/delivery_bundle/delivery_bundle.md` confirmed the generated objective audit includes the Docker default smoke contract and `results/container_default_smoke`.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.
- `results/local_acceptance/local_acceptance_summary.md` still records `release_gate` failed with exit code `1`, while `quickstart_handoff` and `delivery_bundle` passed.

Commit:
- hash: 7e2a0ec2b229f66218c9c6887a54242508b6de40
- message: docs: surface docker default smoke in objective audit
- files: objective audit evidence, objective audit tests, history

Next:
- Commit the objective-audit evidence update, then continue polishing final workflow delivery while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Add Docker default smoke to handoff report

Context:
- The delivery bundle and objective audit now expose the Dockerfile default standard smoke contract.
- The first human-facing handoff report still listed only container profile smoke outputs, so users reading just that report could miss the in-image default smoke contract.

Decisions:
- Add `Dockerfile` and `results/container_default_smoke` to the handoff report `Key Evidence` list.
- Keep the next command focused on `runtime_bootstrap.sh` while Docker/Apptainer remain unavailable.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because the handoff report did not include `Dockerfile` or `results/container_default_smoke`.
- `python -m pytest tests/test_build_handoff_report.py -q` passed with 5 tests after adding both entries to `Key Evidence`.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing handoff and delivery-bundle artifacts.
- `rg -n "Dockerfile|container_default_smoke|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:" results/handoff/handoff_report.md results/release_checks/release_checks.md results/objective_audit/objective_audit.md` confirmed the generated handoff report includes `Dockerfile` and `results/container_default_smoke`.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.
- `results/local_acceptance/local_acceptance_summary.md` still records `release_gate` failed with exit code `1`, while `quickstart_handoff` and `delivery_bundle` passed.

Commit:
- hash: 2ea9b31dfb91ed698c87314c7cfe9a62b0104825
- message: docs: add docker default smoke to handoff report
- files: handoff report, handoff report tests, history

Next:
- Commit the handoff-report update, then continue polishing final workflow delivery while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Add Docker default smoke to handoff summary TSV

Context:
- The handoff Markdown report now lists `Dockerfile` and `results/container_default_smoke`.
- The machine-readable `results/handoff/handoff_summary.tsv` still lacked a stable key for the Dockerfile default standard smoke contract.

Decisions:
- Add `container_default_smoke` to `build_handoff_sections()`.
- Make `write_summary_tsv()` include a default `container_default_smoke` row even when older callers pass a partial section dictionary.
- Use `Dockerfile -> results/container_default_smoke` as the stable summary value.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because `container_default_smoke` was missing from `build_handoff_sections()` and the summary TSV output.
- `python -m pytest tests/test_build_handoff_report.py -q` passed with 5 tests after adding the stable handoff summary key.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing handoff and delivery-bundle artifacts.
- `rg -n "container_default_smoke|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:" results/handoff/handoff_summary.tsv results/release_checks/release_checks.md results/objective_audit/objective_audit.md` confirmed the generated `results/handoff/handoff_summary.tsv` contains `container_default_smoke`.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.
- `results/local_acceptance/local_acceptance_summary.md` still records `release_gate` failed with exit code `1`, while `quickstart_handoff` and `delivery_bundle` passed.

Commit:
- hash: 0f6dc778dd3c39efe24aa53a2e72b14e841c9390
- message: docs: expose docker default smoke in handoff summary
- files: handoff summary builder, handoff summary tests, history

Next:
- Commit the handoff-summary update, then continue polishing final workflow delivery while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Document container default smoke handoff key

Context:
- `results/handoff/handoff_summary.tsv` now includes a stable `container_default_smoke` key.
- README and the readiness checklist still described the handoff TSV generically, so users and scripts did not have a documented stable key to look for.

Decisions:
- Document `container_default_smoke` in README and `docs/readiness_checklist.md`.
- Use the same stable value as the TSV: `Dockerfile -> results/container_default_smoke`.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/readiness_checklist.md`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report tests/test_runtime_environment_files.py::test_readiness_checklist_points_to_local_acceptance_summary -q` first failed because README and the readiness checklist did not document `container_default_smoke`.
- The same command passed with 2 tests after documenting the stable handoff summary key.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing handoff and delivery-bundle artifacts.
- `rg -n "container_default_smoke|Dockerfile -> results/container_default_smoke|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:" README.md docs/readiness_checklist.md results/handoff/handoff_summary.tsv results/release_checks/release_checks.md results/objective_audit/objective_audit.md` confirmed README, readiness checklist, and the generated handoff TSV all document the stable key.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.
- `results/local_acceptance/local_acceptance_summary.md` still records `release_gate` failed with exit code `1`, while `quickstart_handoff` and `delivery_bundle` passed.

Commit:
- hash: 69c46a74d770bb4bcd70ac5c8048f1accd699edb
- message: docs: document docker default smoke handoff key
- files: README, readiness checklist, runtime docs tests, history

Next:
- Commit the handoff-key documentation update, then continue polishing final workflow delivery while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Run Docker default smoke in runtime bootstrap

Context:
- The Dockerfile default command now runs the standard branch smoke and writes `results/container_default_smoke`.
- The generated runtime bootstrap script built the Docker image but did not run that default smoke before Apptainer build and container-profile smoke checks.

Decisions:
- Add `docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest` to the generated bootstrap shell.
- Place it immediately after `docker build -t genefam-pipeline:latest .`.
- Document the command and `results/container_default_smoke` output in the generated bootstrap Markdown plan.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/plan_runtime_bootstrap.py`
- `tests/test_plan_runtime_bootstrap.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` first failed because the generated bootstrap plan did not run the Docker image default smoke.
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` passed with 3 tests after adding the `docker run` default smoke command and documentation.
- `python -m pytest tests -q` passed with 274 tests.
- `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` regenerated the bootstrap Markdown and shell outputs.
- `rg -n "docker build|docker run --rm|container_default_smoke|apptainer build" results/readiness/runtime_bootstrap.sh results/readiness/runtime_bootstrap_plan.md` confirmed the generated bootstrap script runs the Docker default smoke immediately after image build and before Apptainer build.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing readiness, objective, handoff, quickstart, and delivery-bundle artifacts.
- `rg -n "docker run --rm|container_default_smoke|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:" results/readiness/runtime_bootstrap.sh results/readiness/runtime_bootstrap_plan.md results/release_checks/release_checks.md results/objective_audit/objective_audit.md results/handoff/handoff_summary.tsv` confirmed generated evidence contains the Docker default smoke command and stable handoff key.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.
- `results/local_acceptance/local_acceptance_summary.md` still records `release_gate` failed with exit code `1`, while `quickstart_handoff` and `delivery_bundle` passed.

Commit:
- hash: 1e824c5dba3cc97d7316e8990665834ee36378c9
- message: feat: run docker default smoke in runtime bootstrap
- files: runtime bootstrap planner, runtime bootstrap tests, history

Next:
- Continue polishing final workflow delivery while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Document bootstrap Docker default smoke command

Timestamp:
- 2026-06-25 13:27:56 CST

Context:
- The runtime bootstrap script already generates a Docker image default smoke command.
- README, readiness, runtime, and release docs still described the bootstrap broadly, which could make the container step look like premature packaging instead of final runtime verification.

Decisions:
- Expose the exact Docker default smoke command in the human-facing docs: `docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest`.
- Keep Docker/Apptainer framed as the remaining external runtime blocker, while the analysis workflow and Conda/local evidence remain the current development focus.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/runtime_environment.md`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `tests/test_runtime_environment_files.py`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit tests/test_runtime_environment_files.py::test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file tests/test_runtime_environment_files.py::test_readme_current_status_matches_release_evidence tests/test_release_audit_docs.py::test_release_audit_maps_goal_requirements_to_evidence_and_commands -q` first failed with 4 tests because the docs did not include the exact Docker default smoke command.
- The same command passed with 4 tests after documenting the bootstrap Docker default smoke command.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release, handoff, quickstart, local acceptance, and delivery-bundle evidence.
- `rg -n 'docker run --rm|container_default_smoke|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:' README.md docs/runtime_environment.md docs/readiness_checklist.md docs/release_audit.md results/readiness/runtime_bootstrap.sh results/readiness/runtime_bootstrap_plan.md results/release_checks/release_checks.md results/objective_audit/objective_audit.md results/local_acceptance/local_acceptance_summary.md` confirmed README, runtime docs, readiness checklist, release audit, and generated bootstrap outputs all expose the Docker default smoke command and `container_default_smoke` output.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 8857c70168566b958f5a4e3075d39e58405ff970
- message: docs: document bootstrap docker default smoke command
- files: README, runtime docs, readiness checklist, release audit, runtime docs tests, release audit tests, history

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-27 - Add publication report audit release gate

Timestamp:
- 2026-06-27 02:54:03 CST

Context:
- The active `/goal` requires a paper-level final report with close reading for every figure, software and R package versions in methods, QC notes, and reproducibility information.
- Existing figure smokes and reports produced the needed artifacts, but release checks did not have a dedicated gate proving that plot manifests, figure interpretations, software versions, and final reports were closed together.

Decisions:
- Add a standalone publication report audit that checks the `Nextflow standard visualization smoke` report package rather than relying only on dispersed plot-specific smokes.
- Require every registered plot to have a structured figure interpretation row with QC tables, method/software, reproducibility, result-reading status, and output path.
- Require the final report to embed the software-version section and every registered figure's interpretation details.
- Make the objective audit's `final reports` item depend on the new publication report audit.

Added:
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `results/publication_report_audit/publication_report_audit.tsv`
- `results/publication_report_audit/publication_report_audit.md`

Modified:
- `HISTORY.md`
- `README.md`
- `README.zh-CN.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `tests/test_audit_objective_completion.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py -q` first failed because `bin.genefam.audit_publication_report` did not exist, then passed with 3 tests after implementation.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_publication_report_audit_after_visualization_report -q` first failed because `publication report audit` was not present in `default_checks()`, then passed after wiring it after `Nextflow standard visualization smoke`.
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_require_publication_report_audit -q` first failed because `final reports` was considered achieved without the publication audit, then passed after tightening the objective audit.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` exited `0`.
- `python -m pytest tests -q` passed with 356 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; `results/release_checks/release_checks.md` reports `Passed: 44`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `results/publication_report_audit/publication_report_audit.md` reports `Passed: 4`, `Failed: 0`, and `Complete: true`.
- `results/objective_audit/objective_audit.md` reports `Achieved: 12`, `Blocked: 1`, `Missing: 0`, and `Complete: false`; the remaining blocker is Docker/Apptainer reproducibility.

Commit:
- hash: c7e5b29c68cd3dc589aa46ae5340b10c868efe84
- message: feat: audit publication report closure
- files: publication report audit, release/objective audit wiring, README docs, tests, history

Next:
- Continue toward the final container/Apptainer reproducibility stage once local runtimes are available.

## 2026-06-27 - Document publication audit in release audit evidence map

Timestamp:
- 2026-06-27 03:14:55 CST

Context:
- `publication_report_audit` was present in the runtime outputs and user-facing quickstart/readiness docs, but `docs/release_audit.md` still omitted it from the requirement-to-evidence map.
- The active `/goal` requires every figure's close reading, software/R package versions, QC, and reproducibility evidence to be represented in the final validation surfaces.

Decisions:
- Add publication audit TSV/Markdown outputs to the release-output inventory.
- Add `audit_publication_report.py` and publication audit artifacts to the quickstart handoff evidence row.
- Expand the final report evidence row to include figure interpretations, software versions, and the publication audit artifact.

Added:
- none

Modified:
- `HISTORY.md`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not mention `audit_publication_report.py`.
- `python -m pytest tests/test_release_audit_docs.py -q` passed after updating the release audit evidence map.
- `python -m pytest tests/test_release_audit_docs.py tests/test_quickstart_docs.py tests/test_runtime_environment_files.py tests/test_audit_publication_report.py -q` passed with 19 tests.
- `python -m pytest tests -q` passed with 356 tests.
- `rg -n "audit_publication_report.py|publication report audit|publication_report_audit|figure interpretations|software versions|reproducibility commands" docs/release_audit.md` confirmed the publication audit evidence entries.

Commit:
- hash: b9299ed4f178be4d32dd3790d04735069ad05dc2
- message: docs: add publication audit release evidence
- files: release audit docs, release audit docs test, history

Next:
- Continue toward the final container/Apptainer reproducibility stage once local runtimes are available.

## 2026-06-27 - Document publication audit in readiness checklist

Timestamp:
- 2026-06-27 03:11:42 CST

Context:
- `publication_report_audit` was documented in quickstart and surfaced in local acceptance/delivery outputs, but `docs/readiness_checklist.md` still omitted it from the first files to inspect.
- The active `/goal` requires a complete MVP handoff, so the readiness checklist should point to the same paper-style report closure evidence as the command outputs.

Decisions:
- Add `results/publication_report_audit/publication_report_audit.md` to the readiness checklist's first inspection list.
- Document that the publication audit checks figure interpretations, QC tables, software versions, and reproducibility commands.
- Include publication audit output in the post-runtime-refresh file list.

Added:
- none

Modified:
- `HISTORY.md`
- `docs/readiness_checklist.md`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit -q` first failed because `docs/readiness_checklist.md` did not mention `results/publication_report_audit/publication_report_audit.md`.
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit -q` passed after updating the checklist.
- `python -m pytest tests/test_runtime_environment_files.py tests/test_quickstart_docs.py tests/test_local_acceptance_script.py tests/test_run_delivery_bundle.py -q` passed with 18 tests.
- `python -m pytest tests -q` passed with 356 tests.
- `rg -n "publication_report_audit|paper-style report closure|figure interpretations|software versions|reproducibility" docs/readiness_checklist.md` confirmed the documented readiness entrypoints.

Commit:
- hash: 8d5eb80d7af55a5bbdee4c2dcb1e6a2a870281c9
- message: docs: add publication audit readiness checklist
- files: readiness checklist docs, runtime environment docs test, history

Next:
- Continue toward the final container/Apptainer reproducibility stage once local runtimes are available.

## 2026-06-27 - Document publication audit in quickstart

Timestamp:
- 2026-06-27 03:09:01 CST

Context:
- `publication_report_audit` is now present in release checks, local acceptance, and delivery bundle outputs.
- `docs/quickstart.md` still described local acceptance as release/quickstart/delivery only, so the shortest user-facing guide did not explain the paper-style report closure artifact.

Decisions:
- Document `publication_report_audit` in the local acceptance wrapper description.
- Add `results/publication_report_audit/publication_report_audit.md` to the quickstart key output list.
- State that the publication audit checks figure interpretations, QC tables, software versions, and reproducibility commands.

Added:
- none

Modified:
- `HISTORY.md`
- `docs/quickstart.md`
- `tests/test_quickstart_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_quickstart_docs.py -q` first failed because `docs/quickstart.md` did not mention `results/publication_report_audit/publication_report_audit.md`.
- `python -m pytest tests/test_quickstart_docs.py -q` passed after updating the quickstart guide.
- `python -m pytest tests/test_quickstart_docs.py tests/test_local_acceptance_script.py tests/test_write_local_acceptance_summary.py tests/test_run_delivery_bundle.py tests/test_release_audit_docs.py -q` passed with 8 tests.
- `rg -n "publication_report_audit|paper-style report closure|figure interpretations|software versions|reproducibility" docs/quickstart.md` confirmed the documented local acceptance and publication audit entrypoints.

Commit:
- hash: af10a4ece382e81578184e56be2e94c4ba0a72c4
- message: docs: explain publication audit quickstart
- files: quickstart docs, quickstart docs test, history

Next:
- Continue toward the final container/Apptainer reproducibility stage once local runtimes are available.

## 2026-06-27 - Add publication report audit to local acceptance summary

Timestamp:
- 2026-06-27 03:06:22 CST

Context:
- `publication_report_audit` was visible in release checks and the delivery bundle, but the compact local acceptance summary still only showed release, quickstart, and delivery bundle steps.
- The active `/goal` requires a perfect MVP handoff, so the local one-command acceptance surface should show the paper-style report closure evidence directly.

Decisions:
- Add a `publication_report_audit` row to local acceptance summaries.
- Keep release gate as the source of truth, and have `scripts/run_local_acceptance.sh` read the `publication report audit` exit code from `release_checks.tsv`.
- Expose `PUBLICATION_OUTDIR`, defaulting to `results/publication_report_audit`, for local acceptance wrapper customization.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/write_local_acceptance_summary.py`
- `scripts/run_local_acceptance.sh`
- `tests/test_local_acceptance_script.py`
- `tests/test_write_local_acceptance_summary.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_write_local_acceptance_summary.py -q` first failed because `write_acceptance_summary()` and `build_acceptance_rows()` did not accept publication audit arguments.
- `python -m pytest tests/test_local_acceptance_script.py -q` first failed because `scripts/run_local_acceptance.sh` did not expose `PUBLICATION_OUTDIR`, pass publication audit status, or print the publication audit artifact.
- `python -m pytest tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py -q` passed after adding the local acceptance row and shell wiring.
- `python bin/genefam/write_local_acceptance_summary.py --release-status 0 --publication-status 0 --quickstart-status 0 --delivery-status 0 --release-outdir results/release_checks --publication-outdir results/publication_report_audit --quickstart-outdir results/quickstart --delivery-outdir results/delivery_bundle --outdir results/local_acceptance` regenerated local acceptance outputs with `publication_report_audit`.
- `python -m pytest tests -q` passed with 356 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; `results/release_checks/release_checks.md` reports `Passed: 44`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `results/local_acceptance/local_acceptance_summary.tsv` now includes `publication_report_audit	passed	0	results/publication_report_audit/publication_report_audit.md	paper-style report closure evidence`.
- `results/handoff/handoff_summary.tsv` still reports `analysis_release_ready=true; final_stage_blockers=Docker/Apptainer reproducibility`.

Commit:
- hash: babb9ff4e1dc1bf406a1f840fa532ec4d32c474a
- message: feat: show publication audit in local acceptance
- files: local acceptance summary writer, local acceptance wrapper script, tests, history

Next:
- Continue toward the final container/Apptainer reproducibility stage once local runtimes are available.

## 2026-06-27 - Surface publication report audit in delivery bundle

Timestamp:
- 2026-06-27 03:00:01 CST

Context:
- The publication report audit was already a required release check, but the final delivery bundle did not yet expose it as a first-class artifact for the user to open.
- The active `/goal` asks for a perfect MVP-level handoff, so the final user-facing bundle should show the evidence that every figure has close reading, QC, software versions, and reproducibility information.

Decisions:
- Add `publication_report_audit` to the delivery manifest `status` section.
- Derive its availability from the release check named `publication report audit`.
- Point the bundle entry to `results/publication_report_audit/publication_report_audit.md`.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index -q` first failed because `status/publication_report_audit` was missing from the delivery manifest.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed after adding the delivery manifest entry.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` regenerated `results/delivery_bundle/delivery_bundle.md` and `results/delivery_bundle/delivery_manifest.tsv`.
- `python -m pytest tests/test_run_delivery_bundle.py tests/test_run_release_checks.py tests/test_audit_publication_report.py -q` passed with 54 tests.
- `python -m pytest tests -q` passed with 356 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; `results/release_checks/release_checks.md` reports `Passed: 44`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `results/delivery_bundle/delivery_manifest.tsv` now includes `status	publication_report_audit	available	results/publication_report_audit/publication_report_audit.md	paper-style report closure: figure interpretations, QC, software versions, and reproducibility`.

Commit:
- hash: 86fa69aa56462fcf5448b9346e7406fb768679b0
- message: feat: surface publication audit in delivery bundle
- files: delivery bundle manifest builder, delivery bundle test, history

Next:
- Continue toward the final container/Apptainer reproducibility stage once local runtimes are available.

## 2026-06-27 - Add per-figure QC and reproducibility notes to final reports

Timestamp:
- 2026-06-27 01:57:42 CST

Context:
- The final report already rendered figure-level interpretation text, but each figure still needed explicit QC tables, method/software provenance, reproducibility commands, and a close-reading status.
- The user requires final reports to support per-figure close reading and method sections that identify software and versions.

Decisions:
- Keep figure interpretation generation template-driven so every registered plot gets the same report contract.
- Use real repository smoke commands in figure reproducibility notes and test that the referenced scripts exist.
- Preserve the current workflow stage: flow-first development, with container/profile failures recorded as known final-stage blockers.

Added:
- QC table, method/software, reproducibility, and close-reading status fields in `figure_interpretations.tsv`.
- Tests that require the new report fields and verify referenced reproducibility scripts exist.

Modified:
- `HISTORY.md`
- `bin/genefam/build_figure_interpretations.py`
- `bin/genefam/assemble_report.py`
- `tests/test_build_figure_interpretations.py`
- `tests/test_assemble_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_figure_interpretations.py tests/test_assemble_report.py -q` first failed with 3 failures because `qc_tables`, `method_and_software`, `reproducibility`, and `result_reading_status` were not generated or rendered yet.
- `python -m pytest tests/test_build_figure_interpretations.py tests/test_assemble_report.py -q` passed with 5 tests after implementation.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` passed and refreshed the standard report package.
- `rg -n "run_mcscanx_circlize_smoke|run_kaks_wgd_plot_smoke|run_expression_heatmap_smoke|run_promoter_cis_smoke|run_tree_feature_smoke" results/nextflow_standard_smoke/standard/report/final_report.md` confirmed the final report includes real reproducibility smoke commands.
- `python -m pytest tests -q` passed with 349 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`: 42 checks passed; `readiness audit` remained the only required failure; Docker and Apptainer profile smokes remained optional failures.

Commit:
- hash: e07f52e9b92bc568ab159a7466b94a20d8655a398
- message: feat: add figure qc reproducibility notes
- files: figure interpretation builder, final report assembler, figure/report tests, history

Next:
- Continue final MVP hardening by reducing the readiness audit gap, then return to container/profile packaging after the analysis flow is fully stable.

## 2026-06-27 - Make container runtime readiness optional for analysis MVP gate

Timestamp:
- 2026-06-27 02:10:10 CST

Context:
- `run_release_checks.py` still failed the required readiness gate because `audit_readiness.py` treated missing `docker` and `apptainer` as required command failures.
- The project direction is flow-first development, with Docker/Apptainer packaging kept as the final stage rather than a blocker for the analysis MVP.

Decisions:
- Add a `requirement` column to `command_readiness.tsv`.
- Keep core analysis commands as `required`.
- Mark `docker` and `apptainer` as `optional` container-stage commands so they remain visible in readiness, bootstrap, handoff, and delivery evidence without blocking release readiness for the analysis flow.

Added:
- Readiness tests covering optional container commands and the new `requirement` field.
- Documentation language that distinguishes required core analysis commands from optional container-stage commands.

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_readiness.py`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `tests/test_audit_readiness.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_readiness.py -q` first failed with 8 failures because `requirement` was not generated and optional container commands still blocked readiness.
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit -q` first failed because the readiness checklist did not document required core analysis commands versus optional container-stage commands.
- `python -m pytest tests/test_audit_readiness.py -q` passed with 9 tests after implementation.
- `python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv` exited `0`; `docker` and `apptainer` remained `missing` with `requirement=optional`.
- `python -m pytest tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit tests/test_release_audit_docs.py tests/test_audit_readiness.py -q` passed with 11 tests after documentation updates.
- `python -m pytest tests -q` passed with 350 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; release checks reported `Passed: 43`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.

Commit:
- hash: 69d802721f41e1e4ff23a99041f75d58c30cfbca
- message: fix: make container readiness optional
- files: readiness audit, readiness/release docs, README, readiness tests, history

Next:
- Continue final MVP audit against the original objective, with Docker and Apptainer profile smokes preserved as explicit optional final-stage packaging work.

## 2026-06-27 - Detect IQ-TREE version through iqtree fallback

Timestamp:
- 2026-06-27 02:16:01 CST

Context:
- The software version table already recorded R package versions for plotting methods, including `ggplot2`, `pheatmap`, `circlize`, `ggtree`, `treeio`, and `ggNetView`.
- The standard Nextflow report still showed `IQ-TREE` as `version_not_detected` because the version collector only tried `iqtree2 --version`, while the `GeneFamilyFlow` environment exposes `iqtree`.

Decisions:
- Allow software version commands to define ordered fallback command options.
- Use `iqtree2 --version` first and fall back to `iqtree --version`.
- Preserve the existing single-command API for current tests and callers.

Added:
- A regression test proving `collect_versions` can use an alternate command when the primary command is missing.

Modified:
- `HISTORY.md`
- `bin/genefam/collect_software_versions.py`
- `tests/test_collect_software_versions.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_collect_software_versions.py -q` first failed because `collect_versions` could not accept fallback command lists.
- `python -m pytest tests/test_collect_software_versions.py -q` passed with 3 tests after implementation.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` passed and refreshed the standard report package.
- `rg -n "IQ-TREE|ggNetView|circlize|pheatmap|R_package" results/nextflow_standard_smoke/standard/report/software_versions.tsv results/nextflow_standard_smoke/standard/report/final_report.md` confirmed `IQ-TREE` is detected from `iqtree --version` and R plotting package versions remain in the report.
- `python -m pytest tests -q` passed with 351 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; release checks reported `Passed: 43`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.

Commit:
- hash: cbff7f3e8982d58b677ceafacacb63032433e95d
- message: fix: detect iqtree version fallback
- files: software version collector, software version tests, history

Next:
- Continue closing paper-level report polish and keep Docker/Apptainer profile smokes as explicit final-stage packaging work.

## 2026-06-27 - Add IQ-TREE fallback to runtime bootstrap script

Timestamp:
- 2026-06-27 02:21:18 CST

Context:
- Readiness and software-version collection now accept `iqtree` as a fallback when `iqtree2` is not exposed by the active Conda environment.
- The generated `runtime_bootstrap.sh` still hard-coded `conda run -n GeneFamilyFlow iqtree2 --version`, which could make the recovery script fail on the same environment where reports correctly detect IQ-TREE through `iqtree`.

Decisions:
- Add the same `iqtree2` then `iqtree` fallback to the generated runtime bootstrap script.
- Document the alias behavior in `runtime_bootstrap_plan.md`.

Added:
- A bootstrap-plan regression test requiring the generated shell script to include the IQ-TREE fallback command.

Modified:
- `HISTORY.md`
- `bin/genefam/plan_runtime_bootstrap.py`
- `tests/test_plan_runtime_bootstrap.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` first failed because the generated shell still only used `iqtree2 --version`.
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` passed with 3 tests after implementation.
- `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` regenerated the bootstrap plan and shell.
- `rg -n "iqtree2 --version|iqtree --version|IQ-TREE verification" results/readiness/runtime_bootstrap.sh results/readiness/runtime_bootstrap_plan.md` confirmed the generated artifacts include the fallback and note.
- `python -m pytest tests -q` passed with 351 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; release checks reported `Passed: 43`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.

Commit:
- hash: 05baf8cb4b8af42b26c7c0b904ed56cde0544a21
- message: fix: add iqtree bootstrap fallback
- files: runtime bootstrap planner, bootstrap tests, history

Next:
- Continue final-stage container hardening while preserving the current analysis-flow release readiness.

## 2026-06-27 - Add actionable missing-runtime notes to container profile smoke

Timestamp:
- 2026-06-27 02:26:53 CST

Context:
- Docker and Apptainer are still not installed on this machine, so container profile smokes remain optional failures.
- The existing `missing_runtime` note only said the runtime was absent; it did not point directly to the generated bootstrap script, rerun command, or diagnostic output path.

Decisions:
- Keep Docker/Apptainer profile smokes optional until the final packaging environment exists.
- Make each missing-runtime profile smoke report actionable by naming the bootstrap command, rerun command, and expected Markdown diagnostic artifact.

Added:
- A regression test requiring `missing_runtime` notes to include `bash results/readiness/runtime_bootstrap.sh`, the profile smoke rerun command, and the profile diagnostic Markdown path.

Modified:
- `HISTORY.md`
- `bin/genefam/run_container_profile_smoke.py`
- `tests/test_run_container_profile_smoke.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_container_profile_smoke.py -q` first failed because `missing_runtime` notes did not include the bootstrap next step.
- `python -m pytest tests/test_run_container_profile_smoke.py -q` passed with 6 tests after implementation.
- `python bin/genefam/run_container_profile_smoke.py --profile docker --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/docker` exited `1` as expected without Docker and refreshed the Docker diagnostic Markdown.
- `python bin/genefam/run_container_profile_smoke.py --profile apptainer --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/apptainer` exited `1` as expected without Apptainer and refreshed the Apptainer diagnostic Markdown.
- `rg -n "Next step: run|runtime_bootstrap.sh|Expected diagnostic output" results/container_profile_smoke/docker/container_profile_smoke.md results/container_profile_smoke/apptainer/container_profile_smoke.md results/release_checks/release_checks.md` confirmed both profile diagnostics now include the actionable next step.
- `python -m pytest tests -q` passed with 351 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; release checks reported `Passed: 43`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.

Commit:
- hash: 6ab7879f6eab4e98b16d4be3ed4acbb4678d6eaf
- message: fix: clarify container runtime diagnostics
- files: container profile smoke diagnostics, container smoke tests, history

Next:
- Continue final-stage container hardening; full Docker/Apptainer execution still requires installing or exposing those runtimes on the machine.

## 2026-06-27 - Surface container runtime recovery notes in release checks

Timestamp:
- 2026-06-27 02:32:21 CST

Context:
- Container profile smoke Markdown files contained actionable missing-runtime recovery notes.
- `results/release_checks/release_checks.md` still showed blank notes for optional Docker and Apptainer failures because `run_container_profile_smoke.py` wrote diagnostics only to files, not stdout/stderr captured by the release runner.

Decisions:
- Print the container profile smoke note from the CLI after writing TSV and Markdown outputs.
- Keep the structured TSV/Markdown outputs unchanged.

Added:
- A CLI regression test requiring missing-runtime container profile smoke output to include the runtime bootstrap command and profile rerun command on stdout.

Modified:
- `HISTORY.md`
- `bin/genefam/run_container_profile_smoke.py`
- `tests/test_run_container_profile_smoke.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_container_profile_smoke.py -q` first failed because the CLI stdout was empty.
- `python -m pytest tests/test_run_container_profile_smoke.py -q` passed with 6 tests after printing the note.
- `python -m pytest tests -q` passed with 351 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; release checks reported `Passed: 43`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- `rg -n "Docker profile smoke|Apptainer profile smoke|runtime_bootstrap.sh|Expected diagnostic output" results/release_checks/release_checks.md` confirmed the release summary now includes actionable recovery notes for both optional container profile failures.

Commit:
- hash: d1cf4ef833f5f31f3423855a6c6744e9d03b9921
- message: fix: surface container recovery in release notes
- files: container profile smoke CLI output, container profile smoke tests, history

Next:
- Continue final-stage container hardening; true Docker/Apptainer profile success still depends on installing or exposing those runtimes.

## 2026-06-27 - Add explicit analysis-flow status to handoff report

Timestamp:
- 2026-06-27 02:44:53 CST

Context:
- The handoff report included release-check and objective-audit summaries, but the analysis-flow readiness signal was embedded inside the release summary string.
- The user-facing handoff should clearly separate the current analysis MVP state from the final-stage Docker/Apptainer blocker.

Decisions:
- Add an `analysis_flow_status` section to the handoff summary.
- Derive `analysis_release_ready` from required release-check failures.
- Derive `final_stage_blockers` from blocked or missing objective requirements.

Added:
- Handoff tests requiring `analysis_flow_status` in section data, Markdown, and summary TSV outputs.

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because `analysis_flow_status` was missing from the generated sections and Markdown.
- `python -m pytest tests/test_build_handoff_report.py -q` passed with 5 tests after implementation.
- `python bin/genefam/build_handoff_report.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --container-smoke results/container_profile_smoke/docker/container_profile_smoke.tsv --container-smoke results/container_profile_smoke/apptainer/container_profile_smoke.tsv --out results/handoff/handoff_report.md --summary-tsv results/handoff/handoff_summary.tsv` refreshed the handoff artifacts.
- `rg -n "analysis_flow_status|Analysis flow status|analysis_release_ready" results/handoff/handoff_report.md results/handoff/handoff_summary.tsv` confirmed the handoff now reports `analysis_release_ready=true; final_stage_blockers=Docker/Apptainer reproducibility`.
- `python -m pytest tests -q` passed with 351 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; release checks reported `Passed: 43`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- The same `rg` check confirmed release checks regenerated the enhanced handoff artifacts with the new analysis-flow status.

Commit:
- hash: 82e5311c66cce972f24fcdb9a2a8bfe87907a660
- message: feat: clarify analysis flow handoff status
- files: handoff report builder, handoff tests, history

Next:
- Continue final-stage container hardening; true Docker/Apptainer profile success still depends on installing or exposing those runtimes.

## 2026-06-27 - Add release-ready and container profile diagnostics to delivery bundle

Timestamp:
- 2026-06-27 02:39:09 CST

Context:
- The delivery bundle listed release checks, objective blockers, runtime commands, and runtime recovery artifacts.
- It did not show a direct `release_ready=true` handoff row or direct links to the Docker/Apptainer profile smoke diagnostic Markdown files.

Decisions:
- Add a `status/release_ready` row derived from required and optional release-check failures.
- Add `runtime_recovery/docker_profile_smoke` and `runtime_recovery/apptainer_profile_smoke` rows pointing to the optional container diagnostic Markdown files.
- Keep Docker/Apptainer profile rows marked `missing` when their optional smoke checks fail.

Added:
- Delivery bundle tests requiring release-ready status and container profile diagnostic links in both TSV and Markdown outputs.

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because the delivery manifest did not include the new `release_ready` row or container profile diagnostic entries.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed with 1 test after implementation.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` refreshed the delivery bundle.
- `rg -n "release_ready|docker_profile_smoke|apptainer_profile_smoke|container_profile_smoke" results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md` confirmed the new status and diagnostic rows were present.
- `python -m pytest tests -q` passed with 351 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `0`; release checks reported `Passed: 43`, `Required failed: 0`, `Optional failed: 2`, and `Release ready: true`.
- The same `rg` check confirmed release checks regenerated the enhanced delivery bundle with the new rows.

Commit:
- hash: 69c64c9f26299d7ed226c0906935d5701c45b4b1
- message: feat: add container diagnostics to delivery bundle
- files: delivery bundle builder, delivery bundle tests, history

Next:
- Continue final-stage container hardening; true Docker/Apptainer profile success still depends on installing or exposing those runtimes.

## 2026-06-27 - Add density and duplicate-type tracks to MCScanX circlize plots

Timestamp:
- 2026-06-27 00:55:00 CST

Context:
- The MCScanX/circlize path already generated chromosome sectors and syntenic links.
- The reference plotting matrix still marked MCScanX/circlize synteny as partial because it lacked density tracks and duplicate-type style tracks.

Decisions:
- Extend `build_circlize_inputs.py` to generate linked-gene density windows and duplicate-type track rows.
- Preserve the previous three-output Python API by requiring `include_tracks=True` for the five-output enhanced mode.
- Preserve the old `plot_mcscanx_circlize.R <chromosomes.tsv> <links.tsv> <outdir>` interface while adding the enhanced five-argument mode.
- Label linked genes as `syntenic` when no explicit duplicate-type table is supplied, so the standard branch can still render a complete track.
- Add the new support tables to the standard report index and wire the changed Nextflow output positions explicitly.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_circlize_inputs.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_mcscanx_circlize_smoke.py`
- `docs/reference_plotting_reuse.md`
- `scripts/plot_mcscanx_circlize.R`
- `tests/test_build_circlize_inputs.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_run_mcscanx_circlize_smoke.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_circlize_inputs.py tests/test_run_mcscanx_circlize_smoke.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_reference_plotting_reuse.py -q` first failed because density and duplicate-type track generation was not implemented.
- `python -m pytest tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch tests/test_standard_branch_report_index.py -q` first failed because the standard report index and main workflow did not know the new circlize support-table outputs.
- `python -m pytest tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch tests/test_standard_branch_report_index.py tests/test_build_circlize_inputs.py tests/test_run_mcscanx_circlize_smoke.py tests/test_reference_plotting_reuse.py -q` passed with 10 tests.
- `python bin/genefam/run_mcscanx_circlize_smoke.py --r-bin /usr/local/bin/R --outdir results/mcscanx_circlize_smoke` passed and wrote `tables/circlize_link_density.tsv`, `tables/circlize_duplicate_type_tracks.tsv`, and `plots/mcscanx_circlize.pdf/png`.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --outdir results/nextflow_standard_feature_smoke` passed and the standard report index marked the new circlize support tables as available.
- `python -m pytest tests -q` passed with 343 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` with `41 passed / 3 failed`; `MCScanX circlize visualization smoke` passed and included the two new support tables, while `readiness audit` failed and Docker/Apptainer profile smokes remained optional failures.

Commit:
- hash: 2d41dab
- message: feat: add circlize density tracks
- files: circlize input builder, circlize R plot, MCScanX circlize smoke, standard report index, Nextflow wiring, reference plotting docs, tests, history

Next:
- Continue remaining paper-level visualization polish, especially promoter/copy-number/pangenome interpretation gaps, while container packaging remains final-stage work.

## 2026-06-27 - Add per-element promoter cis-element annotations and dot heatmap

Timestamp:
- 2026-06-27 01:04:00 CST

Context:
- The promoter cis-element path already normalized PlantCARE-style input and produced a category matrix plus top-element summary.
- The reference plotting matrix still marked promoter cis-element visualization as partial because per-element biological annotations and dot-heatmap style tracks were missing.

Decisions:
- Add `promoter_cis_gene_element_matrix.tsv` to retain gene-by-element counts and promoter positions.
- Add `promoter_cis_element_annotations.tsv` to summarize each cis-element category, gene/species support, total count, position range, median position, and descriptions.
- Extend `plot_promoter_cis_elements.R` with an enhanced five-argument mode that draws a gene-by-element dot heatmap while preserving the old three-argument interface.
- Wire the new tables through `PLOT_PROMOTER_CIS_ELEMENTS`, the standard report index, and the main workflow output positions.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_promoter_cis_elements.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_promoter_cis_smoke.py`
- `docs/reference_plotting_reuse.md`
- `scripts/plot_promoter_cis_elements.R`
- `tests/test_build_promoter_cis_elements.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_run_promoter_cis_smoke.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_promoter_cis_elements.py tests/test_run_promoter_cis_smoke.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_standard_branch_report_index.py tests/test_reference_plotting_reuse.py -q` first failed because gene-element matrix, element annotations, R enhanced inputs, report index keys, and reference-matrix status were not implemented.
- `python -m pytest tests/test_build_promoter_cis_elements.py tests/test_run_promoter_cis_smoke.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_standard_branch_report_index.py tests/test_reference_plotting_reuse.py -q` passed with 9 tests after implementation.
- `python -m pytest tests/test_workflow_modules.py::test_main_workflow_includes_plot_processes tests/test_build_promoter_cis_elements.py tests/test_run_promoter_cis_smoke.py -q` passed with 4 tests after locking the `PLOT_PROMOTER_CIS_ELEMENTS.out[]` indices.
- `python bin/genefam/run_promoter_cis_smoke.py --r-bin /usr/local/bin/R --outdir results/promoter_cis_smoke` passed and wrote `tables/promoter_cis_gene_element_matrix.tsv`, `tables/promoter_cis_element_annotations.tsv`, and `plots/promoter_cis_elements.pdf/png`.
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_reference_plotting_reuse.py -q` passed with 8 tests.
- `python -m pytest tests -q` passed with 343 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` with `41 passed / 3 failed`; `promoter cis-element visualization smoke` passed and included the new gene-element matrix and element-annotation table, while `readiness audit` failed and Docker/Apptainer profile smokes remained optional failures.

Commit:
- hash: 64b6b16
- message: feat: add promoter element annotation tracks
- files: promoter cis-element table builder, R promoter plot, smoke runner, standard report index, Nextflow wiring, reference plotting docs, tests, history

Next:
- Continue remaining paper-level visualization polish, especially copy-number/gene-family summary and large-scale pangenome/Ks interpretation gaps.

## 2026-06-27 - Add gene family copy-number expansion panels

Timestamp:
- 2026-06-27 01:13:00 CST

Context:
- The gene family information plot already included per-species copy number, copy-number classes, and protein-property panels.
- The reference plotting matrix still marked gene family information and large-scale copy-number expansion as partial because species ordering and expansion/contracted interpretation tables were missing.

Decisions:
- Add `gene_family_species_order.tsv` to provide a stable copy-number-ranked plotting order.
- Add `gene_family_copy_number_expansion.tsv` to classify each species as `expanded`, `baseline`, `contracted`, or `absent` relative to the nonzero median copy number.
- Extend `plot_gene_family_info.R` with an enhanced six-argument mode that draws a copy-number expansion status panel while preserving the old four-argument interface.
- Wire the new tables into `PLOT_GENE_FAMILY_INFO`, the standard report index, and the main workflow output positions.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_gene_family_info.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_gene_family_info_smoke.py`
- `docs/reference_plotting_reuse.md`
- `scripts/plot_gene_family_info.R`
- `tests/test_build_gene_family_info.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_run_gene_family_info_smoke.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_gene_family_info.py tests/test_run_gene_family_info_smoke.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_standard_branch_report_index.py tests/test_reference_plotting_reuse.py -q` first failed because species-order and copy-number expansion tables were not implemented or wired.
- `python -m pytest tests/test_build_gene_family_info.py tests/test_run_gene_family_info_smoke.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_includes_plot_processes tests/test_standard_branch_report_index.py tests/test_reference_plotting_reuse.py -q` passed with 10 tests after implementation.
- `python bin/genefam/run_gene_family_info_smoke.py --r-bin /usr/local/bin/R --outdir results/gene_family_info_smoke` passed and wrote `tables/gene_family_species_order.tsv`, `tables/gene_family_copy_number_expansion.tsv`, and `plots/gene_family_info_summary.pdf/png`.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` passed and the standard report index marked `gene_family_species_order` and `gene_family_copy_number_expansion` as available.
- `python -m pytest tests -q` passed with 343 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` with `41 passed / 3 failed`; `gene family information visualization smoke` and `Nextflow standard branch smoke` passed, while `readiness audit` failed and Docker/Apptainer profile smokes remained optional failures.

Commit:
- hash: bda976c
- message: feat: add copy number expansion summary
- files: gene family info builder, R plot, smoke runner, standard report index, Nextflow wiring, reference plotting docs, tests, history

Next:
- Continue remaining paper-level polish for PPI upstream-network documentation and large-scale pangenome/Ks interpretation templates, then final MVP acceptance audit.

## 2026-06-27 - Add WGD event annotations to Ks distribution plots

Timestamp:
- 2026-06-27 00:44:00 CST

Context:
- The WGD branch already classified Ks pairs into anonymous WGD layers and named events such as alpha, beta, gamma, and theta.
- The Ks distribution plot was still a plain histogram, so the visual output did not directly show WGD event peaks/layers.

Decisions:
- Add a dedicated `kaks_wgd_annotations.tsv` plotting table derived from `wgd_layers.tsv`.
- Keep `wgd_event_evidence.tsv` as the interpretation/evidence table, and use the new annotation table only for figure labels and label positions.
- Preserve the old `plot_kaks.R <kaks.tsv> <outdir>` interface while adding the WGD-aware `plot_kaks.R <kaks.tsv> <kaks_wgd_annotations.tsv> <outdir>` mode.

Added:
- `bin/genefam/build_kaks_plot_annotations.py`
- `bin/genefam/run_kaks_wgd_plot_smoke.py`
- `tests/test_build_kaks_plot_annotations.py`
- `tests/test_run_kaks_wgd_plot_smoke.py`

Modified:
- `HISTORY.md`
- `bin/genefam/build_wgd_report_index.py`
- `bin/genefam/run_release_checks.py`
- `docs/reference_plotting_reuse.md`
- `scripts/plot_kaks.R`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_run_release_checks.py`
- `tests/test_wgd_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/duplication_retention.nf`
- `workflows/modules/plots.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_kaks_plot_annotations.py tests/test_run_kaks_wgd_plot_smoke.py -q` first failed because `bin.genefam.build_kaks_plot_annotations` did not exist.
- `python -m pytest tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_wgd_report_index.py tests/test_run_release_checks.py::test_default_checks_include_kaks_wgd_annotation_plot_smoke tests/test_reference_plotting_reuse.py -q` first failed because the new annotation table was not wired into Nextflow, report indexing, release checks, or the reference plotting matrix.
- `python -m pytest tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_wgd_report_index.py tests/test_run_release_checks.py::test_default_checks_include_kaks_wgd_annotation_plot_smoke tests/test_reference_plotting_reuse.py tests/test_build_kaks_plot_annotations.py tests/test_run_kaks_wgd_plot_smoke.py -q` passed with 10 tests.
- `python bin/genefam/run_kaks_wgd_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/kaks_wgd_plot_smoke` passed and wrote `tables/kaks_wgd_annotations.tsv`, `plots/ks_distribution.pdf`, and `plots/ks_distribution.png`.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke` passed and published alpha, beta, gamma, theta annotations in `results/nextflow_wgd_smoke/wgd/tables/kaks_wgd_annotations.tsv`.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke` passed and published `tables/kaks_wgd_annotations.tsv` for the raw MCScanX/KaKs entry.
- `python -m pytest tests -q` passed with 342 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1` with `41 passed / 3 failed`; the new `Ka/Ks WGD annotation plot smoke` passed, while `readiness audit` failed and Docker/Apptainer profile smokes remained optional failures.

Commit:
- hash: 7905bd3
- message: feat: annotate ks plots with wgd layers
- files: Ka/Ks WGD annotation builder, smoke runner, R plot script, Nextflow WGD wiring, WGD report index, release checks, plotting reuse docs, tests, history

Next:
- Continue paper-level visualization polish and final MVP acceptance while container profile execution remains outside the current no-container phase.

## 2026-06-25 16:08 - Add promoter and feature-summary visualization smokes

Context:
- The user asked to continue filling promoter analysis and MCScanX visualization, plus MEME motif, gene structure, and domain visualization/statistics for very large gene families.
- The user emphasized that large gene sets need statistics and summaries, not only per-gene visual outputs.

Decisions:
- Keep promoter extraction as a Python table/FASTA helper that consumes family candidates, species manifest, genome FASTA, and GFF3.
- Add a small self-contained promoter smoke rather than changing the species-bank fixtures, preserving the current optional-genome input contract.
- Aggregate domain, motif, gene-structure, synteny, and promoter evidence into `feature_summary.tsv` before plotting.
- Use `/usr/local/bin/R` and a shared R script to produce compact PDF/PNG feature-summary plots.
- Register the new promoter and feature-summary smokes in the default release checks.

Added:
- `bin/genefam/extract_promoters.py`
- `bin/genefam/run_promoter_smoke.py`
- `bin/genefam/summarize_feature_tables.py`
- `bin/genefam/run_feature_summary_smoke.py`
- `scripts/plot_feature_summary.R`
- `tests/test_extract_promoters.py`
- `tests/test_run_promoter_smoke.py`
- `tests/test_summarize_feature_tables.py`
- `tests/test_run_feature_summary_smoke.py`

Modified:
- `README.md`
- `docs/release_audit.md`
- `bin/genefam/run_release_checks.py`
- `tests/test_run_release_checks.py`
- `tests/test_release_audit_docs.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_feature_summary_smoke.py -q` passed after adding the feature-summary smoke runner.
- `python -m pytest tests/test_run_promoter_smoke.py tests/test_extract_promoters.py tests/test_summarize_feature_tables.py tests/test_run_feature_summary_smoke.py -q` passed with 6 tests after fixing the promoter smoke function call.
- `python -m pytest tests/test_run_release_checks.py tests/test_release_audit_docs.py -q` passed with 38 tests after wiring the new smokes into release checks and docs.
- `python bin/genefam/run_promoter_smoke.py --r-bin /usr/local/bin/R --outdir results/promoter_smoke` wrote promoter BED/FASTA plus feature-summary PDF/PNG.
- `python bin/genefam/run_feature_summary_smoke.py --domains results/domain_filter_smoke/tables/filtered_domains.tsv --motifs results/motif_smoke/tables/motif_summary.tsv --gene-structures results/gene_structure_smoke/tables/gene_structure_summary.tsv --synteny results/synteny_smoke/tables/syntenic_pairs.tsv --promoters results/promoter_smoke/tables/promoters.bed --r-bin /usr/local/bin/R --outdir results/feature_summary_smoke` wrote aggregate statistics and feature-summary PDF/PNG.
- `python -m pytest tests -q` passed with 290 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release evidence.
- `results/release_checks/release_checks.md` reports `Passed: 30`, `Required failed: 1`, `Optional failed: 2`; `promoter smoke` and `feature summary visualization smoke` both passed.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 4a28750cffab52e873f86af31dc14941917b2e76
- message: feat: add promoter and feature summary visualization
- files: promoter extraction, feature-summary statistics, R visualization, release checks, docs, tests, history
- hash: b6024d63b491edfa981d346dec5922ae0dfe4cb9
- message: docs: record promoter visualization commit hash
- files: history commit-hash backfill

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 16:26 - Add MCScanX circlize visualization smoke

Context:
- The user asked whether MCScanX + circlize visualization had been implemented.
- The repository only had MCScanX `.collinearity` parsing and aggregate synteny statistics, not a dedicated circlize/circos-style syntenic-link figure.

Decisions:
- Add a dedicated MCScanX circlize visualization path rather than overloading the feature-summary plot.
- Join MCScanX syntenic gene pairs to chromosome-location coordinates before plotting.
- Write skipped links to a separate TSV when gene coordinates are missing, so large real datasets can report annotation mismatches without failing the whole visualization step.
- Use the installed R `circlize` package through `/usr/local/bin/R`.
- Register the visualization smoke in the default release checks after the synteny parser smoke.

Added:
- `bin/genefam/build_circlize_inputs.py`
- `bin/genefam/run_mcscanx_circlize_smoke.py`
- `scripts/plot_mcscanx_circlize.R`
- `tests/test_build_circlize_inputs.py`
- `tests/test_run_mcscanx_circlize_smoke.py`

Modified:
- `README.md`
- `docs/release_audit.md`
- `bin/genefam/run_release_checks.py`
- `tests/test_run_release_checks.py`
- `tests/test_release_audit_docs.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `/usr/local/bin/R --vanilla --slave -e "cat(requireNamespace('circlize', quietly=TRUE))"` returned `TRUE`.
- `python -m pytest tests/test_build_circlize_inputs.py tests/test_run_mcscanx_circlize_smoke.py -q` first failed because `bin.genefam.build_circlize_inputs` did not exist.
- `python -m pytest tests/test_build_circlize_inputs.py tests/test_run_mcscanx_circlize_smoke.py -q` then failed because chromosome extents used only successful links instead of all provided chromosome-location rows.
- `python -m pytest tests/test_build_circlize_inputs.py tests/test_run_mcscanx_circlize_smoke.py -q` passed with 2 tests after using all chromosome-location rows.
- `python bin/genefam/run_mcscanx_circlize_smoke.py --r-bin /usr/local/bin/R --outdir results/mcscanx_circlize_smoke` wrote circlize input TSVs plus `mcscanx_circlize.pdf` and `mcscanx_circlize.png`.
- `python -m pytest tests/test_build_circlize_inputs.py tests/test_run_mcscanx_circlize_smoke.py tests/test_run_release_checks.py tests/test_release_audit_docs.py -q` passed with 41 tests.
- `python -m pytest tests -q` passed with 293 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release evidence.
- `results/release_checks/release_checks.md` reports `Passed: 31`, `Required failed: 1`, `Optional failed: 2`; `MCScanX circlize visualization smoke` passed.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: f9ebf37b7d6b6dacfb6ff63d45996c06b66757d9
- message: feat: add mcscanx circlize visualization
- files: MCScanX circlize input builder, R circlize plot, smoke runner, release checks, docs, tests, history

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 16:45 - Add Chinese README for first real species runs

Context:
- The user said the current README was hard to understand and asked for a Chinese version.
- The project now needs user-facing guidance for preparing a small real 3-species run.

Decisions:
- Keep the existing English `README.md` as the detailed engineering/release surface.
- Add `README.zh-CN.md` as a practical Chinese usage guide rather than a line-by-line translation.
- Add a Chinese README link near the top of `README.md`.
- Focus the Chinese guide on species-bank layout, YAML editing, preflight validation, 3-species first run strategy, result locations, MCScanX circlize outputs, and WGD event interpretation.

Added:
- `README.zh-CN.md`

Modified:
- `README.md`
- `HISTORY.md`

Deleted:
- none

Verification:
- `rg -n "README.zh-CN|validate_config|run_identification|MCScanX|gamma|beta|alpha|theta|3 个物种|GeneFamilyFlow" README.md README.zh-CN.md` confirmed the Chinese entry link and key usage sections.

Commit:
- hash: 6710fafe47fe60f5747d177fa3e271d6a748c562
- message: docs: add Chinese README guide
- files: Chinese README, English README link, history

Next:
- Review the Chinese guide during the first real 3-species run and adjust examples to the user's actual species names and data paths.

## 2026-06-26 19:36 - Wire standard visualization modules into Nextflow

Context:
- The user asked to continue development while away, prioritizing promoter/MCScanX/feature-summary integration into the formal Nextflow branch before deeper MCScanX/KaKs automation, report upgrades, and visualization expansion.
- Promoter extraction, feature-summary plotting, and MCScanX circlize plotting already existed as Python/R scripts and smoke checks, but were not yet wired into the standard Nextflow branch.

Decisions:
- Add optional Nextflow switches instead of forcing these modules on by default.
- Keep `run_promoter`, `run_feature_summary`, and `run_mcscanx_circlize` defaulted to `false` so existing standard runs do not require genome FASTA or synteny inputs.
- Let report index entries mark these outputs as `missing` unless the corresponding module is enabled.
- Use a normalized `syntenic_pairs.tsv` fixture for formal Nextflow visualization smoke rather than passing raw MCScanX `.collinearity` to the circlize step.

Added:
- `tests/fixtures/mcscanx/syntenic_pairs.tsv`

Modified:
- `workflows/nextflow.config`
- `workflows/main.nf`
- `workflows/modules/annotation_integration.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `bin/genefam/run_release_checks.py`
- `docs/release_audit.md`
- `README.md`
- `README.zh-CN.md`
- `tests/test_runtime_environment_files.py`
- `tests/test_workflow_modules.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_release_checks.py`
- `tests/test_release_audit_docs.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_runtime_environment_files.py::test_nextflow_config_has_container_profiles tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_workflow_modules.py::test_annotation_module_extracts_promoters_for_standard_branch tests/test_standard_branch_report_index.py -q` first failed with 7 expected failures because params, processes, workflow wiring, and report index keys were missing.
- The same targeted test group passed with 9 tests after adding optional Nextflow params, `EXTRACT_PROMOTERS`, `PLOT_FEATURE_SUMMARY`, `PLOT_MCSCANX_CIRCLIZE`, and report-index keys.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_smoke` passed, confirming default-off optional visualization modules do not break the standard branch.
- `python -m pytest tests/test_run_nextflow_standard_smoke.py::test_build_nextflow_command_can_enable_standard_visualization_modules tests/test_run_nextflow_standard_smoke.py::test_expected_published_outputs_can_include_standard_visualization_modules -q` first failed because the standard Nextflow smoke runner did not expose visualization module flags.
- The same runner tests passed after adding `--run-feature-summary`, `--run-mcscanx-circlize`, `--syntenic-pairs`, and expected visualization outputs.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_standard_feature_smoke --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv` passed and wrote feature-summary plus MCScanX circlize outputs under `results/nextflow_standard_feature_smoke/standard/`.
- `python -m pytest tests -q` passed with 297 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release evidence.
- `results/release_checks/release_checks.md` reports `Passed: 32`, `Required failed: 1`, `Optional failed: 2`; `Nextflow standard visualization smoke` passed.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: eaeee52
- message: feat: wire standard visualization modules into nextflow
- files: Nextflow standard visualization wiring, report-index optional outputs, smoke runner, release checks, docs, tests, history

Next:
- Continue with true MCScanX/KaKs endpoint automation and richer report/visualization outputs.

## 2026-06-25 - Stabilize standard Nextflow alignment and FastTree readiness

Timestamp:
- 2026-06-25 15:36:23 CST

Context:
- Full standard Nextflow smoke failed inside `RUN_ALIGNMENT` because MAFFT tried to write to `/dev/stderr` in the managed execution environment.
- The workflow now defaults to FastTree, but readiness and bootstrap checks did not yet treat FastTree as a first-class runtime command.
- Objective audit still reported the Nextflow and standard-branch requirements as missing because the standard Nextflow smokes were failing.

Decisions:
- Run MAFFT with `--quiet --auto` inside the Nextflow alignment process.
- Add `FastTree` to the default readiness command set and Conda-scoped lookup.
- Add FastTree verification to the runtime bootstrap plan and readiness checklist.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/audit_readiness.py`
- `bin/genefam/plan_runtime_bootstrap.py`
- `docs/readiness_checklist.md`
- `tests/test_audit_readiness.py`
- `tests/test_plan_runtime_bootstrap.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_workflow_modules.py`
- `workflows/modules/alignment_phylogeny.nf`

Deleted:
- none

Verification:
- `/Users/liuyue/miniforge3/envs/GeneFamilyFlow/bin/mafft --quiet --auto tests/fixtures/alignment/family_members.faa > /private/tmp/genefam_mafft_quiet_test.aln.faa` passed.
- `python -m pytest tests/test_workflow_modules.py -q` first failed because `RUN_ALIGNMENT` did not use quiet MAFFT.
- `python -m pytest tests/test_workflow_modules.py -q` passed with 17 tests after adding `mafft --quiet --auto`.
- `/Users/liuyue/miniforge3/bin/python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --outdir /private/tmp/genefam_nextflow_standard_debug2` passed and published `alignment/GDSL.mafft.aln.faa`, `phylogeny/GDSL.fasttree.treefile`, `report/report_index.tsv`, and `report/final_report.md`.
- `/Users/liuyue/miniforge3/bin/python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --config configs/manifest.example.yaml --outdir /private/tmp/genefam_nextflow_manifest_debug2` passed.
- `python -m pytest tests/test_audit_readiness.py -q` first failed because `DEFAULT_COMMANDS` did not include `FastTree`.
- `python -m pytest tests/test_audit_readiness.py -q` passed with 8 tests after adding FastTree readiness.
- `/Users/liuyue/miniforge3/bin/python bin/genefam/audit_readiness.py --command FastTree --conda-env GeneFamilyFlow --out /private/tmp/genefam_fasttree_readiness.tsv` passed and reported `FastTree` as `available_in_conda`.
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` first failed because the bootstrap plan did not verify FastTree.
- `python -m pytest tests/test_plan_runtime_bootstrap.py -q` passed with 3 tests after adding the FastTree bootstrap check.
- `python -m pytest tests/test_runtime_environment_files.py -q` first failed because the readiness checklist did not document FastTree.
- `python -m pytest tests/test_runtime_environment_files.py -q` passed with 13 tests after updating the checklist.
- `/Users/liuyue/miniforge3/bin/python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 1 with `passed=28`, `failed=3`, `required_failed=1`, and `optional_failed=2`; the only remaining required failure is the readiness audit because Docker and Apptainer are missing.
- Refreshed `results/objective_audit/objective_audit.md` now reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited 1 after refreshing release, quickstart, local acceptance, handoff, and delivery-bundle outputs; `results/handoff/handoff_report.md` reports only `Docker/Apptainer reproducibility` as blocked.

Commit:
- hash: dc2f9cd8e0258401baf19408e56487540f543e6f
- message: fix: stabilize standard nextflow phylogeny runtime
- files: alignment/phylogeny module, readiness audit, runtime bootstrap plan, readiness checklist, tests, history

Next:
- Continue toward the final container-runtime verification.

## 2026-06-25 - Add real alignment and tree outputs to the standard report index

Timestamp:
- 2026-06-25 15:18:14 CST

Context:
- The standard Nextflow branch now publishes real MAFFT alignment and FastTree/IQ-TREE output files.
- The final standard report still indexed only `alignment_manifest` and `phylogeny_manifest`, so users had to infer where the real alignment and tree files were.

Decisions:
- Add `alignment_file` and `phylogeny_tree` to the standard report index.
- Pass `RUN_ALIGNMENT.out` and `RUN_PHYLOGENY.out` into `BUILD_STANDARD_REPORT_INDEX`.
- Keep manifest rows in the report index because they document preparation parameters and planned output paths.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/build_standard_report_index.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_standard_branch_report_index.py -q` first failed because `alignment_file` and `phylogeny_tree` were missing from the report index and CLI.
- `python -m pytest tests/test_standard_branch_report_index.py -q` passed with 4 tests after adding the new report index keys.
- `python -m pytest tests/test_workflow_modules.py -q` passed with 17 tests after wiring the real alignment/tree outputs into `BUILD_STANDARD_REPORT_INDEX`.
- `python -m pytest tests/test_standard_branch_report_index.py tests/test_workflow_modules.py tests/test_release_audit_docs.py -q` passed with 22 tests.
- `python -m pytest tests/test_run_nextflow_standard_smoke.py -q` passed with 9 tests.
- `python -m pytest tests -q` passed with 280 tests in 25.85 seconds; pytest emitted a non-fatal temporary-directory cleanup warning.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited 1 after refreshing release, quickstart, local acceptance, and delivery-bundle outputs; the release gate remains blocked by external runtime readiness, with details in `results/handoff/handoff_report.md`.

Commit:
- hash: a710df741ec7faf022b45e7ce1792556ffbf6c07
- message: feat: index standard alignment and tree outputs
- files: standard report index, standard postprocess module, main workflow, README, release audit docs, tests, history

Next:
- Continue hardening final report evidence before final container packaging.

## 2026-06-25 - Wire real standard-branch alignment and phylogeny execution

Timestamp:
- 2026-06-25 15:07:11 CST

Context:
- The standard Nextflow branch prepared alignment and phylogeny manifests, but it did not call `RUN_ALIGNMENT` or `RUN_PHYLOGENY`.
- `RUN_ALIGNMENT` and `RUN_PHYLOGENY` also emitted generic filenames, which did not match the report-ready manifest paths.
- Large multi-species runs should use FastTree by default while keeping IQ-TREE available as an explicit slower option.

Decisions:
- Wire `RUN_ALIGNMENT` and `RUN_PHYLOGENY` into the non-truncated standard identification branch.
- Publish real alignment and tree outputs with manifest-compatible names: `GDSL.mafft.aln.faa` and `GDSL.fasttree.treefile` by default.
- Change the Nextflow default tree builder to `fasttree`; users can still pass `--tree_builder iqtree`.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/alignment_phylogeny.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py -q` first failed because the standard branch did not call `RUN_ALIGNMENT` or `RUN_PHYLOGENY`, and alignment/tree outputs were generic filenames.
- `python -m pytest tests/test_run_nextflow_standard_smoke.py -q` first failed because full standard-smoke expected outputs did not include real alignment/tree files.
- `python -m pytest tests/test_runtime_environment_files.py -q` first failed because `workflows/nextflow.config` still defaulted to `params.tree_builder = "iqtree"`.
- `python -m pytest tests/test_workflow_modules.py -q` passed with 17 tests after wiring real execution and manifest-compatible output names.
- `python -m pytest tests/test_run_nextflow_standard_smoke.py -q` passed with 9 tests after adding expected published alignment/tree outputs.
- `python -m pytest tests/test_runtime_environment_files.py -q` passed with 13 tests after switching the Nextflow default tree builder to FastTree.
- `python -m pytest tests/test_release_audit_docs.py -q` passed with 1 test after documenting real alignment/phylogeny execution.
- `python -m pytest tests -q` passed with 280 tests in 79.39 seconds.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited 1 after refreshing release, quickstart, local acceptance, and delivery-bundle outputs; the release gate remains blocked by external runtime readiness, with details in `results/handoff/handoff_report.md`.

Commit:
- hash: 9d419afa5a514f28b44807192f74254a9f563366
- message: feat: run standard alignment and phylogeny
- files: standard Nextflow workflow, alignment/phylogeny module, Nextflow config, standard-smoke expected outputs, README, release audit docs, tests, history

Next:
- Continue closing release-gate gaps before final container packaging.

## 2026-06-25 - Add FastTree phylogeny branch for large multi-species runs

Timestamp:
- 2026-06-25 14:55:44 CST

Context:
- Large multi-species gene-family phylogenies can be too slow if every run depends on IQ-TREE model selection and bootstrap settings.
- The alignment and phylogeny manifest layer already accepted `tree_builder = fasttree`, and the GeneFamilyFlow environment files already included `fasttree`.
- The actual Nextflow `RUN_PHYLOGENY` process still hard-coded IQ-TREE, so selecting FastTree was not executable at the workflow-module level.

Decisions:
- Add a FastTree branch to `RUN_PHYLOGENY` using `FastTree`/`fasttree` and WAG protein distances.
- Keep the IQ-TREE branch available for slower model-selection/bootstrap analyses.
- Document `--tree-builder fasttree` as the recommended fast path for large multi-species family trees.

Added:
- none

Modified:
- `HISTORY.md`
- `README.md`
- `docs/release_audit.md`
- `tests/test_release_audit_docs.py`
- `tests/test_workflow_modules.py`
- `workflows/modules/alignment_phylogeny.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py -q` first failed because `RUN_PHYLOGENY` had no FastTree branch.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because the release audit did not mention FastTree or `--tree-builder fasttree`.
- `python -m pytest tests/test_workflow_modules.py -q` passed with 17 tests after adding the FastTree branch.
- `python -m pytest tests/test_release_audit_docs.py -q` passed with 1 test after documenting FastTree.
- `python -m pytest tests -q` passed with 280 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited 1 after refreshing release, quickstart, local acceptance, and delivery-bundle outputs; the release gate remains blocked by external runtime readiness, with details in `results/handoff/handoff_report.md`.

Commit:
- hash: 9441ffb38f96556e58a1378a5518c4b777af703a
- message: feat: add fasttree phylogeny branch
- files: alignment/phylogeny Nextflow module, README, release audit docs, workflow module test, release audit test, history

Next:
- Continue wiring larger standard-analysis execution paths before final container packaging.

## 2026-06-25 - Reject WGD event labels without metadata

Timestamp:
- 2026-06-25 14:44:48 CST

Context:
- WGD event metadata fields are now required, but a classified layer table could still contain a misspelled event label such as `alhpa`.
- `build_wgd_event_evidence.py` treated unknown labels as inferred layers, which could hide typos in gamma/beta/alpha/theta event mappings.

Decisions:
- Reject named WGD event labels when no matching event metadata exists.
- Keep `unannotated` and `mixed` layers valid because they are observational/inferred states rather than configured event labels.
- Document that configured WGD event labels must have matching metadata.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_wgd_event_evidence.py`
- `docs/wgd_event_evidence.md`
- `docs/release_audit.md`
- `tests/test_build_wgd_event_evidence.py`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_event_evidence.py -q` first failed because a misspelled `alhpa` event label was accepted without matching metadata.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because the release audit did not document the matching-metadata rule.
- `python -m pytest tests/test_build_wgd_event_evidence.py tests/test_release_audit_docs.py -q` passed with 7 tests after adding the validation and documentation.
- `python -m pytest tests -q` passed with 280 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited 1 after refreshing release, quickstart, local acceptance, and delivery-bundle outputs; the release gate remains blocked by external runtime readiness, with details in `results/handoff/handoff_report.md`.

Commit:
- hash: 132b34b1958e87ae35080330d20a7521b1be15f1
- message: fix: reject wgd event labels without metadata
- files: WGD event evidence loader, WGD event docs, release audit docs, WGD event tests, history

Next:
- Add FastTree support for large multi-species phylogeny construction before the final container packaging stage.

## 2026-06-25 - Index primary YAML entrypoints in delivery bundle

Timestamp:
- 2026-06-25 13:34:04 CST

Context:
- The delivery bundle already indexed manifest-mode input, reports, WGD evidence, Reference governance, runtime status, and recovery commands.
- The final user-facing index did not directly list the primary species-bank config or the named WGD event config, even though those are the files a user edits first for selected species and gamma/beta/alpha/theta event mapping.

Decisions:
- Add `configs/example.config.yaml` as the species-bank YAML entrypoint with selected species.
- Add `configs/wgd_events.brassicaceae.yaml` as the gamma/beta/alpha/theta named-event YAML mapping.
- Keep the change in the delivery bundle generator so regenerated handoff artifacts stay aligned.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Generated/refreshed but not staged:
- `results/delivery_bundle/delivery_manifest.tsv`
- `results/delivery_bundle/delivery_bundle.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `species_bank_config` and `events_config` were missing from the generated delivery manifest.
- `python -m pytest tests/test_run_delivery_bundle.py -q` passed with 1 test after adding the two primary YAML entrypoints.
- `python bin/genefam/run_delivery_bundle.py --outdir results/delivery_bundle` refreshed the generated delivery manifest and Markdown bundle.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release, handoff, quickstart, local acceptance, and delivery-bundle evidence.
- `rg -n 'species_bank_config|events_config|configs/example.config.yaml|configs/wgd_events.brassicaceae.yaml|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:' results/delivery_bundle/delivery_manifest.tsv results/delivery_bundle/delivery_bundle.md results/release_checks/release_checks.md results/objective_audit/objective_audit.md results/local_acceptance/local_acceptance_summary.md` confirmed the final delivery index exposes both primary YAML entrypoints.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: c4c5b1c4782627fb744d9ff39edc5d5da1b96c3b
- message: feat: index primary yaml entrypoints in delivery bundle
- files: delivery bundle generator, delivery bundle test, history

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Document primary YAML entrypoints in quickstart

Timestamp:
- 2026-06-25 13:42:14 CST

Context:
- The final delivery bundle now indexes the primary species-bank YAML config and the WGD named-event YAML config.
- `docs/quickstart.md` still listed many output artifacts but did not explicitly call out which YAML files the user edits first for target species and gamma/beta/alpha/theta event mapping.

Decisions:
- Add a `Primary YAML Entrypoints` section to the quickstart.
- Document `configs/example.config.yaml` as the primary species-bank YAML entrypoint.
- Document `configs/wgd_events.brassicaceae.yaml` as the primary WGD event YAML entrypoint.
- Keep `configs/manifest.example.yaml` as the manifest-mode alternative.

Added:
- none

Modified:
- `HISTORY.md`
- `docs/quickstart.md`
- `tests/test_quickstart_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_quickstart_docs.py -q` first failed because the quickstart did not include `primary species-bank YAML entrypoint`.
- `python -m pytest tests/test_quickstart_docs.py -q` passed with 2 tests after adding the primary YAML entrypoint section.
- `python -m pytest tests -q` passed with 274 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release, handoff, quickstart, local acceptance, and delivery-bundle evidence.
- `grep -n -E 'Primary YAML Entrypoints|primary species-bank YAML entrypoint|primary WGD event YAML entrypoint|configs/example.config.yaml|configs/wgd_events.brassicaceae.yaml|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:' docs/quickstart.md results/release_checks/release_checks.md results/objective_audit/objective_audit.md results/local_acceptance/local_acceptance_summary.md` confirmed the quickstart and release evidence expose both primary YAML entrypoints.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 8430514116ac5ad212adf448b6312dfcfc3b065a
- message: docs: document primary yaml entrypoints in quickstart
- files: quickstart docs, quickstart docs test, history

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Reject duplicate WGD event names

Timestamp:
- 2026-06-25 13:52:22 CST

Context:
- `configs/wgd_events.brassicaceae.yaml` is the primary configuration for mapping anonymous WGD layers to gamma, beta, alpha, theta, or custom event labels.
- The event metadata loader accepted duplicate event names, which could silently overwrite a biological event label's scope or expected age.

Decisions:
- Reject duplicate WGD event names in `load_event_metadata`.
- Document the uniqueness rule in the WGD event evidence model and release audit.
- Keep the validation focused on duplicate names in this step.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_wgd_event_evidence.py`
- `docs/wgd_event_evidence.md`
- `docs/release_audit.md`
- `tests/test_build_wgd_event_evidence.py`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_event_evidence.py -q` first failed because duplicate `alpha` WGD events were accepted without error.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because the release audit did not document that WGD event names must be unique.
- `python -m pytest tests/test_build_wgd_event_evidence.py tests/test_release_audit_docs.py -q` passed with 5 tests after adding duplicate-name validation and documentation.
- `python -m pytest tests -q` passed with 275 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release, handoff, quickstart, local acceptance, and delivery-bundle evidence.
- `grep -n -E 'WGD event names must be unique|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:|release_gate|quickstart_handoff|delivery_bundle' docs/wgd_event_evidence.md docs/release_audit.md results/release_checks/release_checks.md results/objective_audit/objective_audit.md results/local_acceptance/local_acceptance_summary.md` confirmed the uniqueness rule and current release evidence.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 6d1b22c157151fa6211acb52d8d5921d5aba22cd
- message: fix: reject duplicate wgd event names
- files: WGD event evidence loader, WGD event docs, release audit docs, WGD event tests, history

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Validate named WGD event maps during config preflight

Timestamp:
- 2026-06-25 14:08:49 CST

Context:
- The WGD event metadata loader now rejects duplicate event names.
- The main YAML preflight still did not require `wgd_events.event_map` when named event annotation was enabled, and strict `--check-paths` did not validate the event-map YAML before a run.

Decisions:
- Require `wgd_events.event_map` when `wgd_events.named_event_annotation: true`.
- In strict `--check-paths` mode, require the event-map path to exist and validate it with `load_event_metadata`.
- Document this preflight behavior in `docs/input_contract.md` and `schemas/config.schema.yaml`.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `schemas/config.schema.yaml`
- `tests/test_validate_config.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_named_wgd_events_without_event_map tests/test_validate_config.py::test_validate_config_check_paths_rejects_duplicate_wgd_event_names -q` first failed because `validate_config` did not check `wgd_events.event_map`.
- `python -m pytest tests/test_runtime_environment_files.py::test_input_contract_and_schema_document_identification_tool_flags -q` first failed because the input contract and schema did not document `wgd_events.event_map` or duplicate WGD event names.
- `python -m pytest tests/test_validate_config.py tests/test_runtime_environment_files.py::test_input_contract_and_schema_document_identification_tool_flags -q` passed with 24 tests after adding preflight validation and documentation.
- `python -m pytest tests -q` passed with 277 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release, handoff, quickstart, local acceptance, and delivery-bundle evidence.
- `grep -n -E 'wgd_events.event_map|duplicate WGD event names|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:|release_gate|quickstart_handoff|delivery_bundle' docs/input_contract.md schemas/config.schema.yaml results/release_checks/release_checks.md results/objective_audit/objective_audit.md results/local_acceptance/local_acceptance_summary.md` confirmed the event-map preflight documentation and current release evidence.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 685b9cd3c21db2e57301a1bd775cd2db3016c9f1
- message: feat: validate named wgd event maps in config preflight
- files: config validator, input contract, config schema, validator tests, runtime docs tests, history

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-25 - Require duplication-retention module for named WGD events

Timestamp:
- 2026-06-25 14:20:49 CST

Context:
- `wgd_events.named_event_annotation` now requires an event-map YAML and validates it in strict preflight mode.
- The config validator still allowed named WGD event annotation while `modules.duplication_retention` was disabled, which would make gamma/beta/alpha/theta interpretation unreachable in the configured workflow.

Decisions:
- Require `modules.duplication_retention: true` when `wgd_events.named_event_annotation: true`.
- Document the dependency in the input contract and schema.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/validate_config.py`
- `docs/input_contract.md`
- `schemas/config.schema.yaml`
- `tests/test_validate_config.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_validate_config.py::test_validate_config_reports_named_wgd_events_without_duplication_retention_module -q` first failed because named WGD event annotation did not require `modules.duplication_retention`.
- `python -m pytest tests/test_runtime_environment_files.py::test_input_contract_and_schema_document_identification_tool_flags -q` first failed because the dependency was not documented in both the input contract and schema.
- `python -m pytest tests/test_validate_config.py tests/test_runtime_environment_files.py::test_input_contract_and_schema_document_identification_tool_flags -q` passed with 25 tests after adding the dependency and documentation.
- `python -m pytest tests -q` passed with 278 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release, handoff, quickstart, local acceptance, and delivery-bundle evidence.
- `grep -n -E 'wgd_events.named_event_annotation requires modules.duplication_retention|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:|release_gate|quickstart_handoff|delivery_bundle' docs/input_contract.md schemas/config.schema.yaml results/release_checks/release_checks.md results/objective_audit/objective_audit.md results/local_acceptance/local_acceptance_summary.md` confirmed the dependency documentation and current release evidence.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: e5e6b664bcb3035d913563f56a41f74ebb67de75
- message: feat: require duplication retention for named wgd events
- files: config validator, input contract, config schema, validator tests, runtime docs tests, history

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-27 - Add pangenome-class Ka/Ks comparison plots

Timestamp:
- 2026-06-27 01:49:54 CST

Context:
- The WGD branch already supported Ks distributions, named WGD event labels, and duplicate-type grouped Ka/Ks plots.
- The large-scale ASMT/COMT-style reference also compares gene retention and Ks patterns across core/dispensable pangenome classes, which needed a formal table and plot path.

Decisions:
- Add a gene-level `pangenome_classes` input for WGD/evolution runs, with at least `gene_id` and `pangenome_class` columns.
- Build pairwise `pangenome_kaks` tables by joining both genes in each Ka/Ks pair to their pangenome class.
- Treat same-class pairs as their class and mixed-class pairs as `mixed`; skipped pairs are recorded when either gene lacks pangenome-class evidence.
- Wire the plot into the WGD branch and release checks while keeping `pangenome_classes` optional for user runs.

Added:
- `bin/genefam/build_pangenome_kaks.py`
- `bin/genefam/run_pangenome_kaks_smoke.py`
- `scripts/plot_pangenome_kaks.R`
- `PLOT_PANGENOME_KAKS` and `EMPTY_PANGENOME_KAKS` Nextflow processes.
- `params.pangenome_classes` in `workflows/nextflow.config`.
- WGD report-index keys for `pangenome_kaks`, `pangenome_kaks_summary`, `pangenome_kaks_skipped`, `pangenome_kaks_pdf`, and `pangenome_kaks_png`.
- Release-check smoke for pangenome-class Ka/Ks visualization.
- Tests covering builder behavior, R smoke, Nextflow WGD command wiring, WGD report index, release checks, Reference reuse, and release audit docs.

Modified:
- `HISTORY.md`
- `bin/genefam/build_wgd_report_index.py`
- `bin/genefam/run_nextflow_wgd_smoke.py`
- `bin/genefam/run_release_checks.py`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_nextflow_wgd_smoke.py`
- `tests/test_run_release_checks.py`
- `tests/test_wgd_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/duplication_retention.nf`
- `workflows/nextflow.config`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_pangenome_kaks.py tests/test_run_pangenome_kaks_smoke.py tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes tests/test_wgd_report_index.py tests/test_run_release_checks.py::test_default_checks_include_pangenome_kaks_visualization_smoke tests/test_reference_plotting_reuse.py tests/test_release_audit_docs.py -q` first failed because the smoke runner, Nextflow process, WGD report keys, release check, and documentation were not implemented.
- `python -m pytest tests/test_run_nextflow_wgd_smoke.py::test_build_nextflow_wgd_command_targets_duplication_retention_branch tests/test_run_nextflow_wgd_smoke.py::test_expected_published_outputs_cover_wgd_results -q` first failed because the Nextflow WGD smoke command did not yet accept `pangenome_classes` and expected outputs did not include pangenome Ka/Ks artifacts.
- `python -m pytest tests/test_build_pangenome_kaks.py tests/test_run_pangenome_kaks_smoke.py tests/test_run_nextflow_wgd_smoke.py tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes tests/test_wgd_report_index.py tests/test_run_release_checks.py::test_default_checks_include_pangenome_kaks_visualization_smoke tests/test_reference_plotting_reuse.py tests/test_release_audit_docs.py -q` passed with 15 tests after implementation.
- `python bin/genefam/run_pangenome_kaks_smoke.py --r-bin /usr/local/bin/R --outdir results/pangenome_kaks_smoke` passed and produced `pangenome_kaks.tsv`, `pangenome_kaks_summary.tsv`, `pangenome_kaks_skipped.tsv`, `pangenome_kaks.pdf`, and `pangenome_kaks.png`.
- `cat results/pangenome_kaks_smoke/tables/pangenome_kaks_summary.tsv` confirmed grouped core, dispensable, and mixed pair summaries with median Ks and mean Ka/Ks.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke` passed and produced real WGD-branch `pangenome_kaks` tables and plots.
- `rg -n "pangenome_kaks" results/nextflow_wgd_smoke/wgd/report/report_index.tsv results/nextflow_wgd_smoke/wgd/report/final_report.md` confirmed the WGD report package indexes the pangenome-class Ka/Ks outputs.
- `python -m pytest tests -q` passed with 348 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`: pangenome-class Ka/Ks visualization smoke and Nextflow WGD smoke passed; `readiness audit` and Docker/Apptainer profile smokes remained the known final-stage runtime/container blockers.

Commit:
- hash: 76fab4f5133bf158ce0dea9cd31060c08d20cf0e
- message: feat: add pangenome class kaks plots
- files: pangenome Ka/Ks builder, smoke runner, R plotting script, Nextflow WGD wiring, WGD report index, release checks, Reference/release docs, tests, history

Next:
- Continue final MVP hardening around report interpretation depth, objective audit coverage, and eventual Docker/Apptainer packaging.

## 2026-06-27 - Add gene family pangenome presence summary

Timestamp:
- 2026-06-27 01:34:01 CST

Context:
- The gene family information plot already covered copy-number class, species ordering, expansion/contracted status, and protein properties.
- Large-scale copy-number papers also emphasize pan/core/dispensable presence patterns and copy-number dosage balance, which were not yet represented as a formal result table or report interpretation entry.

Decisions:
- Add a `gene_family_pangenome_summary.tsv` table derived from per-species family counts.
- Classify family presence breadth as `core`, `soft_core`, `dispensable`, or `absent` using transparent presence-fraction thresholds.
- Reuse the existing gene family information PDF/PNG, but add a dedicated plot-manifest and final-report interpretation entry for pangenome/copy-number balance.

Added:
- `tables/gene_family_pangenome_summary.tsv` output from `build_gene_family_info.py`, the gene family info smoke, and `PLOT_GENE_FAMILY_INFO`.
- A pangenome presence panel in `scripts/plot_gene_family_info.R`.
- `gene_family_pangenome_summary` entries in the standard report index, plot manifest, final report, and figure interpretation templates.
- Tests covering pangenome summary classification, R smoke output, Nextflow output ordering, report index wiring, Reference plotting reuse, and release audit documentation.

Modified:
- `HISTORY.md`
- `bin/genefam/build_figure_interpretations.py`
- `bin/genefam/build_gene_family_info.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_gene_family_info_smoke.py`
- `docs/reference_plotting_reuse.md`
- `docs/release_audit.md`
- `scripts/plot_gene_family_info.R`
- `tests/test_build_figure_interpretations.py`
- `tests/test_build_gene_family_info.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_gene_family_info_smoke.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_gene_family_info.py tests/test_run_gene_family_info_smoke.py tests/test_build_figure_interpretations.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_includes_plot_processes tests/test_standard_branch_report_index.py -q` first failed with 11 failures because the pangenome summary table, plot input, report-index key, and figure interpretation template did not exist yet.
- `python -m pytest tests/test_build_gene_family_info.py tests/test_run_gene_family_info_smoke.py tests/test_build_figure_interpretations.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_includes_plot_processes tests/test_standard_branch_report_index.py tests/test_reference_plotting_reuse.py tests/test_release_audit_docs.py -q` passed with 13 tests after implementation and documentation updates.
- `python bin/genefam/run_gene_family_info_smoke.py --r-bin /usr/local/bin/R --outdir results/gene_family_info_smoke` passed and produced `gene_family_pangenome_summary.tsv`, `gene_family_info_summary.pdf`, and `gene_family_info_summary.png`.
- `cat results/gene_family_info_smoke/tables/gene_family_pangenome_summary.tsv` confirmed the smoke example had `total_species=4`, `present_species=3`, `presence_fraction=0.7500`, and `pangenome_presence_class=dispensable`.
- `python -m pytest tests -q` passed with 344 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`: gene family information smoke, Nextflow standard branch, and related workflow checks passed; `readiness audit` and Docker/Apptainer profile smokes remained the known final-stage runtime/container blockers.
- `cat results/nextflow_standard_smoke/standard/tables/gene_family_pangenome_summary.tsv` confirmed the Nextflow standard branch publishes the pangenome summary table.
- `rg -n "gene_family_pangenome_summary" results/nextflow_standard_smoke/standard/report/report_index.tsv results/nextflow_standard_smoke/standard/report/figure_interpretations.tsv results/nextflow_standard_smoke/standard/report/final_report.md` confirmed the new table and figure interpretation are present in the report package.

Commit:
- hash: 1a7d82315fd2bad600db6ac10495808aef86a7b5
- message: feat: add gene family pangenome summary
- files: gene family info builder, plotting script, smoke runner, Nextflow wiring, report index, figure interpretations, Reference/release docs, tests, history

Next:
- Continue the paper-level MVP polish with combined Ks-by-pangenome-class comparison plots when accession-level core/dispensable input tables are available.

## 2026-06-27 - Add PPI input evidence and network QC outputs

Timestamp:
- 2026-06-27 01:23:06 CST

Context:
- The PPI branch already used ggNetView for network visualization, but the final report package still lacked explicit evidence for how user-provided PPI edge tables were cleaned.
- For paper-level review, PPI results need both a visual network and auditable statistics about edge normalization, skipped rows, annotation coverage, and network size.

Decisions:
- Keep the upstream PPI source as a user-provided edge table while making the boundary explicit and auditable.
- Add two formal PPI result tables: `ppi_input_evidence.tsv` for edge-cleaning provenance and `ppi_network_qc.tsv` for network-level QC metrics.
- Wire both tables through the formal Nextflow PPI process and standard report index.

Added:
- `tables/ppi_input_evidence.tsv` output from the PPI table builder, ggNetView smoke, and `PLOT_PPI_GGNETVIEW`.
- `tables/ppi_network_qc.tsv` output from the PPI table builder, ggNetView smoke, and `PLOT_PPI_GGNETVIEW`.
- Tests asserting PPI input evidence, network QC metrics, Nextflow output ordering, report-index keys, and Reference plotting reuse status.

Modified:
- `HISTORY.md`
- `bin/genefam/build_ppi_tables.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/run_ppi_ggnetview_plot_smoke.py`
- `docs/reference_plotting_reuse.md`
- `tests/test_build_ppi_tables.py`
- `tests/test_reference_plotting_reuse.py`
- `tests/test_run_ppi_ggnetview_plot_smoke.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/plots.nf`
- `workflows/modules/standard_postprocess.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_ppi_tables.py tests/test_run_ppi_ggnetview_plot_smoke.py tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_workflow_modules.py::test_standard_postprocess_module_extracts_family_sequences_and_report_index tests/test_workflow_modules.py::test_main_workflow_wires_standard_identification_branch tests/test_workflow_modules.py::test_main_workflow_includes_plot_processes tests/test_standard_branch_report_index.py tests/test_reference_plotting_reuse.py -q` first failed with 7 failures because the new PPI evidence/QC outputs did not exist yet.
- The same focused pytest command passed with 12 tests after implementation.
- `python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke` passed and produced PPI edges, nodes, hubs, input evidence, network QC, status, PDF, PNG, and summary outputs.
- `python -m pytest tests -q` passed with 343 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited `1`: required workflow and visualization checks passed through PPI and Nextflow standard branches, while `readiness audit` remained failed and Docker/Apptainer profile smokes remained failed as the known final-stage container/runtime blocker.

Commit:
- hash: ff7595b6df554f8f6a1a568cc59d47922d71349f
- message: feat: add ppi evidence and qc outputs
- files: PPI table builder, PPI ggNetView smoke, Nextflow PPI wiring, standard report index, Reference plotting reuse matrix, tests, history

Next:
- Continue the paper-level MVP polish with the remaining large-scale copy-number/pangenome/Ks visualization and final report interpretation depth.

## 2026-06-25 - Require complete WGD event metadata fields

Timestamp:
- 2026-06-25 14:31:50 CST

Context:
- WGD event names were unique, but event metadata entries could still omit fields such as `scope`.
- Missing metadata fields would make gamma/beta/alpha/theta interpretation tables look configured while leaving report columns blank.

Decisions:
- Require every configured WGD event to provide `name`, `scope`, `evidence`, and `expected_relative_age`.
- Document the required metadata fields in the WGD event evidence model and release audit.

Added:
- none

Modified:
- `HISTORY.md`
- `bin/genefam/build_wgd_event_evidence.py`
- `docs/wgd_event_evidence.md`
- `docs/release_audit.md`
- `tests/test_build_wgd_event_evidence.py`
- `tests/test_release_audit_docs.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_wgd_event_evidence.py -q` first failed because an `alpha` event without `scope` was accepted.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because the release audit did not document the required WGD event metadata fields.
- `python -m pytest tests/test_build_wgd_event_evidence.py tests/test_release_audit_docs.py -q` passed with 6 tests after adding required-field validation and documentation.
- `python -m pytest tests -q` passed with 279 tests.
- `PYTHON_BIN=/Users/liuyue/miniforge3/bin/python CONDA_ENV=GeneFamilyFlow bash scripts/run_local_acceptance.sh` exited `1`, as expected while Docker/Apptainer remain unavailable, after refreshing release, handoff, quickstart, local acceptance, and delivery-bundle evidence.
- `grep -n -E 'WGD event metadata requires name, scope, evidence, and expected_relative_age|Passed:|Required failed:|Optional failed:|Achieved:|Blocked:|Missing:|release_gate|quickstart_handoff|delivery_bundle' docs/wgd_event_evidence.md docs/release_audit.md results/release_checks/release_checks.md results/objective_audit/objective_audit.md results/local_acceptance/local_acceptance_summary.md` confirmed the required metadata fields and current release evidence.
- `results/release_checks/release_checks.md` still reports `Passed: 28`, `Required failed: 1`, `Optional failed: 2`.
- `results/objective_audit/objective_audit.md` still reports `Achieved: 11`, `Blocked: 1`, `Missing: 0`.

Commit:
- hash: 5cd7f293b2ff6796a98bea2248d4fc862f7a40ea
- message: fix: require complete wgd event metadata
- files: WGD event evidence loader, WGD event docs, release audit docs, WGD event tests, history

Next:
- Continue the final delivery polish while Docker/Apptainer remains the external runtime blocker.

## 2026-06-27 - Audit publication plot files and dynamic manifest

Timestamp:
- 2026-06-27 03:54 CST

Context:
- The publication report audit verified interpretation coverage and software/version sections, but it did not prove that every plot registered in `plot_manifest.tsv` existed on disk.
- The standard plot manifest listed optional plots such as promoter, PPI, expression, and Ks outputs even when those branches were not enabled or were owned by a different branch.

Decisions:
- Treat registered plot files as part of the publication-level contract: every manifest path must exist and be non-empty.
- Generate the standard branch plot manifest from active Nextflow parameters so optional figures are only registered when their branches run.
- Keep `ks_distribution` out of the standard plot manifest because WGD/Ks reporting owns that output.

Added:
- `plot_files_exist` check in `bin/genefam/audit_publication_report.py`.
- Regression coverage for missing, empty, and valid plot files in `tests/test_audit_publication_report.py`.
- Nextflow module test coverage proving standard plot manifest entries are parameter-aware.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_publication_report.py`
- `tests/test_audit_publication_report.py`
- `tests/test_workflow_modules.py`
- `workflows/modules/plots.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_publication_report.py -q` first failed because the audit only reported four checks and had no plot-file existence check.
- `python -m pytest tests/test_audit_publication_report.py -q` passed with 4 tests after adding file checks.
- A manual publication audit against `results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv` first failed because optional static manifest rows pointed to missing promoter, PPI, Ks, and expression plots.
- `python -m pytest tests/test_workflow_modules.py::test_plot_module_runs_r_scripts_through_configured_r_bin tests/test_workflow_modules.py::test_main_workflow_includes_plot_processes tests/test_audit_publication_report.py -q` passed with 6 tests after making the manifest dynamic.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --outdir results/nextflow_standard_feature_smoke` passed.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` passed with `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests -q` passed with 363 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` passed required checks and reported `Release ready: true`, with only optional Docker and Apptainer profile smokes failing because those runtimes are not installed.

Commit:
- hash: e970d5b46db5aedcc713a974aafe6cef9e212beb
- message: feat: audit publication plot files
- files: publication report audit, plot manifest module, audit/workflow tests, history

Next:
- Continue final container/runtime verification when Docker or Apptainer is available; the non-container MVP checks are release-ready.

## 2026-06-27 - Run full publication visualization smoke through release gate

Timestamp:
- 2026-06-27 04:05 CST

Context:
- The publication report audit checked the standard visualization report, but the release-gated Nextflow smoke only enabled feature summary and MCScanX/circlize.
- Promoter cis-element, PPI ggNetView, and expression heatmap were tested by separate smokes but were not proven to enter the same standard final report and per-figure interpretation package.
- Re-running the complete publication smoke exposed an input-safety issue: an expression input named `family_expression.tsv` could be overwritten by a Nextflow process output of the same name.

Decisions:
- Upgrade `run_nextflow_standard_smoke.py` so it can enable promoter cis-element, PPI ggNetView, and expression heatmap modules in addition to feature summary and MCScanX/circlize.
- Upgrade the required release check named `Nextflow standard visualization smoke` to run the full publication visualization set before `publication report audit`.
- Stage the expression matrix input as `input_expression_matrix.tsv` inside the Nextflow work directory so the output `family_expression.tsv` cannot overwrite a source input or fixture.

Added:
- CLI flags in `bin/genefam/run_nextflow_standard_smoke.py` for `--run-promoter-cis`, `--promoter-cis-elements`, `--run-ppi`, `--ppi-edges`, `--ppi-nodes`, `--expression-matrix`, and `--expression-metadata`.
- Expected-output checks for promoter cis-element tables/plots, PPI evidence/QC/ggNetView plots, and expression summary/heatmap outputs.
- Regression test requiring safe staged naming for the expression matrix input in `SUBSET_EXPRESSION_MATRIX`.

Modified:
- `HISTORY.md`
- `bin/genefam/run_nextflow_standard_smoke.py`
- `bin/genefam/run_release_checks.py`
- `tests/test_run_nextflow_standard_smoke.py`
- `tests/test_run_release_checks.py`
- `tests/test_workflow_modules.py`
- `workflows/modules/annotation_integration.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_nextflow_standard_smoke.py::test_build_nextflow_command_can_enable_full_publication_visualization_modules tests/test_run_nextflow_standard_smoke.py::test_expected_published_outputs_can_include_full_publication_visualization_modules -q` first failed because the standard smoke wrapper did not accept promoter/PPI/expression publication-module arguments.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_nextflow_standard_visualization_smoke_before_wgd -q` first failed because the release check did not pass promoter/PPI/expression arguments to the standard visualization smoke.
- `python -m pytest tests/test_workflow_modules.py::test_annotation_integration_module_covers_chromosome_and_expression_steps -q` first failed because the expression matrix input was not staged under a safe non-output name.
- `python -m pytest tests/test_workflow_modules.py::test_annotation_integration_module_covers_chromosome_and_expression_steps tests/test_run_nextflow_standard_smoke.py tests/test_run_release_checks.py::test_default_checks_include_nextflow_standard_visualization_smoke_before_wgd -q` passed with 18 tests after implementation.
- `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --run-promoter-cis --promoter-cis-elements tests/fixtures/promoter_cis/plantcare.tsv --run-ppi --ppi-edges tests/fixtures/ppi/ppi_edges.tsv --ppi-nodes tests/fixtures/ppi/ppi_nodes.tsv --expression-matrix tests/fixtures/expression/family_expression.tsv --expression-metadata tests/fixtures/expression/sample_metadata.tsv --outdir results/nextflow_standard_feature_smoke` passed and left `tests/fixtures/expression/family_expression.tsv` unchanged.
- The refreshed `plot_manifest.tsv` registered 9 final-report figures: family counts, gene-family information, pangenome summary, tree features, feature summary, MCScanX/circlize, promoter cis-elements, PPI ggNetView, and expression heatmap.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md` passed with `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests -q` passed with 365 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 44`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.

Commit:
- hash: 887791802f51cf3d084c414a0c2f9eb4854ec398
- message: feat: gate full publication visualization smoke
- files: standard smoke wrapper, release checks, annotation integration module, tests, history

Next:
- Keep the goal active for final Docker/Apptainer runtime verification and any additional Reference-level visual polish.

## 2026-06-27 - Add WGD publication report closure

Timestamp:
- 2026-06-27 04:14 CST

Context:
- The standard branch had a publication report closure with `plot_manifest.tsv`, software/R package versions, figure interpretations, and a release-gated publication audit.
- The WGD/evolution branch generated Ka/Ks, duplicate-type Ka/Ks, pangenome-class Ka/Ks, WGD event evidence, and a final report, but it did not yet have the same plot-manifest and per-figure interpretation closure.

Decisions:
- Give the WGD branch its own report closure: WGD plot manifest, WGD software version table, WGD figure interpretations, and final report embedding.
- Register `ks_distribution`, `duplicate_type_kaks`, and `pangenome_kaks` as WGD report figures because these are the key Ka/Ks/WGD visual outputs tied to gamma, beta, alpha, theta interpretation.
- Add a required `WGD publication report audit` release check so WGD/evolution report quality is verified independently from the standard branch report.

Added:
- `BUILD_WGD_PLOT_MANIFEST`, `COLLECT_WGD_SOFTWARE_VERSIONS`, and `BUILD_WGD_FIGURE_INTERPRETATIONS` processes in `workflows/modules/duplication_retention.nf`.
- WGD plot manifest, software version, and figure interpretation outputs to `run_nextflow_wgd_smoke.py` expected outputs.
- Required `WGD publication report audit` release check.
- Objective audit requirement that final reports need both standard and WGD publication report audits.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_nextflow_wgd_smoke.py`
- `bin/genefam/run_release_checks.py`
- `tests/test_audit_objective_completion.py`
- `tests/test_run_nextflow_wgd_smoke.py`
- `tests/test_run_release_checks.py`
- `tests/test_workflow_modules.py`
- `workflows/main.nf`
- `workflows/modules/duplication_retention.nf`

Deleted:
- none

Verification:
- `python -m pytest tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes -q` first failed because the WGD branch did not expose plot-manifest, software-version, or figure-interpretation processes.
- `python -m pytest tests/test_run_nextflow_wgd_smoke.py::test_expected_published_outputs_cover_wgd_results -q` first failed because the WGD smoke expected outputs did not include the new report closure files.
- `python -m pytest tests/test_run_release_checks.py::test_default_checks_include_wgd_publication_report_audit_after_wgd_smoke -q` first failed because no WGD publication report audit existed in the release gate.
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_require_wgd_publication_report_audit -q` first failed because the objective audit considered final reports complete with only the standard publication audit.
- `python -m pytest tests/test_workflow_modules.py::test_duplication_retention_module_exposes_wgd_helper_processes tests/test_workflow_modules.py::test_main_workflow_includes_duplication_retention_processes tests/test_run_nextflow_wgd_smoke.py::test_expected_published_outputs_cover_wgd_results -q` passed with 3 tests after implementation.
- `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke` passed and generated WGD report `plot_manifest.tsv`, `software_versions.tsv`, `figure_interpretations.tsv`, `figure_interpretations.md`, and `final_report.md`.
- `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md` passed with `Passed: 5`, `Failed: 0`, `Complete: true`.
- `python -m pytest tests -q` passed with 367 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.

Commit:
- hash: 8035842aaf70c3bcd3383d089165f53042f7350d
- message: feat: add wgd publication report closure
- files: WGD Nextflow report wiring, WGD smoke/release/objective checks, tests, history

Next:
- Keep Docker/Apptainer runtime verification as the remaining final-stage external blocker; continue polishing Reference-level figure fidelity where useful.

## 2026-06-27 - Index final-report figure traceability matrix

Timestamp:
- 2026-06-27 13:39 CST

Context:
- The standard and WGD final reports contain a `Figure Traceability Matrix`, and the delivery gallery now links to it.
- The per-branch `report_index.tsv` files still exposed only `final_report`, so a user or audit script entering through the report index did not get a direct traceability-matrix entry.

Decisions:
- Add `figure_traceability_matrix` as a first-class report-index key for both standard and WGD branches.
- Derive the path from `final_report.md#figure-traceability-matrix` so the index stays synchronized with the final report path.
- Teach `audit_report_index.py` to require the traceability key and to validate anchor paths by checking the underlying Markdown file.

Added:
- Standard report-index row `figure_traceability_matrix`.
- WGD report-index row `figure_traceability_matrix`.
- Report-index audit requirement for the traceability matrix anchor.

Modified:
- `bin/genefam/audit_report_index.py`
- `bin/genefam/build_standard_report_index.py`
- `bin/genefam/build_wgd_report_index.py`
- `tests/test_audit_report_index.py`
- `tests/test_standard_branch_report_index.py`
- `tests/test_wgd_report_index.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_report_index.py tests/test_standard_branch_report_index.py tests/test_wgd_report_index.py -q` first failed with 7 failures because report indexes and audits did not yet require or emit `figure_traceability_matrix`.
- After implementation, `python -m pytest tests/test_audit_report_index.py tests/test_standard_branch_report_index.py tests/test_wgd_report_index.py -q` passed with 9 tests.
- `python -m pytest tests/test_audit_report_index.py tests/test_standard_branch_report_index.py tests/test_wgd_report_index.py tests/test_run_release_checks.py tests/test_workflow_modules.py -q` passed with 81 tests.
- `python -m pytest tests -q` passed with 434 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0; the generated TSV reported 50 total checks, 0 required failures, and 2 optional failures for missing Docker and Apptainer runtimes.
- `rg -n "figure_traceability_matrix|figure-traceability-matrix" results/nextflow_standard_feature_smoke/standard/report/report_index.tsv results/nextflow_wgd_smoke/wgd/report/report_index.tsv results/report_index_audit/standard_report_index_audit.md results/report_index_audit/wgd_report_index_audit.md` confirmed standard and WGD report indexes expose the final-report traceability anchor.
- `cat results/report_index_audit/standard_report_index_audit.tsv` and `cat results/report_index_audit/wgd_report_index_audit.tsv` showed both report-index audit checks passed.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed handoff, delivery bundle, release checks, report-index audits, quickstart, and local acceptance summaries; final-stage blocker remains Docker/Apptainer reproducibility.

Commit:
- hash: 26052c8c336a8e03bf3a3eb91bb91bf1a2074a21
- message: feat: index figure traceability in report indexes
- files: report-index builders, report-index audit, report-index tests, history

Next:
- Continue final MVP hardening while Docker/Apptainer packaging remains the intentionally deferred final stage.

## 2026-06-27 - Validate report-index traceability anchors

Timestamp:
- 2026-06-27 13:49 CST

Context:
- The standard and WGD report indexes now expose `figure_traceability_matrix` paths using `final_report.md#figure-traceability-matrix`.
- The report-index audit validated that the underlying Markdown file existed, but it did not prove the referenced anchor heading was present.

Decisions:
- Keep `figure_traceability_matrix` as the report-index entry point, but make the audit validate the anchor target itself.
- Use lightweight Markdown heading slug generation so `## Figure Traceability Matrix` satisfies `#figure-traceability-matrix`.
- Continue validating the file path separately before checking anchor content.

Added:
- Report-index audit check for missing Markdown anchors in indexed paths.
- Regression test proving a `figure_traceability_matrix` path fails when `final_report.md` lacks `## Figure Traceability Matrix`.

Modified:
- `bin/genefam/audit_report_index.py`
- `tests/test_audit_report_index.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_report_index.py -q` first failed because `report_index_artifact_files_exist` still passed when the final-report anchor heading was absent.
- After implementation and fixture update, `python -m pytest tests/test_audit_report_index.py -q` passed with 4 tests.
- `python -m pytest tests/test_audit_report_index.py tests/test_standard_branch_report_index.py tests/test_wgd_report_index.py tests/test_run_release_checks.py -q` passed with 64 tests.
- `python -m pytest tests -q` passed with 435 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0; the generated TSV reported 50 total checks, 0 required failures, and 2 optional failures for missing Docker and Apptainer runtimes.
- `cat results/report_index_audit/standard_report_index_audit.tsv` and `cat results/report_index_audit/wgd_report_index_audit.tsv` showed both report-index audit checks passed.
- `rg -n "Figure Traceability Matrix|figure_traceability_matrix|figure-traceability-matrix" results/nextflow_standard_feature_smoke/standard/report/final_report.md results/nextflow_wgd_smoke/wgd/report/final_report.md results/nextflow_standard_feature_smoke/standard/report/report_index.tsv results/nextflow_wgd_smoke/wgd/report/report_index.tsv` confirmed both indexed anchors and final-report headings exist in the generated standard/WGD reports.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed handoff, delivery bundle, release checks, report-index audits, quickstart, and local acceptance summaries; final-stage blocker remains Docker/Apptainer reproducibility.

Commit:
- hash: 7f81ef92cab2bdb787ebd7972aceaaff235e77a3
- message: test: validate report index traceability anchors
- files: report-index audit, report-index audit tests, history

Next:
- Continue final MVP hardening with report and audit evidence increasingly tied to concrete generated artifacts.

## 2026-06-27 - Add release-gated figure gallery audit

Timestamp:
- 2026-06-27 13:59 CST

Context:
- The delivery bundle writes a global `figure_gallery.tsv` and `figure_gallery.md` as the shortest paper-level plot navigation entry.
- The existing delivery bundle smoke only checked a few text fragments, so it did not prove that every gallery row links to real plot files, close-reading reports, software version tables, final reports, and traceability anchors.

Decisions:
- Add an explicit `audit_figure_gallery.py` gate for the delivery-bundle figure gallery.
- Validate required navigation columns and every linked file target in each row.
- Validate Markdown anchors such as `final_report.md#figure-traceability-matrix` by checking the target heading exists.
- Run the gallery audit in release checks immediately after the delivery bundle gallery smoke and before readiness/runtime checks.

Added:
- `bin/genefam/audit_figure_gallery.py`
- `tests/test_audit_figure_gallery.py`
- Release check `delivery bundle figure gallery audit`.

Modified:
- `bin/genefam/run_release_checks.py`
- `tests/test_run_release_checks.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_figure_gallery.py tests/test_run_release_checks.py::test_default_checks_include_delivery_bundle_gallery_audit_after_smoke -q` first failed because `bin.genefam.audit_figure_gallery` did not exist.
- After implementation, `python -m pytest tests/test_audit_figure_gallery.py tests/test_run_release_checks.py::test_default_checks_include_delivery_bundle_gallery_audit_after_smoke -q` passed with 3 tests.
- `python -m pytest tests/test_audit_figure_gallery.py tests/test_run_release_checks.py tests/test_run_delivery_bundle.py -q` passed with 58 tests.
- `python -m pytest tests -q` passed with 438 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0; the generated TSV reported 51 total checks, 0 required failures, and 2 optional failures for missing Docker and Apptainer runtimes.
- `cat results/delivery_bundle_smoke/figure_gallery_audit.tsv` and `cat results/delivery_bundle_smoke/figure_gallery_audit.md` showed `figure_gallery_required_columns` and `figure_gallery_linked_files_exist` both passed.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed handoff, delivery bundle, release checks, report-index audits, quickstart, and local acceptance summaries; final-stage blocker remains Docker/Apptainer reproducibility.

Commit:
- hash: 87b0c510c9abd38034d9fe3d1a8c84dfca3f96f9
- message: feat: audit delivery figure gallery links
- files: figure gallery audit script, release checks, figure gallery audit tests, history

Next:
- Continue tightening release evidence so every paper-level handoff artifact is generated and independently audited.

## 2026-06-27 - Document figure gallery audit and traceability index evidence

Timestamp:
- 2026-06-27 14:12 CST

Context:
- The release gate now includes `delivery bundle figure gallery audit`.
- The standard and WGD report indexes expose `figure_traceability_matrix` anchors, but README, quickstart, release-audit, and readiness docs still described the older evidence surface.

Decisions:
- Document `bin/genefam/audit_figure_gallery.py` and its generated `figure_gallery_audit.tsv/md` outputs as release-gated delivery evidence.
- Update report-index wording so users know `figure_traceability_matrix` is part of report-index closure.
- Keep the user-facing inspection order focused on handoff, publication audits, report-index audits, delivery bundle, and the final-stage Docker/Apptainer blocker.

Added:
- Documentation references to `results/delivery_bundle_smoke/figure_gallery_audit.tsv`.
- Documentation references to `results/delivery_bundle_smoke/figure_gallery_audit.md`.
- Documentation references to `figure_traceability_matrix`.
- Regression assertions in docs tests for the new gallery audit and traceability-index wording.

Modified:
- `README.md`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `docs/readiness_checklist.md`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`
- `HISTORY.md`

Deleted:
- none

Verification:
- `python -m pytest tests/test_release_audit_docs.py tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report tests/test_quickstart_docs.py::test_quickstart_documents_minimum_verified_run_path -q` first failed because the docs did not mention `audit_figure_gallery.py`, `figure_gallery_audit`, or `figure_traceability_matrix`.
- After documentation updates, the same command passed with 4 tests.
- `python -m pytest tests/test_release_audit_docs.py tests/test_runtime_environment_files.py tests/test_quickstart_docs.py -q` passed with 17 tests.
- `python -m pytest tests -q` passed with 438 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0; the generated TSV reported 51 total checks, 0 required failures, and 2 optional failures for missing Docker and Apptainer runtimes.
- `cat results/delivery_bundle_smoke/figure_gallery_audit.tsv` showed `figure_gallery_required_columns` and `figure_gallery_linked_files_exist` both passed.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed handoff, delivery bundle, release checks, report-index audits, quickstart, and local acceptance summaries; final-stage blocker remains Docker/Apptainer reproducibility.

Commit:
- hash: e4c9ecf1cc2741ef1654ec8cc6333a65e209b69f
- message: docs: document figure gallery audit evidence
- files: README, quickstart/release/readiness docs, docs tests, history

Next:
- Continue aligning user-facing docs with each new release-gated evidence surface.

## 2026-06-27 - Expose figure traceability links in delivery gallery

Timestamp:
- 2026-06-27 13:28 CST

Context:
- Final reports now contain a `Figure Traceability Matrix`, but the top-level delivery bundle figure gallery only linked plot files, close-reading reports, software versions, and final reports.
- For a paper-style handoff, each gallery row should directly expose the exact final-report traceability anchor so users can audit every figure from the global index.

Decisions:
- Add a machine-readable `traceability_matrix` column to `figure_gallery.tsv`.
- Add the same `traceability_matrix` field to `figure_gallery.md`.
- Derive the traceability link automatically from each row's `final_report` path using `#figure-traceability-matrix`, so future standard/WGD plots inherit the link without repeating constants.

Added:
- `traceability_matrix` column in the delivery bundle figure gallery TSV/Markdown outputs.
- Regression assertions that the gallery header and `tree_features` row include the traceability anchor.

Modified:
- `HISTORY.md`
- `bin/genefam/run_delivery_bundle.py`
- `tests/test_run_delivery_bundle.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py -q` first failed because `figure_gallery.tsv` did not include `traceability_matrix`.
- After implementation, `python -m pytest tests/test_run_delivery_bundle.py -q` passed with 1 test.
- `python -m pytest tests -q` passed with 434 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0; the generated TSV reported 50 total checks, 0 required failures, and 2 optional failures for missing Docker and Apptainer runtimes.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed `results/delivery_bundle/figure_gallery.tsv` plus `results/delivery_bundle/figure_gallery.md`; final-stage blocker remains Docker/Apptainer reproducibility.
- `head -n 3 results/delivery_bundle/figure_gallery.tsv` and `rg -n "traceability_matrix|figure-traceability-matrix" results/delivery_bundle/figure_gallery.md results/delivery_bundle/figure_gallery.tsv` confirmed every standard/WGD figure row exposes the traceability anchor.

Commit:
- hash: 6c8a5552aeab707220d776dbb7e8eac39fda3f9a
- message: feat: expose figure traceability in delivery gallery
- files: delivery bundle figure gallery, delivery bundle test, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging intentionally deferred until the analysis/report flow remains stable.

## 2026-06-27 - Require raw MCScanX KaKs Nextflow evidence for WGD audits

Timestamp:
- 2026-06-27 08:09 CST

Context:
- The active MVP goal explicitly includes real MCScanX and Ka/Ks end-to-end entrypoints for WGD/evolution analysis.
- Release checks already included `Nextflow raw MCScanX/KaKs WGD smoke`, but `WGD gamma beta alpha theta evidence` and `Ka/Ks and retention analysis` could still be achieved without that raw-input Nextflow evidence.

Decisions:
- Require `Nextflow raw MCScanX/KaKs WGD smoke` for the WGD event evidence objective row.
- Require the same raw-input smoke for the Ka/Ks and retention analysis objective row.
- Update notes so both rows state that prepared evidence, raw MCScanX/Ka/Ks inputs, and formal Nextflow WGD branch evidence are represented.

Added:
- Regression test proving WGD event evidence remains `missing` without `Nextflow raw MCScanX/KaKs WGD smoke`.
- Regression test proving Ka/Ks and retention analysis remains `missing` without `Nextflow raw MCScanX/KaKs WGD smoke`.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_wgd_event_evidence_requires_raw_mcscanx_kaks_nextflow_smoke tests/test_audit_objective_completion.py::test_kaks_and_retention_analysis_requires_raw_mcscanx_kaks_nextflow_smoke -q` first failed with the old rule because both objective rows were `achieved` without raw MCScanX/Ka/Ks Nextflow evidence.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 38 tests after implementation.
- `python -m pytest tests -q` passed with 398 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "WGD gamma beta alpha theta evidence|Ka/Ks and retention analysis|Nextflow raw MCScanX/KaKs WGD smoke|raw MCScanX/KaKs" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed both WGD/KaKs audit rows now name the raw MCScanX/Ka/Ks Nextflow evidence.

Commit:
- hash: bec5eda5c4b5b0a70cb56c13e5fe34b415a3fb8b
- message: test: require raw mcscanx kaks evidence for wgd audits
- files: objective audit rule, objective audit tests, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging still intentionally deferred to the final runtime stage.

## 2026-06-27 - Require formal Nextflow sources for final report audit

Timestamp:
- 2026-06-27 08:02 CST

Context:
- The objective requires final reports to include every figure interpretation, software/R package versions, QC, and reproducibility information.
- `final reports` already required standard report, prepared-WGD handoff, quickstart, and both publication report audits, but it did not explicitly require the formal Nextflow standard visualization or WGD branch smokes that produce the report packages being audited.

Decisions:
- Require `Nextflow standard visualization smoke` for the `final reports` objective row.
- Require `Nextflow WGD event smoke` for the same row.
- Update the final-report note so the standard and WGD Markdown report packages are tied to formal Nextflow standard visualization and WGD branch evidence.

Added:
- Regression test proving `final reports` remains `missing` when formal Nextflow standard visualization and WGD branch evidence are absent.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_require_nextflow_standard_and_wgd_report_sources -q` first failed with the old rule because final reports were `achieved` without `Nextflow standard visualization smoke` or `Nextflow WGD event smoke`.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 36 tests after implementation.
- `python -m pytest tests -q` passed with 396 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "final reports|Nextflow standard visualization smoke|Nextflow WGD event smoke|formal Nextflow standard visualization" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed the final reports row now names the formal Nextflow sources.

Commit:
- hash: a1a2d36dc647b828f76897e11acec87458b4af37
- message: test: require nextflow sources for final report audit
- files: objective audit rule, objective audit tests, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging still intentionally deferred to the final runtime stage.

## 2026-06-27 - Require manifest Nextflow evidence for YAML species selection audit

Timestamp:
- 2026-06-27 07:56 CST

Context:
- The active MVP goal requires YAML-driven species selection from large species directories and manifest-style inputs.
- `Nextflow DSL2 workflow` already required `Nextflow standard manifest smoke`, but `YAML-driven species selection` could still be achieved with only config validation and Python species-selection smokes.

Decisions:
- Require `Nextflow standard manifest smoke` for the `YAML-driven species selection` objective row.
- Update the YAML species-selection evidence and note so manifest-mode Nextflow standard runs are explicitly part of the YAML-driven input contract.

Added:
- Regression test proving `YAML-driven species selection` remains `missing` when manifest-mode Nextflow standard evidence is absent.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_yaml_driven_species_selection_requires_nextflow_manifest_standard_smoke -q` first failed with the old rule because YAML-driven species selection was `achieved` without `Nextflow standard manifest smoke`.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 35 tests after implementation.
- `python -m pytest tests -q` passed with 395 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "YAML-driven species selection|Nextflow standard manifest smoke|manifest-mode Nextflow" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed the YAML species-selection row now names manifest-mode Nextflow standard evidence.

Commit:
- hash: 40fbff181d800bc5c10d88815a83d1c4a8bd9ddf
- message: test: require manifest nextflow evidence for yaml audit
- files: objective audit rule, objective audit tests, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging still intentionally deferred to the final runtime stage.

## 2026-06-27 - Require alignment phylogeny evidence for standard branch audit

Timestamp:
- 2026-06-27 07:50 CST

Context:
- The active MVP goal includes system phylogeny as a core analysis component.
- `Nextflow DSL2 workflow` already required `alignment phylogeny smoke`, but the higher-level `standard identification branch` row could still be achieved without alignment/phylogeny evidence.

Decisions:
- Require `alignment phylogeny smoke` for the `standard identification branch` objective row.
- Update the standard branch evidence and note so alignment/phylogeny outputs are explicitly represented alongside domain filtering, motif parsing, gene structure, Python standard branch, and Nextflow standard branch evidence.

Added:
- Regression test proving `standard identification branch` remains `missing` when alignment/phylogeny evidence is absent.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_standard_identification_branch_requires_alignment_phylogeny_smoke -q` first failed with the old rule because standard branch evidence was `achieved` without `alignment phylogeny smoke`.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 34 tests after implementation.
- `python -m pytest tests -q` passed with 394 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "standard identification branch|alignment phylogeny smoke|alignment/phylogeny" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed the standard identification branch row now names alignment/phylogeny evidence.

Commit:
- hash: 5498fe18a2d06c3a9ac30791bc6eb157e7264b84
- message: test: require alignment phylogeny evidence for standard audit
- files: objective audit rule, objective audit tests, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging still intentionally deferred to the final runtime stage.

## 2026-06-27 - Require Nextflow and heatmap evidence for chromosome expression audit

Timestamp:
- 2026-06-27 07:44 CST

Context:
- The objective requires chromosome localization and RNA-seq expression integration as part of the paper-level MVP.
- The dedicated expression heatmap objective already required `expression heatmap visualization smoke` and `Nextflow standard visualization smoke`, but the higher-level `chromosome and expression integration` row only required chromosome location, standard branch, expression subset, and quickstart evidence.

Decisions:
- Require `Nextflow standard branch smoke` for the `chromosome and expression integration` objective row.
- Require `expression heatmap visualization smoke` for the same row so expression integration includes report-ready heatmap figure evidence, not only matrix subsetting.
- Update the row note to state that chromosome locations, RNA-seq subsets, heatmap figures, and standard report handoff are exercised through script evidence and the formal Nextflow standard branch.

Added:
- Regression test proving `chromosome and expression integration` remains `missing` when formal Nextflow standard branch and expression heatmap evidence are absent.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_chromosome_and_expression_integration_requires_nextflow_and_heatmap_evidence -q` first failed with the old rule because chromosome/expression integration was `achieved` without `Nextflow standard branch smoke` or `expression heatmap visualization smoke`.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 33 tests after implementation.
- `python -m pytest tests -q` passed with 393 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "chromosome and expression integration|Nextflow standard branch smoke|expression heatmap visualization smoke|formal Nextflow standard branch" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed the chromosome/expression integration row now names the formal Nextflow and heatmap evidence.

Commit:
- hash: 0d5c622425e9a61feeb3240f19f37eb60fa1bc4d
- message: test: require nextflow heatmap evidence for chromosome expression audit
- files: objective audit rule, objective audit tests, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging still intentionally deferred to the final runtime stage.

## 2026-06-27 - Name Nextflow WGD evidence in WGD event audit

Timestamp:
- 2026-06-27 07:38 CST

Context:
- The `WGD gamma beta alpha theta evidence` objective row already required `Nextflow WGD event smoke` internally.
- Its displayed evidence text still only named synteny parser, WGD event, and prepared handoff checks, so the generated objective audit understated the formal Nextflow WGD branch evidence behind gamma beta alpha theta interpretation.

Decisions:
- Keep the achieved condition unchanged because it already required the correct formal WGD smoke.
- Update the objective-audit evidence and note so the report explicitly names `Nextflow WGD event smoke` and the formal Nextflow WGD branch.

Added:
- Regression test proving the WGD event objective row names `Nextflow WGD event smoke` in evidence and `formal Nextflow WGD branch` in the note when achieved.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_wgd_event_evidence_names_nextflow_wgd_branch_evidence -q` first failed with the old evidence text because `Nextflow WGD event smoke` was absent from the displayed WGD event evidence.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 32 tests after implementation.
- `python -m pytest tests -q` passed with 392 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "WGD gamma beta alpha theta evidence|Nextflow WGD event smoke|formal Nextflow WGD branch" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed the WGD event evidence row now names the formal Nextflow WGD branch.

Commit:
- hash: 0839885483ec8c839d0fb93ec064bbd00cb5d7b4
- message: test: name nextflow wgd evidence in objective audit
- files: objective audit evidence text, objective audit tests, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging still intentionally deferred to the final runtime stage.

## 2026-06-27 - Require formal WGD evidence for Ka/Ks retention audit

Timestamp:
- 2026-06-27 07:33 CST

Context:
- The dedicated Ka/Ks/WGD visualization and aggregate paper-level visualization gates already required pangenome-class Ka/Ks and formal Nextflow WGD evidence.
- The higher-level `Ka/Ks and retention analysis` objective row still treated the analysis branch as complete with parser, duplicate-type Ka/Ks, retention enrichment, WGD event, and prepared handoff evidence, but without pangenome-class Ka/Ks or formal Nextflow WGD branch evidence.

Decisions:
- Require `pangenome-class Ka/Ks visualization smoke` for the `Ka/Ks and retention analysis` objective row.
- Require `Nextflow WGD event smoke` for the same row so the analysis audit is connected to the formal WGD DSL2 branch, not only prepared standalone evidence.
- Keep `WGD publication report audit` in the report/visualization gates rather than duplicating it in this analysis row.

Added:
- Regression test proving `Ka/Ks and retention analysis` remains `missing` when pangenome-class Ka/Ks and formal Nextflow WGD evidence are absent.
- Objective-audit evidence text naming pangenome-class Ka/Ks and formal Nextflow WGD branch evidence.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_kaks_and_retention_analysis_requires_pangenome_and_nextflow_wgd_evidence -q` first failed with the old rule because `Ka/Ks and retention analysis` was `achieved` without pangenome-class Ka/Ks or `Nextflow WGD event smoke`.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 31 tests after implementation.
- `python -m pytest tests -q` passed with 391 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "Ka/Ks and retention analysis|pangenome-class Ka/Ks visualization smoke|formal Nextflow WGD branch" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed the analysis row now names pangenome-class Ka/Ks and formal Nextflow WGD branch evidence.

Commit:
- hash: 5a783e45706fcf4e1e2506f49ae3169600b8978e
- message: test: require formal wgd evidence for kaks retention audit
- files: objective audit rule, objective audit tests, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging still intentionally deferred to the final runtime stage.

## 2026-06-27 - Require WGD figures in paper-level visualization audit

Timestamp:
- 2026-06-27 07:27 CST

Context:
- The dedicated `Ka/Ks WGD visualization` objective row already required Ks distribution, duplicate-type Ka/Ks, pangenome-class Ka/Ks, `Nextflow WGD event smoke`, and `WGD publication report audit`.
- The broader `paper-level visualization modules` row still considered the paper-level figure set complete without those WGD figure/report checks, which made the top-level visualization gate weaker than the actual MVP promise.

Decisions:
- Promote the Ka/Ks/WGD figure evidence into the aggregate paper-level visualization objective.
- Keep WGD-specific biological interpretation in the dedicated Ka/Ks WGD row, while making the aggregate row prove that the whole paper-style figure suite includes WGD plots and WGD report evidence.

Added:
- Regression test proving `paper-level visualization modules` stays `missing` when standard visualizations pass but Ka/Ks/WGD figures and WGD report evidence are absent.
- Aggregate visualization evidence text that explicitly includes `Ka/Ks WGD annotation plot smoke`, `duplicate-type Ka/Ks visualization smoke`, `pangenome-class Ka/Ks visualization smoke`, `Nextflow WGD event smoke`, and `WGD publication report audit`.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_paper_level_visualization_modules_require_wgd_visualization_evidence -q` first failed with the old rule because the aggregate paper-level visualization row was `achieved` without WGD figure/report evidence.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 30 tests after implementation.
- `python -m pytest tests -q` passed with 390 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "paper-level visualization modules|Ka/Ks WGD annotation plot smoke|WGD publication report audit|Ks distribution" results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed the aggregate paper-level visualization row now names the WGD figure and report evidence.

Commit:
- hash: 35dbe6234ed96dad95bf414581c9cf2f55ef1686
- message: test: require wgd figures in paper visualization audit
- files: objective audit rule, objective audit tests, history

Next:
- Continue final MVP hardening with Docker/Apptainer packaging still intentionally deferred to the final runtime stage.

## 2026-06-27 - Require Nextflow report evidence for Ka/Ks WGD audit

Timestamp:
- 2026-06-27 07:22 CST

Context:
- The Ka/Ks WGD objective audit already checked standalone Ks distribution, duplicate-type Ka/Ks, and pangenome-class Ka/Ks visualization smokes.
- The active MVP goal requires gamma beta alpha theta WGD interpretation and Ka/Ks figures to be connected to the formal Nextflow WGD branch and publication-style report, not only standalone plotting scripts.

Decisions:
- Require `Nextflow WGD event smoke` for the `Ka/Ks WGD visualization` objective row.
- Require `WGD publication report audit` for the same objective row so the WGD figures must include report-registered close reading and method/software evidence.
- Keep container runtime verification deferred to the final packaging phase; no Docker/Apptainer requirement was promoted from optional to required.

Added:
- Regression test proving Ka/Ks WGD visualization remains `missing` when standalone WGD plot smokes pass but formal Nextflow WGD/report evidence is absent.
- Objective-audit evidence text that explicitly names `Nextflow WGD event smoke` and `WGD publication report audit`.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_objective_audit_lists_named_paper_level_visualization_requirements tests/test_audit_objective_completion.py::test_kaks_wgd_visualization_requires_nextflow_wgd_report_evidence -q` first failed with the old rule because Ka/Ks WGD visualization was achieved without `Nextflow WGD event smoke` or `WGD publication report audit`.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 29 tests after implementation.
- `python -m pytest tests -q` passed with 389 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` passed and reported `Achieved: 19`, `Blocked: 1`, `Missing: 0`, `Complete: false`.
- `rg -n "Ka/Ks WGD visualization|Nextflow WGD event smoke|WGD publication report audit|Nextflow report evidence" results/objective_audit/objective_audit.md results/release_checks/release_checks.tsv` confirmed the Ka/Ks WGD audit row now requires the formal WGD Nextflow smoke and WGD publication report audit.

Commit:
- hash: 2e852301e3aee824c5d163ad2cc53f93b228a58a
- message: test: require nextflow evidence for wgd audit
- files: objective audit rule, objective audit tests, history

Next:
- Continue final MVP hardening with container/runtime packaging still intentionally deferred until the analysis flow and report gates are fully stable.

## 2026-06-27 - Audit all available report-index paths

Timestamp:
- 2026-06-27 15:26 CST

Context:
- The report-index audit checked required core artifacts such as plot manifest, software versions, figure interpretations, final report, and traceability anchor.
- Standard and WGD `report_index.tsv` files also contain many additional `available` rows for report tables, plots, sequences, alignments, trees, promoter/PPI/expression outputs, WGD event evidence, and Ka/Ks outputs.
- A non-core indexed plot/table path could drift without failing the previous report-index audit.

Decisions:
- Add `report_index_available_paths_exist` to `bin/genefam/audit_report_index.py`.
- Make the new check validate every `status=available` report-index row, including non-core tables and plots, with anchor checks for Markdown fragment paths.
- Update README, quickstart, release audit, and readiness checklist to state that report-index audits verify all available indexed report paths exist.

Added:
- Regression test proving a missing non-core `tree_features_pdf` available path fails report-index audit.
- Documentation assertions for the stronger report-index audit contract.

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_report_index.py`
- `docs/quickstart.md`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `tests/test_audit_report_index.py`
- `tests/test_release_audit_docs.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_report_index.py -q` first failed because `report_index_available_paths_exist` did not exist.
- `python -m pytest tests/test_audit_report_index.py -q` passed with 5 tests after implementation and summary-count updates.
- `python -m pytest tests/test_audit_report_index.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py tests/test_quickstart_docs.py -q` passed with 22 tests after documentation updates.
- `python -m pytest tests -q` passed with 445 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and wrote `Passed: 50`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `cat results/report_index_audit/standard_report_index_audit.tsv` and `cat results/report_index_audit/wgd_report_index_audit.tsv` confirmed `report_index_available_paths_exist` passed for both standard and WGD report indexes.
- `rg -n "report_index_available_paths_exist|all available indexed report paths exist|standard report index audit|WGD report index audit" results/report_index_audit/standard_report_index_audit.md results/report_index_audit/wgd_report_index_audit.md results/release_checks/release_checks.tsv README.md docs/quickstart.md docs/release_audit.md docs/readiness_checklist.md` confirmed generated audit outputs, release commands, and docs expose the stronger report-index contract.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed release checks, quickstart, delivery bundle, and local acceptance outputs; it reported the expected final-stage blocker: Docker/Apptainer reproducibility.
- `python -m pytest tests -q` passed again with 445 tests after local acceptance refreshed generated outputs.

Commit:
- hash: 2a12e4a4e94c129f63478353dcc8530d2d141e7f
- message: test: audit report index available paths
- files: report-index audit, README/quickstart/release/readiness docs, tests, history

Next:
- Continue final MVP hardening by checking remaining report/summary surfaces for drift between generated inventories and top-level evidence; Docker/Apptainer remains the final packaging-stage runtime blocker.

## 2026-06-27 - Surface delivery audits in handoff report

Timestamp:
- 2026-06-27 15:13 CST

Context:
- Release checks, delivery bundle, and local acceptance already exposed `figure_gallery_audit` and `delivery_manifest_audit`.
- The compact handoff report and `handoff_summary.tsv` still only exposed report-index audits plus figure-gallery file paths, so the top-level handoff surface did not show whether the delivery audits passed.

Decisions:
- Add `figure_gallery_audit` and `delivery_manifest_audit` status rows to handoff sections and summary TSV.
- Add both audit Markdown paths to the handoff report's key evidence list.
- Keep handoff report focused on status and evidence rather than duplicating full audit tables.

Added:
- Handoff status line for `figure_gallery_audit`.
- Handoff status line for `delivery_manifest_audit`.
- Handoff evidence links to `results/delivery_bundle_smoke/figure_gallery_audit.md` and `results/delivery_bundle_smoke/delivery_manifest_audit.md`.

Modified:
- `HISTORY.md`
- `bin/genefam/build_handoff_report.py`
- `tests/test_build_handoff_report.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_build_handoff_report.py -q` first failed because the handoff report and summary did not output the two delivery audit statuses; the initial fixture count also needed to reflect the two newly added passed release rows.
- `python -m pytest tests/test_build_handoff_report.py -q` passed with 5 tests after implementation.
- `python -m pytest tests -q` passed with 444 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and wrote `Passed: 50`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `rg -n "Figure gallery audit|Delivery manifest audit|figure_gallery_audit|delivery_manifest_audit|Passed: 50|Required failed: 0|Optional failed: 2" results/handoff/handoff_report.md results/handoff/handoff_summary.tsv results/release_checks/release_checks.md` confirmed the top-level handoff report, handoff summary TSV, and release report all expose the delivery-audit evidence.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed release checks, quickstart, delivery bundle, and local acceptance outputs; it reported the expected final-stage blocker: Docker/Apptainer reproducibility.
- `python -m pytest tests -q` passed again with 444 tests after local acceptance refreshed generated outputs.

Commit:
- hash: 84cbf57357fff90c07d61f08101445a73beb57d8
- message: feat: surface delivery audits in handoff
- files: handoff report builder, handoff tests, history

Next:
- Continue final MVP hardening by checking any remaining top-level documentation or generated summaries for missing report/visualization evidence; Docker/Apptainer remains the final packaging-stage runtime blocker.

## 2026-06-27 - Surface delivery audits in local acceptance

Timestamp:
- 2026-06-27 15:03 CST

Context:
- The release gate already ran `delivery bundle figure gallery audit` and `delivery bundle manifest audit`.
- The local acceptance summary did not list those two delivery audits as separate pass/fail rows, so a user opening only `results/local_acceptance/local_acceptance_summary.md` could miss whether the global plot gallery and final handoff manifest had been checked.

Decisions:
- Add `figure_gallery_audit` and `delivery_manifest_audit` rows to the local acceptance summary.
- Extract both statuses from `results/release_checks/release_checks.tsv` inside `scripts/run_local_acceptance.sh`.
- Print both delivery-audit Markdown files in the primary handoff file list and fail the wrapper if either required audit fails.
- Update README and quickstart docs so the local acceptance summary is documented as covering the two delivery audits.

Added:
- Local acceptance row for `figure_gallery_audit`.
- Local acceptance row for `delivery_manifest_audit`.
- Script assertions and docs assertions for the new local acceptance rows.

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/write_local_acceptance_summary.py`
- `docs/quickstart.md`
- `scripts/run_local_acceptance.sh`
- `tests/test_local_acceptance_script.py`
- `tests/test_quickstart_docs.py`
- `tests/test_runtime_environment_files.py`
- `tests/test_write_local_acceptance_summary.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py -q` first failed because `write_acceptance_summary()` and `build_acceptance_rows()` did not accept `figure_gallery_status`/`delivery_manifest_status`, and the wrapper did not extract those statuses.
- `python -m pytest tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py -q` passed with 5 tests after implementation.
- `python -m pytest tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py tests/test_quickstart_docs.py tests/test_runtime_environment_files.py -q` first failed because a README test still expected the older shorter local acceptance description.
- `python -m pytest tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py tests/test_quickstart_docs.py tests/test_runtime_environment_files.py -q` passed with 21 tests after updating the docs contract.
- `python -m pytest tests -q` passed with 444 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0.
- `bash scripts/run_local_acceptance.sh` exited 0 and printed both `results/delivery_bundle_smoke/figure_gallery_audit.md` and `results/delivery_bundle_smoke/delivery_manifest_audit.md` in the primary handoff file list; it reported the expected final-stage blocker: Docker/Apptainer reproducibility.
- `cat results/local_acceptance/local_acceptance_summary.tsv` confirmed `figure_gallery_audit` and `delivery_manifest_audit` rows both passed.
- `rg -n "figure_gallery_audit|delivery_manifest_audit|Overall status|Passed: 50|Required failed: 0|Optional failed: 2" results/local_acceptance/local_acceptance_summary.md results/release_checks/release_checks.md` confirmed local acceptance exposes the delivery audits and release checks remain `Passed: 50`, `Required failed: 0`, `Optional failed: 2`.
- `python -m pytest tests -q` passed again with 444 tests after local acceptance refreshed generated outputs.

Commit:
- hash: c4e648c122a6cb65d8c9cb5333af15e793de85d7
- message: feat: surface delivery audits in acceptance
- files: local acceptance summary, local acceptance wrapper, README/quickstart docs, tests, history

Next:
- Continue final MVP hardening by making the final handoff/report surfaces easier to audit end to end; Docker/Apptainer remains the final packaging-stage runtime blocker.

## 2026-06-27 - Audit delivery manifest handoff paths

Timestamp:
- 2026-06-27 14:51 CST

Context:
- The delivery bundle manifest is the final user-facing handoff index, but release checks did not yet verify that rows marked `available` or `blocked` point to real files or accepted runtime locators.
- A stale delivery manifest path would make the MVP look complete while sending users to a missing report, audit, config, or recovery artifact.

Decisions:
- Add a dedicated delivery-manifest audit after the figure-gallery audit in the release gate.
- Treat `available` and `blocked` manifest rows as path-bearing handoff rows that must resolve to existing filesystem targets, while allowing `missing` rows to point at absent optional runtime diagnostics and allowing `GeneFamilyFlow:` runtime locators.
- Include `delivery bundle manifest audit` in the `final reports` objective-audit completion evidence.
- Document the new audit in README, quickstart, release audit, and readiness checklist.

Added:
- `bin/genefam/audit_delivery_manifest.py`
- `tests/test_audit_delivery_manifest.py`
- Release check `delivery bundle manifest audit`
- Objective-audit regression test proving final reports remain missing without the delivery manifest audit.

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_objective_completion.py`
- `bin/genefam/run_release_checks.py`
- `docs/quickstart.md`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `tests/test_audit_objective_completion.py`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_delivery_manifest.py tests/test_run_release_checks.py::test_default_checks_include_delivery_bundle_manifest_audit_after_gallery_audit tests/test_audit_objective_completion.py::test_final_reports_require_delivery_manifest_audit tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure -q` first failed because `bin.genefam.audit_delivery_manifest` did not exist.
- `python -m pytest tests/test_audit_delivery_manifest.py tests/test_run_release_checks.py::test_default_checks_include_delivery_bundle_manifest_audit_after_gallery_audit tests/test_audit_objective_completion.py::test_final_reports_require_delivery_manifest_audit tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure -q` passed with 5 tests after implementation.
- `python -m pytest tests/test_audit_delivery_manifest.py tests/test_audit_objective_completion.py tests/test_run_release_checks.py -q` first failed because `tests/test_run_release_checks.py::test_write_objective_audit_reads_publication_detail_audits` used the old final-report release fixture without `delivery bundle manifest audit`.
- `python -m pytest tests/test_audit_delivery_manifest.py tests/test_audit_objective_completion.py tests/test_run_release_checks.py -q` passed with 104 tests after fixture update.
- `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py tests/test_runtime_environment_files.py -q` passed with 17 tests after documentation updates.
- `python -m pytest tests -q` passed with 444 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and wrote `Passed: 50`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `cat results/delivery_bundle_smoke/delivery_manifest_audit.tsv` confirmed `delivery_manifest_required_columns` and `delivery_manifest_paths_exist` both passed.
- `rg -n "delivery bundle manifest audit|delivery_manifest_audit|delivery manifest audit|final reports|Available and blocked|available and blocked" results/release_checks/release_checks.tsv results/objective_audit/objective_audit.tsv results/objective_audit/objective_audit.md README.md docs/quickstart.md docs/release_audit.md docs/readiness_checklist.md` confirmed release, objective, and documentation evidence for the new audit.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed release checks, quickstart, delivery bundle, and local acceptance outputs; it reported the expected final-stage blocker: Docker/Apptainer reproducibility.
- `python -m pytest tests -q` passed again with 444 tests after local acceptance refreshed generated outputs.

Commit:
- hash: 3823576983e398867a98a3f3ce63ec0e223a800b
- message: test: audit delivery manifest handoff paths
- files: delivery manifest audit, release gate, objective audit, docs, tests, history

Next:
- Continue final MVP hardening by checking remaining generated handoff/report artifacts for drift, while keeping Docker/Apptainer runtime verification as the final packaging-stage blocker.

## 2026-06-27 - Audit delivery figure gallery against plot manifests

Timestamp:
- 2026-06-27 14:37 CST

Context:
- The delivery figure gallery linked existing rows to plots, figure interpretations, software versions, final reports, and traceability anchors.
- The standard report `plot_manifest.tsv` also registered `gene_family_pangenome_summary`, but the delivery gallery did not list that plot key, and the gallery audit did not compare gallery coverage against the standard/WGD plot manifests.

Decisions:
- Make `figure_gallery_audit` verify plot_manifest coverage for the standard and WGD report manifests.
- Add `gene_family_pangenome_summary` to the delivery figure gallery so the global plot index covers the pangenome/copy-number balance figure registered by the standard report.
- Run the gallery audit in release checks with explicit `standard=.../plot_manifest.tsv` and `wgd=.../plot_manifest.tsv` coverage inputs.
- Update README, release-audit, and readiness docs to describe plot_manifest coverage as part of the gallery audit contract.

Added:
- `figure_gallery_manifest_coverage` audit check.
- CLI support for repeated `--plot-manifest BRANCH=PATH` arguments in `bin/genefam/audit_figure_gallery.py`.
- Regression test proving a missing `gene_family_pangenome_summary` gallery row fails manifest coverage.
- Delivery-bundle test assertions for the `gene_family_pangenome_summary` TSV/Markdown gallery entry.

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/audit_figure_gallery.py`
- `bin/genefam/run_delivery_bundle.py`
- `bin/genefam/run_release_checks.py`
- `docs/readiness_checklist.md`
- `docs/release_audit.md`
- `tests/test_audit_figure_gallery.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_run_release_checks.py`
- `tests/test_runtime_environment_files.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_figure_gallery.py::test_figure_gallery_audit_requires_manifest_plot_coverage tests/test_run_release_checks.py::test_default_checks_include_delivery_bundle_gallery_audit_after_smoke tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index -q` first failed because `audit_figure_gallery` did not accept plot manifests, the release check did not pass them, and the delivery gallery lacked `gene_family_pangenome_summary`.
- `python -m pytest tests/test_audit_figure_gallery.py tests/test_run_release_checks.py::test_default_checks_include_delivery_bundle_gallery_audit_after_smoke tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index tests/test_runtime_environment_files.py::test_readiness_checklist_documents_command_audit tests/test_runtime_environment_files.py::test_readme_points_to_final_handoff_report -q` passed with 7 tests after implementation and docs updates.
- `python -m pytest tests -q` passed with 440 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and wrote `Passed: 49`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `cat results/delivery_bundle_smoke/figure_gallery_audit.tsv` confirmed `figure_gallery_manifest_coverage` passed for `standard=results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv` and `wgd=results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv`.
- `rg -n "gene_family_pangenome_summary|figure_gallery_manifest_coverage|delivery bundle figure gallery audit|plot_manifest coverage" results/delivery_bundle_smoke/delivery_bundle/figure_gallery.tsv results/delivery_bundle_smoke/figure_gallery_audit.md results/release_checks/release_checks.tsv results/delivery_bundle/figure_gallery.tsv README.md docs/release_audit.md docs/readiness_checklist.md` confirmed the gallery row, release command, audit output, and docs all expose the new coverage contract.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed release checks, quickstart, delivery bundle, and local acceptance outputs; it reported the expected final-stage blocker: Docker/Apptainer reproducibility.
- `python -m pytest tests -q` passed again with 440 tests after local acceptance refreshed the generated handoff outputs.

Commit:
- hash: 36d0a6dffb66e1ac9434f9379c5a36610bd26790
- message: test: audit figure gallery manifest coverage
- files: figure gallery audit, delivery gallery, release gate, docs, tests, history

Next:
- Continue final MVP hardening by looking for remaining places where report/generated inventories can drift apart, while leaving Docker/Apptainer runtime verification for the final packaging stage.

## 2026-06-27 - Require figure gallery audit in final objective reports

Timestamp:
- 2026-06-27 14:24 CST

Context:
- The delivery bundle already had a dedicated `delivery bundle figure gallery audit` release gate.
- The long-form objective audit still allowed `final reports` to be marked achieved from publication/report-index audits alone, so the final goal summary did not explicitly require the global figure gallery linkage audit.

Decisions:
- Treat `delivery bundle figure gallery audit` as part of the formal `final reports` completion contract.
- Make the final-report objective note describe how `figure_gallery_audit` links plot files to figure interpretations, software versions, final report anchors, and the traceability matrix.

Added:
- Regression test proving `final reports` remains `missing` when the delivery figure gallery audit is absent.
- Release-check writer test coverage proving `objective_audit.tsv` records `delivery bundle figure gallery audit` in the final-report evidence.

Modified:
- `HISTORY.md`
- `bin/genefam/audit_objective_completion.py`
- `tests/test_audit_objective_completion.py`
- `tests/test_run_release_checks.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_audit_objective_completion.py::test_final_reports_require_delivery_figure_gallery_audit tests/test_audit_objective_completion.py::test_final_reports_note_names_complete_publication_report_closure -q` first failed because the old objective audit marked final reports achieved without `delivery bundle figure gallery audit` and did not mention `figure_gallery_audit`.
- `python -m pytest tests/test_audit_objective_completion.py -q` passed with 45 tests after implementation.
- `python -m pytest tests -q` first failed because `tests/test_run_release_checks.py::test_write_objective_audit_reads_publication_detail_audits` still used the old release fixture without the gallery audit row.
- `python -m pytest tests/test_audit_objective_completion.py tests/test_run_release_checks.py::test_write_objective_audit_reads_publication_detail_audits -q` passed with 46 tests after fixture update.
- `python -m pytest tests -q` passed with 439 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and wrote `Passed: 49`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.
- `rg -n "delivery bundle figure gallery audit|final reports|figure_gallery_audit|Achieved|Blocked|Missing|Complete" results/release_checks/release_checks.tsv results/objective_audit/objective_audit.md results/objective_audit/objective_audit.tsv` confirmed `final reports` is achieved with `delivery bundle figure gallery audit`, `figure_gallery_audit`, `Achieved: 19`, `Blocked: 1`, `Missing: 0`, and `Complete: false`.
- `bash scripts/run_local_acceptance.sh` exited 0 and refreshed release checks, quickstart, delivery bundle, and local acceptance outputs; it reported the expected final-stage blocker: Docker/Apptainer reproducibility.

Commit:
- hash: 9503b4a919c5e9682459e55d5c7eafae30df106d
- message: test: require figure gallery objective evidence
- files: objective audit rule, release/objective tests, history

Next:
- Continue final MVP hardening; Docker/Apptainer runtime verification remains intentionally deferred to the final packaging stage.

## 2026-06-27 - Surface WGD publication audit in delivery outputs

Timestamp:
- 2026-06-27 04:23 CST

Context:
- The release gate already produced both the standard `publication report audit` and the `WGD publication report audit`.
- The final delivery bundle, README, quickstart, release audit, and local acceptance summary still emphasized only the standard publication audit, so a user inspecting delivery outputs could miss the WGD/evolution report closure.

Decisions:
- Add `wgd_publication_report_audit` to the delivery manifest and Markdown bundle as a first-class status item.
- Update local acceptance so it extracts and records both standard and WGD publication audit statuses.
- Update user-facing docs to point at both audit reports and to describe WGD report closure as Ka/Ks/WGD figure interpretation plus gamma beta alpha theta evidence.

Added:
- Delivery bundle status row for `results/publication_report_audit/wgd_publication_report_audit.md`.
- Local acceptance row for `wgd_publication_report_audit`.
- Quickstart and release-audit documentation for WGD publication report audit paths.

Modified:
- `HISTORY.md`
- `README.md`
- `bin/genefam/run_delivery_bundle.py`
- `bin/genefam/write_local_acceptance_summary.py`
- `docs/quickstart.md`
- `docs/release_audit.md`
- `scripts/run_local_acceptance.sh`
- `tests/test_local_acceptance_script.py`
- `tests/test_quickstart_docs.py`
- `tests/test_release_audit_docs.py`
- `tests/test_run_delivery_bundle.py`
- `tests/test_write_local_acceptance_summary.py`

Deleted:
- none

Verification:
- `python -m pytest tests/test_run_delivery_bundle.py::test_run_delivery_bundle_cli_writes_user_facing_index -q` first failed because the delivery bundle did not include `wgd_publication_report_audit`.
- `python -m pytest tests/test_release_audit_docs.py -q` first failed because `docs/release_audit.md` did not document the WGD publication report audit paths.
- `python -m pytest tests/test_quickstart_docs.py::test_quickstart_documents_minimum_verified_run_path -q` first failed because `docs/quickstart.md` did not mention the WGD publication report audit.
- `python -m pytest tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py::test_local_acceptance_script_runs_release_gate_and_quickstart -q` first failed because local acceptance did not accept or extract `wgd_publication_status`.
- `python -m pytest tests/test_release_audit_docs.py tests/test_quickstart_docs.py tests/test_run_delivery_bundle.py tests/test_write_local_acceptance_summary.py tests/test_local_acceptance_script.py -q` passed with 8 tests after implementation.
- `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle` passed and wrote a delivery manifest row for `wgd_publication_report_audit`.
- `python -m pytest tests -q` passed with 367 tests.
- `python bin/genefam/run_release_checks.py --outdir results/release_checks` exited 0 and reported `Passed: 45`, `Required failed: 0`, `Optional failed: 2`, `Release ready: true`; only optional Docker and Apptainer profile smokes failed because those runtimes are not installed.

Commit:
- hash: b1221cfc3ea59d62c61a58acb39dde9cd3b9980b
- message: feat: surface wgd publication audit in delivery
- files: delivery bundle, local acceptance, README/quickstart/release audit docs, tests, history

Next:
- Keep Docker/Apptainer runtime verification as the remaining final-stage external blocker; continue polishing Reference-level figure fidelity where useful.
