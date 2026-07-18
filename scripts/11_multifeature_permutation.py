#!/usr/bin/env python3
"""
11_multifeature_permutation.py — Corrected multi-feature agreement (Finding 1.6)

WHAT WAS WRONG
--------------
`04_extended_analysis.py::combined_agreement` estimated the expected joint
agreement rate by multiplying per-feature marginals:

    joint_expected = 1.0
    for ie in individual_expected:
        joint_expected *= ie

That is valid only if suffix, length, mantle, and circle-count are mutually
independent. They are not. All four are functions of the same token:

  - f_suffix reads the final characters
  - f_length counts characters, and suffix class constrains token length
  - f_mantle reads mantle-layer characters, which include the final -dy/-ey
    material that f_suffix keys on
  - f_circles counts o/a/y, and y is the terminal character of the two most
    common suffix classes

Multiplying correlated marginals produces an expected value far below the true
one, inflating the observed/expected ratio. The published 5-9x multi-feature
agreement figures are inflated by an unknown amount and should not be cited
until recomputed.

WHAT THIS SCRIPT DOES INSTEAD
-----------------------------
Estimates the null by permutation, which requires no independence assumption.

For each family pair (A -> B):
  1. Collect the observed adjacent (source, target) token pairs.
  2. Count how many agree on ALL features simultaneously.
  3. Build the null by shuffling target tokens across pairs within the same
     family, N_PERM times, recomputing all-feature agreement each time. This
     destroys the pairing while preserving both marginal token distributions
     AND the internal feature correlation structure of every token, because
     whole tokens are permuted rather than features.
  4. Report observed / mean(null), an empirical p-value, and a null 95%
     interval.

The permuted null is the correct comparison: any inflation caused by feature
dependence is present in the null as well and therefore cancels.

Also reports the single-feature (suffix-only) ratio under the same permutation
null, so the multi-feature and single-feature figures are directly comparable
for the first time.

USAGE
    python scripts/11_multifeature_permutation.py
    python scripts/11_multifeature_permutation.py --perms 5000

OUTPUT
    results/multifeature_permutation_results.json
"""

import argparse
import json
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _canonical import load_corpus, classify  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
SEED = 42
N_PERM = 2000

INTERACTIONS = [("CHEDY", "QOK"), ("QOK", "QOK"), ("OK", "OT"),
                ("OK", "OK"), ("OT", "OT")]


# ─── Feature functions ───────────────────────────────────────────────────────
# COPIED VERBATIM from 04_extended_analysis.py so that the only thing changing
# between the old and new figures is the null model, never the features.

def f_suffix(tok):
    if tok.endswith("dy"): return "dy"
    if tok.endswith("ey"): return "ey"
    if tok.endswith("al"): return "al"
    if tok.endswith("ol"): return "ol"
    if tok.endswith("ar"): return "ar"
    if tok.endswith("or"): return "or"
    if tok.endswith("am"): return "am"
    if tok.endswith("y"): return "y"
    if tok.endswith("n"): return "n"
    return "x"


def f_length(tok):
    n = len(tok)
    return "S" if n <= 4 else ("M" if n <= 6 else ("L" if n <= 8 else "XL"))


def parse_eva(token):
    chars = []; i = 0
    while i < len(token):
        if i < len(token)-2 and token[i] == 'c' and token[i+1] in 'tkpf' and token[i+2] == 'h':
            chars.append(token[i:i+3]); i += 3
        elif i < len(token)-1 and token[i:i+2] in ('ch', 'sh', 'ee', 'ii', 'ai', 'oi'):
            chars.append(token[i:i+2]); i += 2
        else:
            chars.append(token[i]); i += 1
    return chars


def layer(unit):
    if unit in ('cth', 'ckh', 'cph', 'cfh', 't', 'p', 'k', 'f'): return 'C'
    if unit in ('ch', 'sh', 'ee'): return 'M'
    if unit in ('o', 'a', 'y'): return 'O'
    return 'R'


def f_mantle(tok):
    return "".join(c for c in parse_eva(tok) if layer(c) == 'M') or "none"


def f_circles(tok):
    return sum(1 for c in parse_eva(tok) if layer(c) == 'O')


FEATURE_SETS = {
    "suffix_only": [f_suffix],
    "all_four": [f_suffix, f_length, f_mantle, f_circles],
}


# ─── Permutation test ────────────────────────────────────────────────────────
def agreement_count(sources, targets, fns):
    """Number of pairs agreeing on every feature in fns."""
    return sum(1 for s, t in zip(sources, targets)
               if all(fn(s) == fn(t) for fn in fns))


