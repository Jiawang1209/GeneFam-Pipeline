import csv
import subprocess
import sys
from pathlib import Path

from bin.genefam.assemble_report import assemble_report


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_assemble_report_renders_output_availability_and_wgd_sections():
    report_index = [
        {
            "key": "family_counts",
            "path": "tables/family_counts.tsv",
            "status": "available",
            "description": "Per-species gene family member counts",
        },
        {
            "key": "family_event_retention_summary",
            "path": "tables/family_event_retention_summary.tsv",
            "status": "available",
            "description": "Family gene counts by duplicate type and WGD event",
        },
    ]
    wgd_event_evidence = [
        {
            "wgd_layer": "WGD_layer_1",
            "pair_count": "12",
            "ks_min": "0.1000",
            "ks_median": "0.1800",
            "ks_max": "0.3000",
            "event_name": "alpha",
            "interpretation_status": "configured_named_event",
            "evidence_source": "literature",
            "species_scope": "Brassicaceae",
            "expected_relative_age": "recent",
        }
    ]
    family_event_retention = [
        {
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "duplicate_type": "WGD/segmental",
            "family_gene_count": "4",
            "pair_evidence_count": "6",
            "gene_ids": "AT1,AT2,AT3,AT4",
        }
    ]
    retention_enrichment = [
        {
            "duplicate_type": "WGD/segmental",
            "family_count": "4",
            "family_total": "5",
            "background_count": "20",
            "background_total": "100",
            "fold_enrichment": "4.0000",
            "p_value": "0.001",
        }
    ]
    plot_manifest = [
        {"plot_key": "family_counts", "path": "plots/family_counts.pdf", "description": "Family counts"},
        {"plot_key": "kaks", "path": "plots/ks_distribution.pdf", "description": "Ks distribution"},
    ]

    report = assemble_report(
        project_name="GeneFam demo",
        gene_family="GDSL",
        report_index_rows=report_index,
        wgd_event_evidence=wgd_event_evidence,
        family_event_retention=family_event_retention,
        retention_enrichment=retention_enrichment,
        plot_manifest=plot_manifest,
    )

    assert "# GeneFam-Pipeline Final Report" in report
    assert "Project: GeneFam demo" in report
    assert "Gene family: GDSL" in report
    assert "| family_counts | available | tables/family_counts.tsv | Per-species gene family member counts |" in report
    assert "## WGD Event Evidence" in report
    assert (
        "| wgd_layer | event_name | pair_count | ks_median | interpretation_status | evidence_source | species_scope | expected_relative_age |"
        in report
    )
    assert "| WGD_layer_1 | alpha | 12 | 0.1800 | configured_named_event | literature | Brassicaceae | recent |" in report
    assert "## Family Event Retention" in report
    assert "| WGD_layer_1 | alpha | WGD/segmental | 4 | 6 | AT1,AT2,AT3,AT4 |" in report
    assert "## Duplicate-Type Retention Enrichment" in report
    assert "| WGD/segmental | 4 | 5 | 4.0000 | 0.001 |" in report
    assert "## Plots" in report
    assert "| family_counts | plots/family_counts.pdf | Family counts |" in report


def test_assemble_report_cli_writes_markdown(tmp_path):
    report_index = tmp_path / "report_index.tsv"
    wgd_events = tmp_path / "wgd_event_evidence.tsv"
    plot_manifest = tmp_path / "plot_manifest.tsv"
    out_path = tmp_path / "final_report.md"
    report_index.write_text(
        "key\tpath\tstatus\tdescription\n"
        "family_counts\ttables/family_counts.tsv\tavailable\tPer-species counts\n",
        encoding="utf-8",
    )
    wgd_events.write_text(
        "wgd_layer\tpair_count\tks_min\tks_median\tks_max\tevent_name\tinterpretation_status\tevidence_source\tspecies_scope\texpected_relative_age\n"
        "WGD_layer_1\t12\t0.1000\t0.1800\t0.3000\talpha\tconfigured_named_event\tliterature\tBrassicaceae\trecent\n",
        encoding="utf-8",
    )
    plot_manifest.write_text(
        "plot_key\tpath\tdescription\nfamily_counts\tplots/family_counts.pdf\tFamily counts\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/assemble_report.py",
            "--project-name",
            "GeneFam demo",
            "--gene-family",
            "GDSL",
            "--report-index",
            str(report_index),
            "--wgd-event-evidence",
            str(wgd_events),
            "--plot-manifest",
            str(plot_manifest),
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    text = out_path.read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Final Report" in text
    assert "| WGD_layer_1 | alpha | 12 | 0.1800 | configured_named_event | literature | Brassicaceae | recent |" in text
    assert "| family_counts | plots/family_counts.pdf | Family counts |" in text


def test_assemble_report_cli_supports_standard_branch_without_wgd_tables(tmp_path):
    report_index = tmp_path / "report_index.tsv"
    plot_manifest = tmp_path / "plot_manifest.tsv"
    out_path = tmp_path / "final_report.md"
    report_index.write_text(
        "key\tpath\tstatus\tdescription\n"
        "family_members_faa\tfamily_members.faa\tavailable\tFamily member peptide FASTA\n",
        encoding="utf-8",
    )
    plot_manifest.write_text(
        "plot_key\tpath\tdescription\nfamily_counts\tplots/family_counts.pdf\tFamily counts\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/assemble_report.py",
            "--project-name",
            "GDSL demo",
            "--gene-family",
            "GDSL",
            "--report-index",
            str(report_index),
            "--plot-manifest",
            str(plot_manifest),
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    text = out_path.read_text(encoding="utf-8")
    assert "Project: GDSL demo" in text
    assert "| family_members_faa | available | family_members.faa | Family member peptide FASTA |" in text
    assert "No WGD event evidence table was available for this run." in text
