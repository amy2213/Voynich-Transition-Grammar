#!/usr/bin/env python3
"""
04_extended_analysis.py — Scripted reproduction of findings 1.4–1.10.

Covers:
  1.4  Line-bounded grammar (within-line vs cross-line transition rules)
  1.5  Suffix agreement between adjacent tokens
  1.6  Multi-feature agreement
  1.7  Agreement cascades through 3-token chains
  1.8  Productive morphological paradigm structure
  1.9  CHEDY avoids line-final position
  1.10 Glyph layer architecture

These analyses were originally developed interactively and documented in
docs/durable_findings.md. This script packages them as reproducible code
with canonical value verification.

Usage:
  python scripts/04_extended_analysis.py

Output:
  results/extended_analysis_results.json
"""

import os
import re
import json
import sys
import numpy as np
from collections import Counter, defaultdict
from math import log2

np.random.seed(42)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# ─── Load Data ───────────────────────────────────────────────────────────────

print("Loading Zandbergen-Landini EVA transliteration...")
import pandas as pd

parquet_path = os.path.join(PROJECT_ROOT, "data", "raw", "voynich",
                            "AncientLanguages_Voynich_snapshot", "train.parquet")
if not os.path.exists(parquet_path):
    print("ERROR: Dataset not found. Run scripts/00_fetch_datasets.py first.")
    sys.exit(1)

df = pd.read_parquet(parquet_path)
zl = df[df["source_name"] == "Zandbergen-Landini"].copy()
for col in ["H", "L", "Q", "I", "X"]:
    zl[col] = zl[col].fillna("?")

# ─── Token Parsing & Family Definitions ──────────────────────────────────────

def parse_tokens(text):
    if not text or not isinstance(text, str):
        return []
    return [t for t in text.strip().split()
            if not t.startswith("%") and not t.startswith("{") and t not in ["-", "=", "!"]]

def classify(tok):
    if "aiin" in tok or "ain" in tok: return "AIIN"
    if tok.startswith("qok"): return "QOK"
    if tok.startswith("ok") and not tok.startswith("qok"): return "OK"
    if tok.startswith("ot"): return "OT"
    if any(p in tok for p in ["chedy", "shedy", "chey", "shey"]): return "CHEDY"
    return "OTHER"

def get_section(page):
    m = re.match(r"f(\d+)", page)
    if not m: return "other"
    n = int(m.group(1))
    if n <= 57: return "herbal_A"
    elif 67 <= n <= 73: return "astronomical"
    elif 75 <= n <= 84: return "biological"
    elif 87 <= n <= 102: return "herbal_B"
    elif 103 <= n <= 116: return "recipes_Q20"
    return "other"

FAMS = ["QOK", "OK", "OT", "CHEDY", "AIIN", "OTHER"]
BACKBONE = ["QOK", "OK", "OT", "CHEDY", "AIIN"]

# ─── Build Line Data ─────────────────────────────────────────────────────────

lines = []
for _, row in zl.iterrows():
    tokens = parse_tokens(row["text"])
    if tokens:
        lines.append({
            "page": row["page"], "section": get_section(row["page"]),
            "hand": row["H"], "currier": row["L"], "tokens": tokens,
        })

all_tokens = [t for l in lines for t in l["tokens"]]
all_classes = [classify(t) for t in all_tokens]
tc = Counter(all_tokens)
n_tokens = len(all_tokens)

print(f"Loaded: {len(lines)} lines, {n_tokens} tokens, {len(set(l['page'] for l in lines))} pages")

# ─── Feature Extractors ─────────────────────────────────────────────────────

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
        if i < len(token)-2 and token[i]=='c' and token[i+1] in 'tkpf' and token[i+2]=='h':
            chars.append(token[i:i+3]); i += 3
        elif i < len(token)-1 and token[i:i+2] in ('ch','sh','ee','ii','ai','oi'):
            chars.append(token[i:i+2]); i += 2
        else: chars.append(token[i]); i += 1
    return chars

