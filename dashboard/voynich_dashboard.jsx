import { useState, useEffect, useMemo } from "react";

const FINDINGS = {
  transitionRules: {
    title: "Transition Rules",
    subtitle: "Two hard sequential constraints survive every test",
    data: [
      { rule: "CHEDY → QOK", ratio: 2.625, type: "attraction", obs: 626, exp: 238, ci: [2.34, 2.67], pages: "78%", pVal: "<0.001" },
      { rule: "AIIN → QOK", ratio: 0.504, type: "repulsion", obs: 160, exp: 317, ci: [0.39, 0.53], pages: "67%", pVal: "<0.001" },
      { rule: "QOK → AIIN", ratio: 0.86, type: "repulsion", obs: 290, exp: 339, ci: null, pages: null, pVal: "0.001" },
      { rule: "AIIN → OK", ratio: 1.18, type: "attraction", obs: 276, exp: 234, ci: null, pages: null, pVal: "0.006" },
      { rule: "AIIN → OT", ratio: 1.30, type: "attraction", obs: 298, exp: 229, ci: null, pages: null, pVal: "<0.001" },
      { rule: "OT → OT", ratio: 1.85, type: "attraction", obs: 136, exp: 73, ci: null, pages: null, pVal: "<0.001" },
    ]
  },
  familyDensities: {
    title: "Family Densities by Section",
    sections: [
      { name: "Herbal A", qok: 3.6, ok: 4.2, ot: 3.6, chedy: 4.1, aiin: 14.9, other: 69.6, tokens: 9893, hand: "1", currier: "A" },
      { name: "Biological", qok: 11.9, ok: 3.9, ot: 3.8, chedy: 16.5, aiin: 13.0, other: 50.9, tokens: 6898, hand: "2", currier: "B" },
      { name: "Recipes Q20", qok: 7.8, ok: 5.2, ot: 5.9, chedy: 9.2, aiin: 18.6, other: 53.2, tokens: 10892, hand: "3", currier: "B" },
      { name: "Herbal B", qok: 5.7, ok: 6.8, ot: 4.2, chedy: 2.6, aiin: 10.8, other: 70.0, tokens: 1984, hand: "1", currier: "A" },
      { name: "Astronomical", qok: 0.7, ok: 13.4, ot: 16.8, chedy: 4.5, aiin: 5.5, other: 59.0, tokens: 685, hand: "4", currier: "?" },
    ]
  },
  crossLinguistic: {
    title: "Cross-Linguistic Comparison",
    languages: [
      { name: "Arabic", type: "Semitic", sc: 1.92, sfx: 2.662, ratio: 0.72, bucket: "SUFFIX-DOM" },
      { name: "VOYNICH", type: "Unknown", sc: 1.524, sfx: 1.544, ratio: 0.99, bucket: "SYMM-HIGH", highlight: true },
      { name: "Estonian", type: "Uralic", sc: 0.962, sfx: 2.328, ratio: 0.41, bucket: "SUFFIX-DOM" },
      { name: "Finnish", type: "Uralic", sc: 1.006, sfx: 1.511, ratio: 0.67, bucket: "SUFFIX-DOM" },
      { name: "Hungarian", type: "Uralic", sc: 0.944, sfx: 1.169, ratio: 0.81, bucket: "SUFFIX-DOM" },
      { name: "Turkish", type: "Turkic", sc: 0.906, sfx: 0.98, ratio: 0.92, bucket: "SYMM-LOW" },
      { name: "Latin", type: "IE", sc: 1.105, sfx: 2.925, ratio: 0.38, bucket: "SUFFIX-DOM" },
      { name: "N. Azerbaijani", type: "Turkic", sc: 0.815, sfx: 0.795, ratio: 1.02, bucket: "SYMM-LOW" },
      { name: "Italian", type: "IE", sc: 0.685, sfx: 0.964, ratio: 0.71, bucket: "SYMM-LOW" },
      { name: "Hebrew", type: "Semitic", sc: 0.713, sfx: 2.474, ratio: 0.29, bucket: "SUFFIX-DOM" },
      { name: "KJV English", type: "IE", sc: 0.551, sfx: 0.704, ratio: 0.78, bucket: "SYMM-LOW" },
      { name: "Middle English", type: "IE", sc: 0.411, sfx: 0.692, ratio: 0.59, bucket: "SYMM-LOW" },
      { name: "Gibberish", type: "Control", sc: 0.923, sfx: 0.966, ratio: 0.96, bucket: "SYMM-LOW", control: true }
    ]
  },
  carryThrough: {
    title: "Carry-Through: AIIN as Transparent Connector",
    data: [
      { family: "OT", ratio: 2.21, description: "STRONGEST — OT passes through AIIN" },
      { family: "CHEDY", ratio: 1.64, description: "Strong carry-through" },
      { family: "OK", ratio: 2.73, description: "Moderate carry-through" },
      { family: "QOK", ratio: 0.83, description: "BLOCKED — QOK cannot pass through AIIN" },
    ]
  },
  tokenLevel: {
    title: "Token-Level Grammar Test",
    chedyAttract: { total: 69, attracting: 54, pct: 78 },
    qokAttracted: { total: 47, attracted: 35, pct: 74 },
    aiinRepel: { total: 52, repelling: 36, pct: 69 },
    topPairsCoverage: 13.3,
    uniquePairs: 369,
    verdict: "DISTRIBUTED — grammatical rule, not fixed phrases"
  }
};

