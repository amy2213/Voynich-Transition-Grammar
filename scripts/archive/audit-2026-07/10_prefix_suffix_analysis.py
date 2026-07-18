#!/usr/bin/env python3
"""
10_prefix_suffix_analysis.py — GENERATES results/prefix_suffix_analysis.json

WHY THIS SCRIPT EXISTS
----------------------
Prior to this script, results/prefix_suffix_analysis.json was a committed
artifact with no generating code in the repository. No script in the pipeline
(01-09) computed suffix-side self-clustering at all: 02_cross_linguistic.py
builds prefix families only (`w.startswith(prefix)`) and reports a single
`mean_self_cluster`. The headline SYMM-HIGH result — prefix SC 1.52x,
suffix SC 1.54x, ratio 0.99 — therefore could not be reconstructed from raw
data by following the documented workflow, and tests/test_canonical_values.py
was asserting a static file against itself.

This script closes that gap.

THE ASYMMETRY IT ALSO FIXES
---------------------------
The committed file's own `method` field states:

    "Auto-detected top-5 affix families (2-3 char, 2-20% coverage).
     Voynich uses standard EVA prefix families for prefix SC."

That is a methodological asymmetry: Voynich was scored using hand-picked EVA
families already selected for structural salience, while every comparator was
scored using automatically discovered families. That can inflate Voynich's
prefix SC relative to comparators for reasons unrelated to the manuscript.

This script applies ONE detection procedure to ALL systems, Voynich included,
and reports the legacy asymmetric variant alongside it so the delta is visible
and quantified rather than assumed harmless.

METHOD (identical for every system)
-----------------------------------
1. Tokenize.
2. Detect top-K prefix families: candidate affixes of length 2-3, keep those
   with coverage in [MIN_COV, MAX_COV], greedily, non-nested, K families.
3. Detect top-K suffix families by the mirror-image procedure (endswith).
4. Assign each token to a family (first match, documented order) or OTHER.
5. Self-clustering for class c = observed(c->c) / expected(c->c) under
   independence, where expected = src[c] * (dst[c]/total). Mean over classes
   with src[c] > MIN_CLASS_N and dst[c] > MIN_CLASS_N.
6. prefix_sc = mean over prefix-partition; suffix_sc = mean over suffix-
   partition; ratio = prefix_sc / suffix_sc.
7. Bootstrap 95% CI by resampling contiguous token blocks (preserves local
   sequential dependence, which an i.i.d. token bootstrap would destroy).

Bucket definitions are unchanged from the committed file so results remain
comparable.

USAGE
  python scripts/10_prefix_suffix_analysis.py
  python scripts/10_prefix_suffix_analysis.py --sentences 20000   # legacy table
  python scripts/10_prefix_suffix_analysis.py --bootstrap 0       # skip CIs
  python scripts/10_prefix_suffix_analysis.py --out results/prefix_suffix_analysis.json

OUTPUT
  results/prefix_suffix_analysis_generated.json   (default; does not clobber
  the committed artifact so you can diff generated vs. published)
"""

import argparse
import json
import os
import random
import re
import sys
import tarfile
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

SEED = 42
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

# ─── Detection parameters (identical for every system) ───────────────────────
N_FAMILIES = 5
AFFIX_MIN_LEN = 2
AFFIX_MAX_LEN = 3
MIN_COV = 0.02
MAX_COV = 0.20
CANDIDATE_POOL = 80
MIN_CLASS_N = 10
MAX_TOKENS = 400_000          # cap for tractability; actual n is reported
BOOTSTRAP_N = 500
BLOCK_SIZE = 50               # contiguous block bootstrap
BOOTSTRAP_SUBSAMPLE = 50_000  # comparator CI subsample cap

BUCKET_DEFINITIONS = {
    "SYMM-HIGH": "Both prefix and suffix SC > 1.1x, ratio between 0.80 and 1.25",
    "SUFFIX-DOM": "Suffix SC > 1.1x and ratio < 0.80, OR suffix > 1.1x and prefix < 1.1x",
    "PREFIX-DOM": "Prefix SC > 1.1x and ratio > 1.25, OR prefix > 1.1x and suffix < 1.1x",
    "SYMM-LOW": "Both prefix and suffix SC < 1.1x",
}

