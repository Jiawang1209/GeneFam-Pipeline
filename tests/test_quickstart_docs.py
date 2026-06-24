from pathlib import Path


def test_readme_links_final_quickstart():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "docs/quickstart.md" in readme


def test_quickstart_documents_minimum_verified_run_path():
    text = Path("docs/quickstart.md").read_text(encoding="utf-8")

    required_snippets = [
        "GeneFamilyFlow",
        "/usr/local/bin/R",
        "species bank",
        "python bin/genefam/run_release_checks.py --outdir results/release_checks",
        "Required failed",
        "Optional failed",
        "python bin/genefam/run_quickstart.py",
        "--outdir results/quickstart",
        "results/quickstart/quickstart_summary.md",
        "python bin/genefam/audit_objective_completion.py",
        "results/objective_audit/objective_audit.md",
        "results/handoff/handoff_report.md",
        "python bin/genefam/run_standard_smoke.py",
        "python bin/genefam/run_nextflow_single_tool_smoke.py",
        "--config configs/example.config.yaml",
        "--groups configs/species_groups.yaml",
        "--mock-evidence-dir tests/fixtures/mock_evidence",
        "--outdir results/standard_smoke",
        "--outdir results/nextflow_single_tool_smoke",
        "nextflow_standard_hmmer_only",
        "nextflow_standard_diamond_only",
        "python bin/genefam/run_prepared_wgd_handoff_example.py",
        "--example-dir examples/prepared_wgd_handoff",
        "--outdir results/example_prepared_wgd",
        "results/standard_smoke/report/final_report.md",
        "results/example_prepared_wgd/report/final_report.md",
        "results/example_prepared_wgd/tables/wgd_event_evidence.tsv",
        "alpha",
        "beta",
        "gamma",
        "theta",
        "docker",
        "apptainer",
        "bash results/readiness/runtime_bootstrap.sh",
        "genefam-pipeline_latest.sif",
        "HISTORY.md",
        "Reference/",
    ]
    for snippet in required_snippets:
        assert snippet in text
