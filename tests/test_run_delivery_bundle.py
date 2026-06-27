import subprocess
import sys
from pathlib import Path


def _write_tsv(path: Path, header: str, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_run_delivery_bundle_cli_writes_user_facing_index(tmp_path):
    release = tmp_path / "release_checks.tsv"
    objective = tmp_path / "objective_audit.tsv"
    readiness = tmp_path / "command_readiness.tsv"
    quickstart = tmp_path / "quickstart_summary.tsv"
    outdir = tmp_path / "delivery_bundle"

    _write_tsv(
        release,
        "check\trequired\tstatus\texit_code\tcommand\tnote",
        [
            "standard branch smoke\ttrue\tpassed\t0\tstandard\tfinal report",
            "Nextflow standard manifest smoke\ttrue\tpassed\t0\tnextflow manifest\tmanifest config",
            "WGD event smoke\ttrue\tpassed\t0\twgd\talpha beta gamma theta",
            "publication report audit\ttrue\tpassed\t0\tpublication report\tfigures interpreted",
            "standard report index audit\ttrue\tpassed\t0\tstandard report index\tindexed standard report artifacts",
            "WGD publication report audit\ttrue\tpassed\t0\twgd publication report\twgd figures interpreted",
            "WGD report index audit\ttrue\tpassed\t0\twgd report index\tindexed WGD report artifacts",
            "readiness audit\ttrue\tpassed\t0\treadiness\tcore tools available",
            "Docker profile smoke\tfalse\tfailed\t1\tdocker profile\tmissing runtime",
            "Apptainer profile smoke\tfalse\tfailed\t1\tapptainer profile\tmissing runtime",
        ],
    )
    _write_tsv(
        objective,
        "requirement\tstatus\tevidence\tnote",
        [
            "final reports\tachieved\tstandard and WGD reports\tok",
            "Docker/Apptainer reproducibility\tblocked\treadiness\tMissing container commands: docker, apptainer",
        ],
    )
    _write_tsv(
        readiness,
        "command\tstatus\tpath",
        [
            "nextflow\tavailable_in_conda\tGeneFamilyFlow:/bin/nextflow",
            "/usr/local/bin/R\tavailable\t/usr/local/bin/R",
            "docker\tmissing\t",
            "apptainer\tmissing\t",
        ],
    )
    _write_tsv(
        quickstart,
        "step\tstatus\tpath\tnote",
        [
            "standard_branch_smoke\tpassed\tresults/quickstart/standard_smoke/report/final_report.md\tstandard report",
            "prepared_wgd_handoff\tpassed\tresults/quickstart/example_prepared_wgd/report/final_report.md\talpha beta gamma theta evidence",
        ],
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_delivery_bundle.py",
            "--release-checks",
            str(release),
            "--objective-audit",
            str(objective),
            "--readiness",
            str(readiness),
            "--quickstart",
            str(quickstart),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    manifest = outdir / "delivery_manifest.tsv"
    summary = outdir / "delivery_bundle.md"
    gallery = outdir / "figure_gallery.tsv"
    gallery_md = outdir / "figure_gallery.md"
    assert manifest.exists()
    assert summary.exists()
    assert gallery.exists()
    assert gallery_md.exists()

    manifest_text = manifest.read_text(encoding="utf-8")
    assert manifest_text.startswith("section\titem\tstatus\tpath\tnote\n")
    assert (
        "status\tfigure_gallery\tavailable\t"
        + str(gallery)
        + "\tglobal figure gallery linking paper-level plots to their close-reading reports and software versions"
        in manifest_text
    )
    assert "standard\tfinal_report\tavailable\tresults/quickstart/standard_smoke/report/final_report.md" in manifest_text
    assert (
        "standard\trun_config_snapshot\tavailable\tresults/quickstart/standard_smoke/tables/run_config_snapshot.tsv\tstandard branch run configuration"
        in manifest_text
    )
    assert (
        "standard\twgd_handoff_manifest\tavailable\tresults/quickstart/standard_smoke/tables/wgd_handoff_manifest.tsv\tstandard-to-WGD handoff checklist"
        in manifest_text
    )
    assert (
        "standard\tpaper_level_visual_report\tavailable\tresults/nextflow_standard_feature_smoke/standard/report/final_report.md\tpaper-level standard visualization report with tree/motif/gene-structure/domain, MCScanX/circlize, promoter cis-elements, expression heatmap, copy number, feature summary, and ggNetView PPI"
        in manifest_text
    )
    assert (
        "standard\tpaper_level_plot_manifest\tavailable\tresults/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv\tregistered plot inventory for the full standard visualization branch"
        in manifest_text
    )
    assert (
        "standard\tpaper_level_figure_interpretations\tavailable\tresults/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md\tper-figure close reading for the full standard visualization branch"
        in manifest_text
    )
    assert (
        "standard\tpaper_level_software_versions\tavailable\tresults/nextflow_standard_feature_smoke/standard/report/software_versions.tsv\tsoftware and R package versions for the full standard visualization branch"
        in manifest_text
    )
    assert "input\tmanifest_config\tavailable\tconfigs/manifest.example.yaml\tmanifest-mode YAML example" in manifest_text
    assert (
        "input\tspecies_bank_config\tavailable\tconfigs/example.config.yaml\tspecies-bank YAML example with selected species"
        in manifest_text
    )
    assert (
        "input\tmanifest_fixture\tavailable\ttests/fixtures/species_manifest.tsv\tprebuilt species manifest fixture"
        in manifest_text
    )
    assert (
        "input\tmanifest_selection_smoke\tavailable\tresults/species_manifest_selection_smoke/tables/species_manifest.tsv\tmanifest-mode selected species"
        in manifest_text
    )
    assert (
        "nextflow\tnextflow_standard_manifest_smoke\tavailable\tresults/nextflow_standard_manifest_smoke/nextflow_standard_smoke.tsv\tmanifest-mode standard DSL2 smoke"
        in manifest_text
    )
    assert (
        "nextflow\tconfig_preflight\tavailable\tworkflows/modules/config_validation.nf\tstrict config path preflight before Nextflow branches"
        in manifest_text
    )
    assert "wgd\tfinal_report\tavailable\tresults/quickstart/example_prepared_wgd/report/final_report.md" in manifest_text
    assert (
        "wgd\trun_config_snapshot\tavailable\tresults/quickstart/example_prepared_wgd/tables/wgd_run_config_snapshot.tsv\tWGD branch run configuration"
        in manifest_text
    )
    assert (
        "wgd\twgd_paper_level_visual_report\tavailable\tresults/nextflow_wgd_smoke/wgd/report/final_report.md\tpaper-level Nextflow WGD report with Ka/Ks, Ks-derived WGD layers, gamma beta alpha theta event interpretation, retention enrichment, duplicate-type selection, and pangenome-class selection"
        in manifest_text
    )
    assert (
        "wgd\twgd_paper_level_plot_manifest\tavailable\tresults/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv\tregistered plot inventory for the formal Nextflow WGD branch"
        in manifest_text
    )
    assert (
        "wgd\twgd_paper_level_figure_interpretations\tavailable\tresults/nextflow_wgd_smoke/wgd/report/figure_interpretations.md\tper-figure close reading for the formal Nextflow WGD branch"
        in manifest_text
    )
    assert (
        "wgd\twgd_paper_level_software_versions\tavailable\tresults/nextflow_wgd_smoke/wgd/report/software_versions.tsv\tsoftware and R package versions for the formal Nextflow WGD branch"
        in manifest_text
    )
    assert (
        "wgd\tevents_config\tavailable\tconfigs/wgd_events.brassicaceae.yaml\tgamma beta alpha theta named-event YAML mapping"
        in manifest_text
    )
    assert "wgd\tevent_evidence\tavailable\tresults/wgd_smoke/tables/wgd_event_evidence.tsv\talpha,beta,gamma,theta" in manifest_text
    assert (
        "governance\treference_governance\tavailable\tresults/reference_governance/reference_governance.md\ttracked Reference/ changes are release-blocking"
        in manifest_text
    )
    assert (
        "governance\treference_gitignore\tavailable\t.gitignore\tReference/ ignored so paper PDFs, source data, and plotting templates are not accidentally staged"
        in manifest_text
    )
    assert (
        "governance\treference_governance_tsv\tavailable\tresults/reference_governance/reference_governance.tsv\tmachine-readable Reference/ status"
        in manifest_text
    )
    assert "runtime\tGeneFamilyFlow\tavailable\tGeneFamilyFlow:/bin/nextflow" in manifest_text
    assert "runtime\t/usr/local/bin/R\tavailable\t/usr/local/bin/R" in manifest_text
    assert "runtime\tdocker\tmissing\t" in manifest_text
    assert "runtime\tapptainer\tmissing\t" in manifest_text
    assert (
        "runtime_recovery\tbootstrap_plan\tavailable\tresults/readiness/runtime_bootstrap_plan.md\tcontainer/runtime recovery plan"
        in manifest_text
    )
    assert (
        "runtime_recovery\tbootstrap_shell\tavailable\tresults/readiness/runtime_bootstrap.sh\texecutable recovery and verification script"
        in manifest_text
    )
    assert (
        "runtime_recovery\tlocal_acceptance\tavailable\tscripts/run_local_acceptance.sh\trefreshes release, handoff, quickstart, and delivery bundle outputs"
        in manifest_text
    )
    assert (
        "runtime_recovery\tcontainer_default_smoke\tavailable\tDockerfile\tdocker run default command writes results/container_default_smoke"
        in manifest_text
    )
    assert (
        "status\tlocal_acceptance_summary\tblocked\tresults/local_acceptance/local_acceptance_summary.md\tcompact local acceptance pass/fail index; overall=blocked; final_stage_blocker=Docker/Apptainer reproducibility"
        in manifest_text
    )
    assert (
        "status\tpublication_report_audit\tavailable\tresults/publication_report_audit/publication_report_audit.md\tpaper-style report closure: valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete per-figure close-reading text, QC tables and warnings, software/R package versions, per-figure method/software version coverage, and reproducibility commands"
        in manifest_text
    )
    assert (
        "status\tstandard_report_index_audit\tavailable\tresults/report_index_audit/standard_report_index_audit.md\treport-index closure: standard report index exposes plot manifest, software versions, figure interpretations in TSV/Markdown, and final report"
        in manifest_text
    )
    assert (
        "status\twgd_publication_report_audit\tavailable\tresults/publication_report_audit/wgd_publication_report_audit.md\tWGD report closure: valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete Ka/Ks/WGD figure close-reading text, gamma beta alpha theta interpretation, QC tables and warnings, software/R package versions, per-figure method/software version coverage, and reproducibility commands"
        in manifest_text
    )
    assert (
        "status\twgd_report_index_audit\tavailable\tresults/report_index_audit/wgd_report_index_audit.md\treport-index closure: WGD report index exposes plot manifest, software versions, figure interpretations in TSV/Markdown, and final report"
        in manifest_text
    )
    assert (
        "status\tfinal_stage_blocker\tblocked\tresults/objective_audit/objective_audit.md\tDocker/Apptainer reproducibility"
        in manifest_text
    )
    assert (
        "status\trelease_ready\tavailable\tresults/release_checks/release_checks.md\trelease_ready=true; optional_failed=2"
        in manifest_text
    )
    assert (
        "runtime_recovery\tdocker_profile_smoke\tmissing\tresults/container_profile_smoke/docker/container_profile_smoke.md\toptional container profile diagnostic"
        in manifest_text
    )
    assert (
        "runtime_recovery\tapptainer_profile_smoke\tmissing\tresults/container_profile_smoke/apptainer/container_profile_smoke.md\toptional container profile diagnostic"
        in manifest_text
    )

    summary_text = summary.read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Delivery Bundle" in summary_text
    assert "figure_gallery" in summary_text
    assert str(gallery) in summary_text
    assert "standard report" in summary_text
    assert "paper_level_visual_report" in summary_text
    assert "results/nextflow_standard_feature_smoke/standard/report/final_report.md" in summary_text
    assert "tree/motif/gene-structure/domain, MCScanX/circlize, promoter cis-elements, expression heatmap, copy number, feature summary, and ggNetView PPI" in summary_text
    assert "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md" in summary_text
    assert "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv" in summary_text
    assert "manifest-mode YAML example" in summary_text
    assert "species-bank YAML example with selected species" in summary_text
    assert "manifest-mode standard DSL2 smoke" in summary_text
    assert "strict config path preflight" in summary_text
    assert "gamma beta alpha theta named-event YAML mapping" in summary_text
    assert "wgd_paper_level_visual_report" in summary_text
    assert "results/nextflow_wgd_smoke/wgd/report/final_report.md" in summary_text
    assert "Ka/Ks, Ks-derived WGD layers, gamma beta alpha theta event interpretation, retention enrichment, duplicate-type selection, and pangenome-class selection" in summary_text
    assert "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.md" in summary_text
    assert "results/nextflow_wgd_smoke/wgd/report/software_versions.tsv" in summary_text
    assert "alpha, beta, gamma, theta" in summary_text
    assert "Reference governance" in summary_text
    assert "reference_gitignore" in summary_text
    assert "Reference/ ignored so paper PDFs, source data, and plotting templates are not accidentally staged" in summary_text
    assert "runtime recovery" in summary_text
    assert "results/container_default_smoke" in summary_text
    assert "compact local acceptance pass/fail index" in summary_text
    assert "overall=blocked; final_stage_blocker=Docker/Apptainer reproducibility" in summary_text
    assert "complete per-figure close-reading text" in summary_text
    assert "valid plot file signatures" in summary_text
    assert "registered-only figure interpretation scope" in summary_text
    assert "plot manifest and interpretation output path consistency" in summary_text
    assert "QC tables and warnings" in summary_text
    assert "software/R package versions" in summary_text
    assert "per-figure method/software version coverage" in summary_text
    assert "reproducibility commands" in summary_text
    assert "results/publication_report_audit/publication_report_audit.md" in summary_text
    assert "results/report_index_audit/standard_report_index_audit.md" in summary_text
    assert "standard_report_index_audit" in summary_text
    assert "report-index closure" in summary_text
    assert "complete Ka/Ks/WGD figure close-reading text" in summary_text
    assert "results/publication_report_audit/wgd_publication_report_audit.md" in summary_text
    assert "results/report_index_audit/wgd_report_index_audit.md" in summary_text
    assert "wgd_report_index_audit" in summary_text
    assert "Docker/Apptainer reproducibility" in summary_text
    assert "final_stage_blocker" in summary_text
    assert "release_ready=true" in summary_text
    assert "results/container_profile_smoke/docker/container_profile_smoke.md" in summary_text
    assert "results/container_profile_smoke/apptainer/container_profile_smoke.md" in summary_text

    gallery_text = gallery.read_text(encoding="utf-8")
    assert gallery_text.startswith(
        "branch\tplot_key\tplot_path\tplot_description\tfigure_interpretations\tsoftware_versions\tfinal_report\ttraceability_matrix\n"
    )
    assert (
        "standard\ttree_features\tresults/nextflow_standard_feature_smoke/standard/plots/tree_features.pdf\tTree, motif, gene-structure, and domain composite plot\tresults/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md\tresults/nextflow_standard_feature_smoke/standard/report/software_versions.tsv\tresults/nextflow_standard_feature_smoke/standard/report/final_report.md\tresults/nextflow_standard_feature_smoke/standard/report/final_report.md#figure-traceability-matrix"
        in gallery_text
    )
    assert (
        "standard\tmcscanx_circlize\tresults/nextflow_standard_feature_smoke/standard/plots/mcscanx_circlize.pdf\tMCScanX synteny and chromosome-scale circlize plot\tresults/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md\tresults/nextflow_standard_feature_smoke/standard/report/software_versions.tsv\tresults/nextflow_standard_feature_smoke/standard/report/final_report.md"
        in gallery_text
    )
    assert (
        "standard\tgene_family_pangenome_summary\tresults/nextflow_standard_feature_smoke/standard/plots/gene_family_info_summary.pdf\tGene family pangenome presence and copy-number balance\tresults/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md\tresults/nextflow_standard_feature_smoke/standard/report/software_versions.tsv\tresults/nextflow_standard_feature_smoke/standard/report/final_report.md"
        in gallery_text
    )
    assert (
        "standard\tppi_ggnetview\tresults/nextflow_standard_feature_smoke/standard/plots/ppi_ggnetview.pdf\tPPI network generated with ggNetView\tresults/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md\tresults/nextflow_standard_feature_smoke/standard/report/software_versions.tsv\tresults/nextflow_standard_feature_smoke/standard/report/final_report.md"
        in gallery_text
    )
    assert (
        "wgd\tks_distribution\tresults/nextflow_wgd_smoke/wgd/plots/ks_distribution.pdf\tKs distribution for duplicated pairs and WGD layer interpretation\tresults/nextflow_wgd_smoke/wgd/report/figure_interpretations.md\tresults/nextflow_wgd_smoke/wgd/report/software_versions.tsv\tresults/nextflow_wgd_smoke/wgd/report/final_report.md"
        in gallery_text
    )
    assert (
        "wgd\tduplicate_type_kaks\tresults/nextflow_wgd_smoke/wgd/plots/duplicate_type_kaks.pdf\tDuplicate-type grouped Ks and Ka/Ks selection overview\tresults/nextflow_wgd_smoke/wgd/report/figure_interpretations.md\tresults/nextflow_wgd_smoke/wgd/report/software_versions.tsv\tresults/nextflow_wgd_smoke/wgd/report/final_report.md"
        in gallery_text
    )

    gallery_md_text = gallery_md.read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Figure Gallery" in gallery_md_text
    assert "tree_features" in gallery_md_text
    assert "gene_family_pangenome_summary" in gallery_md_text
    assert "ks_distribution" in gallery_md_text
    assert "software_versions.tsv" in gallery_md_text
    assert "traceability_matrix" in gallery_md_text
    assert "final_report.md#figure-traceability-matrix" in gallery_md_text
