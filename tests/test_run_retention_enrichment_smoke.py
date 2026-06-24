import csv
import subprocess
import sys


def read_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_run_retention_enrichment_smoke_writes_enrichment_outputs(tmp_path):
    outdir = tmp_path / "retention_enrichment_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_retention_enrichment_smoke.py",
            "--family-members",
            "examples/prepared_wgd_handoff/family_candidates.tsv",
            "--duplicates",
            "examples/prepared_wgd_handoff/duplicate_types.tsv",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "retention_enrichment" in completed.stdout
    assert (outdir / "tables/normalized_duplicate_types.tsv").exists()
    assert (outdir / "tables/family_duplicate_classification.tsv").exists()
    enrichment = read_tsv(outdir / "tables/retention_enrichment.tsv")
    by_type = {row["duplicate_type"]: row for row in enrichment}

    assert set(by_type) == {"WGD/segmental", "dispersed", "singleton", "tandem"}
    assert by_type["WGD/segmental"]["family_count"] == "8"
    assert by_type["WGD/segmental"]["family_total"] == "8"
    assert by_type["WGD/segmental"]["background_count"] == "8"
    assert by_type["WGD/segmental"]["background_total"] == "12"
    assert by_type["WGD/segmental"]["fold_enrichment"] == "1.5000"
    assert by_type["tandem"]["family_count"] == "0"

    summary = (outdir / "retention_enrichment_smoke.md").read_text(encoding="utf-8")
    assert "Family genes: 8" in summary
    assert "Background genes: 12" in summary
    assert "Enrichment rows: 4" in summary
