nextflow.enable.dsl = 2

include { PREPARE_SPECIES } from './modules/prepare_species.nf'

workflow {
    if (!params.config) {
        error "Missing required parameter: --config configs/example.config.yaml"
    }

    config_ch = Channel.value(file(params.config))
    groups_ch = Channel.value(file(params.groups))

    PREPARE_SPECIES(config_ch, groups_ch)

    PREPARE_SPECIES.out.view { manifest -> "Species manifest: ${manifest}" }
}