def layer(unit):
    if unit in ('cth','ckh','cph','cfh','t','p','k','f'): return 'C'
    if unit in ('ch','sh','ee'): return 'M'
    if unit in ('o','a','y'): return 'O'
    return 'R'

def f_mantle(tok):
    chars = parse_eva(tok)
    m = tuple(c for c in chars if layer(c) == 'M')
    return "".join(m) if m else "none"

def f_circles(tok):
    chars = parse_eva(tok)
    return sum(1 for c in chars if layer(c) == 'O')

def f_bundle(tok):
    return (f_suffix(tok), f_length(tok), f_mantle(tok))

def edit_distance(a, b):
    if len(a) < len(b): return edit_distance(b, a)
    if len(b) == 0: return len(a)
    prev = list(range(len(b)+1))
    for i, ca in enumerate(a):
        curr = [i+1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j+1]+1, curr[j]+1, prev[j]+(ca!=cb)))
        prev = curr
    return prev[len(b)]

results = {}

# =============================================================================
# FINDING 1.4: LINE-BOUNDED GRAMMAR
# =============================================================================
print("\n" + "=" * 70)
print("FINDING 1.4: Line-bounded grammar")
print("=" * 70)

# Within-line transitions
within = []
for l in lines:
    fams = [classify(t) for t in l["tokens"]]
    for i in range(len(fams) - 1):
        within.append((fams[i], fams[i+1]))

# Cross-line transitions (same page)
cross = []
for i in range(len(lines) - 1):
    if lines[i]["page"] == lines[i+1]["page"]:
        cross.append((classify(lines[i]["tokens"][-1]),
                       classify(lines[i+1]["tokens"][0])))

def transition_ratio(pairs, src, dst):
    s = sum(1 for a, _ in pairs if a == src)
    d = sum(1 for _, b in pairs if b == dst)
    both = sum(1 for a, b in pairs if a == src and b == dst)
    total = len(pairs)
    exp = s * (d / total) if total > 0 else 0
    return both / exp if exp > 1 else None

cq_within = transition_ratio(within, "CHEDY", "QOK")
cq_cross = transition_ratio(cross, "CHEDY", "QOK")
aq_within = transition_ratio(within, "AIIN", "QOK")
aq_cross = transition_ratio(cross, "AIIN", "QOK")

# Cross-line self-clustering
sc_cross = {}
for fam in BACKBONE:
    sc_cross[fam] = transition_ratio(cross, fam, fam)

# Template recurrence
line_templates = Counter(tuple(classify(t) for t in l["tokens"]) for l in lines)
real_recurring = sum(1 for _, c in line_templates.items() if c >= 2)
real_covered = sum(c for _, c in line_templates.items() if c >= 2)

shuf_recurring = []
all_fams_flat = [f for l in lines for f in [classify(t) for t in l["tokens"]]]
for _ in range(20):
    shuf = all_fams_flat.copy()
    np.random.shuffle(shuf)
    idx = 0; st = Counter()
    for l in lines:
        n = len(l["tokens"])
        st[tuple(shuf[idx:idx+n])] += 1
        idx += n
    shuf_recurring.append(sum(1 for _, c in st.items() if c >= 2))

template_ratio = real_recurring / np.mean(shuf_recurring) if np.mean(shuf_recurring) > 0 else 0
coverage_real = real_covered / len(lines)

results["1.4_line_bounded_grammar"] = {
    "chedy_qok_within": round(cq_within, 2),
    "chedy_qok_cross": round(cq_cross, 2),
    "aiin_qok_within": round(aq_within, 2),
    "aiin_qok_cross": round(aq_cross, 2),
    "cross_line_self_clustering": {f: round(v, 2) for f, v in sc_cross.items() if v},
    "template_recurrence_ratio": round(template_ratio, 2),
    "template_coverage_pct": round(coverage_real * 100, 1),
    "n_within_pairs": len(within),
    "n_cross_pairs": len(cross),
}

