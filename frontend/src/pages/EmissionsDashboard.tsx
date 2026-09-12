import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { calculateEmissions, getFactoryEmissions, getHotspots } from "../services/emissions";
import { generateRecommendations, getRecommendations } from "../services/recommendations";
import { generateExplanations } from "../services/explanations";
import { simulateFactory } from "../services/simulation";
import { getActionPlan } from "../services/actionPlan";
import { ApiError } from "../services/api";
import type { ActionPlan, EmissionsBreakdown, Explanation, Hotspot, Recommendation, SimulationResult } from "../types/domain";
import CategoryBreakdownChart from "../components/emissions/CategoryBreakdownChart";
import ProcessBreakdownTable from "../components/emissions/ProcessBreakdownTable";
import HotspotList from "../components/emissions/HotspotList";
import RecommendationList from "../components/recommendations/RecommendationList";
import SimulationPanel from "../components/simulation/SimulationPanel";
import ActionPlanPanel from "../components/action-plan/ActionPlanPanel";
import ReportDownloadButton from "../components/report/ReportDownloadButton";
import WorkspaceInsights from "../components/workspace/WorkspaceInsights";
import { clearSession } from "../services/persistence";

type LoadState = "loading" | "not-calculated" | "ready" | "error";

function formatCo2e(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString(undefined, { maximumFractionDigits: 2 }) : value;
}

