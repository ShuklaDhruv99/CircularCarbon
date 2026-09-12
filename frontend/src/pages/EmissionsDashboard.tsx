import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { calculateEmissions, getFactoryEmissions, getHotspots } from "../services/emissions";
import { generateRecommendations, getRecommendations } from "../services/recommendations";
import { generateExplanations } from "../services/explanations";
import { simulateFactory } from "../services/simulation";
import { ApiError } from "../services/api";
import type { EmissionsBreakdown, Explanation, Hotspot, Recommendation, SimulationResult } from "../types/domain";
import CategoryBreakdownChart from "../components/emissions/CategoryBreakdownChart";
import ProcessBreakdownTable from "../components/emissions/ProcessBreakdownTable";
import HotspotList from "../components/emissions/HotspotList";
import RecommendationList from "../components/recommendations/RecommendationList";
import SimulationPanel from "../components/simulation/SimulationPanel";

type LoadState = "loading" | "not-calculated" | "ready" | "error";

function formatCo2e(value: string): string {
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

  const loadData = useCallback(async () => {
    if (!factoryId) return;
    setState("loading");
    setError(null);
    try {
      const [breakdownResult, hotspotsResult] = await Promise.all([
        getFactoryEmissions(Number(factoryId)),
        getHotspots(Number(factoryId)),
      ]);
      setBreakdown(breakdownResult);
      setHotspots(hotspotsResult);
      setState("ready");

      // Recommendations may not have been generated yet even though
      // emissions/hotspots are calculated (they're a separate action), so
      // a 404 here just means "no recommendations yet" rather than an error.
      try {
        setRecommendations(await getRecommendations(Number(factoryId)));
      } catch (recErr) {
        if (recErr instanceof ApiError && recErr.status === 404) {
          setRecommendations([]);
        } else {
          throw recErr;
        }
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setState("not-calculated");
        return;
      }
      setError("Unable to load emissions data.");
      setState("error");
    }
  }, [factoryId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCalculate = useCallback(async () => {
    if (!factoryId) return;
    setIsCalculating(true);
    setError(null);
    try {
      await calculateEmissions(Number(factoryId));
      await loadData();
    } catch {
      setError("Unable to calculate emissions.");
    } finally {
      setIsCalculating(false);
    }
  }, [factoryId, loadData]);

  const handleGenerateRecommendations = useCallback(async () => {
    if (!factoryId) return;
    setIsGeneratingRecommendations(true);
    setError(null);
    try {
      const result = await generateRecommendations(Number(factoryId));
      setRecommendations(result);
    } catch {
      setError("Unable to generate recommendations.");
    } finally {
      setIsGeneratingRecommendations(false);
    }
  }, [factoryId]);

  const handleExplainRecommendations = useCallback(async () => {
    if (!factoryId) return;
    setIsGeneratingExplanations(true);
    setError(null);
    try {
      const result = await generateExplanations(Number(factoryId));
      setExplanations(
        result.reduce<Record<number, Explanation>>((acc, explanation) => {
          acc[explanation.recommendation_id] = explanation;
          return acc;
        }, {}),
      );
    } catch {
      setError("Unable to generate explanations.");
    } finally {
      setIsGeneratingExplanations(false);
    }
  }, [factoryId]);

  const handleToggleRecommendation = useCallback((id: number) => {
    setSelectedRecommendationIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handleRunSimulation = useCallback(async () => {
    if (!factoryId) return;
    setIsSimulating(true);
    setSimulationError(null);
    try {
      const result = await simulateFactory(Number(factoryId), Array.from(selectedRecommendationIds));
      setSimulationResult(result);
    } catch {
      setSimulationError("Unable to run simulation.");
    } finally {
      setIsSimulating(false);
    }
  }, [factoryId, selectedRecommendationIds]);

  if (state === "loading") {
    return (
      <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-4 bg-background px-4 py-10">
        <p className="text-muted">Loading emissions data...</p>
      </div>
    );
  }

  if (state === "not-calculated") {
    return (
      <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-4 bg-background px-4 py-10">
        <h1 className="text-2xl font-semibold text-text">Emissions not yet calculated</h1>
        <p className="text-sm text-muted">
          This factory has entered process data but no emissions calculation has been run yet.
        </p>
        {error && <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>}
        <button
          type="button"
          onClick={handleCalculate}
          disabled={isCalculating}
          className="w-fit rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
        >
          {isCalculating ? "Calculating..." : "Calculate emissions"}
        </button>
        <Link to="/" className="text-primary underline">
          Back to home
        </Link>
      </div>
    );
  }

  if (state === "error" || !breakdown) {
    return (
      <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-4 bg-background px-4 py-10">
        <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">
          {error ?? "Unable to load emissions data."}
        </p>
        <Link to="/" className="text-primary underline">
          Back to home
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-4xl flex-col gap-8 bg-background px-4 py-10">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold text-text">Emissions Dashboard</h1>
        <button
          type="button"
          onClick={handleCalculate}
          disabled={isCalculating}
          className="w-fit rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
        >
          {isCalculating ? "Recalculating..." : "Recalculate"}
        </button>
      </div>

      {error && <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>}

      <section className="rounded-md border border-border bg-surface p-4">
        <h2 className="text-lg font-semibold text-text">Total Emissions</h2>
        <p className="text-3xl font-bold text-primary">{formatCo2e(breakdown.factory_total_co2e)} kg CO2e</p>
      </section>

      <section className="flex flex-col gap-4 rounded-md border border-border bg-surface p-4">
        <h2 className="text-lg font-semibold text-text">Category Breakdown</h2>
        <CategoryBreakdownChart categories={breakdown.category_breakdown} />
      </section>

      <section className="flex flex-col gap-4 rounded-md border border-border bg-surface p-4">
        <h2 className="text-lg font-semibold text-text">Process Breakdown</h2>
        <ProcessBreakdownTable processes={breakdown.process_breakdown} />
      </section>

      <section className="flex flex-col gap-4 rounded-md border border-border bg-surface p-4">
        <h2 className="text-lg font-semibold text-text">Emission Hotspots</h2>
        <HotspotList hotspots={hotspots} />
      </section>

      <section className="flex flex-col gap-4 rounded-md border border-border bg-surface p-4">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-text">Circular Recommendations</h2>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleGenerateRecommendations}
              disabled={isGeneratingRecommendations}
              className="w-fit rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
            >
              {isGeneratingRecommendations ? "Generating..." : "Generate Recommendations"}
            </button>
            <button
              type="button"
              onClick={handleExplainRecommendations}
              disabled={isGeneratingExplanations || recommendations.length === 0}
              className="w-fit rounded-md border border-primary px-4 py-2 text-sm font-semibold text-primary disabled:opacity-60"
            >
              {isGeneratingExplanations ? "Explaining..." : "Explain Recommendations"}
            </button>
          </div>
        </div>
        <RecommendationList
          recommendations={recommendations}
          explanations={explanations}
          selectedIds={selectedRecommendationIds}
          onToggle={handleToggleRecommendation}
        />
      </section>

      <section className="flex flex-col gap-4 rounded-md border border-border bg-surface p-4">
        <h2 className="text-lg font-semibold text-text">What-If Simulator</h2>
        <SimulationPanel
          result={simulationResult}
          isLoading={isSimulating}
          error={simulationError}
          onRun={handleRunSimulation}
          disabled={recommendations.length === 0}
        />
      </section>

      <Link to="/" className="text-primary underline">
        Back to home
      </Link>
    </div>
  );
}

export default EmissionsDashboard;
