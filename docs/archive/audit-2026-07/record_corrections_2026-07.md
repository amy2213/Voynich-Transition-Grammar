# Record Corrections — Ready to Apply

Six edits to `docs/durable_findings.md`, one to the README. Each gives the
current text, the replacement, and the evidence. Apply verbatim or reword —
what matters is that the claims match what the code now produces.

---

## 1. §3.5 — wrong cause recorded

The ledger misattributes a correction to itself. This one matters most: an
incorrect causal claim inside the retraction record undermines the artifact
that makes the whole project credible.

**Current:** the 2.50x → 2.625x correction is attributed to *"token-parsing
variation."*

**Replace with:**

> **§3.5 (amended 2026-07)** — The earlier 2.50x CHEDY→QOK figure was
> originally attributed to token-parsing variation. That attribution was
> incorrect. The discrepancy was caused by two different family-classification
> orders coexisting in the codebase: scripts 01/08 tested prefix families
> first, scripts 02/03/04 tested substring families first. On the identical
> frozen dataset, substring-first yields 2.497x and prefix-first yields 2.625x.
> The pipeline now uses a single canonical classifier (`scripts/_canonical.py`).
> Canonical value: **2.659x** (prefix-first, within-line).

**Evidence:** `docs/migration_report_2026-07.md` §2; `scripts/_canonical.py`
diagnostic output.

---

## 2. §3.8 and MVE item 3 — OT→OT is now significant

**Current:** OT→OT suffix agreement recorded at z = 1.9, below the significance
threshold.

**Replace with:**

> Under the canonical classifier, OT→OT suffix agreement is **z = 2.5 on
> n = 169 pairs** (previously z = 1.9 on n = 105, computed under the
> substring-first classifier). All five family pairs now clear z ≥ 2.5.
> OK→OK also strengthens, from z = 2.8 to z = 4.9.

**Evidence:** `docs/migration_report_2026-07.md` §4.2.

---

## 3. §1.6 and MVE item 4 — four of five cascades, not five

**Current:** "All five chains survive Benjamini–Hochberg FDR at α = 0.05."

**Replace with:**

> **Four of five** chains survive BH-FDR at α = 0.05 under two-tailed testing.
> OT→OTHER→OT fails (two-tailed p = 0.0505; the previous one-tailed test was
> carrying it). Corrected figures, using raw counts and Newcombe-Wilson
> intervals for the difference of proportions:
>
> | Chain | Δ | 95% CI | FDR |
> | --- | --- | --- | --- |
> | CHEDY→OTHER→CHEDY | +80.4pp | [+53.1, +91.7] | pass |
> | CHEDY→QOK→CHEDY | +61.2pp | [+40.3, +76.1] | pass |
> | QOK→OTHER→QOK | +38.7pp | [+20.5, +55.8] | pass |
> | QOK→QOK→QOK | +33.0pp | [+7.4, +52.4] | pass |
> | OT→OTHER→OT | +19.8pp | [−0.1, +43.1] | **fail** |
>
> Note also a correction in the opposite direction: QOK→QOK→QOK previously
> appeared marginal because its interval was computed by subtracting the far
> endpoints of two independent Wilson intervals — a conservative bound, not a
> 95% interval. Its correct Newcombe interval excludes zero.

**Evidence:** `docs/inference_fixes_2026-07.md` Part 2.

---

## 4. §1.5 and MVE item 3 — multi-feature compounding

**Current:** "Multi-feature agreement (suffix + length + mantle + circles)
compounds to 5–9x."

**Replace with:**

> The 5–9x figures were computed by multiplying per-feature marginal
> probabilities, which assumes independence between suffix, length, mantle, and
> circle-count. All four are functions of the same token and are strongly
> correlated, so the expected value was understated and the ratio inflated.
>
> Recomputed against a permutation null (whole tokens shuffled, preserving
> feature correlation structure), the all-four range is **1.53x–4.27x**.
> Comparing single-feature to multi-feature under the same null:
>
> | Pair | Suffix only | All four |
> | --- | --- | --- |
> | OT→OT | 1.49x | 1.53x |
> | QOK→QOK | 1.43x | 2.05x |
> | OK→OK | 1.91x | 2.64x |
> | OK→OT | 1.93x | 2.69x |
> | CHEDY→QOK | 1.19x | 4.27x |
>
> Only CHEDY→QOK shows substantial compounding, and on 6 of 615 pairs. OT→OT
> shows none. Suffix-only ratios are unaffected by the correction, so Finding
> 1.5 stands as originally stated.
>
> This is consistent with the existing note that length agreement conditioned
> on suffix and frequency collapses to 1.00x: agreement is suffix-led.

**Evidence:** `docs/inference_fixes_2026-07.md` Part 1.

---

## 5. §1.2 and MVE item 3 — AIIN invariance splits by definition

The largest correction. The claim does not survive in its current form.

