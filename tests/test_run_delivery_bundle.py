import subprocess
import sys
from pathlib import Path


def _write_tsv(path: Path, header: str, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_run_delivery_bundle_cli_writes_user_facing_index(tmp_path):
    release = tmp_path / "release_checks.tsv"
    objective = tmp_path / "objective_audit.tsv"
    readiness = tmp_path / "command_readiness.tsv"
    quickstart = tmp_path / "quickstart_summary.tsv"
    outdir = tmp_path / "delivery_bundle"

    _write_tsv(
        release,
        "check\trequired\tstatus\texit_code\tcommand\tnote",
        [
            "standard branch smoke\ttrue\tpassed\t0\tstandard\tfinal report",
            "WGD event smoke\ttrue\tpassed\t0\twgd\talpha beta gamma theta",
            "readiness audit\ttrue\tfailed\t1\treadiness\tdocker missing",
        ],
    )
    _write_tsv(
        objective,
        "requirement\tstatus\tevidence\tnote",
        [
            "final reports\tachieved\tstandard and WGD reports\tok",
            "Docker/Apptainer reproducibility\tblocked\treadiness\tMissing container commands: docker, apptainer",
        ],
    )
    _write_tsv(
        readiness,
        "command\tstatus\tpath",
        [
            "nextflow\tavailable_in_conda\tGeneFamilyFlow:/bin/nextflow",
            "/usr/local/bin/R\tavailable\t/usr/local/bin/R",
            "docker\tmissing\t",
            "apptainer\tmissing\t",
        ],
    )
    _write_tsv(
        quickstart,
        "step\tstatus\tpath\tnote",
        [
            "standard_branch_smoke\tpassed\tresults/quickstart/standard_smoke/report/final_report.md\tstandard report",
            "prepared_wgd_handoff\tpassed\tresults/quickstart/example_prepared_wgd/report/final_report.md\talpha beta gamma theta evidence",
        ],
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_delivery_bundle.py",
            "--release-checks",
            str(release),
            "--objective-audit",
            str(objective),
            "--readiness",
            str(readiness),
            "--quickstart",
            str(quickstart),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    manifest = outdir / "delivery_manifest.tsv"
    summary = outdir / "delivery_bundle.md"
    assert manifest.exists()
    assert summary.exists()

    manifest_text = manifest.read_text(encoding="utf-8")
    assert manifest_text.startswith("section\titem\tstatus\tpath\tnote\n")
    assert "standard\tfinal_report\tavailable\tresults/quickstart/standard_smoke/report/final_report.md" in manifest_text
    assert (
        "standard\trun_config_snapshot\tavailable\tresults/quickstart/standard_smoke/tables/run_config_snapshot.tsv\tstandard branch run configuration"
        in manifest_text
    )
    assert "wgd\tfinal_report\tavailable\tresults/quickstart/example_prepared_wgd/report/final_report.md" in manifest_text
    assert (
        "wgd\trun_config_snapshot\tavailable\tresults/quickstart/example_prepared_wgd/tables/wgd_run_config_snapshot.tsv\tWGD branch run configuration"
        in manifest_text
    )
    assert "wgd\tevent_evidence\tavailable\tresults/wgd_smoke/tables/wgd_event_evidence.tsv\talpha,beta,gamma,theta" in manifest_text
    assert (
        "governance\treference_governance\tavailable\tresults/reference_governance/reference_governance.md\ttracked Reference/ changes are release-blocking"
        in manifest_text
    )
    assert (
        "governance\treference_governance_tsv\tavailable\tresults/reference_governance/reference_governance.tsv\tmachine-readable Reference/ status"
        in manifest_text
    )
    assert "runtime\tGeneFamilyFlow\tavailable\tGeneFamilyFlow:/bin/nextflow" in manifest_text
    assert "runtime\t/usr/local/bin/R\tavailable\t/usr/local/bin/R" in manifest_text
    assert "runtime\tdocker\tmissing\t" in manifest_text
    assert "runtime\tapptainer\tmissing\t" in manifest_text
    assert (
        "runtime_recovery\tbootstrap_plan\tavailable\tresults/readiness/runtime_bootstrap_plan.md\tcontainer/runtime recovery plan"
        in manifest_text
    )
    assert (
        "runtime_recovery\tbootstrap_shell\tavailable\tresults/readiness/runtime_bootstrap.sh\texecutable recovery and verification script"
        in manifest_text
    )
    assert (
        "runtime_recovery\tlocal_acceptance\tavailable\tscripts/run_local_acceptance.sh\trefreshes release, handoff, quickstart, and delivery bundle outputs"
        in manifest_text
    )

    summary_text = summary.read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Delivery Bundle" in summary_text
    assert "standard report" in summary_text
    assert "alpha, beta, gamma, theta" in summary_text
    assert "Reference governance" in summary_text
    assert "runtime recovery" in summary_text
    assert "Docker/Apptainer reproducibility" in summary_text
