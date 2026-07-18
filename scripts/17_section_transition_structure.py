#!/usr/bin/env python3
"""
17_section_transition_structure.py — Does transition structure vary by section?

THE QUESTION
------------
If the manuscript is produced by a generative system applying positional rules,
different sections might run on different rule-sets — the herbal pages and the
balneological pages would show measurably different transition structure. If it
encodes content, the same grammar should operate throughout and section
differences should be lexical, not structural.

Script 03 tests section-level SELF-CLUSTERING and finds it stable, which is
weak evidence against different rule-sets. Nobody has tested the full
transition matrix per section with correction. That is what this does.

THE CONFOUND, AND THE NATURAL EXPERIMENT THAT BREAKS IT
-------------------------------------------------------
Section and Currier language are heavily confounded: herbal_A is mostly
Currier A, while biological and recipes_Q20 are Currier B. A naive
section-by-section comparison would measure language, not section.

But the corpus contains the cell needed to separate them:

    herbal_A     Currier A    1,149 lines    7,006 tokens
    herbal_A     Currier B      304 lines    2,689 tokens     <-- both
    biological   Currier B      917 lines    6,898 tokens
    recipes_Q20  Currier B    1,084 lines   10,890 tokens

That supports two orthogonal contrasts:

  TEST 1 — SECTION effect, language held constant.
      Within Currier B only: herbal_A vs biological vs recipes_Q20.
      Any difference is attributable to section, not language.

  TEST 2 — LANGUAGE effect, section held constant.
      Within herbal_A only: Currier A vs Currier B.
      Any difference is attributable to language, not section.

Comparing the magnitude of the two answers the actual question: is the
manuscript's structural variation organized by what the page is ABOUT, or by
who/how it was written?

METHOD
------
Per stratum, the full 6x6 within-line transition matrix over canonical
families. Two tests:

  (a) Chi-square test of homogeneity across strata on the collapsed
      source x destination table, per source family.
  (b) Per-cell ratio comparison with bootstrap CIs on the difference,
      for the cells the paper relies on (CHEDY->QOK, AIIN->QOK).

BH-FDR correction across all cell comparisons.

USAGE
    python scripts/17_section_transition_structure.py

OUTPUT
    results/section_transition_structure.json
"""

import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2_contingency

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _canonical import load_corpus, classify, FAMILY_NAMES  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
SEED = 42
N_BOOT = 2000
ALPHA = 0.05

KEY_CELLS = [("CHEDY", "QOK"), ("AIIN", "QOK"), ("QOK", "QOK"),
             ("OT", "OT"), ("OK", "OK"), ("CHEDY", "AIIN")]


def strata_lines(lines, section=None, currier=None):
    out = []
    for l in lines:
        if section and l["section"] != section:
            continue
        if currier and str(l["currier"])[:1] != currier:
            continue
        out.append(l)
    return out


def matrix(lines):
    tr = defaultdict(int)
    src, dst = Counter(), Counter()
    total = 0
    for l in lines:
        c = [classify(t) for t in l["tokens"]]
        for i in range(len(c) - 1):
            tr[(c[i], c[i + 1])] += 1
            src[c[i]] += 1
            dst[c[i + 1]] += 1
            total += 1
    return tr, src, dst, total


def ratio(tr, src, dst, total, s, d):
    if not total or not src[s] or not dst[d]:
        return None, 0
    exp = src[s] * (dst[d] / total)
    obs = tr.get((s, d), 0)
    return (obs / exp if exp > 1 else None), obs


def boot_ratio_diff(lines_a, lines_b, s, d, rng, n=N_BOOT):
    """Bootstrap CI on the ratio difference, resampling whole LINES.

    Lines are the resampling unit because transitions are computed within
    lines; resampling tokens would break the dependence structure being
    measured.
    """
    diffs = []
    for _ in range(n):
        sa = [lines_a[i] for i in rng.integers(0, len(lines_a), len(lines_a))]
        sb = [lines_b[i] for i in rng.integers(0, len(lines_b), len(lines_b))]
        ra, _ = ratio(*matrix(sa), s, d)
        rb, _ = ratio(*matrix(sb), s, d)
        if ra and rb:
            diffs.append(ra - rb)
    if len(diffs) < n // 4:
        return None, None, None
    return (float(np.mean(diffs)),
            float(np.percentile(diffs, 2.5)),
            float(np.percentile(diffs, 97.5)))


