nextflow.enable.dsl = 2

include { PREPARE_SPECIES } from './modules/prepare_species.nf'
include { BUILD_IDENTIFICATION_INPUTS } from './modules/identification_inputs.nf'
include { HMMER_SEARCH } from './modules/hmmer_search.nf'
include { DIAMOND_SEARCH } from './modules/diamond_search.nf'
include {
    DOMAIN_FILTER;
    CONCAT_FAMILY_CANDIDATES;
    MOCK_IDENTIFICATION_EVIDENCE;
    EMPTY_HMMER_EVIDENCE;
    EMPTY_DIAMOND_EVIDENCE
} from './modules/domain_filter.nf'
include { FAMILY_SUMMARY } from './modules/family_summary.nf'
include { EXTRACT_FAMILY_SEQUENCES; BUILD_STANDARD_REPORT_INDEX; ASSEMBLE_STANDARD_REPORT } from './modules/standard_postprocess.nf'
include { MOCK_MVP } from './modules/mock_mvp.nf'
include { ASSEMBLE_REPORT } from './modules/report.nf'
include { PLOT_FAMILY_COUNTS; PLOT_KAKS; PLOT_EXPRESSION_HEATMAP; BUILD_PLOT_MANIFEST } from './modules/plots.nf'
include {
    PREPARE_ALIGNMENT_INPUTS;
    RUN_ALIGNMENT;
    PREPARE_PHYLOGENY_INPUTS;
    RUN_PHYLOGENY;
    PARSE_MEME_MOTIFS
} from './modules/alignment_phylogeny.nf'
include {
    EXTRACT_CHROMOSOME_LOCATIONS;
    SUBSET_EXPRESSION_MATRIX
} from './modules/annotation_integration.nf'
include {
    NORMALIZE_DUPLICATE_TYPES;
    JOIN_FAMILY_DUPLICATES;
    CLASSIFY_WGD_LAYERS;
    BUILD_WGD_EVENT_EVIDENCE;
    ANNOTATE_FAMILY_WGD_EVENTS;
    SUMMARIZE_FAMILY_EVENT_RETENTION;
    RETENTION_ENRICHMENT;
    BUILD_WGD_REPORT_INDEX;
    ASSEMBLE_WGD_REPORT
} from './modules/duplication_retention.nf'

def asBooleanParam(value) {
    if (value instanceof Boolean) {
        return value
    }
    return value?.toString()?.trim()?.toLowerCase() in ['true', '1', 'yes', 'on']
}

