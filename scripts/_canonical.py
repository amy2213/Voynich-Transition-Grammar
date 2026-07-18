#!/usr/bin/env python3
"""
_canonical.py — Single source of truth for tokenization and family assignment.

WHY THIS MODULE EXISTS
----------------------
Family classification was defined independently in five scripts with two
different priority orders:

    scripts/01_core_analysis.py     QOK -> OK -> OT -> CHEDY -> AIIN
    scripts/08_per_scribe_analysis  QOK -> OK -> OT -> CHEDY -> AIIN
    scripts/02_cross_linguistic.py  AIIN -> QOK -> OK -> OT -> CHEDY
    scripts/03_stress_tests.py      AIIN -> QOK -> OK -> OT -> CHEDY
    scripts/04_extended_analysis.py AIIN -> QOK -> OK -> OT -> CHEDY

Measured on the ZL corpus (31,608 tokens), the two orders disagree on
191 types / 4,269 token instances (3.59% of corpus). The headline CHEDY->QOK
statistic and the stress tests validating it were therefore computed over
different data models.

THE ROOT CAUSE IS NOT THE ORDER — IT IS THE FAMILY DEFINITIONS
--------------------------------------------------------------
QOK / OK / OT are *prefix* tests (word-initial material).
CHEDY / AIIN are *substring* tests (material anywhere in the token).

Mixing prefix and substring predicates in one priority chain means overlap is
guaranteed. Measured overlap: 1,423 token instances (4.50% of corpus),
160 types, distributed as:

    QOK + AIIN     547     (qokain, qokaiin, ...)
    OK  + AIIN     359     (okaiin, okain, ...)
    OT  + AIIN     253     (otaiin, otain, ...)
    QOK + CHEDY     97     (qokchedy, ...)
    OK  + CHEDY     78     (okchey, ...)
    OT  + CHEDY     77
    CHEDY + AIIN    12

`qokaiin` is genuinely both a QOK-prefixed token and an AIIN-containing token.
No priority order makes that fact go away; it only hides it. This module makes
the overlap explicit and lets each analysis declare how it handles it, instead
of inheriting a silent decision from whichever file it was copied from.

WHAT DEPENDS ON THE CHOICE (measured)
-------------------------------------
                                    CHEDY->QOK      AIIN->QOK
    prefix-first,  flattened          2.625x          0.504x   <- published
    prefix-first,  within-line        2.659x          0.444x
    substring-first, flattened        2.497x          0.475x
    substring-first, within-line      2.535x          0.402x

Two things follow.

1. The headline effect is robust to the choice: the full spread is
   2.497x-2.659x, roughly 6%. The finding survives; the reported figure moves.

2. `durable_findings.md` §3.5 records the earlier 2.50x value as corrected to
   2.625x, attributing the difference to "token-parsing variation." That
   attribution is incorrect. 2.497x is what the substring-first order produces
   on the identical frozen dataset; 2.625x is what prefix-first produces. The
   discrepancy was a classifier-order difference, not parsing noise. §3.5
   should be amended.

DEFAULT AND ITS JUSTIFICATION
-----------------------------
Default is PREFIX_FIRST, for three reasons:

  (a) It matches `01_core_analysis.py`, the source of every currently published
      canonical value, so adopting it does not silently restate the record.
  (b) The prefix families are defined on a structurally privileged position.
      Voynichese word-initial material is the most constrained region of the
      token, and the project's own Finding 1.9 reports family identity is best
      predicted by crust characters (79.4%). Word-initial evidence should
      therefore take precedence over "contains this string anywhere."
  (c) AIIN-first assigns `qokaiin` to AIIN, which places a qok-initial token in
      the family the project treats as function-word-like. That is the less
      defensible of the two readings.

This is a judgment call, not a derivation. It is recorded here so it can be
argued with, and `ORDER_SUBSTRING_FIRST` plus `strict=True` are provided so any
result can be re-run under the alternatives. Every analysis should report which
policy it used.

USAGE
-----
    from _canonical import load_corpus, classify, FAMILY_NAMES

    lines = load_corpus()                 # list[Line]
    fam   = classify(token)               # default policy
    fam   = classify(token, strict=True)  # returns "AMBIGUOUS" on overlap

    from _canonical import transitions, self_clustering
    tr = transitions(lines, within_line=True)      # line-respecting (correct)
    tr = transitions(lines, within_line=False)     # legacy flattened

Run directly for a diagnostic report:
    python scripts/_canonical.py
"""

