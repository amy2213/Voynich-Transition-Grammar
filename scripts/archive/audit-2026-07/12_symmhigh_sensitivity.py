#!/usr/bin/env python3
"""
12_symmhigh_sensitivity.py — Is SYMM-HIGH robust to the affix-detection
parameters, or an artifact of one parameterization?

WHY THIS IS NOW THE HIGHEST-PRIORITY TEST
-----------------------------------------
The published prefix/suffix ratio was 0.99, comfortably inside the SYMM-HIGH
band (0.80-1.25). Three independent code paths now agree the ratio is
approximately 0.84:

    scripts/10_prefix_suffix_analysis.py   0.852  [95% CI 0.815, 0.966]
    scripts/05_cross_transcription.py      0.836
    (published, not reproducible)          0.99

0.836 sits 0.036 above the SYMM-HIGH/SUFFIX-DOM boundary at 0.80, and the
bootstrap lower bound is 0.815 — 0.015 of margin. At 0.99 the bucket
assignment was not in question. At 0.84 it is, and it must be shown to be
stable before the finding can be stated categorically.

WHAT THIS SCRIPT TESTS
----------------------
A grid over every free parameter of the affix-detection procedure:

    n_families   how many affix families are detected per direction
    affix_len    candidate affix character length range
    coverage     min/max share of the corpus a family may cover

For each cell it computes prefix SC, suffix SC, ratio, and bucket for Voynich
and for every comparator, using the same procedure everywhere.

TWO DISTINCT QUESTIONS, REPORTED SEPARATELY
-------------------------------------------
1. BUCKET STABILITY  -- what fraction of parameterizations put Voynich in
   SYMM-HIGH?
2. UNIQUENESS        -- in what fraction does Voynich remain the ONLY system
   in SYMM-HIGH?

(2) is the claim the paper actually makes. (1) can degrade without (2) failing,
and (2) is what should be reported. A finding that survives (2) across the grid
is considerably stronger than a single point estimate with a bootstrap CI.

USAGE
    python scripts/12_symmhigh_sensitivity.py            # full grid
    python scripts/12_symmhigh_sensitivity.py --quick    # reduced grid
    python scripts/12_symmhigh_sensitivity.py --cap 60000

OUTPUT
    results/symmhigh_sensitivity_results.json
"""

import argparse
import itertools
import json
import os
import re
import sys
import tarfile
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
SEED = 42
MIN_CLASS_N = 10
CANDIDATE_POOL = 80

# ─── Parameter grid ──────────────────────────────────────────────────────────
GRID_FULL = {
    "n_families": [3, 4, 5, 6, 8],
    "affix_len": [(2, 2), (2, 3), (2, 4), (3, 3)],
    "coverage": [(0.01, 0.25), (0.02, 0.20), (0.03, 0.15), (0.05, 0.30)],
}
GRID_QUICK = {
    "n_families": [4, 5, 6],
    "affix_len": [(2, 2), (2, 3)],
    "coverage": [(0.02, 0.20), (0.03, 0.15)],
}

BUCKET_LO, BUCKET_HI = 0.80, 1.25
SC_THRESHOLD = 1.1


# ─── Core measurement (parameterized) ────────────────────────────────────────
def detect_affixes(words, side, n, lo_len, hi_len, min_cov, max_cov):
    counts = Counter()
    index = defaultdict(list)
    for i, w in enumerate(words):
        for alen in range(lo_len, min(hi_len, len(w)) + 1):
            a = w[:alen] if side == "prefix" else w[-alen:]
            counts[a] += 1
            index[a].append(i)
    total = len(words)
    if not total:
        return []
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


