import type { ActionPlan, ActionPlanPhase } from "../../types/domain";

interface ActionPlanPanelProps {
  plan: ActionPlan | null;
  isLoading?: boolean;
  error?: string | null;
  onGenerate: () => void;
  disabled?: boolean;
}

// Presentational only: the parent (EmissionsDashboard) owns the "Generate
// Action Plan" API call; this component renders whatever ActionPlan it is
// given verbatim, it never recomputes any phase totals.
function formatNumber(value: string): string {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString(undefined, { maximumFractionDigits: 2 }) : value;
}

const PHASE_LABELS: Record<ActionPlanPhase["phase"], string> = {
  now: "Now (0-3 months)",
  next: "Next (3-12 months)",
  later: "Later (12+ months)",
};

function PhaseSection({ phase }: { phase: ActionPlanPhase }) {
  return (
    <div
      data-testid={`action-plan-phase-${phase.phase}`}
      className="flex flex-col gap-2 rounded-md border border-border bg-background p-4"
    >
      <h3 className="text-sm font-semibold text-text">{PHASE_LABELS[phase.phase]}</h3>

      {phase.recommendations.length === 0 ? (
        <p className="text-sm text-muted">No recommendations in this phase.</p>
      ) : (
        <ul className="list-disc pl-5 text-sm text-text">
          {phase.recommendations.map((recommendation) => (
            <li key={recommendation.id}>{recommendation.title}</li>
          ))}
        </ul>
      )}

      <div className="flex gap-6 text-xs text-muted">
        <span>
          CO2 reduction: <span className="font-semibold text-text">{formatNumber(phase.total_co2_reduction)} kg</span>
        </span>
        <span>
          Implementation cost:{" "}
          <span className="font-semibold text-text">{formatNumber(phase.total_implementation_cost)}</span>
        </span>
      </div>
    </div>
  );
}

function ActionPlanPanel({ plan, isLoading, error, onGenerate, disabled }: ActionPlanPanelProps) {
  return (
    <div className="flex flex-col gap-4">
      <button
        type="button"
        onClick={onGenerate}
        disabled={isLoading || disabled}
        className="w-fit rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
      >
        {isLoading ? "Generating..." : "Generate Action Plan"}
      </button>

      {error && (
        <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger" role="alert">
          {error}
        </p>
      )}

      {!isLoading && !error && plan && (
        <div data-testid="action-plan-result" className="flex flex-col gap-4">
          <PhaseSection phase={plan.now} />
          <PhaseSection phase={plan.next} />
          <PhaseSection phase={plan.later} />
        </div>
      )}
    </div>
  );
}

export default ActionPlanPanel;
