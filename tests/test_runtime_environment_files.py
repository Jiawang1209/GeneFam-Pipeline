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
    assert "params.use_hmmer = true" in config
    assert "params.use_diamond = true" in config


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
    assert "iqtree2" in text
    assert "meme" in text
    assert "results/handoff/handoff_report.md" in text
    assert "results/handoff/handoff_summary.tsv" in text
    assert "first file to inspect" in text


def test_input_contract_and_schema_document_identification_tool_flags():
    contract = Path("docs/input_contract.md").read_text(encoding="utf-8")
    schema = Path("schemas/config.schema.yaml").read_text(encoding="utf-8")

    for text in (contract, schema):
        assert "identification.use_hmmer" in text
        assert "identification.use_diamond" in text
        assert "at least one" in text


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
    assert "first file to inspect" in readme
    assert "run_release_checks.py" in readme


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
    assert "params.container_image" in readme
    assert "params.apptainer_image" in readme


def test_standard_to_wgd_handoff_doc_links_identification_and_wgd_branches():
    text = Path("docs/standard_to_wgd_handoff.md").read_text(encoding="utf-8")

    required_snippets = [
        "results/<run>/tables/family_candidates.tsv",
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
