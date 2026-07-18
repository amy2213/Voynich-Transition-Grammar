# Section vs Language: Where Does Transition Structure Vary?

**Date:** 18 July 2026
**Question:** does the manuscript's transition grammar differ between sections
(suggesting different rule-sets per topic — a production process) or between
Currier languages (suggesting scribal/dialectal variation), or neither?

**Answer:** structure varies by **section**, with Currier language held
constant. That is the result that discriminates, and it favours a
generative-system reading.

---

## 1. The confound and how it was broken

Section and Currier language are heavily confounded — `herbal_A` is mostly
Currier A, `biological` and `recipes_Q20` are Currier B. A naive
section-by-section comparison measures language, not section.

The corpus contains the cell needed to separate them:

| Section | Currier | Lines | Tokens |
| --- | --- | --- | --- |
| herbal_A | A | 1,149 | 7,006 |
| **herbal_A** | **B** | **304** | **2,689** |
| biological | B | 917 | 6,898 |
| recipes_Q20 | B | 1,084 | 10,890 |

`herbal_A` contains substantial text in *both* languages. That supports two
orthogonal contrasts:

- **TEST 1 — section effect**, Currier B only: herbal_A vs biological vs
  recipes_Q20. Any difference is section, not language.
- **TEST 2 — language effect**, herbal_A only: Currier A vs Currier B. Any
  difference is language, not section.

---

## 2. Point estimates

**TEST 1 — section effect (Currier B throughout)**

| Stratum | Lines | Tokens | CHEDY→QOK | AIIN→QOK | QOK→QOK |
| --- | --- | --- | --- | --- | --- |
| herbal_A/B | 304 | 2,689 | 2.47x | 0.59x | 1.05x |
| biological/B | 917 | 6,898 | 2.04x | **0.16x** | 0.98x |
| recipes_Q20/B | 1,084 | 10,890 | 2.21x | 0.50x | **1.46x** |

**TEST 2 — language effect (herbal_A throughout)**

| Stratum | Lines | Tokens | CHEDY→QOK | AIIN→QOK | QOK→QOK |
| --- | --- | --- | --- | --- | --- |
| herbal_A/A | 1,149 | 7,006 | 1.57x | 1.05x | 2.43x |
| herbal_A/B | 304 | 2,689 | 2.47x | 0.59x | 1.05x |

---

## 3. Chi-square homogeneity of transition rows

| Source family | TEST 1 (section) | TEST 2 (language) |
| --- | --- | --- |
| QOK | χ²=74.5, p<0.0001 | χ²=25.5, p=0.0001 |
| OK | χ²=61.3, p<0.0001 | χ²=16.2, p=0.0062 |
| OT | χ²=44.4, p<0.0001 | χ²=5.0, p=0.417 |
| CHEDY | χ²=71.4, p<0.0001 | χ²=25.9, p=0.0001 |
| AIIN | χ²=62.1, p<0.0001 | χ²=77.7, p<0.0001 |
| OTHER | χ²=283.8, p<0.0001 | χ²=142.2, p<0.0001 |

**Section effect: 6/6 source families heterogeneous, surviving BH-FDR.**
**Language effect: 5/6 source families heterogeneous, surviving BH-FDR.**

Both factors matter. Section matters for every family; language spares OT.

---

## 4. Bootstrap on key cells (120 iterations, resampling whole lines)