function EmissionsDashboard() {
  const { factoryId } = useParams<{ factoryId: string }>();
  const [state, setState] = useState<LoadState>("loading");
  const [breakdown, setBreakdown] = useState<EmissionsBreakdown | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [explanations, setExplanations] = useState<Record<number, Explanation>>({});
  const [error, setError] = useState<string | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isGeneratingRecommendations, setIsGeneratingRecommendations] = useState(false);
  const [isGeneratingExplanations, setIsGeneratingExplanations] = useState(false);
  const [selectedRecommendationIds, setSelectedRecommendationIds] = useState<Set<number>>(new Set());
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);
  const [actionPlan, setActionPlan] = useState<ActionPlan | null>(null);
  const [isGeneratingActionPlan, setIsGeneratingActionPlan] = useState(false);
  const [actionPlanError, setActionPlanError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!factoryId) return;
    setState("loading");
    setError(null);
    try {
      const [nextBreakdown, nextHotspots] = await Promise.all([getFactoryEmissions(Number(factoryId)), getHotspots(Number(factoryId))]);
      setBreakdown(nextBreakdown);
      setHotspots(nextHotspots);
      setState("ready");
      try {
        setRecommendations(await getRecommendations(Number(factoryId)));
      } catch (recErr) {
        if (recErr instanceof ApiError && recErr.status === 404) setRecommendations([]);
        else throw recErr;
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) setState("not-calculated");
      else { setError("Unable to load emissions data."); setState("error"); }
    }
  }, [factoryId]);

  useEffect(() => { void loadData(); }, [loadData]);

  const handleCalculate = useCallback(async () => {
    if (!factoryId) return;
    setIsCalculating(true); setError(null);
    try { await calculateEmissions(Number(factoryId)); await loadData(); }
    catch { setError("Unable to calculate emissions."); }
    finally { setIsCalculating(false); }
  }, [factoryId, loadData]);

  const handleGenerateRecommendations = useCallback(async () => {
    if (!factoryId) return;
    setIsGeneratingRecommendations(true); setError(null);
    try { setRecommendations(await generateRecommendations(Number(factoryId))); }
    catch { setError("Unable to generate recommendations."); }
    finally { setIsGeneratingRecommendations(false); }
  }, [factoryId]);

  const handleExplainRecommendations = useCallback(async () => {
    if (!factoryId) return;
    setIsGeneratingExplanations(true); setError(null);
    try {
      const result = await generateExplanations(Number(factoryId));
      setExplanations(result.reduce<Record<number, Explanation>>((acc, item) => { acc[item.recommendation_id] = item; return acc; }, {}));
    } catch { setError("Unable to generate explanations."); }
    finally { setIsGeneratingExplanations(false); }
  }, [factoryId]);

  const handleToggleRecommendation = useCallback((id: number) => {
    setSelectedRecommendationIds((current) => { const next = new Set(current); next.has(id) ? next.delete(id) : next.add(id); return next; });
  }, []);

  const handleRunSimulation = useCallback(async () => {
    if (!factoryId) return;
    setIsSimulating(true); setSimulationError(null);
    try { setSimulationResult(await simulateFactory(Number(factoryId), Array.from(selectedRecommendationIds))); }
    catch { setSimulationError("Unable to run simulation."); }
    finally { setIsSimulating(false); }
  }, [factoryId, selectedRecommendationIds]);

  const handleGenerateActionPlan = useCallback(async () => {
    if (!factoryId) return;
    setIsGeneratingActionPlan(true); setActionPlanError(null);
    try { setActionPlan(await getActionPlan(Number(factoryId))); }
    catch { setActionPlanError("Unable to generate action plan."); }
    finally { setIsGeneratingActionPlan(false); }
  }, [factoryId]);

  if (state === "loading") return <div className="workspace-state"><span className="workspace-spinner" /><p>Loading emissions data…</p></div>;
  if (state === "not-calculated") return <div className="workspace-state"><span className="eyebrow">Baseline ready / 01</span><h1>Emissions not yet calculated</h1><p>This facility has data, but no emissions model has been generated yet.</p>{error && <p className="workspace-error">{error}</p>}<button type="button" className="workspace-button workspace-button-primary" onClick={handleCalculate} disabled={isCalculating}>{isCalculating ? "Calculating…" : "Calculate emissions"}</button><Link to="/" className="workspace-back">Back to home</Link></div>;
  if (state === "error" || !breakdown) return <div className="workspace-state"><span className="eyebrow">Workspace unavailable</span><h1>We couldn’t load this assessment.</h1><p>{error ?? "Unable to load emissions data."}</p><Link to="/" className="workspace-back">Back to home</Link></div>;

  const hotspotCount = hotspots.filter((item) => item.is_hotspot).length;
  const topHotspot = hotspots.find((item) => item.is_hotspot);
  const potentialReduction = recommendations.reduce((total, item) => total + Number(item.co2_reduction), 0);
  const factorSources = Array.from(new Set(breakdown.results.map((item) => item.emission_factor_source).filter(Boolean))).slice(0, 3);

  return (
    <div className="workspace-shell">
      <header className="workspace-topbar"><Link to="/" className="brand"><span className="brand-mark" />CircularCarbon</Link><div className="workspace-topbar-right"><span className="workspace-sync"><span className="status-dot" />Model synced</span><span className="workspace-avatar">CC</span></div></header>
      <div className="workspace-layout">
        <aside className="workspace-rail">
          <div className="workspace-facility"><span className="workspace-facility-kicker">Facility</span><strong>Factory #{factoryId}</strong><span>Carbon baseline</span></div>
          <nav className="workspace-nav"><span className="workspace-nav-label">Analyze</span><Link className="is-active" to={`/factories/${factoryId}/emissions`}><span>◒</span>Overview</Link><Link to={`/factories/${factoryId}/emissions/hotspots`}><span>⌁</span>Hotspots <b>{hotspotCount}</b></Link><Link to={`/factories/${factoryId}/emissions/processes`}><span>▦</span>Processes</Link><span className="workspace-nav-label">Decide</span><Link to={`/factories/${factoryId}/emissions/recommendations`}><span>✦</span>Recommendations <b>{recommendations.length}</b></Link><Link to={`/factories/${factoryId}/emissions/simulator`}><span>↗</span>Simulator</Link><Link to={`/factories/${factoryId}/emissions/action-plan`}><span>✓</span>Action plan</Link><Link to={`/factories/${factoryId}/emissions/reports`}><span>▤</span>Reports</Link></nav>
          <div className="workspace-rail-bottom"><Link to="/onboarding">＋ New assessment</Link><button type="button" className="workspace-exit" onClick={() => { clearSession(); window.location.assign("/"); }}>← Exit workspace</button></div>
        </aside>

        <main className="workspace-content" id="overview">
          <div className="workspace-breadcrumb"><span>Workspace</span><i>/</i><strong>Emissions overview</strong><span className="workspace-updated">Updated just now</span></div>
          <div className="workspace-title-row"><div><span className="eyebrow">Decision workspace / 01</span><h1>See what is driving your footprint.</h1><p>Translate your operating data into the next action worth taking.</p></div><div className="workspace-actions"><button type="button" className="workspace-button" onClick={handleCalculate} disabled={isCalculating}>{isCalculating ? "Recalculating…" : "↻ Recalculate"}</button><ReportDownloadButton factoryId={Number(factoryId)} hasCalculatedEmissions /></div></div>
          {error && <div className="workspace-error" role="alert">{error}</div>}

          <section className="workspace-hero-card"><div><span className="workspace-card-label">Total emissions</span><div className="workspace-total">{formatCo2e(breakdown.factory_total_co2e)}<small>kg CO₂e</small></div><span className="workspace-positive">↓ Baseline calculated from submitted activity data</span></div><div className="workspace-hero-side"><span className="workspace-card-label">Primary signal</span><strong>{topHotspot?.activity ?? "No hotspot yet"}</strong><span>{topHotspot ? `${topHotspot.percentage}% of measured footprint` : "Awaiting results"}</span><div className="workspace-orbit"><span>{hotspotCount}</span><small>hotspots</small></div></div></section>

          <div className="workspace-stat-grid"><div className="workspace-stat"><span>Categories tracked</span><strong>{breakdown.category_breakdown.length}</strong><small>Energy · materials · waste</small></div><div className="workspace-stat"><span>Processes tracked</span><strong>{breakdown.process_breakdown.length}</strong><small>Operational contributors</small></div><div className="workspace-stat"><span>Action candidates</span><strong>{recommendations.length}</strong><small>{recommendations.length ? "Ready to compare" : "Generate from hotspots"}</small></div><div className="workspace-stat"><span>Assessment status</span><strong className="workspace-status-text">Live</strong><small>Model is up to date</small></div></div>
          <section className="workspace-insight-strip"><div><span className="workspace-card-label">Modeled opportunity</span><strong>{potentialReduction.toLocaleString(undefined, { maximumFractionDigits: 2 })} <small>kg CO₂e potential reduction</small></strong><p>Based on currently generated recommendations; actual outcomes depend on implementation.</p></div><div><span className="workspace-card-label">Calculation basis</span><strong>Deterministic engine</strong><p>{factorSources.length ? `${factorSources.length} factor sources attached to this assessment.` : "Factor source details are available after calculation."}</p></div><Link to={`/factories/${factoryId}/emissions/reports`} className="workspace-insight-link">View methodology ↗</Link></section>

          <div className="workspace-section-heading"><div><span className="eyebrow">Read the model / 02</span><h2>Where impact is concentrated</h2></div><span className="workspace-section-note">Contribution by source</span></div>
          <div className="workspace-analysis-grid"><section className="workspace-card workspace-chart-card"><div className="workspace-card-heading"><div><h3>Category contribution</h3><p>Which inputs create the most CO₂e?</p></div><span className="workspace-chip">kg CO₂e</span></div><CategoryBreakdownChart categories={breakdown.category_breakdown} /></section><section className="workspace-card" id="hotspots"><div className="workspace-card-heading"><div><h3>Emission hotspots</h3><p>Highest-impact signals first</p></div><span className="workspace-chip workspace-chip-warning">{hotspotCount} flagged</span></div><HotspotList hotspots={hotspots.slice(0, 4)} /></section></div>

          <section className="workspace-card workspace-process-card" id="processes"><div className="workspace-card-heading"><div><h3>Process contribution</h3><p>Compare the operational footprint across your facility.</p></div><span className="workspace-section-note">Ranked by CO₂e</span></div><ProcessBreakdownTable processes={breakdown.process_breakdown} /></section>

          <WorkspaceInsights breakdown={breakdown} hotspots={hotspots} recommendations={recommendations} />

          <section className="workspace-recommendation-section" id="recommendations"><div className="workspace-section-heading"><div><span className="eyebrow">Turn insight into action / 03</span><h2>Moves worth modelling</h2><p>Choose the interventions you want to compare in the simulator.</p></div><div className="workspace-actions"><button type="button" className="workspace-button workspace-button-primary" onClick={handleGenerateRecommendations} disabled={isGeneratingRecommendations}>{isGeneratingRecommendations ? "Generating…" : "✦ Generate recommendations"}</button><button type="button" className="workspace-button" onClick={handleExplainRecommendations} disabled={isGeneratingExplanations || recommendations.length === 0}>{isGeneratingExplanations ? "Explaining…" : "Explain logic"}</button></div></div><div className="workspace-card workspace-recommendations-card"><RecommendationList recommendations={recommendations} explanations={explanations} selectedIds={selectedRecommendationIds} onToggle={handleToggleRecommendation} /></div></section>

          <div className="workspace-decision-grid"><section className="workspace-card" id="simulator"><div className="workspace-card-heading"><div><span className="eyebrow">Scenario lab / 04</span><h3>What happens if you act?</h3><p>Model selected recommendations against your current baseline.</p></div></div><SimulationPanel result={simulationResult} isLoading={isSimulating} error={simulationError} onRun={handleRunSimulation} disabled={recommendations.length === 0} /></section><section className="workspace-card" id="action-plan"><div className="workspace-card-heading"><div><span className="eyebrow">Execution / 05</span><h3>Your action sequence</h3><p>Put the highest-value moves in the right order.</p></div></div><ActionPlanPanel plan={actionPlan} isLoading={isGeneratingActionPlan} error={actionPlanError} onGenerate={handleGenerateActionPlan} disabled={recommendations.length === 0} /></section></div>
          <footer className="workspace-footer"><span>Need to update the baseline?</span><Link to="/onboarding">Start a new assessment ↗</Link><span className="mono">CircularCarbon / {factoryId}</span></footer>
        </main>
      </div>
    </div>
  );
}

export default EmissionsDashboard;
