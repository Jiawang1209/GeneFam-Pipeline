import subprocess
import sys


def test_run_kaks_smoke_writes_normalized_selection_table(tmp_path):
    outdir = tmp_path / "kaks_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_kaks_smoke.py",
            "--kaks",
            "tests/fixtures/kaks/kaks_calculator.tsv",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "normalized_kaks" in completed.stdout
    normalized = (outdir / "tables/normalized_kaks.tsv").read_text(encoding="utf-8")
    assert normalized.startswith("gene_a\tgene_b\tka\tks\tka_ks\tp_value\tselection_category\n")
    assert "\tpurifying\n" in normalized
    assert "\tneutral\n" in normalized
    assert "\tpositive\n" in normalized

    summary = (outdir / "kaks_smoke.md").read_text(encoding="utf-8")
    assert "Input pairs: 3" in summary
    assert "purifying: 1" in summary
    assert "neutral: 1" in summary
    assert "positive: 1" in summary
