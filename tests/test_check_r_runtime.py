import subprocess
import sys
from pathlib import Path


def _write_fake_r(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)


def test_check_r_runtime_records_passed_health_report(tmp_path):
    fake_r = tmp_path / "R"
    outdir = tmp_path / "r_health"
    _write_fake_r(fake_r, "echo 'R version 4.4.0 smoke'\n")

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/check_r_runtime.py",
            "--r-bin",
            str(fake_r),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    tsv = (outdir / "r_runtime_health.tsv").read_text(encoding="utf-8")
    md = (outdir / "r_runtime_health.md").read_text(encoding="utf-8")
    assert "r_runtime\tpassed\t0" in tsv
    assert "R version 4.4.0 smoke" in tsv
    assert "Status: passed" in md


def test_check_r_runtime_records_failed_health_report_with_exit_code(tmp_path):
    fake_r = tmp_path / "R"
    outdir = tmp_path / "r_health"
    _write_fake_r(fake_r, "echo 'R startup killed' >&2\nexit 137\n")

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/check_r_runtime.py",
            "--r-bin",
            str(fake_r),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    tsv = (outdir / "r_runtime_health.tsv").read_text(encoding="utf-8")
    md = (outdir / "r_runtime_health.md").read_text(encoding="utf-8")
    assert "r_runtime\tfailed\t137" in tsv
    assert "R startup killed" in tsv
    assert "Status: failed" in md
    assert "R startup killed" in md
