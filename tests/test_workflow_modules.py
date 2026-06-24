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


def test_identification_inputs_module_builds_hmmer_and_diamond_tables():
    module = Path("workflows/modules/identification_inputs.nf").read_text(encoding="utf-8")

    assert "process BUILD_IDENTIFICATION_INPUTS" in module
    assert "build_identification_inputs.py" in module
    assert "--species-manifest ${species_manifest}" in module
    assert 'path "identification_inputs/hmmer_inputs.tsv"' in module
    assert 'path "identification_inputs/diamond_inputs.tsv"' in module


def test_domain_filter_module_can_concatenate_species_candidate_tables():
    module = Path("workflows/modules/domain_filter.nf").read_text(encoding="utf-8")

    assert "process MOCK_IDENTIFICATION_EVIDENCE" in module
    assert "${mock_evidence_dir}/hmmer.tsv" in module
    assert "${mock_evidence_dir}/diamond.tsv" in module
    assert 'tuple val("mock"), path("hmmer.tsv"), path("diamond.tsv")' in module

    assert "process CONCAT_FAMILY_CANDIDATES" in module
    assert 'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true' in module
    assert "concat_tsv.py" in module
    assert "--inputs ${candidate_tables}" in module
    assert "--out family_candidates.tsv" in module


def test_standard_postprocess_module_extracts_family_sequences_and_report_index():
    module = Path("workflows/modules/standard_postprocess.nf").read_text(encoding="utf-8")

    assert "process EXTRACT_FAMILY_SEQUENCES" in module
    assert 'publishDir "${params.outdir}/sequences", mode: "copy", overwrite: true' in module
    assert "extract_family_sequences.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--out family_members.faa" in module

    assert "process BUILD_STANDARD_REPORT_INDEX" in module
    assert 'publishDir "${params.outdir}/report", mode: "copy", overwrite: true' in module
    assert "build_standard_report_index.py" in module
    assert "--family-members-faa ${family_members_faa}" in module
    assert "--phylogeny-manifest ${phylogeny_manifest}" in module
    assert "--published-outdir ${params.outdir}" in module
    assert "--out report_index.tsv" in module

    assert "process ASSEMBLE_STANDARD_REPORT" in module
    assert 'publishDir "${params.outdir}/report", mode: "copy", overwrite: true' in module
    assert "assemble_report.py" in module
    assert "--project-name ${project_name}" in module
    assert "--gene-family ${gene_family}" in module
    assert "--report-index ${report_index}" in module
    assert "--plot-manifest ${plot_manifest}" in module
    assert "--out final_report.md" in module