import os
import re
from dataclasses import dataclass
from enum import Enum
from collections import Counter, defaultdict

import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARQUET_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "voynich",
                            "AncientLanguages_Voynich_snapshot", "train.parquet")

FAMILY_NAMES = ["QOK", "OK", "OT", "CHEDY", "AIIN", "OTHER"]
AMBIGUOUS = "AMBIGUOUS"


class AmbiguityPolicy(str, Enum):
    """Explicit policies for tokens matching more than one family."""

    CANONICAL_PRECEDENCE = "canonical_precedence"
    SUBSTRING_PRECEDENCE = "substring_precedence"
    AMBIGUOUS_AS_CLASS = "ambiguous_as_class"
    DROP_AND_BREAK_SEQUENCE = "drop_and_break_sequence"


@dataclass(frozen=True)
class SequenceUnit:
    """One natural sequence unit that must never be joined implicitly."""

    unit_id: str
    tokens: tuple
    boundary_type: str = "line"
    page: str = ""
    section: str = ""
    hand: str = ""
    currier: str = ""
    document: str = ""


# ─── Family predicates ───────────────────────────────────────────────────────
# Kept byte-identical to the historical definitions so that adopting this
# module changes results ONLY through the ordering/line-boundary policy, never
# through a silent redefinition of what a family is.

def is_qok(tok):   return tok.startswith("qok")
def is_ok(tok):    return tok.startswith("ok") and not tok.startswith("qok")
def is_ot(tok):    return tok.startswith("ot")
def is_chedy(tok): return any(p in tok for p in ["chedy", "shedy", "chey", "shey"])
def is_aiin(tok):  return "aiin" in tok or "ain" in tok

PREDICATES = {
    "QOK": is_qok, "OK": is_ok, "OT": is_ot,
    "CHEDY": is_chedy, "AIIN": is_aiin,
}

PREFIX_FAMILIES = ("QOK", "OK", "OT")        # word-initial predicates
SUBSTRING_FAMILIES = ("CHEDY", "AIIN")       # anywhere-in-token predicates

ORDER_PREFIX_FIRST = ["QOK", "OK", "OT", "CHEDY", "AIIN"]      # 01, 08
ORDER_SUBSTRING_FIRST = ["AIIN", "QOK", "OK", "OT", "CHEDY"]   # 02, 03, 04

DEFAULT_ORDER = ORDER_PREFIX_FIRST


# ─── Tokenizer ───────────────────────────────────────────────────────────────
def parse_tokens(text):
    """Canonical tokenizer. Identical to 01_core_analysis.py's original."""
    if not text or not isinstance(text, str):
        return []
    return [t for t in text.strip().split()
            if not t.startswith("%") and not t.startswith("{")
            and t not in ["-", "=", "!"]]


def parse_tokens_ivtff(text):
    """Tokenizer for RAW IVTFF source (e.g. LSI_ivtff_0d.txt).

    Distinct from `parse_tokens` by necessity, not by accident. The parquet
    snapshot is already cleaned; raw IVTFF still carries inline comments,
    uncertainty markers, and dot word-separators that must be stripped first.

    MEASURED DIFFERENCE against `parse_tokens` on the ZL corpus:

        parse_tokens        31,608 tokens
        parse_tokens_ivtff  30,298 tokens
        gap                  1,310  =  1,161 tokens shorter than 2 chars
                                    +    149 tokens containing non-alpha chars

    The gap is fully accounted for by this function's two extra filters
    (len >= 2 and isalpha), not by any difference in word segmentation. Scripts
    reading the parquet should use `parse_tokens`; scripts reading raw IVTFF
    should use this. Both now live here so the divergence stays documented.
    """
    if not text or not isinstance(text, str):
        return []
    text = re.sub(r"\{[^}]*\}", "", text)
    text = re.sub(r"%[^ ]*", "", text)
    text = re.sub(r"<[^>]*>", "", text)
    for ch in "!=-?*":
        text = text.replace(ch, "")
    text = text.replace(".", " ")
    return [t for t in text.strip().split() if len(t) >= 2 and t.isalpha()]


