#!/usr/bin/env python3
"""
Voynich Manuscript Transition Grammar Analysis
Core analysis script — reproduces all verified findings.

Requirements: pip install datasets scipy numpy
Data source: AncientLanguages/Voynich on Hugging Face

Usage: python 01_core_analysis.py
"""

import re
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import ks_2samp, chi2_contingency
import pandas as pd

np.random.seed(42)

# ─── Load Data ───────────────────────────────────────────────────────────────

print("Loading Zandbergen-Landini EVA transliteration from local snapshot...")
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parquet_path = os.path.join(PROJECT_ROOT, "data", "raw", "voynich", "AncientLanguages_Voynich_snapshot", "train.parquet")
if not os.path.exists(parquet_path):
    print("ERROR: Run scripts/00_fetch_datasets.py first")
    exit(1)
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

def is_qok(tok):   return tok.startswith("qok")
def is_ok(tok):    return tok.startswith("ok") and not tok.startswith("qok")
def is_ot(tok):    return tok.startswith("ot")
def is_chedy(tok): return any(p in tok for p in ["chedy", "shedy", "chey", "shey"])
def is_aiin(tok):  return "aiin" in tok or "ain" in tok

FAMILIES = {"QOK": is_qok, "OK": is_ok, "OT": is_ot, "CHEDY": is_chedy, "AIIN": is_aiin}
FAMILY_NAMES = ["QOK", "OK", "OT", "CHEDY", "AIIN", "OTHER"]

def classify(tok):
    for name, fn in FAMILIES.items():
        if fn(tok):
            return name
    return "OTHER"

def get_section(page):
    m = re.match(r"f(\d+)", page)
    if not m:
        return "unknown"
    n = int(m.group(1))
    if n <= 57:       return "herbal_A"
    elif n == 58:     return "text_f58"
    elif 67 <= n <= 73: return "astronomical"
    elif 75 <= n <= 84: return "biological"
    elif 87 <= n <= 102: return "herbal_B"
    elif 103 <= n <= 116: return "recipes_Q20"
    return "other"

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
n_tokens = len(all_tokens)

print(f"Loaded: {len(lines)} lines, {n_tokens} tokens, {len(set(l['page'] for l in lines))} pages")

# ─── Transition Matrix ───────────────────────────────────────────────────────

def compute_transitions(classes):
    tr = defaultdict(lambda: defaultdict(int))
    src = defaultdict(int)
    dst = defaultdict(int)
    total = len(classes) - 1
    for i in range(total):
        tr[classes[i]][classes[i + 1]] += 1
        src[classes[i]] += 1
        dst[classes[i + 1]] += 1
    return tr, src, dst, total

def transition_ratio(tr, src, dst, total, s, d):
    obs = tr[s][d]
    exp = src[s] * (dst[d] / total) if total > 0 and src[s] > 0 and dst[d] > 0 else 0
    return obs, exp, (obs / exp if exp > 1 else None)

tr, src, dst, total_bi = compute_transitions(all_classes)

print("\n" + "=" * 70)
print("TRANSITION RULES")
print("=" * 70)

rules = [
    ("CHEDY→QOK", "CHEDY", "QOK"), ("AIIN→QOK", "AIIN", "QOK"),
    ("QOK→AIIN", "QOK", "AIIN"),   ("AIIN→OK", "AIIN", "OK"),
    ("AIIN→OT", "AIIN", "OT"),     ("OT→OT", "OT", "OT"),
]

results = {"transition_rules": {}}
for label, s, d in rules:
    obs, exp, ratio = transition_ratio(tr, src, dst, total_bi, s, d)
    # Shuffle test
    n_perms = 2000
    shuf_count = 0
    for _ in range(n_perms):
        sh = all_classes.copy()
        np.random.shuffle(sh)
        sh_obs = sum(1 for i in range(len(sh) - 1) if sh[i] == s and sh[i + 1] == d)
        sh_ratio = sh_obs / exp if exp > 0 else 0
        if ratio and ratio > 1 and sh_ratio >= ratio:
            shuf_count += 1
        elif ratio and ratio < 1 and sh_ratio <= ratio:
            shuf_count += 1
    p_val = shuf_count / n_perms

    print(f"  {label:<12}: ratio={ratio:.3f}x  obs={obs}  exp={exp:.0f}  p={p_val:.4f}")
    results["transition_rules"][label] = {
        "ratio": round(ratio, 3) if ratio else None,
        "obs": obs, "exp": round(exp, 1), "p": round(p_val, 4),
    }

# ─── Full Transition Matrix ──────────────────────────────────────────────────

print("\n  Full matrix (obs/expected):")
print(f"  {'':8}", end="")
for d in FAMILY_NAMES:
    print(f" {d:>7}", end="")
