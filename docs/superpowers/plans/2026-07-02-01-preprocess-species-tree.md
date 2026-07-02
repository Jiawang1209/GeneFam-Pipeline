# 01 Preprocess Species Tree Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add species-list and optional species-tree preparation outputs to `01_preprocess`.

**Superseded decision, 2026-07-02:** TimeTree automation was removed. `01_preprocess` now only writes species Latin-name tables and optionally copies a user-provided Newick tree. Missing or disabled species trees are recorded in `species_tree_status.tsv` and must not stop preprocessing or later modules.

**Architecture:** `build_species_clean_bank.py` remains the stable 01 entrypoint. It writes successful species names as Latin names and supports copying a user-provided Newick tree.

**Tech Stack:** Python standard library, pytest.

---

### Task 1: Species Info Outputs

**Files:**
- Modify: `bin/genefam/build_species_clean_bank.py`
- Test: `tests/test_build_species_clean_bank.py`

- [ ] Write a failing test asserting `species_info.txt` contains one Latin name per successful species with underscores replaced by spaces, and `species_info.tsv` contains `species_id` plus `latin_name`.
- [ ] Implement `write_species_info()` and wire it into `main()`.
- [ ] Run `python -m pytest tests/test_build_species_clean_bank.py -q`.

### Task 2: User Tree Mode

**Files:**
- Modify: `bin/genefam/build_species_clean_bank.py`
- Test: `tests/test_build_species_clean_bank.py`

- [ ] Write a failing test for `--species-tree-source user --species-tree-user-tree <file.nwk>`.
- [ ] Copy the user tree to `species_tree/species_tree.nwk` and write `species_tree/species_tree_status.tsv`.
- [ ] Run `python -m pytest tests/test_build_species_clean_bank.py -q`.

### Task 3: Disabled/Missing Tree Mode

**Files:**
- Modify: `bin/genefam/build_species_clean_bank.py`
- Test: `tests/test_build_species_clean_bank.py`

- [ ] Write a failing test that `--species-tree-source none` writes a disabled status and removes stale managed species-tree outputs.
- [ ] Write a failing test that `--species-tree-source user` with a missing tree records `missing_input` and exits successfully.
- [ ] Run 01 tests.

### Task 4: Docs, Whirly, History, Commit

**Files:**
- Modify: `projects/Whirly_2026/project.yaml`
- Modify: `docs/superpowers/specs/2026-06-29-species-clean-bank-design.md`
- Modify: `HISTORY.md`

- [ ] Document YAML shape under `preprocess.species_tree`.
- [ ] Rebuild Whirly 01 and inspect the new files.
- [ ] Record verification in `HISTORY.md`.
- [ ] Commit.
