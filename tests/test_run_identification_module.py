import csv
import os
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_identification_module.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_clean_bank(root: Path) -> Path:
    clean_bank = root / "species_clean_bank"
    for species, records in {
        "Arabidopsis_thaliana": [("AT1G00010", "MAAA"), ("AT1G00020", "MBBB")],
        "Brassica_rapa": [("BraA01g000010", "MCCC")],
    }.items():
        clean = clean_bank / species / "clean"
        clean.mkdir(parents=True, exist_ok=True)
        clean.joinpath(f"{species}.protein.clean.fa").write_text(
            "".join(f">{record_id}\n{seq}\n" for record_id, seq in records),
            encoding="utf-8",
        )
    return clean_bank


def write_module_inputs(root: Path) -> tuple[Path, Path, Path]:
    outdir = root / "projects/GDSL_2026/results"
    hmm = outdir / "02_hmm/tables/hmm_candidates.tsv"
    blastp = outdir / "03_blastp/tables/blastp_candidates.tsv"
    hmm.parent.mkdir(parents=True, exist_ok=True)
    blastp.parent.mkdir(parents=True, exist_ok=True)
    hmm.write_text(
        "species_id\tgene_id\tbest_evalue\tbest_bitscore\n"
        "Arabidopsis_thaliana\tAT1G00010\t1e-40\t200\n"
        "Arabidopsis_thaliana\tAT1G00020\t1e-30\t180\n",
        encoding="utf-8",
    )
    blastp.write_text(
        "species_id\tgene_id\tbest_subject_id\tbest_evalue\tbest_bitscore\n"
        "Arabidopsis_thaliana\tAT1G00010\tOryza_sativa|LOC_Os01g00010\t1e-50\t240\n"
        "Brassica_rapa\tBraA01g000010\tArabidopsis_thaliana|AT1G00010\t1e-20\t120\n",
        encoding="utf-8",
    )
    hmm_dir = root / "projects/GDSL_2026/config/hmm_profiles"
    hmm_dir.mkdir(parents=True, exist_ok=True)
    hmm_profile = hmm_dir / "PF00657.hmm"
    hmm_profile.write_text("HMMER3/f\nNAME PF00657\n//\n", encoding="utf-8")
    return outdir, hmm_profile, hmm_dir


def write_project(root: Path, clean_bank: Path, hmm_dir: Path) -> Path:
    project = root / "projects/GDSL_2026/project.yaml"
    project.parent.mkdir(parents=True, exist_ok=True)
    project.write_text(
        "project:\n"
        "  outdir: projects/GDSL_2026/results\n"
        "database:\n"
        f"  species_clean_bank: {clean_bank}\n"
        "hmm:\n"
        f"  hmm_dir: {hmm_dir}\n"
        "identification:\n"
        "  final_rule: intersection\n"
        "  domain_terms:\n"
        "    - PF00657\n"
        "  domain_evalue: 1.0e-5\n",
        encoding="utf-8",
    )
    return project


def write_fake_hmmsearch(bin_dir: Path) -> None:
    bin_dir.mkdir(exist_ok=True)
    fake = bin_dir / "hmmsearch"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "domtbl = Path(sys.argv[sys.argv.index('--domtblout') + 1])\n"
        "domtbl.parent.mkdir(parents=True, exist_ok=True)\n"
        "domtbl.write_text('# domtblout\\nArabidopsis_thaliana|AT1G00010 - 4 PF00657 - 100 1e-40 200.0 0.0 1 1 1e-40 1e-40 200.0 0.0 1 4 1 4 1 4 0.99 hit\\n', encoding='utf-8')\n"
        "out = Path(sys.argv[-1])\n"
        "print(f'searched {out}')\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)


def write_fake_pfam_scan(bin_dir: Path) -> None:
    bin_dir.mkdir(exist_ok=True)
    fake = bin_dir / "pfam_scan.pl"
    fake.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "out = Path(sys.argv[sys.argv.index('-out') + 1])\n"
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "out.write_text('Arabidopsis_thaliana|AT1G00010 1 4 PF00657.24 GDSL 1e-40\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)


