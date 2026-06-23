import subprocess
import sys

from bin.genefam.summarize_family_event_retention import summarize_family_event_retention


def test_summarize_family_event_retention_counts_unique_genes_and_pair_evidence():
    rows = [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1",
            "duplicate_type": "WGD/segmental",
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "partner_gene": "AT2",
            "ks": "0.10",
            "confidence": "configured",
        },
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1",
            "duplicate_type": "WGD/segmental",
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "partner_gene": "AT3",
            "ks": "0.11",
            "confidence": "configured",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "Bra1",
            "duplicate_type": "tandem",
            "wgd_layer": "WGD_layer_2",
            "event_name": "beta",
            "partner_gene": "Bra2",
            "ks": "0.50",
            "confidence": "configured",
        },
    ]

    assert summarize_family_event_retention(rows) == [
        {
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "duplicate_type": "WGD/segmental",
            "family_gene_count": "1",
            "pair_evidence_count": "2",
            "gene_ids": "AT1",
        },
        {
            "wgd_layer": "WGD_layer_2",
            "event_name": "beta",
            "duplicate_type": "tandem",
            "family_gene_count": "1",
            "pair_evidence_count": "1",
            "gene_ids": "Bra1",
        },
    ]


def test_summarize_family_event_retention_cli_writes_summary(tmp_path):
    input_path = tmp_path / "family_wgd_events.tsv"
    out_path = tmp_path / "summary.tsv"
    input_path.write_text(
        "species_id\tgene_id\tduplicate_type\twgd_layer\tevent_name\tpartner_gene\tks\tconfidence\n"
        "Arabidopsis_thaliana\tAT1\tWGD/segmental\tWGD_layer_1\talpha\tAT2\t0.10\tconfigured\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/summarize_family_event_retention.py",
            "--family-wgd-events",
            str(input_path),
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert out_path.read_text(encoding="utf-8") == (
        "wgd_layer\tevent_name\tduplicate_type\tfamily_gene_count\tpair_evidence_count\tgene_ids\n"
        "WGD_layer_1\talpha\tWGD/segmental\t1\t1\tAT1\n"
    )