workflow {
    if (!params.config) {
        error "Missing required parameter: --config configs/example.config.yaml"
    }

    config_ch = Channel.value(file(params.config))
    groups_ch = Channel.value(file(params.groups))

    if (params.mock_mvp) {
        mock_evidence_ch = Channel.value(file(params.mock_evidence_dir))
        outdir_ch = Channel.value(params.outdir)
        MOCK_MVP(config_ch, groups_ch, mock_evidence_ch, outdir_ch)

        MOCK_MVP.out.view { outputs -> "Mock MVP output index: ${outputs}" }
    } else if (params.run_duplication_retention) {
        duplicates_ch = Channel.value(file(params.duplicates))
        family_members_ch = Channel.value(file(params.family_members))
        kaks_pairs_ch = Channel.value(file(params.kaks_pairs))
        events_config_ch = Channel.value(file(params.events_config))
        ks_bins_ch = Channel.value(params.ks_bins)
        event_args_ch = Channel.value(params.wgd_event_args ?: "")
        outdir_ch = Channel.value(params.outdir)
        project_name_ch = Channel.value(params.project_name)
        family_name_ch = Channel.value(params.gene_family)

        NORMALIZE_DUPLICATE_TYPES(duplicates_ch)
        JOIN_FAMILY_DUPLICATES(family_members_ch, NORMALIZE_DUPLICATE_TYPES.out)
        CLASSIFY_WGD_LAYERS(kaks_pairs_ch, ks_bins_ch, event_args_ch)
        BUILD_WGD_EVENT_EVIDENCE(CLASSIFY_WGD_LAYERS.out, events_config_ch)
        ANNOTATE_FAMILY_WGD_EVENTS(JOIN_FAMILY_DUPLICATES.out, CLASSIFY_WGD_LAYERS.out)
        SUMMARIZE_FAMILY_EVENT_RETENTION(ANNOTATE_FAMILY_WGD_EVENTS.out)
        RETENTION_ENRICHMENT(JOIN_FAMILY_DUPLICATES.out, NORMALIZE_DUPLICATE_TYPES.out)
        BUILD_WGD_REPORT_INDEX(outdir_ch)
        ASSEMBLE_WGD_REPORT(
            project_name_ch,
            family_name_ch,
            BUILD_WGD_REPORT_INDEX.out,
            BUILD_WGD_EVENT_EVIDENCE.out,
            SUMMARIZE_FAMILY_EVENT_RETENTION.out,
            RETENTION_ENRICHMENT.out
        )

        BUILD_WGD_EVENT_EVIDENCE.out.view { evidence -> "WGD event evidence: ${evidence}" }
        SUMMARIZE_FAMILY_EVENT_RETENTION.out.view { summary -> "Family event retention summary: ${summary}" }
        RETENTION_ENRICHMENT.out.view { enrichment -> "Retention enrichment: ${enrichment}" }
        ASSEMBLE_WGD_REPORT.out.view { report -> "WGD final report: ${report}" }
    } else if (params.run_identification) {
        PREPARE_SPECIES(config_ch, groups_ch)

        final_rule_ch = Channel.value(params.final_rule)
        family_name_ch = Channel.value(params.gene_family)
        project_name_ch = Channel.value(params.project_name)
        aligner_ch = Channel.value(params.aligner)
        tree_builder_ch = Channel.value(params.tree_builder)
        alignment_outdir_ch = Channel.value("${params.outdir}/alignment")
        phylogeny_outdir_ch = Channel.value("${params.outdir}/phylogeny")

        if (asBooleanParam(params.mock_external_tools)) {
            mock_evidence_ch = Channel.value(file(params.mock_evidence_dir))
            MOCK_IDENTIFICATION_EVIDENCE(mock_evidence_ch)
            joined_evidence_ch = MOCK_IDENTIFICATION_EVIDENCE.out
        } else {
            BUILD_IDENTIFICATION_INPUTS(config_ch, PREPARE_SPECIES.out)

            species_ids_ch = PREPARE_SPECIES.out
                .splitCsv(header: true, sep: '\t')
                .map { row -> row.species_id }

            hmmer_inputs_ch = BUILD_IDENTIFICATION_INPUTS.out[0]
                .splitCsv(header: true, sep: '\t')
                .map { row -> tuple(row.species_id, file(row.pep), row.hmm_id, file(row.hmm_profile)) }

            diamond_inputs_ch = BUILD_IDENTIFICATION_INPUTS.out[1]
                .splitCsv(header: true, sep: '\t')
                .map { row -> tuple(row.species_id, file(row.pep), file(row.reference_peptides)) }

            if (asBooleanParam(params.use_hmmer)) {
                HMMER_SEARCH(hmmer_inputs_ch)
                hmmer_evidence_ch = HMMER_SEARCH.out
            } else {
                EMPTY_HMMER_EVIDENCE(species_ids_ch)
                hmmer_evidence_ch = EMPTY_HMMER_EVIDENCE.out
            }

            if (asBooleanParam(params.use_diamond)) {
                DIAMOND_SEARCH(diamond_inputs_ch)
                diamond_evidence_ch = DIAMOND_SEARCH.out
            } else {
                EMPTY_DIAMOND_EVIDENCE(species_ids_ch)
                diamond_evidence_ch = EMPTY_DIAMOND_EVIDENCE.out
            }

            joined_evidence_ch = hmmer_evidence_ch
                .join(diamond_evidence_ch, by: 0)
                .map { species_id, hmmer_tsv, diamond_tsv -> tuple(species_id, hmmer_tsv, diamond_tsv) }
        }

        DOMAIN_FILTER(joined_evidence_ch, final_rule_ch)
        candidate_tables_ch = DOMAIN_FILTER.out.map { species_id, candidates -> candidates }
        CONCAT_FAMILY_CANDIDATES(candidate_tables_ch.collect())

        PREPARE_SPECIES.out.view { manifest -> "Species manifest: ${manifest}" }
        CONCAT_FAMILY_CANDIDATES.out.view { candidates -> "Family candidates: ${candidates}" }

        if (!asBooleanParam(params.standard_stop_after_family_candidates)) {
            FAMILY_SUMMARY(CONCAT_FAMILY_CANDIDATES.out)
            EXTRACT_FAMILY_SEQUENCES(CONCAT_FAMILY_CANDIDATES.out, PREPARE_SPECIES.out)
            PREPARE_ALIGNMENT_INPUTS(family_name_ch, EXTRACT_FAMILY_SEQUENCES.out, aligner_ch, alignment_outdir_ch)
            PREPARE_PHYLOGENY_INPUTS(PREPARE_ALIGNMENT_INPUTS.out, tree_builder_ch, phylogeny_outdir_ch)
            meme_txt_ch = Channel.value(file(params.meme_txt))
            PARSE_MEME_MOTIFS(meme_txt_ch, family_name_ch)
            EXTRACT_CHROMOSOME_LOCATIONS(CONCAT_FAMILY_CANDIDATES.out, PREPARE_SPECIES.out)
            family_expression_report_ch = Channel.value("")
            if (params.expression_matrix) {
                expression_matrix_ch = Channel.value(file(params.expression_matrix))
                SUBSET_EXPRESSION_MATRIX(CONCAT_FAMILY_CANDIDATES.out, expression_matrix_ch)
                family_expression_report_ch = SUBSET_EXPRESSION_MATRIX.out
            }
            PLOT_FAMILY_COUNTS(FAMILY_SUMMARY.out)
            BUILD_PLOT_MANIFEST()
            BUILD_STANDARD_REPORT_INDEX(
                PREPARE_SPECIES.out,
                CONCAT_FAMILY_CANDIDATES.out,
                FAMILY_SUMMARY.out,
                EXTRACT_FAMILY_SEQUENCES.out,
                PREPARE_ALIGNMENT_INPUTS.out,
                PREPARE_PHYLOGENY_INPUTS.out,
                PARSE_MEME_MOTIFS.out,
                EXTRACT_CHROMOSOME_LOCATIONS.out,
                family_expression_report_ch,
                BUILD_PLOT_MANIFEST.out
            )
            ASSEMBLE_STANDARD_REPORT(project_name_ch, family_name_ch, BUILD_STANDARD_REPORT_INDEX.out, BUILD_PLOT_MANIFEST.out)

            FAMILY_SUMMARY.out.view { counts -> "Family counts: ${counts}" }
            BUILD_STANDARD_REPORT_INDEX.out.view { report_index -> "Report index: ${report_index}" }
            ASSEMBLE_STANDARD_REPORT.out.view { report -> "Final report: ${report}" }
        }
    } else {
        PREPARE_SPECIES(config_ch, groups_ch)

        PREPARE_SPECIES.out.view { manifest -> "Species manifest: ${manifest}" }
    }
}
