# Audit Closed — Multiple Comparisons, Tokenizer, Pipeline

**Date:** 18 July 2026
**Scope:** the final three remediation items. Regression suite 15/15 pass.
**Status:** the audit is closed. Remaining work is research, not repair.

---

## 1. Matrix-wide multiple-comparisons correction

### The problem

CHEDY→QOK and AIIN→QOK are presented as headline findings. Both are cells
selected from a 6×6 transition matrix — 36 cells — on the basis of being the
most extreme, and no correction was applied across the family they were drawn
from. `durable_findings.md` §5.5 labels the matrix exploratory, but the README
and abstract present these two cells as results. Selecting the largest of 36
effects and reporting its uncorrected p-value is the textbook error.

### Method

`scripts/13_matrix_fdr.py`. Two test families corrected separately, since
pooling them would be over-conservative:

- **Family A** — 36 transition cells. Each tested by collapsing to 2×2 (this
  cell against everything else on both margins) and applying chi-square with
  continuity correction, or Fisher's exact where any expected count falls
  below 5.
- **Family B** — 5 suffix-agreement pairs, two-tailed z.

Both get Benjamini-Hochberg FDR at α=0.05. Holm-Bonferroni (FWER) is reported
alongside — BH is the right primary correction for exploratory screening, but
surviving FWER is a stronger statement and a reviewer will ask.

### Results — both headlines survive FWER, not merely FDR

| Cell | Obs | Expected | Ratio | p (raw) | BH-FDR | Holm-FWER |
| --- | --- | --- | --- | --- | --- | --- |
| **CHEDY→QOK** | 615 | 231.3 | **2.659** | 2.0e-169 | **pass** | **pass** |
| **AIIN→QOK** | 127 | 286.3 | **0.444** | 1.3e-25 | **pass** | **pass** |
| QOK→QOK | 371 | 241.6 | 1.536 | 5.5e-20 | pass | pass |
| QOK→OTHER | 1358 | 1556.8 | 0.872 | 1.3e-16 | pass | pass |
| QOK→CHEDY | 333 | 229.4 | 1.452 | 6.7e-14 | pass | pass |
| QOK→AIIN | 199 | 287.0 | 0.693 | 8.7e-09 | pass | pass |
| OK→OK | 157 | 102.2 | 1.536 | 1.1e-08 | pass | pass |
| AIIN→OK | 266 | 193.7 | 1.373 | 1.5e-08 | pass | pass |
| AIIN→OT | 244 | 181.1 | 1.347 | 3.9e-07 | pass | pass |
| CHEDY→AIIN | 214 | 274.8 | 0.779 | 5.3e-05 | pass | pass |

**Family A: 26 of 36 cells survive BH-FDR; 20 of 36 survive Holm-FWER.**

CHEDY→QOK at p = 2.0e-169 is not remotely marginal — it clears Bonferroni
correction against the full matrix by 167 orders of magnitude. The
multiple-comparisons objection, which was legitimate as a procedural matter,
turns out to cost nothing.

**Family B: 5 of 5 suffix pairs survive both BH-FDR and Holm-FWER**, including
OT→OT (z = 2.5, p = 0.0124), which was below threshold before the classifier
migration.

### What to say in the paper

Replace "matrix is exploratory, uncorrected" with the correction and its
result. This converts a known weakness into a strength: *26 of 36 transition
cells survive BH-FDR across the full matrix, and both headline cells survive
Holm-Bonferroni FWER correction.* That is a materially stronger claim than the
uncorrected version, and it removes the most obvious reviewer objection.

---

## 2. Tokenizer unification

Script 05 carried its own IVTFF tokenizer, yielding 30,298 tokens against the
canonical 31,608. Both now live in `_canonical`, with the difference measured
and documented rather than accidental:

```
parse_tokens        31,608 tokens   (parquet snapshot — already cleaned)
parse_tokens_ivtff  30,298 tokens   (raw IVTFF — strips comments, dots, markers)
gap                  1,310  =  1,161 tokens shorter than 2 characters
                            +    149 tokens containing non-alphabetic characters
```

**The gap is entirely attributable to two extra filters (`len >= 2` and
`isalpha`), not to any difference in word segmentation.** That is the
reassuring answer: the two tokenizers agree on where words begin and end, which
is what the transition analysis depends on.

The divergence is legitimate — raw IVTFF genuinely needs more cleaning than the
parquet snapshot — so both are retained. What changes is that they now sit in
one file with the difference quantified in the docstring, instead of drifting
apart in separate scripts.

Cross-transcription results are unchanged by this move.

---

## 3. Pipeline

`run_all.py` now includes the four new analyses:

```python
("Prefix/suffix (SYMM-HIGH)",  scripts/10_prefix_suffix_analysis.py)
("Multi-feature permutation",  scripts/11_multifeature_permutation.py)
("SYMM-HIGH sensitivity",      scripts/12_symmhigh_sensitivity.py)
("Transition matrix FDR",      scripts/13_matrix_fdr.py)
```

Script 05 remains outside the default pipeline (it requires
`LSI_ivtff_0d.txt`, a separate data file) — unchanged, and correctly so.

Note that 12 is slow: the full 80-cell grid over 17 systems takes a while. Run
`--quick` in CI and the full grid manually before submission.

---

## 4. Record changes from this step

1. **`durable_findings.md` §5.5** — replace the exploratory-and-uncorrected
   note with: 26/36 cells survive BH-FDR; CHEDY→QOK and AIIN→QOK survive
   Holm-Bonferroni FWER across the full 36-cell matrix; all 5 suffix-agreement
   pairs survive both.
2. **README / abstract** — add the FWER result to the headline transition
   claims. It is the cheapest credibility gain available in the whole document.

---

## 5. Audit status

**Closed.** All seven defects from `technical_audit_2026-07.md` are remediated:

| # | Defect | Status |
| --- | --- | --- |
| 2.1 | Headline table had no generating code | fixed — `10_prefix_suffix_analysis.py` |
| 2.2 | Six divergent classifier copies | fixed — `_canonical.py` |
| 2.3 | Transitions crossed line boundaries | fixed — within-line canonical |
| 2.4 | Multi-feature independence assumption | fixed — `11_multifeature_permutation.py` |
| 2.5 | Cascade rounded counts, one-tailed tests | fixed — raw counts, two-tailed, Newcombe |
| 2.6 | Hardcoded ZL baseline | fixed — `compute_zl_baseline()` |
| 2.7 | Multiple comparisons only partial | fixed — `13_matrix_fdr.py` |

Plus two defects found during remediation and not present in the original
audit: the `durable_findings` §3.5 misattribution, and the AIIN
invariance definitional split (`finding_1_2_recomputed.md`).

**Outstanding, none blocking:**

1. Apply the record corrections (`record_corrections_2026-07.md`) — yours to do.
2. AIIN equivalence margin — the invariance claim still lacks a declared TOST
   margin, though it now needs restating anyway.
3. Mandarin requires jieba/pypinyin segmentation before inclusion.
4. Comparator bootstrap CIs in script 10 not computed (runtime; not
   load-bearing, comparators sit far from the boundary).

**Next is research, not repair:** genre-matched medieval comparators (Trotula,
Circa instans, Macer Floridus, Bald's Leechbook), non-EVA character-boundary
validation, and a tuned adversarial generator targeting MVE items 5 and 7 —
the two your constructed control did not cheaply reproduce.
