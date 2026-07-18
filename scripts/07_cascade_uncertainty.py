#!/usr/bin/env python3
"""
07_cascade_uncertainty.py — Confidence intervals and multiple-comparisons
correction for the agreement cascade claims (Finding 1.7).

CONTEXT
-------
Finding 1.7 (durable_findings §1.7; paper §3.8) reports agreement cascades of
+20–80 percentage points across three-token chains. The headline
CHEDY→OTHER→CHEDY cascade (+80pp) rests on n_agree = 13 trials. Point estimates
alone are not adequate uncertainty framing for effects of this size.

OBJECTION (independent audit, §3.4)
-----------------------------------
- +80pp reported without CI. Binomial CI on 11/13 runs roughly [55%, 98%].
- Five distinct chains were tested without pre-registration. No multiple-
  comparisons correction applied.

WHAT THIS SCRIPT DOES
---------------------
1. Recompute each cascade with exact cell counts (already present in
   extended_analysis_results.json).
2. Add Wilson-score 95% binomial CIs on each conditional probability.
3. Compute a two-proportion z-test p-value for each cascade vs its null.
4. Apply Benjamini-Hochberg FDR correction across the five chain configurations.
5. Report which chains survive FDR at α=0.05 and which do not.

Usage:
  python scripts/07_cascade_uncertainty.py

Output:
  results/cascade_uncertainty_results.json
"""