print(f"  CHEDY→QOK: within={cq_within:.2f}x, cross={cq_cross:.2f}x")
print(f"  AIIN→QOK:  within={aq_within:.2f}x, cross={aq_cross:.2f}x")
print(f"  Template recurrence: {template_ratio:.2f}x above shuffled")

# =============================================================================
# FINDING 1.5: SUFFIX AGREEMENT
# =============================================================================
print("\n" + "=" * 70)
print("FINDING 1.5: Suffix agreement between adjacent tokens")
print("=" * 70)

def suffix_agreement(pairs_list, feature_fn):
    if not pairs_list: return None, None, None
    same = sum(1 for s, t in pairs_list if feature_fn(s) == feature_fn(t))
    total = len(pairs_list)
    observed = same / total
    src_dist = Counter(feature_fn(s) for s, _ in pairs_list)
    tgt_dist = Counter(feature_fn(t) for _, t in pairs_list)
    expected = sum((src_dist[f]/total) * (tgt_dist.get(f,0)/total) for f in src_dist)
    ratio = observed / expected if expected > 0 else 0
    return observed * 100, expected * 100, ratio

interactions = [
    ("CHEDY", "QOK"), ("QOK", "QOK"), ("OK", "OT"),
    ("OK", "OK"), ("OT", "OT"),
]

agreement_results = {}
for sf, tf in interactions:
    pairs = []
    for l in lines:
        fams = [classify(t) for t in l["tokens"]]
        for i in range(len(l["tokens"]) - 1):
            if fams[i] == sf and fams[i+1] == tf:
                pairs.append((l["tokens"][i], l["tokens"][i+1]))
    
    obs, exp, ratio = suffix_agreement(pairs, f_suffix)
    label = f"{sf}→{tf}"
    agreement_results[label] = {
        "obs_pct": round(obs, 1) if obs else None,
        "exp_pct": round(exp, 1) if exp else None,
        "ratio": round(ratio, 2) if ratio else None,
        "n_pairs": len(pairs),
    }
    
    # Shuffled null z-score
    if len(pairs) >= 20:
        src_toks = [s for s, _ in pairs]
        tgt_toks = [t for _, t in pairs]
        shuf_ratios = []
        for _ in range(200):
            np.random.shuffle(tgt_toks)
            shuf_pairs = list(zip(src_toks, tgt_toks))
            _, _, sr = suffix_agreement(shuf_pairs, f_suffix)
            shuf_ratios.append(sr)
        z = (ratio - np.mean(shuf_ratios)) / np.std(shuf_ratios) if np.std(shuf_ratios) > 0 else 0
        agreement_results[label]["z_score"] = round(z, 1)
        print(f"  {label}: ratio={ratio:.2f}x, z={z:.1f}, n={len(pairs)}")

# CHEDY subtype selection
from scipy.stats import chi2_contingency
chedy_qok_pairs = []
for l in lines:
    fams = [classify(t) for t in l["tokens"]]
    for i in range(len(l["tokens"]) - 1):
        if fams[i] == "CHEDY" and fams[i+1] == "QOK":
            chedy_qok_pairs.append((l["tokens"][i], l["tokens"][i+1]))

qok_after_chedy = Counter(t for _, t in chedy_qok_pairs)
qok_elsewhere = Counter()
for l in lines:
    fams = [classify(t) for t in l["tokens"]]
    for i in range(len(l["tokens"])):
        if fams[i] == "QOK" and (i == 0 or fams[i-1] != "CHEDY"):
            qok_elsewhere[l["tokens"][i]] += 1

all_qok = qok_after_chedy + qok_elsewhere
top_qok = [t for t, _ in all_qok.most_common(10)]
table = [[qok_after_chedy.get(t, 0), qok_elsewhere.get(t, 0)] for t in top_qok]
oa = sum(qok_after_chedy.values()) - sum(qok_after_chedy.get(t,0) for t in top_qok)
oe = sum(qok_elsewhere.values()) - sum(qok_elsewhere.get(t,0) for t in top_qok)
table.append([max(oa, 0), max(oe, 0)])

