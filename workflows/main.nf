nextflow.enable.dsl = 2

include { PREPARE_SPECIES } from './modules/prepare_species.nf'
include { BUILD_IDENTIFICATION_INPUTS } from './modules/identification_inputs.nf'
include { HMMER_SEARCH } from './modules/hmmer_search.nf'
include { DIAMOND_SEARCH } from './modules/diamond_search.nf'
include { DOMAIN_FILTER; CONCAT_FAMILY_CANDIDATES } from './modules/domain_filter.nf'
include { FAMILY_SUMMARY } from './modules/family_summary.nf'
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
    RETENTION_ENRICHMENT
} from './modules/duplication_retention.nf'

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

        NORMALIZE_DUPLICATE_TYPES(duplicates_ch)
        JOIN_FAMILY_DUPLICATES(family_members_ch, NORMALIZE_DUPLICATE_TYPES.out)
        CLASSIFY_WGD_LAYERS(kaks_pairs_ch, ks_bins_ch, event_args_ch)
        BUILD_WGD_EVENT_EVIDENCE(CLASSIFY_WGD_LAYERS.out, events_config_ch)
        ANNOTATE_FAMILY_WGD_EVENTS(JOIN_FAMILY_DUPLICATES.out, CLASSIFY_WGD_LAYERS.out)
        SUMMARIZE_FAMILY_EVENT_RETENTION(ANNOTATE_FAMILY_WGD_EVENTS.out)
        RETENTION_ENRICHMENT(JOIN_FAMILY_DUPLICATES.out, NORMALIZE_DUPLICATE_TYPES.out)

        BUILD_WGD_EVENT_EVIDENCE.out.view { evidence -> "WGD event evidence: ${evidence}" }
        SUMMARIZE_FAMILY_EVENT_RETENTION.out.view { summary -> "Family event retention summary: ${summary}" }
        RETENTION_ENRICHMENT.out.view { enrichment -> "Retention enrichment: ${enrichment}" }
    } else if (params.run_identification) {
        PREPARE_SPECIES(config_ch, groups_ch)
        BUILD_IDENTIFICATION_INPUTS(config_ch, PREPARE_SPECIES.out)

        hmmer_inputs_ch = BUILD_IDENTIFICATION_INPUTS.out[0]
            .splitCsv(header: true, sep: '\t')
            .map { row -> tuple(row.species_id, file(row.pep), row.hmm_id, file(row.hmm_profile)) }

        diamond_inputs_ch = BUILD_IDENTIFICATION_INPUTS.out[1]
            .splitCsv(header: true, sep: '\t')
            .map { row -> tuple(row.species_id, file(row.pep), file(row.reference_peptides)) }

        final_rule_ch = Channel.value(params.final_rule)

        HMMER_SEARCH(hmmer_inputs_ch)
        DIAMOND_SEARCH(diamond_inputs_ch)

        joined_evidence_ch = HMMER_SEARCH.out
            .join(DIAMOND_SEARCH.out, by: 0)
            .map { species_id, hmmer_tsv, diamond_tsv -> tuple(species_id, hmmer_tsv, diamond_tsv) }

        DOMAIN_FILTER(joined_evidence_ch, final_rule_ch)
        candidate_tables_ch = DOMAIN_FILTER.out.map { species_id, candidates -> candidates }
        CONCAT_FAMILY_CANDIDATES(candidate_tables_ch.collect())
        FAMILY_SUMMARY(CONCAT_FAMILY_CANDIDATES.out)
        PLOT_FAMILY_COUNTS(FAMILY_SUMMARY.out)

        PREPARE_SPECIES.out.view { manifest -> "Species manifest: ${manifest}" }
        CONCAT_FAMILY_CANDIDATES.out.view { candidates -> "Family candidates: ${candidates}" }
        FAMILY_SUMMARY.out.view { counts -> "Family counts: ${counts}" }
    } else {
        PREPARE_SPECIES(config_ch, groups_ch)

        PREPARE_SPECIES.out.view { manifest -> "Species manifest: ${manifest}" }
    }
}
