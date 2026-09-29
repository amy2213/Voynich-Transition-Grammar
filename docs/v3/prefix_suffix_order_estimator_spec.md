# Version 3 composition-controlled affix-order estimator specification

Status: research candidate  
Estimator version: `3.0.0-dev`  
Opened: 2026-09-29

## Purpose

Version 3 measures whether the ordering of automatically discovered prefix and
suffix classes contributes self-transition structure beyond what is expected
from each natural unit's own class composition.

It is a replacement for the reopened Version 2 cross-corpus prefix/suffix
comparison. It does not modify or supersede frozen Version 2 artifacts until a
Version 3 release is explicitly approved.

## Natural sequence units

- Voynich: Zandbergen-Landini lines.
- Leipzig corpora: Leipzig sentence records.
- Gutenberg corpora: sentence-like segments after header/footer removal.
- CoNLL-U: blank-line-delimited sentences using alphabetic surface forms.

No transition crosses a natural sequence-unit boundary.

## Comparator token policy

Comparator alphabetic words of length 1 are retained. Version 2 discarded them,
which could manufacture adjacency between their former neighbors.

Voynich continues to use the canonical frozen transcription tokenizer. Any
future change to Voynich transcription-token normalization is a separate
sensitivity analysis and must not be silently folded into this estimator.

## Affix discovery

For every system and sample:

- candidate lengths: 2 and 3 code points;
- candidate coverage: 2% through 20%, inclusive;
- maximum families per side: 5;
- candidate pool: 80 most frequent candidates;
- deterministic descending-frequency selection with lexical tie-breaking;
- same-side nesting is prohibited;
- prefix nesting is tested with prefix logic;
- suffix nesting is tested with suffix logic;
- first matching selected family receives the token; unmatched tokens are
  assigned to `OTHER`.

The Version 2 suffix bug remains available only as an explicit legacy mode for
exact historical reproduction.

## Primary composition-controlled order statistic

After affix assignment, consider a class c in one natural unit containing n
tokens, k of which belong to c.

Under a uniformly random permutation of that unit's fixed class multiset, the
exact expected number of adjacent c->c transitions is:

```
k(k - 1) / n
```

The expectation is summed across units.

For each supported class:

```
order_ratio(c) =
    observed within-unit c->c transitions
    /
    exact within-unit permutation expectation
```

A value:

- > 1 indicates order-driven self-clustering relative to fixed unit
  composition;
- = 1 indicates no net order contribution;
- < 1 indicates order-driven anti-clustering.

The primary side score is the aggregate observed self-transition count divided
by the aggregate composition-conditioned expectation across supported
discovered classes. This weights classes by their null self-transition
exposure and avoids giving a rare class the same leverage as a common class.

The unweighted mean of class-specific ratios is retained as a sensitivity
diagnostic, not the primary cross-system statistic. `OTHER` is excluded from
the primary score.

This statistic conditions directly on unit composition and therefore cannot be
inflated solely because different lines or sentences contain different affix
mixtures.

## Full-corpus estimate and size-matched sensitivity

The primary descriptive estimate is calculated on each system's complete
available corpus.

A secondary matched-size sensitivity repeatedly samples natural units without
replacement for every system using the same algorithm. The common target is
90% of the smallest available system corpus so the smallest system also has
resampling headroom. If the final unit would exceed the target, a single
contiguous fragment supplies the remainder and remains an independent unit.

This matched-size distribution is a robustness diagnostic. Replicate indices
across systems have no linguistic pairing.

## Inference

Version 3 does not create a cross-system p-value by pairing independent
replicate indices.

Initial reporting is descriptive:

- full-corpus prefix and suffix order ratios;
- matched-size medians and percentile intervals;
- discovered-family identities and supported-class counts.

Any future hypothesis test must define its null and sampling unit separately
and pass an explicit review gate before publication.

## Acceptance tests

At minimum:

1. suffix discovery cannot select nested suffixes such as `dy/edy` or
   `in/iin`;
2. a corpus made of compositionally pure units scores exactly 1.0 regardless of
   global heterogeneity;
3. a deliberately alternating class sequence scores below 1.0;
4. one-character comparator words survive tokenization;
5. no adjacency is created across natural-unit or sampling boundaries;
6. the frozen `v2.0.0` tag remains unchanged.

## Claim gate

No new Voynich-vs-language claim is supported merely because the Version 3
code runs successfully. The observed Version 3 results must be generated,
audited, and interpreted before any scientific conclusion is promoted from
candidate status.
