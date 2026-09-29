# Version 3 composition-controlled affix-order estimator specification

Status: pre-freeze correction candidate; external review incorporated  
Estimator version: `3.0.0`  
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
- Leipzig corpora: boundary-safe fragments within Leipzig sentence records.
- Gutenberg corpora: boundary-safe fragments within sentence-like segments
  after header/footer removal.
- CoNLL-U: boundary-safe fragments within blank-line-delimited sentences.

No transition crosses a natural sequence-unit boundary or an excluded lexical
item. If a whitespace item is dropped or would split into multiple accepted
word runs, that item terminates the current comparator sequence.

## Comparator token policy

Comparator alphabetic words of length 1 are retained. Version 2 discarded them,
which could manufacture adjacency between their former neighbors.

Comparator tokenization is also boundary-safe. A whitespace item is accepted
only when it contains exactly one target-alphabet run and any surrounding
characters are punctuation. Numeric items, foreign-script gaps, mixed-content
items, and orthographic forms that split into multiple target-alphabet runs
terminate the current sequence. Their surviving neighbors are never joined.

Voynich continues to use the canonical frozen transcription tokenizer. The
cleaned parquet contains no whitespace items dropped by that tokenizer in the
canonical corpus, so no parallel seam correction is required there.

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

## Full-corpus estimate and robustness analyses

The primary descriptive effect-size estimate is calculated on each system's
complete available corpus.

Three robustness analyses are required.

### Line/sentence deletion stability

Voynich plus every sufficiently large comparator except Ottoman Turkish is
sampled without replacement to 90% of the canonical Voynich token count. This
analysis answers whether the result is stable to deleting roughly 10% of the
available natural units. For Voynich, the resulting replicates overlap heavily
and therefore **must not** be presented as cluster-aware uncertainty.

### Voynich page-block bootstrap

Voynich receives a separate page-block bootstrap at the same token target.
Pages are sampled with replacement while the lines nested inside each sampled
page remain separate sequence units. This is the cluster-aware robustness
summary used when discussing whether the Voynich prefix/minimum side is
distinguishable from the neutral value 1.0.

### All-system small-target sensitivity

A third sensitivity includes Ottoman Turkish and every other system. Its target
is 90% of the smallest available system token count and uses without-replacement
natural-unit sampling. It remains a sample-size sensitivity rather than a
population confidence procedure.

For without-replacement analyses, if the final unit would exceed the target,
one contiguous fragment supplies the remaining tokens and remains a separate
unit.

All replicate distributions are robustness diagnostics. Replicate indices
across systems have no linguistic pairing and must not be used as paired
observations.

## Inference

Version 3 does not create a cross-system p-value by pairing independent
replicate indices.

Initial reporting is descriptive:

- full-corpus prefix and suffix order ratios;
- 200-replicate line/sentence deletion-stability summaries;
- 200-replicate Voynich page-block bootstrap summaries;
- 200-replicate all-system small-target summaries;
- within-system fractions below or at/above the neutral order ratio of 1.0;
- discovered-family identities and supported-class counts;
- comparator tokenization break diagnostics;
- an exact-adjacent-repeat robustness check for Voynich;
- the unweighted mean of class-specific ratios as a sensitivity diagnostic.

The line-deletion Voynich interval and its fraction above 1.0 are not headline
uncertainty statements. Neutrality claims for Voynich must use the page-block
bootstrap.

No cross-system replicate-index pairing is permitted.

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
5. `word 123 word` cannot create a word-to-word seam;
6. a foreign-script gap cannot create a seam;
7. a split orthographic form such as `l'arte` cannot create a seam;
8. punctuation-wrapped single words remain valid tokens;
9. no adjacency is created across natural-unit or sampling boundaries;
10. Voynich page-block sampling preserves nested line boundaries;
11. the 90% line/sentence analysis is labeled deletion stability, not
    cluster-aware uncertainty;
12. the all-system sensitivity target is based on 90% of the smallest corpus;
13. no cross-system paired p-value is produced;
14. the frozen `v2.0.0` tag remains unchanged.

## Claim gate

No new Voynich-vs-language claim is supported merely because the Version 3
code runs successfully. The observed Version 3 results must be generated,
audited, and interpreted before any scientific conclusion is promoted from
candidate status.
