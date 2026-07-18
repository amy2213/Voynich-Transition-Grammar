# Finding 1.2 Recomputed — AIIN "Invariance" Splits By Definition

**Date:** 18 July 2026
**Trigger:** the canonical classifier migration shrank the AIIN family by 25%.
Finding 1.2 needed recomputation to establish what it now describes.
**Outcome:** the invariance result holds under one definition of AIIN and fails
under the other. Which definition the paper means is not currently stated.

---

## 1. The two definitions

The pipeline has been using two different things under the name AIIN:

- **Substring predicate** — `is_aiin(t)`: the token *contains* "aiin" or "ain".
  This is what `01_core_analysis.py` uses for the invariance test (it calls
  `is_aiin` directly, bypassing `classify`).
- **Family assignment** — `classify(t) == "AIIN"`: the token's canonical family
  is AIIN, meaning it contains the string *and* is not claimed first by a
  prefix family. `qokaiin` is QOK, not AIIN.

Every other finding in the paper uses the second. Finding 1.2 uses the first.
That inconsistency was invisible while the two produced similar numbers.

---

## 2. Page-level Currier A vs B — the result flips

| Definition | Currier A | Currier B | KS p | Bootstrap 95% CI on difference | Verdict |
| --- | --- | --- | --- | --- | --- |
| Substring predicate | 14.96% | 14.97% | 0.742 | [−1.88, +1.94] pp | **INVARIANT** |
| Canonical family | 13.58% | 10.77% | **0.003** | **[+1.18, +4.49] pp** | **DIFFERENT** |

n = 102 Currier A pages, 72 Currier B pages, ≥20 tokens each.

Per-line unit gives the same split (substring: no difference; family: KS
p < 0.001, CI [+1.26, +3.11] pp), so this is not a unit-of-analysis artifact.

**The AIIN family is not invariant across the Currier languages.** Only the raw
string occurrence is.

---

## 3. What is actually invariant, and why it is interesting

Decomposing the aiin-bearing tokens by page:

| | Total aiin-bearing | Bare AIIN tokens | Embedded in a prefixed token | Share embedded |
| --- | --- | --- | --- | --- |
| Currier A | 14.96% | 13.58% | 1.37% | **9%** |
| Currier B | 14.97% | 10.77% | 4.20% | **28%** |

The two languages use the aiin string at an almost identical overall rate —
14.96% vs 14.97%, which is a striking agreement — but distribute it very
differently. Currier B embeds three times as much of it inside `qok`/`ok`/`ot`-
prefixed tokens.

This is a better finding than the one it replaces. "Total aiin material is
conserved across the Currier languages while its morphological placement
shifts" is a specific, falsifiable structural claim. "AIIN density is
invariant" was true only because the two effects cancel.

It also connects to the existing Currier A/B literature in a way the original
framing did not: A/B differences are usually described in terms of token
inventory and affix frequency, and this is a quantified instance of exactly
that, discovered rather than assumed.

---

## 4. Type counts — the 842 figure

| | Canonical family | `aiin_first` (published) |
| --- | --- | --- |
| AIIN tokens | 3,584 (11.3%) | 4,755 (15.0%) |
| **AIIN unique types** | **737** | **842** |
| AIIN entropy | 6.58 bits | 6.61 bits |
| CHEDY tokens | 2,693 | 2,681 |
| CHEDY unique types | 353 | 342 |
| CHEDY entropy | 5.35 bits | 5.32 bits |

**The published 842-unique-types figure is the `aiin_first` number.** Under the
canonical classifier it is 737.

The point that figure was making survives unchanged and is if anything
sharpened: AIIN carries 737 types at 6.58 bits against CHEDY's 353 types at
5.35 bits. AIIN remains far more diverse and higher-entropy than CHEDY under
either definition — still the opposite of function-word behaviour.

---

## 5. Record changes required

1. **`durable_findings.md` §1.2 and MVE item 3** — the invariance claim must be
   restated. Recommended wording: *total aiin-string density is invariant
   across Currier A and B (14.96% vs 14.97%, KS p = 0.742), but the AIIN
   token family is not (13.58% vs 10.77%, KS p = 0.003); Currier B embeds 28%
   of its aiin material inside prefixed tokens against Currier A's 9%.*
2. **Replace 842 with 737**, or state explicitly that the figure uses the
   `aiin_first` policy.
3. **`01_core_analysis.py`** — the invariance block calls `is_aiin` directly
   while the rest of the script uses `classify`. Decide which is intended and
   make it explicit in code; if both are wanted, compute and report both.
4. **MVE checklist** — if item 3 rests on AIIN family invariance, it does not
   currently pass. If it rests on aiin-string invariance, it passes and should
   say so.

---

## 6. Assessment

This is the largest single correction of the audit, and it is not a number
change — it is a claim that does not survive in the form it was stated.

It is also recoverable, and the replacement is stronger. A conserved total with
a shifted morphological distribution is a more specific structural result than
a flat density, and it is the kind of finding that is hard to produce by
accident. I would lead with it rather than bury it in a retraction entry.

The failure mode this exposes is worth noting for its own sake: two definitions
of the same family were live in one codebase, and the discrepancy was invisible
because they happened to produce similar aggregate numbers. That is exactly
what the canonical module exists to prevent, and it only surfaced because the
module forced the two into contact.