# ─── Classification ──────────────────────────────────────────────────────────
def matching_families(tok):
    """All families whose predicate the token satisfies. Order-independent."""
    return tuple(name for name in FAMILY_NAMES[:-1] if PREDICATES[name](tok))


def classify(tok, order=None, strict=False):
    """Assign a token to one family.

    order   -- priority list; defaults to DEFAULT_ORDER (prefix-first).
    strict  -- if True, tokens matching more than one family return
               AMBIGUOUS instead of being silently resolved by priority.
               Use for any analysis where a 4.5% misassignment would matter.
    """
    hits = matching_families(tok)
    if not hits:
        return "OTHER"
    if strict and len(hits) > 1:
        return AMBIGUOUS
    for name in (order or DEFAULT_ORDER):
        if name in hits:
            return name
    return "OTHER"


def classify_all(tokens, order=None, strict=False):
    return [classify(t, order=order, strict=strict) for t in tokens]


def classify_with_policy(tok, policy=AmbiguityPolicy.CANONICAL_PRECEDENCE):
    """Classify under a named, auditable ambiguity policy."""
    policy = AmbiguityPolicy(policy)
    if policy == AmbiguityPolicy.CANONICAL_PRECEDENCE:
        return classify(tok, order=ORDER_PREFIX_FIRST)
    if policy == AmbiguityPolicy.SUBSTRING_PRECEDENCE:
        return classify(tok, order=ORDER_SUBSTRING_FIRST)
    if policy in (AmbiguityPolicy.AMBIGUOUS_AS_CLASS,
                  AmbiguityPolicy.DROP_AND_BREAK_SEQUENCE):
        return classify(tok, order=ORDER_PREFIX_FIRST, strict=True)
    raise ValueError(f"Unsupported ambiguity policy: {policy}")


# ─── Corpus loading ──────────────────────────────────────────────────────────
def get_section(page):
    m = re.match(r"f(\d+)", page or "")
    if not m:
        return "unknown"
    n = int(m.group(1))
    if n <= 57:            return "herbal_A"
    elif n == 58:          return "text_f58"
    elif 67 <= n <= 73:    return "astronomical"
    elif 75 <= n <= 84:    return "biological"
    elif 87 <= n <= 102:   return "herbal_B"
    elif 103 <= n <= 116:  return "recipes_Q20"
    return "other"


def load_corpus(path=None):
    """Return list of line dicts: page, section, hand, currier, tokens.

    Lines are the unit of analysis. Callers that need a flat token list should
    say so explicitly rather than flattening by default — see `transitions`.
    """
    path = path or PARQUET_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Run scripts/00_fetch_datasets.py first.")
    df = pd.read_parquet(path)
    zl = df[df["source_name"] == "Zandbergen-Landini"].copy()
    for col in ["H", "L", "Q", "I", "X"]:
        if col in zl.columns:
            zl[col] = zl[col].fillna("?")
    lines = []
    for _, row in zl.iterrows():
        toks = parse_tokens(row["text"])
        if toks:
            lines.append({
                "page": row["page"],
                "section": get_section(row["page"]),
                "hand": row.get("H", "?"),
                "currier": row.get("L", "?"),
                "tokens": toks,
            })
    return lines


def flat_tokens(lines):
    return [t for l in lines for t in l["tokens"]]


