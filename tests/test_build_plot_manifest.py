import subprocess
import sys

from bin.genefam.build_plot_manifest import build_plot_manifest


def test_build_plot_manifest_records_known_plot_outputs():
    rows = build_plot_manifest(
        [
            ("family_counts", "plots/family_counts.pdf", "Family member counts by species"),
            ("ks_distribution", "plots/ks_distribution.pdf", "Ks distribution for duplicated pairs"),
        ]
    )

    assert rows == [
        {
            "plot_key": "family_counts",
            "path": "plots/family_counts.pdf",
            "description": "Family member counts by species",
        },
        {
            "plot_key": "ks_distribution",
            "path": "plots/ks_distribution.pdf",
            "description": "Ks distribution for duplicated pairs",
        },
    ]


def test_build_plot_manifest_cli_writes_tsv(tmp_path):
    out_path = tmp_path / "plot_manifest.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_plot_manifest.py",
            "--plot",
            "family_counts=plots/family_counts.pdf=Family member counts by species",
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert out_path.read_text(encoding="utf-8") == (
        "plot_key\tpath\tdescription\n"
        "family_counts\tplots/family_counts.pdf\tFamily member counts by species\n"
    )
