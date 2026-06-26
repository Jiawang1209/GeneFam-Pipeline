import subprocess
import sys

from bin.genefam.build_kaks_plot_annotations import build_kaks_plot_annotations


def test_build_kaks_plot_annotations_summarizes_named_wgd_layers():
    rows = [
        {"gene_a": "A1", "gene_b": "A2", "ks": "0.10", "wgd_layer": "WGD_layer_1", "event_name": "alpha", "confidence": "configured"},
        {"gene_a": "A3", "gene_b": "A4", "ks": "0.20", "wgd_layer": "WGD_layer_1", "event_name": "alpha", "confidence": "configured"},
        {"gene_a": "B1", "gene_b": "B2", "ks": "0.55", "wgd_layer": "WGD_layer_2", "event_name": "beta", "confidence": "configured"},
    ]

    annotations = build_kaks_plot_annotations(rows)

    assert annotations == [
        {
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "pair_count": "2",
            "ks_min": "0.1000",
            "ks_median": "0.1500",
            "ks_max": "0.2000",
            "label_position": "0.1500",
            "label": "alpha (WGD_layer_1, n=2)",
        },
        {
            "wgd_layer": "WGD_layer_2",
            "event_name": "beta",
            "pair_count": "1",
            "ks_min": "0.5500",
            "ks_median": "0.5500",
            "ks_max": "0.5500",
            "label_position": "0.5500",
            "label": "beta (WGD_layer_2, n=1)",
        },
    ]


def test_build_kaks_plot_annotations_cli_writes_tsv(tmp_path):
    classified = tmp_path / "wgd_layers.tsv"
    out = tmp_path / "kaks_wgd_annotations.tsv"
    classified.write_text(
        "\n".join(
            [
                "gene_a\tgene_b\tks\twgd_layer\tevent_name\tconfidence",
                "G1\tG2\t1.20\tWGD_layer_3\tgamma\tconfigured",
                "G3\tG4\t1.80\tWGD_layer_4\ttheta\tconfigured",
                "",
            ]
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_kaks_plot_annotations.py",
            "--classified-pairs",
            str(classified),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    text = out.read_text(encoding="utf-8")
    assert text.startswith("wgd_layer\tevent_name\tpair_count\tks_min\tks_median\tks_max\tlabel_position\tlabel\n")
    assert "WGD_layer_3\tgamma\t1\t1.2000\t1.2000\t1.2000\t1.2000\tgamma (WGD_layer_3, n=1)" in text
