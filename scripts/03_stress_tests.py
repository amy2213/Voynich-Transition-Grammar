#!/usr/bin/env python3
"""
Stress Tests & Accuracy Verification
Tests robustness of core findings under different methods.

Requirements: pip install datasets scipy numpy
Usage: python 03_stress_tests.py
"""

import re
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import ks_2samp, spearmanr
import pandas as pd

np.random.seed(42)

import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parquet_path = os.path.join(PROJECT_ROOT, "data", "raw", "voynich", "AncientLanguages_Voynich_snapshot", "train.parquet")
if not os.path.exists(parquet_path):
    print("ERROR: Run scripts/00_fetch_datasets.py first"); exit(1)
df = pd.read_parquet(parquet_path)
zl = df[df["source_name"] == "Zandbergen-Landini"].copy()
for col in ["H", "L", "Q", "I", "X"]:
    zl[col] = zl[col].fillna("?")

def parse_tokens(text):
    if not text or not isinstance(text, str): return []
    return [t for t in text.strip().split() if not t.startswith("%") and not t.startswith("{") and t not in ["-", "=", "!"]]

def is_qok(tok): return tok.startswith("qok")
def is_ok(tok): return tok.startswith("ok") and not tok.startswith("qok")
def is_ot(tok): return tok.startswith("ot")
def is_chedy(tok): return any(p in tok for p in ["chedy", "shedy", "chey", "shey"])
def is_aiin(tok): return "aiin" in tok or "ain" in tok

def classify(tok):
    if is_aiin(tok): return "AIIN"
    if is_qok(tok): return "QOK"
    if is_ok(tok): return "OK"
    if is_ot(tok): return "OT"
    if is_chedy(tok): return "CHEDY"
    return "OTHER"

lines = []
for _, row in zl.iterrows():
    tokens = parse_tokens(row["text"])
    if tokens:
        lines.append({"page": row["page"], "hand": row["H"], "currier": row["L"], "tokens": tokens})

all_tok = [t for l in lines for t in l["tokens"]]
all_cls = [classify(t) for t in all_tok]
n = len(all_tok)

print(f"Corpus: {len(lines)} lines, {n} tokens")
results = {}

# ─── Test 1: AIIN definition sensitivity ─────────────────────────────────────

print("\n" + "=" * 70)
print("TEST 1: AIIN DEFINITION SENSITIVITY")
print("=" * 70)

pg_data = defaultdict(lambda: {"n": 0, "cur": "?"})
for l in lines:
    pg_data[l["page"]]["cur"] = l["currier"]
    pg_data[l["page"]]["n"] += len(l["tokens"])

defs = {
    "Standard (aiin/ain in tok)": is_aiin,
    "Strict (6 exact tokens)": lambda t: t in ["aiin", "daiin", "ain", "dain", "saiin", "sain"],
    "Loose (contains ii)": lambda t: "ii" in t,
}

results["definition_sensitivity"] = {}
for def_name, fn in defs.items():
    # Recount per page
    page_pcts = defaultdict(lambda: {"a": 0, "n": 0, "cur": "?"})
    for l in lines:
        p = l["page"]
        page_pcts[p]["cur"] = l["currier"]
        for t in l["tokens"]:
            page_pcts[p]["n"] += 1
            if fn(t): page_pcts[p]["a"] += 1

    a = [d["a"] / d["n"] * 100 for d in page_pcts.values() if d["n"] >= 20 and d["cur"] == "A"]
    b = [d["a"] / d["n"] * 100 for d in page_pcts.values() if d["n"] >= 20 and d["cur"] == "B"]
    ks, kp = ks_2samp(a, b) if a and b else (0, 1)
    verdict = "INVARIANT" if kp > 0.05 else "DIFFERENT"
    print(f"  {def_name:<35}: A={np.mean(a):.1f}% B={np.mean(b):.1f}% KS p={kp:.4f} {verdict}")
    results["definition_sensitivity"][def_name] = {"a_mean": round(np.mean(a), 1), "b_mean": round(np.mean(b), 1), "ks_p": round(kp, 4)}