def sequence_units(lines, boundary_type="line"):
    """Convert corpus records into immutable natural-boundary units."""
    units = []
    for i, line in enumerate(lines):
        units.append(SequenceUnit(
            unit_id=f"{line.get('page', '?')}:{i}",
            tokens=tuple(line["tokens"]),
            boundary_type=boundary_type,
            page=str(line.get("page", "")),
            section=str(line.get("section", "")),
            hand=str(line.get("hand", "")),
            currier=str(line.get("currier", "")),
        ))
    return units


def build_class_sequences(lines, policy=AmbiguityPolicy.CANONICAL_PRECEDENCE):
    """Build class sequences without manufacturing any adjacency.

    Each input line remains separate. Under ``drop_and_break_sequence``, an
    ambiguous token is removed and splits its line into two independent
    segments. Its neighbours never become adjacent.
    """
    policy = AmbiguityPolicy(policy)
    out = []
    for unit in sequence_units(lines):
        segments = [[]]
        for tok in unit.tokens:
            label = classify_with_policy(tok, policy)
            if (policy == AmbiguityPolicy.DROP_AND_BREAK_SEQUENCE
                    and label == AMBIGUOUS):
                if segments[-1]:
                    out.append(tuple(segments[-1]))
                segments = [[]]
                continue
            segments[-1].append(label)
        if segments[-1]:
            out.append(tuple(segments[-1]))
    return out


# ─── Transitions ─────────────────────────────────────────────────────────────
def transitions(lines, within_line=True, order=None, strict=False,
                ambiguity_policy=None):
    """Class transition counts.

    within_line=True  -- transitions computed inside lines only. CORRECT.
                         Finding 1.4 establishes that transition structure
                         resets at line boundaries; the canonical statistic
                         must not span them.
    within_line=False -- legacy behavior of 01_core_analysis.py, which
                         flattened tokens across lines before pairing.
                         Retained only for reproducing historical values.
    """
    tr = defaultdict(int)
    src, dst = Counter(), Counter()
    total = 0

    if ambiguity_policy is not None and (order is not None or strict):
        raise ValueError("Use ambiguity_policy or legacy order/strict, not both")

    if within_line and ambiguity_policy is not None:
        seqs = build_class_sequences(lines, ambiguity_policy)
    elif within_line:
        seqs = [classify_all(l["tokens"], order, strict) for l in lines]
    else:
        seqs = [classify_all(flat_tokens(lines), order, strict)]

    for c in seqs:
        for i in range(len(c) - 1):
            tr[(c[i], c[i + 1])] += 1
            src[c[i]] += 1
            dst[c[i + 1]] += 1
            total += 1
    return {"tr": dict(tr), "src": src, "dst": dst, "total": total}


def transition_ratio(t, source, dest):
    """Observed / expected-under-independence for one cell."""
    obs = t["tr"].get((source, dest), 0)
    if t["total"] == 0 or not t["src"][source] or not t["dst"][dest]:
        return obs, 0.0, None
    exp = t["src"][source] * (t["dst"][dest] / t["total"])
    return obs, exp, (obs / exp if exp > 1 else None)


def self_clustering(classes, min_n=10):
    """Mean observed/expected self-transition ratio across supported classes."""
    total = len(classes) - 1
    if total <= 0:
        return None
    same = Counter()
    src, dst = Counter(), Counter()
    for i in range(total):
        a, b = classes[i], classes[i + 1]
        src[a] += 1
        dst[b] += 1
        if a == b:
            same[a] += 1
    ratios = []
    for c in set(classes):
        if src[c] > min_n and dst[c] > min_n:
            exp = src[c] * (dst[c] / total)
            if exp > 1:
                ratios.append(same[c] / exp)
    return sum(ratios) / len(ratios) if ratios else None


def self_clustering_sequences(sequences, min_n=10, include_other=False,
                              included_classes=None):
    """Boundary-aware mean self-clustering over separate class sequences."""
    same, src, dst = Counter(), Counter(), Counter()
    total = 0
    for classes in sequences:
        for a, b in zip(classes, classes[1:]):
            src[a] += 1
            dst[b] += 1
            same[a] += int(a == b)
            total += 1
    if not total:
        return None
    candidates = set(src) | set(dst)
    if included_classes is not None:
        candidates &= set(included_classes)
    if not include_other:
        candidates.discard("OTHER")
    candidates.discard(AMBIGUOUS)
    ratios = []
    for label in sorted(candidates):
        if src[label] > min_n and dst[label] > min_n:
            expected = src[label] * dst[label] / total
            if expected > 1:
                ratios.append(same[label] / expected)
    return sum(ratios) / len(ratios) if ratios else None


