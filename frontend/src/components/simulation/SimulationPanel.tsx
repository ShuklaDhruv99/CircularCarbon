import type { SimulationResult } from "../../types/domain";

interface SimulationPanelProps {
  result: SimulationResult | null;
  isLoading?: boolean;
  error?: string | null;
  onRun: () => void;
  disabled?: boolean;
}

// Presentational only: the parent (EmissionsDashboard) owns the "Run What-If
// Simulation" API call and selection state; this component renders whatever
// SimulationResult it is given verbatim, it never recomputes any totals.
function formatNumber(value: string): string {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString(undefined, { maximumFractionDigits: 2 }) : value;
}

function formatPayback(value: string | null): string {
  if (value === null) return "N/A";
  const parsed = Number(value);
  return Number.isFinite(parsed) ? `${formatNumber(value)} months` : value;
}

function SimulationPanel({ result, isLoading, error, onRun, disabled }: SimulationPanelProps) {
  return (
    <div className="flex flex-col gap-4">
      <button
        type="button"
        onClick={onRun}
        disabled={isLoading || disabled}
        className="w-fit rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
      >
        {isLoading ? "Simulating..." : "Run What-If Simulation"}
      </button>

      {error && (
        <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger" role="alert">
          {error}
        </p>
      )}

      {!isLoading && !error && result && (
        <div
          data-testid="simulation-result"
          className="flex flex-col gap-4 rounded-md border border-border bg-background p-4 text-sm text-text"
        >
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <span className="text-xs text-muted">Baseline CO2e</span>
              <p className="text-lg font-semibold text-text">{formatNumber(result.baseline_co2e)} kg</p>
            </div>
            <div>
              <span className="text-xs text-muted">Projected CO2e</span>
              <p className="text-lg font-semibold text-primary">{formatNumber(result.projected_co2e)} kg</p>
            </div>
            <div>
              <span className="text-xs text-muted">Reduction</span>
              <p className="text-lg font-semibold text-text">
                {formatNumber(result.co2_reduction)} kg ({formatNumber(result.reduction_percentage)}%)
              </p>
            </div>
            <div>
              <span className="text-xs text-muted">Implementation Cost</span>
              <p className="text-lg font-semibold text-text">
                {formatNumber(result.total_implementation_cost)}
              </p>
            </div>
          </div>

          <div>
            <span className="text-xs text-muted">Estimated Payback</span>
            <p className="text-lg font-semibold text-text">{formatPayback(result.estimated_payback_months)}</p>
          </div>

          <div>
            <span className="text-xs font-semibold text-muted">Applied Recommendations</span>
            {result.applied_recommendations.length === 0 ? (
              <p className="text-sm text-muted">No recommendations applied.</p>
            ) : (
              <ul className="list-disc pl-5">
                {result.applied_recommendations.map((recommendation) => (
                  <li key={recommendation.id}>{recommendation.title}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulationPanel;
