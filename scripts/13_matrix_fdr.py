#!/usr/bin/env python3
"""
13_matrix_fdr.py — Matrix-wide multiple-comparisons correction

WHAT THIS ADDRESSES
-------------------
CHEDY->QOK (2.659x) and AIIN->QOK (0.444x) are presented as headline findings.
Both are cells selected from a 6x6 transition matrix — 36 cells — on the basis
of being the most extreme. `durable_findings.md` §5.5 correctly labels the
matrix exploratory, but the README and abstract present these two cells as
results, and no correction was ever applied across the family of tests they
were drawn from.

Selecting the largest of 36 effects and then reporting its uncorrected p-value
is the textbook multiple-comparisons error. The effects here are large enough
that they very likely survive correction — but "likely survives" is an
assertion, and this script turns it into a demonstration. The same applies to
the ~10 suffix-agreement pairs in Finding 1.5.

METHOD
------
Two test families, corrected separately (they answer different questions, so
pooling them would be over-conservative):

  FAMILY A — transition matrix, 36 cells (6 source x 6 destination classes).
    Per cell: observed count vs expectation under independence
    (row_total * col_total / grand_total), tested with a two-tailed
    chi-square goodness-of-fit on the 2x2 collapse
    [[obs, row-obs], [col-obs, rest]]. Fisher's exact is used where any
    expected cell falls below 5.

  FAMILY B — suffix agreement, one test per family pair.
    Two-proportion z-test, two-tailed, observed agreement vs the
    within-pair shuffled expectation already computed in
    04_extended_analysis.py.

Both families get Benjamini-Hochberg FDR at alpha=0.05, and Holm-Bonferroni
(FWER) reported alongside. BH is the appropriate primary correction for
exploratory screening; Holm is included because a reviewer will ask, and
surviving FWER is a stronger statement worth making if the effects clear it.

USAGE
    python scripts/13_matrix_fdr.py

OUTPUT
    results/matrix_fdr_results.json
"""

import json
import os
import sys
from collections import Counter

