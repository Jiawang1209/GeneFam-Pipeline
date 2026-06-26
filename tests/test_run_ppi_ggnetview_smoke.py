import subprocess
import sys


def test_run_ppi_ggnetview_smoke_writes_explicit_dependency_status(tmp_path):
    outdir = tmp_path / "ppi_ggnetview"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_ppi_ggnetview_smoke.py",
            "--outdir",
            str(outdir),
            "--force-missing",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    status = (outdir / "ppi_ggnetview_smoke.tsv").read_text(encoding="utf-8")
    assert "check\tstatus\tpackage\tversion\tnote\n" in status
    assert "ppi_ggnetview\tmissing_dependency\tggNetView\tversion_not_detected" in status
    summary = (outdir / "ppi_ggnetview_smoke.md").read_text(encoding="utf-8")
    assert "ggNetView PPI Smoke" in summary
    assert "missing_dependency" in summary
