# Inference-Layer Fixes — Findings 1.6 and 1.7

**Date:** 18 July 2026
**Scope:** audit §2.4 (multi-feature independence assumption) and §2.5 (cascade
inference procedure). Both gate MVE checklist items 3 and 4.
**Status:** both fixed. Regression suite 15/15 pass.

---

## Part 1 — Multi-feature agreement was inflated 1.6x–4.2x

### What was wrong

`04_extended_analysis.py::combined_agreement` estimated expected joint
agreement by multiplying per-feature marginals:

```python
joint_expected = 1.0
for ie in individual_expected:
    joint_expected *= ie
```

Valid only under mutual independence of suffix, length, mantle, and
circle-count. They are all functions of the same token and are strongly
correlated — suffix reads the final characters, mantle includes the same
terminal `-dy`/`-ey` material, circle-count counts `y` which terminates the two
commonest suffix classes, and suffix class constrains length. Multiplying
correlated marginals drives the denominator far below its true value.

### The fix

`scripts/11_multifeature_permutation.py` replaces the analytic null with a
permutation null. Target tokens are shuffled across pairs within the same
family transition. Both marginal token distributions are preserved exactly,
and because **whole tokens** are permuted, each token's internal feature
correlations travel with it — so any dependence-driven inflation appears in the
null as well and cancels in the ratio. No independence assumption is required.

Feature functions were copied verbatim from `04_extended_analysis.py` so the
only thing changing between old and new figures is the null model.

### Results (2,000 permutations, seed 42)

| Pair | n | Feature set | Observed | Null mean | **Ratio vs permuted null** | p (2-sided) | Old (independence) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHEDY→QOK | 615 | suffix only | 28.8% | 24.3% | **1.19x** | 0.0015 | 1.19x |
| CHEDY→QOK | 615 | all four | 1.0% | 0.2% | **4.27x** | 0.0025 | 6.83x |
| QOK→QOK | 371 | suffix only | 31.5% | 22.1% | **1.43x** | 0.0005 | 1.43x |
| QOK→QOK | 371 | all four | 16.2% | 7.9% | **2.05x** | 0.0005 | 6.32x |
| OK→OT | 115 | suffix only | 30.4% | 15.8% | **1.93x** | 0.0005 | 1.92x |
| OK→OT | 115 | all four | 20.0% | 7.4% | **2.69x** | 0.0005 | 11.43x |
| OK→OK | 157 | suffix only | 24.8% | 13.0% | **1.91x** | 0.0005 | 1.91x |
| OK→OK | 157 | all four | 16.6% | 6.3% | **2.64x** | 0.0005 | 9.76x |
| OT→OT | 169 | suffix only | 19.5% | 13.1% | **1.49x** | 0.0150 | 1.48x |
| OT→OT | 169 | all four | 10.7% | 7.0% | **1.53x** | 0.0470 | 6.14x |

### What this means

**Single-feature figures are unaffected.** Suffix-only ratios are identical to
three decimal places under both nulls — as expected, since no multiplication
occurs. Finding 1.5 stands.

**The "5–9x compounding" claim is retired.** Multiplied marginals overstated
the all-four ratio by 1.6x–4.2x (mean 3.3x). The corrected range is
**1.53x–4.27x**.

**More consequentially, the compounding narrative largely dissolves.** The
claim was that agreement *compounds* across features. Compare suffix-only to
all-four under the correct null:

| Pair | Suffix only | All four | Compounding? |
| --- | --- | --- | --- |
| OT→OT | 1.49x | 1.53x | **none** |
| QOK→QOK | 1.43x | 2.05x | modest |
| OK→OK | 1.91x | 2.64x | modest |
| OK→OT | 1.93x | 2.69x | modest |
| CHEDY→QOK | 1.19x | 4.27x | substantial |

Only CHEDY→QOK shows strong multi-feature compounding, and it does so on an
observed agreement rate of 1.0% (6 of 615 pairs) — thin. OT→OT shows none at
all. Everything is still significant, but "the effect compounds across multiple
features (5–9x)" should be replaced with something like: *adjacent-token
agreement is suffix-led; joint agreement across four features exceeds a
permutation null by 1.5x–4.3x, with substantial multi-feature compounding
only in CHEDY→QOK.*

This also **strengthens** the existing §1.5 note that "length agreement
conditioned on suffix + frequency collapses to 1.00x — suffix is the primary
feature." The permutation result is consistent with that and should be
presented alongside it.

---

## Part 2 — Cascade inference

### What was wrong

1. **Counts reconstructed from rounded percentages.**
   `07_cascade_uncertainty.py` did `k = round(pct/100 * n)` where `pct` had
   already been rounded to a whole number by script 04. At n=13 that can shift
   the count by ±1 and move the interval materially.
2. **One-tailed tests.** `two_prop_z` returned `norm_sf(z)`, presupposing the
   direction of an effect discovered in the same data.
