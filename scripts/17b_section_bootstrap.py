import sys, numpy as np, json
sys.path.insert(0, '/home/claude/repo/scripts')
from _canonical import load_corpus, classify
from collections import Counter, defaultdict

rng = np.random.default_rng(42)
lines = load_corpus()
for l in lines:
    l['fam'] = [classify(t) for t in l['tokens']]

def strat(sec=None, cur=None):
    return [l for l in lines
            if (not sec or l['section'] == sec)
            and (not cur or str(l['currier'])[:1] == cur)]

CELLS = [("CHEDY", "QOK"), ("AIIN", "QOK"), ("QOK", "QOK")]

def ratios(ls):
    tr = defaultdict(int); src = Counter(); dst = Counter(); tot = 0
    for l in ls:
        c = l['fam']
        for i in range(len(c) - 1):
            tr[(c[i], c[i+1])] += 1; src[c[i]] += 1; dst[c[i+1]] += 1; tot += 1
    out = {}
    for s, d in CELLS:
        e = src[s] * (dst[d] / tot) if tot and src[s] and dst[d] else 0
        out[(s, d)] = tr[(s, d)] / e if e > 1 else None
    return out

def bootdiff(A, B, n=120):
    acc = {c: [] for c in CELLS}
    for _ in range(n):
        ra = ratios([A[i] for i in rng.integers(0, len(A), len(A))])
        rb = ratios([B[i] for i in rng.integers(0, len(B), len(B))])
        for c in CELLS:
            if ra[c] and rb[c]:
                acc[c].append(ra[c] - rb[c])
    return {c: (float(np.mean(v)), float(np.percentile(v, 2.5)),
                float(np.percentile(v, 97.5)))
            for c, v in acc.items() if len(v) > 30}

S = {"herbal_A/B": strat("herbal_A", "B"),
     "biological/B": strat("biological", "B"),
     "recipes_Q20/B": strat("recipes_Q20", "B"),
     "herbal_A/A": strat("herbal_A", "A")}

comps = [("SECTION", "herbal_A/B", "biological/B"),
         ("SECTION", "herbal_A/B", "recipes_Q20/B"),
         ("SECTION", "biological/B", "recipes_Q20/B"),
         ("LANGUAGE", "herbal_A/A", "herbal_A/B")]

rows = []
print(f"{'contrast':<10}{'comparison':<32}{'cell':<14}{'diff':>8}{'95% CI':>20}{'!=0':>5}", flush=True)
for kind, na, nb in comps:
    r = bootdiff(S[na], S[nb])
    for c, (m, lo, hi) in r.items():
        ex = lo > 0 or hi < 0
        rows.append({"contrast": kind, "a": na, "b": nb,
                     "cell": f"{c[0]}->{c[1]}", "mean_diff": round(m, 3),
                     "ci95": [round(lo, 3), round(hi, 3)],
                     "excludes_zero": bool(ex)})
        ci = f"[{lo:+.2f}, {hi:+.2f}]"
        print(f"{kind:<10}{na+' vs '+nb:<32}{c[0]+'→'+c[1]:<14}{m:>+8.2f}{ci:>20}{'Y' if ex else 'n':>5}", flush=True)

ns = sum(1 for r in rows if r['contrast'] == 'SECTION' and r['excludes_zero'])
nst = sum(1 for r in rows if r['contrast'] == 'SECTION')
nl = sum(1 for r in rows if r['contrast'] == 'LANGUAGE' and r['excludes_zero'])
nlt = sum(1 for r in rows if r['contrast'] == 'LANGUAGE')
print(f"\nSECTION contrasts excluding zero:  {ns}/{nst}")
print(f"LANGUAGE contrasts excluding zero: {nl}/{nlt}")
json.dump({"rows": rows, "section": [ns, nst], "language": [nl, nlt]},
          open('/home/claude/repo/results/section_bootstrap.json', 'w'), indent=2)
print("SAVED")
