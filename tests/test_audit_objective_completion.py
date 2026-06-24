import subprocess
import sys

from bin.genefam.audit_objective_completion import (
    build_objective_audit,
    summarize_objective_audit,
    write_markdown,
    write_tsv,
)


def _release_row(check, status="passed"):
    return {
        "check": check,
        "required": "true",
        "status": status,
        "exit_code": "0" if status == "passed" else "1",
        "command": check,
        "note": "",
    }


def _readiness_row(command, status="available_in_conda", path=None):
    return {
        "command": command,
        "status": status,
        "path": path or ("GeneFamilyFlow:/bin/" + command if status.startswith("available") else ""),
    }


def test_build_objective_audit_marks_goal_items_and_runtime_blockers():
    release_rows = [
        _release_row("pytest"),
        _release_row("validate example config"),
        _release_row("validate advanced config"),
        _release_row("mock MVP"),
        _release_row("standard branch smoke"),
        _release_row("synteny parser smoke"),
        _release_row("WGD event smoke"),
        _release_row("Nextflow mock MVP smoke"),
        _release_row("Nextflow standard branch smoke"),
        _release_row("Nextflow standard single-tool smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("readiness audit", status="failed"),
        _release_row("runtime bootstrap plan"),
        _release_row("container materials audit"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Nextflow DSL2 workflow"]["status"] == "achieved"
    assert by_requirement["YAML-driven species selection"]["status"] == "achieved"
    assert by_requirement["GeneFamilyFlow runtime"]["status"] == "achieved"
    assert by_requirement["Docker/Apptainer reproducibility"]["status"] == "blocked"
    assert "container materials audit" in by_requirement["Docker/Apptainer reproducibility"]["evidence"]
    assert "docker, apptainer" in by_requirement["Docker/Apptainer reproducibility"]["note"]
    assert by_requirement["WGD gamma beta alpha theta evidence"]["status"] == "achieved"
    assert by_requirement["quickstart handoff"]["status"] == "achieved"


def test_wgd_event_evidence_requires_synteny_parser_smoke():
    release_rows = [
        _release_row("WGD event smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["WGD gamma beta alpha theta evidence"]["status"] == "missing"
    assert "synteny parser smoke" in by_requirement["WGD gamma beta alpha theta evidence"]["evidence"]


def test_nextflow_dsl2_requires_single_tool_smoke_evidence():
    release_rows = [
        _release_row("Nextflow mock MVP smoke"),
        _release_row("Nextflow standard branch smoke"),
        _release_row("Nextflow WGD event smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Nextflow DSL2 workflow"]["status"] == "missing"
    assert "single-tool" in by_requirement["Nextflow DSL2 workflow"]["note"]


def test_summarize_objective_audit_counts_statuses():
    rows = [
        {"requirement": "A", "status": "achieved", "evidence": "", "note": ""},
        {"requirement": "B", "status": "blocked", "evidence": "", "note": ""},
        {"requirement": "C", "status": "missing", "evidence": "", "note": ""},
    ]

    assert summarize_objective_audit(rows) == {
        "achieved": 1,
        "blocked": 1,
        "missing": 1,
        "complete": False,
    }


def test_write_objective_audit_outputs(tmp_path):
    rows = [
        {
            "requirement": "Docker/Apptainer reproducibility",
            "status": "blocked",
            "evidence": "readiness audit",
            "note": "missing docker, apptainer",
        }
    ]

    write_tsv(rows, tmp_path / "objective_audit.tsv")
    write_markdown(rows, tmp_path / "objective_audit.md")

    assert (tmp_path / "objective_audit.tsv").read_text(encoding="utf-8").startswith(
        "requirement\tstatus\tevidence\tnote\n"
    )
    markdown = (tmp_path / "objective_audit.md").read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Objective Audit" in markdown
    assert "Docker/Apptainer reproducibility" in markdown
    assert "Complete: false" in markdown


def test_audit_objective_completion_cli_writes_outputs(tmp_path):
    release = tmp_path / "release_checks.tsv"
    release.write_text(
        "check\trequired\tstatus\texit_code\tcommand\tnote\n"
        "pytest\ttrue\tpassed\t0\tpytest\t\n"
        "validate example config\ttrue\tpassed\t0\tvalidate\t\n"
        "validate advanced config\ttrue\tpassed\t0\tvalidate\t\n"
        "standard branch smoke\ttrue\tpassed\t0\tstandard\t\n"
        "synteny parser smoke\ttrue\tpassed\t0\tsynteny\t\n"
        "WGD event smoke\ttrue\tpassed\t0\twgd\t\n"
        "Nextflow mock MVP smoke\ttrue\tpassed\t0\tnextflow\t\n"
        "Nextflow standard branch smoke\ttrue\tpassed\t0\tnextflow\t\n"
        "Nextflow standard single-tool smoke\ttrue\tpassed\t0\tnextflow\t\n"
        "Nextflow WGD event smoke\ttrue\tpassed\t0\tnextflow\t\n"
        "prepared WGD handoff example\ttrue\tpassed\t0\tprepared\t\n"
        "quickstart handoff\ttrue\tpassed\t0\tquickstart\t\n"
        "readiness audit\ttrue\tfailed\t1\treadiness\t\n",
        encoding="utf-8",
    )
    readiness = tmp_path / "command_readiness.tsv"
    readiness.write_text(
        "command\tstatus\tpath\n"
        "nextflow\tavailable_in_conda\tGeneFamilyFlow:/bin/nextflow\n"
        "/usr/local/bin/R\tavailable\t/usr/local/bin/R\n"
        "hmmsearch\tavailable_in_conda\tGeneFamilyFlow:/bin/hmmsearch\n"
        "diamond\tavailable_in_conda\tGeneFamilyFlow:/bin/diamond\n"
        "mafft\tavailable_in_conda\tGeneFamilyFlow:/bin/mafft\n"
        "iqtree2\tavailable_in_conda\tGeneFamilyFlow:/bin/iqtree\n"
        "meme\tavailable_in_conda\tGeneFamilyFlow:/bin/meme\n"
        "docker\tmissing\t\n"
        "apptainer\tmissing\t\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "objective"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_objective_completion.py",
            "--release-checks",
            str(release),
            "--readiness",
            str(readiness),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Docker/Apptainer reproducibility\tblocked" in (
        outdir / "objective_audit.tsv"
    ).read_text(encoding="utf-8")
    assert "Complete: false" in (outdir / "objective_audit.md").read_text(encoding="utf-8")
