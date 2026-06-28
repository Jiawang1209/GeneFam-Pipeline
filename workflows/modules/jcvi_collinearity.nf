process PREPARE_JCVI_COLLINEARITY {
    tag "prepare JCVI collinearity"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path family_candidates
    path species_manifest

    output:
    path "jcvi_collinearity"

    script:
    """
    mkdir -p jcvi_collinearity
    python ${projectDir}/../bin/genefam/prepare_jcvi_collinearity.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --outdir jcvi_collinearity

    if python - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("jcvi") else 1)
PY
    then
      printf 'check\tstatus\tdetail\\n' > jcvi_collinearity/jcvi_dependency_status.tsv
      printf 'jcvi_python_module\tavailable\tjcvi Python package is importable; run commands/jcvi_commands.sh to execute Reference Step8\\n' >> jcvi_collinearity/jcvi_dependency_status.tsv
    else
      printf 'check\tstatus\tdetail\\n' > jcvi_collinearity/jcvi_dependency_status.tsv
      printf 'jcvi_python_module\tmissing_dependency\tInstall jcvi in GeneFamilyFlow or use the container route before running Reference Step8 ortholog/screen/karyotype\\n' >> jcvi_collinearity/jcvi_dependency_status.tsv
    fi
    """
}

process RUN_JCVI_COLLINEARITY {
    tag "run JCVI collinearity"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path prepared_jcvi_collinearity, stageAs: "prepared_jcvi_collinearity"

    output:
    path "jcvi_collinearity"

    script:
    """
    cp -R prepared_jcvi_collinearity jcvi_collinearity
    python ${projectDir}/../bin/genefam/run_jcvi_collinearity.py \\
      --jcvi-dir jcvi_collinearity \\
      --python-bin ${params.python_bin}
    test -s jcvi_collinearity/jcvi_run_status.tsv
    """
}