# ─── Symmetric affix estimator ──────────────────────────────────────────────
def discover_affixes(sequences, side, n_families=5, min_len=2, max_len=3,
                     min_coverage=0.02, max_coverage=0.20,
                     candidate_pool=80):
    """Discover affix families identically on separate token sequences.

    Discovery itself does not use adjacency, but accepting sequences here
    makes the boundary-preserving representation the common interface for all
    systems. Ties are resolved lexically so results do not depend on Counter
    insertion order.
    """
    if side not in ("prefix", "suffix"):
        raise ValueError("side must be 'prefix' or 'suffix'")
    tokens = [token for sequence in sequences for token in sequence]
    if not tokens:
        return []
    counts = Counter()
    for token in tokens:
        for length in range(min_len, min(max_len, len(token)) + 1):
            affix = token[:length] if side == "prefix" else token[-length:]
            counts[affix] += 1
    candidates = sorted(counts, key=lambda value: (-counts[value], value))
    selected = []
    for affix in candidates[:candidate_pool]:
        coverage = counts[affix] / len(tokens)
        if not min_coverage <= coverage <= max_coverage:
            continue
        if any(affix.startswith(old) or old.startswith(affix)
               for old in selected):
            continue
        selected.append(affix)
        if len(selected) == n_families:
            break
    return selected


def assign_affix_sequences(sequences, affixes, side):
    """Assign tokens while retaining every input sequence boundary."""
    if side not in ("prefix", "suffix"):
        raise ValueError("side must be 'prefix' or 'suffix'")
    assigned = []
    for sequence in sequences:
        labels = []
        for token in sequence:
            label = "OTHER"
            for affix in affixes:
                matched = (token.startswith(affix) if side == "prefix"
                           else token.endswith(affix))
                if matched:
                    label = affix
                    break
            labels.append(label)
        assigned.append(tuple(labels))
    return assigned


def self_clustering_details(sequences, min_n=10, include_other=False):
    """Return the boundary-aware score and its exact class-level evidence."""
    same, src, dst = Counter(), Counter(), Counter()
    total = 0
    for classes in sequences:
        for source, destination in zip(classes, classes[1:]):
            src[source] += 1
            dst[destination] += 1
            same[source] += int(source == destination)
            total += 1
    details = {}
    ratios = []
    for label in sorted(set(src) | set(dst)):
        expected = src[label] * dst[label] / total if total else 0.0
        supported = (src[label] > min_n and dst[label] > min_n
                     and expected > 1
                     and (include_other or label != "OTHER"))
        ratio = same[label] / expected if expected else None
        details[label] = {
            "observed": same[label],
            "expected": expected,
            "source_n": src[label],
            "destination_n": dst[label],
            "ratio": ratio,
            "included_in_mean": supported,
        }
        if supported:
            ratios.append(ratio)
    return {
        "score": sum(ratios) / len(ratios) if ratios else None,
        "transition_n": total,
        "included_class_n": len(ratios),
        "classes": details,
    }


def affix_clustering_scores(sequences, include_other=False, **discovery):
    """Discover and score prefix and suffix partitions symmetrically."""
    discovery = dict(discovery)
    min_n = discovery.pop("min_n", 10)
    output = {}
    for side in ("prefix", "suffix"):
        affixes = discover_affixes(sequences, side, **discovery)
        classes = assign_affix_sequences(sequences, affixes, side)
        output[side] = {
            "affixes": affixes,
            **self_clustering_details(
                classes,
                min_n=min_n,
                include_other=include_other,
            ),
        }
    prefix = output["prefix"]["score"]
    suffix = output["suffix"]["score"]
    output["ratio"] = prefix / suffix if prefix is not None and suffix else None
    output["minimum"] = min(prefix, suffix) if None not in (prefix, suffix) else None
    return output


