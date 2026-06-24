# Release Audit

This document maps the original GeneFam-Pipeline goal to current repository evidence, verification commands, and known gaps.

## Verification Commands

Repository-level checks:

```bash
python bin/genefam/run_release_checks.py --outdir results/release_checks
python -m pytest tests -q
python bin/genefam/validate_config.py configs/example.config.yaml
python bin/genefam/validate_config.py configs/advanced_modules.example.yaml
python bin/genefam/run_mock_mvp.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/mock_mvp
python bin/genefam/run_standard_smoke.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/standard_smoke
python bin/genefam/run_wgd_smoke.py \
  --events-config configs/wgd_events.brassicaceae.yaml \
  --outdir results/wgd_smoke
python bin/genefam/run_nextflow_smoke.py --outdir results/nextflow_smoke
python bin/genefam/run_nextflow_wgd_smoke.py --outdir results/nextflow_wgd_smoke
python bin/genefam/run_prepared_wgd_handoff_example.py \
  --conda-env GeneFamilyFlow \
  --example-dir examples/prepared_wgd_handoff \
  --outdir results/example_prepared_wgd
PATH="/Users/liuyue/miniforge3/envs/GeneFamilyFlow/bin:$PATH" nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile activated \
  --config configs/example.config.yaml \
  --run_duplication_retention true \
  --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv \
  --family_members examples/prepared_wgd_handoff/family_candidates.tsv \
  --kaks_pairs examples/prepared_wgd_handoff/kaks_pairs.tsv \
  --events_config configs/wgd_events.brassicaceae.yaml \
  --ks_bins 0.3,0.8,1.5 \
  --wgd_event_args "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta" \
  --outdir results/example_prepared_wgd
python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv
python bin/genefam/plan_runtime_bootstrap.py \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/readiness
```

The readiness audit may exit non-zero when runtime commands are missing; inspect the TSV for exact missing tools and use the bootstrap planner to generate next-step commands.

The release checks runner writes:

- `results/release_checks/release_checks.tsv`
- `results/release_checks/release_checks.md`
- `results/readiness/runtime_bootstrap_plan.md`
- `results/readiness/runtime_bootstrap.sh`

## Requirement Audit

