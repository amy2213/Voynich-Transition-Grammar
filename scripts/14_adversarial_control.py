#!/usr/bin/env python3
"""
14_adversarial_control.py — Tuned constructed system targeting MVE items 5 and 7

WHY THIS EXISTS
---------------
`09_constructed_control.py` built a first-pass synthetic system that satisfied
5 of 7 MVE checklist items by direct design. It failed items 5 and 7:

    Item 5  bidirectional SYMM-HIGH under auto-detected affixes
    Item 7  open vocabulary at ~71% hapax, TTR ~0.23

`durable_findings.md` §4 draws the correct conclusion from that: items 1-4 and
6 are cheaply engineered, so items 5 and 7 are the only ones doing
discriminating work, and "a tuned generator targeting items 5 and 7
specifically has not been attempted. Until it is tested and shown to fail, the
constructed-system hypothesis cannot be excluded."

This script attempts it. It is deliberately adversarial: it is built to make
the manuscript's central claim FAIL, and it is written by someone who knows
exactly which statistics the pipeline computes. That is the correct posture for
a control — a control that is not genuinely trying to win proves nothing.

THE TWO TARGETS, AND HOW THEY ARE ENGINEERED
--------------------------------------------
Item 5 (bidirectional SYMM-HIGH) requires prefix self-clustering AND suffix
self-clustering to both exceed 1.1x with their ratio in [0.80, 1.25]. Natural
languages fail this because affixation is overwhelmingly one-directional:
suffixing languages cluster on suffixes, and their word-initial material is
near-random with respect to the previous token.

The mechanism: emit tokens as PREFIX + STEM + SUFFIX, and run TWO INDEPENDENT
Markov chains over adjacent tokens — one on prefix identity, one on suffix
identity — each with a tunable self-transition probability. Prefix SC and
suffix SC then become direct functions of those two probabilities, and the
ratio can be tuned to whatever is wanted by adjusting them relative to each
other.

Item 7 (open vocabulary) requires ~71% hapax at TTR ~0.23. The first-pass
generator failed because a small stem inventory forces type reuse. The
mechanism: a large stem inventory drawn from a heavy-tailed (Zipf-like)
distribution, with stem length itself variable, so the product
prefix x stem x suffix yields mostly-unique full tokens at the target corpus
size.

Neither mechanism requires any linguistic content. Both are a few lines of
code.

WHAT A PASS WOULD MEAN
----------------------
If this generator hits both items, the honest conclusion is that all 7
checklist items are engineerable, and the checklist does not discriminate
encoded natural language from a sufficiently motivated constructed system.
That does not make the manuscript a hoax — it means this particular argument
cannot exclude the constructed hypothesis, and the claim must be narrowed to
what the statistics actually support: the manuscript has structure of a kind
that is unusual among natural languages.

USAGE
    python scripts/14_adversarial_control.py
    python scripts/14_adversarial_control.py --tune     # grid over parameters

OUTPUT
    results/adversarial_control_results.json
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
SEED = 42

# Target values, taken from the manuscript's own measured statistics
TARGET = {
    "n_tokens": 31608,
    "n_lines": 4197,
    "hapax_pct": 71.4,
    "ttr": 0.23,
    "prefix_sc": 1.256,     # corrected canonical values (2026-07 audit)
    "suffix_sc": 1.475,
    "ps_ratio": 0.852,
}

# Affix inventories, deliberately Voynich-shaped but content-free
PREFIXES = ["qo", "ch", "sh", "ok", "da", "ot", "yk", "lk"]
SUFFIXES = ["dy", "in", "ey", "ol", "ar", "am", "al", "or"]
STEM_CHARS = "aeiokdlrsty"


# ─── Measurement (mirrors scripts/10 and 12 exactly) ─────────────────────────
MIN_CLASS_N = 10
CANDIDATE_POOL = 80


def detect_affixes(words, side, n=5, lo=2, hi=3, min_cov=0.02, max_cov=0.20):
    counts, index = Counter(), defaultdict(list)
    for i, w in enumerate(words):
        for alen in range(lo, min(hi, len(w)) + 1):
            a = w[:alen] if side == "prefix" else w[-alen:]
            counts[a] += 1
            index[a].append(i)
    total = len(words)
    fams, used = [], set()
    for affix, _ in counts.most_common(CANDIDATE_POOL):
        members = [i for i in index.get(affix, ()) if i not in used]
        cov = len(members) / total
        if cov < min_cov or cov > max_cov:
            continue
        if any(affix.startswith(e) or e.startswith(affix) for e in fams):
            continue
        fams.append(affix)
        used.update(members)
        if len(fams) >= n:
            break
    return fams


def classify_by(words, affixes, side):
    match = str.startswith if side == "prefix" else str.endswith
    out = []
    for w in words:
        lab = "OTHER"
        for a in affixes:
            if match(w, a):
                lab = a
                break
        out.append(lab)
    return out


def self_clustering(classes):
    total = len(classes) - 1
    if total <= 0:
        return None
    same, src, dst = Counter(), Counter(), Counter()
    for i in range(total):
        a, b = classes[i], classes[i + 1]
        src[a] += 1
        dst[b] += 1
        if a == b:
            same[a] += 1
    ratios = []
    for c in set(classes):
        if src[c] > MIN_CLASS_N and dst[c] > MIN_CLASS_N:
            exp = src[c] * (dst[c] / total)
            if exp > 1:
                ratios.append(same[c] / exp)
    return float(np.mean(ratios)) if ratios else None


def measure(tokens):
    pfx = detect_affixes(tokens, "prefix")
    sfx = detect_affixes(tokens, "suffix")
    if len(pfx) < 2 or len(sfx) < 2:
        return None
    p = self_clustering(classify_by(tokens, pfx, "prefix"))
    s = self_clustering(classify_by(tokens, sfx, "suffix"))
    if not p or not s:
        return None
    ratio = p / s
    if p > 1.1 and s > 1.1:
        bucket = ("SYMM-HIGH" if 0.80 <= ratio <= 1.25
                  else ("PREFIX-DOM" if ratio > 1.25 else "SUFFIX-DOM"))
    elif s > 1.1:
        bucket = "SUFFIX-DOM"
    elif p > 1.1:
        bucket = "PREFIX-DOM"
    else:
        bucket = "SYMM-LOW"
    c = Counter(tokens)
    return {
        "prefix_sc": round(p, 3), "suffix_sc": round(s, 3),
        "ratio": round(ratio, 3), "bucket": bucket,
        "n_tokens": len(tokens), "n_types": len(c),
        "ttr": round(len(c) / len(tokens), 3),
        "hapax_pct": round(100 * sum(1 for v in c.values() if v == 1) / len(c), 1),
        "detected_prefixes": pfx, "detected_suffixes": sfx,
    }


# ─── Generator ───────────────────────────────────────────────────────────────
def make_stems(rng, n_stems, zipf_s=1.1):
    """Heavy-tailed stem inventory. Item 7 is engineered here."""
    stems, seen = [], set()
    while len(stems) < n_stems:
        ln = int(rng.integers(1, 5))
        s = "".join(rng.choice(list(STEM_CHARS), ln))
        if s not in seen:
            seen.add(s)
            stems.append(s)
    ranks = np.arange(1, n_stems + 1)
    w = 1.0 / ranks ** zipf_s
    return stems, w / w.sum()


def generate(rng, n_lines, mean_line_len, p_prefix_stay, p_suffix_stay,
             n_stems, zipf_s):
    """Two independent Markov chains — one over prefixes, one over suffixes.

    Item 5 is engineered here. p_prefix_stay and p_suffix_stay directly set the
    self-transition rate of each chain, and therefore prefix SC and suffix SC.
    """
    stems, sw = make_stems(rng, n_stems, zipf_s)
    np_, ns = len(PREFIXES), len(SUFFIXES)
    lines = []
    for _ in range(n_lines):
        ln = max(2, int(rng.poisson(mean_line_len)))
        pi = int(rng.integers(np_))
        si = int(rng.integers(ns))
        toks = []
        for _ in range(ln):
            # prefix chain
            if rng.random() >= p_prefix_stay:
                pi = int(rng.integers(np_))
            # suffix chain, independent of the prefix chain
            if rng.random() >= p_suffix_stay:
                si = int(rng.integers(ns))
            stem = stems[int(rng.choice(len(stems), p=sw))]
            toks.append(PREFIXES[pi] + stem + SUFFIXES[si])
        lines.append(toks)
    return lines


def flat(lines):
    return [t for l in lines for t in l]


def check_items(m):
    """Item 5 and item 7 pass/fail against the manuscript's own thresholds."""
    item5 = m["bucket"] == "SYMM-HIGH"
    item7 = (m["hapax_pct"] >= 65.0 and 0.18 <= m["ttr"] <= 0.30)
    return item5, item7


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tune", action="store_true",
                    help="grid search over generator parameters")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    print("=" * 78)
    print("ADVERSARIAL CONSTRUCTED CONTROL — TARGETING MVE ITEMS 5 AND 7")
    print("=" * 78)
    print(f"Targets: SYMM-HIGH bucket; hapax >=65%, TTR 0.18-0.30")
    print(f"Manuscript reference: prefix {TARGET['prefix_sc']}, "
          f"suffix {TARGET['suffix_sc']}, ratio {TARGET['ps_ratio']}, "
          f"hapax {TARGET['hapax_pct']}%, TTR {TARGET['ttr']}\n")

    mean_len = TARGET["n_tokens"] / TARGET["n_lines"]

    if args.tune:
        grid = []
        for pp in [0.14, 0.18, 0.22, 0.40, 0.60]:
            for ps in [0.18, 0.22, 0.26, 0.45, 0.65]:
                for ns_ in [1500, 2000, 8000]:
                    grid.append((pp, ps, ns_))
        print(f"Tuning over {len(grid)} configurations\n")
        print(f"{'p_pfx':>6}{'p_sfx':>7}{'stems':>7}{'pfxSC':>8}{'sfxSC':>8}"
              f"{'ratio':>7}{'hapax':>7}{'TTR':>6}  {'bucket':<11}{'5':>2}{'7':>2}")
        print("-" * 78)
        best = None
        for pp, ps, ns_ in grid:
            lines = generate(rng, TARGET["n_lines"], mean_len, pp, ps, ns_, 1.4)
            m = measure(flat(lines))
            if not m:
                continue
            i5, i7 = check_items(m)
            print(f"{pp:>6.2f}{ps:>7.2f}{ns_:>7}{m['prefix_sc']:>8.2f}"
                  f"{m['suffix_sc']:>8.2f}{m['ratio']:>7.2f}{m['hapax_pct']:>7.1f}"
                  f"{m['ttr']:>6.2f}  {m['bucket']:<11}"
                  f"{'Y' if i5 else 'n':>2}{'Y' if i7 else 'n':>2}")
            if i5 and i7:
                score = (abs(m["ratio"] - TARGET["ps_ratio"])
                         + abs(m["hapax_pct"] - TARGET["hapax_pct"]) / 100)
                if best is None or score < best[0]:
                    best = (score, pp, ps, ns_, m)
        if best:
            _, pp, ps, ns_, m = best
            print(f"\nBEST CONFIG SATISFYING BOTH: p_prefix_stay={pp}, "
                  f"p_suffix_stay={ps}, n_stems={ns_}")
        else:
            print("\nNo configuration satisfied both items.")
        chosen = best
    else:
        # Winning configuration found by --tune: satisfies items 5 AND 7,
        # and lands closest to the manuscript's own SC magnitudes.
        pp, ps, ns_ = 0.14, 0.18, 1500
        lines = generate(rng, TARGET["n_lines"], mean_len, pp, ps, ns_, 1.4)
        m = measure(flat(lines))
        i5, i7 = check_items(m)
        chosen = ((0, pp, ps, ns_, m) if (i5 and i7) else None)
        print(f"Single run: p_prefix_stay={pp}, p_suffix_stay={ps}, n_stems={ns_}")

    # Report the chosen / default configuration in full
    if chosen:
        _, pp, ps, ns_, m = chosen
    i5, i7 = check_items(m)

    print("\n" + "=" * 78)
    print("RESULT")
    print("=" * 78)
    print(f"{'':<22}{'generated':>12}{'manuscript':>13}")
    print(f"{'prefix SC':<22}{m['prefix_sc']:>12.3f}{TARGET['prefix_sc']:>13.3f}")
    print(f"{'suffix SC':<22}{m['suffix_sc']:>12.3f}{TARGET['suffix_sc']:>13.3f}")
    print(f"{'ratio':<22}{m['ratio']:>12.3f}{TARGET['ps_ratio']:>13.3f}")
    print(f"{'bucket':<22}{m['bucket']:>12}{'SYMM-HIGH':>13}")
    print(f"{'hapax %':<22}{m['hapax_pct']:>12.1f}{TARGET['hapax_pct']:>13.1f}")
    print(f"{'TTR':<22}{m['ttr']:>12.3f}{TARGET['ttr']:>13.3f}")
    print(f"{'types':<22}{m['n_types']:>12}")
    print(f"\nITEM 5 (bidirectional SYMM-HIGH): {'PASS' if i5 else 'FAIL'}")
    print(f"ITEM 7 (open vocabulary):         {'PASS' if i7 else 'FAIL'}")

    if i5 and i7:
        verdict = ("BOTH ITEMS SATISFIED. All 7 MVE checklist items are "
                   "engineerable by a constructed system. The checklist does "
                   "not discriminate encoded natural language from a "
                   "sufficiently motivated constructed system.")
    elif i5 or i7:
        verdict = (f"ONE ITEM SATISFIED ({'5' if i5 else '7'}). The other "
                   "resisted direct engineering in this implementation.")
    else:
        verdict = ("NEITHER ITEM SATISFIED. The first-pass conclusion stands "
                   "for this generator class.")
    print(f"\nVERDICT: {verdict}")

    out = {
        "description": ("Adversarial constructed control explicitly engineering "
                        "MVE items 5 and 7, which durable_findings.md §4 "
                        "identifies as the only discriminating items."),
        "method": ("Tokens emitted as PREFIX+STEM+SUFFIX. Two independent "
                   "Markov chains over adjacent tokens — one on prefix "
                   "identity, one on suffix identity — with tunable "
                   "self-transition probabilities, which set prefix SC and "
                   "suffix SC directly (item 5). Large heavy-tailed stem "
                   "inventory yields mostly-unique full tokens (item 7). No "
                   "linguistic content of any kind."),
        "seed": SEED,
        "config": {"p_prefix_stay": pp, "p_suffix_stay": ps, "n_stems": ns_},
        "targets": TARGET,
        "generated": m,
        "item_5_bidirectional_symmhigh": bool(i5),
        "item_7_open_vocabulary": bool(i7),
        "verdict": verdict,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "adversarial_control_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
