import subprocess
import sys

from bin.genefam.audit_readiness import audit_commands, summarize_status


def test_audit_commands_marks_available_and_missing_commands():
    rows = audit_commands(
        required_commands=["nextflow", "/usr/local/bin/R", "mafft"],
        which=lambda command: f"/mock/bin/{command}" if command in {"nextflow", "/usr/local/bin/R"} else "",
    )

    assert rows == [
        {"command": "nextflow", "status": "available", "path": "/mock/bin/nextflow"},
        {"command": "/usr/local/bin/R", "status": "available", "path": "/mock/bin//usr/local/bin/R"},
        {"command": "mafft", "status": "missing", "path": ""},
    ]


def test_summarize_status_counts_missing_commands():
    rows = [
        {"command": "nextflow", "status": "available", "path": "/mock/bin/nextflow"},
        {"command": "docker", "status": "missing", "path": ""},
    ]

    assert summarize_status(rows) == {"available": 1, "missing": 1, "ready": False}


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
        "command\tstatus\tpath",
        f"{sys.executable}\tavailable\t{sys.executable}",
        "/definitely/not/a/real/genefam/tool\tmissing\t",
    ]
