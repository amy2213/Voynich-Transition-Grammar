#!/usr/bin/env python3
"""
Cross-Linguistic Comparison — uses ONLY local frozen datasets.

Verified comparators (12):
  Voynich, Middle English, KJV English, Turkish, Hungarian, Finnish,
  Hebrew, Arabic, Latin (proxy), N. Azerbaijani, Italian (proxy), Estonian

Pending (3): Uzbek, Kazakh, Mongolian
Controls (1): Gibberish (shuffled Voynich)

NOT included: Old French, Medieval Italian, Latin (Caesar literary)

Run from project root: python scripts/02_cross_linguistic.py
Requires: pip install pandas pyarrow scipy numpy
"""
import os, re, json, tarfile, numpy as np, pandas as pd
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency

np.random.seed(42)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

def is_aiin(tok): return "aiin" in tok or "ain" in tok
def is_qok(tok): return tok.startswith("qok")
def is_ok(tok): return tok.startswith("ok") and not tok.startswith("qok")
def is_ot(tok): return tok.startswith("ot")
def is_chedy(tok): return any(p in tok for p in ["chedy","shedy","chey","shey"])

def classify_voynich(tok):
    if is_aiin(tok): return "FUNC"
    if is_qok(tok): return "QOK"
    if is_ok(tok): return "OK"
    if is_ot(tok): return "OT"
    if is_chedy(tok): return "CHEDY"
    return "OTHER"

def get_top_families(words, n=5):
    pc = Counter()
    for w in words:
        for plen in range(2, min(4,len(w)+1)):
            pc[w[:plen]] += 1
    fams = {}; used = set()
    for prefix, _ in pc.most_common(80):
        m = [w for w in words if w.startswith(prefix) and w not in used]
        cov = len(m)/len(words) if words else 0
        if cov<0.02 or cov>0.20: continue
        if any(prefix.startswith(e) or e.startswith(prefix) for e in fams): continue
        fams[prefix] = cov
        for w in m: used.add(w)
        if len(fams)>=n: break
    return fams

def compute_metrics(words, func_words, label):
    nf = [w for w in words if w not in func_words]
    fams = get_top_families(nf, 5)
    fn = list(fams.keys())
    def cl(w):
        if w in func_words: return "FUNC"
        for p in fn:
            if w.startswith(p): return p.upper()[:6]
        return "OTHER"
    classes = [cl(w) for w in words]
    ac = list(set(classes))
    tr = defaultdict(lambda: defaultdict(int))
    sc = defaultdict(int); dc = defaultdict(int); total = len(classes)-1
    for i in range(total):
        tr[classes[i]][classes[i+1]] += 1; sc[classes[i]] += 1; dc[classes[i+1]] += 1
    if total==0: return None
    df = {c: dc[c]/total for c in ac}
    om = np.array([[tr[s][d] for d in ac] for s in ac])
    rs=om.sum(1);cs=om.sum(0);v=(rs>0)&(cs>0)
    c2=0
    if v.sum()>=2:
        try: c2v,_,_,_=chi2_contingency(om[np.ix_(v,v)]); c2=c2v/(v.sum()**2)
        except: pass
    vc=[c for c in ac if sc[c]>10 and dc[c]>10]
    asym=[]
    for i,s in enumerate(vc):
        for j,d in enumerate(vc):
            if j<=i: continue
            es=sc[s]*df.get(d,0);ed=sc[d]*df.get(s,0)
            ra=tr[s][d]/es if es>1 else None; rb=tr[d][s]/ed if ed>1 else None
            if ra and rb: asym.append(abs(ra-rb))
    ar=[tr[s][d]/(sc[s]*df.get(d,0)) for s in vc for d in vc if sc[s]*df.get(d,0)>1]
    scl=[tr[c][c]/(sc[c]*df.get(c,0)) for c in vc if sc[c]*df.get(c,0)>1]
    carry=[]
    for f in vc:
        if f=="FUNC": continue
        cr=0;tf=0
        for i in range(1,len(classes)-1):
            if classes[i]=="FUNC" and classes[i-1]==f:
                tf+=1
                if classes[i+1]==f: cr+=1
        if tf>=5:
            b=dc[f]/total
            carry.append((cr/tf)/b if b>0 else 0)
    fd=[]
    for st in range(0,len(words)-50,50):
        pg=words[st:st+50]
        fd.append(sum(1 for w in pg if w in func_words)/50)
    return {"label":label,"total_words":len(words),
            "func_density":round(np.mean(fd)*100,1) if fd else 0,
            "func_cv":round(np.std(fd)/np.mean(fd),3) if fd and np.mean(fd)>0 else 0,
            "chi2_per_cell":round(c2,1),
            "mean_asymmetry":round(np.mean(asym),3) if asym else 0,
            "max_attraction":round(max(ar),2) if ar else 1,
            "max_repulsion":round(min(ar),2) if ar else 1,
            "mean_self_cluster":round(np.mean(scl),3) if scl else 1.0,
            "mean_carry_through":round(np.mean(carry),2) if carry else 1.0}

