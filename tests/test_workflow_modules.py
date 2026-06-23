from pathlib import Path


def test_hmmer_module_writes_normalized_tsv():
    module = Path("workflows/modules/hmmer_search.nf").read_text(encoding="utf-8")

    assert "parse_hmmer_domtbl.py" in module
    assert "filter_hmmer_domains.py" in module
    assert "--species-id ${species_id}" in module
    assert "--min-domain-coverage ${params.hmmer_min_domain_coverage}" in module
    assert 'path("${species_id}.${hmm_id}.hmmer.tsv")' in module


def test_diamond_module_writes_normalized_tsv():
    module = Path("workflows/modules/diamond_search.nf").read_text(encoding="utf-8")

    assert "parse_diamond_outfmt6.py" in module
    assert "--species-id ${species_id}" in module
    assert "--out ${species_id}.diamond.tsv" in module


def test_duplication_retention_module_exposes_wgd_helper_processes():
    module = Path("workflows/modules/duplication_retention.nf").read_text(encoding="utf-8")

    assert "process NORMALIZE_DUPLICATE_TYPES" in module
    assert "normalize_duplicate_types.py" in module
    assert "--duplicates ${duplicates}" in module
    assert "--out normalized_duplicate_types.tsv" in module

    assert "process JOIN_FAMILY_DUPLICATES" in module
    assert "join_family_duplicates.py" in module
    assert "--family-members ${family_members}" in module
    assert "--duplicates ${normalized_duplicates}" in module
    assert "--out family_duplicate_classification.tsv" in module

    assert "process CLASSIFY_WGD_LAYERS" in module
    assert "classify_wgd_layers.py" in module
    assert "--bins ${ks_bins}" in module
    assert "--out wgd_layers.tsv" in module

    assert "process BUILD_WGD_EVENT_EVIDENCE" in module
    assert "build_wgd_event_evidence.py" in module
    assert "--events-config ${events_config}" in module
    assert "--out wgd_event_evidence.tsv" in module

    assert "process ANNOTATE_FAMILY_WGD_EVENTS" in module
    assert "annotate_family_wgd_events.py" in module
    assert "--family-duplicates ${family_duplicates}" in module
    assert "--classified-pairs ${classified_pairs}" in module
    assert "--out family_wgd_event_membership.tsv" in module

    assert "process SUMMARIZE_FAMILY_EVENT_RETENTION" in module
    assert "summarize_family_event_retention.py" in module
    assert "--family-wgd-events ${family_wgd_events}" in module
    assert "--out family_event_retention_summary.tsv" in module

    assert "process RETENTION_ENRICHMENT" in module
    assert "retention_enrichment.py" in module
    assert "--family-duplicates ${family_duplicates}" in module
    assert "--background-duplicates ${background_duplicates}" in module
    assert "--out retention_enrichment.tsv" in module


def test_main_workflow_includes_duplication_retention_processes():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "NORMALIZE_DUPLICATE_TYPES" in workflow
    assert "JOIN_FAMILY_DUPLICATES" in workflow
    assert "CLASSIFY_WGD_LAYERS" in workflow
    assert "BUILD_WGD_EVENT_EVIDENCE" in workflow
    assert "ANNOTATE_FAMILY_WGD_EVENTS" in workflow
    assert "SUMMARIZE_FAMILY_EVENT_RETENTION" in workflow
    assert "RETENTION_ENRICHMENT" in workflow


def test_report_module_assembles_final_markdown():
    module = Path("workflows/modules/report.nf").read_text(encoding="utf-8")

    assert "process ASSEMBLE_REPORT" in module
    assert "assemble_report.py" in module
    assert "--project-name ${project_name}" in module
    assert "--gene-family ${gene_family}" in module
    assert "--report-index ${report_index}" in module
    assert "--out final_report.md" in module


def test_main_workflow_includes_report_process():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "include { ASSEMBLE_REPORT } from './modules/report.nf'" in workflow


def test_plot_module_runs_r_scripts_through_configured_r_bin():
    module = Path("workflows/modules/plots.nf").read_text(encoding="utf-8")

    assert "process PLOT_FAMILY_COUNTS" in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/scripts/plot_family_counts.R" in module
    assert "--args ${family_counts} plots" in module
    assert 'path "plots/family_counts.pdf"' in module
    assert 'path "plots/family_counts.png"' in module

    assert "process PLOT_KAKS" in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/scripts/plot_kaks.R" in module
    assert "--args ${kaks_pairs} plots" in module
    assert 'path "plots/ks_distribution.pdf"' in module

    assert "process PLOT_EXPRESSION_HEATMAP" in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/scripts/plot_expression_heatmap.R" in module
    assert "--args ${expression_matrix} plots" in module
    assert 'path "plots/expression_heatmap.pdf"' in module

    assert "process BUILD_PLOT_MANIFEST" in module
    assert "build_plot_manifest.py" in module
    assert "--plot family_counts=plots/family_counts.pdf=Family member counts by species" in module
    assert "--plot ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs" in module
    assert "--plot expression_heatmap=plots/expression_heatmap.pdf=Family member expression heatmap" in module
    assert "--out plot_manifest.tsv" in module


def test_main_workflow_includes_plot_processes():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "PLOT_FAMILY_COUNTS" in workflow
    assert "PLOT_KAKS" in workflow
    assert "PLOT_EXPRESSION_HEATMAP" in workflow
    assert "BUILD_PLOT_MANIFEST" in workflow
