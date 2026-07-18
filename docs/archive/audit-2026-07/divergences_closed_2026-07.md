# Final Divergences Closed — Scripts 02 and 05

**Date:** 18 July 2026
**Scope:** audit §2.6 (hardcoded ZL baseline, cross-transcription independence)
and the last two unmigrated classifiers.
**Status:** all six classifier copies now resolve to `scripts/_canonical.py`.
Regression suite 15/15 pass.

---

## 1. There were six copies, not five

The audit identified five divergent classifiers. `05_cross_transcription.py`
carried a sixth, under a comment reading:

```python
# ─── Family classification (same as all other scripts) ──────────────────────
```

It was not the same as all other scripts. It used the substring-first order,
while 01 and 08 used prefix-first. The comment asserting consistency is
precisely the kind of claim that stops anyone from checking.

All six now import `_canonical.classify`. Script 05 retains case-folding
(`tok.lower()`) because the LSI interlinear mixes case across transcribers;
that is a genuine requirement of its input, documented in place.

---

## 2. The ZL baseline was typed in — now computed

### What was wrong

`05_cross_transcription.py` auto-analysed four alternative transcriptions and
then printed the comparison baseline as literal strings:

```python
print(f"  {'ZL (baseline)':<13} {'31608':>7} {'2.63':>6} {'0.50':>6} "
      f"{'1.52':>7} {'1.54':>7} {'0.99':>6} SYMM-HIGH")
```

with a matching hardcoded `zl_baseline` block in the JSON output. The four
alternatives were measured; the thing they were measured against was asserted.
That is not a comparison.

### The fix

`compute_zl_baseline()` reads the ZL parquet snapshot and runs **the same
functions** used for C/F/H/V — same tokenizer, same canonical classifier, same
`compute_prefix_suffix_sc`, same bucket rule.

### Result — and it is the important finding of this step

| Transcriber | Tokens | C→Q | A→Q | Prefix SC | Suffix SC | Ratio | Bucket |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Currier | 16,453 | 2.58 | 0.45 | 1.30 | 1.53 | 0.85 | SYMM-HIGH |
| FSG (Friedman) | 28,811 | 2.51 | 0.48 | 1.23 | 1.47 | 0.84 | SYMM-HIGH |
| Takahashi | 30,426 | 2.53 | 0.49 | 1.28 | 1.50 | 0.86 | SYMM-HIGH |
| Grove | 7,657 | 2.10 | 0.27 | 1.14 | 1.15 | 0.99 | SYMM-HIGH |
| **ZL (computed)** | **30,298** | **2.52** | **0.50** | **1.27** | **1.52** | **0.836** | **SYMM-HIGH** |
| ~~ZL (hardcoded)~~ | ~~31,608~~ | ~~2.63~~ | ~~0.50~~ | ~~1.52~~ | ~~1.54~~ | ~~0.99~~ | SYMM-HIGH |

**The hardcoded baseline was visibly out of line with every alternative and
nobody could notice, because it was typed in.** The four measured
transcriptions cluster at ratio 0.84–0.86 (Grove at 0.99 on only 7,657 tokens);
the asserted ZL row sat at 0.99 with a prefix SC of 1.52 against a measured
1.23–1.30 range.

Computed, ZL lands at **prefix 1.27 / suffix 1.52 / ratio 0.836** — squarely
inside the band formed by the other four.

### Independent convergence

`scripts/10_prefix_suffix_analysis.py`, written separately with its own affix
detection and its own bucket logic, produced **1.256 / 1.475 / 0.852** on the
full ZL corpus. Script 05, different code path and different tokenizer, produces
**1.268 / 1.516 / 0.836**.

Two independent implementations agree on ≈0.84–0.85 and neither reproduces
0.99. The published ratio is not recoverable by any code in the repository.

### Cross-transcription conclusion — restated

The SYMM-HIGH bucket holds across all five rows, so the qualitative
cross-transcription claim survives. But two qualifications belong in the paper:

1. These are **not independent transcriptions.** Script 05's own docstring
   states all systems are Stolfi-mapped into EVA; they differ in word-boundary
   placement and coverage, not in independently defined alphabets. Describe
   them as EVA-mapped tokenization variants.
