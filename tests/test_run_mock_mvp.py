import csv
import subprocess
import sys
from pathlib import Path

from bin.genefam.run_mock_mvp import run_mock_mvp


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_run_mock_mvp_writes_core_outputs(tmp_path):
    mock_evidence = tmp_path / "mock_evidence"
    mock_evidence.mkdir()
    (mock_evidence / "hmmer.tsv").write_text(
        "\t".join(["species_id", "gene_id", "hmm_id", "evalue"]) + "\n"
        "Arabidopsis_thaliana\tAT1G01010\tPF00657\t1e-40\n"
        "Arabidopsis_thaliana\tAT1G01020\tPF00657\t1e-20\n"
        "Brassica_rapa\tBraA010001\tPF00657\t1e-35\n",
        encoding="utf-8",
    )
    (mock_evidence / "diamond.tsv").write_text(
        "\t".join(["species_id", "gene_id", "reference_hit", "evalue"]) + "\n"
        "Arabidopsis_thaliana\tAT1G01010\tAT_REF\t1e-30\n"
        "Brassica_rapa\tBraA010001\tAT_REF\t1e-25\n",
        encoding="utf-8",
    )

    outdir = tmp_path / "results"

    outputs = run_mock_mvp(
        config_path=Path("configs/example.config.yaml"),
        groups_path=Path("configs/species_groups.yaml"),
        mock_evidence_dir=mock_evidence,
        outdir=outdir,
    )

    assert outputs["species_manifest"] == outdir / "tables" / "species_manifest.tsv"
    assert outputs["family_candidates"] == outdir / "tables" / "family_candidates.tsv"
    assert outputs["family_counts"] == outdir / "tables" / "family_counts.tsv"
    assert outputs["family_members_faa"] == outdir / "sequences" / "family_members.faa"
    assert outputs["summary_report"] == outdir / "report" / "summary.md"

    candidates = read_tsv(outputs["family_candidates"])
    assert [row["gene_id"] for row in candidates] == ["AT1G01010", "BraA010001"]
    assert {row["evidence_sources"] for row in candidates} == {"diamond,hmmer"}

    counts = read_tsv(outputs["family_counts"])
    assert counts == [
        {
            "species_id": "Arabidopsis_thaliana",
            "member_count": "1",
            "hmmer_count": "1",
            "diamond_count": "1",
            "intersection_count": "1",
        },
        {
            "species_id": "Brassica_rapa",
            "member_count": "1",
            "hmmer_count": "1",
            "diamond_count": "1",
            "intersection_count": "1",
        },
    ]

    fasta_text = outputs["family_members_faa"].read_text(encoding="utf-8")
    assert ">Arabidopsis_thaliana|AT1G01010" in fasta_text
    assert ">Brassica_rapa|BraA010001" in fasta_text

    report_text = outputs["summary_report"].read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Mock MVP Summary" in report_text
    assert "Final rule: intersection" in report_text


def test_run_mock_mvp_cli_works_when_invoked_by_script_path(tmp_path):
    outdir = tmp_path / "cli_results"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_mock_mvp.py",
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
    assert (outdir / "tables" / "family_candidates.tsv").exists()
    assert "family_counts" in completed.stdout