| Contrast | Comparison | Cell | Δratio | 95% CI | ≠0 |
| --- | --- | --- | --- | --- | --- |
| SECTION | herbal_A/B vs biological/B | CHEDY→QOK | +0.45 | [−0.16, +1.20] | n |
| SECTION | herbal_A/B vs biological/B | **AIIN→QOK** | **+0.42** | **[+0.08, +0.78]** | **Y** |
| SECTION | herbal_A/B vs biological/B | QOK→QOK | +0.07 | [−0.54, +0.62] | n |
| SECTION | herbal_A/B vs recipes_Q20/B | CHEDY→QOK | +0.27 | [−0.35, +0.88] | n |
| SECTION | herbal_A/B vs recipes_Q20/B | AIIN→QOK | +0.09 | [−0.24, +0.45] | n |
| SECTION | herbal_A/B vs recipes_Q20/B | QOK→QOK | −0.36 | [−0.91, +0.31] | n |
| SECTION | biological/B vs recipes_Q20/B | CHEDY→QOK | −0.18 | [−0.46, +0.09] | n |
| SECTION | biological/B vs recipes_Q20/B | **AIIN→QOK** | **−0.34** | **[−0.48, −0.20]** | **Y** |
| SECTION | biological/B vs recipes_Q20/B | **QOK→QOK** | **−0.49** | **[−0.71, −0.30]** | **Y** |
| LANGUAGE | herbal_A/A vs herbal_A/B | CHEDY→QOK | −0.93 | [−2.21, +0.31] | n |
| LANGUAGE | herbal_A/A vs herbal_A/B | AIIN→QOK | +0.50 | [−0.05, +1.00] | n |
| LANGUAGE | herbal_A/A vs herbal_A/B | QOK→QOK | +1.20 | [−0.01, +2.38] | n |

**SECTION: 3 of 9 contrasts exclude zero. LANGUAGE: 0 of 3.**

The language contrasts have large point estimates (QOK→QOK +1.20,
CHEDY→QOK −0.93) but wide intervals — herbal_A/B has only 304 lines. Two of
three sit right at the boundary ([−0.01, +2.38] and [−0.05, +1.00]). **These
are underpowered, not null.** With more Currier B text in herbal_A they would
likely separate. Do not report "language has no effect" — report that the
contrast is underpowered while the section contrast is not.

---

## 5. Interpretation

**The strongest single result: AIIN→QOK repulsion varies by section under
constant language.** It measures 0.59x in herbal_A/B, 0.16x in biological/B,
0.50x in recipes_Q20/B — with the biological/recipes difference at
[−0.48, −0.20], comfortably excluding zero. The biological section suppresses
AIIN→QOK roughly three times harder than the other two.

**QOK→QOK self-clustering also varies by section**: 1.46x in recipes_Q20
against 0.98x in biological, CI [−0.71, −0.30].

Meanwhile CHEDY→QOK — the headline finding — shows **no** section contrast
excluding zero. It measures 2.04x–2.47x across all three Currier B strata. The
principal attraction is stable across sections; what varies is the *secondary*
structure around it.

### What this favours

A single uniform grammar operating throughout would predict section-invariant
transition structure. That is not what is observed: 6/6 families show
heterogeneity, and two key cells shift with CIs excluding zero, with language
held constant.

The pattern — a stable primary attraction plus section-varying secondary
constraints — is what you would expect if a shared underlying procedure were
being applied with locally different parameters. That is more consistent with a
**generative system whose settings drift by quire or topic** than with encoded
natural-language content, where one would expect section differences to be
lexical rather than structural.

It is **not** decisive. Two honest caveats:

1. Register variation in a genuine text could plausibly produce structural
   differences too — a recipe list and a descriptive passage differ
   grammatically in real languages. This test cannot separate "different
   rule-set" from "different register within one grammar."
2. Section boundaries here are derived from folio number ranges, not from the
   imagery. If those ranges misclassify pages, some heterogeneity is noise.

### Relation to the adversarial result

This finding sits alongside the adversarial-control result, not against it. The
constructed generator satisfies all seven MVE items *and* would naturally
produce section-varying structure if its parameters were changed partway
through. The two results point the same direction.

---

## 6. Recommended next test

The strongest discriminator available on existing data: **do the section
boundaries that maximise transition-structure heterogeneity coincide with the
quire boundaries, or with the illustration-content boundaries?**

If structure shifts at quire boundaries, that is a production artifact — the
scribe changed something when starting a new gathering. If it shifts at content
boundaries, that is evidence for content. The corpus has page identifiers, so
quire assignment is derivable; this is a few hours' work and it is a sharper
test than anything currently in the pipeline.

---

## Files

| File | Purpose |
| --- | --- |
| `scripts/17_section_transition_structure.py` | full test: strata, chi-square homogeneity, bootstrap |
| `scripts/17b_section_bootstrap.py` | faster standalone bootstrap (120 iterations) |
| `results/section_transition_structure.json` | chi-square and design output |
| `results/section_bootstrap.json` | bootstrap contrasts |
