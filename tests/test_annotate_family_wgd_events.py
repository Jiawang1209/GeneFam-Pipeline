import subprocess
import sys

from bin.genefam.annotate_family_wgd_events import annotate_family_wgd_events


def test_annotate_family_wgd_events_emits_one_row_per_family_gene_pair_hit():
    family_duplicates = [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01010",
            "duplicate_type": "WGD/segmental",
            "raw_duplicate_type": "WGD",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA010001",
            "duplicate_type": "tandem",
            "raw_duplicate_type": "Tandem",
        },
    ]
    classified_pairs = [
        {
            "gene_a": "AT1G01010",
            "gene_b": "AT1G01020",
            "ks": "0.12",
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "confidence": "configured",
        },
        {
            "gene_a": "OTHER",
            "gene_b": "BraA010001",
            "ks": "0.55",
            "wgd_layer": "WGD_layer_2",
            "event_name": "beta",
            "confidence": "configured",
        },
        {
            "gene_a": "UNRELATED1",
            "gene_b": "UNRELATED2",
            "ks": "1.20",
            "wgd_layer": "WGD_layer_3",
            "event_name": "gamma",
            "confidence": "configured",
        },
    ]

    assert annotate_family_wgd_events(family_duplicates, classified_pairs) == [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01010",
            "duplicate_type": "WGD/segmental",
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "partner_gene": "AT1G01020",
            "ks": "0.12",
            "confidence": "configured",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA010001",
            "duplicate_type": "tandem",
            "wgd_layer": "WGD_layer_2",
            "event_name": "beta",
            "partner_gene": "OTHER",
            "ks": "0.55",
            "confidence": "configured",
        },
    ]


def test_annotate_family_wgd_events_emits_both_family_genes_when_pair_is_internal():
    family_duplicates = [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1", "duplicate_type": "WGD/segmental"},
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT2", "duplicate_type": "WGD/segmental"},
    ]
    classified_pairs = [
        {
            "gene_a": "AT1",
            "gene_b": "AT2",
            "ks": "0.10",
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "confidence": "configured",
        }
    ]

    rows = annotate_family_wgd_events(family_duplicates, classified_pairs)

    assert [row["gene_id"] for row in rows] == ["AT1", "AT2"]
    assert [row["partner_gene"] for row in rows] == ["AT2", "AT1"]


def test_annotate_family_wgd_events_cli_writes_event_membership(tmp_path):
    family_path = tmp_path / "family_duplicates.tsv"
    pairs_path = tmp_path / "classified_pairs.tsv"
    out_path = tmp_path / "family_wgd_events.tsv"
    family_path.write_text(
        "species_id\tgene_id\tduplicate_type\traw_duplicate_type\n"
        "Arabidopsis_thaliana\tAT1G01010\tWGD/segmental\tWGD\n",
        encoding="utf-8",
    )
    pairs_path.write_text(
        "gene_a\tgene_b\tks\twgd_layer\tevent_name\tconfidence\n"
        "AT1G01010\tAT1G01020\t0.12\tWGD_layer_1\talpha\tconfigured\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/annotate_family_wgd_events.py",
            "--family-duplicates",
            str(family_path),
            "--classified-pairs",
            str(pairs_path),
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert out_path.read_text(encoding="utf-8") == (
        "species_id\tgene_id\tduplicate_type\twgd_layer\tevent_name\tpartner_gene\tks\tconfidence\n"
        "Arabidopsis_thaliana\tAT1G01010\tWGD/segmental\tWGD_layer_1\talpha\tAT1G01020\t0.12\tconfigured\n"
    )
