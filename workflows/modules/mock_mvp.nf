process MOCK_MVP {
    tag "mock mvp"

    input:
    path config_file
    path groups_file
    path mock_evidence_dir
    val outdir

    output:
    path "mock_mvp_outputs.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/run_mock_mvp.py \\
      --config ${config_file} \\
      --groups ${groups_file} \\
      --mock-evidence-dir ${mock_evidence_dir} \\
      --outdir ${outdir} \\
      > mock_mvp_outputs.tsv
    """
}