| Requirement | Evidence | Verification |
|---|---|---|
| Nextflow DSL2 workflow | `workflows/main.nf`; modules under `workflows/modules/`; `bin/genefam/run_nextflow_smoke.py`; `results/nextflow_smoke/nextflow_smoke.md` | `python -m pytest tests/test_workflow_modules.py tests/test_run_nextflow_smoke.py -q` |
| YAML-driven parameters | `configs/example.config.yaml`; `configs/advanced_modules.example.yaml`; `bin/genefam/build_run_plan.py` | `python bin/genefam/build_run_plan.py --config configs/example.config.yaml --out results/mock_mvp/tables/run_plan.tsv` |
| GeneFamilyFlow runtime | `envs/GeneFamilyFlow.conda.yaml`; `workflows/nextflow.config`; `Dockerfile` | `python -m pytest tests/test_runtime_environment_files.py -q` |
| `/usr/local/bin/R` plotting and reporting convention | `workflows/modules/plots.nf`; `scripts/plot_family_counts.R`; `scripts/plot_kaks.R`; `scripts/plot_expression_heatmap.R` | `python -m pytest tests/test_workflow_modules.py tests/test_runtime_environment_files.py -q` |
| Docker/Conda reproducible running | `Dockerfile`; `envs/GeneFamilyFlow.conda.yaml`; `bin/genefam/plan_runtime_bootstrap.py`; `workflows/nextflow.config` profiles `local`, `docker`, `apptainer` | `python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv` and `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` |
| species bank input model | `docs/input_contract.md`; `bin/genefam/discover_species.py`; `tests/fixtures/species_bank` | `python -m pytest tests/test_discover_species.py -q` |
| target species selection | `configs/species_groups.yaml`; `species.include`; `species.exclude`; `run.species_group` | `python -m pytest tests/test_discover_species.py tests/test_build_run_plan.py -q` |
| standard identification branch | `workflows/main.nf`; `workflows/modules/identification_inputs.nf`; `workflows/modules/standard_postprocess.nf`; `workflows/modules/annotation_integration.nf`; `bin/genefam/build_identification_inputs.py`; `bin/genefam/extract_family_sequences.py`; `bin/genefam/extract_chromosome_locations.py`; `bin/genefam/subset_expression_matrix.py`; `bin/genefam/build_standard_report_index.py`; `bin/genefam/assemble_report.py`; `bin/genefam/run_standard_smoke.py`; `bin/genefam/concat_tsv.py`; `results/standard_smoke/tables/chromosome_locations.tsv`; `results/standard_smoke/report/final_report.md` | `python -m pytest tests/test_build_identification_inputs.py tests/test_concat_tsv.py tests/test_extract_family_sequences.py tests/test_extract_chromosome_locations.py tests/test_subset_expression_matrix.py tests/test_standard_branch_report_index.py tests/test_assemble_report.py tests/test_run_standard_smoke.py tests/test_workflow_modules.py -q` |
| HMMER family identification | `workflows/modules/hmmer_search.nf`; `bin/genefam/parse_hmmer_domtbl.py`; `bin/genefam/filter_hmmer_domains.py` | `python -m pytest tests/test_parse_hmmer_domtbl.py tests/test_filter_hmmer_domains.py -q` |
| DIAMOND confirmation | `workflows/modules/diamond_search.nf`; `bin/genefam/parse_diamond_outfmt6.py` | `python -m pytest tests/test_parse_diamond_outfmt6.py -q` |
| domain filtering | `bin/genefam/filter_hmmer_domains.py`; `workflows/modules/domain_filter.nf` | `python -m pytest tests/test_filter_hmmer_domains.py tests/test_merge_identification_evidence.py -q` |
| family member summary | `bin/genefam/summarize_family.py`; `workflows/modules/family_summary.nf` | `python -m pytest tests/test_summarize_family.py -q` |
| alignment | `bin/genefam/prepare_alignment_inputs.py`; `workflows/modules/alignment_phylogeny.nf` | `python -m pytest tests/test_prepare_alignment_inputs.py tests/test_workflow_modules.py -q` |
| phylogeny | `bin/genefam/prepare_phylogeny_inputs.py`; `workflows/modules/alignment_phylogeny.nf` | `python -m pytest tests/test_prepare_phylogeny_inputs.py tests/test_workflow_modules.py -q` |
| motif | `bin/genefam/parse_meme_motifs.py`; `workflows/modules/alignment_phylogeny.nf` | `python -m pytest tests/test_parse_meme_motifs.py tests/test_workflow_modules.py -q` |
| synteny | `bin/genefam/parse_mcscanx_collinearity.py`; `workflows/modules/duplication_retention.nf` prepared-table branch | `python -m pytest tests/test_parse_mcscanx_collinearity.py tests/test_workflow_modules.py -q` |
| standard-to-WGD prepared handoff | `bin/genefam/run_prepared_wgd_handoff_example.py`; `docs/standard_to_wgd_handoff.md`; `examples/prepared_wgd_handoff/`; `examples/prepared_wgd_handoff/family_candidates.tsv`; `examples/prepared_wgd_handoff/duplicate_types.tsv`; `examples/prepared_wgd_handoff/kaks_pairs.tsv`; `results/example_prepared_wgd/report/final_report.md` | `python -m pytest tests/test_prepared_wgd_handoff_example.py -q`, `python bin/genefam/run_prepared_wgd_handoff_example.py --conda-env GeneFamilyFlow --example-dir examples/prepared_wgd_handoff --outdir results/example_prepared_wgd`, and the `--run_duplication_retention true` Nextflow command above |
| duplication retention | `bin/genefam/normalize_duplicate_types.py`; `bin/genefam/join_family_duplicates.py`; `bin/genefam/retention_enrichment.py` | `python -m pytest tests/test_normalize_duplicate_types.py tests/test_join_family_duplicates.py tests/test_retention_enrichment.py -q` |
| WGD layer and named event model | `bin/genefam/classify_wgd_layers.py`; `bin/genefam/build_wgd_event_evidence.py`; `bin/genefam/run_wgd_smoke.py`; `configs/wgd_events.brassicaceae.yaml`; `results/wgd_smoke/report/final_report.md` | `python -m pytest tests/test_classify_wgd_layers.py tests/test_build_wgd_event_evidence.py tests/test_run_wgd_smoke.py -q` |
| gamma beta alpha theta interpretation | `configs/wgd_events.brassicaceae.yaml`; `docs/wgd_event_evidence.md`; `docs/duplication_retention_design.md` | `python -m pytest tests/test_build_wgd_event_evidence.py -q` |
| Ka/Ks selection pressure | `bin/genefam/prepare_kaks_pairs.py`; `bin/genefam/parse_kaks_results.py`; `workflows/modules/duplication_retention.nf` | `python -m pytest tests/test_prepare_kaks_pairs.py tests/test_parse_kaks_results.py -q` |
| chromosome location | `bin/genefam/extract_chromosome_locations.py`; `workflows/modules/annotation_integration.nf` | `python -m pytest tests/test_extract_chromosome_locations.py tests/test_workflow_modules.py -q` |
| expression integration | `bin/genefam/subset_expression_matrix.py`; `workflows/modules/annotation_integration.nf`; `workflows/modules/plots.nf` | `python -m pytest tests/test_subset_expression_matrix.py tests/test_workflow_modules.py -q` |
| final report | `bin/genefam/assemble_report.py`; `workflows/modules/report.nf`; `results/mock_mvp/report/final_report.md` | `python -m pytest tests/test_assemble_report.py tests/test_run_mock_mvp.py -q` |
| HISTORY.md development diary | `HISTORY.md` records dated development entries and commit hashes | `git log --oneline -6` and inspect `HISTORY.md` |
| Reference/ read-only source material | `.dockerignore`; `docs/input_contract.md`; `README.md`; untracked `Reference/` files are not staged | `git status --short --untracked-files=all` |