print()
matrix_data = {}
for s in FAMILY_NAMES:
    print(f"  {s:<8}", end="")
    matrix_data[s] = {}
    for d in FAMILY_NAMES:
        _, _, ratio = transition_ratio(tr, src, dst, total_bi, s, d)
        val = f"{ratio:.2f}x" if ratio else "  n/a "
        print(f" {val:>7}", end="")
        matrix_data[s][d] = round(ratio, 3) if ratio else None
    print()

obs_mat = np.array([[tr[s][d] for d in FAMILY_NAMES] for s in FAMILY_NAMES])
rs = obs_mat.sum(1); cs = obs_mat.sum(0); v = (rs > 0) & (cs > 0)
chi2_val, chi2_p, _, _ = chi2_contingency(obs_mat[np.ix_(v, v)])
print(f"\n  Chi² = {chi2_val:.1f}, p = {chi2_p:.2e}")
results["transition_matrix"] = matrix_data
results["chi2"] = {"value": round(chi2_val, 1), "p": f"{chi2_p:.2e}"}

# ─── AIIN Invariance ─────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("AIIN INVARIANCE")
print("=" * 70)

page_aiin = {}
for l in lines:
    pg = l["page"]
    if pg not in page_aiin:
        page_aiin[pg] = {"a": 0, "n": 0, "cur": l["currier"], "sec": l["section"]}
    for t in l["tokens"]:
        page_aiin[pg]["n"] += 1
        if is_aiin(t):
            page_aiin[pg]["a"] += 1

a_pcts = [d["a"] / d["n"] * 100 for d in page_aiin.values() if d["n"] >= 20 and d["cur"] == "A"]
b_pcts = [d["a"] / d["n"] * 100 for d in page_aiin.values() if d["n"] >= 20 and d["cur"] == "B"]

ks_stat, ks_p = ks_2samp(a_pcts, b_pcts)

print(f"  Currier A: mean={np.mean(a_pcts):.1f}%, n={len(a_pcts)} pages")
print(f"  Currier B: mean={np.mean(b_pcts):.1f}%, n={len(b_pcts)} pages")
print(f"  KS test: stat={ks_stat:.4f}, p={ks_p:.4f}")
print(f"  Verdict: {'INVARIANT' if ks_p > 0.05 else 'DIFFERENT'}")

# Bootstrap CI
diffs = []
all_page_pcts = [(d["a"] / d["n"] * 100, d["cur"]) for d in page_aiin.values() if d["n"] >= 20 and d["cur"] in ["A", "B"]]
for _ in range(5000):
    sample = [all_page_pcts[i] for i in np.random.randint(0, len(all_page_pcts), len(all_page_pcts))]
    sa = [v for v, c in sample if c == "A"]
    sb = [v for v, c in sample if c == "B"]
    if sa and sb:
        diffs.append(np.mean(sa) - np.mean(sb))

ci_lo, ci_hi = np.percentile(diffs, 2.5), np.percentile(diffs, 97.5)
print(f"  Bootstrap 95% CI for difference: [{ci_lo:+.2f}%, {ci_hi:+.2f}%]")

results["aiin_invariance"] = {
    "currier_a_mean": round(np.mean(a_pcts), 1),
    "currier_b_mean": round(np.mean(b_pcts), 1),
    "ks_p": round(ks_p, 4),
    "bootstrap_ci": [round(ci_lo, 2), round(ci_hi, 2)],
}

# ─── Family Densities by Section ─────────────────────────────────────────────

print("\n" + "=" * 70)
print("FAMILY DENSITIES BY SECTION")
print("=" * 70)

sections = ["herbal_A", "biological", "recipes_Q20", "herbal_B", "astronomical", "text_f58"]
results["section_densities"] = {}

print(f"  {'Section':<15} {'QOK':>6} {'OK':>6} {'OT':>6} {'CHEDY':>7} {'AIIN':>7} {'N':>7}")
for sec in sections:
    stok = [t for l in lines if l["section"] == sec for t in l["tokens"]]
    if not stok:
        continue
    cc = Counter(classify(t) for t in stok)
    n = len(stok)
    print(f"  {sec:<15} {cc['QOK']/n*100:>5.1f}% {cc['OK']/n*100:>5.1f}% {cc['OT']/n*100:>5.1f}% "
          f"{cc['CHEDY']/n*100:>6.1f}% {cc['AIIN']/n*100:>6.1f}% {n:>7}")
    results["section_densities"][sec] = {
        f: round(cc[f] / n * 100, 1) for f in FAMILY_NAMES
    }
    results["section_densities"][sec]["tokens"] = n

