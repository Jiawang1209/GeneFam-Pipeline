import subprocess
import sys


def test_build_reproducibility_code_md_collects_analysis_commands(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("project:\n  name: My_3species_GDSL\n", encoding="utf-8")
    clean_manifest = tmp_path / "species_manifest.clean.tsv"
    clean_manifest.write_text("species_id\tpep\tgff3\tcds\tgenome\nArabidopsis_thaliana\tath.clean.fa\tath.gff3\tath.cds.clean.fa\t\n", encoding="utf-8")
    reference_manifest = tmp_path / "reference_generation.tsv"
    reference_manifest.write_text(
        "hmm_id\treference_peptides\tids\tmissing_ids\n"
        "PF00657\tresults/00_preprocess/reference/PF00657.reference.pep.fa\tresults/00_preprocess/reference/PF00657.TAIR.ID\tresults/00_preprocess/reference/PF00657.missing_ids.txt\n",
        encoding="utf-8",
    )
    family_candidates = tmp_path / "family_candidates.tsv"
    family_candidates.write_text("species_id\tgene_id\nArabidopsis_thaliana\tAT1G06990\n", encoding="utf-8")
    out = tmp_path / "reproducibility_code.md"

    subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_reproducibility_code.py",
            "--config",
            str(config),
            "--clean-species-manifest",
            str(clean_manifest),
            "--reference-manifest",
            str(reference_manifest),
            "--family-candidates",
            str(family_candidates),
            "--config-label",
            "configs/real_3species.template.yaml",
            "--groups-label",
            "configs/species_groups.yaml",
            "--outdir",
            "results/real_3species_full_standard",
            "--preprocess-outdir",
            "results/00_preprocess",
            "--clean-species-manifest-label",
            "results/00_preprocess/species_manifest.clean.tsv",
            "--reference-manifest-label",
            "results/00_preprocess/reference/reference_generation.tsv",
            "--family-candidates-label",
            "results/real_3species_full_standard/tables/family_candidates.tsv",
            "--out",
            str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = out.read_text(encoding="utf-8")
    assert "# Analysis Reproducibility Code" in text
    assert "python bin/genefam/preprocess_species.py" in text
    assert "python bin/genefam/build_reference_from_config.py" in text
    assert "nextflow run workflows/main.nf" in text
    assert "--config configs/real_3species.template.yaml" in text
    assert "--outdir results/real_3species_full_standard" in text
    assert "--preprocess_outdir results/00_preprocess" in text
    assert "results/00_preprocess/reference/PF00657.reference.pep.fa" in text
    assert "results/real_3species_full_standard/tables/family_candidates.tsv" in text
    assert "## Reference-Level Module Commands And Handoffs" in text
    assert "### MEME motif analysis" in text
    assert "RUN_MEME_MOTIFS" in text
    assert "### JCVI inter-species collinearity" in text
    assert "prepare_jcvi_collinearity.py" in text
    assert "run_jcvi_collinearity.py" in text
    assert "### MCScanX self intra-species duplication and circlize" in text
    assert "build_mcscanx_self_inputs.py" in text
    assert "run_mcscanx_self.py" in text
    assert "### JCVI/MCScanX KaKs and WGD layers" in text
    assert "prepare_reference_kaks_inputs.py" in text
    assert "run_reference_kaks_calculator.py" in text
    assert "kaks_failure_summary.tsv" in text
    assert "### Promoter and PlantCARE handoff" in text
    assert "split_promoter_fasta_for_plantcare.py" in text
    assert "plantcare_submission/plantcare_submission_manifest.tsv" in text
    assert "promoter.cis_elements" in text
    assert "### AraNet PPI transfer and ggNetView" in text
    assert "build_aranet_ppi_from_reciprocal_blast.py" in text
    assert "PLOT_PPI_GGNETVIEW" in text
    assert "### Final report and module package" in text
    assert "organize_module_results.py" in text
    assert str(family_candidates) not in text
