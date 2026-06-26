import subprocess
import sys

from bin.genefam.audit_readiness import DEFAULT_COMMANDS, audit_commands, summarize_status


def test_audit_commands_marks_available_and_missing_commands():
    rows = audit_commands(
        required_commands=["nextflow", "/usr/local/bin/R", "mafft"],
        which=lambda command: f"/mock/bin/{command}" if command in {"nextflow", "/usr/local/bin/R"} else "",
    )

    assert rows == [
        {"command": "nextflow", "status": "available", "path": "/mock/bin/nextflow", "requirement": "required"},
        {"command": "/usr/local/bin/R", "status": "available", "path": "/mock/bin//usr/local/bin/R", "requirement": "required"},
        {"command": "mafft", "status": "missing", "path": "", "requirement": "required"},
    ]


def test_audit_commands_can_mark_commands_available_inside_conda_env():
    rows = audit_commands(
        required_commands=["hmmsearch", "diamond"],
        which=lambda command: "",
        conda_env="GeneFamilyFlow",
        conda_which=lambda env_name, command: f"/envs/{env_name}/bin/{command}" if command == "hmmsearch" else "",
    )

    assert rows == [
        {
            "command": "hmmsearch",
            "status": "available_in_conda",
            "path": "GeneFamilyFlow:/envs/GeneFamilyFlow/bin/hmmsearch",
            "requirement": "required",
        },
        {"command": "diamond", "status": "missing", "path": "", "requirement": "required"},
    ]


def test_audit_commands_accepts_iqtree_alias_for_iqtree2():
    rows = audit_commands(
        required_commands=["iqtree2"],
        which=lambda command: "",
        conda_env="GeneFamilyFlow",
        conda_which=lambda env_name, command: "/envs/GeneFamilyFlow/bin/iqtree" if command == "iqtree" else "",
    )

    assert rows == [
        {
            "command": "iqtree2",
            "status": "available_in_conda",
            "path": "GeneFamilyFlow:/envs/GeneFamilyFlow/bin/iqtree",
            "requirement": "required",
        }
    ]


def test_default_readiness_commands_include_fasttree_default_builder():
    assert "FastTree" in DEFAULT_COMMANDS


def test_audit_commands_finds_fasttree_inside_conda_env():
    rows = audit_commands(
        required_commands=["FastTree"],
        which=lambda command: "",
        conda_env="GeneFamilyFlow",
        conda_which=lambda env_name, command: "/envs/GeneFamilyFlow/bin/FastTree" if command == "FastTree" else "",
    )

    assert rows == [
        {
            "command": "FastTree",
            "status": "available_in_conda",
            "path": "GeneFamilyFlow:/envs/GeneFamilyFlow/bin/FastTree",
            "requirement": "required",
        }
    ]


def test_summarize_status_counts_missing_commands():
    rows = [
        {"command": "nextflow", "status": "available", "path": "/mock/bin/nextflow", "requirement": "required"},
        {"command": "hmmsearch", "status": "available_in_conda", "path": "GeneFamilyFlow:/mock/bin/hmmsearch", "requirement": "required"},
        {"command": "docker", "status": "missing", "path": "", "requirement": "required"},
    ]

    assert summarize_status(rows) == {
        "available": 2,
        "missing": 1,
        "missing_required": 1,
        "missing_optional": 0,
        "ready": False,
    }


def test_default_container_commands_are_optional_and_do_not_block_readiness():
    rows = audit_commands(
        required_commands=["nextflow", "docker", "apptainer"],
        which=lambda command: "/mock/bin/nextflow" if command == "nextflow" else "",
    )

    assert rows == [
        {"command": "nextflow", "status": "available", "path": "/mock/bin/nextflow", "requirement": "required"},
        {"command": "docker", "status": "missing", "path": "", "requirement": "optional"},
        {"command": "apptainer", "status": "missing", "path": "", "requirement": "optional"},
    ]
    assert summarize_status(rows) == {
        "available": 1,
        "missing": 2,
        "missing_required": 0,
        "missing_optional": 2,
        "ready": True,
    }


def test_audit_readiness_cli_accepts_conda_env_argument(tmp_path):
    out_path = tmp_path / "readiness.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_readiness.py",
            "--command",
            sys.executable,
            "--conda-env",
            "GeneFamilyFlow",
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert out_path.read_text(encoding="utf-8").splitlines() == [
        "command\tstatus\tpath\trequirement",
        f"{sys.executable}\tavailable\t{sys.executable}\trequired",
    ]



def test_audit_readiness_cli_writes_tsv(tmp_path):
    out_path = tmp_path / "readiness.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_readiness.py",
            "--command",
            sys.executable,
            "--command",
            "/definitely/not/a/real/genefam/tool",
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert out_path.read_text(encoding="utf-8").splitlines() == [
        "command\tstatus\tpath\trequirement",
        f"{sys.executable}\tavailable\t{sys.executable}\trequired",
        "/definitely/not/a/real/genefam/tool\tmissing\t\trequired",
    ]
