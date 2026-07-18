# Quire Boundaries — Null Result, and a Correction to Script 17

**Date:** 18 July 2026
**Test:** does transition structure shift at quire (production) boundaries?
**Answer: no.** And the control that establishes this also undercuts part of
what I told you about the section result. That correction is in §4.

---

## 1. Design

Quire assignment is not in the corpus, so it was derived from the published
collation of Beinecke MS 408 and is an **input assumption, not data**. Q8
(ff.57–66) is contested, Q12 is largely lost, and the foldouts in Q9–Q11 and
Q14 complicate the count. If the collation is wrong, this test is wrong.

Testable quires after the ≥60-line threshold:

| Quire | Lines | Tokens | Section | Currier |
| --- | --- | --- | --- | --- |
| Q1–Q7 | 150–254 each | ~1,000–1,650 | herbal_A | A |
| Q8 | 206 | 1,537 | other/text_f58 | B |
| Q13 | 917 | 6,898 | biological | B |
| Q15, Q17, Q18 | 89–183 | 472–1,000 | herbal_B | A |
| Q19 | 561 | 5,588 | recipes_Q20 | B |
| Q20 | 524 | 5,304 | recipes_Q20 | B |

---

## 2. The control that matters

Any partition of a corpus into groups shows heterogeneity, because transition
ratios are noisy on small samples. "Quires differ" means nothing without a
null.

Observed quire-level heterogeneity was therefore compared against **random
contiguous page groupings of the same sizes**. Contiguity is essential — pages
near each other are similar for many reasons, and an i.i.d. page shuffle would
make any grouping look significant.

**TEST A result:**

| | Mean CV |
| --- | --- |
| Observed (real quire boundaries) | 0.4202 |
| Null, contiguous partitions (n=300) | 0.4108 |
| Null 95th percentile | 0.4721 |
| **Empirical p** | **0.4219** |

**Quire boundaries produce no more structural heterogeneity than arbitrary
contiguous page groupings.** The observed value sits almost exactly at the null
mean.

---

## 3. Supporting tests

**TEST B — within Currier B, quire vs section partition:**

| Partition | Groups | Mean CV |
| --- | --- | --- |
| Quire | 6 | 0.3484 |
| Section | 4 | 0.3403 |

The script prints "QUIRE shows more heterogeneity," but **ignore that verdict**
— the difference is 0.008, far inside noise, and Test A shows neither partition
beats a random contiguous one. The script's threshold logic is too crude here;
I have left the output as-is rather than quietly tuning it after seeing the
result.

**TEST C — within herbal_A, Currier A only, across 7 quires:**

| Quire | Lines | CHEDY→QOK | AIIN→QOK |
| --- | --- | --- | --- |
| Q1 | 227 | n/a | 1.43x |
| Q2 | 150 | n/a | 1.31x |
| Q3 | 219 | 2.82x | 1.16x |
| Q4 | 128 | n/a | 0.78x |
| Q5 | 107 | n/a | 1.56x |
| Q6 | 110 | n/a | 0.61x |
| Q7 | 208 | 2.21x | 0.77x |

Mean CV 0.2868 — *lower* than the corpus-wide figure, i.e. quires within a
single section and language are, if anything, more similar to each other than
groups elsewhere.

Note that CHEDY→QOK is unestimable in 5 of 7 quires: at 100–230 lines per quire
the CHEDY and QOK families do not co-occur often enough to compute a stable
ratio. **This test is underpowered for the headline cell**, and that limitation
is structural, not fixable by more permutations.

---

## 4. Correction: I overstated the section result

The contiguous-partition null used here should have been applied in script 17,
and was not. Applying it retrospectively changes how that result reads.

What script 17 actually established:

- **Chi-square homogeneity, 6/6 families, p<0.0001.** With ~7,000–11,000 tokens
  per stratum, chi-square will detect heterogeneity in essentially any real
  corpus partition. This is a weak result and I presented it as a strong one.
- **Bootstrap CIs excluding zero on 3 of 9 section contrasts.** This is the
  meaningful part and it stands — particularly AIIN→QOK in biological/B (0.16x)
  against recipes_Q20/B (0.50x), CI [−0.48, −0.20].

So the honest position: **specific transition cells do differ between specific
sections, with language held constant.** But the general claim that "structure
varies by section" was not tested against the right null, and when a null of
that kind is applied at quire level it does not clear it.

I should have run the permutation control before drawing the inference. That's
on me, and it is the same class of error the original audit flagged in the
manuscript — a heterogeneity claim without a null.

---

## 5. What this means for the interpretation

The production-artifact reading I offered after script 17 is **not supported**.
Structure does not shift at gathering boundaries. If a scribe changed parameters
between sittings, this test should have detected it and did not.

That leaves three live possibilities, and this test does not separate them:

1. **Localised structural variation exists but is not organised by quire.** The
   biological-section AIIN→QOK suppression is real (CI excludes zero) but does
   not align with production units.
2. **The variation is register-driven** — a genuine text about different
   subjects, whose grammar shifts with content. Consistent with the surviving
   bootstrap contrasts.
3. **The variation is noise at the level the corpus can resolve.** Several
   strata are small, and CHEDY→QOK is unestimable in most quires.

Net effect on the overall picture: **this weakens my earlier lean toward a
generative system.** The adversarial-control result still stands — the MVE
checklist does not discriminate — but that is an argument about what the
checklist can prove, not evidence for a constructed origin. Absent a quire
signal, I would now describe the mechanism question as genuinely open rather
than leaning either way.

---

## 6. What would actually settle it

The limiting factor is statistical power per production unit, not method.
Quires of 100–250 lines cannot support a stable CHEDY→QOK estimate.

Two options that would work:

1. **Bifolio- or hand-level analysis instead of quire-level.** Script 08 already
   shows per-scribe decomposition works and is stable; extending that to
   interact hand with position in gathering would use the same data more
   efficiently.
2. **Test the specific finding that survived** — AIIN→QOK suppression in the
   biological section — against the contiguous-partition null directly. If that
   one cell clears the null, it is a real localised effect worth reporting. If
   it does not, the section result should be retired too.

Option 2 is a couple of hours and should be done before any of this is written
up. I would not put the section result in a paper until it has passed the same
control that quires just failed.

---

## Files

| File | Purpose |
| --- | --- |
| `scripts/18_quire_boundaries.py` | quire assignment, permutation null, three tests |
| `results/quire_boundary_results.json` | full output including quire mapping |
