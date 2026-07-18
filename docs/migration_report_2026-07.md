# Canonical Classifier Migration — Change Report

**Date:** 18 July 2026
**Change:** `scripts/_canonical.py` introduced as the single source of truth for
tokenization, family predicates, and family assignment. Scripts 01, 03, 04, and
08 migrated to import it. Canonical transition statistic switched from
flattened to within-line.
**Result:** all 15 regression tests pass. **175 numeric values changed across
four result files.**

---

## 1. What was wrong

Five scripts carried independent copies of the classifier with two different
priority orders (01/08: QOK-first; 02/03/04: AIIN-first). The orders disagreed
on 191 types / 4,269 token instances — 3.59% of the corpus.

Root cause was not the ordering. QOK/OK/OT are *prefix* predicates; CHEDY/AIIN
are *substring* predicates. Mixing them in one priority chain guarantees
overlap: **1,423 token instances (4.50% of corpus), 160 types.**

| Overlap | Instances | Examples |
| --- | --- | --- |
| QOK + AIIN | 547 | `qokain`, `qokaiin` |
| OK + AIIN | 359 | `okaiin`, `okain` |
| OT + AIIN | 253 | `otaiin`, `otain` |
| QOK + CHEDY | 97 | `qokchedy` |
| OK + CHEDY | 78 | `okchey` |
| OT + CHEDY | 77 | |
| CHEDY + AIIN | 12 | |

`qokaiin` genuinely satisfies both definitions. No priority order resolves
that; it only conceals which choice was made. `_canonical.classify(strict=True)`
now returns `AMBIGUOUS` for these tokens so any analysis can exclude them.

**Adopted policy:** prefix-first ordering, within-line transitions. Justified in
the `_canonical.py` docstring; both alternatives remain runnable.

---

## 2. Headline result — robust

| Policy | CHEDY→QOK | AIIN→QOK |
| --- | --- | --- |
| prefix-first, flattened *(old published)* | 2.625x | 0.504x |
| **prefix-first, within-line (new canonical)** | **2.659x** | **0.444x** |
| substring-first, flattened | 2.497x | 0.475x |
| substring-first, within-line | 2.535x | 0.402x |
| strict — ambiguous tokens excluded entirely | 2.518x | — |

Full spread 2.497x–2.659x (≈6%). **The effect survives every policy, including
dropping all 1,423 ambiguous tokens.** Report it as a range with the
sensitivity, not as a bare point estimate — it is a stronger claim that way.

---

## 3. Corrections required to the record

### 3.1 `durable_findings.md` §3.5 is wrong about its own cause

§3.5 records the earlier 2.50x as corrected to 2.625x, attributing the
difference to *"token-parsing variation."* It was not. **2.497x is exactly what
the substring-first classifier produces on the identical frozen dataset.** The
discrepancy was a classifier-order difference between scripts, not parsing
noise. Amend the entry — the retraction ledger is the project's principal
credibility asset and an incorrect causal attribution inside it costs more than
the number does.

### 3.2 Observed CHEDY→QOK count: 626 → 615

Eleven of the 626 pairs spanned a line boundary. Under Finding 1.4 those pairs
should never have been counted.

### 3.3 OT→OT suffix agreement is now significant

Retraction §3.8 corrected the blanket "all significant z=3.4–5.0" claim,
recording OT→OT at z=1.9 as below threshold. Under the canonical classifier
OT→OT is **z = 2.5 on n = 169 pairs** (was z=1.9 on n=105). The original
correction was right to be made; the finding it retired now stands. Update §3.8
and MVE item 3 — all five family pairs are significant.

---

## 4. Every material change, by file

### 4.1 `core_analysis_results.json` — 62 changes

| Value | Before | After | Δ |
| --- | --- | --- | --- |
| CHEDY→QOK ratio | 2.625x | **2.659x** | +1.3% |
| CHEDY→QOK obs | 626 | **615** | −11 pairs |
| AIIN→QOK ratio | 0.504x | **0.444x** | −11.9% |
| AIIN→QOK obs | 160 | 127 | −21% |
| OT→OT ratio | 2.052x | 1.933x | −5.8% |
| QOK→AIIN ratio | 0.725x | 0.693x | −4.4% |
| Self-clustering (all) | 1.384x | 1.345x | −2.8% |
| Self-clustering (backbone) | 1.451x | 1.403x | −3.3% |
| Chi² | 1407.8 | 1385.4 | −1.6% |
| Carry-through OK | 2.73x | 2.67x | −2.2% |
| Carry-through OT | 2.21x | 2.14x | −3.2% |
| Carry-through CHEDY | 1.64x | 1.60x | −2.4% |

AIIN invariance is unaffected: Currier A 15.0%, B 15.0%, KS p = 0.742.

