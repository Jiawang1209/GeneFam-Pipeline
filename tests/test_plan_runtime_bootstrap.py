import subprocess
import sys

from bin.genefam.plan_runtime_bootstrap import build_bootstrap_plan, read_readiness_tsv


def test_build_bootstrap_plan_groups_missing_commands_into_actionable_steps():
    rows = [
        {"command": "nextflow", "status": "missing", "path": ""},
        {"command": "conda", "status": "available", "path": "/opt/conda/bin/conda"},
        {"command": "/usr/local/bin/R", "status": "available", "path": "/usr/local/bin/R"},
        {"command": "docker", "status": "missing", "path": ""},
        {"command": "apptainer", "status": "missing", "path": ""},
        {"command": "hmmsearch", "status": "missing", "path": ""},
        {"command": "diamond", "status": "missing", "path": ""},
        {"command": "mafft", "status": "missing", "path": ""},
        {"command": "iqtree2", "status": "missing", "path": ""},
        {"command": "meme", "status": "missing", "path": ""},
    ]

    plan = build_bootstrap_plan(rows)

    assert "conda env update -n GeneFamilyFlow -f envs/GeneFamilyFlow.conda.yaml --prune" in plan["shell"]
    assert "conda run -n GeneFamilyFlow nextflow -version" in plan["shell"]
    assert "docker build -t genefam-pipeline:latest ." in plan["shell"]
    assert "docker run --rm -v \"$PWD/results:/opt/GeneFam-Pipeline/results\" genefam-pipeline:latest" in plan["shell"]
    assert plan["shell"].index("docker build -t genefam-pipeline:latest .") < plan["shell"].index(
        "docker run --rm -v \"$PWD/results:/opt/GeneFam-Pipeline/results\" genefam-pipeline:latest"
    )
    assert "apptainer build --force genefam-pipeline_latest.sif docker-daemon://genefam-pipeline:latest" in plan["shell"]
    assert plan["shell"].index(
        "docker run --rm -v \"$PWD/results:/opt/GeneFam-Pipeline/results\" genefam-pipeline:latest"
    ) < plan["shell"].index("apptainer build --force genefam-pipeline_latest.sif docker-daemon://genefam-pipeline:latest")
    assert "python bin/genefam/run_container_profile_smoke.py --profile docker --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/docker" in plan["shell"]
    assert "python bin/genefam/run_container_profile_smoke.py --profile apptainer --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/apptainer" in plan["shell"]
    assert "python bin/genefam/run_release_checks.py --outdir results/release_checks" in plan["shell"]
    assert "bash scripts/run_local_acceptance.sh" in plan["shell"]
    assert "Missing commands: nextflow, docker, apptainer, hmmsearch, diamond, mafft, iqtree2, meme" in plan["markdown"]
    assert "GeneFamilyFlow" in plan["markdown"]
    assert "/usr/local/bin/R" in plan["markdown"]
    assert "genefam-pipeline_latest.sif" in plan["markdown"]
    assert "docker run --rm -v \"$PWD/results:/opt/GeneFam-Pipeline/results\" genefam-pipeline:latest" in plan["markdown"]
    assert "results/container_default_smoke" in plan["markdown"]
    assert "run_container_profile_smoke.py --profile docker" in plan["markdown"]
    assert "run_container_profile_smoke.py --profile apptainer" in plan["markdown"]
    assert "scripts/run_local_acceptance.sh" in plan["markdown"]
    assert "results/delivery_bundle/delivery_bundle.md" in plan["markdown"]


def test_read_readiness_tsv_preserves_command_status_rows(tmp_path):
    readiness = tmp_path / "readiness.tsv"
    readiness.write_text(
        "command\tstatus\tpath\n"
        "nextflow\tmissing\t\n"
        "conda\tavailable\t/opt/conda/bin/conda\n",
        encoding="utf-8",
    )

    assert read_readiness_tsv(readiness) == [
        {"command": "nextflow", "status": "missing", "path": ""},
        {"command": "conda", "status": "available", "path": "/opt/conda/bin/conda"},
    ]


def test_plan_runtime_bootstrap_cli_writes_markdown_and_shell_outputs(tmp_path):
    readiness = tmp_path / "readiness.tsv"
    outdir = tmp_path / "bootstrap"
    readiness.write_text(
        "command\tstatus\tpath\n"
        "nextflow\tmissing\t\n"
        "conda\tavailable\t/opt/conda/bin/conda\n"
        "/usr/local/bin/R\tavailable\t/usr/local/bin/R\n"
        "hmmsearch\tmissing\t\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/plan_runtime_bootstrap.py",
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
    assert "Missing commands: nextflow, hmmsearch" in (outdir / "runtime_bootstrap_plan.md").read_text(
        encoding="utf-8"
    )
    assert (outdir / "runtime_bootstrap.sh").read_text(encoding="utf-8").startswith("#!/usr/bin/env bash\n")
