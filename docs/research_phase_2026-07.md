# Research Phase — Adversarial Control, Boundary Validation, Genre Comparators

**Date:** 18 July 2026
**Scope:** the three post-audit research items.
**Headline:** one result substantially weakens the manuscript's central
conclusion. Two strengthen it.

---

## 1. Adversarial constructed control — the manuscript's central argument does not hold

### The claim under test

`durable_findings.md` §4 established that the first-pass constructed control
(`09_constructed_control.py`) satisfied 5 of 7 MVE items by direct design, and
drew the right conclusion: items 1–4 and 6 are cheaply engineered, so **items 5
and 7 are the only ones doing discriminating work**. It also stated the correct
open question:

> "A tuned generator targeting items 5 and 7 specifically has not been
> attempted. Until it is tested and shown to fail, the constructed-system
> hypothesis cannot be excluded."

`scripts/14_adversarial_control.py` attempts it, deliberately adversarially —
written to make the claim fail, by someone who knows exactly which statistics
the pipeline computes.

### Mechanism

Neither target required anything sophisticated.

**Item 5 (bidirectional SYMM-HIGH).** Emit tokens as PREFIX + STEM + SUFFIX and
run *two independent Markov chains* over adjacent tokens — one on prefix
identity, one on suffix identity — each with a tunable self-transition
probability. Prefix SC and suffix SC become direct functions of those two
probabilities. The ratio is tuned by adjusting them relative to each other.

Natural languages fail item 5 because affixation is overwhelmingly
one-directional: suffixing languages cluster on suffixes and their word-initial
material is near-random with respect to the previous token. A constructed
system is under no such constraint. **Two independent chains is the whole
trick.**

**Item 7 (open vocabulary).** A large heavy-tailed stem inventory, so that
prefix × stem × suffix yields mostly-unique tokens at corpus size. The
first-pass generator failed only because its stem inventory was too small.

No linguistic content of any kind is involved.

### Result

| | Generated | Manuscript |
| --- | --- | --- |
| Prefix SC | 1.721 | 1.256 |
| Suffix SC | 1.942 | 1.475 |
| Ratio | 0.886 | 0.852 |
| Bucket | **SYMM-HIGH** | SYMM-HIGH |
| Hapax | 66.6% | 71.4% |
| TTR | 0.199 | 0.230 |
| Types | 6,308 | — |

**ITEM 5: PASS. ITEM 7: PASS.**

Item 5 passed on the *first attempt*, at every one of 60+ parameter
configurations tested — including configurations that overshoot the
manuscript badly (prefix SC 4.16, suffix SC 3.35). It was never close to
failing. Item 7 required only reducing the stem inventory from 8,000 to 1,500
and steepening the Zipf exponent to 1.4.

### What this means

**All 7 MVE checklist items are engineerable by a constructed system.** The
checklist does not discriminate encoded natural language from a sufficiently
motivated constructed system.

This does not make the manuscript a hoax, and it does not touch the descriptive
findings — the transition structure is measured and real regardless of what
produced it. What it removes is the *inferential* step. The sentence

> "encoded structured language is the only tested class that satisfies all
> seven checklist items"

is no longer true, and should be retired rather than narrowed.

**Recommended replacement framing:** the manuscript exhibits a statistical
profile — elevated bidirectional affix self-clustering, class-specific
transition attraction, line-bounded reset — that is unmatched among tested
natural languages. That profile constrains the space of generating mechanisms
but does not identify one, and it is reproducible by a deliberately tuned
constructed system.

**Honest caveat in the other direction.** The generator overshoots the
manuscript's *magnitudes*: the lowest SC values reachable while still passing
both items were 1.72/1.94, against the manuscript's 1.26/1.48. Below roughly
p_stay = 0.14 the chains approach randomness and item 5 fails. So the
manuscript sits in a *lower*, more moderate region of the SYMM-HIGH band than
this generator naturally produces. That is a real observation and worth
reporting, but it is a weak defence — it is a matter of tuning, not of
principle, and it should not be presented as rescuing the argument.

### Record change

`durable_findings.md` §4 and §3.7, plus the checklist scoring table: the
"Constructed (tested)" column becomes **Y** for items 5 and 7. Every item is
now Y. The revised conclusion in §4 must be rewritten.

---

## 2. Non-EVA boundary validation — findings survive, and this one is earned

### The objection

Every family definition is stated in EVA characters. EVA is a modern
transliteration convention; where one character ends and the next begins is an
editorial decision. The cross-transcription test (script 05) does **not**
address this — all four alternative transcriptions are Stolfi-mapped into EVA,
so they vary *word* boundaries while holding *character* boundaries fixed.

`scripts/15_boundary_validation.py` varies character boundaries instead.

### First attempt was vacuous — worth recording

Four schemes (`eva_standard`, `atomic`, `maximal`, `gallows_split`) returned
byte-identical results: 2.659x, 615 observations. The reason is that `qok`,
`ok`, `ot`, `chedy` and `aiin` are all expressible as whole-unit sequences
under every one of them, so boundary alignment is always satisfiable. That is
informative but it is not a test, and reporting it as one would have been
misleading.

Three adversarial schemes were added, each positing a ligature that
deliberately *straddles* a family pattern so that tokens matching as ASCII
substrings fail to match at unit boundaries.

### Results

