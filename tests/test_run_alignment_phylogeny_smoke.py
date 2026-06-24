import subprocess
import sys


def test_run_alignment_phylogeny_smoke_writes_manifests(tmp_path):
    outdir = tmp_path / "alignment_phylogeny_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_alignment_phylogeny_smoke.py",
            "--family-name",
            "GDSL",
            "--fasta",
            "tests/fixtures/alignment/family_members.faa",
            "--aligner",
            "mafft",
            "--tree-builder",
            "iqtree",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "alignment_manifest" in completed.stdout
    assert "phylogeny_manifest" in completed.stdout

    alignment = (outdir / "tables/alignment_manifest.tsv").read_text(encoding="utf-8")
    assert alignment.startswith("family_name\taligner\tsequence_count\tinput_fasta\traw_alignment\ttrimmed_alignment\n")
    assert "GDSL\tmafft\t3\ttests/fixtures/alignment/family_members.faa" in alignment
    assert "alignment/GDSL.mafft.trimmed.aln.faa" in alignment

    phylogeny = (outdir / "tables/phylogeny_manifest.tsv").read_text(encoding="utf-8")
    assert phylogeny.startswith("family_name\ttree_builder\talignment\ttreefile\tsupport_file\n")
    assert "GDSL\tiqtree" in phylogeny
    assert "phylogeny/GDSL.iqtree.treefile" in phylogeny

    summary = (outdir / "alignment_phylogeny_smoke.md").read_text(encoding="utf-8")
    assert "Sequence count: 3" in summary
    assert "Aligner: mafft" in summary
    assert "Tree builder: iqtree" in summary
