import subprocess
import sys


def test_run_gene_structure_smoke_writes_structure_summary_from_species_bank(tmp_path):
    outdir = tmp_path / "gene_structure_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_gene_structure_smoke.py",
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
    assert "gene_structure_summary" in completed.stdout
    structure = (outdir / "tables/gene_structure_summary.tsv").read_text(encoding="utf-8")
    assert structure.startswith(
        "species_id\tgene_id\tgene_length\ttranscript_count\texon_count\tcds_count\texon_total_length\tcds_total_length\n"
    )
    assert "Arabidopsis_thaliana\tAT1G01010\t401\t0\t0\t0\t0\t0\n" in structure
    assert "Brassica_rapa\tBraA010001\t701\t0\t0\t0\t0\t0\n" in structure

    summary = (outdir / "gene_structure_smoke.md").read_text(encoding="utf-8")
    assert "Structured genes: 2" in summary
    assert "Species represented: 2" in summary
