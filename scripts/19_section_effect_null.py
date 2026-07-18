#!/usr/bin/env python3
"""
19_section_effect_null.py — Does the surviving section finding clear the null?

WHAT THIS TESTS
---------------
Script 17 found one section effect with a bootstrap CI excluding zero:
AIIN->QOK repulsion measures 0.16x in the biological section (Currier B) against
0.50x in recipes_Q20 (Currier B) — a difference of -0.34 with CI
[-0.48, -0.20], language held constant.

Script 18 then showed that quire-level heterogeneity does NOT exceed what
random contiguous page groupings produce. That control was never applied to the
section result. It should have been, because a bootstrap CI answers a different
question: "given these two groups, is the difference stable?" — not "is a
difference this large surprising for two arbitrary contiguous groups of this
size?"

Only the second question distinguishes a real localised effect from the ordinary
lumpiness of a heterogeneous manuscript.

METHOD
------
Restrict to Currier B, so language is held constant throughout. Order its pages
by folio. Then:

  TEST 1 — Is the biological/recipes DIFFERENCE extreme?
      Draw two disjoint contiguous page blocks matching the real section sizes,
      compute the AIIN->QOK difference between them, repeat. Compare the
      observed -0.34 against that distribution.

  TEST 2 — Is the biological VALUE itself extreme?
      Draw single contiguous blocks the size of the biological section and
      collect their AIIN->QOK ratios. Compare the observed 0.16x against that
      distribution. This asks whether the biological section is unusually
      suppressed, independent of what it is compared against.

  TEST 3 — Same two tests for CHEDY->QOK, as a negative control.
      Script 17 found no section contrast excluding zero for CHEDY->QOK, so it
      should NOT clear these nulls. If it does, the null is too permissive and
      TEST 1 and 2 cannot be trusted.

TEST 3 is the part that makes the other two interpretable. A null that flags
everything proves nothing.

USAGE
    python scripts/19_section_effect_null.py --perms 2000

OUTPUT
    results/section_effect_null_results.json
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _canonical import load_corpus, classify  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
SEED = 42
CELLS = [("AIIN", "QOK"), ("CHEDY", "QOK")]


def folio_num(p):
    m = re.match(r"f(\d+)", p or "")
    return int(m.group(1)) if m else 999


def ratio_of(lines, s, d):
    tr = 0
    src = dst = total = 0
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=2000)
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    lines = load_corpus()
    for l in lines:
        l["fam"] = [classify(t) for t in l["tokens"]]

    # Currier B only — language held constant
    b = [l for l in lines if str(l["currier"])[:1] == "B"]
    pages = sorted({l["page"] for l in b}, key=lambda p: (folio_num(p), p))
    page_lines = defaultdict(list)
    for l in b:
        page_lines[l["page"]].append(l)

    bio = [l for l in b if l["section"] == "biological"]
    rec = [l for l in b if l["section"] == "recipes_Q20"]
    n_bio_pages = len({l["page"] for l in bio})
    n_rec_pages = len({l["page"] for l in rec})

    print("=" * 78)
    print("DOES THE SECTION EFFECT CLEAR A CONTIGUOUS-PARTITION NULL?")
    print("=" * 78)
    print(f"\nCurrier B corpus: {len(pages)} pages, {len(b)} lines, "
          f"{sum(len(l['tokens']) for l in b)} tokens")
    print(f"  biological:  {n_bio_pages} pages, {len(bio)} lines")
    print(f"  recipes_Q20: {n_rec_pages} pages, {len(rec)} lines")

    obs = {}
    for s, d in CELLS:
        rb = ratio_of(bio, s, d)
        rr = ratio_of(rec, s, d)
        obs[(s, d)] = {"biological": rb, "recipes": rr,
                       "diff": (rb - rr) if (rb and rr) else None}
        print(f"\nObserved {s}→{d}: biological {rb:.3f}x, "
              f"recipes {rr:.3f}x, diff {rb - rr:+.3f}")

    # ── Build nulls ──
    def draw_two_blocks():
        """Two disjoint contiguous page blocks of the real section sizes."""
        need = n_bio_pages + n_rec_pages
        if len(pages) < need:
            return None, None
        for _ in range(40):
            i = int(rng.integers(0, len(pages) - n_bio_pages + 1))
            blk1 = pages[i:i + n_bio_pages]
            rest = pages[:i] + pages[i + n_bio_pages:]
            if len(rest) < n_rec_pages:
                continue
            j = int(rng.integers(0, len(rest) - n_rec_pages + 1))
            blk2 = rest[j:j + n_rec_pages]
            return blk1, blk2
        return None, None

    def lines_of(block):
        return [l for p in block for l in page_lines[p]]

    null_diff = {c: [] for c in CELLS}
    null_val = {c: [] for c in CELLS}
    for _ in range(args.perms):
        b1, b2 = draw_two_blocks()
        if b1 is None:
            continue
        l1, l2 = lines_of(b1), lines_of(b2)
        for c in CELLS:
            r1 = ratio_of(l1, *c)
            r2 = ratio_of(l2, *c)
            if r1 and r2:
                null_diff[c].append(r1 - r2)
            if r1:
                null_val[c].append(r1)

    print("\n" + "=" * 78)
    print(f"{'cell':<14}{'test':<12}{'observed':>10}{'null mean':>11}"
          f"{'null 2.5/97.5':>22}{'p':>9}")
    print("-" * 78)

    results = {}
    for c in CELLS:
        s, d = c
        key = f"{s}->{d}"
        results[key] = {}

        # TEST: difference
        o = obs[c]["diff"]
        arr = np.array(null_diff[c])
        if len(arr) > 50 and o is not None:
            p = float((np.abs(arr) >= abs(o)).sum() + 1) / (len(arr) + 1)
            lo, hi = np.percentile(arr, [2.5, 97.5])
            print(f"{key:<14}{'difference':<12}{o:>+10.3f}{arr.mean():>+11.3f}"
                  f"{f'[{lo:+.2f}, {hi:+.2f}]':>22}{p:>9.4f}")
            results[key]["difference"] = {
                "observed": round(o, 3), "null_mean": round(float(arr.mean()), 3),
                "null_ci": [round(float(lo), 3), round(float(hi), 3)],
                "p_empirical": round(p, 4), "n_null": len(arr),
                "clears_null": bool(p < 0.05)}

        # TEST: absolute value of the biological block
        o2 = obs[c]["biological"]
        arr2 = np.array(null_val[c])
        if len(arr2) > 50 and o2 is not None:
            centre = float(arr2.mean())
            p2 = float((np.abs(arr2 - centre) >= abs(o2 - centre)).sum() + 1) / (len(arr2) + 1)
            lo2, hi2 = np.percentile(arr2, [2.5, 97.5])
            print(f"{key:<14}{'bio value':<12}{o2:>10.3f}{centre:>11.3f}"
                  f"{f'[{lo2:.2f}, {hi2:.2f}]':>22}{p2:>9.4f}")
            results[key]["biological_value"] = {
                "observed": round(o2, 3), "null_mean": round(centre, 3),
                "null_ci": [round(float(lo2), 3), round(float(hi2), 3)],
                "p_empirical": round(p2, 4), "n_null": len(arr2),
                "clears_null": bool(p2 < 0.05)}

    # ── Verdict ──
    print("\n" + "=" * 78)
    aiin = results.get("AIIN->QOK", {})
    chedy = results.get("CHEDY->QOK", {})
    a_diff = aiin.get("difference", {}).get("clears_null")
    a_val = aiin.get("biological_value", {}).get("clears_null")
    c_diff = chedy.get("difference", {}).get("clears_null")
    c_val = chedy.get("biological_value", {}).get("clears_null")

    print(f"AIIN→QOK  difference clears null: {a_diff}")
    print(f"AIIN→QOK  bio value  clears null: {a_val}")
    print(f"CHEDY→QOK difference clears null: {c_diff}   (negative control)")
    print(f"CHEDY→QOK bio value  clears null: {c_val}   (negative control)")

    control_ok = not (c_diff or c_val)
    if not control_ok:
        verdict = ("NULL IS TOO PERMISSIVE. The negative control (CHEDY→QOK) "
                   "also clears it, so nothing here is interpretable. The "
                   "contiguous-block null needs redesign before either result "
                   "can be trusted.")
    elif a_diff or a_val:
        verdict = ("SECTION EFFECT SURVIVES. The AIIN→QOK suppression in the "
                   "biological section exceeds what random contiguous page "
                   "blocks of the same size produce, while the negative "
                   "control does not. This is a real localised effect and can "
                   "be reported.")
    else:
        verdict = ("SECTION EFFECT DOES NOT SURVIVE. The AIIN→QOK difference "
                   "is within the range produced by arbitrary contiguous page "
                   "blocks. The bootstrap CI in script 17 answered a narrower "
                   "question and should not be read as establishing a section "
                   "effect. Retire the claim alongside the quire result.")
    print(f"\nVERDICT: {verdict}")

    out = {
        "description": ("Applies the contiguous-partition null from script 18 "
                        "to the one section effect that survived bootstrap in "
                        "script 17."),
        "design": ("Currier B only. Two disjoint contiguous page blocks matching "
                   "the real biological and recipes_Q20 page counts, drawn "
                   "repeatedly. CHEDY->QOK included as a negative control."),
        "seed": SEED, "n_permutations": args.perms,
        "observed": {f"{s}->{d}": {k: (round(v, 3) if v else None)
                                   for k, v in obs[(s, d)].items()}
                     for s, d in CELLS},
        "tests": results,
        "negative_control_behaved": bool(control_ok),
        "verdict": verdict,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "section_effect_null_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
