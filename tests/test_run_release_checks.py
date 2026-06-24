import subprocess
import sys

from bin.genefam.run_release_checks import (
    CheckSpec,
    default_checks,
    run_checks,
    summarize_checks,
    write_handoff_report,
    write_markdown,
    write_objective_audit,
    write_tsv,
)


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

    assert summarize_checks(rows) == {
        "passed": 1,
        "failed": 1,
        "required_failed": 1,
        "optional_failed": 0,
        "release_ready": False,
    }


def test_summarize_checks_keeps_release_ready_when_only_optional_checks_fail():
    rows = [
        {"check": "unit tests", "required": "true", "status": "passed", "exit_code": "0", "command": "pytest", "note": ""},
        {
            "check": "Docker profile smoke",
            "required": "false",
            "status": "failed",
            "exit_code": "127",
            "command": "container smoke",
            "note": "docker missing",
        },
    ]

    assert summarize_checks(rows) == {
        "passed": 1,
        "failed": 1,
        "required_failed": 0,
        "optional_failed": 1,
        "release_ready": True,
    }


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


def test_write_markdown_summarizes_required_and_optional_failures(tmp_path):
    out_path = tmp_path / "release_checks.md"
    rows = [
        {"check": "pytest", "required": "true", "status": "passed", "exit_code": "0", "command": "pytest", "note": ""},
        {
            "check": "readiness audit",
            "required": "true",
            "status": "failed",
            "exit_code": "1",
            "command": "readiness",
            "note": "",
        },
        {
            "check": "Docker profile smoke",
            "required": "false",
            "status": "failed",
            "exit_code": "1",
            "command": "docker smoke",
            "note": "",
        },
    ]

    write_markdown(rows, out_path)

    text = out_path.read_text(encoding="utf-8")
    assert "Required failed: 1" in text
    assert "Optional failed: 1" in text


def test_default_checks_generate_runtime_bootstrap_after_readiness_audit():
    names = [check.name for check in default_checks()]

    assert names.index("runtime bootstrap plan") > names.index("readiness audit")
    bootstrap = next(check for check in default_checks() if check.name == "runtime bootstrap plan")
    assert "bin/genefam/plan_runtime_bootstrap.py" in " ".join(bootstrap.command)
    assert "--readiness results/readiness/command_readiness.tsv" in " ".join(bootstrap.command)


def test_default_checks_include_optional_container_profile_smokes_after_bootstrap():
    checks = default_checks()
    names = [check.name for check in checks]

    assert names.index("container materials audit") > names.index("runtime bootstrap plan")
    assert names.index("Docker profile smoke") > names.index("container materials audit")
    assert names.index("Docker profile smoke") > names.index("runtime bootstrap plan")
    assert names.index("Apptainer profile smoke") > names.index("Docker profile smoke")

    materials = next(check for check in checks if check.name == "container materials audit")
    assert materials.required is True
    materials_command = " ".join(materials.command)
    assert "bin/genefam/audit_container_materials.py" in materials_command
    assert "--outdir results/container_materials" in materials_command

    docker = next(check for check in checks if check.name == "Docker profile smoke")
    assert docker.required is False
    docker_command = " ".join(docker.command)
    assert "bin/genefam/run_container_profile_smoke.py" in docker_command
    assert "--profile docker" in docker_command
    assert "--conda-env GeneFamilyFlow" in docker_command
    assert "--outdir results/container_profile_smoke/docker" in docker_command

    apptainer = next(check for check in checks if check.name == "Apptainer profile smoke")
    assert apptainer.required is False
    apptainer_command = " ".join(apptainer.command)
    assert "bin/genefam/run_container_profile_smoke.py" in apptainer_command
    assert "--profile apptainer" in apptainer_command
    assert "--conda-env GeneFamilyFlow" in apptainer_command
    assert "--outdir results/container_profile_smoke/apptainer" in apptainer_command


def test_default_checks_include_nextflow_single_tool_smoke():
    checks = default_checks()
    names = [check.name for check in checks]

    assert names.index("Nextflow standard single-tool smoke") > names.index("Nextflow standard branch smoke")
    smoke = next(check for check in checks if check.name == "Nextflow standard single-tool smoke")
    assert smoke.required is True
    command = " ".join(smoke.command)
    assert "bin/genefam/run_nextflow_single_tool_smoke.py" in command
    assert "--conda-env GeneFamilyFlow" in command
    assert "--outdir results/nextflow_single_tool_smoke" in command


def test_default_checks_do_not_include_handoff_report_as_a_stale_input_check():
    checks = default_checks()
    names = [check.name for check in checks]

    assert "handoff report" not in names


