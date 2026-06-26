import subprocess
import sys

from bin.genefam.audit_objective_completion import (
    build_objective_audit,
    summarize_objective_audit,
    write_markdown,
    write_tsv,
)


def _release_row(check, status="passed"):
    return {
        "check": check,
        "required": "true",
        "status": status,
        "exit_code": "0" if status == "passed" else "1",
        "command": check,
        "note": "",
    }


def _readiness_row(command, status="available_in_conda", path=None):
    return {
        "command": command,
        "status": status,
        "path": path or ("GeneFamilyFlow:/bin/" + command if status.startswith("available") else ""),
    }


def test_build_objective_audit_marks_goal_items_and_runtime_blockers():
    release_rows = [
        _release_row("pytest"),
        _release_row("validate example config"),
        _release_row("validate advanced config"),
        _release_row("validate manifest config"),
        _release_row("species selection smoke"),
        _release_row("species manifest selection smoke"),
        _release_row("mock MVP"),
        _release_row("domain filter smoke"),
        _release_row("motif parser smoke"),
        _release_row("standard branch smoke"),
        _release_row("gene structure smoke"),
        _release_row("chromosome location smoke"),
        _release_row("feature summary visualization smoke"),
        _release_row("promoter cis-element visualization smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("PPI ggNetView plot smoke"),
        _release_row("standard branch expression smoke"),
        _release_row("alignment phylogeny smoke"),
        _release_row("synteny parser smoke"),
        _release_row("Ka/Ks parser smoke"),
        _release_row("retention enrichment smoke"),
        _release_row("WGD event smoke"),
        _release_row("Nextflow mock MVP smoke"),
        _release_row("Nextflow standard branch smoke"),
        _release_row("Nextflow standard manifest smoke"),
        _release_row("Nextflow standard single-tool smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("Reference governance audit"),
        _release_row("readiness audit", status="failed"),
        _release_row("runtime bootstrap plan"),
        _release_row("container materials audit"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Nextflow DSL2 workflow"]["status"] == "achieved"
    assert by_requirement["YAML-driven species selection"]["status"] == "achieved"
    assert by_requirement["GeneFamilyFlow runtime"]["status"] == "achieved"
    assert by_requirement["Docker/Apptainer reproducibility"]["status"] == "blocked"
    assert "container materials audit" in by_requirement["Docker/Apptainer reproducibility"]["evidence"]
    assert "Dockerfile default standard smoke" in by_requirement["Docker/Apptainer reproducibility"]["evidence"]
    assert "results/container_default_smoke" in by_requirement["Docker/Apptainer reproducibility"]["note"]
    assert "docker, apptainer" in by_requirement["Docker/Apptainer reproducibility"]["note"]
    assert by_requirement["WGD gamma beta alpha theta evidence"]["status"] == "achieved"
    assert by_requirement["paper-level visualization modules"]["status"] == "achieved"
    assert "promoter cis-element visualization smoke" in by_requirement["paper-level visualization modules"]["evidence"]
    assert by_requirement["quickstart handoff"]["status"] == "achieved"


def test_paper_level_visualization_modules_require_promoter_cis_smoke():
    release_rows = [
        _release_row("feature summary visualization smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("PPI ggNetView plot smoke"),
        _release_row("standard branch expression smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["paper-level visualization modules"]["status"] == "missing"
    assert "promoter cis-element visualization smoke" in by_requirement["paper-level visualization modules"]["evidence"]


def test_yaml_driven_species_selection_requires_species_selection_smokes():
    release_rows = [
        _release_row("validate example config"),
        _release_row("validate advanced config"),
        _release_row("species selection smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["YAML-driven species selection"]["status"] == "missing"
    assert "species manifest selection smoke" in by_requirement["YAML-driven species selection"]["evidence"]


def test_history_and_reference_governance_requires_reference_audit():
    release_rows = [
        _release_row("pytest"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["history and Reference governance"]["status"] == "missing"
    assert "Reference governance audit" in by_requirement["history and Reference governance"]["evidence"]


def test_standard_identification_branch_requires_domain_filter_smoke():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard branch smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["standard identification branch"]["status"] == "missing"
    assert "domain filter smoke" in by_requirement["standard identification branch"]["evidence"]


def test_standard_identification_branch_requires_motif_parser_smoke():
    release_rows = [
        _release_row("domain filter smoke"),
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard branch smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["standard identification branch"]["status"] == "missing"
    assert "motif parser smoke" in by_requirement["standard identification branch"]["evidence"]


def test_standard_identification_branch_requires_gene_structure_smoke():
    release_rows = [
        _release_row("domain filter smoke"),
        _release_row("motif parser smoke"),
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard branch smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["standard identification branch"]["status"] == "missing"
    assert "gene structure smoke" in by_requirement["standard identification branch"]["evidence"]


def test_wgd_event_evidence_requires_synteny_parser_smoke():
    release_rows = [
        _release_row("WGD event smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["WGD gamma beta alpha theta evidence"]["status"] == "missing"
    assert "synteny parser smoke" in by_requirement["WGD gamma beta alpha theta evidence"]["evidence"]


def test_kaks_and_retention_analysis_requires_kaks_parser_smoke():
    release_rows = [
        _release_row("WGD event smoke"),
        _release_row("prepared WGD handoff example"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Ka/Ks and retention analysis"]["status"] == "missing"
    assert "Ka/Ks parser smoke" in by_requirement["Ka/Ks and retention analysis"]["evidence"]


def test_kaks_and_retention_analysis_requires_retention_enrichment_smoke():
    release_rows = [
        _release_row("Ka/Ks parser smoke"),
        _release_row("WGD event smoke"),
        _release_row("prepared WGD handoff example"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Ka/Ks and retention analysis"]["status"] == "missing"
    assert "retention enrichment smoke" in by_requirement["Ka/Ks and retention analysis"]["evidence"]


def test_chromosome_and_expression_integration_requires_chromosome_smoke():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("standard branch expression smoke"),
        _release_row("quickstart handoff"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["chromosome and expression integration"]["status"] == "missing"
    assert "chromosome location smoke" in by_requirement["chromosome and expression integration"]["evidence"]


def test_nextflow_dsl2_requires_alignment_phylogeny_smoke_evidence():
    release_rows = [
        _release_row("Nextflow mock MVP smoke"),
        _release_row("Nextflow standard branch smoke"),
        _release_row("Nextflow standard single-tool smoke"),
        _release_row("Nextflow WGD event smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Nextflow DSL2 workflow"]["status"] == "missing"
    assert "alignment phylogeny smoke" in by_requirement["Nextflow DSL2 workflow"]["evidence"]


def test_nextflow_dsl2_requires_single_tool_smoke_evidence():
    release_rows = [
        _release_row("Nextflow mock MVP smoke"),
        _release_row("Nextflow standard branch smoke"),
        _release_row("Nextflow WGD event smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Nextflow DSL2 workflow"]["status"] == "missing"
    assert "single-tool" in by_requirement["Nextflow DSL2 workflow"]["note"]


def test_nextflow_dsl2_requires_manifest_standard_smoke_evidence():
    release_rows = [
        _release_row("Nextflow mock MVP smoke"),
        _release_row("Nextflow standard branch smoke"),
        _release_row("Nextflow standard single-tool smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("alignment phylogeny smoke"),
    ]
    readiness_rows = [
        _readiness_row("nextflow"),
        _readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R"),
        _readiness_row("hmmsearch"),
        _readiness_row("diamond"),
        _readiness_row("mafft"),
        _readiness_row("iqtree2", "available_in_conda", "GeneFamilyFlow:/bin/iqtree"),
        _readiness_row("meme"),
        _readiness_row("docker", "missing", ""),
        _readiness_row("apptainer", "missing", ""),
    ]

    rows = build_objective_audit(release_rows, readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Nextflow DSL2 workflow"]["status"] == "missing"
    assert "manifest" in by_requirement["Nextflow DSL2 workflow"]["evidence"]


def test_summarize_objective_audit_counts_statuses():
    rows = [
        {"requirement": "A", "status": "achieved", "evidence": "", "note": ""},
        {"requirement": "B", "status": "blocked", "evidence": "", "note": ""},
        {"requirement": "C", "status": "missing", "evidence": "", "note": ""},
    ]

    assert summarize_objective_audit(rows) == {
        "achieved": 1,
        "blocked": 1,
        "missing": 1,
        "complete": False,
    }


def test_write_objective_audit_outputs(tmp_path):
    rows = [
        {
            "requirement": "Docker/Apptainer reproducibility",
            "status": "blocked",
            "evidence": "readiness audit",
            "note": "missing docker, apptainer",
        }
    ]

    write_tsv(rows, tmp_path / "objective_audit.tsv")
    write_markdown(rows, tmp_path / "objective_audit.md")

    assert (tmp_path / "objective_audit.tsv").read_text(encoding="utf-8").startswith(
        "requirement\tstatus\tevidence\tnote\n"
    )
    markdown = (tmp_path / "objective_audit.md").read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Objective Audit" in markdown
    assert "Docker/Apptainer reproducibility" in markdown
    assert "Complete: false" in markdown


def test_audit_objective_completion_cli_writes_outputs(tmp_path):
    release = tmp_path / "release_checks.tsv"
    release.write_text(
        "check\trequired\tstatus\texit_code\tcommand\tnote\n"
        "pytest\ttrue\tpassed\t0\tpytest\t\n"
        "validate example config\ttrue\tpassed\t0\tvalidate\t\n"
        "validate advanced config\ttrue\tpassed\t0\tvalidate\t\n"
        "species selection smoke\ttrue\tpassed\t0\tspecies\t\n"
        "domain filter smoke\ttrue\tpassed\t0\tdomain\t\n"
        "motif parser smoke\ttrue\tpassed\t0\tmotif\t\n"
        "standard branch smoke\ttrue\tpassed\t0\tstandard\t\n"
        "gene structure smoke\ttrue\tpassed\t0\tgene_structure\t\n"
        "chromosome location smoke\ttrue\tpassed\t0\tchromosome\t\n"
        "alignment phylogeny smoke\ttrue\tpassed\t0\talignment\t\n"
        "synteny parser smoke\ttrue\tpassed\t0\tsynteny\t\n"
        "Ka/Ks parser smoke\ttrue\tpassed\t0\tkaks\t\n"
        "retention enrichment smoke\ttrue\tpassed\t0\tretention\t\n"
        "WGD event smoke\ttrue\tpassed\t0\twgd\t\n"
        "Nextflow mock MVP smoke\ttrue\tpassed\t0\tnextflow\t\n"
        "Nextflow standard branch smoke\ttrue\tpassed\t0\tnextflow\t\n"
        "Nextflow standard single-tool smoke\ttrue\tpassed\t0\tnextflow\t\n"
        "Nextflow WGD event smoke\ttrue\tpassed\t0\tnextflow\t\n"
        "prepared WGD handoff example\ttrue\tpassed\t0\tprepared\t\n"
        "quickstart handoff\ttrue\tpassed\t0\tquickstart\t\n"
        "Reference governance audit\ttrue\tpassed\t0\treference\t\n"
        "readiness audit\ttrue\tfailed\t1\treadiness\t\n",
        encoding="utf-8",
    )
    readiness = tmp_path / "command_readiness.tsv"
    readiness.write_text(
        "command\tstatus\tpath\n"
        "nextflow\tavailable_in_conda\tGeneFamilyFlow:/bin/nextflow\n"
        "/usr/local/bin/R\tavailable\t/usr/local/bin/R\n"
        "hmmsearch\tavailable_in_conda\tGeneFamilyFlow:/bin/hmmsearch\n"
        "diamond\tavailable_in_conda\tGeneFamilyFlow:/bin/diamond\n"
        "mafft\tavailable_in_conda\tGeneFamilyFlow:/bin/mafft\n"
        "iqtree2\tavailable_in_conda\tGeneFamilyFlow:/bin/iqtree\n"
        "meme\tavailable_in_conda\tGeneFamilyFlow:/bin/meme\n"
        "docker\tmissing\t\n"
        "apptainer\tmissing\t\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "objective"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_objective_completion.py",
            "--release-checks",
            str(release),
            "--readiness",
            str(readiness),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Docker/Apptainer reproducibility\tblocked" in (
        outdir / "objective_audit.tsv"
    ).read_text(encoding="utf-8")
    assert "Complete: false" in (outdir / "objective_audit.md").read_text(encoding="utf-8")
