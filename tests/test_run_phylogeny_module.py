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
        "    - -lg\n"
        "  subfamily:\n"
        "    enabled: true\n"
        "    method: auto_topology\n"
        "    min_size: 2\n"
        "    max_groups: 3\n"
        "    r_bin: Rscript\n",
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
    rscript = bin_dir / "Rscript"
    rscript.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "outdir = Path(sys.argv[3])\n"
        "outdir.mkdir(parents=True, exist_ok=True)\n"
        "(outdir / 'tables').mkdir(parents=True, exist_ok=True)\n"
        "(outdir / 'plots').mkdir(parents=True, exist_ok=True)\n"
        "(outdir / 'tables/tree_subfamily_assignments.tsv').write_text('gene_id\\tspecies_id\\tsubfamily\\ttree_label\\nGeneA\\tSpecies_a\\tC1\\tSpecies_a|GeneA\\nGeneB\\tSpecies_b\\tC2\\tSpecies_b|GeneB\\nGeneC\\tSpecies_c\\tC2\\tSpecies_c|GeneC\\n', encoding='utf-8')\n"
        "(outdir / 'tables/tree_subfamily_stats.tsv').write_text('species_id\\tsubfamily\\tcount\\nSpecies_a\\tC1\\t1\\nSpecies_b\\tC2\\t1\\nSpecies_c\\tC2\\t1\\n', encoding='utf-8')\n"
        "(outdir / 'plots/tree_subfamily.pdf').write_bytes(b'%PDF fake tree subfamily')\n"
        "(outdir / 'plots/tree_subfamily.png').write_bytes(b'fake png')\n"
        "(outdir / 'plots/tree_subfamily_species_stats.pdf').write_bytes(b'%PDF fake stats')\n"
        "(outdir / 'plots/tree_subfamily_species_stats.png').write_bytes(b'fake png')\n",
        encoding="utf-8",
    )
    rscript.chmod(0o755)


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
    assert "Subfamily method: `auto_topology`" in summary
    assert "Subfamily assignments:" in summary
    assert "tree_subfamily.pdf" in summary
    assert (outdir / "tables/tree_subfamily_assignments.tsv").exists()
    assert (outdir / "tables/tree_subfamily_stats.tsv").exists()
    assert (outdir / "plots/tree_subfamily.pdf").exists()
    assert (outdir / "plots/tree_subfamily.png").exists()
    assert (outdir / "plots/tree_subfamily_species_stats.pdf").exists()
    assert (outdir / "plots/tree_subfamily_species_stats.png").exists()


def test_plot_tree_subfamilies_r_script_assigns_groups_and_stats(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts/plot_tree_subfamilies.R"
    script_text = script.read_text(encoding="utf-8")
    assert "ggtree::ggtree" in script_text
    assert "geom_strip" in script_text
    assert "geom_tippoint" in script_text
    assert "geom_nodepoint" in script_text
    assert "ggplot2::ggplot" in script_text
    tree = tmp_path / "tree.nwk"
    tree.write_text(
        "((Arabidopsis_thaliana|AT1G14410:0.1,Arabidopsis_thaliana|AT1G71260:0.1)0.9:0.2,"
        "(Oryza_sativa|LOC_Os02g06370:0.1,(Zea_mays|Zm00001:0.1,Zea_mays|Zm00002:0.1)0.8:0.1)0.9:0.2);\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "subfamily"

    completed = subprocess.run(
        [
            "/usr/local/bin/R",
            "--vanilla",
            "--slave",
            "-f",
            str(script),
            "--args",
            str(tree),
            str(outdir),
            "Whirly",
            "2",
            "4",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assignments = read_tsv(outdir / "tables/tree_subfamily_assignments.tsv")
    assert len(assignments) == 5
    assert set(assignments[0]) >= {"gene_id", "species_id", "subfamily", "tree_label"}
    assert {row["subfamily"] for row in assignments} >= {"C1", "C2"}
    stats = read_tsv(outdir / "tables/tree_subfamily_stats.tsv")
    assert any(row["species_id"] == "Zea_mays" and row["count"] == "2" for row in stats)
    assert (outdir / "plots/tree_subfamily.pdf").exists()
    assert (outdir / "plots/tree_subfamily.png").exists()
    assert (outdir / "plots/tree_subfamily_species_stats.pdf").exists()
    assert (outdir / "plots/tree_subfamily_species_stats.png").exists()