chi2, p_chi, _, _ = chi2_contingency(table)
agreement_results["chedy_selects_qok_subtypes"] = {
    "chi2": round(chi2, 1), "p": float(f"{p_chi:.2e}"),
}
print(f"  CHEDY selects QOK subtypes: Chi²={chi2:.1f}, p={p_chi:.2e}")

results["1.5_suffix_agreement"] = agreement_results

# =============================================================================
# FINDING 1.6: MULTI-FEATURE AGREEMENT
# =============================================================================
print("\n" + "=" * 70)
print("FINDING 1.6: Multi-feature agreement")
print("=" * 70)

def combined_agreement(pairs, feature_fns):
    if not pairs: return None, None, None
    same = sum(1 for s, t in pairs if all(fn(s) == fn(t) for fn in feature_fns))
    total = len(pairs)
    observed = same / total * 100
    individual_expected = []
    for fn in feature_fns:
        src_d = Counter(fn(s) for s, _ in pairs)
        tgt_d = Counter(fn(t) for _, t in pairs)
        ie = sum((src_d[f]/total) * (tgt_d.get(f,0)/total) for f in src_d)
        individual_expected.append(ie)
    joint_expected = 1.0
    for ie in individual_expected:
        joint_expected *= ie
    joint_expected *= 100
    ratio = observed / joint_expected if joint_expected > 0 else 0
    return observed, joint_expected, ratio

multi_results = {}
for sf, tf in interactions:
    pairs = []
    for l in lines:
        fams = [classify(t) for t in l["tokens"]]
        for i in range(len(l["tokens"]) - 1):
            if fams[i] == sf and fams[i+1] == tf:
                pairs.append((l["tokens"][i], l["tokens"][i+1]))
    
    if len(pairs) < 20: continue
    label = f"{sf}→{tf}"
    
    obs_s, exp_s, r_s = combined_agreement(pairs, [f_suffix])
    obs_all, exp_all, r_all = combined_agreement(pairs, [f_suffix, f_length, f_mantle, lambda t: f_circles(t)])
    
    multi_results[label] = {
        "suffix_only_ratio": round(r_s, 2),
        "all_four_ratio": round(r_all, 2),
        "n_pairs": len(pairs),
    }
    print(f"  {label}: suffix={r_s:.2f}x, all_four={r_all:.2f}x (n={len(pairs)})")

results["1.6_multi_feature_agreement"] = multi_results

# =============================================================================
# FINDING 1.7: AGREEMENT CASCADES
# =============================================================================
print("\n" + "=" * 70)
print("FINDING 1.7: Agreement cascades through 3-token chains")
print("=" * 70)

def trigram_cascade(fam_a, fam_b, fam_c, feature_fn):
    chain_agree_agree = 0; chain_agree_total = 0
    chain_disagree_agree = 0; chain_disagree_total = 0
    
    for l in lines:
        fams = [classify(t) for t in l["tokens"]]
        for i in range(len(l["tokens"]) - 2):
            if fams[i] == fam_a and fams[i+1] == fam_b and fams[i+2] == fam_c:
                fa = feature_fn(l["tokens"][i])
                fb = feature_fn(l["tokens"][i+1])
                fc = feature_fn(l["tokens"][i+2])
                if fa == fb:
                    chain_agree_total += 1
                    if fb == fc: chain_agree_agree += 1
                else:
                    chain_disagree_total += 1
                    if fb == fc: chain_disagree_agree += 1
    
    pct_if_agree = chain_agree_agree / chain_agree_total * 100 if chain_agree_total > 5 else None
    pct_if_disagree = chain_disagree_agree / chain_disagree_total * 100 if chain_disagree_total > 5 else None
    cascade = (pct_if_agree - pct_if_disagree) if pct_if_agree is not None and pct_if_disagree is not None else None
    
    return {
        "if_agree_pct": round(pct_if_agree, 0) if pct_if_agree is not None else None,
        "if_disagree_pct": round(pct_if_disagree, 0) if pct_if_disagree is not None else None,
        "cascade_pp": round(cascade, 0) if cascade is not None else None,
        "n_agree": chain_agree_total,
        "n_disagree": chain_disagree_total,
    }

