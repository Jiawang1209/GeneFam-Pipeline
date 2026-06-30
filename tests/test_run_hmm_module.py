import csv
import os
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_hmm_module.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_clean_bank(root: Path) -> Path:
    clean_bank = root / "species_clean_bank"
    species_a = clean_bank / "Species_a/clean"
    species_b = clean_bank / "Species_b/clean"
    species_a.mkdir(parents=True)
    species_b.mkdir(parents=True)
    (species_a / "Species_a.protein.clean.fa").write_text(
        ">GeneA\nMAAAA\n>GeneBoth\nMBBBB\n>GeneNone\nMNNN\n",
        encoding="utf-8",
    )
    (species_b / "Species_b.protein.clean.fa").write_text(
        ">GeneB\nMCCCC\n>GeneBoth\nMDDDD\n",
        encoding="utf-8",
    )
    return clean_bank


def write_hmms(root: Path) -> Path:
    hmm_dir = root / "hmms"
    hmm_dir.mkdir(parents=True)
    (hmm_dir / "PF00001.hmm").write_text("HMMER3/f\nNAME PF00001\n//\n", encoding="utf-8")
    (hmm_dir / "PF00002.hmm").write_text("HMMER3/f\nNAME PF00002\n//\n", encoding="utf-8")
    return hmm_dir


def write_fake_hmmsearch(bin_dir: Path) -> None:
    bin_dir.mkdir()
    fake = bin_dir / "hmmsearch"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "domtbl = Path(sys.argv[sys.argv.index('--domtblout') + 1])\n"
        "name_parts = domtbl.name.split('.')\n"
        "species = name_parts[0]\n"
        "hmm = name_parts[1]\n"
        "hits = []\n"
        "if hmm == 'PF00001':\n"
        "    hits.append('GeneA' if species == 'Species_a' else 'GeneBoth')\n"
        "    hits.append('GeneBoth')\n"
        "if hmm == 'PF00002':\n"
        "    hits.append('GeneB' if species == 'Species_b' else 'GeneBoth')\n"
        "    hits.append('GeneBoth')\n"
        "if hmm == 'family_rebuilt':\n"
        "    hits.append('GeneBoth')\n"
        "with domtbl.open('w', encoding='utf-8') as handle:\n"
        "    for gene in sorted(set(hits)):\n"
        "        handle.write(f'{gene} - 100 {hmm} - 50 1e-20 80.0 0 1 1 1e-20 1e-20 80.0 0 1 50 1 50 desc\\n')\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)


def write_fake_rebuild_tools(bin_dir: Path) -> None:
    mafft = bin_dir / "mafft"
    mafft.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "print(Path(sys.argv[-1]).read_text(encoding='utf-8'), end='')\n",
        encoding="utf-8",
    )
    mafft.chmod(0o755)
    hmmbuild = bin_dir / "hmmbuild"
    hmmbuild.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "Path(sys.argv[1]).write_text('HMMER3/f\\nNAME family_rebuilt\\n//\\n', encoding='utf-8')\n"
        "print('hmmbuild ok')\n",
        encoding="utf-8",
    )
    hmmbuild.chmod(0o755)


def test_run_hmm_module_scans_hmm_dir_and_combines_any_hits(tmp_path):
    clean_bank = write_clean_bank(tmp_path)
    hmm_dir = write_hmms(tmp_path)
    fake_bin = tmp_path / "bin"
    write_fake_hmmsearch(fake_bin)
    outdir = tmp_path / "02_hmm"
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--clean-bank",
            str(clean_bank),
            "--hmm-dir",
            str(hmm_dir),
            "--outdir",
            str(outdir),
            "--combine-rule",
            "any",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    candidates = read_tsv(outdir / "tables/hmm_candidates.tsv")
    assert [row["gene_id"] for row in candidates] == ["GeneA", "GeneBoth", "GeneB", "GeneBoth"]
    by_species_gene = {(row["species_id"], row["gene_id"]): row for row in candidates}
    assert by_species_gene[("Species_a", "GeneA")]["matched_hmm_count"] == "1"
    assert by_species_gene[("Species_a", "GeneBoth")]["matched_hmm_count"] == "2"
    assert (outdir / "fasta/hmm_candidates.pep.fa").read_text(encoding="utf-8").startswith(">Species_a|GeneA\n")
    assert read_tsv(outdir / "inputs/hmm_profiles.tsv") == [
        {"hmm_id": "PF00001", "hmm_profile": str(hmm_dir / "PF00001.hmm")},
        {"hmm_id": "PF00002", "hmm_profile": str(hmm_dir / "PF00002.hmm")},
    ]