const COLORS = {
  bg: "#0a0e17",
  surface: "#111827",
  surfaceLight: "#1a2235",
  border: "#2a3a52",
  accent: "#c4a35a",
  accentDim: "#8b7340",
  text: "#e8e0d4",
  textDim: "#8899aa",
  attract: "#4ade80",
  repel: "#f87171",
  neutral: "#60a5fa",
  qok: "#f59e0b",
  ok: "#3b82f6",
  ot: "#8b5cf6",
  chedy: "#ec4899",
  aiin: "#10b981",
  other: "#6b7280",
  voynich: "#c4a35a",
};

const FAMILY_COLORS = { QOK: COLORS.qok, OK: COLORS.ok, OT: COLORS.ot, CHEDY: COLORS.chedy, AIIN: COLORS.aiin, OTHER: COLORS.other };

function Bar({ value, max, color, label, width = "100%" }) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div style={{ width, marginBottom: 4 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: COLORS.textDim, marginBottom: 2 }}>
        <span>{label}</span><span style={{ color }}>{value.toFixed(1)}%</span>
      </div>
      <div style={{ height: 6, background: COLORS.border, borderRadius: 3 }}>
        <div style={{ height: "100%", width: `${pct}%`, background: color, borderRadius: 3, transition: "width 0.8s ease" }} />
      </div>
    </div>
  );
}

function RatioBar({ ratio, label, maxRatio = 3.5 }) {
  const isAttract = ratio > 1;
  const color = ratio > 1.3 ? COLORS.attract : ratio < 0.7 ? COLORS.repel : COLORS.neutral;
  const center = 50;
  const extent = Math.min(Math.abs(ratio - 1) / (maxRatio - 1) * 50, 50);
  const left = isAttract ? center : center - extent;
  const width = extent;

  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 3 }}>
        <span style={{ color: COLORS.text, fontFamily: "'IBM Plex Mono', monospace" }}>{label}</span>
        <span style={{ color, fontWeight: 700 }}>{ratio.toFixed(2)}x</span>
      </div>
      <div style={{ height: 8, background: COLORS.border, borderRadius: 4, position: "relative" }}>
        <div style={{ position: "absolute", left: "50%", top: 0, bottom: 0, width: 1, background: COLORS.textDim, opacity: 0.4 }} />
        <div style={{ position: "absolute", left: `${left}%`, width: `${width}%`, top: 0, bottom: 0, background: color, borderRadius: 4, transition: "all 0.8s ease" }} />
      </div>
    </div>
  );
}

function Card({ children, style = {} }) {
  return (
    <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 8, padding: 24, ...style }}>
      {children}
    </div>
  );
}

function SectionTitle({ children, sub }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <h2 style={{ margin: 0, fontSize: 20, color: COLORS.accent, fontFamily: "'Playfair Display', serif", letterSpacing: 0.5 }}>{children}</h2>
      {sub && <p style={{ margin: "4px 0 0", fontSize: 13, color: COLORS.textDim }}>{sub}</p>}
    </div>
  );
}