def compute_voynich_metrics(words, label):
    classes=[classify_voynich(w) for w in words]
    ac=list(set(classes))
    tr=defaultdict(lambda:defaultdict(int))
    sc=defaultdict(int);dc=defaultdict(int);total=len(classes)-1
    for i in range(total):
        tr[classes[i]][classes[i+1]]+=1;sc[classes[i]]+=1;dc[classes[i+1]]+=1
    if total==0: return None
    df={c:dc[c]/total for c in ac}
    vc=[c for c in ac if sc[c]>10 and dc[c]>10]
    om=np.array([[tr[s][d] for d in ac] for s in ac])
    rs=om.sum(1);cs=om.sum(0);v=(rs>0)&(cs>0)
    c2=0
    if v.sum()>=2:
        try: c2v,_,_,_=chi2_contingency(om[np.ix_(v,v)]);c2=c2v/(v.sum()**2)
        except: pass
    asym=[abs((tr[s][d]/(sc[s]*df[d]) if sc[s]*df[d]>1 else 1)-(tr[d][s]/(sc[d]*df[s]) if sc[d]*df[s]>1 else 1))
          for i,s in enumerate(vc) for j,d in enumerate(vc) if j>i and sc[s]*df.get(d,0)>1 and sc[d]*df.get(s,0)>1]
    ar=[tr[s][d]/(sc[s]*df[d]) for s in vc for d in vc if sc[s]*df.get(d,0)>1]
    scl=[tr[c][c]/(sc[c]*df[c]) for c in vc if sc[c]*df.get(c,0)>1]
    carry=[]
    for f in vc:
        if f=="FUNC": continue
        cr=0;tf=0
        for i in range(1,len(classes)-1):
            if classes[i]=="FUNC" and classes[i-1]==f:
                tf+=1
                if classes[i+1]==f: cr+=1
        if tf>=5:
            b=dc[f]/total;carry.append((cr/tf)/b if b>0 else 0)
    fd=[]
    for st in range(0,len(words)-50,50):
        pg=words[st:st+50]
        fd.append(sum(1 for w in pg if is_aiin(w))/50)
    return {"label":label,"total_words":len(words),
            "func_density":round(np.mean(fd)*100,1) if fd else 0,
            "func_cv":round(np.std(fd)/np.mean(fd),3) if fd and np.mean(fd)>0 else 0,
            "chi2_per_cell":round(c2,1),
            "mean_asymmetry":round(np.mean(asym),3) if asym else 0,
            "max_attraction":round(max(ar),2) if ar else 1,
            "max_repulsion":round(min(ar),2) if ar else 1,
            "mean_self_cluster":round(np.mean(scl),3) if scl else 1.0,
            "mean_carry_through":round(np.mean(carry),2) if carry else 1.0}