| Scheme | CHEDY→QOK | obs | AIIN→QOK | QOK family n |
| --- | --- | --- | --- | --- |
| eva_standard | 2.659x | 615 | 0.444x | 2,799 |
| atomic | 2.659x | 615 | 0.444x | 2,799 |
| maximal | 2.659x | 615 | 0.444x | 2,799 |
| gallows_split | 2.659x | 615 | 0.444x | 2,799 |
| currier_like | 2.491x | 767 | 0.481x | 3,815 |
| **straddle_A** | **2.324x** | 237 | 0.496x | **1,235** |
| straddle_B | 2.657x | 616 | 0.445x | 2,799 |
| straddle_C | 2.526x | 470 | 0.437x | 2,258 |

CHEDY→QOK range **2.324x–2.659x**. AIIN→QOK range **0.437x–0.496x**.

**The strongest single result:** `straddle_A` posits `kai`/`tai`/`kee`/`ked` as
ligatures, which destroys **56% of the QOK family** (2,799 → 1,235 tokens) and
cuts observed CHEDY→QOK pairs from 615 to 237. The attraction still measures
**2.324x**. An artifact of EVA segmentation would not survive that.

**Verdict:** both transition findings are boundary-robust. This is a real
robustness result and it addresses an objection the cross-transcription test
was previously being credited with answering but did not.

---

## 3. Genre- and period-matched comparators — narrowed, not closed

### The confound

All 16 existing comparators are modern Wikipedia prose plus two English
literary texts. The manuscript's visible register is herbal, pharmaceutical and
recipe-like: short repetitive entries, heavy nominal repetition, formulaic
construction. Self-clustering measures whether adjacent tokens share affix
families, and a recipe list plausibly clusters differently from encyclopedia
prose *regardless of language*.

### Results

| System | n | Prefix SC | Suffix SC | Ratio | Hapax | Bucket |
| --- | --- | --- | --- | --- | --- | --- |
| **VOYNICH** | 31,608 | **1.26** | **1.48** | **0.85** | 71.4% | **SYMM-HIGH** |
| Pliny, *Naturalis Historia* | 67,914 | 0.63 | 1.37 | 0.46 | 68.8% | SUFFIX-DOM |
| Medieval Latin prose | 81,499 | 0.62 | 1.32 | 0.47 | 61.5% | SUFFIX-DOM |
| Middle English (Chaucer) | 217,642 | 0.46 | 0.57 | 0.81 | 48.7% | SYMM-LOW |
| KJV English | 400,000 | 0.35 | 0.22 | 1.60 | 34.0% | SYMM-LOW |

No comparator reaches SYMM-HIGH.

Pliny is the useful addition: it is the naturalist/herbal register itself and
the direct textual ancestor of the medieval herbal tradition the manuscript's
illustrations belong to. It sits firmly SUFFIX-DOM at 0.46 — nowhere near the
Voynich profile — despite a hapax rate (68.8%) close to the manuscript's
(71.4%). **Register alone does not produce the SYMM-HIGH profile**, which is
the specific thing this test needed to establish.

### The gap that remains — do not overstate this result

These are register-**adjacent**, not register-**matched**. The genuinely
genre-matched corpus is the medieval herbal and pharmacological tradition:

- the *Trotula* (Green's edition)
- *Circa instans* (Platearius)
- Macer Floridus, *De viribus herbarum*
- *Herbarium* of Pseudo-Apuleius
- Bald's *Leechbook* (Cockayne, *Leechdoms Wortcunning and Starcraft*)

**None is available as freely fetchable plaintext.** They exist in scholarly
editions requiring manual extraction or institutional access (Corpus Corporum,
dMGH, and the printed editions above).

Also note the Pliny fetch retrieved only 6 of 37 books before rate-limiting,
so that corpus is a partial sample.

This step narrows the register confound. It does not close it. Sourcing those
texts by hand remains genuinely outstanding, and a reviewer is entitled to
raise it.

---

## 4. Net assessment

| Item | Direction | Weight |
| --- | --- | --- |
| Adversarial control passes items 5 and 7 | **against** | **major** |
| Findings survive non-EVA character boundaries | for | moderate |
| No genre-adjacent comparator reaches SYMM-HIGH | for | moderate |

The descriptive work is in better shape than before: the transition findings
now survive multiple-comparisons correction at FWER, classifier-policy
variation, line-boundary correction, and character-boundary variation. Those
are measurements and they hold.

The inferential claim is in worse shape. The MVE checklist was the argument
connecting those measurements to "encoded structured language," and a
motivated constructed system now satisfies all seven items. The right response
is to lead with the measurements and retire the inference, not to defend the
checklist.

That is a narrower paper. It is also one that will survive contact with a
hostile reviewer, which the current version would not — the two-independent-
chains construction is not difficult to think of, and it is better to publish
it yourself than to have it published about you.

---

## 5. Files

| File | Purpose |
| --- | --- |
| `scripts/14_adversarial_control.py` | tuned constructed system targeting items 5 and 7 |
| `scripts/15_boundary_validation.py` | eight character-segmentation schemes, three adversarial |
| `scripts/16_genre_comparators.py` | genre/period-adjacent corpora, with fetcher |
| `results/adversarial_control_results.json` | |
| `results/boundary_validation_results.json` | |
| `results/genre_comparators_results.json` | |
| `data/raw/genre_matched/*.txt` | cached downloads |