# ─── Test 2: Transition rules by text type ────────────────────────────────────

print("\n" + "=" * 70)
print("TEST 2: TRANSITION RULES BY TEXT TYPE (line length)")
print("=" * 70)

results["text_type_robustness"] = {}
for type_name, min_len, max_len in [("Short ≤3", 1, 3), ("Medium 4-8", 4, 8), ("Long ≥9", 9, 999)]:
    ttok = [t for l in lines if min_len <= len(l["tokens"]) <= max_len for t in l["tokens"]]
    if len(ttok) < 200: continue
    tcls = [classify(t) for t in ttok]
    ttr = defaultdict(lambda: defaultdict(int))
    tsc = defaultdict(int); tdc = defaultdict(int); ttot = len(tcls) - 1
    for i in range(ttot):
        ttr[tcls[i]][tcls[i + 1]] += 1; tsc[tcls[i]] += 1; tdc[tcls[i + 1]] += 1

    cq_obs = ttr["CHEDY"]["QOK"]
    cq_exp = tsc["CHEDY"] * (tdc["QOK"] / ttot) if ttot > 0 and tsc["CHEDY"] > 0 and tdc["QOK"] > 0 else 0
    cq_r = cq_obs / cq_exp if cq_exp > 1 else None

    aq_obs = ttr["AIIN"]["QOK"]
    aq_exp = tsc["AIIN"] * (tdc["QOK"] / ttot) if ttot > 0 and tsc["AIIN"] > 0 and tdc["QOK"] > 0 else 0
    aq_r = aq_obs / aq_exp if aq_exp > 1 else None

    print(f"  {type_name}: CHEDY→QOK={'%.2fx' % cq_r if cq_r else 'n/a'}, AIIN→QOK={'%.2fx' % aq_r if aq_r else 'n/a'} ({len(ttok)} tokens)")
    results["text_type_robustness"][type_name] = {"chedy_qok": round(cq_r, 2) if cq_r else None, "aiin_qok": round(aq_r, 2) if aq_r else None}

# ─── Test 3: Split-half reliability ──────────────────────────────────────────

print("\n" + "=" * 70)
print("TEST 3: SPLIT-HALF RELIABILITY (100 splits)")
print("=" * 70)

n_splits = 100
split_metrics = defaultdict(lambda: {"a": [], "b": []})

def compute_split_metrics(indices):
    htok = [t for i in indices for t in lines[i]["tokens"]]
    hcls = [classify(t) for t in htok]
    htr = defaultdict(lambda: defaultdict(int))
    hsc = defaultdict(int); hdc = defaultdict(int); htot = len(hcls) - 1
    for i in range(htot):
        htr[hcls[i]][hcls[i + 1]] += 1; hsc[hcls[i]] += 1; hdc[hcls[i + 1]] += 1
    cq_exp = hsc["CHEDY"] * (hdc["QOK"] / htot) if htot > 0 and hsc["CHEDY"] > 0 and hdc["QOK"] > 0 else 1
    aq_exp = hsc["AIIN"] * (hdc["QOK"] / htot) if htot > 0 and hsc["AIIN"] > 0 and hdc["QOK"] > 0 else 1
    sv = [htr[f][f] / (hsc[f] * (hdc[f] / htot)) for f in ["QOK", "OK", "OT", "CHEDY", "AIIN"]
          if hsc[f] * (hdc[f] / htot) > 1] if htot > 0 else []
    return {
        "cq": htr["CHEDY"]["QOK"] / cq_exp if cq_exp > 0 else 0,
        "aq": htr["AIIN"]["QOK"] / aq_exp if aq_exp > 0 else 0,
        "sc": np.mean(sv) if sv else 0,
        "aiin": sum(1 for c in hcls if c == "AIIN") / len(hcls) * 100,
    }

