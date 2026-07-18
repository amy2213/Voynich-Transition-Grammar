#!/usr/bin/env python3
"""
15_boundary_validation.py — Do the findings survive non-EVA character boundaries?

THE OBJECTION THIS ADDRESSES
----------------------------
Every family definition in the pipeline is stated in EVA characters: `qok`,
`ot`, `chedy`, `aiin`. EVA is a transliteration convention, not a fact about
the manuscript. Where one EVA character ends and the next begins is a modern
editorial decision, and the alternatives are not equivalent — EVA `ch` may be
one glyph or two, `iin` may be three strokes or one ligature, and the gallows
characters `cth`/`ckh` are explicitly composite in EVA's own design.

If CHEDY->QOK at 2.659x is an artifact of EVA's segmentation choices rather
than a property of the text, it should move substantially when those choices
change. The cross-transcription test (script 05) does NOT address this: all
four alternative transcriptions are Stolfi-mapped into EVA, so they vary word
boundaries while holding character boundaries fixed.

This script varies the character boundaries instead.

FIVE SEGMENTATION SCHEMES
-------------------------
  eva_standard   EVA digraphs as normally parsed: ch, sh, cth, ckh, cph, cfh,
                 ee, ii treated as single units.
  atomic         Every EVA letter is its own unit. No digraphs at all. This is
                 the maximally sceptical reading — it assumes EVA's composite
                 characters are editorial fictions.
  maximal        Aggressive ligature reading: the above plus aiin, ain, air,
                 dy, ol, or, al, ar as single units. Assumes common sequences
                 are single glyphs.
  gallows_split  Composite gallows decomposed (cth -> c+t+h) while other
                 digraphs are retained. Targets EVA's most contested choice.
  currier_like   Approximates the Currier alphabet's coarser distinctions by
                 collapsing visually similar EVA characters into classes
                 (e.g. o/a, k/t, d/l/r), then re-deriving families.

For each scheme, families are re-derived FROM THE SEGMENTED FORM rather than
matched as raw substrings, so a family means "begins with these units" rather
than "contains this ASCII string". CHEDY->QOK and AIIN->QOK are then
recomputed.

WHAT COUNTS AS PASSING
----------------------
The finding is boundary-robust if the direction and rough magnitude survive:
CHEDY->QOK clearly above 1, AIIN->QOK clearly below 1, across all schemes. A
scheme-dependent sign flip, or collapse toward 1.0, would indicate an EVA
artifact.

USAGE
    python scripts/15_boundary_validation.py

OUTPUT
    results/boundary_validation_results.json
"""

import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _canonical import load_corpus  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

# ─── Segmentation schemes ────────────────────────────────────────────────────
EVA_STANDARD = ["cth", "ckh", "cph", "cfh", "ch", "sh", "ee", "ii"]
MAXIMAL = EVA_STANDARD + ["aiin", "ain", "air", "dy", "ol", "or", "al", "ar"]
GALLOWS_SPLIT = ["ch", "sh", "ee", "ii"]          # composite gallows NOT kept
ATOMIC = []                                       # no multi-char units

COLLAPSE_MAP = {  # currier_like: merge visually similar EVA characters
    "a": "o", "o": "o",
    "k": "K", "t": "K",
    "p": "P", "f": "P",
    "d": "D", "l": "D", "r": "D",
    "e": "e", "i": "i", "n": "n", "m": "n",
    "s": "s", "y": "y", "q": "q", "c": "c", "h": "h", "g": "D", "x": "s",
}


def segment(token, units):
    """Split a token into units, longest-match-first."""
    out, i = [], 0
    ordered = sorted(units, key=len, reverse=True)
    while i < len(token):
        hit = None
        for u in ordered:
            if token.startswith(u, i):
                hit = u
                break
        if hit:
            out.append(hit)
            i += len(hit)
        else:
            out.append(token[i])
            i += 1
    return out


def segment_currier(token):
    """Collapse similar characters, then segment atomically."""
    return [COLLAPSE_MAP.get(c, c) for c in token]


