import subprocess
import sys
from pathlib import Path

from bin.genefam.audit_container_materials import audit_container_materials


def test_audit_container_materials_passes_repository_contracts():
    rows = audit_container_materials(
        dockerfile=Path("Dockerfile"),
        linux_env=Path("envs/GeneFamilyFlow.linux-64.conda.yaml"),
        nextflow_config=Path("workflows/nextflow.config"),
        dockerignore=Path(".dockerignore"),
    )

    assert {row["status"] for row in rows} == {"passed"}
    checks = {row["check"] for row in rows}
    assert checks == {
        "dockerfile_genefamilyflow_env",
        "dockerfile_usr_local_r",
        "linux_env_full_toolchain",
        "nextflow_container_profiles",
        "container_image_params",
        "dockerignore_build_context",
    }


def test_audit_container_materials_reports_missing_required_contract(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM scratch\n", encoding="utf-8")
    env = tmp_path / "GeneFamilyFlow.linux-64.conda.yaml"
    env.write_text("name: GeneFamilyFlow\ndependencies:\n  - python\n", encoding="utf-8")
    config = tmp_path / "nextflow.config"
    config.write_text("params.env_name = \"GeneFamilyFlow\"\n", encoding="utf-8")

    rows = audit_container_materials(
        dockerfile=dockerfile,
        linux_env=env,
        nextflow_config=config,
        dockerignore=tmp_path / ".dockerignore",
    )

    failed = {row["check"]: row for row in rows if row["status"] == "failed"}
    assert "dockerfile_genefamilyflow_env" in failed
    assert "linux_env_full_toolchain" in failed
    assert "nextflow_container_profiles" in failed
    assert "dockerignore_build_context" in failed
    assert "GeneFamilyFlow.linux-64.conda.yaml" in failed["dockerfile_genefamilyflow_env"]["note"]
    assert "jcvi" in failed["linux_env_full_toolchain"]["note"]
    assert "work/" in failed["dockerignore_build_context"]["note"]


def test_audit_container_materials_cli_writes_tsv_and_markdown(tmp_path):
    outdir = tmp_path / "container_materials"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_container_materials.py",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert (outdir / "container_materials.tsv").read_text(encoding="utf-8").startswith(
        "check\tstatus\tnote\n"
    )
    markdown = (outdir / "container_materials.md").read_text(encoding="utf-8")
    assert "# Container Materials Audit" in markdown
    assert "container_image_params" in markdown
