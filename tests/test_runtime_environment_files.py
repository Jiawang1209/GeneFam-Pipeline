from pathlib import Path


def test_conda_environment_file_defines_genefamilyflow_runtime():
    environment = Path("envs/GeneFamilyFlow.conda.yaml")

    assert environment.exists()
    text = environment.read_text(encoding="utf-8")
    assert "name: GeneFamilyFlow" in text
    assert "bioconda" in text
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
