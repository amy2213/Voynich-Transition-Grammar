# Technical Audit — Voynich-Transition-Grammar

**Repository:** `github.com/amy2213/Voynich-Transition-Grammar` (main, 36 commits)
**Audit date:** 18 July 2026
**Scope:** source-level review of `scripts/01`–`scripts/09`, `run_all.py`,
`tests/test_canonical_values.py`, `results/*.json`, `docs/durable_findings.md`
**Method:** repository cloned and executed locally; all claims below verified
against source or by running code, not inferred from documentation.

---

## Summary

This is a serious, self-correcting research program. The retraction discipline
in `durable_findings.md` — particularly the trigram-null test that killed the
productive-morphology interpretation, and the constructed-control that demoted
five of seven checklist items — puts it ahead of essentially everything else in
the public Voynich-computational space.

It also has five implementation defects that affect published numbers, and one
that invalidated the reproducibility claim entirely. That defect is now fixed
(§3). The remaining four are not.

**Verdict:** credible, original, transparent, worth continuing. The descriptive
transition findings are promising. The central cross-linguistic uniqueness
claim was, until this audit, not reproducible from the advertised workflow; it
now is, and it survives — with corrected numbers and a new robustness caveat.

**Do not submit the preprint until §4.1–§4.4 are repaired**, because each of
them moves published values.

---

## 1. What holds up

**1.1 `docs/durable_findings.md` is the project's strongest artifact.** A living
retained/narrowed/retired ledger, with the specific test that killed each
retired claim, is pre-registration-adjacent discipline rarely seen in solo
work. The §3.1 retraction (r = 0.42–0.71 edit-graph correlation, retired
because a character-trigram null containing no morphology reproduces it) is
evidence that the surviving findings are being tested honestly — it shows
willingness to lose a wanted result.

**1.2 The constructed-control test is the correct adversarial move**, and its
limits are scoped correctly. Five of seven checklist items were cheaply
engineered by a first-pass generator, which properly demotes them from
discriminating evidence to descriptive baseline, leaving items 5 and 7 as the
actual load-bearing claims.

**1.3 Per-scribe decomposition caught a real aggregation artifact.** A
manuscript-wide CHEDY→QOK claim that turns out to be Hands 2/3-specific
(n = 596 of 617 observations) was caught internally rather than by a reviewer.

**1.4 Cross-transcription testing addresses the right objection** — that the
effect is an artifact of one tokenization — even though the implementation is
weaker than claimed (§4.5).

---

## 2. Verified defects

Each item below was confirmed by reading or running the code.

### 2.1 The headline result had no generating code — FIXED (§3)

Every `json.dump` in `scripts/` traced to its output:

| Script | Writes |
| --- | --- |
| 01_core_analysis | `core_analysis_results.json` |
| 02_cross_linguistic | `cross_linguistic_results.json` |
| 03–09 | their own respective files |

**No script wrote `results/prefix_suffix_analysis.json`** — the source of the
SYMM-HIGH table, the paper's most quotable claim. Script 02 could not have
produced it: `get_top_families()` builds prefix families only
(`w.startswith(prefix)`) and returns a single `mean_self_cluster`. No
suffix-side self-clustering was computed anywhere in the pipeline.

Because `tests/test_canonical_values.py` loads that JSON and asserts against
it, the regression suite was confirming that a static file still contained the
values it was committed with. Tautological, not a reproducibility check.

Compounding this, the file's own `method` field documented a methodological
asymmetry: *"Auto-detected top-5 affix families... Voynich uses standard EVA
prefix families for prefix SC."* Voynich was scored with hand-picked families
selected for structural salience; comparators with auto-detected ones.

### 2.2 Family classification order is inconsistent across scripts

| Script | Check order |
| --- | --- |
| 01_core_analysis | QOK → OK → OT → CHEDY → AIIN |
| 08_per_scribe_analysis | QOK → OK → OT → CHEDY → AIIN |
| 02_cross_linguistic | **AIIN** → QOK → OK → OT → CHEDY |
| 03_stress_tests | **AIIN** → QOK → OK → OT → CHEDY |
| 04_extended_analysis | **AIIN** → QOK → OK → OT → CHEDY |