for _ in range(n_splits):
    perm = np.random.permutation(len(lines))
    half = len(lines) // 2
    ma = compute_split_metrics(perm[:half])
    mb = compute_split_metrics(perm[half:])
    for k in ma:
        split_metrics[k]["a"].append(ma[k])
        split_metrics[k]["b"].append(mb[k])

results["split_half"] = {}
for metric in ["cq", "aq", "sc", "aiin"]:
    a_vals = split_metrics[metric]["a"]
    b_vals = split_metrics[metric]["b"]
    all_vals = a_vals + b_vals
    label = {"cq": "CHEDY→QOK", "aq": "AIIN→QOK", "sc": "Self-cluster", "aiin": "AIIN %"}[metric]
    spread = [round(np.percentile(all_vals, 2.5), 3), round(np.percentile(all_vals, 97.5), 3)]
    print(f"  {label:<15}: mean={np.mean(all_vals):.3f}, 95% range={spread}")
    results["split_half"][metric] = {"mean": round(np.mean(all_vals), 3), "range_95": spread}

# ─── Test 4: Self-clustering with shuffle control per section ─────────────────

print("\n" + "=" * 70)
print("TEST 4: SELF-CLUSTERING SHUFFLE CONTROL BY SECTION")
print("=" * 70)

def get_section(page):
    m = re.match(r"f(\d+)", page)
    if not m: return "unknown"
    num = int(m.group(1))
    if num <= 57: return "herbal_A"
    elif 75 <= num <= 84: return "biological"
    elif 103 <= num <= 116: return "recipes_Q20"
    elif 87 <= num <= 102: return "herbal_B"
    elif 67 <= num <= 73: return "astronomical"
    return "other"

results["section_self_clustering"] = {}
for sec in ["herbal_A", "biological", "recipes_Q20", "herbal_B"]:
    stok = [t for l in lines if get_section(l["page"]) == sec for t in l["tokens"]]
    if len(stok) < 100: continue
    scls = [classify(t) for t in stok]
    ttr = defaultdict(lambda: defaultdict(int))
    tsc = defaultdict(int); tdc = defaultdict(int); ttot = len(scls) - 1
    for i in range(ttot):
        ttr[scls[i]][scls[i + 1]] += 1; tsc[scls[i]] += 1; tdc[scls[i + 1]] += 1

    real_vals = [ttr[f][f] / (tsc[f] * (tdc[f] / ttot)) for f in ["QOK", "OK", "OT", "CHEDY", "AIIN"]
                 if tsc[f] * (tdc[f] / ttot) > 1]
    real = np.mean(real_vals) if real_vals else 0

    shuf_means = []
    for _ in range(1000):
        sh = scls.copy(); np.random.shuffle(sh)
        str2 = defaultdict(lambda: defaultdict(int))
        ssc = defaultdict(int); sdc = defaultdict(int)
        for i in range(len(sh) - 1):
            str2[sh[i]][sh[i + 1]] += 1; ssc[sh[i]] += 1; sdc[sh[i + 1]] += 1
        sv = [str2[f][f] / (ssc[f] * (sdc[f] / ttot)) for f in ["QOK", "OK", "OT", "CHEDY", "AIIN"]
              if ssc[f] * (sdc[f] / ttot) > 1]
        if sv: shuf_means.append(np.mean(sv))

    p_val = np.mean([s >= real for s in shuf_means]) if shuf_means else 1
    print(f"  {sec:<15}: real={real:.3f}x, shuffle={np.mean(shuf_means):.3f}±{np.std(shuf_means):.3f}, p={p_val:.4f}")
    results["section_self_clustering"][sec] = {"real": round(real, 3), "shuffle_mean": round(np.mean(shuf_means), 3), "p": round(p_val, 4)}

# ─── Save ─────────────────────────────────────────────────────────────────────

with open(os.path.join(PROJECT_ROOT, "results", "stress_test_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to results/stress_test_results.json")
