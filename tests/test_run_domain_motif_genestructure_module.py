import csv
import os
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_domain_motif_genestructure_module.py"
PLOT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts/plot_domain_motif_genestructure.R"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_fake_project(root: Path) -> Path:
    project = root / "projects/Whirly_2026"
    results = project / "results"
    (results / "04_identification/fasta").mkdir(parents=True)
    (results / "04_identification/tables").mkdir(parents=True)
    (results / "06_phylogeny/phylogeny").mkdir(parents=True)
    (results / "06_phylogeny/tables").mkdir(parents=True)
    (results / "02_hmm/tables").mkdir(parents=True)
    clean = results / "01_preprocess/species_clean_bank/Species_a/clean"
    clean.mkdir(parents=True)

    (results / "04_identification/fasta/identify.ID.fa").write_text(
        ">Species_a|GeneA\nMKKLLVVAA\n>Species_a|GeneB\nMKKLLVVTT\n",
        encoding="utf-8",
    )
    (results / "04_identification/tables/family_candidates.tsv").write_text(
        "species_id\tgene_id\tevidence_sources\n"
        "Species_a\tGeneA\thmm\n"
        "Species_a\tGeneB\thmm\n",
        encoding="utf-8",
    )
    (results / "06_phylogeny/phylogeny/Whirly.fasttree.treefile").write_text("(GeneA:0.1,GeneB:0.2)0.9;\n", encoding="utf-8")
    (results / "06_phylogeny/tables/phylogeny_manifest.tsv").write_text(
        "family_name\ttree_builder\talignment\ttreefile\tsupport_file\n"
        f"Whirly\tfasttree\taln.fa\t{results / '06_phylogeny/phylogeny/Whirly.fasttree.treefile'}\t\n",
        encoding="utf-8",
    )
    (results / "06_phylogeny/tables/phylogeny_label_map.tsv").write_text(
        "original_id\ttree_label\tgene_id\tspecies_id\n"
        "Species_a|GeneA\tGeneA\tGeneA\tSpecies_a\n"
        "Species_a|GeneB\tGeneB\tGeneB\tSpecies_a\n",
        encoding="utf-8",
    )
    (results / "02_hmm/tables/hmm_hits.filtered.tsv").write_text(
        "species_id\tgene_id\thmm_id\thmm_length\thmm_from\thmm_to\tali_from\tali_to\tdomain_coverage\tevalue\tbitscore\n"
        "Species_a\tGeneA\tPF00001\t100\t5\t50\t2\t47\t0.46\t1e-20\t88\n"
        "Species_a\tGeneB\tPF00001\t100\t6\t52\t3\t49\t0.47\t1e-18\t80\n",
        encoding="utf-8",
    )
    (clean / "Species_a.gff3").write_text(
        "chr1\ttest\tgene\t100\t500\t.\t+\t.\tID=GeneA;Name=GeneA\n"
        "chr1\ttest\tmRNA\t100\t500\t.\t+\t.\tID=GeneA.t1;Name=GeneA.1;Parent=GeneA\n"
        "chr1\ttest\tfive_prime_UTR\t100\t119\t.\t+\t.\tID=utr.GeneA.1;Parent=GeneA.t1\n"
        "chr1\ttest\tCDS\t120\t180\t.\t+\t0\tID=cds.GeneA.1;Parent=GeneA.t1\n"
        "chr1\ttest\tCDS\t250\t320\t.\t+\t0\tID=cds.GeneA.2;Parent=GeneA.t1\n"
        "chr1\ttest\tthree_prime_UTR\t321\t500\t.\t+\t.\tID=utr.GeneA.2;Parent=GeneA.t1\n"
        "chr1\ttest\tgene\t700\t1000\t.\t-\t.\tID=GeneB;Name=GeneB\n"
        "chr1\ttest\tmRNA\t700\t1000\t.\t-\t.\tID=GeneB.t1;Name=GeneB.1;Parent=GeneB\n"
        "chr1\ttest\tCDS\t900\t960\t.\t-\t0\tID=cds.GeneB.1;Parent=GeneB.t1\n",
        encoding="utf-8",
    )
    config = project / "project.yaml"
    config.write_text(
        "project:\n"
        "  name: Whirly_2026\n"
        "  outdir: projects/Whirly_2026/results\n"
        "database:\n"
        "  species_clean_bank: projects/Whirly_2026/results/01_preprocess/species_clean_bank\n"
        "modules:\n"
        "  domain_motif_genestructure: true\n"
        "domain_motif_genestructure:\n"
        "  family_name: Whirly\n"
        "  meme_executable: meme\n"
        "  r_bin: Rscript\n"
        "  nmotifs: 2\n"
        "  minw: 4\n"
        "  maxw: 12\n",
        encoding="utf-8",
    )
    return config


