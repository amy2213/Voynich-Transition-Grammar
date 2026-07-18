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
#
# MIGRATED to the shared canonical module (scripts/_canonical.py). Tokenizer,
# family predicates, and classifier are no longer defined locally; five scripts
# previously carried divergent copies. See _canonical.py for the ordering
# policy and its justification.

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _canonical import (                      # noqa: E402
    load_corpus, flat_tokens, parse_tokens, classify, classify_all,
    is_qok, is_ok, is_ot, is_chedy, is_aiin,
    FAMILY_NAMES, transitions as canon_transitions, transition_ratio,
    ORDER_PREFIX_FIRST, AmbiguityPolicy, build_class_sequences,
    self_clustering_sequences,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# WITHIN_LINE=True is the corrected canonical policy: Finding 1.4 establishes
# that transition structure resets at line boundaries, so the canonical
# transition statistic must not span them. Set to False to reproduce the
# historical (pre-migration) flattened figures.
WITHIN_LINE = True

print("Loading Zandbergen-Landini EVA transliteration via _canonical...")

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

lines = load_corpus()
all_tokens = flat_tokens(lines)
all_classes = classify_all(all_tokens)
n_tokens = len(all_tokens)
class_sequences = build_class_sequences(
    lines, AmbiguityPolicy.CANONICAL_PRECEDENCE
)

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

# Canonical transition matrix. WITHIN_LINE=True computes transitions inside
# lines only (corrected); the legacy path flattens across line boundaries.
if WITHIN_LINE:
    _t = canon_transitions(lines, within_line=True)
    tr = defaultdict(lambda: defaultdict(int))
    for (a, b), n in _t["tr"].items():
        tr[a][b] = n
    src, dst, total_bi = _t["src"], _t["dst"], _t["total"]
else:
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
    # Boundary-matched permutation: shuffle labels inside each line and
    # calculate the permuted cell on the same adjacency sample space.
    n_perms = 2000
    shuf_count = 0
    for _ in range(n_perms):
        sh_obs = 0
        for original in class_sequences:
            sh = list(original)
            np.random.shuffle(sh)
            sh_obs += sum(a == s and b == d for a, b in zip(sh, sh[1:]))
        sh_ratio = sh_obs / exp if exp > 0 else 0
        if ratio and ratio > 1 and sh_ratio >= ratio:
            shuf_count += 1
        elif ratio and ratio < 1 and sh_ratio <= ratio:
            shuf_count += 1
    p_val = (shuf_count + 1) / (n_perms + 1)

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
print("AIIN SUBSTRING AND CANONICAL-FAMILY DENSITY")
print("=" * 70)

page_aiin = {}
for l in lines:
    pg = l["page"]
    if pg not in page_aiin:
        page_aiin[pg] = {"substring": 0, "family": 0, "embedded": 0,
                         "n": 0, "cur": l["currier"], "sec": l["section"]}
    for t in l["tokens"]:
        page_aiin[pg]["n"] += 1
        if is_aiin(t):
            page_aiin[pg]["substring"] += 1
            if classify(t) == "AIIN":
                page_aiin[pg]["family"] += 1
            else:
                page_aiin[pg]["embedded"] += 1

a_pcts = [d["substring"] / d["n"] * 100 for d in page_aiin.values() if d["n"] >= 20 and d["cur"] == "A"]
b_pcts = [d["substring"] / d["n"] * 100 for d in page_aiin.values() if d["n"] >= 20 and d["cur"] == "B"]
a_family = [d["family"] / d["n"] * 100 for d in page_aiin.values() if d["n"] >= 20 and d["cur"] == "A"]
b_family = [d["family"] / d["n"] * 100 for d in page_aiin.values() if d["n"] >= 20 and d["cur"] == "B"]

ks_stat, ks_p = ks_2samp(a_pcts, b_pcts)
family_ks_stat, family_ks_p = ks_2samp(a_family, b_family)

print(f"  Currier A: mean={np.mean(a_pcts):.1f}%, n={len(a_pcts)} pages")
print(f"  Currier B: mean={np.mean(b_pcts):.1f}%, n={len(b_pcts)} pages")
print(f"  KS test: stat={ks_stat:.4f}, p={ks_p:.4f}")
print("  Interpretation: similar observed substring means; equivalence not tested")
print(f"  Canonical AIIN family: A={np.mean(a_family):.1f}%, "
      f"B={np.mean(b_family):.1f}%, KS p={family_ks_p:.4f}")

# Bootstrap CI
diffs = []
all_page_pcts = [(d["substring"] / d["n"] * 100, d["cur"])
                 for d in page_aiin.values()
                 if d["n"] >= 20 and d["cur"] in ["A", "B"]]
for _ in range(5000):
    sample = [all_page_pcts[i] for i in np.random.randint(0, len(all_page_pcts), len(all_page_pcts))]
    sa = [v for v, c in sample if c == "A"]
    sb = [v for v, c in sample if c == "B"]
    if sa and sb:
        diffs.append(np.mean(sa) - np.mean(sb))

ci_lo, ci_hi = np.percentile(diffs, 2.5), np.percentile(diffs, 97.5)
print(f"  Bootstrap 95% CI for difference: [{ci_lo:+.2f}%, {ci_hi:+.2f}%]")

results["aiin_substring_density"] = {
    "currier_a_mean": round(np.mean(a_pcts), 1),
    "currier_b_mean": round(np.mean(b_pcts), 1),
    "ks_p": round(ks_p, 4),
    "bootstrap_ci": [round(ci_lo, 2), round(ci_hi, 2)],
    "status": "descriptive_similarity; equivalence_not_tested",
}
results["aiin_canonical_family_density"] = {
    "currier_a_mean": round(np.mean(a_family), 2),
    "currier_b_mean": round(np.mean(b_family), 2),
    "ks_p": round(family_ks_p, 4),
    "status": "different_under_canonical_classifier",
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
    if sum(len(l["tokens"]) for l in plines) < 40:
        continue
    pseq = build_class_sequences(plines, AmbiguityPolicy.CANONICAL_PRECEDENCE)
    value = self_clustering_sequences(
        pseq,
        included_classes=["QOK", "OK", "OT", "CHEDY", "AIIN"],
    )
    if value is not None:
        page_scs.append(value)

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
    for classes in class_sequences:
        for before, middle, after in zip(classes, classes[1:], classes[2:]):
            if middle == "AIIN" and before == fam:
                total_xf += 1
                if after == fam:
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

qok_base_rate = dst["QOK"] / total_bi
chedy_total_src = Counter()
chedy_to_qok = defaultdict(int)

for line in lines:
    tokens = line["tokens"]
    classes = classify_all(tokens)
    for token, source, dest in zip(tokens, classes, classes[1:]):
        if source == "CHEDY":
            chedy_total_src[token] += 1
            if dest == "QOK":
                chedy_to_qok[token] += 1

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
for line in lines:
    tokens = line["tokens"]
    classes = classify_all(tokens)
    for left, right, source, dest in zip(
            tokens, tokens[1:], classes, classes[1:]):
        if source == "CHEDY" and dest == "QOK":
            cq_pairs[(left, right)] += 1

total_cq = sum(cq_pairs.values())
top5 = sum(c for _, c in cq_pairs.most_common(5))
print(f"  Unique CHEDY→QOK pairs: {len(cq_pairs)}")
print(f"  Top 5 pairs cover: {top5/total_cq*100:.1f}% (distributed = grammatical rule)")
results["token_grammar"]["unique_pairs"] = len(cq_pairs)
results["token_grammar"]["top5_coverage_pct"] = round(top5 / total_cq * 100, 1)
results["methodology"] = {
    "classifier_policy": AmbiguityPolicy.CANONICAL_PRECEDENCE.value,
    "sequence_boundary": "within_line",
    "permutation_unit": "labels_shuffled_within_each_line",
    "monte_carlo_correction": "(b+1)/(B+1)",
}

# ─── Save Results ────────────────────────────────────────────────────────────

output_path = os.path.join(PROJECT_ROOT, "results", "core_analysis_results.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {output_path}")
print("Done.")