def test_run_identification_module_uses_hmm_blastp_intersection_and_domain_confirmation(tmp_path):
    clean_bank = write_clean_bank(tmp_path / "projects/GDSL_2026/results/01_preprocess")
    _outdir, _hmm_profile, hmm_dir = write_module_inputs(tmp_path)
    config = write_project(tmp_path, clean_bank, hmm_dir)
    fake_bin = tmp_path / "bin"
    write_fake_hmmsearch(fake_bin)
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
    outdir = tmp_path / "projects/GDSL_2026/results/04_identification"
    candidates = read_tsv(outdir / "tables/family_candidates.tsv")
    assert [(row["species_id"], row["gene_id"], row["evidence_sources"]) for row in candidates] == [
        ("Arabidopsis_thaliana", "AT1G00010", "blastp,hmm")
    ]
    assert (outdir / "tables/inter.ID").read_text(encoding="utf-8") == "AT1G00010\n"
    assert (outdir / "tables/domain_confirmed.id").read_text(encoding="utf-8") == "AT1G00010\n"
    assert (outdir / "fasta/inter.ID.fa").read_text(encoding="utf-8") == ">Arabidopsis_thaliana|AT1G00010\nMAAA\n"
    assert (outdir / "fasta/identify.ID.fa").read_text(encoding="utf-8") == ">Arabidopsis_thaliana|AT1G00010\nMAAA\n"
    summary = read_tsv(outdir / "report/identification_summary.tsv")
    assert summary[0]["hmm_candidate_count"] == "2"
    assert summary[0]["blastp_candidate_count"] == "2"
    assert summary[0]["intersection_count"] == "1"
    assert summary[0]["domain_confirmed_count"] == "1"


def test_run_identification_module_can_use_union_rule(tmp_path):
    clean_bank = write_clean_bank(tmp_path / "projects/GDSL_2026/results/01_preprocess")
    _outdir, _hmm_profile, hmm_dir = write_module_inputs(tmp_path)
    config = write_project(tmp_path, clean_bank, hmm_dir)
    fake_bin = tmp_path / "bin"
    write_fake_hmmsearch(fake_bin)
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config), "--final-rule", "union"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/GDSL_2026/results/04_identification"
    candidates = read_tsv(outdir / "tables/family_candidates.tsv")
    assert [(row["species_id"], row["gene_id"], row["evidence_sources"]) for row in candidates] == [
        ("Arabidopsis_thaliana", "AT1G00010", "blastp,hmm"),
        ("Arabidopsis_thaliana", "AT1G00020", "hmm"),
        ("Brassica_rapa", "BraA01g000010", "blastp"),
    ]
    summary = read_tsv(outdir / "report/identification_summary.tsv")
    assert summary[0]["final_rule"] == "union"
    assert summary[0]["selected_candidate_count"] == "3"


def test_run_identification_module_can_confirm_domains_with_pfam_scan(tmp_path):
    clean_bank = write_clean_bank(tmp_path / "projects/GDSL_2026/results/01_preprocess")
    _outdir, _hmm_profile, hmm_dir = write_module_inputs(tmp_path)
    config = write_project(tmp_path, clean_bank, hmm_dir)
    fake_bin = tmp_path / "bin"
    write_fake_pfam_scan(fake_bin)
    pfam_dir = tmp_path / "Pfam"
    pfam_dir.mkdir()
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--config",
            str(config),
            "--domain-method",
            "pfam_scan",
            "--pfam-scan-dir",
            str(pfam_dir),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/GDSL_2026/results/04_identification"
    assert (outdir / "domain_confirmation/Pfam_scan.out").exists()
    assert (outdir / "tables/domain_confirmed.id").read_text(encoding="utf-8") == "AT1G00010\n"
    assert (outdir / "fasta/identify.ID.fa").read_text(encoding="utf-8") == ">Arabidopsis_thaliana|AT1G00010\nMAAA\n"
    summary = read_tsv(outdir / "report/identification_summary.tsv")
    assert summary[0]["domain_method"] == "pfam_scan"
