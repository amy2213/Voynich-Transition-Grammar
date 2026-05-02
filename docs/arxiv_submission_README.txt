arXiv submission bundle: Voynich Transition Grammar
====================================================

Files
-----
main.tex        LaTeX source (article class, pdflatex).
references.bib  BibTeX bibliography.
main.bbl        Pre-built bibliography (arXiv builds against this
                if bibtex is not invoked).
figures/        Three PDF figures (prefix/suffix scatter, AIIN
                density, transition matrix).

Build
-----
pdflatex main
bibtex   main
pdflatex main
pdflatex main

Or:   latexmk -pdf main

Output: main.pdf, 19 pages.

Version notes
-------------
This is a substantially revised version of the paper. Changes from the
earlier public draft:

- "Productive morphology" interpretation retracted (Finding 1.8).
  A character-trigram null model produces comparable or higher
  log-freq vs edit-1 variant-count correlations than Voynich;
  Chaucer at the same measurement produces r=0.20, below both
  Voynich and the null. The "standard property of natural-language
  morphology" claim is not supported and is withdrawn. The edit-
  distance graph structure observation is retained as descriptive.

- Minimum Viable Explanation checklist reduced from 8 items to 7
  (the retracted productive-paradigms item is removed).

- A first-pass synthetic constructed-system control (new §3.11)
  satisfies 5 of 7 checklist items by direct design. The earlier
  "only compatible class" conclusion in §5 is withdrawn. The
  discriminative power of the checklist now rests on items 5
  (bidirectional SYMM-HIGH) and 7 (71%+ hapax) specifically.

- Per-scribe decomposition added. CHEDY→QOK is concentrated in
  Hands 2 and 3 (94% of corpus is written in Hands 1–3, but the
  transition rule is primarily a Hand 2/3 property). The
  bidirectional SYMM-HIGH profile holds independently in each of
  Hands 1, 2, and 3, confirming it is not an aggregation artifact.

- Agreement cascades (§3.8) are reported with Wilson-score 95%
  confidence intervals and Benjamini–Hochberg FDR correction.
  All five chains survive FDR at α=0.05; the flagship +81pp effect
  has conservative CI [+48, +94]pp on n=13 agreement trials.

- Table 4 "all z = 3.4–5.0" misstatement corrected; OT→OT at z=1.9
  is now flagged borderline rather than claimed significant.

- Limitations expanded from 9 to 11 items. Partial-reproducibility
  caveat removed (all findings now scripted as 01–09 in
  scripts/; 33 regression tests pass).

Reproducibility
---------------
All numerical values in this paper are produced by scripts available
at https://github.com/amy2213/Voynich-Transition-Grammar and are
covered by 33 regression tests that run on every commit. See the
paper's §8 and the repository's docs/durable_findings.md for details.

No decipherment is claimed.
