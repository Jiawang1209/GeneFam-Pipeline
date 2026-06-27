nextflow.enable.dsl = 2

include { PREPARE_SPECIES } from './modules/prepare_species.nf'
include { VALIDATE_CONFIG } from './modules/config_validation.nf'
include { PREPROCESS_SPECIES; BUILD_REFERENCE_FROM_TAIR_DOMAINS } from './modules/preprocess.nf'
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
include {
    BUILD_RUN_CONFIG_SNAPSHOT;
    EXTRACT_FAMILY_SEQUENCES;
    BUILD_WGD_HANDOFF_MANIFEST;
    BUILD_STANDARD_REPORT_INDEX;
    COLLECT_SOFTWARE_VERSIONS;
    BUILD_FIGURE_INTERPRETATIONS;
    ASSEMBLE_STANDARD_REPORT;
    BUILD_REPRODUCIBILITY_CODE
} from './modules/standard_postprocess.nf'
include { MOCK_MVP } from './modules/mock_mvp.nf'
include { ASSEMBLE_REPORT } from './modules/report.nf'
include { PLOT_FAMILY_COUNTS; PLOT_KAKS; PLOT_EXPRESSION_HEATMAP; PLOT_FEATURE_SUMMARY; PLOT_GENE_FAMILY_INFO; PLOT_TREE_FEATURES; PLOT_PROMOTER_CIS_ELEMENTS; PLOT_MCSCANX_CIRCLIZE; PLOT_PPI_GGNETVIEW; BUILD_PLOT_MANIFEST } from './modules/plots.nf'
include {
    PREPARE_ALIGNMENT_INPUTS;
    RUN_ALIGNMENT;
    PREPARE_PHYLOGENY_INPUTS;
    RUN_PHYLOGENY;
    PARSE_MEME_MOTIFS
} from './modules/alignment_phylogeny.nf'
include {
    EXTRACT_CHROMOSOME_LOCATIONS;
    EXTRACT_GENE_STRUCTURE;
    EXTRACT_PROMOTERS;
    SUBSET_EXPRESSION_MATRIX
} from './modules/annotation_integration.nf'
include {
    PREPARE_MCSCANX_KAKS_HANDOFF;
    BUILD_WGD_RUN_CONFIG_SNAPSHOT;
    NORMALIZE_DUPLICATE_TYPES;
    JOIN_FAMILY_DUPLICATES;
    CLASSIFY_WGD_LAYERS;
    BUILD_KAKS_WGD_ANNOTATIONS;
    BUILD_WGD_EVENT_EVIDENCE;
    ANNOTATE_FAMILY_WGD_EVENTS;
    SUMMARIZE_FAMILY_EVENT_RETENTION;
    RETENTION_ENRICHMENT;
    PLOT_DUPLICATE_TYPE_KAKS;
    PLOT_PANGENOME_KAKS;
    EMPTY_PANGENOME_KAKS;
    BUILD_WGD_PLOT_MANIFEST;
    COLLECT_WGD_SOFTWARE_VERSIONS;
    BUILD_WGD_FIGURE_INTERPRETATIONS;
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
    VALIDATE_CONFIG(config_ch)
    validated_config_ch = VALIDATE_CONFIG.out
    groups_ch = Channel.value(file(params.groups))

    if (params.mock_mvp) {
        mock_evidence_ch = Channel.value(file(params.mock_evidence_dir))
        outdir_ch = Channel.value(params.outdir)
        MOCK_MVP(validated_config_ch, groups_ch, mock_evidence_ch, outdir_ch)

        MOCK_MVP.out.view { outputs -> "Mock MVP output index: ${outputs}" }
    } else if (params.run_duplication_retention) {
        family_members_ch = Channel.value(file(params.family_members))
        events_config_ch = Channel.value(file(params.events_config))
        ks_bins_ch = Channel.value(params.ks_bins)
        event_args_ch = Channel.value(params.wgd_event_args ?: "")
        pangenome_classes_ch = Channel.value(params.pangenome_classes ? file(params.pangenome_classes) : "")
        outdir_ch = Channel.value(params.outdir)
        project_name_ch = Channel.value(params.project_name)
        family_name_ch = Channel.value(params.gene_family)

        if (params.mcscanx_collinearity && params.kaks_results) {
            collinearity_ch = Channel.value(file(params.mcscanx_collinearity))
            kaks_results_ch = Channel.value(file(params.kaks_results))
            cds_a_ch = Channel.value(params.mcscanx_cds_a ?: "")
            cds_b_ch = Channel.value(params.mcscanx_cds_b ?: "")
            PREPARE_MCSCANX_KAKS_HANDOFF(
                collinearity_ch,
                kaks_results_ch,
                cds_a_ch,
                cds_b_ch
            )
            duplicates_ch = PREPARE_MCSCANX_KAKS_HANDOFF.out[1]
            kaks_pairs_ch = PREPARE_MCSCANX_KAKS_HANDOFF.out[3]
        } else if (params.duplicates && params.kaks_pairs) {
            duplicates_ch = Channel.value(file(params.duplicates))
            kaks_pairs_ch = Channel.value(file(params.kaks_pairs))
        } else {
            error "Missing WGD inputs: provide either --duplicates/--kaks_pairs or --mcscanx_collinearity/--kaks_results"
        }

        BUILD_WGD_RUN_CONFIG_SNAPSHOT(duplicates_ch, family_members_ch, kaks_pairs_ch, events_config_ch, ks_bins_ch, event_args_ch)
        NORMALIZE_DUPLICATE_TYPES(duplicates_ch)
        JOIN_FAMILY_DUPLICATES(family_members_ch, NORMALIZE_DUPLICATE_TYPES.out)
        CLASSIFY_WGD_LAYERS(kaks_pairs_ch, ks_bins_ch, event_args_ch)
        BUILD_KAKS_WGD_ANNOTATIONS(CLASSIFY_WGD_LAYERS.out)
        PLOT_KAKS(kaks_pairs_ch, BUILD_KAKS_WGD_ANNOTATIONS.out)
        BUILD_WGD_EVENT_EVIDENCE(CLASSIFY_WGD_LAYERS.out, events_config_ch)
        ANNOTATE_FAMILY_WGD_EVENTS(JOIN_FAMILY_DUPLICATES.out, CLASSIFY_WGD_LAYERS.out)
        SUMMARIZE_FAMILY_EVENT_RETENTION(ANNOTATE_FAMILY_WGD_EVENTS.out)
        RETENTION_ENRICHMENT(JOIN_FAMILY_DUPLICATES.out, NORMALIZE_DUPLICATE_TYPES.out)
        PLOT_DUPLICATE_TYPE_KAKS(NORMALIZE_DUPLICATE_TYPES.out, kaks_pairs_ch)
        if (params.pangenome_classes) {
            PLOT_PANGENOME_KAKS(pangenome_classes_ch, kaks_pairs_ch)
        } else {
            EMPTY_PANGENOME_KAKS()
        }
        BUILD_WGD_PLOT_MANIFEST()
        COLLECT_WGD_SOFTWARE_VERSIONS()
        BUILD_WGD_FIGURE_INTERPRETATIONS(BUILD_WGD_PLOT_MANIFEST.out)
        BUILD_WGD_REPORT_INDEX(outdir_ch)
        ASSEMBLE_WGD_REPORT(
            project_name_ch,
            family_name_ch,
            BUILD_WGD_REPORT_INDEX.out,
            BUILD_WGD_RUN_CONFIG_SNAPSHOT.out,
            BUILD_WGD_EVENT_EVIDENCE.out,
            SUMMARIZE_FAMILY_EVENT_RETENTION.out,
            RETENTION_ENRICHMENT.out,
            BUILD_WGD_PLOT_MANIFEST.out,
            COLLECT_WGD_SOFTWARE_VERSIONS.out,
            BUILD_WGD_FIGURE_INTERPRETATIONS.out[0]
        )

        BUILD_WGD_EVENT_EVIDENCE.out.view { evidence -> "WGD event evidence: ${evidence}" }
        SUMMARIZE_FAMILY_EVENT_RETENTION.out.view { summary -> "Family event retention summary: ${summary}" }
        RETENTION_ENRICHMENT.out.view { enrichment -> "Retention enrichment: ${enrichment}" }
        ASSEMBLE_WGD_REPORT.out.view { report -> "WGD final report: ${report}" }
    } else if (params.run_identification) {
        PREPARE_SPECIES(validated_config_ch, groups_ch)
        PREPROCESS_SPECIES(PREPARE_SPECIES.out)

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
            BUILD_REFERENCE_FROM_TAIR_DOMAINS(validated_config_ch, PREPROCESS_SPECIES.out[1])
            BUILD_IDENTIFICATION_INPUTS(validated_config_ch, PREPROCESS_SPECIES.out[1], BUILD_REFERENCE_FROM_TAIR_DOMAINS.out[0])
            BUILD_REFERENCE_FROM_TAIR_DOMAINS.out[1].view { manifest -> "Reference generation manifest: ${manifest}" }

            species_ids_ch = PREPROCESS_SPECIES.out[1]
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
        BUILD_REPRODUCIBILITY_CODE(
            validated_config_ch,
            PREPROCESS_SPECIES.out[1],
            BUILD_REFERENCE_FROM_TAIR_DOMAINS.out[1],
            CONCAT_FAMILY_CANDIDATES.out
        )

        PREPARE_SPECIES.out.view { manifest -> "Raw species manifest: ${manifest}" }
        PREPROCESS_SPECIES.out[1].view { manifest -> "Clean species manifest: ${manifest}" }
        CONCAT_FAMILY_CANDIDATES.out.view { candidates -> "Family candidates: ${candidates}" }

        if (!asBooleanParam(params.standard_stop_after_family_candidates)) {
            BUILD_RUN_CONFIG_SNAPSHOT(validated_config_ch, PREPROCESS_SPECIES.out[1])
            FAMILY_SUMMARY(CONCAT_FAMILY_CANDIDATES.out)
            EXTRACT_FAMILY_SEQUENCES(CONCAT_FAMILY_CANDIDATES.out, PREPROCESS_SPECIES.out[1])
            BUILD_WGD_HANDOFF_MANIFEST(CONCAT_FAMILY_CANDIDATES.out)
            PREPARE_ALIGNMENT_INPUTS(family_name_ch, EXTRACT_FAMILY_SEQUENCES.out, aligner_ch, alignment_outdir_ch)
            RUN_ALIGNMENT(family_name_ch, aligner_ch, EXTRACT_FAMILY_SEQUENCES.out)
            PREPARE_PHYLOGENY_INPUTS(PREPARE_ALIGNMENT_INPUTS.out, tree_builder_ch, phylogeny_outdir_ch)
            RUN_PHYLOGENY(family_name_ch, RUN_ALIGNMENT.out, tree_builder_ch)
            meme_txt_ch = Channel.value(file(params.meme_txt))
            PARSE_MEME_MOTIFS(meme_txt_ch, family_name_ch)
            EXTRACT_GENE_STRUCTURE(CONCAT_FAMILY_CANDIDATES.out, PREPROCESS_SPECIES.out[1])
            EXTRACT_CHROMOSOME_LOCATIONS(CONCAT_FAMILY_CANDIDATES.out, PREPROCESS_SPECIES.out[1])
            tree_domains_ch = Channel.value(params.filtered_domains ? file(params.filtered_domains) : "")
            PLOT_TREE_FEATURES(
                RUN_PHYLOGENY.out,
                CONCAT_FAMILY_CANDIDATES.out,
                PARSE_MEME_MOTIFS.out,
                EXTRACT_GENE_STRUCTURE.out,
                tree_domains_ch
            )
            promoters_bed_ch = Channel.value("")
            promoters_fasta_ch = Channel.value("")
            if (asBooleanParam(params.run_promoter)) {
                EXTRACT_PROMOTERS(
                    CONCAT_FAMILY_CANDIDATES.out,
                    PREPROCESS_SPECIES.out[1],
                    Channel.value(params.promoter_upstream_bp),
                    Channel.value(params.promoter_downstream_bp)
                )
                promoters_bed_ch = EXTRACT_PROMOTERS.out[0]
                promoters_fasta_ch = EXTRACT_PROMOTERS.out[1]
            }
            feature_summary_ch = Channel.value("")
            feature_summary_pdf_ch = Channel.value("")
            feature_summary_png_ch = Channel.value("")
            if (asBooleanParam(params.run_feature_summary)) {
                domains_ch = Channel.value(params.filtered_domains ? file(params.filtered_domains) : "")
                synteny_ch = Channel.value(params.syntenic_pairs ? file(params.syntenic_pairs) : "")
                PLOT_FEATURE_SUMMARY(
                    domains_ch,
                    PARSE_MEME_MOTIFS.out,
                    EXTRACT_GENE_STRUCTURE.out,
                    synteny_ch,
                    promoters_bed_ch
                )
                feature_summary_ch = PLOT_FEATURE_SUMMARY.out[0]
                feature_summary_pdf_ch = PLOT_FEATURE_SUMMARY.out[1]
                feature_summary_png_ch = PLOT_FEATURE_SUMMARY.out[2]
            }
            promoter_cis_elements_ch = Channel.value("")
            promoter_cis_gene_matrix_ch = Channel.value("")
            promoter_cis_gene_element_matrix_ch = Channel.value("")
            promoter_cis_category_summary_ch = Channel.value("")
            promoter_cis_element_annotations_ch = Channel.value("")
            promoter_cis_pdf_ch = Channel.value("")
            promoter_cis_png_ch = Channel.value("")
            if (asBooleanParam(params.run_promoter_cis)) {
                if (!params.promoter_cis_elements) {
                    error "Missing required parameter for --run_promoter_cis true: --promoter_cis_elements"
                }
                promoter_cis_input_ch = Channel.value(file(params.promoter_cis_elements))
                PLOT_PROMOTER_CIS_ELEMENTS(promoter_cis_input_ch)
                promoter_cis_elements_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[0]
                promoter_cis_gene_matrix_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[1]
                promoter_cis_gene_element_matrix_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[2]
                promoter_cis_category_summary_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[3]
                promoter_cis_element_annotations_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[4]
                promoter_cis_pdf_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[5]
                promoter_cis_png_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[6]
            }
            circlize_link_density_ch = Channel.value("")
            circlize_duplicate_type_tracks_ch = Channel.value("")
            mcscanx_circlize_pdf_ch = Channel.value("")
            mcscanx_circlize_png_ch = Channel.value("")
            if (asBooleanParam(params.run_mcscanx_circlize)) {
                if (!params.syntenic_pairs) {
                    error "Missing required parameter for --run_mcscanx_circlize true: --syntenic_pairs"
                }
                syntenic_pairs_ch = Channel.value(file(params.syntenic_pairs))
                PLOT_MCSCANX_CIRCLIZE(EXTRACT_CHROMOSOME_LOCATIONS.out, syntenic_pairs_ch)
                circlize_link_density_ch = PLOT_MCSCANX_CIRCLIZE.out[2]
                circlize_duplicate_type_tracks_ch = PLOT_MCSCANX_CIRCLIZE.out[3]
                mcscanx_circlize_pdf_ch = PLOT_MCSCANX_CIRCLIZE.out[5]
                mcscanx_circlize_png_ch = PLOT_MCSCANX_CIRCLIZE.out[6]
            }
            ppi_edges_ch = Channel.value("")
            ppi_nodes_ch = Channel.value("")
            ppi_hubs_ch = Channel.value("")
            ppi_input_evidence_ch = Channel.value("")
            ppi_network_qc_ch = Channel.value("")
            ppi_ggnetview_status_ch = Channel.value("")
            ppi_ggnetview_pdf_ch = Channel.value("")
            ppi_ggnetview_png_ch = Channel.value("")
            if (asBooleanParam(params.run_ppi)) {
                if (!params.ppi_edges) {
                    error "Missing required parameter for --run_ppi true: --ppi_edges"
                }
                ppi_edges_input_ch = Channel.value(file(params.ppi_edges))
                ppi_nodes_input_ch = Channel.value(params.ppi_nodes ? file(params.ppi_nodes) : "")
                PLOT_PPI_GGNETVIEW(ppi_edges_input_ch, ppi_nodes_input_ch)
                ppi_edges_ch = PLOT_PPI_GGNETVIEW.out[0]
                ppi_nodes_ch = PLOT_PPI_GGNETVIEW.out[1]
                ppi_hubs_ch = PLOT_PPI_GGNETVIEW.out[2]
                ppi_input_evidence_ch = PLOT_PPI_GGNETVIEW.out[3]
                ppi_network_qc_ch = PLOT_PPI_GGNETVIEW.out[4]
                ppi_ggnetview_status_ch = PLOT_PPI_GGNETVIEW.out[5]
                ppi_ggnetview_pdf_ch = PLOT_PPI_GGNETVIEW.out[6]
                ppi_ggnetview_png_ch = PLOT_PPI_GGNETVIEW.out[7]
            }
            family_expression_report_ch = Channel.value("")
            expression_sample_metadata_ch = Channel.value("")
            expression_group_matrix_ch = Channel.value("")
            expression_gene_summary_ch = Channel.value("")
            expression_heatmap_pdf_ch = Channel.value("")
            expression_heatmap_png_ch = Channel.value("")
            if (params.expression_matrix) {
                expression_matrix_ch = Channel.value(file(params.expression_matrix))
                expression_metadata_ch = Channel.value(params.expression_metadata ? file(params.expression_metadata) : "")
                SUBSET_EXPRESSION_MATRIX(CONCAT_FAMILY_CANDIDATES.out, expression_matrix_ch)
                family_expression_report_ch = SUBSET_EXPRESSION_MATRIX.out
                PLOT_EXPRESSION_HEATMAP(SUBSET_EXPRESSION_MATRIX.out, expression_metadata_ch)
                expression_sample_metadata_ch = PLOT_EXPRESSION_HEATMAP.out[0]
                expression_group_matrix_ch = PLOT_EXPRESSION_HEATMAP.out[1]
                expression_gene_summary_ch = PLOT_EXPRESSION_HEATMAP.out[2]
                expression_heatmap_pdf_ch = PLOT_EXPRESSION_HEATMAP.out[3]
                expression_heatmap_png_ch = PLOT_EXPRESSION_HEATMAP.out[4]
            }
            PLOT_FAMILY_COUNTS(FAMILY_SUMMARY.out)
            PLOT_GENE_FAMILY_INFO(FAMILY_SUMMARY.out, EXTRACT_FAMILY_SEQUENCES.out)
            BUILD_PLOT_MANIFEST()
            COLLECT_SOFTWARE_VERSIONS()
            BUILD_FIGURE_INTERPRETATIONS(BUILD_PLOT_MANIFEST.out)
            BUILD_STANDARD_REPORT_INDEX(
                PREPROCESS_SPECIES.out[1],
                BUILD_RUN_CONFIG_SNAPSHOT.out,
                CONCAT_FAMILY_CANDIDATES.out,
                FAMILY_SUMMARY.out,
                PLOT_FAMILY_COUNTS.out[0],
                PLOT_FAMILY_COUNTS.out[1],
                EXTRACT_FAMILY_SEQUENCES.out,
                PLOT_GENE_FAMILY_INFO.out[0],
                PLOT_GENE_FAMILY_INFO.out[1],
                PLOT_GENE_FAMILY_INFO.out[2],
                PLOT_GENE_FAMILY_INFO.out[3],
                PLOT_GENE_FAMILY_INFO.out[4],
                PLOT_GENE_FAMILY_INFO.out[5],
                PLOT_GENE_FAMILY_INFO.out[6],
                PLOT_GENE_FAMILY_INFO.out[7],
                PREPARE_ALIGNMENT_INPUTS.out,
                RUN_ALIGNMENT.out,
                PREPARE_PHYLOGENY_INPUTS.out,
                RUN_PHYLOGENY.out,
                PARSE_MEME_MOTIFS.out,
                EXTRACT_GENE_STRUCTURE.out,
                PLOT_TREE_FEATURES.out[0],
                PLOT_TREE_FEATURES.out[1],
                PLOT_TREE_FEATURES.out[2],
                EXTRACT_CHROMOSOME_LOCATIONS.out,
                promoters_bed_ch,
                promoters_fasta_ch,
                promoter_cis_elements_ch,
                promoter_cis_gene_matrix_ch,
                promoter_cis_gene_element_matrix_ch,
                promoter_cis_category_summary_ch,
                promoter_cis_element_annotations_ch,
                promoter_cis_pdf_ch,
                promoter_cis_png_ch,
                feature_summary_ch,
                feature_summary_pdf_ch,
                feature_summary_png_ch,
                circlize_link_density_ch,
                circlize_duplicate_type_tracks_ch,
                mcscanx_circlize_pdf_ch,
                mcscanx_circlize_png_ch,
                ppi_edges_ch,
                ppi_nodes_ch,
                ppi_hubs_ch,
                ppi_input_evidence_ch,
                ppi_network_qc_ch,
                ppi_ggnetview_status_ch,
                ppi_ggnetview_pdf_ch,
                ppi_ggnetview_png_ch,
                family_expression_report_ch,
                expression_sample_metadata_ch,
                expression_group_matrix_ch,
                expression_gene_summary_ch,
                expression_heatmap_pdf_ch,
                expression_heatmap_png_ch,
                BUILD_WGD_HANDOFF_MANIFEST.out,
                BUILD_PLOT_MANIFEST.out,
                COLLECT_SOFTWARE_VERSIONS.out,
                BUILD_FIGURE_INTERPRETATIONS.out[0]
            )
            ASSEMBLE_STANDARD_REPORT(project_name_ch, family_name_ch, BUILD_STANDARD_REPORT_INDEX.out, BUILD_RUN_CONFIG_SNAPSHOT.out, BUILD_PLOT_MANIFEST.out, COLLECT_SOFTWARE_VERSIONS.out, BUILD_FIGURE_INTERPRETATIONS.out[0])

            FAMILY_SUMMARY.out.view { counts -> "Family counts: ${counts}" }
            BUILD_STANDARD_REPORT_INDEX.out.view { report_index -> "Report index: ${report_index}" }
            ASSEMBLE_STANDARD_REPORT.out.view { report -> "Final report: ${report}" }
        }
    } else {
        PREPARE_SPECIES(validated_config_ch, groups_ch)

        PREPARE_SPECIES.out.view { manifest -> "Species manifest: ${manifest}" }
    }
}
