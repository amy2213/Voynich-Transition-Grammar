#!/usr/bin/env python3
"""
08_per_scribe_analysis.py — Per-scribe decomposition of headline findings.

CONTEXT
-------
Currier (1976) and Davis (2020) identify multiple scribal hands in the Voynich
Manuscript. All analyses in the project's core pipeline pool tokens across
hands. The independent audit flagged this as a vulnerability: the manuscript-
wide signature (bidirectional symmetry, CHEDY->QOK, suffix agreement) might
be produced by aggregation across hand-specific idiolects that individually
have very different profiles.

WHAT THIS SCRIPT DOES
---------------------
For each of the 5 scribal hands in the ZL metadata (column 'H', values 1-5),
compute the key headline statistics separately:
  1. Prefix/suffix self-clustering (Finding 1.3, bidirectional symmetry)
  2. CHEDY->QOK transition rule (Finding 1.1)
  3. AIIN density (Finding 1.2)

Declared interpretation BEFORE seeing results:
  - If all 5 hands (or at least hands 1, 2, 3 with >1000 lines) individually
    show SYMM-HIGH and elevated CHEDY->QOK, the manuscript-wide finding is
    robustly supported as a manuscript property rather than an aggregation
    artifact.
  - If the signature is concentrated in 1-2 hands (e.g. only Hand 2 shows
    SYMM-HIGH, others show SYMM-LOW), the "manuscript property" claim must
    be reframed as "a property of specific hand(s)."
  - If hands individually show different profiles that only combine to
    SYMM-HIGH in aggregate, the original finding is essentially an
    aggregation artifact.

Usage:
  python scripts/08_per_scribe_analysis.py

Output:
  results/per_scribe_results.json
"""

import os
import sys
import json
import re
from collections import Counter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_tokens(text):
    out = []
    for line in str(text).split("\n"):
        line = line.strip()
        if not line:
            continue
        toks = []
        for tok in line.split():
            tok = re.sub(r"[^a-z]", "", tok.lower())
            if tok:
                toks.append(tok)
        if toks:
            out.append(toks)
    return out


def classify(tok):
    if tok.startswith("qok"):
        return "QOK"
    if tok.startswith("ok"):
        return "OK"
    if tok.startswith("ot"):
        return "OT"
    if any(s in tok for s in ("chedy", "shedy", "chey", "shey")):
        return "CHEDY"
    if "aiin" in tok or "ain" in tok:
        return "AIIN"
    return "OTHER"


def transition_ratio(tokens_flat, src_fam, dst_fam):
    """Observed/expected ratio for adjacent family pair."""
    fams = [classify(t) for t in tokens_flat]
    n_src = fams.count(src_fam)
    n_dst = fams.count(dst_fam)
    n_total = len(fams)
    obs = sum(1 for i in range(len(fams) - 1) if fams[i] == src_fam and fams[i + 1] == dst_fam)
    if n_src == 0 or n_dst == 0 or n_total == 0:
        return None, obs, 0
    exp = n_src * (n_dst / n_total)
    return (obs / exp) if exp > 0 else None, obs, exp


def auto_affix_families(tokens, end="prefix", k=5, min_cov=0.02, max_cov=0.20,
                        affix_len_range=(2, 3)):
    """Auto-detect top-k affix families by coverage within range."""
    counts_by_len = {}
    total = len(tokens)
    for L in range(affix_len_range[0], affix_len_range[1] + 1):
        c = Counter()
        for t in tokens:
            if len(t) < L:
                continue
            af = t[:L] if end == "prefix" else t[-L:]
            c[af] += 1
        counts_by_len[L] = c
    candidates = []
    for L, cnt in counts_by_len.items():
        for af, n in cnt.items():
            cov = n / total
            if min_cov <= cov <= max_cov:
                candidates.append((af, L, n, cov))
    candidates.sort(key=lambda x: -x[2])
    return [c[0] for c in candidates[:k]]


def self_cluster_score(tokens, affixes, end="prefix"):
    """Mean same-family adjacency ratio over the specified affix families."""
    def match(t, af):
        if end == "prefix":
            return t.startswith(af)
        return t.endswith(af)

    n = len(tokens)
    fam = []
    for t in tokens:
        hit = None
        for af in affixes:
            if match(t, af):
                hit = af
                break
        fam.append(hit)
    total_affix_tokens = sum(1 for x in fam if x is not None)
    if total_affix_tokens == 0:
        return None
    scores = []
    for af in affixes:
        nf = sum(1 for x in fam if x == af)
        if nf < 2:
            continue
        obs = sum(1 for i in range(n - 1) if fam[i] == af and fam[i + 1] == af)
        exp = nf * (nf / n)
        if exp > 0:
            scores.append(obs / exp)
    return sum(scores) / len(scores) if scores else None


def classify_bucket(prefix_sc, suffix_sc):
    if prefix_sc is None or suffix_sc is None:
        return "UNDEFINED"
    ratio = prefix_sc / suffix_sc if suffix_sc > 0 else float("inf")
    if prefix_sc > 1.1 and suffix_sc > 1.1 and 0.80 <= ratio <= 1.25:
        return "SYMM-HIGH"
    if suffix_sc > 1.1 and ratio < 0.80:
        return "SUFFIX-DOM"
    if prefix_sc > 1.1 and ratio > 1.25:
        return "PREFIX-DOM"
    return "SYMM-LOW"