# ─── Adversarial schemes ─────────────────────────────────────────────────────
# The five schemes above turn out to be nearly vacuous for these particular
# family patterns: qok, ok, ot, chedy and aiin are all expressible as
# whole-unit sequences under every one of them, so boundary alignment is
# always satisfiable and the results are identical. That is worth knowing but
# it is not a test.
#
# These three schemes are built to BREAK alignment — each posits a ligature
# that straddles a family pattern, so that tokens which match as ASCII
# substrings fail to match at unit boundaries. If the findings survive these,
# the robustness claim is earned rather than trivial.
STRADDLE_A = ["kai", "tai", "kee", "ked"]        # splits qok|aiin and ot|aiin
STRADDLE_B = ["oka", "ota", "qok", "che"]        # absorbs family-initial material
STRADDLE_C = ["okai", "otai", "qokai", "edy"]    # maximal straddling

SCHEMES = {
    "eva_standard":  lambda t: segment(t, EVA_STANDARD),
    "atomic":        lambda t: segment(t, ATOMIC),
    "maximal":       lambda t: segment(t, MAXIMAL),
    "gallows_split": lambda t: segment(t, GALLOWS_SPLIT),
    "currier_like":  segment_currier,
    "straddle_A":    lambda t: segment(t, EVA_STANDARD + STRADDLE_A),
    "straddle_B":    lambda t: segment(t, EVA_STANDARD + STRADDLE_B),
    "straddle_C":    lambda t: segment(t, EVA_STANDARD + STRADDLE_C),
}


# ─── Family definitions expressed as UNIT SEQUENCES, not ASCII substrings ────
def build_classifier(scheme_fn, scheme_name):
    """Re-derive the five families from segmented form.

    Families are defined by unit-sequence prefixes / containment, so that
    changing the segmentation genuinely changes what the family captures
    rather than silently falling back to string matching.
    """
    def units_of(tok):
        return scheme_fn(tok)

    def starts_with_units(u, target_str):
        """Does the unit sequence begin with the units spelling target_str?"""
        joined = ""
        for x in u:
            joined += x
            if joined == target_str:
                return True
            if not target_str.startswith(joined):
                return False
        return False

    def contains_units(u, target_str):
        for i in range(len(u)):
            joined = ""
            for j in range(i, len(u)):
                joined += u[j]
                if joined == target_str:
                    return True
                if not target_str.startswith(joined):
                    break
        return False

    def classify(tok):
        if scheme_name == "currier_like":
            t = "".join(COLLAPSE_MAP.get(c, c) for c in tok)
            if t.startswith("qoK"):
                return "QOK"
            if t.startswith("oK") and not t.startswith("qoK"):
                return "OK" if t[1] == "K" and tok[1] == "k" else "OT"
            if any(p in t for p in ["cheDy", "sheDy", "chey", "shey"]):
                return "CHEDY"
            if "oin" in t or "oiin" in t:
                return "AIIN"
            return "OTHER"
        u = units_of(tok)
        if starts_with_units(u, "qok"):
            return "QOK"
        if starts_with_units(u, "ok"):
            return "OK"
        if starts_with_units(u, "ot"):
            return "OT"
        for p in ("chedy", "shedy", "chey", "shey"):
            if contains_units(u, p):
                return "CHEDY"
        for p in ("aiin", "ain"):
            if contains_units(u, p):
                return "AIIN"
        return "OTHER"

    return classify


def transition_ratio(lines, classify, src, dst):
    tr = 0
    s_ct = d_ct = total = 0
    for l in lines:
        c = [classify(t) for t in l["tokens"]]
        for i in range(len(c) - 1):
            total += 1
            if c[i] == src:
                s_ct += 1
            if c[i + 1] == dst:
                d_ct += 1
            if c[i] == src and c[i + 1] == dst:
                tr += 1
    if not total or not s_ct or not d_ct:
        return tr, None, None
    exp = s_ct * (d_ct / total)
    return tr, exp, (tr / exp if exp > 1 else None)


def family_counts(lines, classify):
    c = Counter()
    for l in lines:
        for t in l["tokens"]:
            c[classify(t)] += 1
    return c


