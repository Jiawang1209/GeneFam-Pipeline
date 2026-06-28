from pathlib import Path

from bin.genefam.organize_module_results import organize


def touch(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_organize_module_results_creates_reference_style_module_folders(tmp_path):
    source = tmp_path / "standard"
    touch(source / "tables/family_candidates.tsv")
    touch(source / "tables/all_transcript_gene_map.tsv")
    touch(source / "tables/all_representative_transcripts.tsv")
    touch(source / "tables/all_preprocess_warnings.tsv")
    touch(source / "species_bank_clean/A/A.pep.clean.fa")
    touch(source / "tables/pfam_confirmation/pfam_confirmation_status.tsv", "status\thmm_id\tcandidate_count\tconfirmed_count\tnote\nmissing_input\tPF00657\t2\t0\tNo Pfam HMM database or precomputed hmmscan domtblout was provided\n")
    touch(source / "tables/pfam_confirmation/inter.ID")
    touch(source / "tables/pfam_confirmation/identify.ID.fa")
    touch(source / "plots/family_counts.pdf")
    touch(source / "plots/family_counts.png")
    touch(source / "tables/domain_filter/Arabidopsis.family_candidates.tsv")
    touch(source / "two_pass_hmmer/first_pass_hits.faa")
    touch(source / "two_pass_hmmer/first_pass_hits.aln.faa")
    touch(source / "two_pass_hmmer/GDSL.rebuilt.hmm")
    touch(source / "two_pass_hmmer/rebuilt_hmmer_inputs.tsv")
    touch(source / "two_pass_hmmer/rebuilt_hmmer_status.tsv")
    touch(source / "alignment/GDSL.mafft.aln.faa")
    touch(source / "phylogeny/GDSL.fasttree.treefile")
    touch(source / "tables/promoters.bed")
    touch(source / "sequences/promoters.fa")
    touch(source / "plantcare_submission/GDSL_promoters.part001.fa")
    touch(source / "plantcare_submission/plantcare_submission_manifest.tsv")
    touch(source / "plantcare_submission/plantcare_submission_status.tsv", "status\ttotal_records\tpart_count\trecords_per_file\tnote\navailable\t2\t1\t100\tPlantCARE submission FASTA parts prepared\n")
    touch(source / "tables/ppi_edges.tsv")
    touch(source / "tables/node_annotation.tsv")
    touch(source / "tables/species_ppi_annotation.tsv")
    touch(source / "tables/ppi_overview_status.tsv")
    touch(source / "tables/ppi_blast/Brassica_rapa/Brassica_rapa_to_Arabidopsis_thaliana.diamond.tsv")
    touch(source / "plots/ppi.pdf")
    touch(source / "plots/ppi.png")
    touch(source / "plots/ppi_ggnetview.pdf")
    touch(source / "jcvi_collinearity/jcvi_pair_manifest.tsv")
    touch(source / "jcvi_collinearity/commands/jcvi_commands.sh")
    touch(source / "jcvi_collinearity/jcvi_dependency_status.tsv", "check\tstatus\tdetail\njcvi_python_module\tmissing_dependency\tInstall jcvi\n")
    touch(source / "jcvi_collinearity/jcvi_run_status.tsv", "status\tcommand_count\tsucceeded_count\tfailed_count\tnote\nmissing_dependency\t5\t0\t0\tJCVI Python module is not importable with python\n")
    touch(source / "mcscanx_self_circos/mcscanx_self_status.tsv", "species_id\tstatus\tfamily_bed\tgene_type\ttandem\tcollinearity\tnote\nA\tmissing_input\tfamily_beds/A.GF.bed\t\t\t\tmissing\n")
    touch(source / "mcscanx_self_circos/mcscanx_run_status.tsv", "species_id\tstatus\tmcscanx_gff\tpep\tcommand\tnote\nA\tprepared\tmcscanx_run/A.gff\tA.pep.fa\tcommands/mcscanx_self_commands.sh\tprepared\n")
    touch(source / "mcscanx_self_circos/mcscanx_execution_status.tsv", "status\texecute\tmissing_tools\tcommand\texit_code\tnote\nready_not_executed\tfalse\t\tcommands/mcscanx_self_commands.sh\t\tready\n")
    touch(source / "mcscanx_self_circos/mcscanx_execution.log", "running\n")
    touch(source / "mcscanx_self_circos/family_beds/A.GF.bed")
    touch(source / "mcscanx_self_circos/mcscanx_run/A.gff")
    touch(source / "mcscanx_self_circos/mcscanx_run/A.blast")
    touch(source / "mcscanx_self_circos/mcscanx_run/A.collinearity")
    touch(source / "mcscanx_self_circos/mcscanx_run/A.tandem")
    touch(source / "mcscanx_self_circos/mcscanx_run/A.html/chr1.html")
    touch(source / "mcscanx_self_circos/commands/mcscanx_self_commands.sh")
    touch(source / "report/plot_manifest.tsv", "plot_key\tpath\tdescription\nfamily_counts\tplots/family_counts.pdf\tFamily counts\n")
    touch(
        source / "report/report_index.tsv",
        "key\tpath\tstatus\tdescription\n"
        "family_counts_pdf\tresults/demo/plots/family_counts.pdf\tavailable\tFamily counts PDF plot\n"
        "family_counts_png\tresults/demo/plots/family_counts.png\tavailable\tFamily counts PNG plot\n",
    )
    touch(source / "report/final_report.md")

    outdir = tmp_path / "analysis_modules"
    rows = organize(source, outdir)

    by_module = {row["module"]: row for row in rows}
    assert (outdir / "00_preprocess/all_transcript_gene_map.tsv").exists()
    assert (outdir / "00_preprocess/all_representative_transcripts.tsv").exists()
    assert (outdir / "00_preprocess/all_preprocess_warnings.tsv").exists()
    assert (outdir / "00_preprocess/species_bank_clean/A/A.pep.clean.fa").exists()
    assert (outdir / "01_gene_identification/family_candidates.tsv").exists()
    assert (outdir / "01_gene_identification/pfam_confirmation/pfam_confirmation_status.tsv").exists()
    assert (outdir / "01_gene_identification/pfam_confirmation/identify.ID.fa").exists()
    assert (outdir / "02_domain_filtering/domain_filter/Arabidopsis.family_candidates.tsv").exists()
    assert (outdir / "02_domain_filtering/two_pass_hmmer/first_pass_hits.faa").exists()
    assert (outdir / "02_domain_filtering/two_pass_hmmer/first_pass_hits.aln.faa").exists()
    assert (outdir / "02_domain_filtering/two_pass_hmmer/GDSL.rebuilt.hmm").exists()
    assert (outdir / "02_domain_filtering/two_pass_hmmer/rebuilt_hmmer_inputs.tsv").exists()
    assert (outdir / "02_domain_filtering/two_pass_hmmer/rebuilt_hmmer_status.tsv").exists()
    assert (outdir / "03_alignment/GDSL.mafft.aln.faa").exists()
    assert (outdir / "04_phylogeny/GDSL.fasttree.treefile").exists()
    assert (outdir / "08_promoter/promoters.bed").exists()
    assert (outdir / "08_promoter/promoters.fa").exists()
    assert (outdir / "08_promoter/plantcare_submission/GDSL_promoters.part001.fa").exists()
    assert (outdir / "08_promoter/plantcare_submission/plantcare_submission_manifest.tsv").exists()
    assert (outdir / "10_synteny_jcvi/jcvi_pair_manifest.tsv").exists()
    assert (outdir / "10_synteny_jcvi/commands/jcvi_commands.sh").exists()
    assert (outdir / "12_ppi/ppi_edges.tsv").exists()
    assert (outdir / "12_ppi/node_annotation.tsv").exists()
    assert (outdir / "12_ppi/species_ppi_annotation.tsv").exists()
    assert (outdir / "12_ppi/ppi_overview_status.tsv").exists()
    assert (outdir / "12_ppi/ppi_blast/Brassica_rapa/Brassica_rapa_to_Arabidopsis_thaliana.diamond.tsv").exists()
    assert (outdir / "12_ppi/ppi.pdf").exists()
    assert (outdir / "12_ppi/ppi.png").exists()
    assert (outdir / "12_ppi/ppi_ggnetview.pdf").exists()
    assert (outdir / "plots/family_counts.pdf").exists()
    assert (outdir / "plots/family_counts.png").exists()
    report_index = (outdir / "report/report_index.tsv").read_text(encoding="utf-8")
    assert "family_counts_pdf\t../plots/family_counts.pdf\tavailable\tFamily counts PDF plot\n" in report_index
    assert "family_counts_png\t../plots/family_counts.png\tavailable\tFamily counts PNG plot\n" in report_index
    assert (outdir / "report/final_report.md").exists()
    assert (outdir / "module_manifest.tsv").exists()
    assert (outdir / "README.md").exists()
    assert (outdir / "module_status_summary.md").exists()
    module_status_summary = (outdir / "module_status_summary.md").read_text(encoding="utf-8")
    assert "## Module Execution Status" in module_status_summary
    assert "| 10_synteny_jcvi | JCVI Collinearity And Karyotype | prepared_missing_dependency |" in module_status_summary
    assert "JCVI Python module is not importable with python" in module_status_summary
    assert by_module["01_gene_identification"]["status"] == "available"
    assert by_module["10_synteny_jcvi"]["status"] == "prepared_missing_dependency"
    assert by_module["10_synteny_jcvi"]["note"] == "JCVI Python module is not importable with python"
    assert (outdir / "11_mcscanx/mcscanx_self_status.tsv").exists()
    assert (outdir / "11_mcscanx/mcscanx_run_status.tsv").exists()
    assert (outdir / "11_mcscanx/mcscanx_execution_status.tsv").exists()
    assert (outdir / "11_mcscanx/mcscanx_execution.log").exists()
    assert (outdir / "11_mcscanx/family_beds/A.GF.bed").exists()
    assert (outdir / "11_mcscanx/mcscanx_run/A.gff").exists()
    assert (outdir / "11_mcscanx/mcscanx_run/A.blast").exists()
    assert (outdir / "11_mcscanx/mcscanx_run/A.collinearity").exists()
    assert (outdir / "11_mcscanx/mcscanx_run/A.tandem").exists()
    assert (outdir / "11_mcscanx/mcscanx_run/A.html/chr1.html").exists()
    assert (outdir / "11_mcscanx/commands/mcscanx_self_commands.sh").exists()
    assert by_module["11_mcscanx"]["status"] == "missing_input"
    assert by_module["11_mcscanx"]["note"] == "ready"


def test_organize_module_results_replaces_existing_output(tmp_path):
    source = tmp_path / "standard"
    touch(source / "tables/family_candidates.tsv")
    outdir = tmp_path / "analysis_modules"
    touch(outdir / "old.txt", "old\n")

    organize(source, outdir)

    assert not (outdir / "old.txt").exists()
    assert (outdir / "01_gene_identification/family_candidates.tsv").exists()


def test_organize_module_results_marks_promoter_cis_missing_input(tmp_path):
    source = tmp_path / "standard"
    touch(
        source / "tables/promoter_cis_status.tsv",
        "status\tnote\nmissing_input\tPlantCARE gene-level hit table not provided\n",
    )

    rows = organize(source, tmp_path / "analysis_modules")

    by_module = {row["module"]: row for row in rows}
    assert by_module["09_promoter_cis"]["status"] == "missing_input"
    assert by_module["09_promoter_cis"]["note"] == "PlantCARE gene-level hit table not provided"


def test_organize_module_results_copies_reference_promoter_plots(tmp_path):
    source = tmp_path / "standard"
    touch(source / "tables/promoter_cis_elements.tsv")
    touch(source / "plots/promoter_cis_elements.pdf")
    touch(source / "plots/promoter1.pdf")
    touch(source / "plots/species_promoter2.pdf")

    rows = organize(source, tmp_path / "analysis_modules")

    by_module = {row["module"]: row for row in rows}
    assert by_module["09_promoter_cis"]["status"] == "available"
    assert (tmp_path / "analysis_modules/09_promoter_cis/promoter_cis_elements.pdf").exists()
    assert (tmp_path / "analysis_modules/09_promoter_cis/promoter1.pdf").exists()
    assert (tmp_path / "analysis_modules/09_promoter_cis/species_promoter2.pdf").exists()


def test_organize_module_results_marks_kaks_missing_input_from_status_file(tmp_path):
    source = tmp_path / "standard"
    touch(source / "tables/wgd_handoff_manifest.tsv")
    touch(
        source / "kaks_inputs/kaks_calculator_status.tsv",
        "status\tpair_count\tsucceeded_count\tfailed_count\tnote\nmissing_input\t0\t0\t0\tNo Ka/Ks input pairs were prepared\n",
    )

    rows = organize(source, tmp_path / "analysis_modules")

    by_module = {row["module"]: row for row in rows}
    assert by_module["14_duplication_retention_kaks"]["status"] == "missing_input"
    assert by_module["14_duplication_retention_kaks"]["note"] == "No Ka/Ks input pairs were prepared"


def test_organize_module_results_marks_kaks_partial_from_status_file(tmp_path):
    source = tmp_path / "standard"
    touch(source / "tables/wgd_handoff_manifest.tsv")
    touch(
        source / "kaks_inputs/kaks_calculator_status.tsv",
        "status\tpair_count\tsucceeded_count\tfailed_count\tnote\npartial\t289\t150\t139\tSome Ka/Ks jobs failed\n",
    )

    rows = organize(source, tmp_path / "analysis_modules")

    by_module = {row["module"]: row for row in rows}
    assert by_module["14_duplication_retention_kaks"]["status"] == "partial"
    assert by_module["14_duplication_retention_kaks"]["note"] == "Some Ka/Ks jobs failed"


def test_organize_module_results_places_mcscanx_duplicate_types_with_kaks_module(tmp_path):
    source = tmp_path / "standard"
    touch(source / "tables/wgd_handoff_manifest.tsv")
    touch(source / "tables/mcscanx_duplicate_types.tsv")
    touch(source / "tables/duplicate_type_kaks.tsv")
    touch(source / "tables/duplicate_type_kaks_summary.tsv")
    touch(source / "plots/duplicate_type_kaks.pdf")

    organize(source, tmp_path / "analysis_modules")

    assert (tmp_path / "analysis_modules/14_duplication_retention_kaks/mcscanx_duplicate_types.tsv").exists()
    assert (tmp_path / "analysis_modules/14_duplication_retention_kaks/duplicate_type_kaks.tsv").exists()
    assert (tmp_path / "analysis_modules/14_duplication_retention_kaks/duplicate_type_kaks_summary.tsv").exists()
    assert (tmp_path / "analysis_modules/14_duplication_retention_kaks/duplicate_type_kaks.pdf").exists()


def test_organize_module_results_marks_mcscanx_available_when_circlize_available(tmp_path):
    source = tmp_path / "standard"
    touch(
        source / "mcscanx_self_circos/mcscanx_self_status.tsv",
        "species_id\tstatus\tfamily_bed\tgene_type\ttandem\tcollinearity\tnote\nA\tmissing_input\tfamily_beds/A.GF.bed\t\t\tA.collinearity\tlegacy status\n",
    )
    touch(
        source / "mcscanx_self_circos/mcscanx_circlize_status.tsv",
        "status\tlink_count\tnote\navailable\t94\tok\n",
    )
    touch(source / "plots/mcscanx_circlize.pdf")
    touch(source / "plots/species/A/circos_A.pdf")

    rows = organize(source, tmp_path / "analysis_modules")

    by_module = {row["module"]: row for row in rows}
    assert by_module["11_mcscanx"]["status"] == "available"
    assert (tmp_path / "analysis_modules/11_mcscanx/plots/species/A/circos_A.pdf").exists()


def test_organize_module_results_marks_expression_skipped_optional(tmp_path):
    source = tmp_path / "standard"
    touch(
        source / "tables/expression_status.tsv",
        "status\tnote\nskipped_optional\tRNA-seq expression matrix not provided; expression module skipped\n",
    )

    rows = organize(source, tmp_path / "analysis_modules")

    by_module = {row["module"]: row for row in rows}
    assert by_module["13_expression"]["status"] == "skipped_optional"
    assert by_module["13_expression"]["note"] == "RNA-seq expression matrix not provided; expression module skipped"


def test_organize_module_results_can_append_module_status_to_final_report(tmp_path):
    source = tmp_path / "standard"
    touch(source / "tables/family_candidates.tsv")
    touch(
        source / "jcvi_collinearity/jcvi_dependency_status.tsv",
        "check\tstatus\tdetail\njcvi_python_module\tmissing_dependency\tInstall jcvi\n",
    )
    touch(source / "jcvi_collinearity/jcvi_pair_manifest.tsv")
    final_report = tmp_path / "final_report.md"
    final_report.write_text("# Report\n\nExisting result interpretation.\n", encoding="utf-8")

    organize(source, tmp_path / "analysis_modules", final_report=final_report)

    report_text = (tmp_path / "analysis_modules/report/final_report.md").read_text(encoding="utf-8")
    assert "Existing result interpretation." in report_text
    assert "## Module Execution Status" in report_text
    assert "| 10_synteny_jcvi | JCVI Collinearity And Karyotype | prepared_missing_dependency |" in report_text