def bucket_of(p, s):
    if p is None or s is None or not s:
        return "UNDEFINED"
    r = p / s
    if p > SC_THRESHOLD and s > SC_THRESHOLD:
        return ("SYMM-HIGH" if BUCKET_LO <= r <= BUCKET_HI
                else ("PREFIX-DOM" if r > BUCKET_HI else "SUFFIX-DOM"))
    if s > SC_THRESHOLD:
        return "SUFFIX-DOM"
    if p > SC_THRESHOLD:
        return "PREFIX-DOM"
    return "SYMM-LOW"


def measure(words, n, alen, cov):
    pfx = detect_affixes(words, "prefix", n, alen[0], alen[1], cov[0], cov[1])
    sfx = detect_affixes(words, "suffix", n, alen[0], alen[1], cov[0], cov[1])
    if len(pfx) < 2 or len(sfx) < 2:
        return None
    p = self_clustering(classify_by(words, pfx, "prefix"))
    s = self_clustering(classify_by(words, sfx, "suffix"))
    if p is None or s is None or not s:
        return None
    return {"prefix_sc": round(p, 4), "suffix_sc": round(s, 4),
            "ratio": round(p / s, 4), "bucket": bucket_of(p, s),
            "n_prefix_fams": len(pfx), "n_suffix_fams": len(sfx)}


# ─── Corpora ─────────────────────────────────────────────────────────────────
def load_voynich():
    p = os.path.join(DATA_DIR, "voynich",
                     "AncientLanguages_Voynich_snapshot", "train.parquet")
    df = pd.read_parquet(p)
    zl = df[df["source_name"] == "Zandbergen-Landini"]
    toks = []
    for t in zl["text"]:
        if isinstance(t, str):
            toks += [x for x in t.strip().split()
                     if not x.startswith("%") and not x.startswith("{")
                     and x not in ["-", "=", "!"]]
    return toks


def load_leipzig(folder, tarball, regex, cap):
    tp = os.path.join(DATA_DIR, "cross_linguistic", folder, tarball)
    if not os.path.exists(tp):
        return None
    try:
        with tarfile.open(tp, "r:gz") as tar:
            for m in tar.getmembers():
                if "sentences" in m.name:
                    f = tar.extractfile(m)
                    if not f:
                        continue
                    lr = f.read().decode("utf-8", errors="ignore").splitlines()
                    texts = [l.split("\t", 1)[1].strip() if "\t" in l else l.strip()
                             for l in lr]
                    w = [x for x in re.findall(regex, " ".join(texts).lower())
                         if len(x) >= 2]
                    return w[:cap]
    except Exception as e:
        print(f"  ! {folder}: {e}")
    return None


def load_plain(folder, fname, regex, cap):
    fp = os.path.join(DATA_DIR, "cross_linguistic", folder, fname)
    if not os.path.exists(fp):
        return None
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    s = text.find("*** START")
    if s > -1:
        text = text[text.find("\n", s) + 1:]
    e = text.find("*** END")
    if e > -1:
        text = text[:e]
    return [w for w in re.findall(regex, text.lower()) if len(w) >= 2][:cap]


def load_words_file(folder, fname, cap):
    fp = os.path.join(DATA_DIR, "cross_linguistic", folder, fname)
    if not os.path.exists(fp):
        return None
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        return [w for w in re.split(r"\s+", f.read().lower()) if len(w) >= 2][:cap]


