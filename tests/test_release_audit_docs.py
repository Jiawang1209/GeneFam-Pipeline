from pathlib import Path


def test_release_audit_maps_goal_requirements_to_evidence_and_commands():
    text = Path("docs/release_audit.md").read_text(encoding="utf-8")

    required_phrases = [
        "Nextflow DSL2",
        "YAML-driven parameters",
        "GeneFamilyFlow",
        "/usr/local/bin/R",
        "species bank",
        "HMMER",
        "DIAMOND",
        "standard identification branch",
        "domain filtering",
        "alignment",
        "phylogeny",
        "motif",
        "synteny",
        "duplication retention",
        "gamma",
        "beta",
        "alpha",
        "theta",
        "Ka/Ks",
        "chromosome location",
        "expression integration",
        "final report",
        "HISTORY.md",
        "Reference/",
    ]
    for phrase in required_phrases:
        assert phrase in text

    required_commands = [
        "python -m pytest tests -q",
        "python bin/genefam/run_release_checks.py --outdir results/release_checks",
        "python bin/genefam/validate_config.py configs/example.config.yaml",
        "python bin/genefam/validate_config.py configs/advanced_modules.example.yaml",
        "python bin/genefam/run_mock_mvp.py",
        "python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv",
        "python bin/genefam/plan_runtime_bootstrap.py",
        "python bin/genefam/audit_container_materials.py",
        "python bin/genefam/audit_objective_completion.py",
        "python bin/genefam/audit_reference_governance.py",
        "python bin/genefam/run_nextflow_single_tool_smoke.py",
        "python bin/genefam/run_container_profile_smoke.py --profile docker",
        "python bin/genefam/run_container_profile_smoke.py --profile apptainer",
    ]
    for command in required_commands:
        assert command in text

    assert "Known Gap" in text
    assert "release_checks.tsv" in text
    assert "runtime_bootstrap_plan.md" in text
    assert "objective_audit.md" in text
    assert "The release checks runner writes" in text
    assert "Required failed" in text
    assert "Optional failed" in text
    assert "results/objective_audit/objective_audit.tsv" in text
    assert "results/container_profile_smoke/docker/container_profile_smoke.md" in text
    assert "results/container_profile_smoke/apptainer/container_profile_smoke.md" in text
    assert "results/container_materials/container_materials.tsv" in text
    assert "results/container_materials/container_materials.md" in text
    assert "results/container_default_smoke" in text
    assert 'docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest' in text
    assert "run_standard_smoke.py" in text
    assert ".dockerignore" in text
    assert "results/handoff/handoff_report.md" in text
    assert "results/handoff/handoff_summary.tsv" in text
    assert "run_delivery_bundle.py" in text
    assert "audit_reference_governance.py" in text
    assert "results/reference_governance/reference_governance.tsv" in text
    assert "results/reference_governance/reference_governance.md" in text
    assert "results/delivery_bundle/delivery_manifest.tsv" in text
    assert "results/delivery_bundle/delivery_bundle.md" in text
    assert "docs/quickstart.md" in text
    assert "run_species_selection_smoke.py" in text
    assert "configs/manifest.example.yaml" in text
    assert "tests/fixtures/species_manifest.tsv" in text
    assert "build_identification_inputs.py" in text
    assert "extract_family_sequences.py" in text
    assert "extract_gene_structure.py" in text
    assert "build_run_config_snapshot.py" in text
    assert "extract_chromosome_locations.py" in text
    assert "run_chromosome_smoke.py" in text
    assert "run_gene_structure_smoke.py" in text
    assert "run_alignment_phylogeny_smoke.py" in text
    assert "FastTree" in text
    assert "--tree-builder fasttree" in text
    assert "subset_expression_matrix.py" in text
    assert "build_standard_report_index.py" in text
    assert "assemble_report.py" in text
    assert "run_standard_smoke.py" in text
    assert "run_domain_filter_smoke.py" in text
    assert "run_motif_smoke.py" in text
    assert "run_kaks_smoke.py" in text
    assert "run_retention_enrichment_smoke.py" in text
    assert "run_wgd_smoke.py" in text
    assert "run_synteny_smoke.py" in text
    assert "build_wgd_run_config_snapshot.py" in text
    assert "run_nextflow_smoke.py" in text
    assert "run_nextflow_single_tool_smoke.py" in text
    assert "results/nextflow_standard_manifest_smoke" in text
    assert "run_container_profile_smoke.py" in text
    assert "run_nextflow_wgd_smoke.py" in text
    assert "run_prepared_wgd_handoff_example.py" in text
    assert "run_quickstart.py" in text
    assert "examples/prepared_wgd_handoff" in text
    assert "test_prepared_wgd_handoff_example.py" in text
    assert "results/species_selection_smoke/tables/species_manifest.tsv" in text
    assert "results/species_selection_smoke/tables/run_plan.tsv" in text
    assert "results/species_manifest_selection_smoke/tables/species_manifest.tsv" in text
    assert "results/species_manifest_selection_smoke/species_selection_smoke.md" in text
    assert "results/standard_smoke/report/final_report.md" in text
    assert "results/standard_smoke/tables/wgd_handoff_manifest.tsv" in text
    assert "results/standard_smoke/tables/run_config_snapshot.tsv" in text
    assert "results/standard_smoke/tables/gene_structure_summary.tsv" in text
    assert "results/gene_structure_smoke/tables/gene_structure_summary.tsv" in text
    assert "results/chromosome_smoke/tables/chromosome_locations.tsv" in text
    assert "tests/fixtures/alignment/family_members.faa" in text
    assert "results/alignment_phylogeny_smoke/tables/alignment_manifest.tsv" in text
    assert "results/alignment_phylogeny_smoke/tables/phylogeny_manifest.tsv" in text
    assert "results/standard_smoke/tables/motif_summary.tsv" in text
    assert "tests/fixtures/mock_evidence/meme.txt" in text
    assert "results/motif_smoke/tables/motif_summary.tsv" in text
    assert "tests/fixtures/hmmer_domains/domains.tsv" in text
    assert "results/domain_filter_smoke/tables/filtered_domains.tsv" in text
    assert "tests/fixtures/kaks/kaks_calculator.tsv" in text
    assert "results/kaks_smoke/tables/normalized_kaks.tsv" in text
    assert "results/retention_enrichment_smoke/tables/retention_enrichment.tsv" in text
    assert "results/standard_expression_smoke/tables/family_expression.tsv" in text
    assert "results/standard_expression_smoke/plots/expression_heatmap.pdf" in text
    assert "tests/fixtures/expression/family_expression.tsv" in text
    assert "tests/fixtures/mcscanx/sample.collinearity" in text
    assert "results/synteny_smoke/tables/syntenic_pairs.tsv" in text
    assert "results/wgd_smoke/report/final_report.md" in text
    assert "results/wgd_smoke/tables/wgd_run_config_snapshot.tsv" in text
    assert "WGD event names must be unique" in text
    assert "WGD event metadata requires name, scope, evidence, and expected_relative_age" in text
    assert "Configured WGD event labels must have matching event metadata" in text
    assert "results/nextflow_smoke/nextflow_smoke.md" in text
    assert "results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv" in text
    assert "results/example_prepared_wgd/report/final_report.md" in text
    assert "--run_identification true" in text
    assert "--run_duplication_retention true" in text
    assert "tests/test_parse_meme_motifs.py" in text
    assert "nextflow" in text
    assert "docker" in text
    assert "mafft" in text