## Known Gap

The repository-level implementation and tests are in place, but this machine does not currently prove full end-to-end runtime execution.

Recent readiness audits found:

- available: `conda`, `/usr/local/bin/R`
- available inside `GeneFamilyFlow`: `nextflow`, `hmmsearch`, `diamond`, `mafft`, `iqtree2` via `iqtree`, `meme`
- missing: `docker`, `apptainer`

This means:

- Mock MVP and Python/R/report helpers can be validated locally.
- Full Nextflow mock-MVP execution now works through `GeneFamilyFlow` with the `activated` profile.
- Docker profile execution needs Docker plus the `genefam-pipeline:latest` image.
- Apptainer profile execution needs Apptainer and access to the Docker image.
- External HMMER, DIAMOND, MAFFT, IQ-TREE, MEME, and related bioinformatics commands are available through the local `GeneFamilyFlow` Conda environment; Linux/container-only helpers such as `jcvi` and `kaks_calculator` are kept in `envs/GeneFamilyFlow.linux-64.conda.yaml`.
- `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` writes a Markdown plan and shell script for the current machine gap.

## Release Decision

Current status is repository-ready but runtime-blocked on this machine.

Do not mark the full objective complete until at least one real runtime route is verified:

```bash
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml --mock_mvp true
```

and the explicit standard identification branch is verified:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_identification true
```

or:

```bash
docker build -t genefam-pipeline:latest .
nextflow run workflows/main.nf -c workflows/nextflow.config -profile docker --config configs/example.config.yaml --mock_mvp true
```

or an equivalent Apptainer run after the missing runtime commands are available.
