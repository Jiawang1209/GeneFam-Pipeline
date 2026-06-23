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
        "python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv",
        "python bin/genefam/plan_runtime_bootstrap.py",
    ]
    for command in required_commands:
        assert command in text

    assert "Known Gap" in text
    assert "release_checks.tsv" in text
    assert "runtime_bootstrap_plan.md" in text
    assert "build_identification_inputs.py" in text
    assert "extract_family_sequences.py" in text
    assert "build_standard_report_index.py" in text
    assert "assemble_report.py" in text
    assert "run_standard_smoke.py" in text
    assert "run_wgd_smoke.py" in text
    assert "run_nextflow_smoke.py" in text
    assert "results/standard_smoke/report/final_report.md" in text
    assert "results/wgd_smoke/report/final_report.md" in text
    assert "results/nextflow_smoke/nextflow_smoke.md" in text
    assert "--run_identification true" in text
    assert "nextflow" in text
    assert "docker" in text
    assert "mafft" in text