def test_write_handoff_report_uses_latest_written_release_tsv(tmp_path):
    release_tsv = tmp_path / "release_checks.tsv"
    objective_tsv = tmp_path / "objective_audit.tsv"
    readiness_tsv = tmp_path / "command_readiness.tsv"
    docker_tsv = tmp_path / "docker.tsv"
    apptainer_tsv = tmp_path / "apptainer.tsv"
    out = tmp_path / "handoff_report.md"
    summary_tsv = tmp_path / "handoff_summary.tsv"
    write_tsv(
        [
            {"check": "pytest", "required": "true", "status": "passed", "exit_code": "0", "command": "pytest", "note": ""},
            {
                "check": "readiness audit",
                "required": "true",
                "status": "failed",
                "exit_code": "1",
                "command": "readiness",
                "note": "",
            },
            {
                "check": "Docker profile smoke",
                "required": "false",
                "status": "failed",
                "exit_code": "1",
                "command": "docker",
                "note": "",
            },
        ],
        release_tsv,
    )
    objective_tsv.write_text(
        "requirement\tstatus\tevidence\tnote\nDocker/Apptainer reproducibility\tblocked\treadiness\tmissing\n",
        encoding="utf-8",
    )
    readiness_tsv.write_text("command\tstatus\tpath\ndocker\tmissing\t\n", encoding="utf-8")
    docker_tsv.write_text(
        "check\tprofile\tstatus\texit_code\tcommand\tnote\ndocker_profile_smoke\tdocker\tmissing_runtime\t127\tdocker\t\n",
        encoding="utf-8",
    )
    apptainer_tsv.write_text(
        "check\tprofile\tstatus\texit_code\tcommand\tnote\napptainer_profile_smoke\tapptainer\tmissing_runtime\t127\tapptainer\t\n",
        encoding="utf-8",
    )

    assert write_handoff_report(
        release_tsv,
        objective_tsv,
        readiness_tsv,
        [docker_tsv, apptainer_tsv],
        out,
        summary_tsv,
    )

    text = out.read_text(encoding="utf-8")
    assert "passed=1 failed=2 required_failed=1 optional_failed=1 release_ready=false" in text
    summary_text = summary_tsv.read_text(encoding="utf-8")
    assert "release\tpassed=1 failed=2 required_failed=1 optional_failed=1 release_ready=false" in summary_text
    assert "blocked_requirements\tDocker/Apptainer reproducibility" in summary_text
    assert (
        "next_unblock_artifacts\tresults/readiness/runtime_bootstrap_plan.md, "
        "results/readiness/runtime_bootstrap.sh" in summary_text
    )
    assert "next_unblock_command\tbash results/readiness/runtime_bootstrap.sh" in summary_text
    assert "container_smoke\tdocker=missing_runtime; apptainer=missing_runtime" in summary_text


def test_default_checks_include_standard_branch_smoke_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("standard branch smoke") < names.index("readiness audit")
    smoke = next(check for check in default_checks() if check.name == "standard branch smoke")
    assert "bin/genefam/run_standard_smoke.py" in " ".join(smoke.command)
    assert "--outdir results/standard_smoke" in " ".join(smoke.command)


def test_default_checks_include_domain_filter_smoke_before_standard_branch_smoke():
    names = [check.name for check in default_checks()]

    assert names.index("domain filter smoke") < names.index("standard branch smoke")
    smoke = next(check for check in default_checks() if check.name == "domain filter smoke")
    command = " ".join(smoke.command)
    assert "bin/genefam/run_domain_filter_smoke.py" in command
    assert "--input tests/fixtures/hmmer_domains/domains.tsv" in command
    assert "--outdir results/domain_filter_smoke" in command


def test_default_checks_include_standard_branch_expression_smoke_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("standard branch expression smoke") < names.index("readiness audit")
    assert names.index("standard branch expression smoke") > names.index("standard branch smoke")
    smoke = next(check for check in default_checks() if check.name == "standard branch expression smoke")
    command = " ".join(smoke.command)
    assert "bin/genefam/run_standard_smoke.py" in command
    assert "--expression-matrix tests/fixtures/expression/family_expression.tsv" in command
    assert "--r-bin /usr/local/bin/R" in command
    assert "--outdir results/standard_expression_smoke" in command


def test_default_checks_include_synteny_parser_smoke_before_wgd_smoke():
    names = [check.name for check in default_checks()]

    assert names.index("synteny parser smoke") < names.index("WGD event smoke")
    assert names.index("synteny parser smoke") > names.index("standard branch expression smoke")
    smoke = next(check for check in default_checks() if check.name == "synteny parser smoke")
    command = " ".join(smoke.command)
    assert "bin/genefam/run_synteny_smoke.py" in command
    assert "--collinearity tests/fixtures/mcscanx/sample.collinearity" in command
    assert "--outdir results/synteny_smoke" in command


def test_default_checks_include_kaks_smoke_before_wgd_smoke():
    names = [check.name for check in default_checks()]

    assert names.index("Ka/Ks parser smoke") < names.index("WGD event smoke")
    assert names.index("Ka/Ks parser smoke") > names.index("synteny parser smoke")
    smoke = next(check for check in default_checks() if check.name == "Ka/Ks parser smoke")
    command = " ".join(smoke.command)
    assert "bin/genefam/run_kaks_smoke.py" in command
    assert "--kaks tests/fixtures/kaks/kaks_calculator.tsv" in command
    assert "--outdir results/kaks_smoke" in command


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
    assert "--conda-env GeneFamilyFlow" in " ".join(smoke.command)
    assert "--outdir results/nextflow_smoke" in " ".join(smoke.command)


