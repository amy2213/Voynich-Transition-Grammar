# Section Effect Retired — and the Corrected Position

**Date:** 18 July 2026
**Test:** does the surviving section finding clear a contiguous-partition null?
**Answer: no.** The section effect should be retired alongside the quire result.

---

## 1. Result

Currier B only, language held constant throughout. Two disjoint contiguous page
blocks matching the real section page counts (biological: 20 pages, recipes_Q20:
23 pages), drawn 1,500 times.

| Cell | Test | Observed | Null mean | Null 2.5/97.5 | p |
| --- | --- | --- | --- | --- | --- |
| **AIIN→QOK** | difference | −0.335 | −0.015 | [−0.36, +0.41] | **0.137** |
| **AIIN→QOK** | biological value | 0.162 | 0.326 | [0.14, 0.68] | **0.426** |
| CHEDY→QOK | difference | −0.176 | −0.031 | [−0.45, +0.49] | 0.367 |
| CHEDY→QOK | biological value | 2.038 | 2.196 | [2.03, 2.59] | 0.126 |

**Nothing clears the null.** The observed AIIN→QOK difference of −0.335 sits
just inside the null's 2.5th percentile of −0.36. The biological section's
0.162x is well within the [0.14, 0.68] range that arbitrary contiguous
20-page blocks produce.

The negative control behaved correctly — CHEDY→QOK also fails to clear, as
expected, which means the null is not too permissive and the AIIN result is
interpretable rather than an artifact of a broken test.

---

## 2. Why the bootstrap said otherwise

Script 17's bootstrap gave AIIN→QOK a difference CI of [−0.48, −0.20],
excluding zero. That is not wrong — it answers the question *"given these two
particular groups, how stable is the difference?"* The answer is: quite stable.

But the question that matters is *"is a difference this large surprising for two
arbitrary contiguous blocks of this size?"* And the answer to that is no. The
manuscript is lumpy enough that a −0.335 difference in AIIN→QOK arises
routinely between arbitrary neighbouring page-blocks.

**This is the same error the audit originally flagged in the manuscript's own
work** — a heterogeneity claim resting on an interval that answers a narrower
question than the one being asked. I made it too, in the section analysis, and
it took the quire null to expose it.

---

## 3. Corrected position on section and quire structure

| Claim | Status |
| --- | --- |
| Structure varies by section (chi-square, 6/6 families) | **retired** — chi-square detects heterogeneity in any large partition |
| AIIN→QOK suppressed in biological section | **retired** — within contiguous-block null |
| QOK→QOK varies by section | **retired** — same reasoning, untested but no reason to expect different |
| Structure shifts at quire boundaries | **retired** — p = 0.42 against contiguous null |
| Structure varies by Currier language | **underpowered, unresolved** — large point estimates, wide CIs |

**There is currently no evidence that transition structure varies systematically
by section, by quire, or by any positional partition of the manuscript.**

What that supports is the opposite of what I suggested two steps ago: the
transition grammar looks **uniform across the manuscript**, at the resolution
this corpus can measure. Section differences appear to be lexical, not
structural.

---

## 4. What this does to the interpretation

Two steps ago I leaned toward a generative system with parameters drifting by
quire or topic. That reading is now unsupported from both directions — no quire
signal, no section signal.

The honest current picture:

**Holds.** A single uniform transition grammar operating throughout the
manuscript. CHEDY→QOK at 2.66x, stable across sections (2.04x–2.47x), scribal
hands, classifier policies, character-segmentation schemes, and surviving
Holm-Bonferroni across the full matrix. Bidirectional self-clustering unmatched
among 20 comparators including register-matched Latin.

**Does not hold.** Any claim that the MVE checklist discriminates encoded
language from a constructed system — a 40-line generator satisfies all seven
items. Any claim of positional structural variation.

**Unresolved.** The Currier A/B contrast, which is underpowered rather than
null, and which is now the only structural partition with any surviving signal.

On mechanism I would now say: the statistics describe a text with strong,
uniform, unusual internal structure, and they do not identify what produced it.
I was too quick to read a generative system into the section result, and the
control that would have caught it was one I hadn't run. Take my earlier
speculation with that in mind.

---

## 5. What is actually worth doing next

The Currier A/B contrast is the only live structural question. Script 17 found
QOK→QOK differing by +1.20 with CI [−0.01, +2.38] and CHEDY→QOK by −0.93 with
CI [−2.21, +0.31] between herbal_A/A and herbal_A/B — big effects, intervals
grazing zero, on only 304 lines of Currier B in that section.

Two ways to power it properly:

1. **Pool across sections.** Compare all Currier A against all Currier B with
   section as a covariate, rather than restricting to herbal_A. More data, at
   the cost of reintroducing the confound — but the confound can be modelled
   rather than avoided.
2. **Run the contiguous-block null on the language contrast**, exactly as done
   here. If Currier A/B clears a null that section and quire both fail, that is
   a genuinely interesting result: structure tracks scribal language and
   nothing else.

Option 2 is the same machinery as this script and would take about an hour. It
is the test I would run before writing anything about internal structure.

---

## Files

| File | Purpose |
| --- | --- |
| `scripts/19_section_effect_null.py` | contiguous-block null with negative control |
| `results/section_effect_null_results.json` | full output |