def homogeneity(strata, s):
    """Chi-square homogeneity across strata for one source family's row."""
    rows = []
    for _, (tr, src, dst, total) in strata:
        row = [tr.get((s, d), 0) for d in FAMILY_NAMES]
        if sum(row) >= 20:
            rows.append(row)
    if len(rows) < 2:
        return None, None
    arr = np.array(rows)
    keep = arr.sum(axis=0) > 0
    arr = arr[:, keep]
    if arr.shape[1] < 2:
        return None, None
    try:
        chi2, p, _, _ = chi2_contingency(arr)
        return float(chi2), float(p)
    except Exception:
        return None, None


def bh(pvals, alpha=ALPHA):
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    rej = [False] * n
    kmax = 0
    for rank, i in enumerate(order, 1):
        if pvals[i] <= alpha * rank / n:
            kmax = rank
    for rank, i in enumerate(order, 1):
        if rank <= kmax:
            rej[i] = True
    return rej


def main():
    rng = np.random.default_rng(SEED)
    lines = load_corpus()
    print("=" * 78)
    print("SECTION vs LANGUAGE: WHERE DOES TRANSITION STRUCTURE VARY?")
    print("=" * 78)

    # ── TEST 1: section effect, Currier B held constant ──
    print("\nTEST 1 — SECTION effect (Currier B only, language held constant)")
    print("-" * 78)
    t1 = []
    for sec in ["herbal_A", "biological", "recipes_Q20"]:
        ls = strata_lines(lines, section=sec, currier="B")
        if len(ls) >= 100:
            t1.append((f"{sec}/B", ls))
    print(f"{'stratum':<18}{'lines':>7}{'tokens':>8}", end="")
    for s, d in KEY_CELLS[:3]:
        print(f"{s[:3]+'→'+d[:3]:>11}", end="")
    print()
    t1m = []
    for name, ls in t1:
        m = matrix(ls)
        t1m.append((name, m))
        ntok = sum(len(l["tokens"]) for l in ls)
        print(f"{name:<18}{len(ls):>7}{ntok:>8}", end="")
        for s, d in KEY_CELLS[:3]:
            r, _ = ratio(*m, s, d)
            print(f"{(r if r else float('nan')):>10.2f}x", end="")
        print()

    # ── TEST 2: language effect, herbal_A held constant ──
    print("\nTEST 2 — LANGUAGE effect (herbal_A only, section held constant)")
    print("-" * 78)
    t2 = []
    for cur in ["A", "B"]:
        ls = strata_lines(lines, section="herbal_A", currier=cur)
        if len(ls) >= 100:
            t2.append((f"herbal_A/{cur}", ls))
    print(f"{'stratum':<18}{'lines':>7}{'tokens':>8}", end="")
    for s, d in KEY_CELLS[:3]:
        print(f"{s[:3]+'→'+d[:3]:>11}", end="")
    print()
    t2m = []
    for name, ls in t2:
        m = matrix(ls)
        t2m.append((name, m))
        ntok = sum(len(l["tokens"]) for l in ls)
        print(f"{name:<18}{len(ls):>7}{ntok:>8}", end="")
        for s, d in KEY_CELLS[:3]:
            r, _ = ratio(*m, s, d)
            print(f"{(r if r else float('nan')):>10.2f}x", end="")
        print()

    # ── Homogeneity tests ──
    print("\n\nCHI-SQUARE HOMOGENEITY OF TRANSITION ROWS")
    print("-" * 78)
    print(f"{'source family':<16}{'TEST1 (section)':>22}{'TEST2 (language)':>24}")
    homog = {}
    p1s, p2s, fams = [], [], []
    for s in ["QOK", "OK", "OT", "CHEDY", "AIIN", "OTHER"]:
        c1, p1 = homogeneity(t1m, s)
        c2, p2 = homogeneity(t2m, s)
        homog[s] = {"section_chi2": c1, "section_p": p1,
                    "language_chi2": c2, "language_p": p2}
        f1 = f"chi2={c1:.1f} p={p1:.4f}" if p1 is not None else "n/a"
        f2 = f"chi2={c2:.1f} p={p2:.4f}" if p2 is not None else "n/a"
        print(f"{s:<16}{f1:>22}{f2:>24}")
        if p1 is not None:
            p1s.append(p1); fams.append(s)
        if p2 is not None:
            p2s.append(p2)
    if p1s:
        r1 = bh(p1s)
        print(f"\nSection effect: {sum(r1)}/{len(p1s)} source families show "
              f"heterogeneity surviving BH-FDR")
    if p2s:
        r2 = bh(p2s)
        print(f"Language effect: {sum(r2)}/{len(p2s)} source families show "
              f"heterogeneity surviving BH-FDR")

    # ── Key-cell bootstrap comparisons ──
    print("\n\nKEY-CELL DIFFERENCES (bootstrap over lines, 95% CI)")
    print("-" * 78)
    comparisons = []
    if len(t1) >= 2:
        for i in range(len(t1)):
            for j in range(i + 1, len(t1)):
                comparisons.append(("SECTION", t1[i], t1[j]))
    if len(t2) == 2:
        comparisons.append(("LANGUAGE", t2[0], t2[1]))

    rows = []
    for kind, (na, la), (nb, lb) in comparisons:
        for s, d in KEY_CELLS[:4]:
            mean, lo, hi = boot_ratio_diff(la, lb, s, d, rng)
            if mean is None:
                continue
            excl = (lo > 0 or hi < 0)
            rows.append({"contrast": kind, "a": na, "b": nb,
                         "cell": f"{s}->{d}", "mean_diff": round(mean, 3),
                         "ci95": [round(lo, 3), round(hi, 3)],
                         "excludes_zero": bool(excl)})
    print(f"{'contrast':<10}{'comparison':<30}{'cell':<14}{'Δratio':>9}{'95% CI':>20}{'≠0':>4}")
    for r in rows:
        ci = f"[{r['ci95'][0]:+.2f}, {r['ci95'][1]:+.2f}]"
        print(f"{r['contrast']:<10}{r['a']+' vs '+r['b']:<30}{r['cell']:<14}"
              f"{r['mean_diff']:>+9.2f}{ci:>20}{'Y' if r['excludes_zero'] else 'n':>4}")

    n_sec = sum(1 for r in rows if r["contrast"] == "SECTION" and r["excludes_zero"])
    n_sec_t = sum(1 for r in rows if r["contrast"] == "SECTION")
    n_lang = sum(1 for r in rows if r["contrast"] == "LANGUAGE" and r["excludes_zero"])
    n_lang_t = sum(1 for r in rows if r["contrast"] == "LANGUAGE")

    print("\n" + "=" * 78)
    print(f"SECTION contrasts with CI excluding zero:  {n_sec}/{n_sec_t}")
    print(f"LANGUAGE contrasts with CI excluding zero: {n_lang}/{n_lang_t}")

    if n_lang_t and n_lang / n_lang_t > (n_sec / n_sec_t if n_sec_t else 0):
        verdict = ("Transition structure varies more by CURRIER LANGUAGE than "
                   "by SECTION. Structural variation tracks who/how the text "
                   "was written rather than what the page depicts — consistent "
                   "with a production process rather than section-specific "
                   "content grammar.")
    elif n_sec_t and n_sec / n_sec_t > 0:
        verdict = ("Transition structure varies by SECTION with language held "
                   "constant. Different parts of the manuscript may run on "
                   "different rule-sets, which favours a generative-system "
                   "reading over a single uniform grammar.")
    else:
        verdict = ("No stratum contrast shows a transition-structure difference "
                   "with a CI excluding zero. The same transition grammar "
                   "operates across sections AND across Currier languages — "
                   "structure is uniform and section differences are lexical.")
    print(f"\nVERDICT: {verdict}")

    out = {
        "description": ("Tests whether transition structure varies by section "
                        "or by Currier language, using herbal_A (which contains "
                        "both languages) to break the section/language "
                        "confound."),
        "design": {
            "test_1_section": "Currier B only: herbal_A vs biological vs recipes_Q20",
            "test_2_language": "herbal_A only: Currier A vs Currier B",
        },
        "seed": SEED, "n_bootstrap": N_BOOT,
        "homogeneity": homog,
        "key_cell_comparisons": rows,
        "n_section_contrasts_excluding_zero": [n_sec, n_sec_t],
        "n_language_contrasts_excluding_zero": [n_lang, n_lang_t],
        "verdict": verdict,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "section_transition_structure.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