function TransitionMatrix() {
  const families = ["QOK", "OK", "OT", "CHEDY", "AIIN", "OTHER"];
  const matrix = {
    QOK: [1.55, 1.28, 1.05, 1.45, 0.69, 0.87],
    OK: [1.11, 1.54, 1.20, 1.08, 0.82, 0.93],
    OT: [0.81, 1.10, 1.93, 0.95, 0.85, 0.96],
    CHEDY: [2.66, 0.82, 0.82, 1.12, 0.78, 0.80],
    AIIN: [0.44, 1.37, 1.35, 1.01, 0.89, 1.03],
    OTHER: [0.77, 0.85, 0.84, 0.90, 1.14, 1.06],
  };

  function cellColor(val) {
    if (val >= 2.0) return "#166534";
    if (val >= 1.3) return "#14532d88";
    if (val <= 0.5) return "#991b1b";
    if (val <= 0.7) return "#7f1d1d88";
    return "transparent";
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 12 }}>
        <thead>
          <tr>
            <th style={{ padding: 6, color: COLORS.textDim, textAlign: "left", borderBottom: `1px solid ${COLORS.border}` }}>FROM ↓ TO →</th>
            {families.map(f => <th key={f} style={{ padding: 6, color: FAMILY_COLORS[f], textAlign: "center", borderBottom: `1px solid ${COLORS.border}`, fontFamily: "'IBM Plex Mono', monospace" }}>{f}</th>)}
          </tr>
        </thead>
        <tbody>
          {families.map(src => (
            <tr key={src}>
              <td style={{ padding: 6, color: FAMILY_COLORS[src], fontWeight: 700, fontFamily: "'IBM Plex Mono', monospace", borderBottom: `1px solid ${COLORS.border}22` }}>{src}</td>
              {matrix[src].map((val, j) => (
                <td key={j} style={{ padding: 6, textAlign: "center", background: cellColor(val), color: COLORS.text, borderBottom: `1px solid ${COLORS.border}22`, fontFamily: "'IBM Plex Mono', monospace" }}>
                  {val.toFixed(2)}x
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const TABS = ["Overview", "Transition Rules", "AIIN Invariance", "Self-Clustering", "Cross-Linguistic", "Token Grammar", "Methodology"];

export default function VoynichDashboard() {
  const [tab, setTab] = useState(0);
  const [loaded, setLoaded] = useState(false);
  useEffect(() => { setLoaded(true); }, []);

  return (
    <div style={{ minHeight: "100vh", background: COLORS.bg, color: COLORS.text, fontFamily: "'Source Sans 3', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+3:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{ borderBottom: `1px solid ${COLORS.border}`, padding: "32px 24px 24px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
            <h1 style={{ margin: 0, fontSize: 28, fontFamily: "'Playfair Display', serif", color: COLORS.accent, letterSpacing: 1 }}>
              Voynich Manuscript
            </h1>
            <span style={{ fontSize: 14, color: COLORS.textDim, fontWeight: 300 }}>Transition Grammar Analysis</span>
          </div>
          <p style={{ margin: "8px 0 0", fontSize: 13, color: COLORS.textDim, maxWidth: 700 }}>
            Quantitative analysis of sequential token-family constraints across 11 natural-language comparators. 
            Cross-validated against independent AI analysis. April 2026.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ borderBottom: `1px solid ${COLORS.border}`, padding: "0 24px", overflowX: "auto" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", display: "flex", gap: 0 }}>
          {TABS.map((t, i) => (
            <button key={i} onClick={() => setTab(i)} style={{
              padding: "12px 16px", border: "none", cursor: "pointer", fontSize: 13, fontWeight: tab === i ? 600 : 400,
              color: tab === i ? COLORS.accent : COLORS.textDim, background: "transparent",
              borderBottom: tab === i ? `2px solid ${COLORS.accent}` : "2px solid transparent",
              transition: "all 0.2s", whiteSpace: "nowrap", fontFamily: "'Source Sans 3', sans-serif"
            }}>{t}</button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 24px 60px", opacity: loaded ? 1 : 0, transition: "opacity 0.5s" }}>

        {tab === 0 && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16 }}>
            <Card>
              <SectionTitle sub="Verified findings">Core Findings</SectionTitle>
              {[
                { label: "Non-random sequential structure", detail: "Chi² = 1407.8, p ≈ 0. Significantly non-random." },
                { label: "AIIN at 15% across Currier A/B", detail: "KS p = 0.742. Language-invariant." },
                { label: "CHEDY→QOK = 2.625x attraction", detail: "Split-half 95% range: [2.34x, 2.67x]" },
                { label: "AIIN→QOK = 0.504x repulsion", detail: "Bidirectional. QOK is blocked." },
                { label: "Rules are GRAMMATICAL", detail: "77% of CHEDY tokens participate." },
              ].map((f, i) => (
                <div key={i} style={{ padding: "10px 0", borderBottom: i < 4 ? `1px solid ${COLORS.border}33` : "none" }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: COLORS.text }}>{f.label}</div>
                  <div style={{ fontSize: 12, color: COLORS.textDim, marginTop: 2 }}>{f.detail}</div>
                </div>
              ))}
            </Card>

            <Card>
              <SectionTitle sub="Excluded hypotheses">Eliminated Hypotheses</SectionTitle>
              {[
                { label: "Gibberish", reason: "Chi²/cell 0.7 vs 30.5", color: COLORS.repel },
                { label: "Simple table generation", reason: "Cannot produce positive self-clustering", color: COLORS.repel },
                { label: "Turkic languages", reason: "All 4 show negative self-clustering (0.79–0.89x)", color: COLORS.repel },
                { label: "Indo-European languages", reason: "All 5 show negative self-clustering (0.49–0.77x)", color: COLORS.repel },
              ].map((h, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 0", borderBottom: i < 3 ? `1px solid ${COLORS.border}33` : "none" }}>
                  <span style={{ color: h.color, fontSize: 16 }}>✗</span>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600 }}>{h.label}</div>
                    <div style={{ fontSize: 12, color: COLORS.textDim }}>{h.reason}</div>
                  </div>
                </div>
              ))}
              <div style={{ marginTop: 16, padding: 12, background: COLORS.surfaceLight, borderRadius: 6, borderLeft: `3px solid ${COLORS.accent}` }}>
                <div style={{ fontSize: 13, color: COLORS.text }}>
                  <strong>Closest structural neighbors:</strong> Voynich is the only tested system with symmetric-high self-clustering (prefix 1.52x, suffix 1.54x, ratio 0.99). All natural languages with positive SC are suffix-dominant.
                </div>
              </div>
            </Card>

            <Card style={{ gridColumn: "1 / -1" }}>
              <SectionTitle sub="Verified family distribution across the manuscript">Family Density Map</SectionTitle>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
                {FINDINGS.familyDensities.sections.map((sec, i) => (
                  <div key={i} style={{ padding: 12, background: COLORS.surfaceLight, borderRadius: 6 }}>
                    <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8, color: COLORS.accent }}>{sec.name}</div>
                    <div style={{ fontSize: 11, color: COLORS.textDim, marginBottom: 8 }}>Hand {sec.hand} · Currier {sec.currier} · {sec.tokens.toLocaleString()} tokens</div>
                    <Bar value={sec.qok} max={25} color={COLORS.qok} label="QOK" />
                    <Bar value={sec.ok} max={25} color={COLORS.ok} label="OK" />
                    <Bar value={sec.ot} max={25} color={COLORS.ot} label="OT" />
                    <Bar value={sec.chedy} max={25} color={COLORS.chedy} label="CHEDY" />
                    <Bar value={sec.aiin} max={25} color={COLORS.aiin} label="AIIN" />
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {tab === 1 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <Card style={{ gridColumn: "1 / -1" }}>
              <SectionTitle sub="Obs/Expected ratios. Green = attraction, Red = repulsion.">Full Transition Matrix</SectionTitle>
              <TransitionMatrix />
            </Card>
            <Card>
              <SectionTitle sub="Strength relative to chance baseline">Key Rules</SectionTitle>
              {FINDINGS.transitionRules.data.map((r, i) => (
                <RatioBar key={i} ratio={r.ratio} label={`${r.rule} (p=${r.pVal})`} />
              ))}
            </Card>
            <Card>
              <SectionTitle sub="AIIN blocks QOK but passes other families">Carry-Through</SectionTitle>
              {FINDINGS.carryThrough.data.map((c, i) => (
                <RatioBar key={i} ratio={c.ratio} label={`${c.family} → AIIN → ${c.family}`} />
              ))}
              <div style={{ marginTop: 12, padding: 10, background: COLORS.surfaceLight, borderRadius: 6, fontSize: 12, color: COLORS.textDim }}>
                AIIN acts as a transparent connector for OK, OT, CHEDY — but actively blocks QOK in both directions.
              </div>
            </Card>
          </div>
        )}

        {tab === 2 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <Card>
              <SectionTitle sub="The cleanest finding in the entire analysis">AIIN at 15% Across Currier A/B</SectionTitle>
              <div style={{ display: "flex", gap: 24, marginBottom: 16 }}>
                {[{ label: "Currier A", value: "15.0%", n: 102 }, { label: "Currier B", value: "15.0%", n: 72 }].map((d, i) => (
                  <div key={i} style={{ flex: 1, padding: 16, background: COLORS.surfaceLight, borderRadius: 6, textAlign: "center" }}>
                    <div style={{ fontSize: 28, fontWeight: 700, color: COLORS.aiin, fontFamily: "'IBM Plex Mono', monospace" }}>{d.value}</div>
                    <div style={{ fontSize: 13, color: COLORS.textDim }}>{d.label} (n={d.n} pages)</div>
                  </div>
                ))}
              </div>
              <div style={{ padding: 12, background: COLORS.surfaceLight, borderRadius: 6, fontSize: 13, borderLeft: `3px solid ${COLORS.aiin}` }}>
                <div><strong>KS test:</strong> p = 0.742</div>
                <div><strong>Bootstrap CI for difference:</strong> [−2.0%, +1.9%]</div>
                <div style={{ marginTop: 6, color: COLORS.textDim }}>Every other family differs significantly between A and B (all p &lt; 0.005). AIIN is the only invariant.</div>
              </div>
            </Card>
            <Card>
              <SectionTitle sub="AIIN does NOT self-cluster — like real function words">Function Word Behavior</SectionTitle>
              {[
                { section: "Herbal A", sc: 1.01 },
                { section: "Recipes Q20", sc: 0.71 },
                { section: "Biological", sc: 0.84 },
              ].map((d, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: `1px solid ${COLORS.border}22` }}>
                  <span style={{ fontSize: 13 }}>{d.section}</span>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", color: d.sc > 1.05 ? COLORS.attract : d.sc < 0.95 ? COLORS.neutral : COLORS.textDim, fontWeight: 600 }}>
                    {d.sc.toFixed(2)}x
                  </span>
                </div>
              ))}
              <div style={{ marginTop: 16, fontSize: 13, color: COLORS.textDim }}>
                Real function words (the, et, di) don't cluster with themselves. Neither does AIIN. Every other backbone family does.
              </div>
            </Card>
            <Card style={{ gridColumn: "1 / -1" }}>
              <SectionTitle sub="AIIN varies by section — invariance is specifically across language modes">Caveat: Section Variance</SectionTitle>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 8 }}>
                {[
                  { sec: "Astronomical", pct: 5.5 }, { sec: "Herbal B", pct: 10.8 },
                  { sec: "Biological", pct: 13.0 }, { sec: "Herbal A", pct: 14.9 },
                  { sec: "Recipes Q20", pct: 18.6 },
                ].map((d, i) => (
                  <div key={i} style={{ padding: 10, background: COLORS.surfaceLight, borderRadius: 6 }}>
                    <div style={{ fontSize: 11, color: COLORS.textDim }}>{d.sec}</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: COLORS.aiin, fontFamily: "'IBM Plex Mono', monospace" }}>{d.pct}%</div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {tab === 3 && (
          <Card>
            <SectionTitle sub="This metric is the most method-sensitive in the study">Self-Clustering: Handle with Care</SectionTitle>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 20 }}>
              {[
                { method: "Pooled (all classes)", value: "1.384x", note: "Includes OTHER" },
                { method: "Pooled (backbone)", value: "1.451x", note: "CI: [1.34, 1.52]" },
                { method: "Page-level mean", value: "0.929x", note: "Most conservative" },
              ].map((m, i) => (
                <div key={i} style={{ padding: 16, background: COLORS.surfaceLight, borderRadius: 6, textAlign: "center" }}>
                  <div style={{ fontSize: 24, fontWeight: 700, color: COLORS.accent, fontFamily: "'IBM Plex Mono', monospace" }}>{m.value}</div>
                  <div style={{ fontSize: 12, color: COLORS.text, marginTop: 4 }}>{m.method}</div>
                  <div style={{ fontSize: 11, color: COLORS.textDim, marginTop: 2 }}>{m.note}</div>
                </div>
              ))}
            </div>
            <div style={{ padding: 14, background: "#1a1a0e", border: `1px solid ${COLORS.accentDim}44`, borderRadius: 6, fontSize: 13 }}>
              <strong style={{ color: COLORS.accent }}>Why the gap matters:</strong>
              <span style={{ color: COLORS.textDim }}> Pooled values let extreme small pages dominate. Page-level averaging is fairer but shows weaker effects. The cross-linguistic comparison uses pooled (apples-to-apples), but absolute values carry uncertainty.</span>
            </div>
          </Card>
        )}

        {tab === 4 && (
          <Card>
            <SectionTitle sub="Voynich is the only system with symmetric-high clustering">Prefix / Suffix Self-Clustering</SectionTitle>
            <div style={{ overflowX: "auto" }}>
              <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 12 }}>
                <thead>
                  <tr>
                    {["System", "Type", "Prefix SC", "Suffix SC", "P/S Ratio", "Bucket"].map(h => (
                      <th key={h} style={{ padding: "8px 10px", textAlign: h === "System" ? "left" : "center", color: COLORS.textDim, borderBottom: `1px solid ${COLORS.border}`, fontSize: 11, fontWeight: 600 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {FINDINGS.crossLinguistic.languages.map((lang, i) => (
                    <tr key={i} style={{ background: lang.highlight ? `${COLORS.accent}11` : lang.control ? `${COLORS.repel}08` : "transparent" }}>
                      <td style={{ padding: "8px 10px", fontWeight: lang.highlight ? 700 : 400, color: lang.highlight ? COLORS.accent : lang.control ? COLORS.textDim : COLORS.text, borderBottom: `1px solid ${COLORS.border}22`, fontFamily: "'IBM Plex Mono', monospace" }}>{lang.name}</td>
                      <td style={{ padding: "8px 10px", textAlign: "center", color: COLORS.textDim, borderBottom: `1px solid ${COLORS.border}22`, fontSize: 11 }}>{lang.type}</td>
                      {[lang.sc, lang.asym, lang.chi2, lang.carry, lang.maxAtt].map((v, j) => (
                        <td key={j} style={{ padding: "8px 10px", textAlign: "center", fontFamily: "'IBM Plex Mono', monospace", borderBottom: `1px solid ${COLORS.border}22`,
                          color: lang.highlight ? COLORS.accent : (j === 0 && v > 1.0 ? COLORS.attract : j === 0 && v < 1.0 ? COLORS.textDim : COLORS.text)
                        }}>{j === 2 ? v.toFixed(1) : v.toFixed(2)}{j < 2 || j > 2 ? "x" : ""}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {tab === 5 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <Card style={{ gridColumn: "1 / -1" }}>
              <SectionTitle sub="Is CHEDY→QOK a few fixed phrases or a class-level rule?">The Grammar Test</SectionTitle>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
                <div style={{ padding: 16, background: COLORS.surfaceLight, borderRadius: 6, textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: 700, color: COLORS.attract, fontFamily: "'IBM Plex Mono', monospace" }}>78%</div>
                  <div style={{ fontSize: 12, color: COLORS.textDim }}>of CHEDY tokens attract QOK</div>
                  <div style={{ fontSize: 11, color: COLORS.textDim }}>(54/69 with ≥5 occurrences)</div>
                </div>
                <div style={{ padding: 16, background: COLORS.surfaceLight, borderRadius: 6, textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: 700, color: COLORS.attract, fontFamily: "'IBM Plex Mono', monospace" }}>74%</div>
                  <div style={{ fontSize: 12, color: COLORS.textDim }}>of QOK tokens attracted by CHEDY</div>
                  <div style={{ fontSize: 11, color: COLORS.textDim }}>(35/47 with ≥5 occurrences)</div>
                </div>
                <div style={{ padding: 16, background: COLORS.surfaceLight, borderRadius: 6, textAlign: "center" }}>
                  <div style={{ fontSize: 32, fontWeight: 700, color: COLORS.repel, fontFamily: "'IBM Plex Mono', monospace" }}>69%</div>
                  <div style={{ fontSize: 12, color: COLORS.textDim }}>of AIIN tokens repel QOK</div>
                  <div style={{ fontSize: 11, color: COLORS.textDim }}>(36/52 with ≥10 occurrences)</div>
                </div>
              </div>
              <div style={{ marginTop: 16, padding: 14, background: "#0e1a0e", border: `1px solid ${COLORS.attract}33`, borderRadius: 6, fontSize: 13 }}>
                <strong style={{ color: COLORS.attract }}>Verdict: </strong>
                <span style={{ color: COLORS.text }}>369 unique token pairs, top 5 cover only 13.3%. The rule is DISTRIBUTED — this is a grammatical class constraint, not fixed collocations. Any CHEDY-class word tends to pull any QOK-class word after it.</span>
              </div>
            </Card>
          </div>
        )}

        {tab === 6 && (
          <div style={{ display: "grid", gap: 16 }}>
            <Card>
              <SectionTitle sub="Data, tools, and reproducibility">Methodology</SectionTitle>
              <div style={{ fontSize: 14, lineHeight: 1.8, color: COLORS.textDim }}>
                <p><strong style={{ color: COLORS.text }}>Corpus:</strong> Zandbergen-Landini EVA transliteration via AncientLanguages/Voynich (Hugging Face). 4,197 lines, 31,608 tokens, 184 pages.</p>
                <p><strong style={{ color: COLORS.text }}>Families:</strong> QOK (prefix qok-), OK (prefix ok- not qok-), OT (prefix ot-), CHEDY (contains chedy/shedy/chey/shey), AIIN (contains aiin/ain). All others = OTHER.</p>
                <p><strong style={{ color: COLORS.text }}>Comparison languages:</strong> 11 verified natural-language comparators (9 Leipzig Wikipedia 100K, 2 Gutenberg literary) plus 1 Ottoman Turkish UD treebank and 1 shuffled-token control.</p>
                <p><strong style={{ color: COLORS.text }}>Statistical tests:</strong> Permutation tests (5,000–10,000 iterations), bootstrap CIs, KS tests, Chi-squared, split-half reliability. All transition ratios = observed/expected under independence.</p>
                
                <p><strong style={{ color: COLORS.text }}>Known limitations:</strong> Family definitions are EVA-specific and may not correspond to paleographic character boundaries. Self-clustering values are method-sensitive (pooled vs page-level). Non-IE comparison texts are modern, not medieval. Ottoman Turkish tested with small UD corpus (16,890 words): SYMM-LOW, not a match. Larger corpus needed.</p>
              </div>
            </Card>
            <Card>
              <SectionTitle>Corrections Log</SectionTitle>
              <div style={{ fontSize: 13, color: COLORS.textDim, lineHeight: 1.7 }}>
                {[
                  "Self-clustering: 0.929x (page-level) to 1.451x (pooled backbone). Method-sensitive.",
                  "CHEDY→QOK page agreement corrected from 92% to 78%. Earlier figure inflated by selection bias.",
                  "AIIN→QOK page agreement corrected from 91% to 67%. Same selection bias.",
                  "Biological self-clustering initially reported as 'not significant.' Rerun shows p < 0.001. Earlier test used different token parsing.",
                  "Carry-through values shift ~15% between runs due to token parsing differences. Directions are stable; exact decimals are approximate.",
                  
                ].map((c, i) => <p key={i} style={{ padding: "4px 0", borderBottom: `1px solid ${COLORS.border}22` }}>• {c}</p>)}
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
