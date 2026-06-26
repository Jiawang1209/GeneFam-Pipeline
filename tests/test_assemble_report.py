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
    software_versions = [
        {"component": "Nextflow", "kind": "command", "version": "26.04.4", "status": "detected", "source": "nextflow -version"},
        {"component": "ggNetView", "kind": "R_package", "version": "version_not_detected", "status": "version_not_detected", "source": "packageVersion(\"ggNetView\")"},
    ]
    figure_interpretations = [
        {
            "figure_key": "family_counts",
            "title": "Family copy number and member count overview",
            "input_data": "Family member count table",
            "what_figure_shows": "Per-species member counts.",
            "key_observations": "Inspect expansion or contraction.",
            "biological_interpretation": "High-copy species may indicate expansion.",
            "qc_warnings": "Smoke/demo data caveat.",
            "output_path": "plots/family_counts.pdf",
        }
    ]
    run_config_snapshot = [
        {"key": "project.name", "value": "GeneFam demo"},
        {"key": "runtime.environment", "value": "GeneFamilyFlow"},
        {"key": "selected_species", "value": "Arabidopsis_thaliana,Brassica_rapa"},
        {"key": "identification.final_rule", "value": "intersection"},
    ]

    report = assemble_report(
        project_name="GeneFam demo",
        gene_family="GDSL",
        report_index_rows=report_index,
        run_config_snapshot=run_config_snapshot,
        wgd_event_evidence=wgd_event_evidence,
        family_event_retention=family_event_retention,
        retention_enrichment=retention_enrichment,
        plot_manifest=plot_manifest,
        software_versions=software_versions,
        figure_interpretations=figure_interpretations,
    )

    assert "# GeneFam-Pipeline Final Report" in report
    assert "Project: GeneFam demo" in report
    assert "Gene family: GDSL" in report
    assert "## Executive Summary" in report
    assert "- Available outputs: 2" in report
    assert "- Registered plots: 2" in report
    assert "- Named WGD events with evidence: 1" in report
    assert "## Methods Summary" in report
    assert "HMMER/DIAMOND" in report
    assert "MCScanX" in report
    assert "Ka/Ks" in report
    assert "### Software Versions" in report
    assert "| Nextflow | command | 26.04.4 | detected | nextflow -version |" in report
    assert "| ggNetView | R_package | version_not_detected | version_not_detected | packageVersion(\"ggNetView\") |" in report
    assert "## Figure Result Interpretations" in report
    assert "### family_counts: Family copy number and member count overview" in report
    assert "- Biological interpretation: High-copy species may indicate expansion." in report
    assert "## Results Package Inventory" in report
    assert "### Available Tables" in report
    assert "| family_event_retention_summary | tables/family_event_retention_summary.tsv | Family gene counts by duplicate type and WGD event |" in report
    assert "### Figures" in report
    assert "| kaks | plots/ks_distribution.pdf | Ks distribution |" in report
    assert "## Reproducibility Note" in report
    assert "GeneFamilyFlow" in report
    assert "/usr/local/bin/R" in report
    assert "## Run Configuration Snapshot" in report
    assert "| runtime.environment | GeneFamilyFlow |" in report
    assert "| selected_species | Arabidopsis_thaliana,Brassica_rapa |" in report
    assert "| identification.final_rule | intersection |" in report
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
    run_config = tmp_path / "run_config_snapshot.tsv"
    wgd_events = tmp_path / "wgd_event_evidence.tsv"
    plot_manifest = tmp_path / "plot_manifest.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    out_path = tmp_path / "final_report.md"
    report_index.write_text(
        "key\tpath\tstatus\tdescription\n"
            "family_counts\ttables/family_counts.tsv\tavailable\tPer-species counts\n",
        encoding="utf-8",
    )
    run_config.write_text(
        "key\tvalue\nruntime.environment\tGeneFamilyFlow\nselected_species\tArabidopsis_thaliana,Brassica_rapa\n",
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
    software_versions.write_text(
        "component\tkind\tversion\tstatus\tsource\nNextflow\tcommand\t26.04.4\tdetected\tnextflow -version\n",
        encoding="utf-8",
    )
    figure_interpretations.write_text(
        "figure_key\ttitle\tinput_data\twhat_figure_shows\tkey_observations\tbiological_interpretation\tqc_warnings\toutput_path\n"
        "family_counts\tFamily copy number and member count overview\tFamily counts\tCounts by species\tInspect counts\tExpansion signal\tSmoke data\tplots/family_counts.pdf\n",
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
            "--run-config-snapshot",
            str(run_config),
            "--wgd-event-evidence",
            str(wgd_events),
            "--plot-manifest",
            str(plot_manifest),
            "--software-versions",
            str(software_versions),
            "--figure-interpretations",
            str(figure_interpretations),
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
    assert "## Executive Summary" in text
    assert "## Results Package Inventory" in text
    assert "### Software Versions" in text
    assert "## Figure Result Interpretations" in text
    assert "| runtime.environment | GeneFamilyFlow |" in text
    assert "| selected_species | Arabidopsis_thaliana,Brassica_rapa |" in text
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
