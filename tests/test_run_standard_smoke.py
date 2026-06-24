import subprocess
import sys


def test_run_standard_smoke_writes_standard_branch_outputs(tmp_path):
    outdir = tmp_path / "standard_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_standard_smoke.py",
            "--config",
            "configs/example.config.yaml",
            "--groups",
            "configs/species_groups.yaml",
            "--mock-evidence-dir",
            "tests/fixtures/mock_evidence",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    expected = [
        "tables/species_manifest.tsv",
        "tables/family_candidates.tsv",
        "tables/family_counts.tsv",
        "sequences/family_members.faa",
        "tables/alignment_manifest.tsv",
        "tables/phylogeny_manifest.tsv",
        "tables/motif_summary.tsv",
        "tables/chromosome_locations.tsv",
        "report/report_index.tsv",
        "report/final_report.md",
    ]
    for relative_path in expected:
        assert (outdir / relative_path).exists(), relative_path
    assert "standard_final_report" in completed.stdout

    report_index = (outdir / "report/report_index.tsv").read_text(encoding="utf-8")
    assert "chromosome_locations" in report_index
    assert "motif_summary" in report_index
    assert "motif_summary.tsv\tavailable" in report_index
    assert "family_expression" in report_index
    motif_summary = (outdir / "tables/motif_summary.tsv").read_text(encoding="utf-8")
    assert motif_summary.startswith("family_name\tmotif_id\tmotif_name\twidth\tsites\tevalue\n")
    assert "GDSL_motif_1" in motif_summary


def test_run_standard_smoke_writes_family_expression_when_matrix_is_provided(tmp_path):
    outdir = tmp_path / "standard_smoke"
    expression_matrix = tmp_path / "expression.tsv"
    expression_matrix.write_text(
        "gene_id\tcold_0h\tcold_3h\n"
        "AT1G01010\t1.0\t3.0\n"
        "BraA010001\t2.0\t5.0\n"
        "unrelated\t9.0\t9.0\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_standard_smoke.py",
            "--config",
            "configs/example.config.yaml",
            "--groups",
            "configs/species_groups.yaml",
            "--mock-evidence-dir",
            "tests/fixtures/mock_evidence",
            "--expression-matrix",
            str(expression_matrix),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    family_expression = outdir / "tables/family_expression.tsv"
    assert family_expression.read_text(encoding="utf-8") == (
        "gene_id\tcold_0h\tcold_3h\n"
        "AT1G01010\t1.0\t3.0\n"
        "BraA010001\t2.0\t5.0\n"
    )
    report_index = (outdir / "report/report_index.tsv").read_text(encoding="utf-8")
    assert "family_expression\t" in report_index
    assert "family_expression.tsv\tavailable" in report_index
