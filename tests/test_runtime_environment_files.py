from pathlib import Path


def test_conda_environment_file_defines_genefamilyflow_runtime():
    environment = Path("envs/GeneFamilyFlow.conda.yaml")

    assert environment.exists()
    text = environment.read_text(encoding="utf-8")
    assert "name: GeneFamilyFlow" in text
    assert "bioconda" in text
    assert "openjdk" in text
    assert "nextflow" in text
    assert "hmmer" in text
    assert "diamond" in text
    assert "mafft" in text
    assert "iqtree" in text
    assert "r-base" in text
    assert "quarto" in text
    assert "\n  - jcvi\n" not in text
    assert "\n  - kaks_calculator\n" not in text


def test_linux_conda_environment_keeps_platform_limited_full_toolchain():
    environment = Path("envs/GeneFamilyFlow.linux-64.conda.yaml")

    assert environment.exists()
    text = environment.read_text(encoding="utf-8")
    assert "name: GeneFamilyFlow" in text
    assert "\n  - jcvi\n" in text
    assert "\n  - kaks_calculator\n" in text


def test_dockerfile_installs_genefamilyflow_and_exposes_usr_local_r():
    dockerfile = Path("Dockerfile")

    assert dockerfile.exists()
    text = dockerfile.read_text(encoding="utf-8")
    assert "GeneFamilyFlow.linux-64.conda.yaml" in text
    assert "GeneFamilyFlow" in text
    assert "/usr/local/bin/R" in text
    assert "micromamba" in text


def test_nextflow_config_has_container_profiles():
    config = Path("workflows/nextflow.config").read_text(encoding="utf-8")

    assert "profiles" in config
    assert "activated" in config
    assert "conda.enabled = false" in config
    assert "docker" in config
    assert "apptainer" in config
    assert "genefam-pipeline:latest" in config
    assert 'params.container_image = "genefam-pipeline:latest"' in config
    assert 'params.apptainer_image = "genefam-pipeline_latest.sif"' in config
    assert "process.container = params.container_image" in config
    assert "process.container = params.apptainer_image" in config
    assert 'params.meme_txt = "tests/fixtures/mock_evidence/meme.txt"' in config
    assert 'params.tree_builder = "fasttree"' in config
    assert "params.use_hmmer = true" in config
    assert "params.use_diamond = true" in config
    assert "params.run_promoter = false" in config
    assert "params.run_promoter_cis = false" in config
    assert "params.promoter_cis_elements = null" in config
    assert "params.promoter_upstream_bp = 2000" in config
    assert "params.promoter_downstream_bp = 0" in config
    assert "params.run_feature_summary = false" in config
    assert "params.run_mcscanx_circlize = false" in config
    assert "params.syntenic_pairs = null" in config
    assert "params.run_ppi = false" in config
    assert "params.ppi_edges = null" in config
    assert "params.ppi_nodes = null" in config
    assert "params.gene_family_species_order = null" in config
    assert "params.mcscanx_collinearity = null" in config
    assert "params.kaks_results = null" in config
    assert "params.mcscanx_cds_a = null" in config
    assert "params.mcscanx_cds_b = null" in config


def test_readiness_checklist_documents_command_audit():
    checklist = Path("docs/readiness_checklist.md")
    text = checklist.read_text(encoding="utf-8")

    assert (
        "python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv"
        in text
    )
    assert "python bin/genefam/run_release_checks.py --outdir results/release_checks" in text
    assert "python bin/genefam/plan_runtime_bootstrap.py" in text
    assert "nextflow" in text
    assert "/usr/local/bin/R" in text
    assert "mafft" in text
    assert "FastTree" in text
    assert "iqtree2" in text
    assert "meme" in text
    assert "results/handoff/handoff_report.md" in text
    assert "results/handoff/handoff_summary.tsv" in text
    assert "results/local_acceptance/local_acceptance_summary.md" in text
    assert "results/publication_report_audit/publication_report_audit.md" in text
    assert "publication_report_audit" in text
    assert "paper-style report closure" in text
    assert "valid plot file signatures" in text
    assert "registered-only figure interpretation scope" in text
    assert "plot manifest and interpretation output path consistency" in text
    assert "complete per-figure close-reading text" in text
    assert "QC tables and warnings" in text
    assert "software/R package versions" in text
    assert "per-figure method/software version coverage" in text
    assert "reproducibility commands" in text
    assert "results/delivery_bundle/delivery_manifest.tsv" in text
    assert "results/delivery_bundle/delivery_bundle.md" in text
    assert "runtime recovery" in text
    assert "results/readiness/runtime_bootstrap_plan.md" in text
    assert "results/readiness/runtime_bootstrap.sh" in text
    assert "optional container-stage commands" in text
    assert "required core analysis commands" in text
    assert 'docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest' in text
    assert "results/container_default_smoke" in text
    assert "scripts/run_local_acceptance.sh" in text
    assert "first file to inspect" in text


def test_input_contract_and_schema_document_identification_tool_flags():
    contract = Path("docs/input_contract.md").read_text(encoding="utf-8")
    schema = Path("schemas/config.schema.yaml").read_text(encoding="utf-8")

    for text in (contract, schema):
        assert "identification.use_hmmer" in text
        assert "identification.use_diamond" in text
        assert "at least one" in text
        assert "wgd_events.event_map" in text
        assert "modules.ppi" in text
        assert "ppi.edges" in text
        assert "modules.promoter_cis" in text
        assert "promoter.cis_elements" in text
        assert "duplicate WGD event names" in text
        assert "wgd_events.named_event_annotation requires modules.duplication_retention" in text


