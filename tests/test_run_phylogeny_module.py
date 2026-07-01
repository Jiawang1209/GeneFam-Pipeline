import csv
import os
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_phylogeny_module.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_project(root: Path) -> Path:
    identify = root / "projects/GDSL_2026/results/04_identification/fasta/identify.ID.fa"
    identify.parent.mkdir(parents=True)
    identify.write_text(
        ">Species_a|GeneA\nMAAA\n"
        ">Species_b|GeneB\nMAAT\n"
        ">Species_c|GeneC\nMATA\n",
        encoding="utf-8",
    )
    config = root / "projects/GDSL_2026/project.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "project:\n"
        "  name: GDSL_2026\n"
        "  outdir: projects/GDSL_2026/results\n"
        "modules:\n"
        "  phylogeny: true\n"
        "phylogeny:\n"
        "  family_name: GDSL\n"
        "  aligner: mafft\n"
        "  aligner_options:\n"
        "    - --auto\n"
        "  tree_builder: fasttree\n"
        "  tree_options:\n"
        "    - -lg\n",
        encoding="utf-8",
    )
    return config


def write_fake_tools(bin_dir: Path) -> None:
    bin_dir.mkdir()
    mafft = bin_dir / "mafft"
    mafft.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "input_path = Path(sys.argv[-1])\n"
        "sys.stderr.write('fake mafft\\n')\n"
        "print(input_path.read_text(encoding='utf-8'), end='')\n",
        encoding="utf-8",
    )
    mafft.chmod(0o755)
    fasttree = bin_dir / "FastTree"
    fasttree.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "out = Path(sys.argv[sys.argv.index('-out') + 1])\n"
        "out.parent.mkdir(parents=True, exist_ok=True)\n"
        "out.write_text('(Species_a|GeneA:0.1,(Species_b|GeneB:0.2,Species_c|GeneC:0.3)0.9:0.4);\\n', encoding='utf-8')\n"
        "sys.stderr.write('fake fasttree\\n')\n",
        encoding="utf-8",
    )
    fasttree.chmod(0o755)


def test_run_phylogeny_module_builds_alignment_tree_and_manifests(tmp_path):
    config = write_project(tmp_path)
    fake_bin = tmp_path / "bin"
    write_fake_tools(fake_bin)
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
    outdir = tmp_path / "projects/GDSL_2026/results/06_phylogeny"
    assert (outdir / "alignment/GDSL.mafft.aln.faa").exists()
    assert (outdir / "phylogeny/GDSL.fasttree.treefile").exists()
    alignment_manifest = read_tsv(outdir / "tables/alignment_manifest.tsv")
    assert alignment_manifest[0]["aligner"] == "mafft"
    assert alignment_manifest[0]["sequence_count"] == "3"
    assert alignment_manifest[0]["raw_alignment"].endswith("alignment/GDSL.mafft.aln.faa")
    phylogeny_manifest = read_tsv(outdir / "tables/phylogeny_manifest.tsv")
    assert phylogeny_manifest[0]["tree_builder"] == "fasttree"
    assert phylogeny_manifest[0]["treefile"].endswith("phylogeny/GDSL.fasttree.treefile")
    commands = read_tsv(outdir / "tables/phylogeny_commands.tsv")
    assert commands[0]["tool"] == "mafft"
    assert commands[1]["tool"] == "fasttree"
    assert "-lg" in commands[1]["command"]
    summary = (outdir / "report/phylogeny_summary.md").read_text(encoding="utf-8")
    assert "Aligner: `mafft`" in summary
    assert "Tree builder: `fasttree`" in summary
