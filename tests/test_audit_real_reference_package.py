import subprocess
import sys
from pathlib import Path

from bin.genefam.audit_real_reference_package import audit_real_reference_package, summarize_audit


def _write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(["\t".join(header), *["\t".join(row) for row in rows], ""]),
        encoding="utf-8",
    )


def _write_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"%PDF-1.4\n")


def _write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n")


def _build_reference_package(root: Path) -> Path:
    analysis = root / "analysis_modules"
    required_modules = [
        "00_preprocess",
        "01_gene_identification",
        "02_domain_filtering",
        "03_alignment",
        "04_phylogeny",
        "05_motif_analysis",
        "06_gene_structure",
        "07_chromosome_location",
        "08_promoter",
        "09_promoter_cis",
        "10_synteny_jcvi",
        "11_mcscanx",
        "12_ppi",
        "13_expression",
        "14_duplication_retention_kaks",
        "15_gene_family_summary",
        "report",
    ]
    for module in required_modules:
        (analysis / module).mkdir(parents=True, exist_ok=True)

    _write_tsv(
        analysis / "module_manifest.tsv",
        ["module", "title", "status", "file_count", "folder", "note"],
        [
            [module, module, "available", "1", module, "ok"]
            for module in required_modules
            if module not in {"09_promoter_cis", "13_expression", "14_duplication_retention_kaks"}
        ]
        + [
            ["09_promoter_cis", "Promoter Cis Element", "missing_input", "1", "09_promoter_cis", "PlantCARE gene-level hit table not provided"],
            ["13_expression", "RNA Seq Expression Integration", "skipped_optional", "1", "13_expression", "RNA-seq expression matrix not provided"],
            ["14_duplication_retention_kaks", "Duplication Retention KaKs WGD Events", "partial", "1", "14_duplication_retention_kaks", "Some Ka/Ks jobs failed"],
        ],
    )

    _write_tsv(
        analysis / "08_promoter/plantcare_submission/plantcare_submission_status.tsv",
        ["status", "total_records", "part_count", "records_per_file", "note"],
        [["available", "100", "1", "100", "PlantCARE submission FASTA parts prepared"]],
    )
    _write_tsv(
        analysis / "08_promoter/plantcare_submission/plantcare_submission_manifest.tsv",
        ["part_id", "path", "record_count"],
        [["part_001", "part_001.fa", "100"]],
    )
    _write_tsv(
        analysis / "13_expression/expression_status.tsv",
        ["status", "note"],
        [["skipped_optional", "RNA-seq expression matrix not provided; expression module skipped"]],
    )

    _write_tsv(
        analysis / "10_synteny_jcvi/jcvi_run_status.tsv",
        ["status", "command_count", "succeeded_count", "failed_count", "note"],
        [["available", "5", "5", "0", "ok"]],
    )
    _write_tsv(
        analysis / "10_synteny_jcvi/jcvi_pair_manifest.tsv",
        ["pair_id", "query_species", "subject_species"],
        [["A__B", "A", "B"]],
    )

    _write_tsv(
        analysis / "11_mcscanx/mcscanx_execution_status.tsv",
        ["status", "execute", "missing_tools", "command", "exit_code", "note"],
        [["executed", "true", "", "commands/mcscanx_self_commands.sh", "0", "MCScanX self command script executed successfully"]],
    )
    _write_tsv(
        analysis / "11_mcscanx/mcscanx_circlize_status.tsv",
        ["status", "link_count", "note"],
        [["available", "36", "ok"]],
    )
    _write_tsv(
        analysis / "11_mcscanx/mcscanx_gene_pairs.tsv",
        ["source", "species_id", "gene_a", "gene_b"],
        [["MCScanX_self", "A", "A1", "A2"]],
    )
    _write_tsv(
        analysis / "11_mcscanx/tables/circlize_links.tsv",
        ["chromosome_a", "start_a", "end_a", "chromosome_b", "start_b", "end_b", "gene_a", "gene_b"],
        [["chr1", "1", "10", "chr1", "20", "30", "A1", "A2"]],
    )
    _write_pdf(analysis / "11_mcscanx/plots/mcscanx_circlize.pdf")
    _write_png(analysis / "11_mcscanx/plots/mcscanx_circlize.png")

    _write_tsv(
        analysis / "14_duplication_retention_kaks/kaks_calculator_status.tsv",
        ["status", "pair_count", "succeeded_count", "failed_count", "note"],
        [["partial", "10", "8", "2", "Some Ka/Ks jobs failed"]],
    )
    _write_tsv(
        analysis / "14_duplication_retention_kaks/kaks_failure_summary.tsv",
        ["source", "status", "note", "qc_flags", "pair_count"],
        [["MCScanX self", "failed", "terminal_stop", "terminal_stop", "2"]],
    )

    _write_tsv(
        analysis / "report/report_index.tsv",
        ["key", "status", "path", "description"],
        [["final_report", "available", "final_report.md", "Final report"]],
    )
    for filename in [
        "plot_manifest.tsv",
        "figure_interpretations.tsv",
        "software_versions.tsv",
        "final_report.md",
        "reproducibility_code.md",
    ]:
        path = analysis / "report" / filename
        path.write_text(
            "MCScanX self intra-species duplication and circlize\n"
            "JCVI inter-species collinearity\n"
            "PlantCARE handoff\n"
            "kaks_failure_summary.tsv\n",
            encoding="utf-8",
        )
    return analysis