2. **Grove is the only row at 0.99**, on 7,657 tokens — the smallest sample by
   a factor of two. It should not be cited as corroborating the published 0.99;
   it is the noisiest row in the table.

### Note on the token count

The computed baseline yields 30,298 tokens against the canonical 31,608. Script
05 has its own IVTFF-oriented `parse_tokens` (strips `{}`, `%`, `<>` markers)
which is stricter than the canonical tokenizer. This is a **remaining
divergence** — smaller than the classifier problem, but it means the baseline
row is computed on a slightly different token set than scripts 01–04. Fold
`parse_tokens` into `_canonical` with an IVTFF flag when convenient.

---

## 3. Script 02 — FUNC mapping made explicit

Script 02 legitimately differs from the rest of the pipeline: it relabels one
Voynich family as FUNC so the carry-through metric has a Voynich analogue of
the comparators' function-word class. That is a defensible design choice, but
the analogy has a flaw worth stating.

For comparator languages FUNC membership is a **whole-token** test (token is in
the top-100 short frequent list). For Voynich, AIIN membership is a
**substring** test. Assigning `qokaiin` to FUNC because it contains "aiin" is
analogous to classifying English "unfortunately" as the function word "for".

Two policies are now provided, with `canonical` as the default and the
alternative reported alongside so the choice is auditable rather than inherited:

| Metric | `canonical` (default) | `aiin_first` (historical) |
| --- | --- | --- |
| FUNC density | **11.3%** | 15.0% |
| Mean self-clustering | **1.384x** | 1.445x |
| Max attraction | 2.62x | 2.50x |
| Max repulsion | 0.50x | 0.48x |
| Mean carry-through | 1.70x | 1.74x |

Under the canonical policy `qokaiin` stays QOK, so FUNC density drops from 15%
to 11.3% — consistent with the 25% split-half AIIN drop reported in the
migration report. **The 15% AIIN density figure that appears throughout the
paper is the `aiin_first` number.** Decide which you are reporting and say so.

---

## 4. Record changes required

1. **`durable_findings.md` §1.3 cross-transcription block** — replace the
   Currier/FSG/Takahashi/Grove PS ratios (0.85/0.84/0.86/0.99) with the
   recomputed values and add the computed ZL row at 0.836. Drop "four
   independent EVA-alphabet transcribers" in favour of "four EVA-mapped
   tokenization variants."
2. **§1.2 AIIN invariance / MVE item 3** — the ~15% density figure is
   policy-dependent (11.3% canonical, 15.0% aiin_first). State the policy.
3. **README** — "SYMM-HIGH profile survives all four alternative EVA-alphabet
   transcriptions tested" is accurate but should note these are tokenization
   variants of one alphabet mapping, not independent transcriptions.
4. **Add the computed baseline to the paper's cross-transcription table.**
   A measured ZL row sitting inside the range of the alternatives is a stronger
   result than an asserted one sitting outside it.

---

## 5. Files

| File | Change |
| --- | --- |
| `scripts/02_cross_linguistic.py` | canonical predicates; explicit `FUNC_POLICY`; alt policy reported |
| `scripts/05_cross_transcription.py` | canonical classifier; `compute_zl_baseline()` replaces hardcoded literals |
| `results/cross_linguistic_results.json` | regenerated, with `alt_policy` block |
| `results/cross_transcription_results.json` | regenerated, computed `zl_baseline` |

---

## 6. Remaining

1. **SYMM-HIGH sensitivity sweep** — ratio CI lower bound 0.815 against the
   0.80 bucket boundary. Now the highest-priority item: three independent code
   paths agree the ratio is ≈0.84, which is closer to the boundary than 0.99
   was, so bucket robustness is the live question.
2. **Matrix-wide multiple-comparisons correction** for the 6×6 transition cells.
3. **Finding 1.2 recomputation** — AIIN family is materially smaller under the
   canonical policy; the 842-unique-types figure needs regenerating.
4. **Unify `parse_tokens`** — script 05's IVTFF tokenizer still differs
   (30,298 vs 31,608 tokens).
5. Add `11_multifeature_permutation.py` to `run_all.py`'s `PIPELINE` list.