import os
import sys
import json
from math import sqrt, erf

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def wilson_ci(k, n, z=1.96):
    """Wilson-score 95% CI for a proportion k/n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z*z / n
    center = (p + z*z / (2*n)) / denom
    margin = (z * sqrt((p * (1 - p) / n) + (z*z / (4 * n * n)))) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def norm_sf(x):
    """Upper-tail survival of the standard normal."""
    return 0.5 * (1 - erf(x / sqrt(2)))


def norm_two_tailed(z):
    """Two-tailed p-value for a z statistic."""
    return 2.0 * norm_sf(abs(z))


def newcombe_wilson_diff(k1, n1, k2, n2, z=1.96):
    """Newcombe-Wilson hybrid-score 95% CI for a difference of proportions.

    Correct interval for p1 - p2 at small n. The previous approach subtracted
    the far endpoints of two independent Wilson intervals, which is valid but
    markedly over-wide (a conservative bound, not a 95% interval). At n=13 the
    difference is large enough to change how the flagship effect reads.
    Newcombe (1998), Statistics in Medicine 17:873-890, method 10.
    """
    if n1 == 0 or n2 == 0:
        return (None, None)
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson_ci(k1, n1, z)
    l2, u2 = wilson_ci(k2, n2, z)
    lower = (p1 - p2) - sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    upper = (p1 - p2) + sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return (max(-1.0, lower), min(1.0, upper))


def two_prop_z(k1, n1, k2, n2):
    """Two-proportion z-test for p1 != p2. Returns (z, two-tailed p)."""
    if n1 == 0 or n2 == 0:
        return 0.0, 1.0
    p1, p2 = k1 / n1, k2 / n2
    p_pool = (k1 + k2) / (n1 + n2)
    var = p_pool * (1 - p_pool) * (1 / n1 + 1 / n2)
    if var <= 0:
        return 0.0, 1.0
    z = (p1 - p2) / sqrt(var)
    # Two-tailed. The earlier one-tailed test presupposed the direction of an
    # effect that was discovered in the same data, which inflates significance.
    return z, norm_two_tailed(z)


def bh_fdr(pvalues, alpha=0.05):
    """Benjamini-Hochberg FDR correction. Returns list of booleans (pass/fail)."""
    n = len(pvalues)
    indexed = sorted(enumerate(pvalues), key=lambda x: x[1])
    results = [False] * n
    max_k = -1
    for k, (idx, p) in enumerate(indexed, start=1):
        threshold = (k / n) * alpha
        if p <= threshold:
            max_k = k
    if max_k > -1:
        for k, (idx, p) in enumerate(indexed, start=1):
            if k <= max_k:
                results[idx] = True
    return results


def main():
    ext_path = os.path.join(PROJECT_ROOT, "results", "extended_analysis_results.json")
    with open(ext_path) as f:
        ext = json.load(f)

    chains = ext["1.7_agreement_cascades"]["chains"]

    processed = []
    for chain_name, d in chains.items():
        n_agree = d["n_agree"]
        n_disagree = d["n_disagree"]
        # Raw success counts, emitted by 04_extended_analysis.py. Previously
        # these were reconstructed as round(pct * n) from percentages already
        # rounded to whole numbers, which at n=13 can shift the count by +/-1
        # and move the interval materially.
        if "k_agree" not in d or "k_disagree" not in d:
            raise KeyError(
                "extended_analysis_results.json lacks raw cascade counts "
                "(k_agree/k_disagree). Re-run scripts/04_extended_analysis.py.")
        k_agree = d["k_agree"]
        k_disagree = d["k_disagree"]
        p_agree = k_agree / n_agree
        p_disagree = k_disagree / n_disagree
        ci_agree = wilson_ci(k_agree, n_agree)
        ci_disagree = wilson_ci(k_disagree, n_disagree)
        z, p = two_prop_z(k_agree, n_agree, k_disagree, n_disagree)
        nw = newcombe_wilson_diff(k_agree, n_agree, k_disagree, n_disagree)
        processed.append({
            "chain": chain_name,
            "n_agree_trials": n_agree,
            "n_disagree_trials": n_disagree,
            "p_if_agree": round(p_agree, 3),
            "p_if_disagree": round(p_disagree, 3),
            "cascade_pp_point_estimate": round((p_agree - p_disagree) * 100, 1),
            "ci95_p_if_agree": [round(ci_agree[0], 3), round(ci_agree[1], 3)],
            "ci95_p_if_disagree": [round(ci_disagree[0], 3), round(ci_disagree[1], 3)],
            "cascade_pp_ci95_conservative": [
                round((ci_agree[0] - ci_disagree[1]) * 100, 1),
                round((ci_agree[1] - ci_disagree[0]) * 100, 1),
            ],
            "cascade_pp_ci95_newcombe": [
                round(100 * nw[0], 1) if nw[0] is not None else None,
                round(100 * nw[1], 1) if nw[1] is not None else None,
            ],
            "k_agree": k_agree,
            "k_disagree": k_disagree,
            "two_prop_z": round(z, 2),
            "two_prop_p_two_tailed": p,
        })

    # Apply BH FDR
    pvalues = [d["two_prop_p_two_tailed"] for d in processed]
    passes = bh_fdr(pvalues, alpha=0.05)
    for d, ok in zip(processed, passes):
        d["survives_bh_fdr_alpha_0.05"] = bool(ok)
        d["two_prop_p_two_tailed"] = float(f"{d['two_prop_p_two_tailed']:.2e}")

    summary = {
        "description": (
            "Confidence intervals and Benjamini-Hochberg FDR correction for the "
            "five agreement-cascade chains reported in Finding 1.7. "
            "ci95_p_if_agree is the Wilson-score 95% interval on the conditional "
            "probability of B->C agreement given A≡B. "
            "cascade_pp_ci95_conservative is (lower_agree - upper_disagree, "
            "upper_agree - lower_disagree), a conservative composite interval."
        ),
        "methodology": {
            "ci": "Wilson-score 95% intervals on each conditional probability.",
            "test": "Two-proportion z-test for p(B->C agree | A≡B) > p(B->C agree | A≠B).",
            "correction": "Benjamini-Hochberg FDR at α=0.05 across 5 chains.",
        },
        "n_chains_tested": len(processed),
        "n_chains_surviving_fdr": sum(passes),
        "chains": processed,
    }

    print("Chain-by-chain summary:")
    for d in processed:
        print(f"  {d['chain']}:")
        print(f"    p(agree|≡) = {d['p_if_agree']} [n={d['n_agree_trials']}] CI {d['ci95_p_if_agree']}")
        print(f"    p(agree|≠) = {d['p_if_disagree']} [n={d['n_disagree_trials']}] CI {d['ci95_p_if_disagree']}")
        print(f"    cascade Δ = {d['cascade_pp_point_estimate']}pp, conservative CI {d['cascade_pp_ci95_conservative']}")
        print(f"    z = {d['two_prop_z']}, p = {d['two_prop_p_two_tailed']}, BH-FDR pass = {d['survives_bh_fdr_alpha_0.05']}")

    out_path = os.path.join(PROJECT_ROOT, "results", "cascade_uncertainty_results.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()