def test_real_reference_package_audit_accepts_required_self_mcscanx_and_nonfatal_handoffs(tmp_path):
    analysis = _build_reference_package(tmp_path)

    rows = audit_real_reference_package(analysis)
    summary = summarize_audit(rows)

    assert summary == {"passed": 10, "failed": 0, "complete": True}
    by_check = {row["check"]: row for row in rows}
    assert by_check["mcscanx_self_intraspecies_required"]["status"] == "passed"
    assert "MCScanX self" in by_check["mcscanx_self_intraspecies_required"]["note"]
    assert by_check["jcvi_interspecies_required"]["status"] == "passed"
    assert "inter-species" in by_check["jcvi_interspecies_required"]["note"]


def test_real_reference_package_audit_fails_when_mcscanx_self_circlize_is_missing(tmp_path):
    analysis = _build_reference_package(tmp_path)
    (analysis / "11_mcscanx/mcscanx_circlize_status.tsv").unlink()

    rows = audit_real_reference_package(analysis)
    summary = summarize_audit(rows)

    assert summary["complete"] is False
    by_check = {row["check"]: row for row in rows}
    assert by_check["mcscanx_self_intraspecies_required"]["status"] == "failed"
    assert "mcscanx_circlize_status.tsv" in by_check["mcscanx_self_intraspecies_required"]["note"]


def test_real_reference_package_audit_cli_can_write_nonblocking_failed_audit(tmp_path):
    analysis = _build_reference_package(tmp_path)
    (analysis / "11_mcscanx/mcscanx_circlize_status.tsv").unlink()
    out_tsv = tmp_path / "audit.tsv"
    out_md = tmp_path / "audit.md"

    result = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_real_reference_package.py",
            "--analysis-modules",
            str(analysis),
            "--out-tsv",
            str(out_tsv),
            "--out-md",
            str(out_md),
            "--allow-incomplete",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "overall_reference_mvp_package\tfailed" in out_tsv.read_text(encoding="utf-8")
    assert "Overall status: failed" in out_md.read_text(encoding="utf-8")


def test_real_reference_package_audit_cli_writes_markdown_and_exits_zero(tmp_path):
    analysis = _build_reference_package(tmp_path)
    out_tsv = tmp_path / "audit.tsv"
    out_md = tmp_path / "audit.md"

    result = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_real_reference_package.py",
            "--analysis-modules",
            str(analysis),
            "--out-tsv",
            str(out_tsv),
            "--out-md",
            str(out_md),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "overall_reference_mvp_package" in out_tsv.read_text(encoding="utf-8")
    markdown = out_md.read_text(encoding="utf-8")
    assert "Overall status: passed" in markdown
    assert "MCScanX self intra-species" in markdown