def affix_clustering_sensitivity_scores(sequences, **discovery):
    """Score primary and OTHER sensitivity partitions after one discovery."""
    discovery = dict(discovery)
    min_n = discovery.pop("min_n", 10)
    primary, with_other = {}, {}
    for side in ("prefix", "suffix"):
        affixes = discover_affixes(sequences, side, **discovery)
        classes = assign_affix_sequences(sequences, affixes, side)
        primary[side] = {
            "affixes": affixes,
            **self_clustering_details(classes, min_n=min_n,
                                      include_other=False),
        }
        with_other[side] = {
            "affixes": affixes,
            **self_clustering_details(classes, min_n=min_n,
                                      include_other=True),
        }
    for output in (primary, with_other):
        prefix = output["prefix"]["score"]
        suffix = output["suffix"]["score"]
        output["ratio"] = prefix / suffix if prefix is not None and suffix else None
        output["minimum"] = (min(prefix, suffix)
                             if None not in (prefix, suffix) else None)
    return {"primary_excludes_other": primary,
            "sensitivity_includes_other": with_other}


def _fragment_unit(unit, token_n, fragment_index=0):
    """Return a leading contiguous fragment as an independent sequence."""
    return SequenceUnit(
        unit_id=f"{unit.unit_id}:fragment-{fragment_index}",
        tokens=tuple(unit.tokens[:token_n]),
        boundary_type=f"{unit.boundary_type}_fragment",
        page=unit.page,
        section=unit.section,
        hand=unit.hand,
        currier=unit.currier,
        document=unit.document,
    )


def sample_units_to_target(units, target_tokens, rng):
    """Sample natural units without replacement to an exact token target."""
    available = sum(len(unit.tokens) for unit in units)
    if available < target_tokens:
        raise ValueError(
            f"corpus has {available} tokens, below target {target_tokens}")
    order = rng.permutation(len(units))
    selected = []
    remaining = target_tokens
    for position in order:
        unit = units[int(position)]
        if len(unit.tokens) <= remaining:
            selected.append(unit)
            remaining -= len(unit.tokens)
        else:
            start = int(rng.integers(0, len(unit.tokens) - remaining + 1))
            fragment = SequenceUnit(
                unit_id=f"{unit.unit_id}:fragment-{start}",
                tokens=tuple(unit.tokens[start:start + remaining]),
                boundary_type=f"{unit.boundary_type}_fragment",
                page=unit.page,
                section=unit.section,
                hand=unit.hand,
                currier=unit.currier,
                document=unit.document,
            )
            selected.append(fragment)
            remaining = 0
        if remaining == 0:
            break
    return selected


def bootstrap_groups_to_target(units, group_attribute, target_tokens, rng):
    """Block-bootstrap groups while preserving all nested sequence units."""
    groups = defaultdict(list)
    for unit in units:
        key = getattr(unit, group_attribute)
        if not key:
            raise ValueError(f"unit {unit.unit_id} lacks {group_attribute}")
        groups[key].append(unit)
    keys = sorted(groups)
    if not keys:
        raise ValueError("no resampling groups")
    selected = []
    remaining = target_tokens
    draw = 0
    while remaining:
        key = keys[int(rng.integers(0, len(keys)))]
        for unit in groups[key]:
            copy = SequenceUnit(
                unit_id=f"draw-{draw}:{unit.unit_id}",
                tokens=unit.tokens,
                boundary_type=unit.boundary_type,
                page=unit.page,
                section=unit.section,
                hand=unit.hand,
                currier=unit.currier,
                document=unit.document,
            )
            if len(copy.tokens) <= remaining:
                selected.append(copy)
                remaining -= len(copy.tokens)
            else:
                selected.append(_fragment_unit(copy, remaining, draw))
                remaining = 0
            if not remaining:
                break
        draw += 1
    return selected