def test_main_workflow_wires_standard_identification_branch():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "include { BUILD_IDENTIFICATION_INPUTS } from './modules/identification_inputs.nf'" in workflow
    assert "include { EXTRACT_FAMILY_SEQUENCES; BUILD_STANDARD_REPORT_INDEX; ASSEMBLE_STANDARD_REPORT } from './modules/standard_postprocess.nf'" in workflow
    assert "include { HMMER_SEARCH } from './modules/hmmer_search.nf'" in workflow
    assert "include { DIAMOND_SEARCH } from './modules/diamond_search.nf'" in workflow
    assert "include { DOMAIN_FILTER; CONCAT_FAMILY_CANDIDATES; MOCK_IDENTIFICATION_EVIDENCE } from './modules/domain_filter.nf'" in workflow
    assert "include { FAMILY_SUMMARY } from './modules/family_summary.nf'" in workflow
    assert "} else if (params.run_identification) {" in workflow
    assert "BUILD_IDENTIFICATION_INPUTS(config_ch, PREPARE_SPECIES.out)" in workflow
    assert "HMMER_SEARCH(hmmer_inputs_ch)" in workflow
    assert "DIAMOND_SEARCH(diamond_inputs_ch)" in workflow
    assert "if (params.mock_external_tools)" in workflow
    assert "MOCK_IDENTIFICATION_EVIDENCE(mock_evidence_ch)" in workflow
    assert "joined_evidence_ch = MOCK_IDENTIFICATION_EVIDENCE.out" in workflow
    assert "DOMAIN_FILTER(joined_evidence_ch, final_rule_ch)" in workflow
    assert "CONCAT_FAMILY_CANDIDATES(candidate_tables_ch.collect())" in workflow
    assert "FAMILY_SUMMARY(CONCAT_FAMILY_CANDIDATES.out)" in workflow
    assert "EXTRACT_FAMILY_SEQUENCES(CONCAT_FAMILY_CANDIDATES.out, PREPARE_SPECIES.out)" in workflow
    assert "PREPARE_ALIGNMENT_INPUTS(family_name_ch, EXTRACT_FAMILY_SEQUENCES.out, aligner_ch, alignment_outdir_ch)" in workflow
    assert "PREPARE_PHYLOGENY_INPUTS(PREPARE_ALIGNMENT_INPUTS.out, tree_builder_ch, phylogeny_outdir_ch)" in workflow
    assert "PLOT_FAMILY_COUNTS(FAMILY_SUMMARY.out)" in workflow
    assert "BUILD_PLOT_MANIFEST()" in workflow
    assert "BUILD_STANDARD_REPORT_INDEX(" in workflow
    assert "ASSEMBLE_STANDARD_REPORT(project_name_ch, family_name_ch, BUILD_STANDARD_REPORT_INDEX.out, BUILD_PLOT_MANIFEST.out)" in workflow


def test_duplication_retention_module_exposes_wgd_helper_processes():
    module = Path("workflows/modules/duplication_retention.nf").read_text(encoding="utf-8")

    assert "process NORMALIZE_DUPLICATE_TYPES" in module
    assert 'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true' in module
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

    assert "process BUILD_WGD_REPORT_INDEX" in module
    assert "build_wgd_report_index.py" in module
    assert "--published-outdir ${published_outdir}" in module
    assert "--out report_index.tsv" in module

    assert "process ASSEMBLE_WGD_REPORT" in module
    assert "assemble_report.py" in module
    assert "--wgd-event-evidence ${wgd_event_evidence}" in module
    assert "--family-event-retention ${family_event_retention}" in module
    assert "--retention-enrichment ${retention_enrichment}" in module
    assert "--out final_report.md" in module


def test_main_workflow_includes_duplication_retention_processes():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "NORMALIZE_DUPLICATE_TYPES" in workflow
    assert "JOIN_FAMILY_DUPLICATES" in workflow
    assert "CLASSIFY_WGD_LAYERS" in workflow
    assert "BUILD_WGD_EVENT_EVIDENCE" in workflow
    assert "ANNOTATE_FAMILY_WGD_EVENTS" in workflow
    assert "SUMMARIZE_FAMILY_EVENT_RETENTION" in workflow
    assert "RETENTION_ENRICHMENT" in workflow
    assert "BUILD_WGD_REPORT_INDEX(outdir_ch)" in workflow
    assert "ASSEMBLE_WGD_REPORT(" in workflow


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
    assert 'publishDir "${params.outdir}", mode: "copy", overwrite: true' in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_family_counts.R" in module
    assert "--args ${family_counts} plots" in module
    assert 'path "plots/family_counts.pdf"' in module
    assert 'path "plots/family_counts.png"' in module

    assert "process PLOT_KAKS" in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_kaks.R" in module
    assert "--args ${kaks_pairs} plots" in module
    assert 'path "plots/ks_distribution.pdf"' in module

    assert "process PLOT_EXPRESSION_HEATMAP" in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_expression_heatmap.R" in module
    assert "--args ${expression_matrix} plots" in module
    assert 'path "plots/expression_heatmap.pdf"' in module

    assert "process BUILD_PLOT_MANIFEST" in module
    assert 'publishDir "${params.outdir}/report", mode: "copy", overwrite: true' in module
    assert "build_plot_manifest.py" in module
    assert '--plot "family_counts=plots/family_counts.pdf=Family member counts by species"' in module
    assert '--plot "ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs"' in module
    assert '--plot "expression_heatmap=plots/expression_heatmap.pdf=Family member expression heatmap"' in module
    assert "--out plot_manifest.tsv" in module