# ─── Legacy hand-picked EVA families (for the asymmetry comparison only) ─────
def is_qok(t):   return t.startswith("qok")
def is_ok(t):    return t.startswith("ok") and not t.startswith("qok")
def is_ot(t):    return t.startswith("ot")
def is_chedy(t): return any(p in t for p in ["chedy", "shedy", "chey", "shey"])
def is_aiin(t):  return "aiin" in t or "ain" in t

EVA_ORDER = [("QOK", is_qok), ("OK", is_ok), ("OT", is_ot),
             ("CHEDY", is_chedy), ("AIIN", is_aiin)]


def classify_eva_fixed(tok):
    for name, fn in EVA_ORDER:
        if fn(tok):
            return name
    return "OTHER"


# ─── Symmetric affix detection ───────────────────────────────────────────────
def detect_affixes(words, side, n=N_FAMILIES):
    """Detect top-n affix families. side='prefix' or 'suffix'.

    Identical algorithm both directions and for every corpus. Returns an
    ordered list of affix strings.
    """
    counts = Counter()
    for w in words:
        for alen in range(AFFIX_MIN_LEN, min(AFFIX_MAX_LEN, len(w)) + 1):
            counts[w[:alen] if side == "prefix" else w[-alen:]] += 1

    total = len(words)
    if total == 0:
        return []

    match = (str.startswith if side == "prefix" else str.endswith)
    fams, used = [], set()
    for affix, _ in counts.most_common(CANDIDATE_POOL):
        members = [w for w in words if match(w, affix) and w not in used]
        cov = len(members) / total
        if cov < MIN_COV or cov > MAX_COV:
            continue
        # reject nested affixes (same rule both directions)
        if any(affix.startswith(e) or e.startswith(affix) for e in fams):
            continue
        fams.append(affix)
        used.update(members)
        if len(fams) >= n:
            break
    return fams


def classify_by_affixes(words, affixes, side):
    match = (str.startswith if side == "prefix" else str.endswith)
    out = []
    for w in words:
        lab = "OTHER"
        for a in affixes:
            if match(w, a):
                lab = a.upper()
                break
        out.append(lab)
    return out


# ─── Self-clustering ─────────────────────────────────────────────────────────
def self_clustering(classes):
    """Mean observed/expected self-transition ratio across valid classes."""
    total = len(classes) - 1
    if total <= 0:
        return None
    tr = defaultdict(int)
    src = Counter()
    dst = Counter()
    for i in range(total):
        a, b = classes[i], classes[i + 1]
        src[a] += 1
        dst[b] += 1
        if a == b:
            tr[a] += 1
    ratios = []
    for c in set(classes):
        if src[c] > MIN_CLASS_N and dst[c] > MIN_CLASS_N:
            exp = src[c] * (dst[c] / total)
            if exp > 1:
                ratios.append(tr[c] / exp)
    return float(np.mean(ratios)) if ratios else None


def sc_pair(words, fixed_prefix_classes=None):
    """Return (prefix_sc, suffix_sc, prefix_affixes, suffix_affixes)."""
    pfx = detect_affixes(words, "prefix")
    sfx = detect_affixes(words, "suffix")
    if fixed_prefix_classes is not None:
        p_sc = self_clustering(fixed_prefix_classes)
    else:
        p_sc = self_clustering(classify_by_affixes(words, pfx, "prefix"))
    s_sc = self_clustering(classify_by_affixes(words, sfx, "suffix"))
    return p_sc, s_sc, pfx, sfx


def bucket_of(p, s):
    if p is None or s is None:
        return "UNDEFINED"
    ratio = p / s if s else 0
    if p > 1.1 and s > 1.1:
        return "SYMM-HIGH" if 0.80 <= ratio <= 1.25 else (
            "PREFIX-DOM" if ratio > 1.25 else "SUFFIX-DOM")
    if s > 1.1 and p <= 1.1:
        return "SUFFIX-DOM"
    if p > 1.1 and s <= 1.1:
        return "PREFIX-DOM"
    return "SYMM-LOW"


