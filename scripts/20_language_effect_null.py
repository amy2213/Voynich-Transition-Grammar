#!/usr/bin/env python3
"""
20_language_effect_null.py — Does the Currier A/B contrast clear the null?

WHERE THIS SITS
---------------
Section (script 19) and quire (script 18) partitions both failed a
contiguous-page-block null. The Currier A/B language contrast is the only
structural partition with surviving signal, and it has never been tested
against the same control.

Script 17 found, within herbal_A (section held constant):

    QOK->QOK    Currier A 2.43x, Currier B 1.05x    diff +1.20  CI [-0.01, +2.38]
    CHEDY->QOK  Currier A 1.57x, Currier B 2.47x    diff -0.93  CI [-2.21, +0.31]

Large effects, intervals grazing zero, on only 304 lines of Currier B in that
section. Underpowered rather than null. This script powers it two ways and
applies the same control that section and quire failed.

TWO ANALYSES
------------
  POOLED    All Currier A against all Currier B, ignoring section. Maximises
            power at the cost of reintroducing the section confound — but the
            confound is then handled by the null rather than by restriction
            (see below).

  RESTRICTED  herbal_A only, both languages. Section held constant, low power.
            Reported for comparison, not as the primary test.

THE NULL, AND WHY IT HANDLES THE CONFOUND
-----------------------------------------
Currier A and B are largely positional — A dominates early folios, B later. So
a naive "A differs from B" finding could just be "early folios differ from late
folios," which is exactly the kind of positional variation that section and
quire turned out NOT to have.

The null therefore draws two contiguous page blocks matching the real A and B
page counts, from the whole corpus ordered by folio. If the A/B difference is
merely positional, arbitrary contiguous blocks of the same sizes will reproduce
it. If A/B exceeds that null while section and quire did not, the difference
tracks something about the language classification specifically, not position.

NEGATIVE CONTROLS
-----------------
Two cells that script 17 did NOT flag as differing by language are included
(OT->OT, and CHEDY->QOK in the pooled analysis where no prior claim was made).
If everything clears the null, the null is too permissive and nothing is
interpretable. The controls are what make the result readable.

USAGE
    python scripts/20_language_effect_null.py --perms 1500

OUTPUT
    results/language_effect_null_results.json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _canonical import load_corpus, classify  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
SEED = 42
CELLS = [("QOK", "QOK"), ("CHEDY", "QOK"), ("AIIN", "QOK"), ("OT", "OT")]


def folio_num(p):
    m = re.match(r"f(\d+)", p or "")
    return int(m.group(1)) if m else 999


def ratio_of(lines, s, d):
    tr = src = dst = total = 0
    for l in lines:
        c = l["fam"]
        for i in range(len(c) - 1):
            total += 1
            if c[i] == s:
                src += 1
            if c[i + 1] == d:
                dst += 1
            if c[i] == s and c[i + 1] == d:
                tr += 1
    if not total or not src or not dst:
        return None
    exp = src * (dst / total)
    return tr / exp if exp > 1 else None


def run_null(pages, page_lines, n1, n2, perms, rng):
    """Contiguous two-block null over an ordered page list."""
    out = {c: [] for c in CELLS}
    if len(pages) < n1 + n2:
        return out
    for _ in range(perms):
        blk1 = blk2 = None
        for _ in range(40):
            i = int(rng.integers(0, len(pages) - n1 + 1))
            blk1 = pages[i:i + n1]
            rest = pages[:i] + pages[i + n1:]
            if len(rest) < n2:
                continue
            j = int(rng.integers(0, len(rest) - n2 + 1))
            blk2 = rest[j:j + n2]
            break
        if not blk1 or not blk2:
            continue
        l1 = [l for p in blk1 for l in page_lines[p]]
        l2 = [l for p in blk2 for l in page_lines[p]]
        for c in CELLS:
            r1, r2 = ratio_of(l1, *c), ratio_of(l2, *c)
            if r1 and r2:
                out[c].append(r1 - r2)
    return out


def report(name, ga, gb, pages, page_lines, perms, rng):
    na = len({l["page"] for l in ga})
    nb = len({l["page"] for l in gb})
    print(f"\n{'='*78}\n{name}\n{'='*78}")
    print(f"Currier A: {na} pages, {len(ga)} lines, "
          f"{sum(len(l['tokens']) for l in ga)} tokens")
    print(f"Currier B: {nb} pages, {len(gb)} lines, "
          f"{sum(len(l['tokens']) for l in gb)} tokens")

    null = run_null(pages, page_lines, na, nb, perms, rng)

    print(f"\n{'cell':<14}{'A':>8}{'B':>8}{'diff':>9}{'null mean':>11}"
          f"{'null 2.5/97.5':>22}{'p':>9}{'':>4}")
    print("-" * 78)
    res = {}
    for c in CELLS:
        s, d = c
        ra, rb = ratio_of(ga, *c), ratio_of(gb, *c)
        if ra is None or rb is None:
            continue
        diff = ra - rb
        arr = np.array(null[c])
        if len(arr) < 50:
            continue
        p = float((np.abs(arr) >= abs(diff)).sum() + 1) / (len(arr) + 1)
        lo, hi = np.percentile(arr, [2.5, 97.5])
        flag = "***" if p < 0.05 else ""
        print(f"{s+'→'+d:<14}{ra:>8.2f}{rb:>8.2f}{diff:>+9.2f}"
              f"{arr.mean():>+11.3f}{f'[{lo:+.2f}, {hi:+.2f}]':>22}"
              f"{p:>9.4f}{flag:>4}")
        res[f"{s}->{d}"] = {
            "currier_a": round(ra, 3), "currier_b": round(rb, 3),
            "diff": round(diff, 3), "null_mean": round(float(arr.mean()), 3),
            "null_ci": [round(float(lo), 3), round(float(hi), 3)],
            "p_empirical": round(p, 4), "n_null": len(arr),
            "clears_null": bool(p < 0.05)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=1500)
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    lines = load_corpus()
    for l in lines:
        l["fam"] = [classify(t) for t in l["tokens"]]
        l["cur"] = str(l["currier"])[:1]

    all_pages = sorted({l["page"] for l in lines},
                       key=lambda p: (folio_num(p), p))
    page_lines = defaultdict(list)
    for l in lines:
        page_lines[l["page"]].append(l)

    print("=" * 78)
    print("DOES THE CURRIER A/B CONTRAST CLEAR A CONTIGUOUS-BLOCK NULL?")
    print("=" * 78)
    print("\nSection and quire partitions both FAILED this control.")
    print("If A/B clears it, structure tracks scribal language and not position.")

    # ── POOLED ──
    ga = [l for l in lines if l["cur"] == "A"]
    gb = [l for l in lines if l["cur"] == "B"]
    pooled = report("POOLED — all Currier A vs all Currier B",
                    ga, gb, all_pages, page_lines, args.perms, rng)

    # ── RESTRICTED ──
    ha = [l for l in lines if l["cur"] == "A" and l["section"] == "herbal_A"]
    hb = [l for l in lines if l["cur"] == "B" and l["section"] == "herbal_A"]
    hpages = sorted({l["page"] for l in lines if l["section"] == "herbal_A"},
                    key=lambda p: (folio_num(p), p))
    restricted = {}
    if len(hb) >= 100:
        restricted = report("RESTRICTED — herbal_A only (section held constant)",
                            ha, hb, hpages, page_lines, args.perms, rng)

    # ── Verdict ──
    print("\n" + "=" * 78)
    n_clear = sum(1 for v in pooled.values() if v["clears_null"])
    n_tot = len(pooled)
    clears = [k for k, v in pooled.items() if v["clears_null"]]
    print(f"POOLED: {n_clear}/{n_tot} cells clear the contiguous-block null")
    if clears:
        print(f"  clearing: {', '.join(clears)}")
    if restricted:
        rc = [k for k, v in restricted.items() if v["clears_null"]]
        print(f"RESTRICTED: {len(rc)}/{len(restricted)} clear"
              + (f" ({', '.join(rc)})" if rc else ""))

    if n_tot and n_clear == n_tot:
        verdict = ("ALL cells clear the null — the null is too permissive to "
                   "interpret. Every contrast looking significant means the "
                   "contiguous-block design does not constrain this comparison, "
                   "probably because Currier A and B occupy nearly disjoint "
                   "folio ranges. Redesign before drawing conclusions.")
    elif n_clear:
        verdict = (f"{n_clear} of {n_tot} cells clear a null that section and "
                   "quire partitions both failed. Transition structure differs "
                   "by Currier language beyond what arbitrary positional splits "
                   "produce. This is the only surviving structural partition in "
                   "the manuscript.")
    else:
        verdict = ("No cell clears the null. The Currier A/B contrast is "
                   "positional like section and quire, and no structural "
                   "partition of the manuscript survives control. The "
                   "transition grammar is uniform throughout.")
    print(f"\nVERDICT: {verdict}")

    out = {
        "description": ("Contiguous-block null applied to the Currier A/B "
                        "contrast — the last structural partition untested "
                        "against the control that section and quire failed."),
        "caveat": ("Currier A and B occupy largely distinct folio ranges, so "
                   "the contiguous-block null may be weakly constraining here. "
                   "Check whether ALL cells clear; if so the design is "
                   "uninformative rather than the result strong."),
        "seed": SEED, "n_permutations": args.perms,
        "pooled": pooled, "restricted_herbal_A": restricted,
        "verdict": verdict,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "language_effect_null_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