def test_runtime_environment_docs_use_conda_env_aware_audit_and_linux_file():
    text = Path("docs/runtime_environment.md").read_text(encoding="utf-8")

    assert "python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv" in text
    assert "GeneFamilyFlow.linux-64.conda.yaml" in text
    assert "python bin/genefam/audit_container_materials.py" in text
    assert "results/container_materials/container_materials.tsv" in text
    assert "results/container_materials/container_materials.md" in text
    assert "python bin/genefam/run_container_profile_smoke.py --profile docker" in text
    assert "python bin/genefam/run_container_profile_smoke.py --profile apptainer" in text
    assert "results/container_profile_smoke/docker/container_profile_smoke.md" in text
    assert "results/container_profile_smoke/apptainer/container_profile_smoke.md" in text
    assert "results/container_default_smoke" in text
    assert "run_standard_smoke.py" in text
    assert 'docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest' in text
    assert "scripts/run_local_acceptance.sh" in text
    assert "results/delivery_bundle/delivery_bundle.md" in text


def test_advanced_module_examples_document_safe_enablement():
    text = Path("docs/advanced_module_examples.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "configs/advanced_modules.example.yaml" in text
    assert "python bin/genefam/validate_config.py configs/advanced_modules.example.yaml" in text
    assert "python bin/genefam/build_run_plan.py" in text
    assert "wgd_events.named_event_annotation: true" in text
    assert "configs/advanced_modules.example.yaml" in readme
    assert "docs/advanced_module_examples.md" in readme


def test_readme_documents_explicit_standard_identification_branch():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Standard Identification Branch" in readme
    assert "--run_identification true" in readme
    assert "HMMER and DIAMOND input tables" in readme
    assert "family_members.faa" in readme
    assert "motif_summary.tsv" in readme
    assert "chromosome_locations.tsv" in readme
    assert "family_expression" in readme
    assert "--expression-matrix" in readme
    assert "standard report index" in readme
    assert "final_report.md" in readme
    assert "run_standard_smoke.py" in readme
    assert "run_wgd_smoke.py" in readme
    assert "run_nextflow_smoke.py" in readme
    assert "docs/standard_to_wgd_handoff.md" in readme


def test_readme_points_to_final_handoff_report():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "results/handoff/handoff_report.md" in readme
    assert "results/handoff/handoff_summary.tsv" in readme
    assert "results/local_acceptance/local_acceptance_summary.md" in readme
    assert "results/publication_report_audit/publication_report_audit.md" in readme
    assert "release, quickstart, publication-report audit, and delivery-bundle steps" in readme
    assert "paper-style report closure" in readme
    assert "valid plot file signatures" in readme
    assert "registered-only figure interpretation scope" in readme
    assert "plot manifest and interpretation output path consistency" in readme
    assert "complete per-figure close-reading text" in readme
    assert "QC tables and warnings" in readme
    assert "software/R package versions" in readme
    assert "per-figure method/software version coverage" in readme
    assert "reproducibility commands" in readme
    assert "final_stage_blocker" in readme
    assert "container_default_smoke" in readme
    assert "Dockerfile -> results/container_default_smoke" in readme
    assert "first file to inspect" in readme
    assert "run_release_checks.py" in readme


def test_chinese_readme_points_to_publication_audit_acceptance():
    readme = Path("README.zh-CN.md").read_text(encoding="utf-8")

    assert "bash scripts/run_local_acceptance.sh" in readme
    assert "results/local_acceptance/local_acceptance_summary.md" in readme
    assert "results/publication_report_audit/publication_report_audit.md" in readme
    assert "论文级报告闭环检查" in readme
    assert "每张图的结果精读" in readme
    assert "方法、软件和 R 包版本" in readme
    assert "可复现命令" in readme


def test_readiness_checklist_points_to_local_acceptance_summary():
    text = Path("docs/readiness_checklist.md").read_text(encoding="utf-8")

    assert "results/local_acceptance/local_acceptance_summary.md" in text
    assert "local acceptance" in text
    assert "container_default_smoke" in text
    assert "Dockerfile -> results/container_default_smoke" in text


def test_readme_current_status_matches_release_evidence():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Full external-tool workflow wiring is still under development" not in readme
    assert "Current Status" in readme
    assert "repository-ready but runtime-blocked" in readme
    assert "Docker/Apptainer reproducibility" in readme
    assert "standard identification branch" in readme
    assert "prepared-table WGD branch" in readme
    assert "results/handoff/handoff_summary.tsv" in readme
    assert "run_nextflow_single_tool_smoke.py" in readme
    assert "bash results/readiness/runtime_bootstrap.sh" in readme
    assert "runtime recovery" in readme
    assert "scripts/run_local_acceptance.sh" in readme
    assert 'docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest' in readme
    assert "params.container_image" in readme
    assert "params.apptainer_image" in readme


def test_standard_to_wgd_handoff_doc_links_identification_and_wgd_branches():
    text = Path("docs/standard_to_wgd_handoff.md").read_text(encoding="utf-8")

    required_snippets = [
        "results/<run>/tables/family_candidates.tsv",
        "results/<run>/tables/wgd_handoff_manifest.tsv",
        "--run_identification true",
        "--run_duplication_retention true",
        "--duplicates path/to/duplicate_types.tsv",
        "--family_members results/<run>/tables/family_candidates.tsv",
        "--kaks_pairs path/to/kaks_pairs.tsv",
        "gene_id",
        "duplicate_type",
        "gene_a",
        "gene_b",
        "ks",
        "wgd_event_evidence.tsv",
        "family_event_retention_summary.tsv",
        "retention_enrichment.tsv",
        "gamma",
        "beta",
        "alpha",
        "theta",
        "python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke",
    ]
    for snippet in required_snippets:
        assert snippet in text
