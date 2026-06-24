import subprocess
import sys

from bin.genefam.build_standard_report_index import build_report_index, published_paths, read_tsv


def test_build_standard_report_index_marks_core_outputs_available():
    rows = build_report_index(
        {
            "species_manifest": "tables/species_manifest.tsv",
            "family_candidates": "tables/family_candidates.tsv",
            "family_counts": "tables/family_counts.tsv",
            "family_members_faa": "sequences/family_members.faa",
            "alignment_manifest": "tables/alignment_manifest.tsv",
            "phylogeny_manifest": "tables/phylogeny_manifest.tsv",
            "chromosome_locations": "tables/chromosome_locations.tsv",
            "family_expression": "",
            "plot_manifest": "tables/plot_manifest.tsv",
        }
    )

    assert rows[0] == {
        "key": "species_manifest",
        "path": "tables/species_manifest.tsv",
        "status": "available",
        "description": "Selected species and input files",
    }
    assert {row["key"] for row in rows} >= {
        "family_members_faa",
        "alignment_manifest",
        "phylogeny_manifest",
        "chromosome_locations",
        "family_expression",
    }
    assert next(row for row in rows if row["key"] == "family_expression")["status"] == "missing"


def test_published_paths_map_standard_outputs_to_user_results_tree():
    paths = published_paths("results/nextflow_standard_smoke/standard", family_expression_available=False)

    assert paths == {
        "species_manifest": "results/nextflow_standard_smoke/standard/tables/species_manifest.tsv",
        "family_candidates": "results/nextflow_standard_smoke/standard/tables/family_candidates.tsv",
        "family_counts": "results/nextflow_standard_smoke/standard/tables/family_counts.tsv",
        "family_members_faa": "results/nextflow_standard_smoke/standard/sequences/family_members.faa",
        "alignment_manifest": "results/nextflow_standard_smoke/standard/tables/alignment_manifest.tsv",
        "phylogeny_manifest": "results/nextflow_standard_smoke/standard/tables/phylogeny_manifest.tsv",
        "chromosome_locations": "results/nextflow_standard_smoke/standard/tables/chromosome_locations.tsv",
        "family_expression": "",
        "plot_manifest": "results/nextflow_standard_smoke/standard/report/plot_manifest.tsv",
    }


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
            "--chromosome-locations",
            "chromosome_locations.tsv",
            "--family-expression",
            "",
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


def test_build_standard_report_index_cli_can_write_published_paths(tmp_path):
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
            "--chromosome-locations",
            "chromosome_locations.tsv",
            "--family-expression",
            "",
            "--plot-manifest",
            "plot_manifest.tsv",
            "--published-outdir",
            "results/demo",
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    rows = {row["key"]: row for row in read_tsv(out)}
    assert rows["family_candidates"]["path"] == "results/demo/tables/family_candidates.tsv"
    assert rows["family_members_faa"]["path"] == "results/demo/sequences/family_members.faa"
    assert rows["plot_manifest"]["path"] == "results/demo/report/plot_manifest.tsv"
