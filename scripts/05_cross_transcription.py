#!/usr/bin/env python3
"""
05_cross_transcription.py — Parse the LSI interlinear file and run
bidirectional self-clustering + transition rules on Currier and FSG
transcriptions separately.

Tests whether the key findings are stable across transcription systems
or are artifacts of the EVA alphabet / Zandbergen-Landini tokenization.

Input: LSI_ivtff_0d.txt (from voynich.nu/data/beta/)
Output: results/cross_transcription_results.json

Transcriber codes in the LSI file:
  C = Currier's transcription (voynich.now)
  F = FSG / First Study Group (Friedman)
  H = Takahashi (complete, EVA encoding)
  V = John Grove
  U = Jorge Stolfi

All transcriptions in the LSI file are mapped to EVA alphabet by Stolfi.
This means C and F lines use EVA characters, not the original Currier or
FSG alphabets. However, the TOKENIZATION (word boundaries, line breaks)
reflects each transcriber's independent judgment. This is the critical
variable: if our findings depend on where Zandbergen-Landini placed word
boundaries, they should differ between transcribers.

Usage:
  python scripts/05_cross_transcription.py

Requirements:
  LSI_ivtff_0d.txt must be present in data/raw/voynich/
  Download from: http://www.voynich.nu/data/beta/LSI_ivtff_0d.txt
"""

import os
import re
import json
import sys
import numpy as np
from collections import Counter, defaultdict

np.random.seed(42)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Locate the LSI file ────────────────────────────────────────────────────

LSI_PATHS = [
    os.path.join(PROJECT_ROOT, "data", "raw", "voynich", "LSI_ivtff_0d.txt"),
    os.path.join(PROJECT_ROOT, "LSI_ivtff_0d.txt"),
    os.path.expanduser("~/LSI_ivtff_0d.txt"),
]

lsi_path = None
for p in LSI_PATHS:
    if os.path.exists(p):
        lsi_path = p
        break

if not lsi_path:
    print("ERROR: LSI_ivtff_0d.txt not found.")
    print("Download from: http://www.voynich.nu/data/beta/LSI_ivtff_0d.txt")
    print(f"Place in: {LSI_PATHS[0]}")
    sys.exit(1)

print(f"Loading LSI file: {lsi_path}")

# ─── Parse IVTFF ────────────────────────────────────────────────────────────

def parse_tokens(text):
    """Clean a raw IVTFF text line into tokens."""
    # Remove inline comments: {anything} and %anything and <!...>
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'%[^ ]*', '', text)
    text = re.sub(r'<[^>]*>', '', text)
    # Remove structural markers
    text = text.replace('!', '').replace('=', '').replace('-', '')
    # Remove uncertainty markers
    text = text.replace('?', '').replace('*', '')
    # Split on dots (word separators in EVA) and whitespace
    text = text.replace('.', ' ')
    tokens = text.strip().split()
    # Filter empty and very short tokens
    tokens = [t for t in tokens if len(t) >= 2 and t.isalpha()]
    return tokens

# Parse all data lines
# Format: <fNNNr.LL,+PP;T> text...
# where T is the transcriber code

LINE_RE = re.compile(r'^<(f\d+[rv])\.(\d+\w?),([^;]*);(\w)>\s*(.*)')

lines_by_transcriber = defaultdict(list)
page_set = set()

with open(lsi_path, 'r', errors='ignore') as f:
    for raw_line in f:
        raw_line = raw_line.strip()
        m = LINE_RE.match(raw_line)
        if not m:
            continue
        
        page = m.group(1)        # e.g., "f1r"
        line_num = m.group(2)    # e.g., "1"
        locus_type = m.group(3)  # e.g., "@P0" or "+P0"
        transcriber = m.group(4) # e.g., "C", "F", "H"
        text = m.group(5)
        
        tokens = parse_tokens(text)
        if not tokens:
            continue
        
        lines_by_transcriber[transcriber].append({
            'page': page,
            'line_num': line_num,
            'tokens': tokens,
        })
        page_set.add(page)

print(f"\nParsed {len(page_set)} pages")
print(f"Lines by transcriber:")
for t in sorted(lines_by_transcriber.keys()):
    n_lines = len(lines_by_transcriber[t])
    n_tokens = sum(len(l['tokens']) for l in lines_by_transcriber[t])
    print(f"  {t}: {n_lines} lines, {n_tokens} tokens")

# ─── Family classification (same as all other scripts) ──────────────────────

def classify(tok):
    tok = tok.lower()
    if "aiin" in tok or "ain" in tok: return "AIIN"
    if tok.startswith("qok"): return "QOK"
    if tok.startswith("ok") and not tok.startswith("qok"): return "OK"
    if tok.startswith("ot"): return "OT"
    if any(p in tok for p in ["chedy", "shedy", "chey", "shey"]): return "CHEDY"
    return "OTHER"

FAMS = ["QOK", "OK", "OT", "CHEDY", "AIIN", "OTHER"]