# ─── Self-Clustering ─────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("SELF-CLUSTERING")
print("=" * 70)

results["self_clustering"] = {}
for method, label in [("backbone", "Pooled backbone"), ("all", "Pooled all classes")]:
    fams = ["QOK", "OK", "OT", "CHEDY", "AIIN"] if method == "backbone" else FAMILY_NAMES
    sc_vals = []
    for f in fams:
        obs = tr[f][f]
        exp = src[f] * (dst[f] / total_bi) if src[f] > 0 and dst[f] > 0 else 0
        if exp > 1:
            sc_vals.append(obs / exp)
    mean_sc = np.mean(sc_vals) if sc_vals else 0
    print(f"  {label}: {mean_sc:.3f}x")
    results["self_clustering"][method] = round(mean_sc, 3)

# Page-level
page_scs = []
page_lines_map = defaultdict(list)
for l in lines:
    page_lines_map[l["page"]].append(l)

for pg, plines in page_lines_map.items():
    ptok = [t for l in plines for t in l["tokens"]]
    if len(ptok) < 40:
        continue
    pcls = [classify(t) for t in ptok]
    ptr, psc, pdc, ptot = compute_transitions(pcls)
    vals = []
    for f in ["QOK", "OK", "OT", "CHEDY", "AIIN"]:
        obs = ptr[f][f]
        exp = psc[f] * (pdc[f] / ptot) if ptot > 0 and psc[f] > 0 and pdc[f] > 0 else 0
        if exp > 1:
            vals.append(obs / exp)
    if vals:
        page_scs.append(np.mean(vals))

print(f"  Page-level mean: {np.mean(page_scs):.3f}x (n={len(page_scs)} pages)")
results["self_clustering"]["page_level"] = round(np.mean(page_scs), 3)

# ─── Carry-Through ───────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("CARRY-THROUGH")
print("=" * 70)

results["carry_through"] = {}
for fam in ["QOK", "OK", "OT", "CHEDY"]:
    carry = 0
    total_xf = 0
    for i in range(1, len(all_classes) - 1):
        if all_classes[i] == "AIIN" and all_classes[i - 1] == fam:
            total_xf += 1
            if all_classes[i + 1] == fam:
                carry += 1
    if total_xf >= 5:
        base = dst[fam] / total_bi
        rate = carry / total_xf
        ratio = rate / base if base > 0 else 0
        print(f"  {fam}→AIIN→{fam}: {ratio:.2f}x ({carry}/{total_xf})")
        results["carry_through"][fam] = round(ratio, 2)

# ─── Token-Level Grammar Test ────────────────────────────────────────────────

print("\n" + "=" * 70)
print("TOKEN-LEVEL GRAMMAR TEST")
print("=" * 70)

qok_base_rate = sum(1 for c in all_classes[1:] if c == "QOK") / (n_tokens - 1)
chedy_total_src = Counter()
chedy_to_qok = defaultdict(int)

for i in range(n_tokens - 1):
    if is_chedy(all_tokens[i]):
        chedy_total_src[all_tokens[i]] += 1
        if is_qok(all_tokens[i + 1]):
            chedy_to_qok[all_tokens[i]] += 1

attractors = 0
tested = 0
for tok in chedy_total_src:
    if chedy_total_src[tok] < 5:
        continue
    tested += 1
    rate = chedy_to_qok[tok] / chedy_total_src[tok]
    ratio = rate / qok_base_rate
    if ratio > 1.3:
        attractors += 1

print(f"  CHEDY tokens attracting QOK: {attractors}/{tested} ({attractors/tested*100:.0f}%)")
results["token_grammar"] = {
    "chedy_attractors": attractors,
    "chedy_tested": tested,
    "chedy_pct": round(attractors / tested * 100, 0),
}

# Count unique CHEDY→QOK pairs
cq_pairs = Counter()
for i in range(n_tokens - 1):
    if is_chedy(all_tokens[i]) and is_qok(all_tokens[i + 1]):
        cq_pairs[(all_tokens[i], all_tokens[i + 1])] += 1

total_cq = sum(cq_pairs.values())
top5 = sum(c for _, c in cq_pairs.most_common(5))
print(f"  Unique CHEDY→QOK pairs: {len(cq_pairs)}")
print(f"  Top 5 pairs cover: {top5/total_cq*100:.1f}% (distributed = grammatical rule)")
results["token_grammar"]["unique_pairs"] = len(cq_pairs)
results["token_grammar"]["top5_coverage_pct"] = round(top5 / total_cq * 100, 1)

# ─── Save Results ────────────────────────────────────────────────────────────

output_path = os.path.join(PROJECT_ROOT, "results", "core_analysis_results.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {output_path}")
print("Done.")
