import subprocess
import sys


def test_run_synteny_smoke_writes_mcscanx_parser_outputs(tmp_path):
    outdir = tmp_path / "synteny_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_synteny_smoke.py",
            "--collinearity",
            "tests/fixtures/mcscanx/sample.collinearity",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "syntenic_pairs" in completed.stdout
    syntenic_pairs = outdir / "tables/syntenic_pairs.tsv"
    assert syntenic_pairs.read_text(encoding="utf-8") == (
        "block_id\tblock_score\tblock_evalue\tblock_pair_count\tgene_a\tgene_b\tpair_evalue\n"
        "0\t123.4\t1e-20\t2\tAT1G01010\tBraA010001\t1e-50\n"
        "0\t123.4\t1e-20\t2\tAT1G01020\tBraA010002\t2e-40\n"
    )
    summary = outdir / "synteny_smoke.md"
    assert "Parsed syntenic pairs: 2" in summary.read_text(encoding="utf-8")
