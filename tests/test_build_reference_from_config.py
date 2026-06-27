import csv
import subprocess
import sys


def test_build_reference_from_config_uses_first_hmm_id_and_clean_reference_species_pep(tmp_path):
    domains = tmp_path / "all.domains.txt"
    domains.write_text(
        "AT1G06990.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n",
        encoding="utf-8",
    )
    ref_pep = tmp_path / "Arabidopsis_thaliana.pep.clean.fa"
    ref_pep.write_text(">AT1G06990\nMAAA\n", encoding="utf-8")
    clean_manifest = tmp_path / "species_manifest.clean.tsv"
    clean_manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        f"Arabidopsis_thaliana\t{ref_pep}\tath.gff3\tath.cds.clean.fa\t\n"
        "Brassica_rapa\tbra.pep.clean.fa\tbra.gff3\tbra.cds.clean.fa\t\n",
        encoding="utf-8",
    )
    config = tmp_path / "config.yaml"
    config.write_text(
        "gene_family:\n"
        "  hmm_profiles:\n"
        "    - id: PF00657\n"
        "      path: data/hmm_profiles/PF00657.hmm\n"
        "reference_generation:\n"
        "  enabled: true\n"
        "  source: tair_all_domains\n"
        f"  domain_annotation: {domains}\n"
        "  reference_species: Arabidopsis_thaliana\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "00_preprocess" / "reference"

    subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_reference_from_config.py",
            "--config",
            str(config),
            "--species-manifest",
            str(clean_manifest),
            "--outdir",
            str(outdir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (outdir / "PF00657.reference.pep.fa").read_text(encoding="utf-8") == ">AT1G06990\nMAAA\n"
    assert (outdir / "PF00657.TAIR.ID").read_text(encoding="utf-8") == "AT1G06990\n"
    manifest_path = outdir / "reference_generation.tsv"
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert rows == [
        {
            "hmm_id": "PF00657",
            "reference_peptides": str(outdir / "PF00657.reference.pep.fa"),
            "ids": str(outdir / "PF00657.TAIR.ID"),
            "missing_ids": str(outdir / "PF00657.missing_ids.txt"),
        }
    ]