# ─── Diagnostics ─────────────────────────────────────────────────────────────
def overlap_report(tokens):
    combos = Counter()
    types = Counter()
    for t in tokens:
        hits = matching_families(t)
        if len(hits) > 1:
            combos[hits] += 1
            types[t] += 1
    return {
        "instances": sum(combos.values()),
        "pct_of_corpus": 100 * sum(combos.values()) / len(tokens) if tokens else 0,
        "n_types": len(types),
        "combinations": {" + ".join(k): v for k, v in sorted(combos.items())},
        "top_types": types.most_common(10),
        "types": dict(sorted(types.items())),
    }


def classifier_disagreement_report(tokens):
    """Exact disagreement counts for the two historical precedence orders."""
    differing = Counter()
    for tok in tokens:
        a = classify(tok, order=ORDER_PREFIX_FIRST)
        b = classify(tok, order=ORDER_SUBSTRING_FIRST)
        if a != b:
            differing[tok] += 1
    n = sum(differing.values())
    return {
        "instances": n,
        "pct_of_corpus": 100 * n / len(tokens) if tokens else 0,
        "n_types": len(differing),
        "types": dict(sorted(differing.items())),
    }


def sample_two_disjoint_contiguous_blocks(items, n1, n2, rng):
    """Sample two disjoint blocks, both contiguous in the original ordering.

    The historical implementation removed block one and sampled block two
    from the concatenated remainder. That allowed block two to cross the
    removal seam. Enumerating valid start pairs makes that impossible.
    """
    if n1 <= 0 or n2 <= 0 or len(items) < n1 + n2:
        return None, None
    starts = []
    for i in range(len(items) - n1 + 1):
        a = set(range(i, i + n1))
        for j in range(len(items) - n2 + 1):
            if a.isdisjoint(range(j, j + n2)):
                starts.append((i, j))
    if not starts:
        return None, None
    i, j = starts[int(rng.integers(0, len(starts)))]
    return items[i:i + n1], items[j:j + n2]


def _main():
    lines = load_corpus()
    toks = flat_tokens(lines)
    print("=" * 72)
    print("CANONICAL CLASSIFIER — DIAGNOSTIC REPORT")
    print("=" * 72)
    print(f"Corpus: {len(lines)} lines, {len(toks)} tokens, "
          f"{len(set(l['page'] for l in lines))} pages")

    ov = overlap_report(toks)
    print(f"\nMulti-family tokens: {ov['instances']} instances "
          f"({ov['pct_of_corpus']:.2f}% of corpus), {ov['n_types']} types")
    for combo, n in sorted(ov["combinations"].items(),
                           key=lambda item: (-item[1], item[0])):
        print(f"  {combo:<22} {n}")

    print("\nHeadline statistics under each policy:")
    print(f"{'policy':<34}{'CHEDY→QOK':>12}{'AIIN→QOK':>12}")
    print("-" * 58)
    for label, order, wl in [
        ("prefix-first,  flattened", ORDER_PREFIX_FIRST, False),
        ("prefix-first,  within-line", ORDER_PREFIX_FIRST, True),
        ("substring-first, flattened", ORDER_SUBSTRING_FIRST, False),
        ("substring-first, within-line", ORDER_SUBSTRING_FIRST, True),
    ]:
        t = transitions(lines, within_line=wl, order=order)
        _, _, cq = transition_ratio(t, "CHEDY", "QOK")
        _, _, aq = transition_ratio(t, "AIIN", "QOK")
        print(f"{label:<34}{cq:>11.3f}x{aq:>11.3f}x")

    t = transitions(lines, within_line=True,
                    ambiguity_policy=AmbiguityPolicy.DROP_AND_BREAK_SEQUENCE)
    _, _, cq = transition_ratio(t, "CHEDY", "QOK")
    print(f"{'strict (ambiguous excluded)':<34}{cq:>11.3f}x")

    print("\nRecommended canonical: prefix-first, within-line.")
    print("Report the strict figure alongside it as a robustness check.")


if __name__ == "__main__":
    _main()