### 4.2 `extended_analysis_results.json` — 87 changes, 50 exceeding ±10%

Largest impact, because script 04 previously used the AIIN-first order.

**Suffix agreement (Finding 1.5):**

| Pair | z before | z after | n before | n after |
| --- | --- | --- | --- | --- |
| CHEDY→QOK | 3.5 | 3.7 | 469 | 615 |
| QOK→QOK | 5.2 | 5.1 | 301 | 371 |
| OK→OT | 3.3 | 4.3 | 76 | 115 |
| OK→OK | 2.8 | **4.9** | 110 | 157 |
| OT→OT | 1.9 | **2.5** | 105 | 169 |

All five now clear z ≥ 2.5. See §3.3.

**Multi-feature agreement (Finding 1.6)** — note these values remain
**unsupported** pending the independence fix (audit §2.4); listed for
completeness only:

| Pair | Before | After |
| --- | --- | --- |
| CHEDY→QOK | 7.64x | 6.83x |
| QOK→QOK | 5.00x | 6.32x |
| OK→OT | 8.74x | 11.43x |
| OK→OK | 6.56x | 9.76x |
| OT→OT | 4.56x | 6.14x |

**Cascades (Finding 1.6/1.7):** denominators grew substantially —
QOK→OTHER→QOK n_disagree 61 → 124 (+103%), CHEDY→QOK→CHEDY 45 → 75 (+67%). The
flagship CHEDY→OTHER→CHEDY chain is unchanged at n_agree = 13, n_disagree = 119.

After rerunning `07_cascade_uncertainty.py`:

| Chain | Cascade | Conservative 95% CI | BH-FDR |
| --- | --- | --- | --- |
| CHEDY→OTHER→CHEDY | +81pp | [+48.3, +93.9] | pass |
| CHEDY→QOK→CHEDY | +61pp | [+33.6, +79.8] | pass |
| QOK→OTHER→QOK | +39pp | [+14.9, +59.9] | pass |
| QOK→QOK→QOK | +33pp | [−3.1, +59.1] | pass |
| OT→OTHER→OT | +20pp | [−8.0, +48.5] | pass |

CHEDY→QOK→CHEDY strengthens (+56 → +61pp); QOK→OTHER→QOK weakens
(+44 → +39pp). Two CIs still touch zero. These figures remain provisional
pending the rounded-count and one-tailed-test fixes (audit §2.5).

### 4.3 `stress_test_results.json` — 26 changes

| Value | Before | After |
| --- | --- | --- |
| Split-half AIIN mean | 15.044 | **11.339** (−25%) |
| Split-half AIIN 95% range | [14.62, 15.47] | [10.94, 11.74] |
| Split-half AIIN→QOK range low | 0.386 | 0.425 |
| Section SC p (biological) | 0.001 | 0.003 |
| Section SC p (herbal_B) | 0.001 | 0.003 |

The 25% drop in split-half AIIN density is the direct, expected consequence of
prefix-first ordering: tokens like `qokaiin` now count as QOK rather than AIIN.
**This is the largest single change in the pipeline and it needs a decision.**
The AIIN family is materially smaller under the canonical policy, which bears
on Finding 1.2 (AIIN invariance) — the invariance itself survives (KS p = 0.742
unchanged in 01), but the family being described is not the same family.

### 4.4 `per_scribe_results.json` — 0 changes

Script 08 already used prefix-first ordering. Per-scribe conclusions stand
unaltered.

---

## 5. Test suite

`tests/test_canonical_values.py` — 15/15 pass. Three canonical values updated,
each with the supersession and its reason recorded in the docstring:

- `test_chedy_to_qok_attraction`: 2.625 → **2.659**
- `test_aiin_to_qok_repulsion`: 0.504 → **0.444**
- `test_chedy_qok_obs_count`: 626 → **615**

The suite now asserts against values generated by the current pipeline rather
than inherited ones.

---

## 6. Still outstanding

Unchanged from the audit; none are addressed by this migration:

1. **Script 02 not migrated.** It uses a separate `classify_voynich` with a
   FUNC label for cross-linguistic comparison. Migrate or document why it
   legitimately differs.
2. **Multi-feature independence** (audit §2.4) — 5–9x figures remain
   unsupported.
3. **Cascade rounded counts / one-tailed tests** (audit §2.5).
4. **Hardcoded ZL baseline** in `05_cross_transcription.py` (audit §2.6).
5. **SYMM-HIGH sensitivity sweep** — ratio CI lower bound 0.815 against a 0.80
   bucket boundary.
6. **Matrix-wide multiple-comparisons correction** for the 6×6 cells.

Recommended next: (2) and (3) together, since both live in the cascade /
agreement path and both currently gate claims in MVE items 3 and 4.
