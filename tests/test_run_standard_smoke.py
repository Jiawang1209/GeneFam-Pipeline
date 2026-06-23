import subprocess
import sys


def test_run_standard_smoke_writes_standard_branch_outputs(tmp_path):
    outdir = tmp_path / "standard_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_standard_smoke.py",
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
    expected = [
        "tables/species_manifest.tsv",
        "tables/family_candidates.tsv",
        "tables/family_counts.tsv",
        "sequences/family_members.faa",
        "tables/alignment_manifest.tsv",
        "tables/phylogeny_manifest.tsv",
        "report/report_index.tsv",
        "report/final_report.md",
    ]
    for relative_path in expected:
        assert (outdir / relative_path).exists(), relative_path
    assert "standard_final_report" in completed.stdout