Measured over the bundled corpus: **191 token types, 4,269 token instances
(3.59% of corpus)** receive different family labels depending on which script
is running. Examples: `chedydaiin`, `cheykaiin`, `chedyotaiin` are CHEDY in the
core analysis and AIIN in the stress tests.

The headline CHEDY→QOK statistic and the stress tests that validate it are not
computed over the same data model.

### 2.3 Core transition matrix crosses line boundaries

`01_core_analysis.py:82`:
```python
all_tokens = [t for l in lines for t in l["tokens"]]
```
`compute_transitions()` then walks that flattened sequence, so the canonical
2.625x includes line-final → line-initial pairs — in a project whose Finding
1.4 establishes that transition structure *resets* at exactly those boundaries.

Script 04 does this correctly (iterates per-line). The headline number and the
line-boundary finding are computed under mutually inconsistent representations.

### 2.4 Multi-feature agreement multiplies dependent marginals

`04_extended_analysis.py::combined_agreement`:
```python
joint_expected = 1.0
for ie in individual_expected:
    joint_expected *= ie
```
Suffix, length, mantle, and circle-count are all functions of the same token
and are strongly correlated — suffix largely determines final characters, which
drive length and mantle. Multiplying marginals produces an artificially small
denominator.

The reported 5–9x multi-feature agreement is inflated by an unknown amount.
Treat as unsupported until recomputed against a permutation null.

### 2.5 Cascade counts reconstructed from rounded percentages

`07_cascade_uncertainty.py`:
```python
p_agree = d["if_agree_pct"] / 100.0
k_agree = round(p_agree * n_agree)
```
Raw integer counts exist upstream in `extended_analysis_results.json`. At
n = 13 for the flagship chain, a percentage rounded to integer precision can
shift the reconstructed count by ±1, materially moving the Wilson interval.

Also confirmed: `two_prop_z` is one-tailed, and BH-FDR is applied to those
one-tailed p-values.

### 2.6 Cross-transcription independence is overstated

Two separate problems:

- The script's own docstring states all four transcriptions are Stolfi-mapped
  into EVA. They differ in word boundaries and coverage, not in independently
  defined character alphabets. They are not independent replications.
- `05_cross_transcription.py:321` prints the ZL baseline row as a **hardcoded
  string literal**:
  ```python
  print(f"  {'ZL (baseline)':<13} {'31608':>7} {'2.63':>6} {'0.50':>6} {'1.52':>7} {'1.54':>7} {'0.99':>6} SYMM-HIGH")
  ```
  The four alternatives use auto-detected families; the baseline they are
  compared against is typed in.

### 2.7 Multiple comparisons — partially handled

BH-FDR is correctly applied to the five cascade chains. Per `durable_findings`
§5.5, the 36-cell transition matrix and ~10 suffix-agreement pairs are
uncorrected and labelled exploratory — but the README presents CHEDY→QOK and
AIIN→QOK as headline findings drawn from that uncorrected matrix. Effect sizes
are large enough that they likely survive correction; that should be
demonstrated, not assumed.

### 2.8 AIIN "invariance" — partially defensible

The critique that `p > 0.05` does not establish equivalence is correct in
general, but weaker here than stated: a bootstrap CI on the A–B difference
([−1.95%, +2.02%]) is already the right *kind* of evidence. What is missing is
a declared equivalence margin. Without one it is not a TOST and should not be
called invariance.

---

## 3. Fix delivered: `scripts/10_prefix_suffix_analysis.py`

Generates the SYMM-HIGH table from raw data, applying **one** detection
procedure to all 17 systems including Voynich: top-5 affixes of length 2–3,
coverage 2–20%, greedy, non-nested; suffix families by the mirror-image
procedure. Self-clustering = observed(c→c) / expected under independence.
Voynich CIs by contiguous block bootstrap (block size 50, 400 iterations) on
the full corpus — blocks rather than i.i.d. tokens, to preserve the local
sequential dependence the analysis is about.