def test_standard_nextflow_modules_publish_user_facing_outputs():
    expected = {
        "workflows/modules/prepare_species.nf": ['publishDir "${params.outdir}/tables", mode: "copy", overwrite: true'],
        "workflows/modules/family_summary.nf": ['publishDir "${params.outdir}/tables", mode: "copy", overwrite: true'],
        "workflows/modules/alignment_phylogeny.nf": [
            'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true'
        ],
        "workflows/modules/annotation_integration.nf": [
            'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true'
        ],
    }

    for module_path, snippets in expected.items():
        module = Path(module_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in module, module_path


def test_main_workflow_includes_plot_processes():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "PLOT_FAMILY_COUNTS" in workflow
    assert "PLOT_KAKS" in workflow
    assert "PLOT_EXPRESSION_HEATMAP" in workflow
    assert "BUILD_PLOT_MANIFEST" in workflow


def test_alignment_phylogeny_module_covers_alignment_tree_and_motif_steps():
    module = Path("workflows/modules/alignment_phylogeny.nf").read_text(encoding="utf-8")

    assert "process PREPARE_ALIGNMENT_INPUTS" in module
    assert "prepare_alignment_inputs.py" in module
    assert "--family-name ${family_name}" in module
    assert "--fasta ${family_members_faa}" in module
    assert "--aligner ${aligner}" in module
    assert "--out alignment_manifest.tsv" in module

    assert "process RUN_ALIGNMENT" in module
    assert "mafft --auto ${family_members_faa} > raw_alignment.faa" in module
    assert 'path "raw_alignment.faa"' in module

    assert "process PREPARE_PHYLOGENY_INPUTS" in module
    assert "prepare_phylogeny_inputs.py" in module
    assert "--tree-builder ${tree_builder}" in module
    assert "--out phylogeny_manifest.tsv" in module

    assert "process RUN_PHYLOGENY" in module
    assert "IQTREE_BIN=\\$(command -v iqtree2 || command -v iqtree)" in module
    assert '"\\${IQTREE_BIN}" -s ${alignment} -m MFP -bb 1000 -nt AUTO' in module
    assert 'path "treefile.nwk"' in module

    assert "process PARSE_MEME_MOTIFS" in module
    assert "parse_meme_motifs.py" in module
    assert "--meme-txt ${meme_txt}" in module
    assert "--out motif_summary.tsv" in module


def test_annotation_integration_module_covers_chromosome_and_expression_steps():
    module = Path("workflows/modules/annotation_integration.nf").read_text(encoding="utf-8")

    assert "process EXTRACT_CHROMOSOME_LOCATIONS" in module
    assert "extract_chromosome_locations.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--out chromosome_locations.tsv" in module

    assert "process SUBSET_EXPRESSION_MATRIX" in module
    assert "subset_expression_matrix.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--expression ${expression_matrix}" in module
    assert "--out family_expression.tsv" in module


def test_main_workflow_includes_remaining_standard_analysis_processes():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "PREPARE_ALIGNMENT_INPUTS" in workflow
    assert "RUN_ALIGNMENT" in workflow
    assert "PREPARE_PHYLOGENY_INPUTS" in workflow
    assert "RUN_PHYLOGENY" in workflow
    assert "PARSE_MEME_MOTIFS" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS" in workflow
    assert "SUBSET_EXPRESSION_MATRIX" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS(CONCAT_FAMILY_CANDIDATES.out, PREPARE_SPECIES.out)" in workflow
    assert "BUILD_STANDARD_REPORT_INDEX(" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS.out" in workflow