def write_fake_tools(bin_dir: Path) -> None:
    bin_dir.mkdir()
    meme = bin_dir / "meme"
    meme.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "out = Path(sys.argv[sys.argv.index('-oc') + 1])\n"
        "out.mkdir(parents=True, exist_ok=True)\n"
        "(out / 'meme.txt').write_text('MEME version 5\\nMotif A MEME-1 Description\\nGeneA 2 1e-5 AAAA\\nGeneB 3 2e-5 CCCC\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    meme.chmod(0o755)
    rscript = bin_dir / "Rscript"
    rscript.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "from pathlib import Path\n"
        "outdir = Path(sys.argv[7])\n"
        "(outdir / 'plots').mkdir(parents=True, exist_ok=True)\n"
        "(outdir / 'plots/tree_domain_motif_genestructure.pdf').write_bytes(b'%PDF fake')\n"
        "(outdir / 'plots/tree_domain_motif_genestructure.png').write_bytes(b'fake png')\n"
        "(outdir / 'plots/tree_domain_motif_genestructure_full_length.pdf').write_bytes(b'%PDF fake full')\n"
        "(outdir / 'plots/tree_domain_motif_genestructure_full_length.png').write_bytes(b'fake png full')\n",
        encoding="utf-8",
    )
    rscript.chmod(0o755)


def test_run_domain_motif_genestructure_module_builds_tables_and_plot(tmp_path):
    config = write_fake_project(tmp_path)
    fake_bin = tmp_path / "bin"
    write_fake_tools(fake_bin)
    env = {**os.environ, "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}"}

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config)],
        cwd=tmp_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/Whirly_2026/results/07_domain_motif_genestructure"
    assert (outdir / "inputs/identify.ID.clean.fa").exists()
    assert (outdir / "meme/meme.txt").exists()
    assert (outdir / "tables/motif_locations.tsv").exists()
    assert (outdir / "tables/domain_locations.tsv").exists()
    assert (outdir / "tables/gene_structure_tracks.tsv").exists()
    assert (outdir / "tables/sequence_lengths.tsv").exists()
    assert (outdir / "plots/tree_domain_motif_genestructure.pdf").exists()
    assert (outdir / "plots/tree_domain_motif_genestructure.png").exists()
    assert (outdir / "plots/tree_domain_motif_genestructure_full_length.pdf").exists()
    assert (outdir / "plots/tree_domain_motif_genestructure_full_length.png").exists()
    assert (outdir / "report/domain_motif_genestructure_summary.md").exists()

    motifs = read_tsv(outdir / "tables/motif_locations.tsv")
    assert motifs[0]["gene_id"] == "GeneA"
    assert motifs[0]["motif_id"] == "MEME-1"
    assert motifs[0]["start"] == "2"
    assert motifs[0]["end"] == "5"
    domains = read_tsv(outdir / "tables/domain_locations.tsv")
    assert domains[0]["domain_id"] == "PF00001"
    assert domains[0]["start"] == "2"
    structures = read_tsv(outdir / "tables/gene_structure_tracks.tsv")
    assert {row["gene_id"] for row in structures} == {"GeneA", "GeneB"}
    assert {"gene", "CDS", "five_prime_UTR", "three_prime_UTR"} <= {row["feature"] for row in structures}
    lengths = read_tsv(outdir / "tables/sequence_lengths.tsv")
    assert lengths[0]["protein_length"] == "9"
    commands = read_tsv(outdir / "tables/domain_motif_genestructure_commands.tsv")
    assert commands[0]["tool"] == "meme"
    assert commands[1]["tool"] == "Rscript"
    summary = (outdir / "report/domain_motif_genestructure_summary.md").read_text(encoding="utf-8")
    assert "Motif locations:" in summary
    assert "Domain locations:" in summary
    assert "Gene structure tracks:" in summary
    assert "tree_domain_motif_genestructure.pdf" in summary
    assert "tree_domain_motif_genestructure_full_length.pdf" in summary


def test_plot_domain_motif_genestructure_r_reuses_reference_style():
    script_text = PLOT_SCRIPT.read_text(encoding="utf-8")
    assert "ggtree::ggtree" in script_text
    assert "gggenes::geom_gene_arrow" in script_text
    assert "geom_segment" in script_text
    assert "geom_rect" in script_text
    assert "five_prime_UTR" in script_text
    assert "three_prime_UTR" in script_text
    assert "tree_domain_motif_genestructure_full_length.pdf" in script_text
    assert "aplot::insert_right" in script_text
    assert "Motif Analysis" in script_text
    assert "Domain Analysis" in script_text
    assert "Gene Structure" in script_text
