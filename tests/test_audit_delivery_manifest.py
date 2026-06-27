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


def _write_delivery_bundle_markdown(path: Path, rows: list[list[str]]) -> None:
    lines = [
        "# GeneFam-Pipeline Delivery Bundle",
        "",
        "| section | item | status | path | note |",
        "|---|---|---|---|---|",
    ]
    for section, item, status, indexed_path, note in rows:
        path_cell = f"[{item}]({indexed_path})" if indexed_path else ""
        lines.append(f"| {section} | {item} | {status} | {path_cell} | {note} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    assert by_check["delivery_manifest_required_items"]["status"] == "failed"
    assert "nextflow:nextflow_single_tool_smoke:missing_item" in by_check[
        "delivery_manifest_required_items"
    ]["note"]
    assert by_check["delivery_bundle_markdown_links"]["status"] == "failed"
    assert "delivery_bundle.md:missing_markdown" in by_check["delivery_bundle_markdown_links"]["note"]
    assert summarize_audit(rows) == {"passed": 1, "failed": 3, "complete": False}


def test_delivery_manifest_audit_requires_core_handoff_items(tmp_path):
    existing = tmp_path / "report.md"
    existing.write_text("# report\n", encoding="utf-8")
    manifest = tmp_path / "delivery_manifest.tsv"
    _write_manifest(
        manifest,
        [
            ["status", "release_checks", "available", str(existing), "ok"],
            ["status", "release_ready", "available", str(existing), "ok"],
            ["status", "objective_audit", "available", str(existing), "ok"],
            ["status", "final_stage_blocker", "blocked", str(existing), "known final-stage blocker"],
            ["status", "figure_gallery", "available", str(existing), "ok"],
            ["status", "delivery_bundle_figure_gallery_smoke", "available", str(existing), "ok"],
            ["status", "publication_report_audit", "available", str(existing), "ok"],
            ["status", "wgd_publication_report_audit", "available", str(existing), "ok"],
            ["standard", "mock_mvp", "available", str(existing), "ok"],
            ["nextflow", "nextflow_mock_mvp_smoke", "available", str(existing), "ok"],
            ["wgd", "event_evidence", "available", str(existing), "ok"],
            ["governance", "reference_gitignore", "available", str(existing), "ok"],
            ["runtime_recovery", "local_acceptance", "available", str(existing), "ok"],
            ["docs", "history", "available", str(existing), "ok"],
        ],
    )

    rows = audit_delivery_manifest(manifest)
    by_check = {row["check"]: row for row in rows}

    assert by_check["delivery_manifest_required_items"]["status"] == "failed"
    assert "nextflow:nextflow_single_tool_smoke:missing_item" in by_check[
        "delivery_manifest_required_items"
    ]["note"]
    assert "status:standard_report_index_audit:missing_item" in by_check[
        "delivery_manifest_required_items"
    ]["note"]
    assert "status:r_runtime_health:missing_item" in by_check[
        "delivery_manifest_required_items"
    ]["note"]
    assert "runtime_recovery:bootstrap_shell_syntax:missing_item" in by_check[
        "delivery_manifest_required_items"
    ]["note"]
    assert by_check["delivery_bundle_markdown_links"]["status"] == "failed"
    assert "delivery_bundle.md:missing_markdown" in by_check["delivery_bundle_markdown_links"]["note"]
    assert summarize_audit(rows) == {"passed": 2, "failed": 2, "complete": False}


def test_delivery_manifest_audit_cli_writes_outputs_for_complete_manifest(tmp_path):
    existing = tmp_path / "delivery_bundle.md"
    manifest = tmp_path / "delivery_manifest.tsv"
    rows = [
        ["status", "delivery_bundle", "available", str(existing), "ok"],
        ["status", "release_checks", "available", str(existing), "ok"],
        ["status", "release_ready", "available", str(existing), "ok"],
        ["status", "objective_audit", "available", str(existing), "ok"],
        ["status", "r_runtime_health", "available", str(existing), "ok"],
        ["status", "final_stage_blocker", "blocked", str(existing), "known final-stage blocker"],
        ["status", "figure_gallery", "available", str(existing), "ok"],
        ["status", "delivery_bundle_figure_gallery_smoke", "available", str(existing), "ok"],
        ["status", "publication_report_audit", "available", str(existing), "ok"],
        ["status", "standard_report_index_audit", "available", str(existing), "ok"],
        ["status", "wgd_publication_report_audit", "available", str(existing), "ok"],
        ["status", "wgd_report_index_audit", "available", str(existing), "ok"],
        ["standard", "mock_mvp", "available", str(existing), "ok"],
        ["nextflow", "nextflow_mock_mvp_smoke", "available", str(existing), "ok"],
        ["nextflow", "nextflow_single_tool_smoke", "available", str(existing), "ok"],
        ["wgd", "event_evidence", "available", str(existing), "ok"],
        ["governance", "reference_gitignore", "available", str(existing), "ok"],
        ["runtime_recovery", "bootstrap_shell_syntax", "available", str(existing), "ok"],
        ["runtime_recovery", "local_acceptance", "available", str(existing), "ok"],
        ["docs", "history", "available", str(existing), "ok"],
        ["runtime", "docker", "missing", "", "container runtime"],
    ]
    _write_manifest(manifest, rows)
    _write_delivery_bundle_markdown(existing, rows)
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
    assert "delivery_manifest_required_items\tpassed" in out_tsv.read_text(encoding="utf-8")
    assert "delivery_bundle_markdown_links\tpassed" in out_tsv.read_text(encoding="utf-8")
    assert "Complete: true" in out_md.read_text(encoding="utf-8")


def test_delivery_manifest_audit_fails_when_delivery_bundle_paths_are_not_clickable(tmp_path):
    existing = tmp_path / "report.md"
    existing.write_text("# report\n", encoding="utf-8")
    manifest = tmp_path / "delivery_manifest.tsv"
    rows = [
        ["status", "release_checks", "available", str(existing), "ok"],
        ["standard", "paper_level_visual_report", "available", str(existing), "paper report"],
    ]
    _write_manifest(manifest, rows)
    (tmp_path / "delivery_bundle.md").write_text(
        "| section | item | status | path | note |\n"
        "|---|---|---|---|---|\n"
        f"| status | release_checks | available | `{existing}` | ok |\n"
        f"| standard | paper_level_visual_report | available | `{existing}` | paper report |\n",
        encoding="utf-8",
    )

    audit_rows = audit_delivery_manifest(manifest)
    by_check = {row["check"]: row for row in audit_rows}

    assert by_check["delivery_bundle_markdown_links"]["status"] == "failed"
    assert "release_checks:markdown_link:missing" in by_check["delivery_bundle_markdown_links"]["note"]
