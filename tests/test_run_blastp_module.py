import csv
import os
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_blastp_module.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_clean_bank(root: Path) -> Path:
    clean_bank = root / "species_clean_bank"
    for species, records in {
        "Arabidopsis_thaliana": [("AT1G00010", "MAAA"), ("AT1G00020", "MBBB")],
        "Oryza_sativa": [("LOC_Os01g00010", "MCCC"), ("LOC_Os01g00020", "MDDD")],
        "Brassica_rapa": [("BraA01g000010", "MEEE"), ("BraA01g000020", "MFFF")],
    }.items():
        clean = clean_bank / species / "clean"
        clean.mkdir(parents=True, exist_ok=True)
        clean.joinpath(f"{species}.protein.clean.fa").write_text(
            "".join(f">{record_id}\n{seq}\n" for record_id, seq in records),
            encoding="utf-8",
        )
    return clean_bank


def write_reference_sources(root: Path) -> Path:
    ann = root / "configs/03_blastp/domain_annotations"
    ann.mkdir(parents=True)
    ath = ann / "Arabidopsis_thaliana.all.domains.txt"
    ath.write_text(
        "AT1G00010.1\t.\tPfam\tPF00657\tLipase_GDSL\t1\t50\n"
        "AT1G99999.1\t.\tPfam\tPF00657\tLipase_GDSL\t1\t50\n",
        encoding="utf-8",
    )
    osa = ann / "Oryza_sativa.all.domains.txt"
    osa.write_text(
        "model\thmm_acc\thmm_name\n"
        "LOC_Os01g00010.1\tPF00657.20\tLipase_GDSL\n"
        "LOC_Os01g99999.1\tPF00657.20\tLipase_GDSL\n",
        encoding="utf-8",
    )
    sources = root / "configs/03_blastp/reference_sources.tsv"
    sources.write_text(
        "species_id\tdomain_annotation\n"
        f"Arabidopsis_thaliana\t{ath}\n"
        f"Oryza_sativa\t{osa}\n",
        encoding="utf-8",
    )
    return sources


def write_project(root: Path, clean_bank: Path, sources: Path) -> Path:
    project = root / "projects/GDSL_2026"
    project.mkdir(parents=True, exist_ok=True)
    config = project / "project.yaml"
    config.write_text(
        "project:\n"
        "  name: GDSL_2026\n"
        "  outdir: projects/GDSL_2026/results\n"
        "database:\n"
        f"  species_clean_bank: {clean_bank}\n"
        "blastp:\n"
        "  domain_terms:\n"
        "    - PF00657\n"
        f"  reference_sources: {sources}\n"
        "  evalue: 1.0e-10\n"
        "  num_threads: 2\n"
        "  num_alignments: 5\n",
        encoding="utf-8",
    )
    return config


def write_fake_blast_tools(bin_dir: Path) -> None:
    bin_dir.mkdir()
    makeblastdb = bin_dir / "makeblastdb"
    makeblastdb.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "db = Path(sys.argv[sys.argv.index('-out') + 1])\n"
        "db.parent.mkdir(parents=True, exist_ok=True)\n"
        "db.with_suffix('.pin').write_text('db ok\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    makeblastdb.chmod(0o755)
    blastp = bin_dir / "blastp"
    blastp.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "out = Path(sys.argv[sys.argv.index('-out') + 1])\n"
        "query = Path(sys.argv[sys.argv.index('-query') + 1])\n"
        "species = query.parent.parent.name\n"
        "hits = []\n"
        "if species == 'Brassica_rapa':\n"
        "    hits.append('BraA01g000010\\tArabidopsis_thaliana|AT1G00010\\t80\\t100\\t0\\t0\\t1\\t100\\t1\\t100\\t1e-40\\t220')\n"
        "else:\n"
        "    hits.append(f'{species}_self\\tArabidopsis_thaliana|AT1G00010\\t90\\t100\\t0\\t0\\t1\\t100\\t1\\t100\\t1e-20\\t150')\n"
        "out.write_text('\\n'.join(hits) + '\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    blastp.chmod(0o755)


def test_run_blastp_module_builds_reference_and_candidates_from_project_yaml(tmp_path):
    clean_bank = write_clean_bank(tmp_path / "projects/GDSL_2026/results/01_preprocess")
    sources = write_reference_sources(tmp_path)
    config = write_project(tmp_path, clean_bank, sources)
    fake_bin = tmp_path / "bin"
    write_fake_blast_tools(fake_bin)
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/GDSL_2026/results/03_blastp"
    references = read_tsv(outdir / "reference/reference_manifest.tsv")
    assert [(row["species_id"], row["reference_count"], row["missing_count"]) for row in references] == [
        ("Arabidopsis_thaliana", "1", "1"),
        ("Oryza_sativa", "1", "1"),
    ]
    seeds = read_tsv(outdir / "seed/seed_manifest.tsv")
    assert [(row["species_id"], row["seed_count"], row["missing_count"]) for row in seeds] == [
        ("Arabidopsis_thaliana", "1", "1"),
        ("Oryza_sativa", "1", "1"),
    ]
    assert (outdir / "seed/combined_seed.pep.fa").read_text(encoding="utf-8") == (
        ">Arabidopsis_thaliana|AT1G00010\nMAAA\n>Oryza_sativa|LOC_Os01g00010\nMCCC\n"
    )
    assert (outdir / "reference/blastp_reference.pep.fa").read_text(encoding="utf-8") == (
        ">Arabidopsis_thaliana|AT1G00010\nMAAA\n>Oryza_sativa|LOC_Os01g00010\nMCCC\n"
    )
    candidates = read_tsv(outdir / "tables/blastp_candidates.tsv")
    by_species_gene = {(row["species_id"], row["gene_id"]): row for row in candidates}
    assert by_species_gene[("Brassica_rapa", "BraA01g000010")]["best_subject_id"] == "Arabidopsis_thaliana|AT1G00010"
