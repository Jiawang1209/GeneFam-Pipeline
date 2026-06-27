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


def _publication_audit_rows(omit=None):
    omit = set(omit or [])
    checks = [
        "plot_files_exist",
        "plot_file_format_valid",
        "figure_interpretation_coverage",
        "figure_interpretation_scope",
        "figure_interpretation_detail",
        "figure_interpretation_close_reading_voice",
        "figure_interpretation_qc_specificity",
        "figure_output_paths_match_manifest",
        "software_versions_present",
        "software_detected_versions_parseable",
        "figure_method_software_versions",
        "final_report_embeds_publication_sections",
        "final_report_figure_traceability",
        "final_report_plot_previews",
        "final_report_placeholder_text",
    ]
    return [
        {"check": check, "status": "passed", "evidence": check, "note": ""}
        for check in checks
        if check not in omit
    ]


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
        _release_row("validate publication modules config"),
        _release_row("gene family information visualization smoke"),
        _release_row("feature summary visualization smoke"),
        _release_row("promoter smoke"),
        _release_row("promoter cis-element visualization smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("PPI ggNetView smoke"),
        _release_row("PPI ggNetView plot smoke"),
        _release_row("standard branch expression smoke"),
        _release_row("expression heatmap visualization smoke"),
        _release_row("alignment phylogeny smoke"),
        _release_row("synteny parser smoke"),
        _release_row("Ka/Ks parser smoke"),
        _release_row("Ka/Ks WGD annotation plot smoke"),
        _release_row("duplicate-type Ka/Ks visualization smoke"),
        _release_row("pangenome-class Ka/Ks visualization smoke"),
        _release_row("retention enrichment smoke"),
        _release_row("WGD event smoke"),
        _release_row("Nextflow mock MVP smoke"),
        _release_row("Nextflow standard branch smoke"),
        _release_row("Nextflow standard manifest smoke"),
        _release_row("Nextflow standard single-tool smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("Nextflow raw MCScanX/KaKs WGD smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("WGD publication report audit"),
        _release_row("Reference visual alignment audit"),
        _release_row("delivery bundle figure gallery audit"),
        _release_row("delivery bundle manifest audit"),
        _release_row("quickstart handoff"),
        _release_row("Reference governance audit"),
        _release_row("readiness audit", status="failed"),
        _release_row("runtime bootstrap plan"),
        _release_row("runtime bootstrap shell syntax"),
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

    rows = build_objective_audit(
        release_rows,
        readiness_rows,
        publication_audit_rows=_publication_audit_rows(),
        wgd_publication_audit_rows=_publication_audit_rows(),
    )
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["Nextflow DSL2 workflow"]["status"] == "achieved"
    assert by_requirement["YAML-driven species selection"]["status"] == "achieved"
    assert by_requirement["GeneFamilyFlow runtime"]["status"] == "achieved"
    assert by_requirement["Docker/Apptainer reproducibility"]["status"] == "blocked"
    assert "container materials audit" in by_requirement["Docker/Apptainer reproducibility"]["evidence"]
    assert "Dockerfile default standard smoke" in by_requirement["Docker/Apptainer reproducibility"]["evidence"]
    assert "Apptainer.def" in by_requirement["Docker/Apptainer reproducibility"]["evidence"]
    assert "runtime bootstrap shell syntax" in by_requirement["Docker/Apptainer reproducibility"]["evidence"]
    assert "results/container_default_smoke" in by_requirement["Docker/Apptainer reproducibility"]["note"]
    assert "Reference-safe Apptainer definition" in by_requirement["Docker/Apptainer reproducibility"]["note"]
    assert "runtime_bootstrap.sh passed bash -n" in by_requirement["Docker/Apptainer reproducibility"]["note"]
    assert "docker, apptainer" in by_requirement["Docker/Apptainer reproducibility"]["note"]
    assert by_requirement["WGD gamma beta alpha theta evidence"]["status"] == "achieved"
    assert by_requirement["paper-level visualization modules"]["status"] == "achieved"
    assert "Reference visual alignment audit" in by_requirement["paper-level visualization modules"]["evidence"]
    assert "validate publication modules config" in by_requirement["paper-level visualization modules"]["evidence"]
    assert "configs/publication_modules.example.yaml" in by_requirement["paper-level visualization modules"]["note"]
    assert "gene family information visualization smoke" in by_requirement["paper-level visualization modules"]["evidence"]
    assert "promoter smoke" in by_requirement["paper-level visualization modules"]["evidence"]
    assert "promoter cis-element visualization smoke" in by_requirement["paper-level visualization modules"]["evidence"]
    assert "PPI ggNetView smoke" in by_requirement["paper-level visualization modules"]["evidence"]
    assert by_requirement["quickstart handoff"]["status"] == "achieved"


def test_r_plotting_objective_requires_runtime_health_release_evidence():
    readiness_rows = [_readiness_row("/usr/local/bin/R", "available", "/usr/local/bin/R")]

    rows = build_objective_audit([], readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["/usr/local/bin/R plotting"]["status"] == "blocked"
    assert "R runtime health" in by_requirement["/usr/local/bin/R plotting"]["evidence"]
    assert "R runtime health" in by_requirement["/usr/local/bin/R plotting"]["note"]

    rows = build_objective_audit([_release_row("R runtime health")], readiness_rows)
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["/usr/local/bin/R plotting"]["status"] == "achieved"
    assert "command readiness audit" in by_requirement["/usr/local/bin/R plotting"]["evidence"]
    assert "R runtime health" in by_requirement["/usr/local/bin/R plotting"]["evidence"]


def test_paper_level_visualization_modules_require_promoter_cis_smoke():
    release_rows = [
        _release_row("gene family information visualization smoke"),
        _release_row("feature summary visualization smoke"),
        _release_row("promoter smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("PPI ggNetView smoke"),
        _release_row("PPI ggNetView plot smoke"),
        _release_row("standard branch expression smoke"),
        _release_row("expression heatmap visualization smoke"),
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


def test_paper_level_visualization_modules_require_promoter_extraction_smoke():
    release_rows = [
        _release_row("gene family information visualization smoke"),
        _release_row("feature summary visualization smoke"),
        _release_row("promoter cis-element visualization smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("PPI ggNetView smoke"),
        _release_row("PPI ggNetView plot smoke"),
        _release_row("standard branch expression smoke"),
        _release_row("expression heatmap visualization smoke"),
        _release_row("Ka/Ks WGD annotation plot smoke"),
        _release_row("duplicate-type Ka/Ks visualization smoke"),
        _release_row("pangenome-class Ka/Ks visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("WGD publication report audit"),
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
    assert "promoter smoke" in by_requirement["paper-level visualization modules"]["evidence"]


def test_paper_level_visualization_modules_require_publication_yaml_validation():
    release_rows = [
        _release_row("gene family information visualization smoke"),
        _release_row("feature summary visualization smoke"),
        _release_row("promoter smoke"),
        _release_row("promoter cis-element visualization smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("PPI ggNetView smoke"),
        _release_row("PPI ggNetView plot smoke"),
        _release_row("standard branch expression smoke"),
        _release_row("expression heatmap visualization smoke"),
        _release_row("Ka/Ks WGD annotation plot smoke"),
        _release_row("duplicate-type Ka/Ks visualization smoke"),
        _release_row("pangenome-class Ka/Ks visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("WGD publication report audit"),
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
    assert "validate publication modules config" in by_requirement["paper-level visualization modules"]["evidence"]


def test_paper_level_visualization_modules_require_expression_heatmap_smoke():
    release_rows = [
        _release_row("gene family information visualization smoke"),
        _release_row("feature summary visualization smoke"),
        _release_row("promoter smoke"),
        _release_row("promoter cis-element visualization smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("PPI ggNetView smoke"),
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
    assert "expression heatmap visualization smoke" in by_requirement["paper-level visualization modules"]["evidence"]


def test_objective_audit_lists_named_paper_level_visualization_requirements():
    release_rows = [
        _release_row("gene family information visualization smoke"),
        _release_row("feature summary visualization smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("synteny parser smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("promoter smoke"),
        _release_row("promoter cis-element visualization smoke"),
        _release_row("standard branch expression smoke"),
        _release_row("expression heatmap visualization smoke"),
        _release_row("PPI ggNetView smoke"),
        _release_row("PPI ggNetView plot smoke"),
        _release_row("Ka/Ks WGD annotation plot smoke"),
        _release_row("duplicate-type Ka/Ks visualization smoke"),
        _release_row("pangenome-class Ka/Ks visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("WGD publication report audit"),
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

    expected_requirements = [
        "gene family information and copy-number visualization",
        "tree motif gene-structure domain visualization",
        "MCScanX synteny circlize visualization",
        "promoter cis-element visualization",
        "expression heatmap visualization",
        "PPI ggNetView visualization",
        "Ka/Ks WGD visualization",
    ]
    for requirement in expected_requirements:
        assert by_requirement[requirement]["status"] == "achieved"

    assert "copy-number" in by_requirement["gene family information and copy-number visualization"]["note"]
    assert "Nextflow standard visualization smoke" in by_requirement[
        "gene family information and copy-number visualization"
    ]["evidence"]
    assert "Nextflow report evidence" in by_requirement[
        "gene family information and copy-number visualization"
    ]["note"]
    assert "Nextflow standard visualization smoke" in by_requirement[
        "tree motif gene-structure domain visualization"
    ]["evidence"]
    assert "tree/motif/gene-structure/domain" in by_requirement["tree motif gene-structure domain visualization"]["note"]
    assert "Nextflow report evidence" in by_requirement["tree motif gene-structure domain visualization"]["note"]
    assert "MCScanX" in by_requirement["MCScanX synteny circlize visualization"]["note"]
    assert "Nextflow standard visualization smoke" in by_requirement["promoter cis-element visualization"]["evidence"]
    assert "promoter extraction" in by_requirement["promoter cis-element visualization"]["note"]
    assert "promoter cis-element" in by_requirement["promoter cis-element visualization"]["note"]
    assert "Nextflow standard visualization smoke" in by_requirement["expression heatmap visualization"]["evidence"]
    assert "RNA-seq" in by_requirement["expression heatmap visualization"]["note"]
    assert "Nextflow report evidence" in by_requirement["expression heatmap visualization"]["note"]
    assert "Nextflow standard visualization smoke" in by_requirement["PPI ggNetView visualization"]["evidence"]
    assert "ggNetView" in by_requirement["PPI ggNetView visualization"]["note"]
    assert "Nextflow report evidence" in by_requirement["PPI ggNetView visualization"]["note"]
    assert "gamma beta alpha theta" in by_requirement["Ka/Ks WGD visualization"]["note"]
    assert "Nextflow WGD event smoke" in by_requirement["Ka/Ks WGD visualization"]["evidence"]
    assert "WGD publication report audit" in by_requirement["Ka/Ks WGD visualization"]["evidence"]
    assert "Nextflow report evidence" in by_requirement["Ka/Ks WGD visualization"]["note"]


def test_promoter_cis_element_visualization_requires_promoter_extraction_smoke():
    release_rows = [
        _release_row("promoter cis-element visualization smoke"),
        _release_row("Nextflow standard visualization smoke"),
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

    assert by_requirement["promoter cis-element visualization"]["status"] == "missing"
    assert "promoter smoke" in by_requirement["promoter cis-element visualization"]["evidence"]


def test_paper_level_visualization_modules_require_wgd_visualization_evidence():
    release_rows = [
        _release_row("gene family information visualization smoke"),
        _release_row("feature summary visualization smoke"),
        _release_row("tree feature visualization smoke"),
        _release_row("synteny parser smoke"),
        _release_row("MCScanX circlize visualization smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("promoter cis-element visualization smoke"),
        _release_row("standard branch expression smoke"),
        _release_row("expression heatmap visualization smoke"),
        _release_row("PPI ggNetView plot smoke"),
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
    assert "Ka/Ks WGD annotation plot smoke" in by_requirement["paper-level visualization modules"]["evidence"]
    assert "Nextflow WGD event smoke" in by_requirement["paper-level visualization modules"]["evidence"]
    assert "WGD publication report audit" in by_requirement["paper-level visualization modules"]["evidence"]


def test_kaks_wgd_visualization_requires_nextflow_wgd_report_evidence():
    release_rows = [
        _release_row("Ka/Ks WGD annotation plot smoke"),
        _release_row("duplicate-type Ka/Ks visualization smoke"),
        _release_row("pangenome-class Ka/Ks visualization smoke"),
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

    assert by_requirement["Ka/Ks WGD visualization"]["status"] == "missing"
    assert "Nextflow WGD event smoke" in by_requirement["Ka/Ks WGD visualization"]["evidence"]
    assert "WGD publication report audit" in by_requirement["Ka/Ks WGD visualization"]["evidence"]


def test_mcscanx_synteny_circlize_visualization_requires_nextflow_standard_visualization_smoke():
    release_rows = [
        _release_row("synteny parser smoke"),
        _release_row("MCScanX circlize visualization smoke"),
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

    assert by_requirement["MCScanX synteny circlize visualization"]["status"] == "missing"
    assert "Nextflow standard visualization smoke" in by_requirement["MCScanX synteny circlize visualization"]["evidence"]


def test_gene_family_information_copy_number_requires_nextflow_standard_visualization_smoke():
    release_rows = [
        _release_row("gene family information visualization smoke"),
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

    assert by_requirement["gene family information and copy-number visualization"]["status"] == "missing"
    assert "Nextflow standard visualization smoke" in by_requirement[
        "gene family information and copy-number visualization"
    ]["evidence"]


def test_tree_motif_gene_structure_domain_requires_nextflow_standard_visualization_smoke():
    release_rows = [
        _release_row("tree feature visualization smoke"),
        _release_row("feature summary visualization smoke"),
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

    assert by_requirement["tree motif gene-structure domain visualization"]["status"] == "missing"
    assert "Nextflow standard visualization smoke" in by_requirement[
        "tree motif gene-structure domain visualization"
    ]["evidence"]


def test_ppi_ggnetview_visualization_requires_nextflow_standard_visualization_smoke():
    release_rows = [
        _release_row("PPI ggNetView smoke"),
        _release_row("PPI ggNetView plot smoke"),
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

    assert by_requirement["PPI ggNetView visualization"]["status"] == "missing"
    assert "Nextflow standard visualization smoke" in by_requirement["PPI ggNetView visualization"]["evidence"]


def test_ppi_ggnetview_visualization_requires_ggnetview_status_smoke():
    release_rows = [
        _release_row("PPI ggNetView plot smoke"),
        _release_row("Nextflow standard visualization smoke"),
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

    assert by_requirement["PPI ggNetView visualization"]["status"] == "missing"
    assert "PPI ggNetView smoke" in by_requirement["PPI ggNetView visualization"]["evidence"]


def test_expression_heatmap_visualization_requires_nextflow_standard_visualization_smoke():
    release_rows = [
        _release_row("standard branch expression smoke"),
        _release_row("expression heatmap visualization smoke"),
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

    assert by_requirement["expression heatmap visualization"]["status"] == "missing"
    assert "Nextflow standard visualization smoke" in by_requirement["expression heatmap visualization"]["evidence"]


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


def test_yaml_driven_species_selection_requires_nextflow_manifest_standard_smoke():
    release_rows = [
        _release_row("validate example config"),
        _release_row("validate advanced config"),
        _release_row("validate manifest config"),
        _release_row("species selection smoke"),
        _release_row("species manifest selection smoke"),
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
    assert "Nextflow standard manifest smoke" in by_requirement["YAML-driven species selection"]["evidence"]


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


def test_final_reports_require_publication_report_audit():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("prepared WGD handoff example"),
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

    assert by_requirement["final reports"]["status"] == "missing"
    assert "publication report audit" in by_requirement["final reports"]["evidence"]


def test_final_reports_require_standard_report_index_audit():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
        _release_row("WGD publication report audit"),
        _release_row("WGD report index audit"),
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

    rows = build_objective_audit(
        release_rows,
        readiness_rows,
        publication_audit_rows=_publication_audit_rows(),
        wgd_publication_audit_rows=_publication_audit_rows(),
    )
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["final reports"]["status"] == "missing"
    assert "standard report index audit" in by_requirement["final reports"]["evidence"]


def test_final_reports_require_wgd_publication_report_audit():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
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

    assert by_requirement["final reports"]["status"] == "missing"
    assert "WGD publication report audit" in by_requirement["final reports"]["evidence"]


def test_final_reports_require_nextflow_standard_and_wgd_report_sources():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
        _release_row("WGD publication report audit"),
        _release_row("standard report index audit"),
        _release_row("WGD report index audit"),
        _release_row("delivery bundle figure gallery audit"),
        _release_row("delivery bundle manifest audit"),
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

    assert by_requirement["final reports"]["status"] == "missing"
    assert "Nextflow standard visualization smoke" in by_requirement["final reports"]["evidence"]
    assert "Nextflow WGD event smoke" in by_requirement["final reports"]["evidence"]


def test_final_reports_require_delivery_figure_gallery_audit():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
        _release_row("WGD publication report audit"),
        _release_row("standard report index audit"),
        _release_row("WGD report index audit"),
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

    rows = build_objective_audit(
        release_rows,
        readiness_rows,
        publication_audit_rows=_publication_audit_rows(),
        wgd_publication_audit_rows=_publication_audit_rows(),
    )
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["final reports"]["status"] == "missing"
    assert "delivery bundle figure gallery audit" in by_requirement["final reports"]["evidence"]


def test_final_reports_require_delivery_manifest_audit():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
        _release_row("WGD publication report audit"),
        _release_row("standard report index audit"),
        _release_row("WGD report index audit"),
        _release_row("delivery bundle figure gallery audit"),
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

    rows = build_objective_audit(
        release_rows,
        readiness_rows,
        publication_audit_rows=_publication_audit_rows(),
        wgd_publication_audit_rows=_publication_audit_rows(),
    )
    by_requirement = {row["requirement"]: row for row in rows}

    assert by_requirement["final reports"]["status"] == "missing"
    assert "delivery bundle manifest audit" in by_requirement["final reports"]["evidence"]


def test_final_reports_note_names_complete_publication_report_closure():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
        _release_row("WGD publication report audit"),
        _release_row("standard report index audit"),
        _release_row("WGD report index audit"),
        _release_row("delivery bundle figure gallery audit"),
        _release_row("delivery bundle manifest audit"),
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

    rows = build_objective_audit(
        release_rows,
        readiness_rows,
        publication_audit_rows=_publication_audit_rows(),
        wgd_publication_audit_rows=_publication_audit_rows(),
    )
    final_report_row = {row["requirement"]: row for row in rows}["final reports"]

    assert final_report_row["status"] == "achieved"
    assert "complete per-figure close-reading text" in final_report_row["note"]
    assert "valid plot file signatures" in final_report_row["note"]
    assert "registered-only figure interpretation scope" in final_report_row["note"]
    assert "plot manifest and interpretation output path consistency" in final_report_row["note"]
    assert "input data" in final_report_row["note"]
    assert "what the figure shows" in final_report_row["note"]
    assert "key observations" in final_report_row["note"]
    assert "biological interpretation" in final_report_row["note"]
    assert "QC warnings" in final_report_row["note"]
    assert "figure-specific QC warnings" in final_report_row["note"]
    assert "software/R package versions" in final_report_row["note"]
    assert "parseable detected version values" in final_report_row["note"]
    assert "Figure Traceability Matrix" in final_report_row["note"]
    assert "embedded PNG plot previews" in final_report_row["note"]
    assert "delivery figure gallery" in final_report_row["note"]
    assert "figure_gallery_audit" in final_report_row["note"]
    assert "valid gallery plot file signatures" in final_report_row["note"]
    assert "per-figure close-reading anchors" in final_report_row["note"]
    assert "delivery manifest audit" in final_report_row["note"]
    assert "reproducibility commands" in final_report_row["note"]
    assert "no TODO/TBD/placeholder text" in final_report_row["note"]


def test_final_reports_require_traceability_matrix_checks_in_publication_audits():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
        _release_row("WGD publication report audit"),
        _release_row("standard report index audit"),
        _release_row("WGD report index audit"),
        _release_row("delivery bundle figure gallery audit"),
        _release_row("delivery bundle manifest audit"),
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

    rows = build_objective_audit(
        release_rows,
        readiness_rows,
        publication_audit_rows=_publication_audit_rows(omit={"final_report_figure_traceability"}),
        wgd_publication_audit_rows=_publication_audit_rows(),
    )
    final_report_row = {row["requirement"]: row for row in rows}["final reports"]

    assert final_report_row["status"] == "missing"
    assert "standard publication audit missing/pending: final_report_figure_traceability" in final_report_row["note"]


def test_final_reports_require_placeholder_text_checks_in_publication_audits():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
        _release_row("WGD publication report audit"),
        _release_row("standard report index audit"),
        _release_row("WGD report index audit"),
        _release_row("delivery bundle figure gallery audit"),
        _release_row("delivery bundle manifest audit"),
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

    rows = build_objective_audit(
        release_rows,
        readiness_rows,
        publication_audit_rows=_publication_audit_rows(omit={"final_report_placeholder_text"}),
        wgd_publication_audit_rows=_publication_audit_rows(),
    )
    final_report_row = {row["requirement"]: row for row in rows}["final reports"]

    assert final_report_row["status"] == "missing"
    assert "standard publication audit missing/pending: final_report_placeholder_text" in final_report_row["note"]


def test_final_reports_require_plot_preview_checks_in_publication_audits():
    release_rows = [
        _release_row("standard branch smoke"),
        _release_row("Nextflow standard visualization smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("prepared WGD handoff example"),
        _release_row("quickstart handoff"),
        _release_row("publication report audit"),
        _release_row("WGD publication report audit"),
        _release_row("standard report index audit"),
        _release_row("WGD report index audit"),
        _release_row("delivery bundle figure gallery audit"),
        _release_row("delivery bundle manifest audit"),
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

    rows = build_objective_audit(
        release_rows,
        readiness_rows,
        publication_audit_rows=_publication_audit_rows(omit={"final_report_plot_previews"}),
        wgd_publication_audit_rows=_publication_audit_rows(),
    )
    final_report_row = {row["requirement"]: row for row in rows}["final reports"]

    assert final_report_row["status"] == "missing"
    assert "standard publication audit missing/pending: final_report_plot_previews" in final_report_row["note"]


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


def test_standard_identification_branch_requires_alignment_phylogeny_smoke():
    release_rows = [
        _release_row("domain filter smoke"),
        _release_row("motif parser smoke"),
        _release_row("gene structure smoke"),
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
    assert "alignment phylogeny smoke" in by_requirement["standard identification branch"]["evidence"]


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


def test_wgd_event_evidence_names_nextflow_wgd_branch_evidence():
    release_rows = [
        _release_row("synteny parser smoke"),
        _release_row("WGD event smoke"),
        _release_row("Nextflow WGD event smoke"),
        _release_row("Nextflow raw MCScanX/KaKs WGD smoke"),
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

    assert by_requirement["WGD gamma beta alpha theta evidence"]["status"] == "achieved"
    assert "Nextflow WGD event smoke" in by_requirement["WGD gamma beta alpha theta evidence"]["evidence"]
    assert "formal Nextflow WGD branch" in by_requirement["WGD gamma beta alpha theta evidence"]["note"]


def test_wgd_event_evidence_requires_raw_mcscanx_kaks_nextflow_smoke():
    release_rows = [
        _release_row("synteny parser smoke"),
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
    assert "Nextflow raw MCScanX/KaKs WGD smoke" in by_requirement["WGD gamma beta alpha theta evidence"]["evidence"]


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


def test_kaks_and_retention_analysis_requires_duplicate_type_kaks_visualization_smoke():
    release_rows = [
        _release_row("Ka/Ks parser smoke"),
        _release_row("retention enrichment smoke"),
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
    assert "duplicate-type Ka/Ks visualization smoke" in by_requirement["Ka/Ks and retention analysis"]["evidence"]


def test_kaks_and_retention_analysis_requires_pangenome_and_nextflow_wgd_evidence():
    release_rows = [
        _release_row("Ka/Ks parser smoke"),
        _release_row("duplicate-type Ka/Ks visualization smoke"),
        _release_row("retention enrichment smoke"),
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
    assert "pangenome-class Ka/Ks visualization smoke" in by_requirement["Ka/Ks and retention analysis"]["evidence"]
    assert "Nextflow WGD event smoke" in by_requirement["Ka/Ks and retention analysis"]["evidence"]


def test_kaks_and_retention_analysis_requires_raw_mcscanx_kaks_nextflow_smoke():
    release_rows = [
        _release_row("Ka/Ks parser smoke"),
        _release_row("duplicate-type Ka/Ks visualization smoke"),
        _release_row("pangenome-class Ka/Ks visualization smoke"),
        _release_row("retention enrichment smoke"),
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

    assert by_requirement["Ka/Ks and retention analysis"]["status"] == "missing"
    assert "Nextflow raw MCScanX/KaKs WGD smoke" in by_requirement["Ka/Ks and retention analysis"]["evidence"]


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


def test_chromosome_and_expression_integration_requires_nextflow_and_heatmap_evidence():
    release_rows = [
        _release_row("chromosome location smoke"),
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
    assert "Nextflow standard branch smoke" in by_requirement["chromosome and expression integration"]["evidence"]
    assert "expression heatmap visualization smoke" in by_requirement["chromosome and expression integration"]["evidence"]


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
        "duplicate-type Ka/Ks visualization smoke\ttrue\tpassed\t0\tduplicate_type_kaks\t\n"
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
