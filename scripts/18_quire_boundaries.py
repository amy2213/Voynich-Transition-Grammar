#!/usr/bin/env python3
"""
18_quire_boundaries.py — Does transition structure shift at QUIRE boundaries?

THE DISCRIMINATING QUESTION
---------------------------
Script 17 established that transition structure varies by section with Currier
language held constant. That is compatible with two very different stories:

  PRODUCTION ARTIFACT   the scribe changed something on starting a new
                        gathering — different sitting, different exemplar,
                        different parameter setting. Structure would then
                        shift at QUIRE boundaries.

  CONTENT              the text is about different things in different
                        places, and the grammar follows the subject matter.
                        Structure would then shift at CONTENT boundaries,
                        cutting across quires where a topic runs on.

These make opposite predictions, and the corpus can test them because quire
boundaries and section boundaries do not coincide everywhere.

QUIRE ASSIGNMENT — PROVENANCE AND CAVEAT
----------------------------------------
The corpus carries page identifiers but no quire field, so quires are assigned
here from the published collation of Beinecke MS 408. The structure is
reasonably settled in the literature but NOT beyond dispute — quire 8 in
particular is contested, several folios are lost, and the foldouts complicate
the count.

This assignment is therefore an INPUT ASSUMPTION, not data. If it is wrong,
this test is wrong. It is stated explicitly below so it can be checked and
replaced.

THE CRITICAL CONTROL
--------------------
Any partition of a corpus into groups will show some heterogeneity, because
transition ratios are noisy on small samples. Reporting "quires differ" without
a null is meaningless.

So the observed quire-level heterogeneity is compared against a permutation
null: random CONTIGUOUS page groupings of the same sizes, drawn from the same
strata. If real quire boundaries produce more heterogeneity than arbitrary
contiguous boundaries, that is evidence the boundaries are structurally real.
If not, the section result from script 17 is better explained some other way.

Contiguity matters in the null — pages near each other are similar for many
reasons, and an i.i.d. page shuffle would make any grouping look significant.

USAGE
    python scripts/18_quire_boundaries.py
    python scripts/18_quire_boundaries.py --perms 500

OUTPUT
    results/quire_boundary_results.json
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _canonical import load_corpus, classify, FAMILY_NAMES  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
SEED = 42

# ─── Quire assignment (published collation, Beinecke MS 408) ─────────────────
# Inclusive folio ranges. Contested points are flagged in QUIRE_NOTES.
QUIRES = [
    ("Q1",  1,   8),
    ("Q2",  9,   16),
    ("Q3",  17,  24),
    ("Q4",  25,  32),
    ("Q5",  33,  40),
    ("Q6",  41,  48),
    ("Q7",  49,  56),
    ("Q8",  57,  66),
    ("Q9",  67,  68),
    ("Q10", 69,  70),
    ("Q11", 71,  72),
    ("Q12", 73,  74),
    ("Q13", 75,  84),
    ("Q14", 85,  86),
    ("Q15", 87,  90),
    ("Q16", 91,  92),
    ("Q17", 93,  96),
    ("Q18", 97,  102),
    ("Q19", 103, 108),
    ("Q20", 109, 116),
]

QUIRE_NOTES = (
    "Assignment from the published collation of Beinecke MS 408. Q8 (ff.57-66) "
    "is contested in the literature; Q12 is largely lost; the foldouts in "
    "Q9-Q11 and Q14 complicate the count. This is an input assumption, not "
    "data — if the collation is wrong, this test is wrong."
)

MIN_LINES = 60          # minimum lines for a group to be tested
KEY_CELLS = [("CHEDY", "QOK"), ("AIIN", "QOK"), ("QOK", "QOK"), ("OT", "OT")]


def folio_num(page):
    m = re.match(r"f(\d+)", page or "")
    return int(m.group(1)) if m else None


def quire_of(page):
    n = folio_num(page)
    if n is None:
        return None
    for name, lo, hi in QUIRES:
        if lo <= n <= hi:
            return name
    return None


def ratios(lines):
    tr = defaultdict(int)
    src, dst = Counter(), Counter()
    total = 0
    for l in lines:
        c = l["fam"]
        for i in range(len(c) - 1):
            tr[(c[i], c[i + 1])] += 1
            src[c[i]] += 1
            dst[c[i + 1]] += 1
            total += 1
    out = {}
    for s, d in KEY_CELLS:
        if total and src[s] and dst[d]:
            e = src[s] * (dst[d] / total)
            out[(s, d)] = tr[(s, d)] / e if e > 1 else None
        else:
            out[(s, d)] = None
    return out


def heterogeneity(groups):
    """Dispersion of key-cell ratios across groups.

    Statistic: mean coefficient of variation over cells that are estimable in
    at least three groups. Scale-free, so cells with different baselines
    contribute comparably.
    """
    per_cell = defaultdict(list)
    for g in groups:
        r = ratios(g)
        for c, v in r.items():
            if v:
                per_cell[c].append(v)
    cvs = []
    for c, vals in per_cell.items():
        if len(vals) >= 3:
            m = float(np.mean(vals))
            if m > 0:
                cvs.append(float(np.std(vals)) / m)
    return (float(np.mean(cvs)) if cvs else None), len(cvs)


def contiguous_partition(pages_sorted, sizes, rng):
    """Random contiguous partition of an ordered page list into given sizes."""
    order = list(sizes)
    rng.shuffle(order)
    out, i = [], 0
    for s in order:
        chunk = pages_sorted[i:i + s]
        if chunk:
            out.append(chunk)
        i += s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=400)
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    lines = load_corpus()
    for l in lines:
        l["fam"] = [classify(t) for t in l["tokens"]]
        l["quire"] = quire_of(l["page"])
        l["folio"] = folio_num(l["page"])

    print("=" * 78)
    print("QUIRE BOUNDARIES vs CONTENT BOUNDARIES")
    print("=" * 78)
    print(f"\n{QUIRE_NOTES}\n")

    # ── Which quires are testable ──
    byq = defaultdict(list)
    for l in lines:
        if l["quire"]:
            byq[l["quire"]].append(l)
    testable = {k: v for k, v in byq.items() if len(v) >= MIN_LINES}
    print(f"{'quire':<8}{'lines':>7}{'tokens':>8}{'sections':>28}{'currier':>10}")
    print("-" * 62)
    for q, _, _ in QUIRES:
        if q not in byq:
            continue
        ls = byq[q]
        secs = Counter(l["section"] for l in ls).most_common(2)
        cur = Counter(str(l["currier"])[:1] for l in ls).most_common(1)[0][0]
        ntok = sum(len(l["tokens"]) for l in ls)
        mark = "" if q in testable else "  (too few lines)"
        secstr = ",".join(f"{s}:{n}" for s, n in secs)
        print(f"{q:<8}{len(ls):>7}{ntok:>8}{secstr:>28}{cur:>10}{mark}")

    # ── TEST A: quire heterogeneity vs contiguous-partition null ──
    print("\n\nTEST A — do quire boundaries produce more heterogeneity than")
    print("         arbitrary contiguous page groupings of the same sizes?")
    print("-" * 78)
    groups = [testable[q] for q, _, _ in QUIRES if q in testable]
    obs, n_cells = heterogeneity(groups)
    sizes = [len({l["page"] for l in g}) for g in groups]
    print(f"Quires tested: {len(groups)}, cells contributing: {n_cells}")
    print(f"Observed heterogeneity (mean CV): {obs:.4f}")

    pages_sorted = sorted({l["page"] for l in lines},
                          key=lambda p: (folio_num(p) or 999, p))
    page_lines = defaultdict(list)
    for l in lines:
        page_lines[l["page"]].append(l)

    null = []
    for _ in range(args.perms):
        parts = contiguous_partition(pages_sorted, sizes, rng)
        gs = []
        for chunk in parts:
            g = [l for p in chunk for l in page_lines[p]]
            if len(g) >= MIN_LINES:
                gs.append(g)
        if len(gs) >= 3:
            h, _ = heterogeneity(gs)
            if h:
                null.append(h)
    if null:
        null = np.array(null)
        p_emp = float(((null >= obs).sum() + 1) / (len(null) + 1))
        print(f"Null (contiguous partitions, n={len(null)}): "
              f"mean {null.mean():.4f}, 95th pct {np.percentile(null,95):.4f}")
        print(f"Empirical p: {p_emp:.4f}")
        verdict_a = ("Quire boundaries produce MORE structural heterogeneity "
                     "than arbitrary contiguous groupings."
                     if p_emp < 0.05 else
                     "Quire boundaries do NOT produce more heterogeneity than "
                     "arbitrary contiguous groupings.")
    else:
        p_emp, verdict_a = None, "null could not be constructed"
    print(f"\n{verdict_a}")

    # ── TEST B: quire vs section, within one language ──
    print("\n\nTEST B — within Currier B, which partition explains more:")
    print("         quire or section?")
    print("-" * 78)
    b_lines = [l for l in lines if str(l["currier"])[:1] == "B"]
    byq_b = defaultdict(list)
    bys_b = defaultdict(list)
    for l in b_lines:
        if l["quire"]:
            byq_b[l["quire"]].append(l)
        bys_b[l["section"]].append(l)
    gq = [v for v in byq_b.values() if len(v) >= MIN_LINES]
    gs_ = [v for v in bys_b.values() if len(v) >= MIN_LINES]
    hq, nq = heterogeneity(gq)
    hs, nsx = heterogeneity(gs_)
    print(f"Quire partition   ({len(gq)} groups): mean CV {hq:.4f}"
          if hq else "quire: n/a")
    print(f"Section partition ({len(gs_)} groups): mean CV {hs:.4f}"
          if hs else "section: n/a")
    if hq and hs:
        verdict_b = ("QUIRE partition shows more heterogeneity — favours a "
                     "production artifact." if hq > hs else
                     "SECTION partition shows more heterogeneity — favours "
                     "content-driven variation.")
    else:
        verdict_b = "insufficient data"
    print(f"\n{verdict_b}")

    # ── TEST C: within-section, across-quire ──
    print("\n\nTEST C — within a single section AND language, do quires differ?")
    print("         (the cleanest production-artifact signal)")
    print("-" * 78)
    testc = {}
    for sec in ["herbal_A", "recipes_Q20", "biological"]:
        for cur in ["A", "B"]:
            sub = [l for l in lines
                   if l["section"] == sec and str(l["currier"])[:1] == cur]
            byq_s = defaultdict(list)
            for l in sub:
                if l["quire"]:
                    byq_s[l["quire"]].append(l)
            gs2 = [v for v in byq_s.values() if len(v) >= MIN_LINES]
            if len(gs2) >= 3:
                h, nc = heterogeneity(gs2)
                if h:
                    key = f"{sec}/{cur}"
                    testc[key] = {"n_quires": len(gs2), "mean_cv": round(h, 4),
                                  "cells": nc}
                    print(f"  {key:<18} {len(gs2)} quires, mean CV {h:.4f}")
                    for g in gs2:
                        q = g[0]["quire"]
                        r = ratios(g)
                        cq = r[("CHEDY", "QOK")]
                        aq = r[("AIIN", "QOK")]
                        print(f"      {q:<6} lines={len(g):<5} "
                              f"CHEDY→QOK={cq if cq else float('nan'):.2f}x  "
                              f"AIIN→QOK={aq if aq else float('nan'):.2f}x")
    if not testc:
        print("  No section/language stratum spans 3+ testable quires.")

    out = {
        "description": ("Tests whether transition structure shifts at quire "
                        "(production) boundaries or content boundaries."),
        "quire_assignment": [{"quire": q, "folio_from": a, "folio_to": b}
                             for q, a, b in QUIRES],
        "quire_assignment_caveat": QUIRE_NOTES,
        "seed": SEED,
        "n_permutations": args.perms,
        "test_a_quire_vs_contiguous_null": {
            "observed_mean_cv": obs,
            "null_mean": float(null.mean()) if len(null) else None,
            "null_95th": float(np.percentile(null, 95)) if len(null) else None,
            "empirical_p": p_emp,
            "verdict": verdict_a,
        },
        "test_b_quire_vs_section": {
            "quire_mean_cv": hq, "n_quire_groups": len(gq),
            "section_mean_cv": hs, "n_section_groups": len(gs_),
            "verdict": verdict_b,
        },
        "test_c_within_section_across_quire": testc,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "quire_boundary_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