# ─── Analysis functions ─────────────────────────────────────────────────────

def compute_transition_ratio(classes, src, dst):
    """Obs/expected ratio for src→dst transition."""
    n = len(classes) - 1
    if n < 10: return None
    trans = sum(1 for i in range(n) if classes[i] == src and classes[i+1] == dst)
    s = sum(1 for c in classes[:-1] if c == src)
    d = sum(1 for c in classes[1:] if c == dst)
    exp = s * (d / n) if n > 0 else 0
    return trans / exp if exp > 1 else None

def compute_prefix_suffix_sc(token_list):
    """Compute bidirectional self-clustering."""
    total = len(token_list)
    if total < 500: return None, None, None
    
    # Auto-detect prefix families
    prefix_counts = Counter(t[:2].lower() for t in token_list if len(t) >= 2)
    prefix_fams = [p for p, c in prefix_counts.most_common(30) 
                   if 0.02 < c/total < 0.20][:5]
    
    suffix_counts = Counter(t[-2:].lower() for t in token_list if len(t) >= 2)
    suffix_fams = [s for s, c in suffix_counts.most_common(30)
                   if 0.02 < c/total < 0.20][:5]
    
    if len(prefix_fams) < 3 or len(suffix_fams) < 3:
        return None, None, None
    
    def sc_for(tokens, families, get_fam):
        fam_seq = [get_fam(t) for t in tokens]
        ratios = []
        for fam in families:
            obs = sum(1 for i in range(len(fam_seq)-1) if fam_seq[i]==fam and fam_seq[i+1]==fam)
            src = sum(1 for f in fam_seq[:-1] if f==fam)
            dst = sum(1 for f in fam_seq[1:] if f==fam)
            n = len(fam_seq) - 1
            exp = src * (dst / n) if n > 0 else 0
            if exp > 1: ratios.append(obs / exp)
        return np.mean(ratios) if ratios else None
    
    pfx = sc_for(token_list, prefix_fams, lambda t: t[:2].lower() if len(t)>=2 else "?")
    sfx = sc_for(token_list, suffix_fams, lambda t: t[-2:].lower() if len(t)>=2 else "?")
    
    if pfx and sfx:
        return pfx, sfx, pfx/sfx
    return None, None, None

def compute_within_cross_line(lines_data):
    """Compute within-line vs cross-line transition ratios."""
    within_pairs = []
    for l in lines_data:
        classes = [classify(t) for t in l['tokens']]
        for i in range(len(classes) - 1):
            within_pairs.append((classes[i], classes[i+1]))
    
    cross_pairs = []
    for i in range(len(lines_data) - 1):
        if lines_data[i]['page'] == lines_data[i+1]['page']:
            cross_pairs.append((
                classify(lines_data[i]['tokens'][-1]),
                classify(lines_data[i+1]['tokens'][0])
            ))
    
    cq_within = compute_transition_ratio(
        [c for a, b in within_pairs for c in [a, b]], "CHEDY", "QOK")
    # Recompute properly on the pair lists
    def pair_ratio(pairs, src, dst):
        s = sum(1 for a, _ in pairs if a == src)
        d = sum(1 for _, b in pairs if b == dst)
        both = sum(1 for a, b in pairs if a == src and b == dst)
        total = len(pairs)
        exp = s * (d / total) if total > 0 else 0
        return both / exp if exp > 1 else None
    
    return {
        "chedy_qok_within": pair_ratio(within_pairs, "CHEDY", "QOK"),
        "chedy_qok_cross": pair_ratio(cross_pairs, "CHEDY", "QOK"),
        "aiin_qok_within": pair_ratio(within_pairs, "AIIN", "QOK"),
        "aiin_qok_cross": pair_ratio(cross_pairs, "AIIN", "QOK"),
        "n_within": len(within_pairs),
        "n_cross": len(cross_pairs),
    }

# ─── Run analysis on each major transcriber ─────────────────────────────────

# Focus on transcribers with enough data
TARGET_TRANSCRIBERS = {
    'C': 'Currier',
    'F': 'FSG (Friedman)',
    'H': 'Takahashi',
    'V': 'Grove',
}

results = {}