def test_run_hmm_module_combines_all_hits(tmp_path):
    clean_bank = write_clean_bank(tmp_path)
    hmm_dir = write_hmms(tmp_path)
    fake_bin = tmp_path / "bin"
    write_fake_hmmsearch(fake_bin)
    outdir = tmp_path / "02_hmm"
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--clean-bank",
            str(clean_bank),
            "--hmm-dir",
            str(hmm_dir),
            "--outdir",
            str(outdir),
            "--combine-rule",
            "all",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    candidates = read_tsv(outdir / "tables/hmm_candidates.tsv")
    assert [(row["species_id"], row["gene_id"]) for row in candidates] == [
        ("Species_a", "GeneBoth"),
        ("Species_b", "GeneBoth"),
    ]


def test_run_hmm_module_reports_missing_hmmsearch(tmp_path):
    clean_bank = write_clean_bank(tmp_path)
    hmm_dir = write_hmms(tmp_path)
    outdir = tmp_path / "02_hmm"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--clean-bank",
            str(clean_bank),
            "--hmm-dir",
            str(hmm_dir),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": str(tmp_path / "empty_bin")},
    )

    assert completed.returncode != 0
    assert "Required command not found: hmmsearch" in completed.stderr


def test_run_hmm_module_rebuild_hmm_runs_two_pass_mode(tmp_path):
    clean_bank = write_clean_bank(tmp_path)
    hmm_dir = write_hmms(tmp_path)
    fake_bin = tmp_path / "bin"
    write_fake_hmmsearch(fake_bin)
    write_fake_rebuild_tools(fake_bin)
    outdir = tmp_path / "02_hmm"
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--clean-bank",
            str(clean_bank),
            "--hmm-dir",
            str(hmm_dir),
            "--outdir",
            str(outdir),
            "--rebuild-hmm",
            "--family-name",
            "family",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    assert (outdir / "rebuilt_hmm/first_pass_hits.pep.fa").exists()
    assert (outdir / "rebuilt_hmm/first_pass_hits.aln.fa").exists()
    assert (outdir / "rebuilt_hmm/family.rebuilt.hmm").exists()
    assert (outdir / "rebuilt_hmm/hmmbuild.log").exists()
    candidates = read_tsv(outdir / "tables/hmm_candidates.tsv")
    assert [(row["species_id"], row["gene_id"]) for row in candidates] == [
        ("Species_a", "GeneBoth"),
        ("Species_b", "GeneBoth"),
    ]


def test_run_hmm_module_reads_project_yaml(tmp_path):
    clean_bank = write_clean_bank(tmp_path)
    hmm_dir = write_hmms(tmp_path)
    fake_bin = tmp_path / "bin"
    write_fake_hmmsearch(fake_bin)
    project = tmp_path / "projects/GDSL_2026"
    project.mkdir(parents=True)
    outdir = project / "results/02_hmm"
    config = project / "project.yaml"
    config.write_text(
        "project:\n"
        "  name: GDSL_2026\n"
        f"  outdir: {project / 'results'}\n"
        "database:\n"
        f"  species_clean_bank: {clean_bank}\n"
        "hmm:\n"
        f"  hmm_dir: {hmm_dir}\n"
        "  combine_rule: all\n"
        "  evalue: 1.0e-10\n"
        "  min_bitscore: 0.0\n"
        "  min_domain_coverage: 0.0\n"
        "  rebuild_hmm: false\n"
        "  family_name: GDSL\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--config",
            str(config),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    candidates = read_tsv(outdir / "tables/hmm_candidates.tsv")
    assert [(row["species_id"], row["gene_id"]) for row in candidates] == [
        ("Species_a", "GeneBoth"),
        ("Species_b", "GeneBoth"),
    ]


def test_run_hmm_module_project_yaml_accepts_repo_relative_paths(tmp_path):
    clean_bank = write_clean_bank(tmp_path / "projects/GDSL_2026/results/01_preprocess")
    hmm_dir = write_hmms(tmp_path / "projects/GDSL_2026/config")
    fake_bin = tmp_path / "bin"
    write_fake_hmmsearch(fake_bin)
    project = tmp_path / "projects/GDSL_2026"
    config = project / "project.yaml"
    config.write_text(
        "project:\n"
        "  name: GDSL_2026\n"
        "  root: projects/GDSL_2026\n"
        "  outdir: projects/GDSL_2026/results\n"
        "database:\n"
        "  species_clean_bank: projects/GDSL_2026/results/01_preprocess/species_clean_bank\n"
        "hmm:\n"
        "  hmm_dir: projects/GDSL_2026/config/hmms\n"
        "  combine_rule: any\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--config",
            str(config),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "projects/GDSL_2026/results/02_hmm/tables/hmm_candidates.tsv").exists()
