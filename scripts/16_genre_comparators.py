#!/usr/bin/env python3
"""
16_genre_comparators.py — Genre and period-matched comparator corpora

THE OBJECTION THIS ADDRESSES
----------------------------
All 16 existing comparators are modern Wikipedia prose (Leipzig 100K corpora),
plus two English literary texts. The Voynich manuscript is a 15th-century
codex whose visible register is herbal, pharmaceutical, balneological and
recipe-like: short repetitive entries, heavy nominal repetition, formulaic
constructions, minimal narrative connective tissue.

That register difference is a live confound for the SYMM-HIGH result.
Self-clustering measures whether adjacent tokens share affix families — and a
recipe list ("take X, take Y, mix with Z") plausibly clusters differently from
encyclopedia prose regardless of language. A finding that Voynich is unlike
modern Wikipedia in 16 languages is weaker than it sounds if no comparator
shares its register.

WHAT THIS SCRIPT DOES
---------------------
Fetches period- and register-adjacent corpora and runs the identical symmetric
affix-detection procedure used in scripts 10 and 12.

    Pliny, Naturalis Historia (Latin)  -- the naturalist/herbal register
        itself, and the direct textual ancestor of the medieval herbal
        tradition the manuscript's illustrations belong to. Ancient rather
        than medieval, but register-matched, which is the harder criterion.

    Medieval Latin prose (Latin Library) -- period-matched: chronicle,
        epistolary and didactic prose from the 8th-14th centuries.

    Middle English (Chaucer) and KJV English -- already bundled; re-measured
        here for a like-for-like comparison in the same table.

HONEST LIMITATION — READ THIS BEFORE CITING
-------------------------------------------
The genuinely genre-matched targets are the medieval herbal and
pharmacological corpus: the Trotula, Circa instans (Platearius), Macer
Floridus De viribus herbarum, the Herbarium of Pseudo-Apuleius, and Bald's
Leechbook. NONE of these is available as freely fetchable plaintext. They exist
in scholarly editions (Green's Trotula, Cockayne's Leechdoms, the Corpus
Corporum and dMGH collections) that require either manual extraction or
institutional access.

This script therefore delivers register-ADJACENT rather than register-MATCHED
comparators. That is an improvement on modern Wikipedia prose, but it does NOT
close the objection. Closing it requires sourcing the texts above by hand.
The script is structured so that dropping a plaintext file into
data/raw/genre_matched/ and adding one line to LOCAL_CORPORA incorporates it.

USAGE
    python scripts/16_genre_comparators.py
    python scripts/16_genre_comparators.py --no-fetch   # local files only

OUTPUT
    results/genre_comparators_results.json
    data/raw/genre_matched/*.txt  (cached downloads)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
GENRE_DIR = os.path.join(DATA_DIR, "genre_matched")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

MIN_CLASS_N = 10
CANDIDATE_POOL = 80
N_FAMILIES = 5
UA = {"User-Agent": "Mozilla/5.0 (research; corpus linguistics)"}

# Pliny Naturalis Historia — books 1-37, naturalist/herbal register
PLINY = [f"https://www.thelatinlibrary.com/pliny.nh{i}.html" for i in range(1, 38)]

# Medieval Latin prose — period-matched
MEDIEVAL = [
    "https://www.thelatinlibrary.com/ein.html",
    "https://www.thelatinlibrary.com/carm.bur.html",
    "https://www.thelatinlibrary.com/asserius.html",
    "https://www.thelatinlibrary.com/annalesregnifrancorum.html",
    "https://www.thelatinlibrary.com/albertofaix.html",
    "https://www.thelatinlibrary.com/capellanus.html",
    "https://www.thelatinlibrary.com/alanus.html",
    "https://www.thelatinlibrary.com/aelredus.html",
    "https://www.thelatinlibrary.com/adso.html",
    "https://www.thelatinlibrary.com/albertanus.html",
    "https://www.thelatinlibrary.com/cato.dis.html",
    "https://www.thelatinlibrary.com/boethiusdacia.html",
    "https://www.thelatinlibrary.com/xanten.html",
    "https://www.thelatinlibrary.com/annalesvedastini.html",
    "https://www.thelatinlibrary.com/epistaustras.html",
]

# Already-bundled corpora, re-measured here for like-for-like comparison
LOCAL_CORPORA = [
    ("Middle English (Chaucer)", "middle_english",
     "chaucer_canterbury_tales_22120.txt", "Middle English, 14c verse"),
    ("KJV English", "kjv_english",
     "king_james_bible_10900.txt", "Early Modern English, 17c"),
]


# ─── Measurement (identical to scripts 10 and 12) ────────────────────────────
def detect_affixes(words, side, n=N_FAMILIES, lo=2, hi=3,
                   min_cov=0.02, max_cov=0.20):
    counts, index = Counter(), defaultdict(list)
    for i, w in enumerate(words):
        for alen in range(lo, min(hi, len(w)) + 1):
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
    if not p or not s:
        return "UNDEFINED"
    r = p / s
    if p > 1.1 and s > 1.1:
        return ("SYMM-HIGH" if 0.80 <= r <= 1.25
                else ("PREFIX-DOM" if r > 1.25 else "SUFFIX-DOM"))
    if s > 1.1:
        return "SUFFIX-DOM"
    if p > 1.1:
        return "PREFIX-DOM"
    return "SYMM-LOW"


def measure(words):
    pfx = detect_affixes(words, "prefix")
    sfx = detect_affixes(words, "suffix")
    if len(pfx) < 2 or len(sfx) < 2:
        return None
    p = self_clustering(classify_by(words, pfx, "prefix"))
    s = self_clustering(classify_by(words, sfx, "suffix"))
    if not p or not s:
        return None
    c = Counter(words)
    return {"prefix_sc": round(p, 3), "suffix_sc": round(s, 3),
            "ratio": round(p / s, 3), "bucket": bucket_of(p, s),
            "n_tokens": len(words), "n_types": len(c),
            "ttr": round(len(c) / len(words), 3),
            "hapax_pct": round(100 * sum(1 for v in c.values() if v == 1) / len(c), 1),
            "detected_prefixes": pfx, "detected_suffixes": sfx}


# ─── Fetching ────────────────────────────────────────────────────────────────
def strip_html(h):
    h = re.sub(r"(?is)<script.*?</script>", " ", h)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&")
    return h


def fetch(url, retries=2):
    for _ in range(retries):
        try:
            r = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(r, timeout=25).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(1.5)
    return None


def fetch_group(name, urls, cache_name):
    os.makedirs(GENRE_DIR, exist_ok=True)
    path = os.path.join(GENRE_DIR, cache_name)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    chunks, ok = [], 0
    for u in urls:
        h = fetch(u)
        if h:
            chunks.append(strip_html(h))
            ok += 1
        time.sleep(0.4)
    if not chunks:
        return None
    text = "\n".join(chunks)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"    fetched {ok}/{len(urls)} documents for {name}")
    return text


def latin_words(text, cap=400_000):
    text = re.sub(r"\b(The Latin Library|The Classics Page|Christian Latin"
                  r"|Medieval Latin|Neo-Latin)\b", " ", text)
    w = [x for x in re.findall(r"[a-z]+", text.lower()) if len(x) >= 2]
    return w[:cap]


def load_local(folder, fname, cap=400_000):
    fp = os.path.join(DATA_DIR, "cross_linguistic", folder, fname)
    if not os.path.exists(fp):
        return None
    with open(fp, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    s = text.find("*** START")
    if s > -1:
        text = text[text.find("\n", s) + 1:]
    e = text.find("*** END")
    if e > -1:
        text = text[:e]
    return [w for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 2][:cap]


def load_voynich():
    import pandas as pd
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true")
    args = ap.parse_args()

    print("=" * 78)
    print("GENRE- AND PERIOD-MATCHED COMPARATORS")
    print("=" * 78)

    systems = {}
    v = load_voynich()
    systems["VOYNICH"] = measure(v)
    systems["VOYNICH"]["register"] = "15c herbal/pharmaceutical codex"

    if not args.no_fetch:
        print("\nFetching:")
        for label, urls, cache, reg in [
            ("Pliny, Naturalis Historia", PLINY, "pliny_nh.txt",
             "Naturalist/herbal register, 1c CE Latin"),
            ("Medieval Latin prose", MEDIEVAL, "medieval_latin.txt",
             "Chronicle/epistolary/didactic, 8-14c Latin"),
        ]:
            t = fetch_group(label, urls, cache)
            if t:
                w = latin_words(t)
                if len(w) >= 5000:
                    m = measure(w)
                    if m:
                        m["register"] = reg
                        systems[label] = m
                else:
                    print(f"    {label}: too few tokens ({len(w)})")
            else:
                print(f"    {label}: fetch failed")

    for label, folder, fname, reg in LOCAL_CORPORA:
        w = load_local(folder, fname)
        if w and len(w) >= 5000:
            m = measure(w)
            if m:
                m["register"] = reg
                systems[label] = m

    print(f"\n{'System':<28}{'n':>9}{'Pfx SC':>8}{'Sfx SC':>8}{'Ratio':>8}"
          f"{'hapax':>7}  Bucket")
    print("-" * 78)
    for k, r in sorted(systems.items(), key=lambda x: -x[1]["prefix_sc"]):
        print(f"{k:<28}{r['n_tokens']:>9}{r['prefix_sc']:>8.2f}"
              f"{r['suffix_sc']:>8.2f}{r['ratio']:>8.2f}{r['hapax_pct']:>7.1f}"
              f"  {r['bucket']}")

    others_high = [k for k, r in systems.items()
                   if k != "VOYNICH" and r["bucket"] == "SYMM-HIGH"]
    print("-" * 78)
    print(f"Non-Voynich systems reaching SYMM-HIGH: "
          f"{', '.join(others_high) if others_high else 'none'}")

    out = {
        "description": ("Genre- and period-adjacent comparators, measured with "
                        "the identical symmetric affix-detection procedure used "
                        "in scripts 10 and 12."),
        "limitation": ("These are register-ADJACENT, not register-MATCHED. The "
                       "genuinely genre-matched corpus is the medieval herbal "
                       "and pharmacological tradition — Trotula, Circa instans, "
                       "Macer Floridus, Herbarium of Pseudo-Apuleius, Bald's "
                       "Leechbook — none of which is available as freely "
                       "fetchable plaintext. This script narrows the register "
                       "confound; it does not close it. Sourcing those texts "
                       "by hand remains outstanding."),
        "systems": systems,
        "non_voynich_symmhigh": others_high,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "genre_comparators_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