def block_bootstrap(words, n_iter, rng):
    """Block bootstrap CIs for (prefix_sc, suffix_sc, ratio)."""
    if n_iter <= 0 or len(words) < BLOCK_SIZE * 10:
        return None
    n_blocks = len(words) // BLOCK_SIZE
    blocks = [words[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE] for i in range(n_blocks)]
    ps, ss, rs = [], [], []
    for _ in range(n_iter):
        idx = rng.integers(0, n_blocks, n_blocks)
        sample = [w for i in idx for w in blocks[i]]
        p, s, _, _ = sc_pair(sample)
        if p and s:
            ps.append(p); ss.append(s); rs.append(p / s)
    if not ps:
        return None
    q = lambda a: [round(float(np.percentile(a, 2.5)), 3),
                   round(float(np.percentile(a, 97.5)), 3)]
    return {"prefix_ci_95": q(ps), "suffix_ci_95": q(ss), "ratio_ci_95": q(rs)}


# ─── Corpus loaders ──────────────────────────────────────────────────────────
def load_voynich():
    p = os.path.join(DATA_DIR, "voynich",
                     "AncientLanguages_Voynich_snapshot", "train.parquet")
    if not os.path.exists(p):
        return None, None
    df = pd.read_parquet(p)
    zl = df[df["source_name"] == "Zandbergen-Landini"]
    lines = []
    for text in zl["text"]:
        if not isinstance(text, str):
            continue
        toks = [t for t in text.strip().split()
                if not t.startswith("%") and not t.startswith("{")
                and t not in ["-", "=", "!"]]
        if toks:
            lines.append(toks)
    return [t for l in lines for t in l], lines


def load_leipzig(folder, tarball, regex, max_sentences=None):
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
                    if max_sentences:
                        lr = lr[:max_sentences]
                    texts = [l.split("\t", 1)[1].strip() if "\t" in l else l.strip()
                             for l in lr]
                    return [w for w in re.findall(regex, " ".join(texts).lower())
                            if len(w) >= 2]
    except Exception as e:
        print(f"  ! {folder}: {e}")
    return None


def load_gutenberg(folder, fname, regex):
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
    return [w for w in re.findall(regex, text.lower()) if len(w) >= 2]


def load_conllu_words(folder, fname):
    fp = os.path.join(DATA_DIR, "cross_linguistic", folder, fname)
    if not os.path.exists(fp):
        return None
    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read().lower()
    return [w for w in re.split(r"\s+", text) if len(w) >= 2]


