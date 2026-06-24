import subprocess
import sys

from bin.genefam.build_handoff_report import (
    build_handoff_sections,
    read_tsv,
    write_markdown,
)


def test_build_handoff_sections_summarizes_release_objective_and_runtime_state(tmp_path):
    release = tmp_path / "release_checks.tsv"
    release.write_text(
        "check\trequired\tstatus\texit_code\tcommand\tnote\n"
        "pytest\ttrue\tpassed\t0\tpytest\t\n"
        "readiness audit\ttrue\tfailed\t1\treadiness\t\n"
        "Docker profile smoke\tfalse\tfailed\t1\tdocker smoke\tmissing docker\n",
        encoding="utf-8",
    )
    objective = tmp_path / "objective_audit.tsv"
    objective.write_text(
        "requirement\tstatus\tevidence\tnote\n"
        "Nextflow DSL2 workflow\tachieved\tchecks\tok\n"
        "Docker/Apptainer reproducibility\tblocked\treadiness\tMissing container commands: docker, apptainer\n",
        encoding="utf-8",
    )
    readiness = tmp_path / "command_readiness.tsv"
    readiness.write_text(
        "command\tstatus\tpath\n"
        "nextflow\tavailable_in_conda\tGeneFamilyFlow:/bin/nextflow\n"
        "docker\tmissing\t\n"
        "apptainer\tmissing\t\n",
        encoding="utf-8",
    )
    docker_smoke = tmp_path / "docker_smoke.tsv"
    docker_smoke.write_text(
        "check\tprofile\tstatus\texit_code\tcommand\tnote\n"
        "docker_profile_smoke\tdocker\tmissing_runtime\t127\tnextflow run\tmissing docker\n",
        encoding="utf-8",
    )

    sections = build_handoff_sections(
        release_rows=read_tsv(release),
        objective_rows=read_tsv(objective),
        readiness_rows=read_tsv(readiness),
        container_rows=read_tsv(docker_smoke),
    )

    assert sections["release"] == "passed=1 failed=2 required_failed=1 optional_failed=1 release_ready=false"
    assert sections["objective"] == "achieved=1 blocked=1 missing=0 complete=false"
    assert sections["available_runtime"] == "nextflow"
    assert sections["missing_runtime"] == "docker, apptainer"
    assert sections["container_smoke"] == "docker=missing_runtime"


def test_write_handoff_markdown_contains_copyable_next_steps(tmp_path):
    out = tmp_path / "handoff_report.md"
    sections = {
        "release": "passed=12 failed=3 required_failed=1 optional_failed=2 release_ready=false",
        "objective": "achieved=11 blocked=1 missing=0 complete=false",
        "available_runtime": "nextflow, /usr/local/bin/R, hmmsearch",
        "missing_runtime": "docker, apptainer",
        "container_smoke": "docker=missing_runtime; apptainer=missing_runtime",
    }

    write_markdown(sections, out)

    text = out.read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Handoff Report" in text
    assert "release_ready=false" in text
    assert "Available runtime commands" in text
    assert "nextflow, /usr/local/bin/R, hmmsearch" in text
    assert "docker, apptainer" in text
    assert "python bin/genefam/run_release_checks.py --outdir results/release_checks" in text
    assert "results/objective_audit/objective_audit.md" in text


def test_build_handoff_report_cli_writes_markdown(tmp_path):
    release = tmp_path / "release_checks.tsv"
    release.write_text(
        "check\trequired\tstatus\texit_code\tcommand\tnote\n"
        "pytest\ttrue\tpassed\t0\tpytest\t\n",
        encoding="utf-8",
    )
    objective = tmp_path / "objective_audit.tsv"
    objective.write_text("requirement\tstatus\tevidence\tnote\nNextflow\tachieved\tchecks\tok\n", encoding="utf-8")
    readiness = tmp_path / "readiness.tsv"
    readiness.write_text("command\tstatus\tpath\ndocker\tmissing\t\n", encoding="utf-8")
    out = tmp_path / "handoff_report.md"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_handoff_report.py",
            "--release-checks",
            str(release),
            "--objective-audit",
            str(objective),
            "--readiness",
            str(readiness),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "GeneFam-Pipeline Handoff Report" in out.read_text(encoding="utf-8")