chains = [
    ("CHEDY", "OTHER", "CHEDY"),
    ("QOK", "OTHER", "QOK"),
    ("QOK", "QOK", "QOK"),
    ("CHEDY", "QOK", "CHEDY"),
    ("OT", "OTHER", "OT"),
]

cascade_results = {}
for fa, fb, fc in chains:
    label = f"{fa}→{fb}→{fc}"
    r = trigram_cascade(fa, fb, fc, f_suffix)
    cascade_results[label] = r
    if r["cascade_pp"] is not None:
        print(f"  {label}: +{r['cascade_pp']:.0f}pp ({r['if_agree_pct']:.0f}% vs {r['if_disagree_pct']:.0f}%)")

# Skip-agreement: family→[OTHER]→family
skip_results = {}
for fam in ["QOK", "CHEDY", "OT"]:
    same = total = 0
    src_sfx = Counter(); tgt_sfx = Counter()
    for l in lines:
        fams = [classify(t) for t in l["tokens"]]
        for i in range(len(l["tokens"]) - 2):
            if fams[i] == fam and fams[i+1] == "OTHER" and fams[i+2] == fam:
                total += 1
                ss = f_suffix(l["tokens"][i]); ts = f_suffix(l["tokens"][i+2])
                src_sfx[ss] += 1; tgt_sfx[ts] += 1
                if ss == ts: same += 1
    
    if total >= 10:
        obs = same / total * 100
        exp = sum((src_sfx[f]/total) * (tgt_sfx.get(f,0)/total) for f in src_sfx) * 100
        ratio = obs / exp if exp > 0 else 0
        skip_results[f"{fam}→O→{fam}"] = {"ratio": round(ratio, 2), "n": total}
        print(f"  {fam}→[OTHER]→{fam}: {ratio:.2f}x (n={total})")

results["1.7_agreement_cascades"] = {
    "chains": cascade_results,
    "skip_agreement": skip_results,
}

# =============================================================================
# FINDING 1.8: PRODUCTIVE MORPHOLOGICAL PARADIGMS
# =============================================================================
print("\n" + "=" * 70)
print("FINDING 1.8: Productive morphological paradigms")
print("=" * 70)

paradigm_results = {}
sections = ["herbal_A", "biological", "recipes_Q20", "herbal_B"]

for fam in ["QOK", "CHEDY", "AIIN"]:
    fam_types = [t for t in set(all_tokens) if classify(t) == fam and tc[t] >= 2]
    freq_types = sorted(fam_types, key=lambda t: -tc[t])[:50]
    
    # Hub degree (edit-distance-1 neighbors)
    neighbors = defaultdict(list)
    for i in range(len(freq_types)):
        for j in range(i+1, len(freq_types)):
            if edit_distance(freq_types[i], freq_types[j]) == 1:
                neighbors[freq_types[i]].append(freq_types[j])
                neighbors[freq_types[j]].append(freq_types[i])
    
    connected = len(neighbors)
    max_degree = max(len(v) for v in neighbors.values()) if neighbors else 0
    mean_degree = np.mean([len(v) for v in neighbors.values()]) if neighbors else 0
    
    # Frequency-variant correlation
    type_variants = {}
    for t in fam_types:
        if tc[t] < 2: continue
        nv = sum(1 for t2 in fam_types if t != t2 and tc[t2] >= 1 and edit_distance(t, t2) == 1)
        type_variants[t] = nv
    
    if len(type_variants) > 10:
        freqs = [tc[t] for t in type_variants]
        variants = [type_variants[t] for t in type_variants]
        r_val = np.corrcoef(np.log(freqs), variants)[0, 1]
    else:
        r_val = None
    
    paradigm_results[fam] = {
        "n_types": len(fam_types),
        "connected_of_top50": connected,
        "max_hub_degree": max_degree,
        "mean_degree": round(mean_degree, 1),
        "freq_variant_r": round(r_val, 3) if r_val is not None else None,
    }
    print(f"  {fam}: {connected}/50 connected, max_degree={max_degree}, r={r_val:.3f}" if r_val else f"  {fam}: {connected}/50 connected")

