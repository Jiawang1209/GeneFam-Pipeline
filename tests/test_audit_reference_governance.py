import subprocess
import sys


def test_reference_governance_cli_allows_untracked_reference_sources(tmp_path):
    outdir = tmp_path / "reference_governance"
    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_reference_governance.py",
            "--status-line",
            "?? Reference/paper/source_code/example.py",
            "--status-line",
            "?? Reference/paper/source_data/example.tsv",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    tsv = (outdir / "reference_governance.tsv").read_text(encoding="utf-8")
    assert "status\tcount\tpaths\n" in tsv
    assert "untracked\t2\tReference/paper/source_code/example.py; Reference/paper/source_data/example.tsv\n" in tsv
    markdown = (outdir / "reference_governance.md").read_text(encoding="utf-8")
    assert "Tracked changes: 0" in markdown
    assert "Untracked reference files: 2" in markdown


def test_reference_governance_cli_fails_on_tracked_reference_changes(tmp_path):
    outdir = tmp_path / "reference_governance"
    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_reference_governance.py",
            "--status-line",
            " M Reference/paper/source_code/plot.py",
            "--status-line",
            "D  Reference/paper/source_data/table.tsv",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    markdown = (outdir / "reference_governance.md").read_text(encoding="utf-8")
    assert "Tracked changes: 2" in markdown
    assert "Reference/paper/source_code/plot.py" in markdown
    assert "Reference/paper/source_data/table.tsv" in markdown