def test_default_checks_include_nextflow_standard_smoke_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("Nextflow standard branch smoke") < names.index("readiness audit")
    assert names.index("Nextflow standard branch smoke") > names.index("Nextflow mock MVP smoke")
    smoke = next(check for check in default_checks() if check.name == "Nextflow standard branch smoke")
    assert "bin/genefam/run_nextflow_standard_smoke.py" in " ".join(smoke.command)
    assert "--conda-env GeneFamilyFlow" in " ".join(smoke.command)
    assert "--outdir results/nextflow_standard_smoke" in " ".join(smoke.command)


def test_default_checks_include_nextflow_wgd_smoke_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("Nextflow WGD event smoke") < names.index("readiness audit")
    assert names.index("Nextflow WGD event smoke") > names.index("Nextflow standard branch smoke")
    smoke = next(check for check in default_checks() if check.name == "Nextflow WGD event smoke")
    assert "bin/genefam/run_nextflow_wgd_smoke.py" in " ".join(smoke.command)
    assert "--conda-env GeneFamilyFlow" in " ".join(smoke.command)
    assert "--outdir results/nextflow_wgd_smoke" in " ".join(smoke.command)


def test_default_checks_include_prepared_wgd_handoff_example_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("prepared WGD handoff example") < names.index("readiness audit")
    assert names.index("prepared WGD handoff example") > names.index("Nextflow WGD event smoke")
    example = next(check for check in default_checks() if check.name == "prepared WGD handoff example")
    command = " ".join(example.command)
    assert "bin/genefam/run_prepared_wgd_handoff_example.py" in command
    assert "--conda-env GeneFamilyFlow" in command
    assert "--example-dir examples/prepared_wgd_handoff" in command
    assert "--outdir results/example_prepared_wgd" in command


def test_default_checks_include_quickstart_handoff_before_readiness():
    names = [check.name for check in default_checks()]

    assert names.index("quickstart handoff") < names.index("readiness audit")
    assert names.index("quickstart handoff") > names.index("prepared WGD handoff example")
    quickstart = next(check for check in default_checks() if check.name == "quickstart handoff")
    command = " ".join(quickstart.command)
    assert "bin/genefam/run_quickstart.py" in command
    assert "--conda-env GeneFamilyFlow" in command
    assert "--outdir results/quickstart" in command


def test_default_readiness_check_audits_genefamilyflow_conda_env():
    readiness = next(check for check in default_checks() if check.name == "readiness audit")

    assert "--conda-env GeneFamilyFlow" in " ".join(readiness.command)


def test_write_objective_audit_uses_release_rows_and_readiness_tsv(tmp_path):
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
    rows = [
        {"check": "pytest", "required": "true", "status": "passed", "exit_code": "0", "command": "pytest", "note": ""},
        {
            "check": "validate example config",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "validate",
            "note": "",
        },
        {
            "check": "validate advanced config",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "validate",
            "note": "",
        },
        {
            "check": "standard branch smoke",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "standard",
            "note": "",
        },
        {
            "check": "standard branch expression smoke",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "standard expression",
            "note": "",
        },
        {
            "check": "WGD event smoke",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "wgd",
            "note": "",
        },
        {
            "check": "Nextflow mock MVP smoke",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "nextflow",
            "note": "",
        },
        {
            "check": "Nextflow standard branch smoke",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "nextflow",
            "note": "",
        },
        {
            "check": "Nextflow WGD event smoke",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "nextflow",
            "note": "",
        },
        {
            "check": "prepared WGD handoff example",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "prepared",
            "note": "",
        },
        {
            "check": "quickstart handoff",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "quickstart",
            "note": "",
        },
    ]

    written = write_objective_audit(rows, readiness, tmp_path / "objective")

    assert written is True
    assert "Docker/Apptainer reproducibility\tblocked" in (
        tmp_path / "objective" / "objective_audit.tsv"
    ).read_text(encoding="utf-8")
    assert "Complete: false" in (tmp_path / "objective" / "objective_audit.md").read_text(encoding="utf-8")


def test_write_objective_audit_requires_expression_smoke_for_expression_integration(tmp_path):
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
    rows = [
        {"check": "pytest", "required": "true", "status": "passed", "exit_code": "0", "command": "pytest", "note": ""},
        {
            "check": "standard branch smoke",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "standard",
            "note": "",
        },
        {
            "check": "quickstart handoff",
            "required": "true",
            "status": "passed",
            "exit_code": "0",
            "command": "quickstart",
            "note": "",
        },
    ]

    written = write_objective_audit(rows, readiness, tmp_path / "objective")

    assert written is True
    assert "chromosome and expression integration\tmissing" in (
        tmp_path / "objective" / "objective_audit.tsv"
    ).read_text(encoding="utf-8")
