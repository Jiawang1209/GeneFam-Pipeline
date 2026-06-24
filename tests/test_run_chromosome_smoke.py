import subprocess
import sys


def test_run_chromosome_smoke_writes_locations_from_species_bank(tmp_path):
    outdir = tmp_path / "chromosome_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_chromosome_smoke.py",
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
    assert "chromosome_locations" in completed.stdout
    locations = (outdir / "tables/chromosome_locations.tsv").read_text(encoding="utf-8")
    assert locations.startswith("species_id\tgene_id\tseqid\tstart\tend\tstrand\n")
    assert "Arabidopsis_thaliana\tAT1G01010\tChr1\t100\t500\t+\n" in locations
    assert "Brassica_rapa\tBraA010001\tA01\t200\t900\t-\n" in locations

    summary = (outdir / "chromosome_smoke.md").read_text(encoding="utf-8")
    assert "Located genes: 2" in summary
    assert "Species represented: 2" in summary
