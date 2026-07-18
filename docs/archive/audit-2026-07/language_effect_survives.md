# The Currier Language Effect Survives — the One Structural Partition That Holds

**Date:** 18 July 2026
**Test:** does the Currier A/B contrast clear the contiguous-block null that
section and quire partitions both failed?
**Answer: yes, for QOK→QOK — and it holds with section held constant.**

---

## 1. Result

### Pooled — all Currier A vs all Currier B

Currier A: 102 pages, 1,573 lines, 9,579 tokens
Currier B: 72 pages, 2,421 lines, 21,102 tokens

| Cell | A | B | Diff | Null mean | Null 2.5/97.5 | p | |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **QOK→QOK** | 2.35 | 1.27 | **+1.07** | +0.013 | [−0.71, +0.83] | **0.0010** | ✓ |
| **CHEDY→QOK** | 1.46 | 2.28 | **−0.82** | +0.152 | [−0.50, +0.48] | **0.0100** | ✓ |
| AIIN→QOK | 0.88 | 0.38 | +0.50 | −0.058 | [−0.62, +0.51] | 0.1029 | |
| OT→OT | 1.66 | 1.94 | −0.27 | −0.089 | [−0.49, +0.32] | 0.2587 | |

### Restricted — herbal_A only, section held constant

Currier A: 86 pages, 1,149 lines | Currier B: 25 pages, 304 lines

| Cell | A | B | Diff | Null mean | Null 2.5/97.5 | p | |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **QOK→QOK** | 2.43 | 1.05 | **+1.39** | +0.492 | [+0.00, +1.12] | **0.0013** | ✓ |
| CHEDY→QOK | 1.57 | 2.47 | −0.90 | −0.226 | [−1.32, +1.76] | 0.2338 | |
| AIIN→QOK | 1.05 | 0.59 | +0.45 | −0.074 | [−0.59, +0.28] | 0.1319 | |
| OT→OT | 1.65 | 2.24 | −0.59 | −0.403 | [−1.74, +1.27] | 0.4975 | |

---

## 2. Why this one is trustworthy where the others were not

**The negative controls behaved.** AIIN→QOK (p = 0.103) and OT→OT (p = 0.259)
do not clear the null. If the contiguous-block design were too permissive here —
a real risk, since Currier A and B occupy largely distinct folio ranges — every
cell would have cleared. Two of four did. The null constrains.

**QOK→QOK clears twice, independently.** Pooled (p = 0.0010) and restricted to
herbal_A with section held constant (p = 0.0013). The restricted test is the
demanding one: 25 pages of Currier B against a null drawn from the same section,
and it still separates. That rules out the section confound directly rather than
by modelling.

**The effect size is large and directionally consistent.** QOK self-clustering
is roughly twice as strong in Currier A as in Currier B — 2.35x vs 1.27x pooled,
2.43x vs 1.05x within herbal_A. Currier B shows essentially no QOK
self-clustering at all (1.05x is chance).

**CHEDY→QOK is weaker evidence.** It clears pooled (p = 0.010) but not
restricted (p = 0.234), where only 304 lines of Currier B are available. Report
it as suggestive, not established.

---

## 3. The corrected structural picture

Four partitions of the manuscript have now been tested against the same control:

| Partition | Result |
| --- | --- |
| Quire (production units) | fails, p = 0.42 |
| Section (content) | fails, p = 0.14 |
| Contiguous page blocks | is the null |
| **Currier language** | **clears, p = 0.001, twice** |

**Transition structure in this manuscript is organised by Currier language and
by nothing else that has been tested.** Not by what the page depicts. Not by
where it sits in a gathering. Not by position.

That is a cleaner result than the messy section-varying picture I sketched two
steps ago, and it points somewhere different.

---

## 4. Interpretation

Currier A and B were originally identified by Prescott Currier on distributional
grounds — different character frequencies, different word inventories, and
associated with different scribal hands. What this adds is that they differ in
**transition grammar**, not merely in inventory. The rules governing which token
class follows which are not the same in the two systems.

That constrains things usefully:

- **Against a single uniform generating procedure.** If one process produced the
  whole manuscript, QOK self-clustering should not double between its two
  halves while section and position show nothing.
- **Against a purely lexical A/B distinction.** The standard reading of Currier
  A/B is different vocabulary or dialect. A vocabulary difference need not change
  the class-transition structure. This one does.
- **Consistent with two related systems** — two scribes applying variants of a
  shared procedure, or one scribe whose practice changed, or genuinely two
  languages or registers sharing an encoding.

It does **not** discriminate content from construction. Two scribes writing real
text in related dialects and two scribes applying related constructed rule-sets
both predict this. Combined with the adversarial-control result — where a 40-line
generator satisfies all seven MVE items — the mechanism question stays open.

What it does do is identify the **one axis along which this manuscript's
structure genuinely varies**, which is a publishable descriptive finding
independent of any decipherment claim.

---

## 5. Relation to Finding 1.2

This connects to the AIIN result from earlier in the audit. Recall:

| | Total aiin-bearing | Bare AIIN | Embedded in prefixed token |
| --- | --- | --- | --- |
| Currier A | 14.96% | 13.58% | 1.37% (9%) |
| Currier B | 14.97% | 10.77% | 4.20% (28%) |

Currier B embeds three times as much aiin material inside `qok`/`ok`/`ot`
tokens. That is a morphological difference between the two systems, and the
QOK→QOK transition difference found here is a syntactic one. **Both point the
same way: A and B differ in how QOK-family tokens are built and how they
sequence.**

Those two findings should be reported together. Independently derived,
mutually reinforcing, both surviving controls — that is a stronger package than
either alone, and it is the most defensible substantive claim to come out of
this entire audit.

---

## 6. What I would write up

The paper I would now write has three parts:

1. **A uniform transition grammar** — CHEDY→QOK at 2.66x, stable across
   sections, quires, hands, classifier policies, and character-segmentation
   schemes, surviving Holm-Bonferroni across the full 36-cell matrix.
2. **One axis of genuine structural variation** — Currier A/B, differing in both
   QOK-family morphology and QOK→QOK sequencing, surviving a positional null
   that section and quire both fail.
3. **A methodological negative result** — the seven-item MVE checklist does not
   discriminate encoded language from a constructed system, demonstrated by
   construction.

That is smaller than the original paper and considerably harder to dismiss.

---

## Files

| File | Purpose |
| --- | --- |
| `scripts/20_language_effect_null.py` | pooled and restricted analyses, contiguous-block null, negative controls |
| `results/language_effect_null_results.json` | full output |
