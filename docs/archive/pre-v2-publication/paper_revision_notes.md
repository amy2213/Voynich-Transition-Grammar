# Paper Revision Notes

Historical record of revisions applied to the paper. The revised paper is
`voynich_paper_v2.pdf` / `arxiv_submission_v2.zip`. The stale pre-revision
PDF at `docs/paper.pdf` should be replaced with the v2 PDF.

---

## Implemented in v2

All items below have been applied to `main.tex` in the arXiv v2 bundle.

### Retractions

- **§3.10 (was §3.9): Productive morphological paradigms — interpretation retracted.**
  Log-frequency vs edit-1 variant-count correlation does not exceed a character-trigram
  null for any family. Chaucer at same measurement produces r=0.20. Section retitled
  "Edit-distance graph structure and paradigm-null retraction." Null-model table added.
  MVE checklist reduced from 8 to 7 items.

- **§5: "Only compatible class" conclusion — withdrawn.**
  First-pass constructed-system control satisfies 5 of 7 items by design. Replaced with
  narrower claim: "among tested classes, encoded structured language is the only candidate
  compatible with all seven items; sophisticated constructed systems cannot be excluded."
  New constructed-control section (§3.11) and empirical MVE table added.

### Corrections

- **Table 4 caption: "all significant z=3.4–5.0" — corrected.**
  OT→OT is z=1.9, below conventional threshold. Per-row z values and n now shown.

- **Scribal hands "1–4" — corrected to "1–5"** to match Currier's five-hand scheme.

- **Comparator count "11 verified" — corrected to "16 natural-language comparators"**
  throughout (was partially stale from pre-Swahili/Georgian/Tagalog/Mandarin drafting).

### Additions

- **Per-scribe decomposition** added to §3.2 (CHEDY→QOK narrowed to Hands 2 and 3)
  and §3.4 (SYMM-HIGH confirmed independently in Hands 1, 2, 3). New table in §3.2.

- **Cascade CIs and FDR** added to §3.8. Wilson-score 95% CIs, two-proportion z-tests,
  BH-FDR correction. New table with n per chain and composite intervals.

- **Constructed-system control** added as new §3.11 with scoring table.

- **Paradigm-null table** added to §3.10.

- **Four new methods subsections** (§2.9–2.12): per-scribe decomposition, cascade
  CIs/FDR, character-trigram null, constructed-system control.

- **Discussion §4.1** updated: dropped "productive morphology-like paradigm structure"
  reference; added paragraph on what is NOT established in the revision.

- **Discussion §4.2** updated: explicit mention of constructed-control support for
  "does not identify as artificial" caveat.

- **Limitations** expanded from 9 to 11 items. New: "grammar is a weak statistical
  tendency" (#8), "MC correction is partial" (#9), "constructed-system test is n=1"
  (#10). Old "partial reproducibility" retired (#11 now states full reproducibility).

- **Open Problems** expanded to 4 items. Tuned constructed generator added as
  highest-priority adversarial test.

- **Data Availability** updated to list all 9 scripts and 33 regression tests.

- **Bibliography** added Currier 1976, Davis 2020, Zandbergen/Landini/Stolfi LSI.

- **Revision-history paragraph** added before §1.

### Formatting

- MVE table rebuilt with p-columns to fix 121pt margin overflow.
- `\path{}` used for long filenames in Data Availability to allow line breaks.
- `\emergencystretch{3em}` added to preamble for minor overflow tolerance.
- Two residual overfull-hbox warnings (5pt, 1.6pt) — visually undetectable.

---

## Still open

These items were identified during the repair pass but are NOT addressed in v2.
They are listed here for tracking; action is deferred to Phase 2 or journal submission.

1. **Multiple-comparisons correction on transition matrix and suffix-agreement table.**
   BH-FDR applied only to 5 cascade chains. The 6×6 transition matrix (36 cells) and
   ~10 suffix-agreement family pairs are not corrected. Noted in limitations but not
   fixed. Planned: `scripts/10_multiple_comparisons.py`.

2. **High-confidence-boundary intersection analysis.** The four EVA-alphabet
   transcriptions disagree on word boundaries in many loci. An analysis restricting
   to tokens where all four agree has not been performed. Planned:
   `scripts/11_boundary_intersection.py`.

3. **Non-EVA character-boundary validation.** All cross-transcription tests use
   EVA character mapping. A system treating ch/sh as single glyphs is untested.
   Most consequential open objection.

4. **Tuned constructed-system control targeting items 5 and 7.** First-pass
   satisfied 5/7. A tuned generator has not been attempted. Planned:
   `scripts/12_tuned_constructed.py`.

5. **Genre-matched medieval comparison.** No medieval herbal, recipe, or formulary
   tested. Planned: `scripts/13_medieval_genre.py`.

6. **`docs/paper.pdf` replacement.** The committed PDF at `docs/paper.pdf` is the
   pre-revision version. It should be replaced with the v2 PDF from
   `arxiv_submission_v2.zip`. This is a file-copy task, not a content task.

---

## Future hardening tasks (Phase 2+)

- AIIN structure decomposition (842 types, high entropy — unexplained)
- Non-EVA character-boundary transcription test (original Currier alphabet)
- Medieval genre comparison (Trotula, Macer Floridus, Bald's Leechbook)
- Polysynthetic language at corpus scale (Inuktitut, Greenlandic)
- CI/CD update to run full 9-script pipeline + 33 tests on every push
