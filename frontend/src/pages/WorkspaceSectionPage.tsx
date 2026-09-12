import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError } from "../services/api";
import { getFactoryEmissions, getHotspots } from "../services/emissions";
import { generateExplanations } from "../services/explanations";
import { getActionPlan } from "../services/actionPlan";
import { generateRecommendations, getRecommendations } from "../services/recommendations";
import { simulateFactory } from "../services/simulation";
import type { ActionPlan, EmissionsBreakdown, Explanation, Hotspot, Recommendation, SimulationResult } from "../types/domain";
import CategoryBreakdownChart from "../components/emissions/CategoryBreakdownChart";
import ProcessBreakdownTable from "../components/emissions/ProcessBreakdownTable";
import HotspotList from "../components/emissions/HotspotList";
import RecommendationList from "../components/recommendations/RecommendationList";
import SimulationPanel from "../components/simulation/SimulationPanel";
import ActionPlanPanel from "../components/action-plan/ActionPlanPanel";
import ReportDownloadButton from "../components/report/ReportDownloadButton";
import { clearSession } from "../services/persistence";

type Section = "hotspots" | "processes" | "recommendations" | "simulator" | "action-plan" | "reports";
const sectionNames: Record<Section, string> = { hotspots: "Emission hotspots", processes: "Process contribution", recommendations: "Recommendations", simulator: "Scenario simulator", "action-plan": "Action plan", reports: "Reports" };

function WorkspaceFrame({ factoryId, section, children, hotspotCount, recommendationCount }: { factoryId: string; section: Section; children: ReactNode; hotspotCount: number; recommendationCount: number }) {
  const link = (name: string) => `/factories/${factoryId}/emissions/${name}`;
  return <div className="workspace-shell"><header className="workspace-topbar"><Link to="/" className="brand"><span className="brand-mark" />CircularCarbon</Link><div className="workspace-topbar-right"><span className="workspace-sync"><span className="status-dot" />Model synced</span><span className="workspace-avatar">CC</span></div></header><div className="workspace-layout"><aside className="workspace-rail"><div className="workspace-facility"><span className="workspace-facility-kicker">Facility</span><strong>Factory #{factoryId}</strong><span>Carbon baseline</span></div><nav className="workspace-nav"><span className="workspace-nav-label">Analyze</span><Link to={`/factories/${factoryId}/emissions`}><span>◒</span>Overview</Link><Link className={section === "hotspots" ? "is-active" : ""} to={link("hotspots")}><span>⌁</span>Hotspots <b>{hotspotCount}</b></Link><Link className={section === "processes" ? "is-active" : ""} to={link("processes")}><span>▦</span>Processes</Link><span className="workspace-nav-label">Decide</span><Link className={section === "recommendations" ? "is-active" : ""} to={link("recommendations")}><span>✦</span>Recommendations <b>{recommendationCount}</b></Link><Link className={section === "simulator" ? "is-active" : ""} to={link("simulator")}><span>↗</span>Simulator</Link><Link className={section === "action-plan" ? "is-active" : ""} to={link("action-plan")}><span>✓</span>Action plan</Link><Link className={section === "reports" ? "is-active" : ""} to={link("reports")}><span>▤</span>Reports</Link></nav><div className="workspace-rail-bottom"><Link to="/onboarding">＋ New assessment</Link><button type="button" className="workspace-exit" onClick={() => { clearSession(); window.location.assign("/"); }}>← Exit workspace</button></div></aside><main className="workspace-content"><div className="workspace-breadcrumb"><span>Workspace</span><i>/</i><strong>{sectionNames[section]}</strong><span className="workspace-updated">Factory #{factoryId}</span></div><div className="workspace-page-heading"><span className="eyebrow">CircularCarbon workspace</span><h1>{sectionNames[section]}</h1><p>Make the next decision with a clear view of your factory data.</p></div>{children}<footer className="workspace-footer"><span>Need to update the baseline?</span><Link to="/onboarding">Start a new assessment ↗</Link><span className="mono">CircularCarbon / {factoryId}</span></footer></main></div></div>;
}

