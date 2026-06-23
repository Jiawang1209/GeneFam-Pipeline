import subprocess
import sys

from bin.genefam.build_standard_report_index import build_report_index, read_tsv


def test_build_standard_report_index_marks_core_outputs_available():
    rows = build_report_index(
        {
            "species_manifest": "tables/species_manifest.tsv",
            "family_candidates": "tables/family_candidates.tsv",
            "family_counts": "tables/family_counts.tsv",
            "family_members_faa": "sequences/family_members.faa",
            "alignment_manifest": "tables/alignment_manifest.tsv",
            "phylogeny_manifest": "tables/phylogeny_manifest.tsv",
            "plot_manifest": "tables/plot_manifest.tsv",
        }
    )

    assert rows[0] == {
        "key": "species_manifest",
        "path": "tables/species_manifest.tsv",
        "status": "available",
        "description": "Selected species and input files",
    }
    assert {row["key"] for row in rows} >= {"family_members_faa", "alignment_manifest", "phylogeny_manifest"}


def test_build_standard_report_index_cli_writes_tsv(tmp_path):
    out = tmp_path / "report_index.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_standard_report_index.py",
            "--species-manifest",
            "species_manifest.tsv",
            "--family-candidates",
            "family_candidates.tsv",
            "--family-counts",
            "family_counts.tsv",
            "--family-members-faa",
            "family_members.faa",
            "--alignment-manifest",
            "alignment_manifest.tsv",
            "--phylogeny-manifest",
            "phylogeny_manifest.tsv",
            "--plot-manifest",
            "plot_manifest.tsv",
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert read_tsv(out)[-1] == {
        "key": "plot_manifest",
        "path": "plot_manifest.tsv",
        "status": "available",
        "description": "Generated plot inventory",
    }