for code, name in TARGET_TRANSCRIBERS.items():
    lines_data = lines_by_transcriber.get(code, [])
    if not lines_data:
        print(f"\n  {code} ({name}): no data, skipping")
        continue
    
    all_tokens = [t for l in lines_data for t in l['tokens']]
    all_classes = [classify(t) for t in all_tokens]
    n_tokens = len(all_tokens)
    
    if n_tokens < 200:
        print(f"\n  {code} ({name}): only {n_tokens} tokens, skipping")
        continue
    
    print(f"\n{'='*60}")
    print(f"Transcriber {code}: {name} ({n_tokens} tokens, {len(lines_data)} lines)")
    print(f"{'='*60}")
    
    # 1. Transition rules
    cq = compute_transition_ratio(all_classes, "CHEDY", "QOK")
    aq = compute_transition_ratio(all_classes, "AIIN", "QOK")
    print(f"  CHEDY→QOK: {cq:.2f}x" if cq else "  CHEDY→QOK: insufficient")
    print(f"  AIIN→QOK:  {aq:.2f}x" if aq else "  AIIN→QOK: insufficient")
    
    # 2. Bidirectional self-clustering
    pfx, sfx, ratio = compute_prefix_suffix_sc(all_tokens)
    if pfx and sfx:
        bucket = "SYMM-HIGH" if pfx > 1.1 and sfx > 1.1 and 0.8 <= ratio <= 1.25 else \
                 "SUFFIX-DOM" if sfx > 1.1 and ratio < 0.8 else \
                 "SYMM-LOW"
        print(f"  Prefix SC: {pfx:.2f}x, Suffix SC: {sfx:.2f}x, Ratio: {ratio:.2f}, Bucket: {bucket}")
    else:
        pfx = sfx = ratio = None
        bucket = None
        print(f"  Bidirectional SC: insufficient data")
    
    # 3. Within-line vs cross-line grammar
    line_grammar = compute_within_cross_line(lines_data)
    if line_grammar["chedy_qok_within"]:
        print(f"  Within-line C→Q: {line_grammar['chedy_qok_within']:.2f}x, "
              f"Cross-line: {line_grammar['chedy_qok_cross']:.2f}x" 
              if line_grammar['chedy_qok_cross'] else 
              f"  Within-line C→Q: {line_grammar['chedy_qok_within']:.2f}x, Cross-line: insufficient")
    
    # 4. Family distribution
    fam_dist = Counter(all_classes)
    aiin_pct = fam_dist.get("AIIN", 0) / n_tokens * 100
    print(f"  AIIN density: {aiin_pct:.1f}%")
    
    results[code] = {
        "name": name,
        "n_tokens": n_tokens,
        "n_lines": len(lines_data),
        "chedy_qok": round(cq, 2) if cq else None,
        "aiin_qok": round(aq, 2) if aq else None,
        "prefix_sc": round(pfx, 3) if pfx else None,
        "suffix_sc": round(sfx, 3) if sfx else None,
        "ps_ratio": round(ratio, 2) if ratio else None,
        "bucket": bucket,
        "chedy_qok_within": round(line_grammar["chedy_qok_within"], 2) if line_grammar["chedy_qok_within"] else None,
        "chedy_qok_cross": round(line_grammar["chedy_qok_cross"], 2) if line_grammar["chedy_qok_cross"] else None,
        "aiin_pct": round(aiin_pct, 1),
        "family_distribution": {f: round(fam_dist.get(f, 0) / n_tokens * 100, 1) for f in FAMS},
    }

# ─── Comparison summary ─────────────────────────────────────────────────────

print(f"\n\n{'='*70}")
print("CROSS-TRANSCRIPTION STABILITY SUMMARY")
print(f"{'='*70}")
print(f"{'Transcriber':<15} {'Tokens':>7} {'C→Q':>6} {'A→Q':>6} {'Pfx SC':>7} {'Sfx SC':>7} {'Ratio':>6} {'Bucket'}")
print(f"{'-'*65}")

for code in ['C', 'F', 'H', 'V']:
    r = results.get(code)
    if not r: continue
    cq = f"{r['chedy_qok']:.2f}" if r['chedy_qok'] else "n/a"
    aq = f"{r['aiin_qok']:.2f}" if r['aiin_qok'] else "n/a"
    pfx = f"{r['prefix_sc']:.2f}" if r['prefix_sc'] else "n/a"
    sfx = f"{r['suffix_sc']:.2f}" if r['suffix_sc'] else "n/a"
    rat = f"{r['ps_ratio']:.2f}" if r['ps_ratio'] else "n/a"
    bkt = r['bucket'] or "n/a"
    print(f"  {r['name']:<13} {r['n_tokens']:>7} {cq:>6} {aq:>6} {pfx:>7} {sfx:>7} {rat:>6} {bkt}")

# Add ZL baseline for comparison
print(f"  {'ZL (baseline)':<13} {'31608':>7} {'2.63':>6} {'0.50':>6} {'1.52':>7} {'1.54':>7} {'0.99':>6} SYMM-HIGH")

# ─── Save results ────────────────────────────────────────────────────────────

output_path = os.path.join(PROJECT_ROOT, "results", "cross_transcription_results.json")
output = {
    "description": "Cross-transcription stability test. All transcriptions use EVA alphabet "
                   "but differ in tokenization (word boundaries) and coverage.",
    "source_file": "LSI_ivtff_0d.txt (voynich.nu/data/beta/)",
    "transcribers": results,
    "zl_baseline": {
        "chedy_qok": 2.625,
        "aiin_qok": 0.504,
        "prefix_sc": 1.524,
        "suffix_sc": 1.544,
        "ps_ratio": 0.99,
        "bucket": "SYMM-HIGH",
        "n_tokens": 31608,
    },
}

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {os.path.relpath(output_path, PROJECT_ROOT)}")
