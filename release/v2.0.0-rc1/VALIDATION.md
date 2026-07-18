# Release-candidate validation

Candidate: `2.0.0-rc1`  
Validation date: 2026-07-18

## Preprint source

Executed from a fresh temporary directory populated only by extracting the
candidate ZIP:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Result:

- build exit status: 0;
- pages: 8;
- page size: A4, 595.276 by 841.89 points;
- final LaTeX warnings: 0;
- undefined-reference occurrences: 0;
- overfull-box occurrences: 0.

The extracted text of the independent build matches `docs/paper.pdf` exactly.
Rasterization of both PDFs at 96 DPI produced eight pixel-identical page
pairs. Byte identity is not required because PDF build metadata can differ.

## Bundle integrity

The ZIP contains exactly five files:

```text
README.txt
figures/prefix_suffix_v2.pdf
main.bbl
main.tex
references.bib
```

The bundle SHA-256 is:

```text
b297cc44cdb5719aca6fb41c59464e780005ecfc690511cc67e0198872b7572a
```

File-level hashes are recorded in `manifest.json` and `SHA256SUMS`. Release
tests reopen the ZIP and independently recompute the bundle and PDF hashes.

## Repository validation

Executed:

```text
python run_all.py
```

Result:

- dataset validation: passed;
- canonical within-line analysis: passed;
- classifier-overlap generation: passed;
- 200-replicate prefix/suffix estimator: passed;
- pytest: 37 collected, 37 passed, 0 failures, 0 errors, 0 skips,
  0 warnings;
- direct Python execution: 37 collected, 37 passed;
- fresh-output checks: passed;
- complete run manifest: true.

This proves that the frozen inputs were accepted, the listed canonical outputs
were freshly regenerated, the locked result assertions held, boundary and
ambiguity invariants remained satisfied, and the release bundle passed its
inventory and hash tests. It does not prove that the statistical models are
the only defensible models, that transition events are independent, or that
the findings generalize beyond the declared transcription, corpora, and
methods.

## Metadata validation

`CITATION.cff` was parsed as YAML, its declared CFF version was checked, and
its release version was matched to `VERSION`. It was then validated with
Draft 7 JSON Schema semantics against the official CFF 1.2.0 `schema.json`.
The schema was obtained from the `citation-file-format/citation-file-format`
repository at validation time and had SHA-256:

```text
0b8d22140da702d766df318dcff3a91af2f39521298dcf36d76315fd99cc169b
```

Result: valid, with zero schema violations.