def main():
    import pandas as pd
    path = os.path.join(PROJECT_ROOT, "data", "raw", "voynich",
                        "AncientLanguages_Voynich_snapshot", "train.parquet")
    df = pd.read_parquet(path)
    zl = df[df["source_name"] == "Zandbergen-Landini"].copy()

    results = {
        "description": (
            "Per-scribe decomposition of headline findings. Tests whether the "
            "manuscript-wide signature is present in each individual hand or is "
            "an aggregation artifact."
        ),
        "methodology": {
            "hand_labels": "Column 'H' in the Zandbergen-Landini parquet metadata. Values 1-5 correspond to Currier's scribal hand attribution; missing values indicate unassigned lines.",
            "per_hand_analyses": [
                "Prefix and suffix self-clustering (bucket classification)",
                "CHEDY->QOK transition ratio",
                "AIIN density",
            ],
        },
        "hands": {}
    }

    # Assign hand at line level; collect tokens per hand
    hand_col = "H"
    tokens_by_hand = {str(i): [] for i in range(1, 6)}
    tokens_by_hand["unassigned"] = []

    for _, row in zl.iterrows():
        text = row.get("text")
        if text is None or pd.isna(text):
            continue
        h = row.get(hand_col)
        if h is None or pd.isna(h) or str(h).strip() == "":
            key = "unassigned"
        else:
            key = str(h).strip()
        for line_toks in parse_tokens(text):
            tokens_by_hand.setdefault(key, []).extend(line_toks)

    total_tokens = sum(len(v) for v in tokens_by_hand.values())
    results["total_tokens"] = total_tokens

    # Voynich EVA prefix families for SC (same as main pipeline)
    EVA_PREFIX_FAMILIES = ["qok", "ok", "ot", "ched", "aiin"]

    for hand, toks in tokens_by_hand.items():
        if len(toks) < 500:
            results["hands"][hand] = {
                "n_tokens": len(toks),
                "status": "skipped (insufficient tokens)",
            }
            continue

        # Bidirectional SC
        suffix_affixes = auto_affix_families(toks, end="suffix", k=5)
        psc = self_cluster_score(toks, EVA_PREFIX_FAMILIES, end="prefix")
        ssc = self_cluster_score(toks, suffix_affixes, end="suffix")
        bucket = classify_bucket(psc, ssc)

        # CHEDY->QOK
        cq_ratio, cq_obs, cq_exp = transition_ratio(toks, "CHEDY", "QOK")

        # AIIN density
        aiin_pct = sum(1 for t in toks if classify(t) == "AIIN") / len(toks) * 100

        results["hands"][hand] = {
            "n_tokens": len(toks),
            "prefix_sc": round(psc, 3) if psc is not None else None,
            "suffix_sc": round(ssc, 3) if ssc is not None else None,
            "ps_ratio": round(psc / ssc, 3) if psc and ssc else None,
            "bucket": bucket,
            "chedy_qok_ratio": round(cq_ratio, 2) if cq_ratio is not None else None,
            "chedy_qok_obs": cq_obs,
            "chedy_qok_exp": round(cq_exp, 1) if cq_exp else None,
            "aiin_pct": round(aiin_pct, 1),
            "auto_suffix_families": suffix_affixes,
        }

    # Verdict
    qualifying_hands = [h for h, d in results["hands"].items()
                        if isinstance(d, dict) and d.get("n_tokens", 0) >= 3000]
    symm_high_hands = [h for h in qualifying_hands
                       if results["hands"][h].get("bucket") == "SYMM-HIGH"]
    chedy_elevated_hands = [h for h in qualifying_hands
                            if (results["hands"][h].get("chedy_qok_ratio") or 0) > 1.5]

    results["verdict"] = {
        "n_hands_with_>=3000_tokens": len(qualifying_hands),
        "qualifying_hands": qualifying_hands,
        "n_qualifying_hands_symm_high": len(symm_high_hands),
        "n_qualifying_hands_with_chedy_qok_above_1.5": len(chedy_elevated_hands),
        "interpretation": (
            "SUPPORTS manuscript-wide finding: all qualifying hands SYMM-HIGH and CHEDY->QOK elevated"
            if len(symm_high_hands) == len(qualifying_hands) and len(chedy_elevated_hands) == len(qualifying_hands)
            else "PARTIAL SUPPORT: majority of hands but not all show the signature"
            if len(symm_high_hands) >= len(qualifying_hands) / 2 and len(chedy_elevated_hands) >= len(qualifying_hands) / 2
            else "AGGREGATION ARTIFACT: signature carried by minority of hands"
        ),
    }

    print(f"\nTotal tokens: {total_tokens}")
    print(f"\nPer-hand summary (hands with >= 500 tokens):")
    for hand, d in results["hands"].items():
        if not isinstance(d, dict) or "status" in d:
            continue
        print(f"  Hand {hand}: n={d['n_tokens']}")
        print(f"    P={d['prefix_sc']}, S={d['suffix_sc']}, ratio={d['ps_ratio']}, bucket={d['bucket']}")
        print(f"    CHEDY->QOK={d['chedy_qok_ratio']}x (obs={d['chedy_qok_obs']}, exp={d['chedy_qok_exp']})")
        print(f"    AIIN={d['aiin_pct']}%")

    print(f"\nVerdict: {results['verdict']['interpretation']}")

    out_path = os.path.join(PROJECT_ROOT, "results", "per_scribe_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