function WorkspaceSectionPage() {
  const { factoryId, section: rawSection } = useParams<{ factoryId: string; section: string }>();
  const section = (rawSection ?? "hotspots") as Section;
  const [breakdown, setBreakdown] = useState<EmissionsBreakdown | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [explanations, setExplanations] = useState<Record<number, Explanation>>({});
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [actionPlan, setActionPlan] = useState<ActionPlan | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!factoryId) return;
    Promise.all([getFactoryEmissions(Number(factoryId)), getHotspots(Number(factoryId))]).then(([nextBreakdown, nextHotspots]) => { setBreakdown(nextBreakdown); setHotspots(nextHotspots); return getRecommendations(Number(factoryId)); }).then(setRecommendations).catch((err) => { if (!(err instanceof ApiError && err.status === 404)) setError("Unable to load this workspace page."); });
  }, [factoryId]);

  const run = useCallback(async (task: () => Promise<void>) => { setBusy(true); setError(null); try { await task(); } catch { setError("That action could not be completed. Please try again."); } finally { setBusy(false); } }, []);
  if (!factoryId || !breakdown) return <div className="workspace-state"><span className="workspace-spinner" /><p>{error ?? "Loading workspace…"}</p></div>;
  const count = hotspots.filter((item) => item.is_hotspot).length;
  const factorSources = Array.from(new Set(breakdown.results.map((item) => item.emission_factor_source).filter(Boolean)));
  const toggle = (id: number) => setSelected((current) => { const next = new Set(current); next.has(id) ? next.delete(id) : next.add(id); return next; });

  let content: ReactNode;
  if (section === "hotspots") content = <><div className="workspace-leak-banner"><span className="workspace-leak-icon">⌁</span><div><span className="eyebrow">Leak-point diagnosis</span><h2>{count ? `${count} process signals need attention first.` : "No dominant leak points detected yet."}</h2><p>Here, a leak point means a process, input, or waste stream creating disproportionate carbon impact — not a physical gas leak.</p></div></div><div className="workspace-page-grid"><section className="workspace-card workspace-chart-card"><div className="workspace-card-heading"><div><h3>Category contribution</h3><p>See the shape of your footprint before prioritising a response.</p></div><span className="workspace-chip">kg CO₂e</span></div><CategoryBreakdownChart categories={breakdown.category_breakdown} /></section><section className="workspace-card"><div className="workspace-card-heading"><div><h3>Ranked hotspots</h3><p>Signals contributing most to the baseline.</p></div><span className="workspace-chip workspace-chip-warning">{count} flagged</span></div><HotspotList hotspots={hotspots} /></section></div></>;
  else if (section === "processes") content = <section className="workspace-card"><div className="workspace-card-heading"><div><h3>Process contribution</h3><p>Compare every tracked process by its emissions contribution.</p></div></div><ProcessBreakdownTable processes={breakdown.process_breakdown} /></section>;
  else if (section === "recommendations") content = <><div className="workspace-toolbar"><p>Generate ranked circular interventions from the hotspots in your assessment.</p><div className="workspace-actions"><button className="workspace-button workspace-button-primary" type="button" onClick={() => void run(async () => setRecommendations(await generateRecommendations(Number(factoryId))))} disabled={busy}>{busy ? "Generating…" : "✦ Generate recommendations"}</button><button className="workspace-button" type="button" onClick={() => void run(async () => { const result = await generateExplanations(Number(factoryId)); setExplanations(result.reduce<Record<number, Explanation>>((acc, item) => { acc[item.recommendation_id] = item; return acc; }, {})); })} disabled={busy || recommendations.length === 0}>Explain logic</button></div></div>{error && <div className="workspace-error">{error}</div>}<section className="workspace-card workspace-recommendations-card"><RecommendationList recommendations={recommendations} explanations={explanations} selectedIds={selected} onToggle={toggle} /></section></>;
  else if (section === "simulator") content = <><section className="workspace-card"><div className="workspace-card-heading"><div><h3>Scenario simulator</h3><p>Select the interventions you want to test. The model compares their combined impact against your current baseline.</p></div><span className="workspace-chip">{selected.size} selected</span></div><RecommendationList recommendations={recommendations} selectedIds={selected} onToggle={toggle} /></section><section className="workspace-card workspace-simulator-run"><SimulationPanel result={simulation} isLoading={busy} error={error} onRun={() => void run(async () => setSimulation(await simulateFactory(Number(factoryId), Array.from(selected))))} disabled={recommendations.length === 0} /></section></>;
  else if (section === "action-plan") content = <section className="workspace-card"><div className="workspace-card-heading"><div><h3>Prioritized action plan</h3><p>Turn recommendations into a staged sequence for execution.</p></div></div><ActionPlanPanel plan={actionPlan} isLoading={busy} error={error} onGenerate={() => void run(async () => setActionPlan(await getActionPlan(Number(factoryId))))} disabled={recommendations.length === 0} /></section>;
  else content = <div className="workspace-report-grid"><section className="workspace-card report-page-card"><div className="report-page-icon">▤</div><h3>Assessment report</h3><p>Download a shareable report of your factory baseline, calculated emissions, hotspots, recommendations, and action plan.</p><ReportDownloadButton factoryId={Number(factoryId)} hasCalculatedEmissions /><div className="report-page-note">Generated from the current assessment model.</div></section><section className="workspace-card methodology-card"><span className="eyebrow">Traceability / assumptions</span><h3>How this estimate was built</h3><p>All calculations use the deterministic carbon engine. The dashboard does not ask the AI model to invent factors, costs, or savings.</p><div className="methodology-list"><div><strong>Emission factors</strong><span>{factorSources.length ? factorSources.map((source) => <small key={source}>{source}</small>) : <small>Sources will appear after emissions are calculated.</small>}</span></div><div><strong>Included scope</strong><span>Energy, materials, waste, and process activity.</span></div><div><strong>MVP limitation</strong><span>Transport, packaging, water, chemicals, and real operating savings are not modeled yet.</span></div></div></section></div>;

  return <WorkspaceFrame factoryId={factoryId} section={section} hotspotCount={count} recommendationCount={recommendations.length}>{content}</WorkspaceFrame>;
}

export default WorkspaceSectionPage;