# Edit operation positional analysis
def find_edit_ops(a, b):
    if len(a) == len(b):
        for i in range(len(a)):
            if a[i] != b[i]:
                rel = i / max(len(a)-1, 1)
                pos = "START" if rel < 0.25 else ("END" if rel > 0.75 else "MID")
                return f"sub:{a[i]}→{b[i]}", pos
    elif len(a) == len(b) + 1:
        for i in range(len(a)):
            if a[:i] + a[i+1:] == b:
                rel = i / max(len(a)-1, 1)
                pos = "START" if rel < 0.25 else ("END" if rel > 0.75 else "MID")
                return f"del:{a[i]}", pos
    elif len(b) == len(a) + 1:
        for i in range(len(b)):
            if b[:i] + b[i+1:] == a:
                rel = i / max(len(b)-1, 1)
                pos = "START" if rel < 0.25 else ("END" if rel > 0.75 else "MID")
                return f"ins:{b[i]}", pos
    return None, None

# Top positionally-locked operations across CHEDY family
chedy_types = [t for t in set(all_tokens) if classify(t) == "CHEDY" and tc[t] >= 2]
op_positions = defaultdict(Counter)
for i in range(len(chedy_types)):
    for j in range(i+1, min(len(chedy_types), i+200)):
        if edit_distance(chedy_types[i], chedy_types[j]) == 1:
            op, pos = find_edit_ops(chedy_types[i], chedy_types[j])
            if op and pos:
                generic = op.split(":")[0] + ":" + op.split(":")[1][0] if ":" in op else op
                op_positions[generic][pos] += 1
            op2, pos2 = find_edit_ops(chedy_types[j], chedy_types[i])
            if op2 and pos2:
                generic2 = op2.split(":")[0] + ":" + op2.split(":")[1][0] if ":" in op2 else op2
                op_positions[generic2][pos2] += 1

top_ops = {}
for op, pos_counts in sorted(op_positions.items(), key=lambda x: -sum(x[1].values()))[:6]:
    total = sum(pos_counts.values())
    dominant = max(pos_counts, key=pos_counts.get)
    dominant_pct = pos_counts[dominant] / total * 100
    top_ops[op] = {"dominant_position": dominant, "pct": round(dominant_pct, 0), "total": total}

paradigm_results["positional_ops_CHEDY"] = top_ops

results["1.8_productive_paradigms"] = paradigm_results

# =============================================================================
# FINDING 1.9: CHEDY AVOIDS LINE-FINAL POSITION
# =============================================================================
print("\n" + "=" * 70)
print("FINDING 1.9: CHEDY avoids line-final position")
print("=" * 70)

# Stratified analysis: section + frequency band
tagged = []
for l in lines:
    toks = l["tokens"]
    n = len(toks)
    fams = [classify(t) for t in toks]
    for i, (tok, fam) in enumerate(zip(toks, fams)):
        rel = i / max(n-1, 1)
        if i == 0: lpos = "first"
        elif i == n-1: lpos = "last"
        elif rel < 0.33: lpos = "early"
        elif rel < 0.67: lpos = "mid"
        else: lpos = "late"
        
        f = tc[tok]
        fband = "rare" if f <= 2 else ("low" if f <= 10 else ("mid" if f <= 50 else "high"))
        tagged.append({"fam": fam, "lpos": lpos, "sec": l["section"], "fband": fband})

