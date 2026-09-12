import type { CSSProperties } from "react";
import type { EmissionsBreakdown, Hotspot, Recommendation } from "../../types/domain";

interface WorkspaceInsightsProps {
  breakdown: EmissionsBreakdown;
  hotspots: Hotspot[];
  recommendations: Recommendation[];
}

const COSTS: Record<Recommendation["estimated_cost"], number> = { low: 50000, medium: 200000, high: 500000 };

function number(value: number | string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString(undefined, { maximumFractionDigits: 2 }) : String(value);
}

function percent(value: number) {
  return `${Math.max(0, Math.min(100, value)).toFixed(1)}%`;
}

function WorkspaceInsights({ breakdown, hotspots, recommendations }: WorkspaceInsightsProps) {
  const total = Number(breakdown.factory_total_co2e) || 0;
  const totalReduction = recommendations.reduce((sum, item) => sum + (Number(item.co2_reduction) || 0), 0);
  const projected = Math.max(0, total - totalReduction);
  const reductionPercent = total ? (totalReduction / total) * 100 : 0;
  const flagged = hotspots.filter((item) => item.is_hotspot);
  const topHotspot = flagged[0];
  const averageScore = recommendations.length
    ? recommendations.reduce((sum, item) => sum + (Number(item.score) || 0), 0) / recommendations.length
    : 0;
  const circularityScore = Math.round(Math.min(100, 42 + averageScore * 0.28 + Math.min(18, recommendations.length * 2)));
  const completeness = Math.min(100, Math.round((breakdown.category_breakdown.length / 3) * 70 + (flagged.length ? 20 : 0) + (recommendations.length ? 10 : 0)));
  const totalCost = recommendations.reduce((sum, item) => sum + COSTS[item.estimated_cost], 0);
  const paybacks = recommendations.map((item) => Number(item.payback_period)).filter((value) => Number.isFinite(value) && value > 0);
  const averagePayback = paybacks.length ? paybacks.reduce((sum, value) => sum + value, 0) / paybacks.length : 0;
  const modeledAnnualValue = averagePayback ? (totalCost / averagePayback) * 12 : 0;
  const sources = Array.from(new Set(breakdown.results.map((item) => item.emission_factor_source).filter(Boolean))).slice(0, 2);

  return (
    <div className="insights-stack">
      <div className="insights-section-heading"><div><span className="eyebrow">Decision intelligence / 06</span><h2>Make the model useful in the room.</h2><p>Translate the baseline into a story your operations team and leadership can act on.</p></div><button className="insights-print" type="button" onClick={() => window.print()}>Print executive summary ↗</button></div>

      <section className="insights-leak-map workspace-card"><div className="insights-card-heading"><div><h3>Emission leak-point map</h3><p>A process view of where carbon is accumulating.</p></div><span className="workspace-chip workspace-chip-warning">{flagged.length} priority signals</span></div><div className="leak-flow">{breakdown.process_breakdown.length ? breakdown.process_breakdown.map((process, index) => <div className="leak-node" key={process.process_id}><div className="leak-node-index">0{index + 1}</div><div className="leak-node-copy"><strong>Process · {process.process_name}</strong><span>{process.percentage}% of facility footprint</span></div><div className="leak-node-bar"><i style={{ width: `${Math.min(100, Number(process.percentage))}%` }} /></div><b>{number(process.co2e)} <small>kg CO₂e</small></b>{index < breakdown.process_breakdown.length - 1 && <span className="leak-arrow">→</span>}</div>) : <p className="workspace-empty">Add process data to build the leak-point map.</p>}</div></section>

      <div className="insights-grid insights-grid-three"><section className="workspace-card score-card"><div className="score-ring" style={{ "--score": `${circularityScore * 3.6}deg` } as CSSProperties}><strong>{circularityScore}</strong><span>/ 100</span></div><span className="eyebrow">Estimated circularity</span><h3>Transition readiness</h3><p>Based on your current recommendation mix and modeled intervention scores.</p><span className="score-confidence">{recommendations.length ? "Medium confidence" : "Needs more data"}</span></section><section className="workspace-card quality-card"><div className="insights-card-heading"><div><span className="eyebrow">Data quality</span><h3>Assessment completeness</h3></div><strong>{completeness}%</strong></div><div className="quality-track"><i style={{ width: `${completeness}%` }} /></div><ul><li className={breakdown.category_breakdown.length ? "done" : ""}>✓ Energy, materials and waste</li><li className={flagged.length ? "done" : ""}>✓ Hotspot calculation</li><li className={recommendations.length ? "done" : ""}>✓ Recommendation model</li><li>○ Transport and packaging not captured</li></ul></section><section className="workspace-card benchmark-card"><span className="eyebrow">Reference signal / beta</span><h3>{topHotspot ? `${topHotspot.percentage}% concentration` : "No benchmark yet"}</h3><p>{topHotspot ? `Your top signal is ${topHotspot.activity}. Facilities with a single source above 50% should prioritise one focused intervention before broad initiatives.` : "Calculate emissions to unlock operational reference context."}</p><span className="benchmark-tag">Operational concentration</span></section></div>

      <div className="insights-grid insights-grid-two"><section className="workspace-card before-after-card"><div className="insights-card-heading"><div><span className="eyebrow">Scenario preview</span><h3>Before vs. after recommended actions</h3><p>Applies the currently generated recommendations as a modeled ceiling.</p></div></div><div className="before-after-values"><div><span>Current baseline</span><strong>{number(total)} <small>kg CO₂e</small></strong></div><div className="before-after-arrow">→</div><div className="after-value"><span>Modeled outcome</span><strong>{number(projected)} <small>kg CO₂e</small></strong></div><div className="reduction-pill">↓ {percent(reductionPercent)} reduction</div></div><div className="before-after-track"><i style={{ width: `${total ? Math.max(2, 100 - reductionPercent) : 0}%` }} /></div></section><section className="workspace-card financial-card"><div className="insights-card-heading"><div><span className="eyebrow">Financial lens / MVP estimate</span><h3>Impact worth funding</h3></div></div><div className="financial-grid"><div><span>Modeled reduction</span><strong>{number(totalReduction)} <small>kg CO₂e</small></strong></div><div><span>Implementation scale</span><strong>₹{number(totalCost)}</strong></div><div><span>Modeled annual value</span><strong>₹{number(modeledAnnualValue)}</strong></div><div><span>Average payback</span><strong>{averagePayback ? `${number(averagePayback)} mo` : "N/A"}</strong></div></div><p>Cost figures use the current MVP cost tiers. Annual value is derived from modeled cost and payback, not live financial data.</p></section></div>

      <section className="workspace-card matrix-card"><div className="insights-card-heading"><div><span className="eyebrow">Prioritisation lens</span><h3>Impact vs. implementation cost</h3><p>The best first move sits high on impact and low on cost.</p></div></div><div className="matrix-layout"><div className="impact-matrix"><span className="matrix-y">Higher impact</span><span className="matrix-x">Lower cost → Higher cost</span><span className="matrix-zone zone-first">DO FIRST</span><span className="matrix-zone zone-plan">PLAN</span>{recommendations.slice(0, 8).map((item) => { const x = item.estimated_cost === "low" ? 18 : item.estimated_cost === "medium" ? 50 : 81; const y = Math.max(10, 90 - (Number(item.co2_reduction) / Math.max(1, total)) * 100); return <span key={item.id} title={item.title} className="matrix-point" style={{ left: `${x}%`, top: `${y}%` }}>{item.id}</span>; })}</div><div className="matrix-legend">{recommendations.slice(0, 8).map((item) => <div key={item.id}><span className="matrix-key">{item.id}</span><span>{item.title}</span><b>{item.estimated_cost}</b></div>)}{!recommendations.length && <p className="workspace-empty">Generate recommendations to populate this decision matrix.</p>}</div></div></section>

      <div className="insights-grid insights-grid-two"><section className="workspace-card ai-brief-card"><div className="ai-brief-mark">✦</div><div><span className="eyebrow">Explainable intelligence</span><h3>Why this matters</h3><p>{topHotspot ? `${topHotspot.activity} is your leading leak point at ${topHotspot.percentage}% of the measured footprint. The fastest path to progress is to compare a focused intervention against the current baseline, then sequence the move with the shortest payback.` : "Calculate your emissions and generate recommendations to receive a plain-language decision brief."}</p><div className="ai-brief-points"><span>01 / Highest-impact signal identified</span><span>02 / Circular response can be compared</span><span>03 / Assumptions remain visible</span></div></div></section><section className="workspace-card executive-card"><div className="insights-card-heading"><div><span className="eyebrow">Leadership view</span><h3>Executive summary</h3></div><span className="workspace-chip">Ready to share</span></div><p>{number(total)} kg CO₂e baseline, with {number(totalReduction)} kg CO₂e of modeled opportunity across {recommendations.length} candidate actions. Prioritise the highest-contribution signal, validate the assumptions with operations, and start with low-cost interventions.</p><button className="workspace-button workspace-button-primary" type="button" onClick={() => window.print()}>Print one-page summary</button></section></div>

      <section className="workspace-card provenance-card"><div><span className="eyebrow">Trust layer</span><h3>Show your working.</h3><p>Every estimate is traceable to the deterministic engine. The AI layer explains and contextualises the result; it does not invent factors or financial inputs.</p></div><div className="provenance-sources">{sources.length ? sources.map((source) => <span key={source}>✓ {source}</span>) : <span>✓ Factor sources appear after calculation</span>}<span>✓ Current scope: energy · materials · waste</span><span>△ Transport, packaging, water and chemicals are future scope</span></div></section>
    </div>
  );
}

export default WorkspaceInsights;
