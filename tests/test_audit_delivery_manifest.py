import subprocess
import sys
from pathlib import Path

from bin.genefam.audit_delivery_manifest import audit_delivery_manifest, summarize_audit


def _write_manifest(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "section\titem\tstatus\tpath\tnote",
                *["\t".join(row) for row in rows],
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_delivery_manifest_audit_requires_available_paths_to_exist(tmp_path):
    existing = tmp_path / "report.md"
    existing.write_text("# report\n", encoding="utf-8")
    manifest = tmp_path / "delivery_manifest.tsv"
    _write_manifest(
        manifest,
        [
            ["status", "release_checks", "available", str(existing), "ok"],
            ["standard", "paper_report", "available", str(tmp_path / "missing_report.md"), "missing"],
            ["runtime_recovery", "docker_profile_smoke", "missing", str(tmp_path / "missing_docker.md"), "optional"],
            ["runtime", "GeneFamilyFlow", "available", "GeneFamilyFlow:/env/bin/nextflow", "runtime locator"],
        ],
    )

    rows = audit_delivery_manifest(manifest)
    by_check = {row["check"]: row for row in rows}

    assert by_check["delivery_manifest_required_columns"]["status"] == "passed"
    assert by_check["delivery_manifest_paths_exist"]["status"] == "failed"
    assert "paper_report:path:missing_file" in by_check["delivery_manifest_paths_exist"]["note"]
    assert "docker_profile_smoke" not in by_check["delivery_manifest_paths_exist"]["note"]
    assert "GeneFamilyFlow" not in by_check["delivery_manifest_paths_exist"]["note"]
    assert summarize_audit(rows) == {"passed": 1, "failed": 1, "complete": False}


def test_delivery_manifest_audit_cli_writes_outputs_for_complete_manifest(tmp_path):
    existing = tmp_path / "delivery_bundle.md"
    existing.write_text("# bundle\n", encoding="utf-8")
    manifest = tmp_path / "delivery_manifest.tsv"
    _write_manifest(
        manifest,
        [
            ["status", "delivery_bundle", "available", str(existing), "ok"],
            ["status", "final_stage_blocker", "blocked", str(existing), "known final-stage blocker"],
            ["runtime", "docker", "missing", "", "container runtime"],
        ],
    )
    out_tsv = tmp_path / "audit.tsv"
    out_md = tmp_path / "audit.md"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_delivery_manifest.py",
            "--delivery-manifest",
            str(manifest),
            "--out-tsv",
            str(out_tsv),
            "--out-md",
            str(out_md),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "delivery_manifest_paths_exist\tpassed" in out_tsv.read_text(encoding="utf-8")
    assert "Complete: true" in out_md.read_text(encoding="utf-8")