The legacy asymmetric variant is retained under `legacy_asymmetric_*` keys so
the effect of the asymmetry is measured rather than assumed harmless.

### 3.1 Results

**Voynich** (n = 31,608):

| | Published | Regenerated | 95% CI |
| --- | --- | --- | --- |
| Prefix SC | 1.524 | **1.256** | [1.202, 1.404] |
| Suffix SC | 1.544 | **1.475** | [1.409, 1.520] |
| Ratio | 0.99 | **0.852** | [0.815, 0.966] |
| Bucket | SYMM-HIGH | SYMM-HIGH | |

Detected prefix families: `ch, qo, sh, ok, da`
Detected suffix families: `dy, in, ey, ol, ar`
Legacy asymmetric variant: prefix 1.384, ratio 0.939.

**Comparators — none reach SYMM-HIGH:**

| System | Prefix | Suffix | Ratio | Bucket |
| --- | --- | --- | --- | --- |
| Arabic | 1.41 | 0.82 | 1.72 | PREFIX-DOM |
| **VOYNICH** | **1.26** | **1.48** | **0.85** | **SYMM-HIGH** |
| Gibberish (shuffled) | 1.02 | 0.98 | 1.05 | SYMM-LOW |
| Swahili | 0.92 | 0.89 | 1.03 | SYMM-LOW |
| Georgian | 0.85 | 0.95 | 0.90 | SYMM-LOW |
| Estonian | 0.76 | 1.70 | 0.45 | SUFFIX-DOM |
| Finnish | 0.71 | 1.27 | 0.56 | SUFFIX-DOM |
| Italian | 0.68 | 0.89 | 0.77 | SYMM-LOW |
| N. Azerbaijani | 0.65 | 0.87 | 0.75 | SYMM-LOW |
| Latin | 0.64 | 2.03 | 0.31 | SUFFIX-DOM |
| Hungarian | 0.63 | 0.93 | 0.67 | SYMM-LOW |
| Turkish | 0.60 | 0.92 | 0.66 | SYMM-LOW |
| Ottoman Turkish | 0.60 | 0.99 | 0.60 | SYMM-LOW |
| Hebrew | 0.59 | 1.53 | 0.39 | SUFFIX-DOM |
| Tagalog | 0.54 | 0.61 | 0.88 | SYMM-LOW |
| Middle English | 0.46 | 0.57 | 0.81 | SYMM-LOW |
| KJV English | 0.35 | 0.22 | 1.60 | SYMM-LOW |

### 3.2 What this changes

**Holds.** Voynich is the only system in SYMM-HIGH and the only one with both
directions elevated above 1.1. Every clustering natural language tested is
suffix-dominant. The shuffled control is SYMM-LOW. The structural claim
reproduces from raw data.

**Three published numbers require correction:**

1. **Prefix SC 1.52 → 1.256.** Inflated by the hand-picked-family asymmetry;
   the legacy variant (1.384) recovers roughly half the gap, with the remainder
   attributable to method and corpus differences.
2. **Ratio 0.99 → 0.852**, CI [0.815, 0.966] — which **excludes 0.99**. "Both
   directions cluster equally" is not supported. Accurate statement: elevated
   clustering in both directions with a residual suffix lean — still unique
   among tested systems, but not symmetric.
3. **Arabic reclassifies** SUFFIX-DOM (0.72) → PREFIX-DOM (1.72). Retraction
   §3.2 ("Arabic is the closest match" — retired *because* Arabic is
   suffix-dominant) rests on a number the symmetric method does not reproduce.
   The conclusion may still hold; the stated reason does not.

**New caveat.** The ratio CI lower bound (0.815) sits 0.015 above the
SYMM-HIGH boundary (0.80). The bucket assignment is not robust — a modestly
different affix-detection parameterization could push Voynich into SUFFIX-DOM.
Report the underlying measurement (prefix 1.26 / suffix 1.48), not the category
label, and run a sensitivity sweep before submission.

