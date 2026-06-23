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
    assert outputs["run_plan"] == outdir / "tables" / "run_plan.tsv"
    assert outputs["family_candidates"] == outdir / "tables" / "family_candidates.tsv"
    assert outputs["family_counts"] == outdir / "tables" / "family_counts.tsv"
    assert outputs["family_members_faa"] == outdir / "sequences" / "family_members.faa"
    assert outputs["alignment_manifest"] == outdir / "tables" / "alignment_manifest.tsv"
    assert outputs["phylogeny_manifest"] == outdir / "tables" / "phylogeny_manifest.tsv"
    assert outputs["summary_report"] == outdir / "report" / "summary.md"
    assert outputs["report_index"] == outdir / "report" / "report_index.tsv"
    assert outputs["final_report"] == outdir / "report" / "final_report.md"

    run_plan = read_tsv(outputs["run_plan"])
    assert {"section": "runtime", "key": "environment", "value": "GeneFamilyFlow"} in run_plan
    assert {"section": "module", "key": "report", "value": "enabled"} in run_plan

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
    assert "## Available Outputs" in report_text
    assert "- `family_candidates`: `tables/family_candidates.tsv`" in report_text
    assert "## Pending Outputs" in report_text
    assert "- `wgd_event_evidence`: Configured WGD event evidence table" in report_text

    final_report_text = outputs["final_report"].read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Final Report" in final_report_text
    assert "Project: GDSL_demo" in final_report_text
    assert "Gene family: GDSL" in final_report_text
    assert "## Output Availability" in final_report_text
    assert "## WGD Event Evidence" in final_report_text

    report_index = read_tsv(outputs["report_index"])
    by_key = {row["key"]: row for row in report_index}
    assert by_key["family_candidates"]["status"] == "available"
    assert by_key["family_candidates"]["path"] == "tables/family_candidates.tsv"
    assert by_key["run_plan"]["status"] == "available"
    assert by_key["run_plan"]["path"] == "tables/run_plan.tsv"
    assert by_key["alignment_manifest"]["status"] == "available"
    assert by_key["alignment_manifest"]["path"] == "tables/alignment_manifest.tsv"
    assert by_key["phylogeny_manifest"]["status"] == "available"
    assert by_key["phylogeny_manifest"]["path"] == "tables/phylogeny_manifest.tsv"
    assert by_key["motif_summary"]["status"] == "not_available"
    assert by_key["syntenic_pairs"]["status"] == "not_available"
    assert by_key["duplicate_classification"]["status"] == "not_available"
    assert by_key["family_duplicate_classification"]["status"] == "not_available"
    assert by_key["kaks_pair_manifest"]["status"] == "not_available"
    assert by_key["kaks_pairs"]["status"] == "not_available"
    assert by_key["summary_report"]["status"] == "available"
    assert by_key["final_report"]["status"] == "available"
    assert by_key["report_index"]["status"] == "available"
    assert by_key["wgd_event_evidence"]["status"] == "not_available"
    assert by_key["family_wgd_event_membership"]["status"] == "not_available"
    assert by_key["family_event_retention_summary"]["status"] == "not_available"


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
    assert (outdir / "report" / "report_index.tsv").exists()
    assert "family_counts" in completed.stdout