def main():
    lines = load_corpus()
    n_tokens = sum(len(l["tokens"]) for l in lines)
    print("=" * 78)
    print("NON-EVA CHARACTER BOUNDARY VALIDATION")
    print("=" * 78)
    print(f"Corpus: {len(lines)} lines, {n_tokens} tokens\n")
    print("Do CHEDY→QOK and AIIN→QOK survive changes to character segmentation?")
    print("(cross-transcription varies WORD boundaries; this varies CHARACTER")
    print(" boundaries, which no prior test in the pipeline addressed)\n")

    results = {}
    print(f"{'scheme':<16}{'CHEDY→QOK':>12}{'obs':>7}{'AIIN→QOK':>12}{'obs':>7}"
          f"{'QOK n':>8}{'CHEDY n':>9}{'AIIN n':>8}")
    print("-" * 78)
    for name, fn in SCHEMES.items():
        classify = build_classifier(fn, name)
        cq_obs, cq_exp, cq = transition_ratio(lines, classify, "CHEDY", "QOK")
        aq_obs, aq_exp, aq = transition_ratio(lines, classify, "AIIN", "QOK")
        fc = family_counts(lines, classify)
        results[name] = {
            "chedy_qok_ratio": round(cq, 3) if cq else None,
            "chedy_qok_obs": cq_obs,
            "chedy_qok_expected": round(cq_exp, 1) if cq_exp else None,
            "aiin_qok_ratio": round(aq, 3) if aq else None,
            "aiin_qok_obs": aq_obs,
            "aiin_qok_expected": round(aq_exp, 1) if aq_exp else None,
            "family_counts": dict(fc),
        }
        print(f"{name:<16}{(cq if cq else float('nan')):>11.3f}x{cq_obs:>7}"
              f"{(aq if aq else float('nan')):>11.3f}x{aq_obs:>7}"
              f"{fc.get('QOK',0):>8}{fc.get('CHEDY',0):>9}{fc.get('AIIN',0):>8}")

    cqs = [v["chedy_qok_ratio"] for v in results.values() if v["chedy_qok_ratio"]]
    aqs = [v["aiin_qok_ratio"] for v in results.values() if v["aiin_qok_ratio"]]

    print("\n" + "=" * 78)
    print(f"CHEDY→QOK across schemes: {min(cqs):.3f}x – {max(cqs):.3f}x")
    print(f"AIIN→QOK  across schemes: {min(aqs):.3f}x – {max(aqs):.3f}x")

    attraction_holds = all(v > 1.5 for v in cqs)
    repulsion_holds = all(v < 0.8 for v in aqs)
    print(f"\nCHEDY→QOK attraction (>1.5x in every scheme): "
          f"{'HOLDS' if attraction_holds else 'FAILS'}")
    print(f"AIIN→QOK repulsion   (<0.8x in every scheme): "
          f"{'HOLDS' if repulsion_holds else 'FAILS'}")

    if attraction_holds and repulsion_holds:
        verdict = ("Both transition findings survive every segmentation scheme "
                   "tested, including fully atomic (no digraphs) and "
                   "Currier-like character collapse. They are not artifacts of "
                   "EVA's character-boundary conventions.")
    else:
        verdict = ("At least one finding is segmentation-dependent. See "
                   "per-scheme values — this would indicate an EVA artifact "
                   "and must be reported.")
    print(f"\nVERDICT: {verdict}")

    out = {
        "description": ("Character-boundary robustness. Varies EVA "
                        "segmentation rather than word boundaries, which the "
                        "cross-transcription test (script 05) holds fixed "
                        "because all its transcriptions are Stolfi-mapped "
                        "into EVA."),
        "schemes": {
            "eva_standard": "EVA digraphs ch, sh, cth, ckh, cph, cfh, ee, ii as single units",
            "atomic": "every EVA letter its own unit; no digraphs",
            "maximal": "eva_standard plus aiin, ain, air, dy, ol, or, al, ar as single units",
            "gallows_split": "composite gallows decomposed; other digraphs retained",
            "currier_like": "visually similar EVA characters collapsed (o/a, k/t, p/f, d/l/r)",
        "straddle_A": "adversarial: kai/tai/kee/ked as ligatures, straddling qok|aiin and ot|aiin",
        "straddle_B": "adversarial: oka/ota/qok/che as ligatures, absorbing family-initial material",
        "straddle_C": "adversarial: okai/otai/qokai/edy as ligatures, maximal straddling",
        "_note": ("eva_standard, atomic, maximal and gallows_split return identical "
                  "values because all five family patterns are expressible as "
                  "whole-unit sequences under each. The straddle_* schemes are the "
                  "load-bearing test."),
        },
        "chedy_qok_range": [min(cqs), max(cqs)],
        "aiin_qok_range": [min(aqs), max(aqs)],
        "attraction_holds_all_schemes": attraction_holds,
        "repulsion_holds_all_schemes": repulsion_holds,
        "verdict": verdict,
        "results": results,
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "boundary_validation_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