**Current:** "AIIN density is invariant across Currier A and B."

**Replace with:**

> This claim depends on which definition of AIIN is used, and the pipeline was
> using two.
>
> | Definition | Currier A | Currier B | KS p | 95% CI on difference |
> | --- | --- | --- | --- | --- |
> | Token *contains* "aiin"/"ain" | 14.96% | 14.97% | 0.742 | [−1.88, +1.94] pp |
> | Canonical AIIN *family* | 13.58% | 10.77% | **0.003** | **[+1.18, +4.49] pp** |
>
> The AIIN token family is **not** invariant. Only total aiin-string density
> is. Decomposing:
>
> | | Total aiin-bearing | Bare AIIN tokens | Embedded in prefixed token | Share embedded |
> | --- | --- | --- | --- | --- |
> | Currier A | 14.96% | 13.58% | 1.37% | 9% |
> | Currier B | 14.97% | 10.77% | 4.20% | 28% |
>
> Restated: **total aiin material is conserved across the Currier languages
> (14.96% vs 14.97%) while its morphological placement shifts — Currier B
> embeds three times as much of it inside qok/ok/ot-prefixed tokens.**
>
> Also correct the type count: **737 unique AIIN types** under the canonical
> classifier, not 842 (that figure used the substring-first policy). The point
> it supported is unchanged — AIIN carries 737 types at 6.58 bits against
> CHEDY's 353 at 5.35 bits, still the opposite of function-word behaviour.

**Note on framing:** the replacement is a better finding than the original. A
conserved total with a shifted distribution is specific and falsifiable; a flat
density was true only because two effects cancelled. Lead with it.

**Evidence:** `docs/finding_1_2_recomputed.md`.

---

## 6. §1.3 — cross-transcription

**Current:** four independent EVA-alphabet transcriptions; ZL baseline
1.52 / 1.54 / 0.99.

**Replace with:**

> All transcriptions are Stolfi-mapped into EVA and differ in word-boundary
> placement and coverage, not in independently defined alphabets. Describe them
> as **EVA-mapped tokenization variants**, not independent transcriptions.
>
> The ZL baseline row was previously a hardcoded print literal
> (`'1.52'`, `'1.54'`, `'0.99'`) rather than a computed value. Computed with
> the same functions applied to the alternatives:
>
> | Transcriber | Tokens | Prefix SC | Suffix SC | Ratio |
> | --- | --- | --- | --- | --- |
> | Currier | 16,453 | 1.30 | 1.53 | 0.85 |
> | FSG | 28,811 | 1.23 | 1.47 | 0.84 |
> | Takahashi | 30,426 | 1.28 | 1.50 | 0.86 |
> | Grove | 7,657 | 1.14 | 1.15 | 0.99 |
> | **ZL (computed)** | 30,298 | **1.27** | **1.52** | **0.836** |
>
> Grove is the only row at 0.99 and has the smallest sample by a factor of two;
> it should not be cited as corroborating the previously published 0.99.

**Evidence:** `docs/divergences_closed_2026-07.md` §2.

---

## 7. README and abstract — the headline

**Current:** prefix SC 1.52, suffix SC 1.54, ratio 0.99, "unique among 16
comparators."

**Replace with:**

> Prefix self-clustering **1.256** [95% CI 1.202, 1.404]; suffix **1.475**
> [1.409, 1.520]; ratio **0.852** [0.815, 0.966]. The confidence interval
> excludes 0.99, so the earlier "near-perfect symmetry" description is not
> supported. The accurate statement is **elevated self-clustering in both
> directions with a residual suffix lean** — still unmatched by any tested
> comparator, but not symmetric.
>
> Across an 80-cell sweep of the affix-detection parameters, Voynich falls in
> SYMM-HIGH in **86%** of parameterizations and is the **only** system in
> SYMM-HIGH in **79%**. Arabic is the sole intruder, reaching SYMM-HIGH in 6 of
> 80 cells.
>
> Report the measurement rather than the bucket label. The Voynich ratio moves
> only 0.69–1.00 across the entire grid (median 0.852), whereas Arabic's moves
> 0.48–5.79. The bucket boundary at 0.80 is a self-selected threshold and
> should not carry the central claim; the underlying measurement is stable and
> can.

**Evidence:** `docs/symm_high_regeneration_note.md`;
`results/symmhigh_sensitivity_results.json`.

---

## Checklist

- [ ] §3.5 cause corrected
- [ ] §3.8 / MVE 3 — OT→OT now significant
- [ ] §1.6 / MVE 4 — four of five cascades
- [ ] §1.5 — multi-feature 1.53–4.27x
- [ ] §1.2 / MVE 3 — AIIN invariance restated, 842 → 737
- [ ] §1.3 — cross-transcription reframed, computed ZL row added
- [ ] README / abstract — headline numbers and sensitivity reported