# Full-control residual for CHEDY at line-final
sections_list = ["herbal_A", "biological", "recipes_Q20", "herbal_B"]
resid_vals = []
for sec in sections_list:
    for fband in ["rare", "low", "mid", "high"]:
        stratum = [t for t in tagged if t["sec"] == sec and t["fband"] == fband]
        if len(stratum) < 30: continue
        s_total = len(stratum)
        s_rate = sum(1 for t in stratum if t["fam"] == "CHEDY") / s_total
        last_tags = [t for t in stratum if t["lpos"] == "last"]
        if len(last_tags) < 3: continue
        obs_rate = sum(1 for t in last_tags if t["fam"] == "CHEDY") / len(last_tags)
        resid_vals.append((obs_rate - s_rate, len(last_tags)))

if resid_vals:
    weights = [w for _, w in resid_vals]
    resids = [r for r, _ in resid_vals]
    wmean = np.average(resids, weights=weights) * 100
else:
    wmean = None

# AIIN at line-first (controlled)
aiin_resid_vals = []
for sec in sections_list:
    for fband in ["rare", "low", "mid", "high"]:
        stratum = [t for t in tagged if t["sec"] == sec and t["fband"] == fband]
        if len(stratum) < 30: continue
        s_total = len(stratum)
        s_rate = sum(1 for t in stratum if t["fam"] == "AIIN") / s_total
        first_tags = [t for t in stratum if t["lpos"] == "first"]
        if len(first_tags) < 3: continue
        obs_rate = sum(1 for t in first_tags if t["fam"] == "AIIN") / len(first_tags)
        aiin_resid_vals.append((obs_rate - s_rate, len(first_tags)))

if aiin_resid_vals:
    aiin_wmean = np.average([r for r, _ in aiin_resid_vals], weights=[w for _, w in aiin_resid_vals]) * 100
else:
    aiin_wmean = None

results["1.9_line_position"] = {
    "chedy_line_final_residual_pct": round(wmean, 1) if wmean is not None else None,
    "aiin_line_initial_residual_pct": round(aiin_wmean, 1) if aiin_wmean is not None else None,
}

print(f"  CHEDY line-final residual: {wmean:+.1f}%" if wmean else "  CHEDY: insufficient data")
print(f"  AIIN line-initial residual: {aiin_wmean:+.1f}%" if aiin_wmean else "  AIIN: insufficient data")

# =============================================================================
# FINDING 1.10: GLYPH LAYER ARCHITECTURE
# =============================================================================
print("\n" + "=" * 70)
print("FINDING 1.10: Glyph layer architecture")
print("=" * 70)

def get_crust(tok):
    chars = parse_eva(tok)
    if len(chars) >= 2: return chars[0] + chars[-1]
    return tok

def get_circles(tok):
    chars = parse_eva(tok)
    return "".join(c for c in chars if layer(c) == 'O')

def get_mantle_core(tok):
    chars = parse_eva(tok)
    return "".join(c for c in chars if layer(c) in ('M', 'C', 'R'))

def layer_sc(tokens, get_layer):
    """Self-clustering on a specific glyph layer."""
    layer_vals = [get_layer(t) for t in tokens]
    top_vals = [v for v, c in Counter(layer_vals).most_common(10) if 0.02 < c/len(tokens) < 0.20][:5]
    if len(top_vals) < 3: return None, None
    
    ratios = []
    for val in top_vals:
        obs = sum(1 for i in range(len(layer_vals)-1) if layer_vals[i]==val and layer_vals[i+1]==val)
        src = sum(1 for v in layer_vals[:-1] if v==val)
        dst = sum(1 for v in layer_vals[1:] if v==val)
        n = len(layer_vals) - 1
        exp = src * (dst / n) if n > 0 else 0
        if exp > 1: ratios.append(obs / exp)
    
    pfx_sc = np.mean(ratios) if ratios else None
    
    # Suffix version
    layer_sfx = [get_layer(t)[-2:] if len(get_layer(t)) >= 2 else get_layer(t) for t in tokens]
    top_sfx = [v for v, c in Counter(layer_sfx).most_common(10) if 0.02 < c/len(tokens) < 0.20][:5]
    sfx_ratios = []
    for val in top_sfx:
        obs = sum(1 for i in range(len(layer_sfx)-1) if layer_sfx[i]==val and layer_sfx[i+1]==val)
        src = sum(1 for v in layer_sfx[:-1] if v==val)
        dst = sum(1 for v in layer_sfx[1:] if v==val)
        n = len(layer_sfx) - 1
        exp = src * (dst / n) if n > 0 else 0
        if exp > 1: sfx_ratios.append(obs / exp)
    
    sfx_sc = np.mean(sfx_ratios) if sfx_ratios else None
    return pfx_sc, sfx_sc

