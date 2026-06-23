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


def test_dockerfile_installs_genefamilyflow_and_exposes_usr_local_r():
    dockerfile = Path("Dockerfile")

    assert dockerfile.exists()
    text = dockerfile.read_text(encoding="utf-8")
    assert "GeneFamilyFlow.conda.yaml" in text
    assert "GeneFamilyFlow" in text
    assert "/usr/local/bin/R" in text
    assert "micromamba" in text


def test_nextflow_config_has_container_profiles():
    config = Path("workflows/nextflow.config").read_text(encoding="utf-8")

    assert "profiles" in config
    assert "docker" in config
    assert "apptainer" in config
    assert "genefam-pipeline:latest" in config


def test_readiness_checklist_documents_command_audit():
    checklist = Path("docs/readiness_checklist.md")
    text = checklist.read_text(encoding="utf-8")

    assert "python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv" in text
    assert "python bin/genefam/run_release_checks.py --outdir results/release_checks" in text
    assert "python bin/genefam/plan_runtime_bootstrap.py" in text
    assert "nextflow" in text
    assert "/usr/local/bin/R" in text
    assert "mafft" in text
    assert "iqtree2" in text
    assert "meme" in text


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
    assert "standard report index" in readme
    assert "final_report.md" in readme
