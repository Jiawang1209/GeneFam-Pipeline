# 01 Preprocess Species Tree Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add species-list and optional species-tree preparation outputs to `01_preprocess`.

**Architecture:** `build_species_clean_bank.py` remains the stable 01 entrypoint. It writes successful species names as Latin names, supports copying a user-provided Newick tree, and can optionally call a separate TimeTree automation helper that writes status instead of failing the clean bank.

**Tech Stack:** Python standard library, optional Playwright for TimeTree browser automation, pytest.

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

### Task 3: TimeTree Optional Helper

**Files:**
- Create: `bin/genefam/fetch_timetree_species_tree.py`
- Modify: `bin/genefam/build_species_clean_bank.py`
- Test: `tests/test_build_species_clean_bank.py`

- [ ] Write a failing test that `--species-tree-source timetree` writes `species_tree/timetree_species_input.txt` and a status row without failing 01 if automation is unavailable.
- [ ] Add the helper script with optional Playwright import and clear status output.
- [ ] Wire the helper through `subprocess.run(..., check=False)`.
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