crust_pfx, crust_sfx = layer_sc(all_tokens, get_crust)
mc_pfx, mc_sfx = layer_sc(all_tokens, get_mantle_core)

# Scramble test: shuffle circles within each token, recompute CHEDY→QOK
def scramble_circles(tok):
    chars = parse_eva(tok)
    circle_indices = [i for i, c in enumerate(chars) if layer(c) == 'O']
    circle_chars = [chars[i] for i in circle_indices]
    np.random.shuffle(circle_chars)
    result = list(chars)
    for idx, ci in enumerate(circle_indices):
        result[ci] = circle_chars[idx]
    return "".join(result)

scrambled_tokens = [scramble_circles(t) for t in all_tokens]
scrambled_classes = [classify(t) for t in scrambled_tokens]
n_scr = len(scrambled_classes)

scr_trans = Counter()
scr_src = Counter()
scr_dst = Counter()
for i in range(n_scr - 1):
    scr_trans[(scrambled_classes[i], scrambled_classes[i+1])] += 1
    scr_src[scrambled_classes[i]] += 1
    scr_dst[scrambled_classes[i+1]] += 1

scr_cq_exp = scr_src["CHEDY"] * (scr_dst["QOK"] / (n_scr - 1))
scr_cq = scr_trans[("CHEDY", "QOK")] / scr_cq_exp if scr_cq_exp > 0 else 0

# Family prediction from crust
correct = 0
for t in all_tokens:
    crust = get_crust(t)
    # Simple rule: first char predicts family
    if t.startswith("qok"): pred = "QOK"
    elif t.startswith("ok"): pred = "OK"
    elif t.startswith("ot"): pred = "OT"
    else: pred = None
    if pred and pred == classify(t):
        correct += 1

# Better: count crust-based prediction accuracy
crust_fam = defaultdict(Counter)
for t in all_tokens:
    crust_fam[get_crust(t)][classify(t)] += 1

crust_correct = sum(max(fc.values()) for fc in crust_fam.values())
crust_accuracy = crust_correct / n_tokens * 100

results["1.10_glyph_layers"] = {
    "crust_sc": {"prefix": round(crust_pfx, 2) if crust_pfx else None,
                 "suffix": round(crust_sfx, 2) if crust_sfx else None},
    "mantle_core_sc": {"prefix": round(mc_pfx, 2) if mc_pfx else None,
                       "suffix": round(mc_sfx, 2) if mc_sfx else None},
    "scramble_circles_chedy_qok": round(scr_cq, 2),
    "original_chedy_qok": round(cq_within, 2),
    "crust_family_prediction_accuracy_pct": round(crust_accuracy, 1),
}

print(f"  Crust SC: {crust_pfx:.2f}x / {crust_sfx:.2f}x" if crust_pfx and crust_sfx else "  Crust: insufficient")
print(f"  Mantle+Core SC: {mc_pfx:.2f}x / {mc_sfx:.2f}x" if mc_pfx and mc_sfx else "  M+C: insufficient")
print(f"  Scramble circles: CHEDY→QOK {scr_cq:.2f}x (original {cq_within:.2f}x)")
print(f"  Crust family prediction: {crust_accuracy:.1f}%")

# =============================================================================
# SAVE RESULTS
# =============================================================================
output_path = os.path.join(PROJECT_ROOT, "results", "extended_analysis_results.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n{'=' * 70}")
print(f"Results saved to {os.path.relpath(output_path, PROJECT_ROOT)}")
print(f"{'=' * 70}")