LATIN = r"[a-z]+"
LEIPZIG_CORPORA = [
    ("Arabic",         "arabic",            "ara_wikipedia_2021_100K.tar.gz", r"[\u0621-\u064a]+", "Semitic"),
    ("Latin",          "latin",             "lat_wikipedia_2021_100K.tar.gz", LATIN, "IE"),
    ("Estonian",       "estonian",          "ekk_wikipedia_2021_100K.tar.gz", r"[a-zõäöüšž]+", "Uralic"),
    ("Hebrew",         "hebrew",            "heb_wikipedia_2021_100K.tar.gz", r"[\u05d0-\u05ea]+", "Semitic"),
    ("Finnish",        "finnish",           "fin_wikipedia_2021_100K.tar.gz", r"[a-zäöå]+", "Uralic"),
    ("Hungarian",      "hungarian",         "hun_wikipedia_2021_100K.tar.gz", r"[a-záéíóöőúüű]+", "Uralic"),
    ("Turkish",        "turkish",           "tur_wikipedia_2021_100K.tar.gz", r"[a-zçğıöşü]+", "Turkic"),
    ("Italian",        "italian",           "ita_wikipedia_2021_100K.tar.gz", r"[a-zàèéìòù]+", "IE"),
    ("N. Azerbaijani", "north_azerbaijani", "aze_wikipedia_2021_100K.tar.gz", r"[a-zçəğıöşü]+", "Turkic"),
    ("Swahili",        "swahili",           "swa_wikipedia_2021_100K.tar.gz", LATIN, "Bantu"),
    ("Georgian",       "georgian",          "kat_wikipedia_2021_100K.tar.gz", r"[\u10d0-\u10f0]+", "Kartvelian"),
    ("Tagalog",        "tagalog",           "tgl_wikipedia_2021_100K.tar.gz", LATIN, "Austronesian"),
    # Mandarin excluded from default run: requires jieba/pypinyin segmentation.
    # Raw Latin-regex extraction over Chinese script yields only embedded romanized
    # fragments and is NOT comparable. Re-add only with proper segmentation.
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sentences", type=int, default=None,
                    help="cap Leipzig sentences per corpus (legacy table used 20000)")
    ap.add_argument("--bootstrap", type=int, default=BOOTSTRAP_N,
                    help="bootstrap iterations; 0 to disable")
    ap.add_argument("--out", default=os.path.join(RESULTS_DIR,
                    "prefix_suffix_analysis_generated.json"))
    args = ap.parse_args()

    rng = np.random.default_rng(SEED)
    random.seed(SEED)
    systems = {}

    print("=" * 78)
    print("PREFIX / SUFFIX SELF-CLUSTERING — symmetric method, all systems")
    print("=" * 78)

    # ── Voynich ──
    vtokens, _ = load_voynich()
    if vtokens is None:
        print("ERROR: Voynich parquet not found. Run scripts/00_fetch_datasets.py")
        sys.exit(1)

    p_sym, s_sym, pfx, sfx = sc_pair(vtokens)
    legacy_classes = [classify_eva_fixed(t) for t in vtokens]
    p_legacy = self_clustering(legacy_classes)

    entry = {
        "prefix_sc": round(p_sym, 3),
        "suffix_sc": round(s_sym, 3),
        "ratio": round(p_sym / s_sym, 3),
        "bucket": bucket_of(p_sym, s_sym),
        "family": "Target system",
        "n": len(vtokens),
        "detected_prefix_families": pfx,
        "detected_suffix_families": sfx,
        "legacy_asymmetric_prefix_sc": round(p_legacy, 3) if p_legacy else None,
        "legacy_asymmetric_ratio": (round(p_legacy / s_sym, 3)
                                    if p_legacy and s_sym else None),
        "legacy_asymmetric_bucket": bucket_of(p_legacy, s_sym),
    }
    ci = block_bootstrap(vtokens, args.bootstrap, rng)
    if ci:
        entry.update(ci)
    systems["VOYNICH"] = entry
    print(f"\nVOYNICH  symmetric: prefix={p_sym:.3f} suffix={s_sym:.3f} "
          f"ratio={p_sym/s_sym:.3f}  [{entry['bucket']}]")
    print(f"         legacy (hand-picked EVA prefix): prefix={p_legacy:.3f} "
          f"ratio={p_legacy/s_sym:.3f}  [{entry['legacy_asymmetric_bucket']}]")
    print(f"         detected prefixes: {pfx}")
    print(f"         detected suffixes: {sfx}")

    # ── Shuffled-token control ──
    shuf = vtokens.copy()
    rng.shuffle(shuf)
    p, s, _, _ = sc_pair(shuf)
    systems["Gibberish (shuffled)"] = {
        "prefix_sc": round(p, 3), "suffix_sc": round(s, 3),
        "ratio": round(p / s, 3), "bucket": bucket_of(p, s),
        "family": "Control", "n": len(shuf),
    }
    print(f"\nControl (shuffled): prefix={p:.3f} suffix={s:.3f} "
          f"ratio={p/s:.3f} [{bucket_of(p,s)}]")

    # ── Comparators ──
    print("\nComparators:")
    todo = [(lbl, load_leipzig, (folder, tar, rx, args.sentences), fam)
            for lbl, folder, tar, rx, fam in LEIPZIG_CORPORA]
    todo += [
        ("Middle English", load_gutenberg, ("middle_english", "chaucer_canterbury_tales_22120.txt", LATIN), "IE"),
        ("KJV English",    load_gutenberg, ("kjv_english", "king_james_bible_10900.txt", LATIN), "IE"),
        ("Ottoman Turkish", load_conllu_words, ("ottoman_turkish", "ota_dudu_words.txt"), "Turkic"),
    ]

    for label, loader, largs, fam in todo:
        words = loader(*largs)
        if not words or len(words) < 1000:
            print(f"  {label:<22} NOT FOUND / too small")
            continue
        if len(words) > MAX_TOKENS:
            words = words[:MAX_TOKENS]
        p, s, pf, sf = sc_pair(words)
        if p is None or s is None:
            print(f"  {label:<22} insufficient class support")
            continue
        rec = {
            "prefix_sc": round(p, 3), "suffix_sc": round(s, 3),
            "ratio": round(p / s, 3), "bucket": bucket_of(p, s),
            "family": fam, "n": len(words),
            "detected_prefix_families": pf, "detected_suffix_families": sf,
        }
        # Comparator CIs use a capped subsample: full-corpus bootstrap over
        # 200K+ tokens x N iterations is not tractable, and comparator point
        # estimates sit far from the SYMM-HIGH boundary, so interval precision
        # is not load-bearing for them. Voynich (the target system, and the one
        # near the boundary) is bootstrapped on its full corpus above.
        ci = block_bootstrap(words[:BOOTSTRAP_SUBSAMPLE],
                             min(args.bootstrap, 100), rng)
        if ci:
            rec.update(ci)
            rec["ci_subsample_n"] = min(len(words), BOOTSTRAP_SUBSAMPLE)
        systems[label] = rec
        print(f"  {label:<22} n={len(words):>7}  prefix={p:.3f}  suffix={s:.3f}  "
              f"ratio={p/s:.3f}  [{rec['bucket']}]")

    # ── Summary table ──
    print("\n" + "=" * 78)
    print(f"{'System':<24}{'Prefix':>8}{'Suffix':>8}{'Ratio':>8}  Bucket")
    print("-" * 78)
    for k in sorted(systems, key=lambda k: -systems[k]["prefix_sc"]):
        r = systems[k]
        print(f"{k:<24}{r['prefix_sc']:>8.2f}{r['suffix_sc']:>8.2f}"
              f"{r['ratio']:>8.2f}  {r['bucket']}")

    n_symm_high = sum(1 for k, r in systems.items()
                      if k != "VOYNICH" and r["bucket"] == "SYMM-HIGH")
    print("-" * 78)
    print(f"Non-Voynich systems in SYMM-HIGH: {n_symm_high}")

    output = {
        "description": "Prefix vs suffix self-clustering, symmetric method, "
                       "generated from raw data by scripts/10_prefix_suffix_analysis.py",
        "method": (f"Auto-detected top-{N_FAMILIES} affix families "
                   f"({AFFIX_MIN_LEN}-{AFFIX_MAX_LEN} char, "
                   f"{MIN_COV:.0%}-{MAX_COV:.0%} coverage), applied IDENTICALLY "
                   "to every system including Voynich. Suffix families detected "
                   "by the mirror-image procedure. No hand-picked families are "
                   "used for any system in the headline numbers."),
        "asymmetry_note": (
            "The previously committed artifact scored Voynich with hand-picked "
            "EVA prefix families while scoring every comparator with "
            "auto-detected families. That variant is retained for Voynich only, "
            "under 'legacy_asymmetric_*' keys, so the effect of the asymmetry "
            "is measurable rather than assumed."),
        "self_clustering_definition":
            "mean over classes of observed(c->c) / [src(c) * dst(c)/total], "
            f"classes with src>{MIN_CLASS_N} and dst>{MIN_CLASS_N}",
        "bootstrap": (f"{args.bootstrap} iterations, contiguous block bootstrap, "
                      f"block size {BLOCK_SIZE}" if args.bootstrap else "disabled"),
        "seed": SEED,
        "leipzig_sentence_cap": args.sentences,
        "max_tokens_per_corpus": MAX_TOKENS,
        "bucket_definitions": BUCKET_DEFINITIONS,
        "systems": systems,
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
