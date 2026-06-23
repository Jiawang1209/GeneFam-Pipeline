import subprocess
import sys

from bin.genefam.run_release_checks import CheckSpec, default_checks, run_checks, summarize_checks, write_markdown


def test_run_checks_records_pass_and_fail_statuses():
    specs = [
        CheckSpec(name="unit tests", command=[sys.executable, "-m", "pytest"], required=True),
        CheckSpec(name="readiness", command=[sys.executable, "audit"], required=True),
    ]

    def runner(command):
        joined = " ".join(command)
        if "audit" in joined:
            return 1, "missing nextflow\n"
        return 0, "ok\n"

    rows = run_checks(specs, runner=runner)

    assert rows == [
        {
            "check": "unit tests",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": f"{sys.executable} -m pytest",
            "note": "ok",
        },
        {
            "check": "readiness",
            "required": "true",
            "status": "failed",
            "exit_code": "1",
            "command": f"{sys.executable} audit",
            "note": "missing nextflow",
        },
    ]


def test_summarize_checks_marks_release_not_ready_when_required_check_fails():
    rows = [
        {"check": "unit tests", "required": "true", "status": "passed", "exit_code": "0", "command": "pytest", "note": ""},
        {
            "check": "readiness",
            "required": "true",
            "status": "failed",
            "exit_code": "1",
            "command": "audit",
            "note": "",
        },
    ]

    assert summarize_checks(rows) == {"passed": 1, "failed": 1, "release_ready": False}


def test_run_release_checks_cli_writes_outputs(tmp_path):
    outdir = tmp_path / "release"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_release_checks.py",
            "--outdir",
            str(outdir),
            "--quick-self-check",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert (outdir / "release_checks.tsv").read_text(encoding="utf-8").startswith(
        "check\trequired\tstatus\texit_code\tcommand\tnote\n"
    )
    assert "# GeneFam-Pipeline Release Checks" in (outdir / "release_checks.md").read_text(encoding="utf-8")


def test_write_markdown_escapes_pipe_characters_in_table_cells(tmp_path):
    out_path = tmp_path / "release_checks.md"
    rows = [
        {
            "check": "mock MVP",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "python script.py",
            "note": "output\tpath | final_report\tresults/report.md",
        }
    ]

    write_markdown(rows, out_path)

    assert "path \\| final_report" in out_path.read_text(encoding="utf-8")


def test_default_checks_generate_runtime_bootstrap_after_readiness_audit():
    names = [check.name for check in default_checks()]

    assert names.index("runtime bootstrap plan") > names.index("readiness audit")
    bootstrap = next(check for check in default_checks() if check.name == "runtime bootstrap plan")
    assert "bin/genefam/plan_runtime_bootstrap.py" in " ".join(bootstrap.command)
    assert "--readiness results/readiness/command_readiness.tsv" in " ".join(bootstrap.command)


def test_default_checks_include_standard_branch_smoke_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("standard branch smoke") < names.index("readiness audit")
    smoke = next(check for check in default_checks() if check.name == "standard branch smoke")
    assert "bin/genefam/run_standard_smoke.py" in " ".join(smoke.command)
    assert "--outdir results/standard_smoke" in " ".join(smoke.command)


def test_default_checks_include_wgd_smoke_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("WGD event smoke") < names.index("readiness audit")
    smoke = next(check for check in default_checks() if check.name == "WGD event smoke")
    assert "bin/genefam/run_wgd_smoke.py" in " ".join(smoke.command)
    assert "--outdir results/wgd_smoke" in " ".join(smoke.command)


def test_default_checks_include_nextflow_smoke_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("Nextflow mock MVP smoke") < names.index("readiness audit")
    smoke = next(check for check in default_checks() if check.name == "Nextflow mock MVP smoke")
    assert "bin/genefam/run_nextflow_smoke.py" in " ".join(smoke.command)
    assert "--outdir results/nextflow_smoke" in " ".join(smoke.command)