LATIN = r"[a-z]+"
COMPARATORS = [
    ("Arabic", "leipzig", ("arabic", "ara_wikipedia_2021_100K.tar.gz", r"[\u0621-\u064a]+")),
    ("Latin", "leipzig", ("latin", "lat_wikipedia_2021_100K.tar.gz", LATIN)),
    ("Estonian", "leipzig", ("estonian", "ekk_wikipedia_2021_100K.tar.gz", r"[a-zõäöüšž]+")),
    ("Hebrew", "leipzig", ("hebrew", "heb_wikipedia_2021_100K.tar.gz", r"[\u05d0-\u05ea]+")),
    ("Finnish", "leipzig", ("finnish", "fin_wikipedia_2021_100K.tar.gz", r"[a-zäöå]+")),
    ("Hungarian", "leipzig", ("hungarian", "hun_wikipedia_2021_100K.tar.gz", r"[a-záéíóöőúüű]+")),
    ("Turkish", "leipzig", ("turkish", "tur_wikipedia_2021_100K.tar.gz", r"[a-zçğıöşü]+")),
    ("Italian", "leipzig", ("italian", "ita_wikipedia_2021_100K.tar.gz", r"[a-zàèéìòù]+")),
    ("N. Azerbaijani", "leipzig", ("north_azerbaijani", "aze_wikipedia_2021_100K.tar.gz", r"[a-zçəğıöşü]+")),
    ("Swahili", "leipzig", ("swahili", "swa_wikipedia_2021_100K.tar.gz", LATIN)),
    ("Georgian", "leipzig", ("georgian", "kat_wikipedia_2021_100K.tar.gz", r"[\u10d0-\u10f0]+")),
    ("Tagalog", "leipzig", ("tagalog", "tgl_wikipedia_2021_100K.tar.gz", LATIN)),
    ("Middle English", "plain", ("middle_english", "chaucer_canterbury_tales_22120.txt", LATIN)),
    ("KJV English", "plain", ("kjv_english", "king_james_bible_10900.txt", LATIN)),
    ("Ottoman Turkish", "words", ("ottoman_turkish", "ota_dudu_words.txt")),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--cap", type=int, default=80_000,
                    help="token cap per comparator (Voynich always full)")
    args = ap.parse_args()

    grid = GRID_QUICK if args.quick else GRID_FULL
    cells = list(itertools.product(grid["n_families"], grid["affix_len"],
                                   grid["coverage"]))
    rng = np.random.default_rng(SEED)

    print("=" * 78)
    print("SYMM-HIGH SENSITIVITY SWEEP")
    print("=" * 78)
    print(f"Grid: {len(cells)} parameter cells "
          f"(n_families x affix_len x coverage)")
    print(f"Comparator token cap: {args.cap}\n")

    # Corpus loading (gzipped Leipzig tarballs) dominates runtime and is
    # identical across grid cells, so it is cached to disk. Delete the cache
    # file to force a reload after changing --cap or the corpus set.
    import pickle
    cache = os.path.join(PROJECT_ROOT, "data", ".corpus_cache_%d.pkl" % args.cap)
    corpora = None
    if os.path.exists(cache):
        try:
            with open(cache, "rb") as f:
                corpora = pickle.load(f)
            print("Loaded %d systems from cache" % len(corpora), flush=True)
        except Exception as e:
            print("Cache unreadable (%s); reloading." % e, flush=True)
            corpora = None
    if corpora is None:
        voy = load_voynich()
        shuf = voy.copy()
        rng.shuffle(shuf)
        print("Voynich: %d tokens (full corpus)" % len(voy), flush=True)
        corpora = {"VOYNICH": voy, "Gibberish (shuffled)": shuf}
        for label, kind, spec in COMPARATORS:
            w = (load_leipzig(*spec, args.cap) if kind == "leipzig" else
                 load_plain(*spec, args.cap) if kind == "plain" else
                 load_words_file(*spec, args.cap))
            if w and len(w) >= 1000:
                corpora[label] = w
                print("  %-22s %d tokens" % (label, len(w)), flush=True)
            else:
                print("  ! %s: unavailable" % label, flush=True)
        # Write atomically: a run interrupted mid-dump would otherwise leave a
        # truncated cache that fails to load on the next invocation.
        tmp = cache + ".tmp"
        with open(tmp, "wb") as f:
            pickle.dump(corpora, f)
        os.replace(tmp, cache)
    print("Systems: %d\n" % len(corpora), flush=True)

    # measure every system in every cell
    per_cell = []
    for _ci, (n, alen, cov) in enumerate(cells, 1):
        print("  cell %d/%d" % (_ci, len(cells)), flush=True)
        cell = {"n_families": n, "affix_len": list(alen),
                "coverage": list(cov), "systems": {}}
        for label, words in corpora.items():
            m = measure(words, n, alen, cov)
            if m:
                cell["systems"][label] = m
        v = cell["systems"].get("VOYNICH")
        if v:
            others_high = [k for k, r in cell["systems"].items()
                           if k != "VOYNICH" and r["bucket"] == "SYMM-HIGH"]
            cell["voynich_bucket"] = v["bucket"]
            cell["voynich_ratio"] = v["ratio"]
            cell["voynich_unique_symmhigh"] = (v["bucket"] == "SYMM-HIGH"
                                               and not others_high)
            cell["other_symmhigh"] = others_high
        per_cell.append(cell)

    valid = [c for c in per_cell if "voynich_bucket" in c]
    n_high = sum(1 for c in valid if c["voynich_bucket"] == "SYMM-HIGH")
    n_uniq = sum(1 for c in valid if c["voynich_unique_symmhigh"])
    ratios = [c["voynich_ratio"] for c in valid]
    buckets = Counter(c["voynich_bucket"] for c in valid)

    print(f"{'cell':<34}{'ratio':>8}  bucket        others in SYMM-HIGH")
    print("-" * 78)
    for c in valid:
        tag = f"n={c['n_families']} len={tuple(c['affix_len'])} cov={tuple(c['coverage'])}"
        others = ",".join(c["other_symmhigh"]) or "-"
        print(f"{tag:<34}{c['voynich_ratio']:>8.3f}  {c['voynich_bucket']:<14}{others}")

    print("\n" + "=" * 78)
    print(f"Cells evaluated:                 {len(valid)}/{len(cells)}")
    print(f"Voynich ratio range:             {min(ratios):.3f} - {max(ratios):.3f} "
          f"(median {float(np.median(ratios)):.3f})")
    print(f"Voynich bucket distribution:     {dict(buckets)}")
    print(f"Voynich in SYMM-HIGH:            {n_high}/{len(valid)} "
          f"({100*n_high/len(valid):.0f}%)")
    print(f"Voynich UNIQUELY in SYMM-HIGH:   {n_uniq}/{len(valid)} "
          f"({100*n_uniq/len(valid):.0f}%)")

    # which comparators ever reach SYMM-HIGH
    intruders = Counter()
    for c in valid:
        for k in c["other_symmhigh"]:
            intruders[k] += 1
    if intruders:
        print("\nComparators reaching SYMM-HIGH in at least one cell:")
        for k, n in intruders.most_common():
            print(f"  {k:<24} {n}/{len(valid)} cells")
    else:
        print("\nNo comparator reaches SYMM-HIGH in any cell.")

    out = {
        "description": ("Sensitivity of the SYMM-HIGH bucket assignment to the "
                        "affix-detection parameters. Tests bucket stability and, "
                        "separately, uniqueness — the latter being the claim the "
                        "paper makes."),
        "bucket_rule": {"sc_threshold": SC_THRESHOLD,
                        "symmhigh_ratio_band": [BUCKET_LO, BUCKET_HI]},
        "grid": {k: [list(x) if isinstance(x, tuple) else x for x in v]
                 for k, v in grid.items()},
        "comparator_token_cap": args.cap,
        "seed": SEED,
        "summary": {
            "cells_evaluated": len(valid),
            "voynich_ratio_min": min(ratios),
            "voynich_ratio_max": max(ratios),
            "voynich_ratio_median": float(np.median(ratios)),
            "voynich_bucket_distribution": dict(buckets),
            "voynich_symmhigh_fraction": round(n_high / len(valid), 3),
            "voynich_unique_symmhigh_fraction": round(n_uniq / len(valid), 3),
            "comparators_ever_symmhigh": dict(intruders),
        },
        "cells": per_cell,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "symmhigh_sensitivity_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
