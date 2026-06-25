process VALIDATE_CONFIG {
    tag "config preflight"

    input:
    path config_file

    output:
    path "validated_config.yaml"

    script:
    """
    python ${projectDir}/../bin/genefam/validate_config.py \\
      ${config_file} \\
      --check-paths \\
      --base-dir ${projectDir}/..
    cp ${config_file} validated_config.yaml
    """
}