def permutation_test(pairs, fns, n_perm, rng):
    """Observed vs permuted-null agreement.

    The null shuffles target tokens across pairs. Both marginal token
    distributions are preserved exactly, and because whole tokens are
    permuted, each token's internal feature correlations travel with it.
    Any inflation from feature dependence therefore appears in the null too
    and cancels in the ratio.
    """
    if len(pairs) < 20:
        return None
    sources = [s for s, _ in pairs]
    targets = [t for _, t in pairs]
    n = len(pairs)

    obs = agreement_count(sources, targets, fns)
    obs_rate = obs / n

    null_rates = np.empty(n_perm)
    tgt = np.array(targets, dtype=object)
    for i in range(n_perm):
        null_rates[i] = agreement_count(sources, rng.permutation(tgt), fns) / n

    null_mean = float(null_rates.mean())
    # Empirical one-sided p with +1 correction; report two-sided as well.
    n_ge = int((null_rates >= obs_rate).sum())
    p_one = (n_ge + 1) / (n_perm + 1)
    n_extreme = int((np.abs(null_rates - null_mean) >=
                     abs(obs_rate - null_mean)).sum())
    p_two = (n_extreme + 1) / (n_perm + 1)

    return {
        "n_pairs": n,
        "observed_agreement_pct": round(100 * obs_rate, 2),
        "null_mean_agreement_pct": round(100 * null_mean, 2),
        "null_95_pct": [round(100 * float(np.percentile(null_rates, 2.5)), 2),
                        round(100 * float(np.percentile(null_rates, 97.5)), 2)],
        "ratio_vs_permuted_null": (round(obs_rate / null_mean, 2)
                                   if null_mean > 0 else None),
        "p_empirical_one_sided": round(p_one, 5),
        "p_empirical_two_sided": round(p_two, 5),
        "n_perm": n_perm,
    }


def independence_ratio(pairs, fns):
    """Reproduces the OLD (incorrect) multiplied-marginals estimate, so the
    magnitude of the inflation is measurable rather than asserted."""
    if not pairs:
        return None
    total = len(pairs)
    same = agreement_count([s for s, _ in pairs], [t for _, t in pairs], fns)
    observed = same / total
    joint_exp = 1.0
    for fn in fns:
        src_d = Counter(fn(s) for s, _ in pairs)
        tgt_d = Counter(fn(t) for _, t in pairs)
        joint_exp *= sum((src_d[f] / total) * (tgt_d.get(f, 0) / total)
                         for f in src_d)
    return round(observed / joint_exp, 2) if joint_exp > 0 else None


def collect_pairs(lines, src_fam, tgt_fam):
    """Adjacent within-line token pairs for a family transition."""
    out = []
    for l in lines:
        fams = [classify(t) for t in l["tokens"]]
        for i in range(len(l["tokens"]) - 1):
            if fams[i] == src_fam and fams[i + 1] == tgt_fam:
                out.append((l["tokens"][i], l["tokens"][i + 1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=N_PERM)
    args = ap.parse_args()

    rng = np.random.default_rng(SEED)
    lines = load_corpus()
    print("=" * 78)
    print("FINDING 1.6 — MULTI-FEATURE AGREEMENT VS PERMUTED NULL")
    print("=" * 78)
    print(f"Corpus: {len(lines)} lines. Permutations: {args.perms}\n")

    results = {
        "description": ("Multi-feature agreement recomputed against a "
                        "permutation null. Supersedes the multiplied-marginals "
                        "estimate in 04_extended_analysis.py, which assumed "
                        "independence between suffix, length, mantle, and "
                        "circle-count — all functions of the same token."),
        "method": ("Target tokens permuted across pairs within the family "
                   "transition; whole tokens permuted so feature correlation "
                   "structure is preserved in the null and cancels in the "
                   "ratio. Empirical p from the permutation distribution."),
        "seed": SEED,
        "pairs": {},
    }

    hdr = f"{'pair':<12}{'featureset':<13}{'n':>6}{'obs%':>8}{'null%':>8}{'ratio':>8}{'p':>10}{'old(indep)':>12}"
    print(hdr)
    print("-" * len(hdr))

    for sf, tf in INTERACTIONS:
        pairs = collect_pairs(lines, sf, tf)
        label = f"{sf}->{tf}"
        results["pairs"][label] = {}
        for fs_name, fns in FEATURE_SETS.items():
            r = permutation_test(pairs, fns, args.perms, rng)
            if r is None:
                continue
            r["old_independence_ratio"] = independence_ratio(pairs, fns)
            r["inflation_factor"] = (
                round(r["old_independence_ratio"] / r["ratio_vs_permuted_null"], 2)
                if r["ratio_vs_permuted_null"] else None)
            results["pairs"][label][fs_name] = r
            print(f"{label:<12}{fs_name:<13}{r['n_pairs']:>6}"
                  f"{r['observed_agreement_pct']:>8.1f}"
                  f"{r['null_mean_agreement_pct']:>8.1f}"
                  f"{r['ratio_vs_permuted_null']:>8.2f}"
                  f"{r['p_empirical_two_sided']:>10.4f}"
                  f"{r['old_independence_ratio']:>12.2f}")

    # Summary of the correction
    infl = [v["all_four"]["inflation_factor"]
            for v in results["pairs"].values() if "all_four" in v]
    if infl:
        results["summary"] = {
            "all_four_inflation_range": [min(infl), max(infl)],
            "all_four_inflation_mean": round(sum(infl) / len(infl), 2),
        }
        print(f"\nMultiplied-marginals estimate overstated the all-four ratio by "
              f"{min(infl):.1f}x-{max(infl):.1f}x (mean {sum(infl)/len(infl):.1f}x).")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = os.path.join(RESULTS_DIR, "multifeature_permutation_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