def load_leipzig(folder,tarball,regex):
    tp=os.path.join(DATA_DIR,"cross_linguistic",folder,tarball)
    if not os.path.exists(tp): return None
    try:
        with tarfile.open(tp,"r:gz") as tar:
            for m in tar.getmembers():
                if "sentences" in m.name:
                    f=tar.extractfile(m)
                    if f:
                        lr=f.read().decode("utf-8",errors="ignore").splitlines()
                        texts=[l.split("\t",1)[1].strip() if "\t" in l else l.strip() for l in lr]
                        return [w for w in re.findall(regex," ".join(texts).lower()) if len(w)>=2]
    except Exception as e: print(f"  Error: {e}")
    return None

def load_gutenberg(folder,fname,regex):
    fp=os.path.join(DATA_DIR,"cross_linguistic",folder,fname)
    if not os.path.exists(fp): return None
    with open(fp,"r",encoding="utf-8",errors="ignore") as f: text=f.read()
    s=text.find("*** START");
    if s>-1: text=text[text.find("\n",s)+1:]
    e=text.find("*** END");
    if e>-1: text=text[:e]
    return [w for w in re.findall(regex,text.lower()) if len(w)>=2]

def main():
    print("="*70)
    print("CROSS-LINGUISTIC COMPARISON (local frozen datasets)")
    print("="*70)
    
    # Voynich
    vp=os.path.join(DATA_DIR,"voynich","AncientLanguages_Voynich_snapshot","train.parquet")
    if not os.path.exists(vp):
        print("ERROR: Run scripts/00_fetch_datasets.py first"); return
    d=pd.read_parquet(vp)
    zl=d[d["source_name"]=="Zandbergen-Landini"]
    vt=[]
    for _,r in zl.iterrows():
        t=r["text"] if isinstance(r["text"],str) else ""
        vt.extend([tk for tk in t.strip().split() if not tk.startswith("%") and not tk.startswith("{") and tk not in ["-","=","!"]])
    print(f"\n  Voynich: {len(vt)} tokens")
    
    R={}
    R["VOYNICH"]=compute_voynich_metrics(vt,"VOYNICH")
    g=vt.copy();np.random.shuffle(g)
    R["GIBBERISH"]=compute_voynich_metrics(g,"GIBBERISH (shuffled)")
    
    # Gutenberg
    print("\nGutenberg texts:")
    for fo,fn,rx,fw,lb in [
        ("middle_english","chaucer_canterbury_tales_22120.txt",r"[a-z]+",
         {"and","the","that","for","with","his","was","but","not","her","she","they","this","hath","than"},"Middle English (Chaucer)"),
        ("kjv_english","king_james_bible_10900.txt",r"[a-z]+",
         {"and","the","of","to","in","that","he","for","it","with","his","was","not","but","be","they","have","him"},"KJV English"),
    ]:
        w=load_gutenberg(fo,fn,rx)
        if w and len(w)>1000:
            r=compute_metrics(w,fw,lb)
            if r: R[lb]=r; print(f"  {lb}: {len(w)} words, SC={r['mean_self_cluster']:.3f}x")
        else: print(f"  {lb}: NOT FOUND")
    
    # Leipzig verified
    print("\nLeipzig verified:")
    for fo,tb,rx,fw,lb in [
        ("turkish","tur_wikipedia_2021_100K.tar.gz",r"[a-zçğıöşüâîû]+",{"ve","bir","bu","için","olan","ile","da","de","olarak","gibi","sonra","ise","çok","daha","en","var"},"Turkish"),
        ("hungarian","hun_wikipedia_2021_100K.tar.gz",r"[a-záéíóöőúüű]+",{"és","az","nem","egy","is","meg","hogy","volt","csak","már","mint","még","sem","van"},"Hungarian"),
        ("finnish","fin_wikipedia_2021_100K.tar.gz",r"[a-zäöå]+",{"ja","on","ei","se","en","oli","hän","kun","niin","jo","ne","tai","sen","vaan","mutta","ovat","kuin","että"},"Finnish"),
        ("hebrew","heb_wikipedia_2021_100K.tar.gz",r"[^\s\d.,;:!?()«»\[\]{}<>\"']+",set(),"Hebrew"),
        ("arabic","ara_wikipedia_2021_100K.tar.gz",r"[^\s\d.,;:!?()«»\[\]{}<>\"']+",set(),"Arabic"),
        ("latin","lat_wikipedia_2021_100K.tar.gz",r"[a-z]+",{"et","in","est","non","qui","quod","ad","cum","ab","de","ex","per","ut","sed","si","atque","neque"},"Latin (proxy)"),
        ("north_azerbaijani","aze_wikipedia_2021_100K.tar.gz",r"[a-zçəğıöşü]+",{"və","bir","bu","ilə","olan","da","də","üçün","kimi","daha","çox","var"},"N. Azerbaijani"),
        ("italian","ita_wikipedia_2021_100K.tar.gz",r"[a-zàáâãäåæçèéêëìíîïòóôõöùúûüý]+",{"e","di","che","in","la","il","le","lo","un","una","per","con","non","si","da","ma","del","al","nel"},"Italian (proxy)"),
        ("estonian","ekk_wikipedia_2021_100K.tar.gz",r"[a-zõäöüšž]+",{"ja","on","ei","see","oli","kui","mis","oma","üks","veel","ka","aga","ning","siis","nii"},"Estonian"),
    ]:
        w=load_leipzig(fo,tb,rx)
        if w and len(w)>1000:
            if not fw:
                wc=Counter(w);fw=set(ww for ww,c in wc.most_common(100) if len(ww)<=4 and c>20)
            r=compute_metrics(w,fw,lb)
            if r: R[lb]=r; print(f"  {lb}: {len(w)} words, SC={r['mean_self_cluster']:.3f}x")
        else: print(f"  {lb}: NOT FOUND")
    
    # Pending
    print("\nPending (unverified):")
    for fo,tb,rx,fw,lb in [
        ("uzbek_pending","uzb_wikipedia_2021_100K.tar.gz",r"[a-z]+",{"va","bir","bu","bilan","uchun","ham","yoki"},"Uzbek (PENDING)"),
        ("kazakh_pending","kaz_wikipedia_2021_100K.tar.gz",r"[^\s\d.,;:!?()«»\[\]{}<>\"']+",set(),"Kazakh (PENDING)"),
        ("mongolian_pending","mon_wikipedia_2021_100K.tar.gz",r"[^\s\d.,;:!?()«»\[\]{}<>\"']+",set(),"Mongolian (PENDING)"),
    ]:
        w=load_leipzig(fo,tb,rx)
        if w and len(w)>1000:
            if not fw:
                wc=Counter(w);fw=set(ww for ww,c in wc.most_common(100) if len(ww)<=4 and c>20)
            r=compute_metrics(w,fw,lb)
            if r: r["verification_status"]="pending"; R[lb]=r; print(f"  {lb}: {len(w)} words [UNVERIFIED]")
        else: print(f"  {lb}: not available")
    
    # Table
    vcount=sum(1 for r in R.values() if r.get("verification_status")!="pending" and "GIBBERISH" not in r["label"])
    pcount=sum(1 for r in R.values() if r.get("verification_status")=="pending")
    print(f"\n{'='*90}")
    print(f"{'System':<30} {'Words':>7} {'SC':>6} {'Asym':>6} {'Chi2':>6} {'Carry':>6} {'MxAtt':>7}")
    print(f"{'-'*90}")
    for k in sorted(R.keys(),key=lambda k:R[k]["mean_self_cluster"],reverse=True):
        r=R[k];p=" *" if r.get("verification_status")=="pending" else ""
        print(f"{r['label']:<30} {r['total_words']:>7} {r['mean_self_cluster']:>5.2f}x {r['mean_asymmetry']:>5.3f} {r['chi2_per_cell']:>5.1f} {r['mean_carry_through']:>5.2f}x {r['max_attraction']:>6.2f}x{p}")
    print(f"\nVerified: {vcount}, Pending: {pcount}, Controls: 1")
    
    os.makedirs(RESULTS_DIR,exist_ok=True)
    with open(os.path.join(RESULTS_DIR,"cross_linguistic_results.json"),"w") as f:
        json.dump(R,f,indent=2,default=str)
    print(f"Saved to results/cross_linguistic_results.json")

if __name__=="__main__": main()