3. **Interval method.** The "conservative" CI subtracted far endpoints of two
   independent Wilson intervals. Valid as a bound, but markedly over-wide — not
   a 95% interval, which is why two chains appeared to touch zero.

### The fix

- `04_extended_analysis.py` now emits raw success counts (`k_agree`,
  `k_disagree`) alongside the percentages. `07` reads them and **raises** if
  they are absent rather than silently reconstructing.
- Two-tailed p-values; BH-FDR applied to those.
- **Newcombe-Wilson hybrid-score interval** for the difference of proportions
  (Newcombe 1998, method 10) reported alongside the conservative bound.

Raw counts now visible for the first time:

| Chain | k/n agree | k/n disagree |
| --- | --- | --- |
| CHEDY→OTHER→CHEDY | 11/13 | 5/119 |
| CHEDY→QOK→CHEDY | 18/26 | 6/75 |
| QOK→OTHER→QOK | 16/31 | 16/124 |
| QOK→QOK→QOK | 14/30 | 3/22 |
| OT→OTHER→OT | 6/19 | 6/51 |

### Results

| Chain | Δ | Conservative CI | **Newcombe CI** | p (2-tailed) | BH-FDR |
| --- | --- | --- | --- | --- | --- |
| CHEDY→OTHER→CHEDY | +80.4pp | [+48.3, +93.9] | **[+53.1, +91.7]** | <1e-16 | pass |
| CHEDY→QOK→CHEDY | +61.2pp | [+33.6, +79.8] | **[+40.3, +76.1]** | 2.6e-10 | pass |
| QOK→OTHER→QOK | +38.7pp | [+14.9, +59.9] | **[+20.5, +55.8]** | 1.9e-06 | pass |
| QOK→QOK→QOK | +33.0pp | [−3.1, +59.1] | **[+7.4, +52.4]** | 0.0121 | pass |
| OT→OTHER→OT | +19.8pp | [−8.0, +48.5] | **[−0.1, +43.1]** | 0.0505 | **fail** |

### What changed

**QOK→QOK→QOK is rescued.** Its conservative CI touched zero ([−3.1, 59.1]);
the correct Newcombe interval is **[+7.4, +52.4]** — entirely above zero. The
apparent weakness was an artifact of the over-wide interval method, not the
data.

**OT→OTHER→OT no longer survives FDR.** Two-tailed p = 0.0505 versus the
previous one-tailed 0.025; its Newcombe CI is [−0.1, +43.1], crossing zero by a
hair. The one-tailed test was carrying it. **The claim that all five chains
survive BH-FDR at α=0.05 is now false — four of five do.** MVE item 4 and
`durable_findings` §1.6 both need updating.

**The flagship is unchanged in substance** but should be quoted more precisely:
+80.4pp (not +81), Newcombe CI [+53.1, +91.7], on k=11/13 agreement trials. The
n=13 thinness caveat stands and should stay in the text.

---

## Record changes required

1. **`durable_findings.md` §1.6** — "All five chains survive Benjamini–Hochberg
   FDR at α=0.05" → four of five. OT→OTHER→OT fails at two-tailed p=0.0505.
2. **MVE checklist item 4** — same correction; effect-size range becomes
   +20pp to +80pp with four chains surviving.
3. **`durable_findings.md` §1.5 / MVE item 3** — replace "Multi-feature
   agreement (suffix + length + mantle + circles) compounds to 5–9x" with the
   permutation-null range 1.53x–4.27x, and note that only CHEDY→QOK shows
   substantial compounding over suffix alone.
4. **README** — the sentence "The effect compounds across multiple features
   (suffix + length + mantle = 5–9x)" is now wrong and is in the headline
   summary.
5. Report the QOK→QOK→QOK rescue explicitly — it is a correction *in your
   favour*, and stating both directions of a correction is more persuasive than
   only reporting the ones that weaken claims.

---

## Files

| File | Change |
| --- | --- |
| `scripts/11_multifeature_permutation.py` | **new** — permutation-null multi-feature agreement |
| `scripts/04_extended_analysis.py` | emits raw `k_agree` / `k_disagree` |
| `scripts/07_cascade_uncertainty.py` | raw counts, two-tailed, Newcombe-Wilson CI |
| `results/multifeature_permutation_results.json` | **new** |
| `results/cascade_uncertainty_results.json` | regenerated |

Add `11_multifeature_permutation.py` to the `PIPELINE` list in `run_all.py`.

---

## Remaining after this step

1. Script 02 not migrated to `_canonical` (separate `classify_voynich`).
2. Hardcoded ZL baseline in `05_cross_transcription.py` (audit §2.6).
3. SYMM-HIGH sensitivity sweep — ratio CI lower bound 0.815 vs 0.80 boundary.
4. Matrix-wide multiple-comparisons correction for the 6×6 cells.
5. Split-half AIIN density fell 25% under the canonical classifier; Finding 1.2
   and the 842-unique-types figure need recomputing.