import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, norm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _canonical import (  # noqa: E402
    load_corpus, classify_all, transitions, FAMILY_NAMES,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
ALPHA = 0.05


# ─── Corrections ─────────────────────────────────────────────────────────────
def benjamini_hochberg(pvals, alpha=ALPHA):
    """Return (rejected_flags, critical_value_used). Standard BH step-up."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    rejected = [False] * n
    crit = 0.0
    kmax = -1
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= alpha * rank / n:
            kmax = rank
            crit = alpha * rank / n
    if kmax > 0:
        for rank, i in enumerate(order, start=1):
            if rank <= kmax:
                rejected[i] = True
    return rejected, crit


def holm_bonferroni(pvals, alpha=ALPHA):
    """Holm step-down FWER control."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    rejected = [False] * n
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= alpha / (n - rank + 1):
            rejected[i] = True
        else:
            break
    return rejected


# ─── Family A: transition matrix ─────────────────────────────────────────────
def cell_test(obs, row_total, col_total, grand_total):
    """Two-tailed test for one matrix cell against independence.

    Collapses the matrix to 2x2 (this cell vs everything else on each margin),
    which is the correct unit: the question is whether THIS transition is
    enriched, not whether the whole matrix is non-independent.
    """
    a = obs
    b = row_total - obs
    c = col_total - obs
    d = grand_total - row_total - col_total + obs
    if min(a, b, c, d) < 0:
        return None, None, None
    table = [[a, b], [c, d]]
    expected = row_total * col_total / grand_total if grand_total else 0
    try:
        if min(a, b, c, d) < 5:
            _, p = fisher_exact(table)
        else:
            _, p, _, _ = chi2_contingency(table, correction=True)
    except Exception:
        return None, expected, None
    ratio = obs / expected if expected > 0 else None
    return p, expected, ratio


def main():
    lines = load_corpus()
    t = transitions(lines, within_line=True)
    tr, src, dst, total = t["tr"], t["src"], t["dst"], t["total"]

    print("=" * 78)
    print("MATRIX-WIDE MULTIPLE-COMPARISONS CORRECTION")
    print("=" * 78)
    print(f"Corpus: {len(lines)} lines, {total} within-line transitions\n")

    # ── Family A ──
    cells = []
    for s in FAMILY_NAMES:
        for d_ in FAMILY_NAMES:
            obs = tr.get((s, d_), 0)
            if src[s] == 0 or dst[d_] == 0:
                continue
            p, exp, ratio = cell_test(obs, src[s], dst[d_], total)
            if p is None:
                continue
            cells.append({"source": s, "dest": d_, "obs": obs,
                          "expected": round(exp, 2),
                          "ratio": round(ratio, 3) if ratio else None,
                          "p_raw": p})

    praw = [c["p_raw"] for c in cells]
    bh, crit = benjamini_hochberg(praw)
    holm = holm_bonferroni(praw)
    for c, b, h in zip(cells, bh, holm):
        c["survives_bh_fdr"] = bool(b)
        c["survives_holm_fwer"] = bool(h)
        c["p_raw"] = float(f"{c['p_raw']:.3e}")

    print(f"FAMILY A — transition matrix: {len(cells)} cells tested "
          f"(6x6 minus empty margins)")
    print(f"BH critical value at alpha={ALPHA}: {crit:.5f}\n")
    print(f"{'cell':<18}{'obs':>7}{'exp':>9}{'ratio':>8}{'p_raw':>12}{'BH':>5}{'Holm':>6}")
    print("-" * 68)
    for c in sorted(cells, key=lambda x: x["p_raw"]):
        if c["survives_bh_fdr"] or c["ratio"] and (c["ratio"] > 1.5 or c["ratio"] < 0.7):
            tag = f"{c['source']}→{c['dest']}"
            print(f"{tag:<18}{c['obs']:>7}{c['expected']:>9.1f}{c['ratio']:>8.3f}"
                  f"{c['p_raw']:>12.2e}{'Y' if c['survives_bh_fdr'] else 'n':>5}"
                  f"{'Y' if c['survives_holm_fwer'] else 'n':>6}")

    n_bh = sum(c["survives_bh_fdr"] for c in cells)
    n_holm = sum(c["survives_holm_fwer"] for c in cells)
    print(f"\nSurviving BH-FDR:      {n_bh}/{len(cells)}")
    print(f"Surviving Holm-FWER:   {n_holm}/{len(cells)}")

    headline = {}
    for pair in [("CHEDY", "QOK"), ("AIIN", "QOK")]:
        m = next((c for c in cells
                  if c["source"] == pair[0] and c["dest"] == pair[1]), None)
        if m:
            headline[f"{pair[0]}->{pair[1]}"] = m
            print(f"\nHEADLINE {pair[0]}→{pair[1]}: ratio {m['ratio']}, "
                  f"p={m['p_raw']:.2e}, BH={'PASS' if m['survives_bh_fdr'] else 'FAIL'}, "
                  f"Holm={'PASS' if m['survives_holm_fwer'] else 'FAIL'}")

    # ── Family B: suffix agreement ──
    ext_path = os.path.join(RESULTS_DIR, "extended_analysis_results.json")
    family_b = []
    if os.path.exists(ext_path):
        ext = json.load(open(ext_path))
        sa = ext.get("1.5_suffix_agreement", {})
        for k, v in sa.items():
            if not isinstance(v, dict) or "z_score" not in v:
                continue
            z = v["z_score"]
            family_b.append({"pair": k, "z": z,
                             "agreement_ratio": v.get("agreement_ratio"),
                             "n_pairs": v.get("n_pairs"),
                             "p_raw": 2.0 * norm.sf(abs(z))})
    if family_b:
        pb = [x["p_raw"] for x in family_b]
        bhb, critb = benjamini_hochberg(pb)
        holmb = holm_bonferroni(pb)
        for x, b, h in zip(family_b, bhb, holmb):
            x["survives_bh_fdr"] = bool(b)
            x["survives_holm_fwer"] = bool(h)
            x["p_raw"] = float(f"{x['p_raw']:.3e}")
        print(f"\n\nFAMILY B — suffix agreement: {len(family_b)} pairs tested")
        print(f"BH critical value: {critb:.5f}\n")
        print(f"{'pair':<16}{'ratio':>8}{'z':>7}{'n':>7}{'p_raw':>12}{'BH':>5}{'Holm':>6}")
        print("-" * 61)
        for x in sorted(family_b, key=lambda r: r["p_raw"]):
            _r = x['agreement_ratio'] if x['agreement_ratio'] is not None else float('nan')
            _n = x['n_pairs'] if x['n_pairs'] is not None else 0
            print(f"{x['pair']:<16}{_r:>8.2f}{x['z']:>7}"
                  f"{_n:>7}{x['p_raw']:>12.2e}"
                  f"{'Y' if x['survives_bh_fdr'] else 'n':>5}"
                  f"{'Y' if x['survives_holm_fwer'] else 'n':>6}")
        print(f"\nSurviving BH-FDR:    {sum(x['survives_bh_fdr'] for x in family_b)}/{len(family_b)}")
        print(f"Surviving Holm-FWER: {sum(x['survives_holm_fwer'] for x in family_b)}/{len(family_b)}")
    else:
        print("\n! extended_analysis_results.json not found — Family B skipped")

    out = {
        "description": ("Multiple-comparisons correction across the full "
                        "transition matrix and the suffix-agreement pair set. "
                        "Addresses the fact that headline cells were selected "
                        "as the most extreme of 36 without correction across "
                        "the family they were drawn from."),
        "alpha": ALPHA,
        "family_a_transition_matrix": {
            "n_tests": len(cells),
            "bh_critical_value": crit,
            "n_surviving_bh_fdr": n_bh,
            "n_surviving_holm_fwer": n_holm,
            "headline_cells": headline,
            "cells": cells,
        },
        "family_b_suffix_agreement": {
            "n_tests": len(family_b),
            "n_surviving_bh_fdr": sum(x["survives_bh_fdr"] for x in family_b),
            "n_surviving_holm_fwer": sum(x["survives_holm_fwer"] for x in family_b),
            "pairs": family_b,
        } if family_b else None,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "matrix_fdr_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
