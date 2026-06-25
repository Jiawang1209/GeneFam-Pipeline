import subprocess
import sys

from bin.genefam.build_handoff_report import (
    build_handoff_sections,
    read_tsv,
    write_markdown,
    write_summary_tsv,
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
    assert sections["blocked_requirements"] == "Docker/Apptainer reproducibility"
    assert (
        sections["next_unblock_artifacts"]
        == "results/readiness/runtime_bootstrap_plan.md, results/readiness/runtime_bootstrap.sh"
    )
    assert sections["next_unblock_command"] == "bash results/readiness/runtime_bootstrap.sh"
    assert sections["available_runtime"] == "nextflow"
    assert sections["missing_runtime"] == "docker, apptainer"
    assert sections["container_smoke"] == "docker=missing_runtime"


def test_write_handoff_markdown_contains_copyable_next_steps(tmp_path):
    out = tmp_path / "handoff_report.md"
    sections = {
        "release": "passed=12 failed=3 required_failed=1 optional_failed=2 release_ready=false",
        "objective": "achieved=11 blocked=1 missing=0 complete=false",
        "blocked_requirements": "Docker/Apptainer reproducibility",
        "next_unblock_artifacts": "results/readiness/runtime_bootstrap_plan.md, results/readiness/runtime_bootstrap.sh",
        "next_unblock_command": "bash results/readiness/runtime_bootstrap.sh",
        "available_runtime": "nextflow, /usr/local/bin/R, hmmsearch",
        "missing_runtime": "docker, apptainer",
        "container_smoke": "docker=missing_runtime; apptainer=missing_runtime",
    }

    write_markdown(sections, out)

    text = out.read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Handoff Report" in text
    assert "release_ready=false" in text
    assert "Available runtime commands" in text
    assert "Blocked requirements" in text
    assert "Docker/Apptainer reproducibility" in text
    assert "Unblock artifacts" in text
    assert "results/readiness/runtime_bootstrap_plan.md" in text
    assert "results/readiness/runtime_bootstrap.sh" in text
    assert "Next unblock command" in text
    assert "bash results/readiness/runtime_bootstrap.sh" in text
    next_command = text.split("## Next Command", 1)[1]
    assert "bash results/readiness/runtime_bootstrap.sh" in next_command
    assert "python bin/genefam/run_release_checks.py --outdir results/release_checks" not in next_command
    assert "nextflow, /usr/local/bin/R, hmmsearch" in text
    assert "docker, apptainer" in text
    assert "results/objective_audit/objective_audit.md" in text
    assert "results/local_acceptance/local_acceptance_summary.md" in text
    assert "results/delivery_bundle/delivery_manifest.tsv" in text
    assert "results/delivery_bundle/delivery_bundle.md" in text
    assert "Dockerfile" in text
    assert "results/container_default_smoke" in text


def test_write_handoff_markdown_uses_release_gate_when_no_unblock_command(tmp_path):
    out = tmp_path / "handoff_report.md"
    sections = {
        "release": "passed=15 failed=0 required_failed=0 optional_failed=0 release_ready=true",
        "objective": "achieved=12 blocked=0 missing=0 complete=true",
        "blocked_requirements": "none",
        "next_unblock_artifacts": "none",
        "next_unblock_command": "none",
        "available_runtime": "nextflow, docker, apptainer",
        "missing_runtime": "none",
        "container_smoke": "docker=passed; apptainer=passed",
    }

    write_markdown(sections, out)

    next_command = out.read_text(encoding="utf-8").split("## Next Command", 1)[1]
    assert "python bin/genefam/run_release_checks.py --outdir results/release_checks" in next_command
    assert "bash results/readiness/runtime_bootstrap.sh" not in next_command


def test_write_handoff_summary_tsv_contains_stable_keys(tmp_path):
    out = tmp_path / "handoff_summary.tsv"
    sections = {
        "release": "passed=12 failed=3 required_failed=1 optional_failed=2 release_ready=false",
        "objective": "achieved=11 blocked=1 missing=0 complete=false",
        "blocked_requirements": "Docker/Apptainer reproducibility",
        "next_unblock_artifacts": "results/readiness/runtime_bootstrap_plan.md, results/readiness/runtime_bootstrap.sh",
        "next_unblock_command": "bash results/readiness/runtime_bootstrap.sh",
        "available_runtime": "nextflow, /usr/local/bin/R, hmmsearch",
        "missing_runtime": "docker, apptainer",
        "container_smoke": "docker=missing_runtime; apptainer=missing_runtime",
    }

    write_summary_tsv(sections, out)

    rows = read_tsv(out)
    assert rows == [
        {
            "section": "release",
            "summary": "passed=12 failed=3 required_failed=1 optional_failed=2 release_ready=false",
        },
        {"section": "objective", "summary": "achieved=11 blocked=1 missing=0 complete=false"},
        {"section": "blocked_requirements", "summary": "Docker/Apptainer reproducibility"},
        {
            "section": "next_unblock_artifacts",
            "summary": "results/readiness/runtime_bootstrap_plan.md, results/readiness/runtime_bootstrap.sh",
        },
        {"section": "next_unblock_command", "summary": "bash results/readiness/runtime_bootstrap.sh"},
        {"section": "available_runtime", "summary": "nextflow, /usr/local/bin/R, hmmsearch"},
        {"section": "missing_runtime", "summary": "docker, apptainer"},
        {"section": "container_smoke", "summary": "docker=missing_runtime; apptainer=missing_runtime"},
    ]


def test_build_handoff_report_cli_writes_markdown_and_summary_tsv(tmp_path):
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
    summary_tsv = tmp_path / "handoff_summary.tsv"

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
            "--summary-tsv",
            str(summary_tsv),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "GeneFam-Pipeline Handoff Report" in out.read_text(encoding="utf-8")
    assert "missing_runtime\tdocker" in summary_tsv.read_text(encoding="utf-8")