### 3.3 Limitations of this run

- **Mandarin excluded.** Raw Latin-regex extraction over Chinese script yields
  only embedded romanized fragments (n ≈ 54K, prefix SC 3.54) and is not
  comparable. Requires jieba/pypinyin segmentation. The published Mandarin row
  (0.82/0.78) cannot be reproduced without a segmentation step absent from the
  pipeline.
- **Corpus sizes differ from the published table**, which used a 20K-sentence
  Leipzig cap; this run uses full corpora. Given retraction §3.3 (Estonian and
  Finnish were false positives at 10K sentences), corpus-size sensitivity is a
  known failure mode and any cap must be justified explicitly.
- **Comparator CIs not computed** in this run (runtime). Point estimates only;
  comparators sit far from the boundary, so not load-bearing, but complete
  before submission.

---

## 4. Prioritized remediation

Repair the instrument before expanding the comparator set. Collecting
genre-matched medieval corpora and feeding them into a pipeline that still
classifies tokens differently between scripts would waste the effort.

**4.1 Canonical tokenizer + classifier module.** One `scripts/_canonical.py`
imported by every script. Choose a family ordering, document why, rerun
everything. Expect the 2.625x to move. *(Blocks everything else.)*

**4.2 Compute the canonical transition matrix within-line**; report cross-line
separately.

**4.3 Replace reconstructed cascade counts** with the raw integers already in
`extended_analysis_results.json`; switch to two-tailed tests.

**4.4 Recompute multi-feature agreement** against a permutation null rather
than multiplied marginals.

**4.5 Delete the hardcoded ZL baseline** in `05_cross_transcription.py`;
compute it. Restate cross-transcription stability as EVA-mapped variants, not
independent transcriptions.

**4.6 Sensitivity sweep on the SYMM-HIGH bucket** (family count, coverage
bounds, affix length) — the 0.815 lower bound makes this mandatory.

**4.7 Matrix-wide multiple-comparisons correction** for the 6×6 transition
cells and suffix-agreement pairs, or explicit exploratory labelling in the
README as well as in `durable_findings`.

**4.8 Declare an equivalence margin** for the AIIN invariance claim, or stop
calling it invariance.

**4.9 Then** genre-matched medieval comparators (Trotula, Circa instans, Macer
Floridus, Bald's Leechbook), non-EVA character-boundary validation, and a tuned
adversarial constructed-system generator targeting items 5 and 7.

---

## 5. Note on presentation

The sentence *"encoded structured language is the only tested class that
satisfies all seven checklist items"* is scoped correctly in three places in
the repo, but its rhetorical shape is exactly what gets quoted out of context
as "science proves Voynich is a real language." Given how polluted this field's
signal-to-noise is — the same GitHub topic space contains claimed decipherments
at "99.8% confidence" — lead with the narrower framing the checklist scoring
table already supports.

Two further presentation notes:

- `results/prefix_suffix_analysis.json` should be regenerated and committed
  from code. When it is, `tests/test_canonical_values.py` will fail. That is
  correct behavior, and updating those canonical values is the moment the test
  suite begins to mean something.
- The AIIN function-word analogy is reported and then immediately undercut in
  the same paragraph (842 unique types, higher entropy than CHEDY — the
  opposite of function-word behavior). The undercut is what a skeptical reader
  remembers. Drop the analogy; the underlying finding (invariant frequency,
  non-self-clustering, selective pass-through) is interesting on its own.

---

## Appendix: files delivered

| File | Purpose |
| --- | --- |
| `scripts/10_prefix_suffix_analysis.py` | Generates the SYMM-HIGH table from raw data, symmetric method |
| `results/prefix_suffix_analysis_generated.json` | Output — written to a new path so it can be diffed against the committed artifact before overwriting |
| `docs/symm_high_regeneration_note.md` | Standalone note on the regeneration and number corrections |
| `docs/technical_audit_2026-07.md` | This document |
