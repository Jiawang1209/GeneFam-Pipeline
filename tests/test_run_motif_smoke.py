import subprocess
import sys


def test_run_motif_smoke_writes_motif_summary(tmp_path):
    outdir = tmp_path / "motif_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_motif_smoke.py",
            "--meme-txt",
            "tests/fixtures/mock_evidence/meme.txt",
            "--family-name",
            "GDSL",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "motif_summary" in completed.stdout
    motif_summary = (outdir / "tables/motif_summary.tsv").read_text(encoding="utf-8")
    assert motif_summary.startswith("family_name\tmotif_id\tmotif_name\twidth\tsites\tevalue\n")
    assert "GDSL\t1\tGDSL_motif_1\t11\t18\t2.3e-12\n" in motif_summary
    assert "GDSL\t2\tGDSL_motif_2\t7\t12\t4.8e-06\n" in motif_summary

    summary = (outdir / "motif_smoke.md").read_text(encoding="utf-8")
    assert "Parsed motifs: 2" in summary
    assert "GDSL_motif_1" in summary
    assert "GDSL_motif_2" in summary
