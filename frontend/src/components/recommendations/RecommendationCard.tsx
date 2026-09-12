import type { Recommendation } from "../../types/domain";

interface RecommendationCardProps {
  recommendation: Recommendation;
}

const strategyLabels: Record<Recommendation["strategy"], string> = {
  reduce: "Reduce",
  reuse: "Reuse",
  recycle: "Recycle",
  substitute: "Substitute",
  recover: "Recover",
  process_optimization: "Process Optimization",
};

const costLabels: Record<Recommendation["estimated_cost"], string> = {
  low: "Low cost",
  medium: "Medium cost",
  high: "High cost",
};

// co2_reduction/score/payback_period arrive as Decimal-backed strings (or
// null) from the backend; parse to Number only for display formatting, never
// to recompute any value.
function formatCo2e(value: string): string {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString(undefined, { maximumFractionDigits: 2 }) : value;
}

function formatScore(value: string | null): string {
  if (value === null) return "N/A";
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(2) : value;
}

function formatPayback(value: string | null): string {
  if (value === null) return "N/A";
  const parsed = Number(value);
  return Number.isFinite(parsed) ? `${parsed} months` : value;
}

function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <li
      data-testid={`recommendation-card-${recommendation.id}`}
      className="flex flex-col gap-2 rounded-md border border-border bg-surface p-4 text-sm text-text"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <span className="font-semibold">{recommendation.title}</span>
          <span className="text-xs text-muted">
            {recommendation.hotspot_activity} ({recommendation.hotspot_category})
          </span>
        </div>
        <span className="w-fit rounded-full bg-mint px-3 py-1 text-xs font-semibold text-primary">
          {strategyLabels[recommendation.strategy]}
        </span>
      </div>

      <p className="text-sm text-text">{recommendation.description}</p>

      <div className="flex flex-wrap items-center gap-4 text-xs text-muted">
        <span>
          <span className="font-semibold text-text">{formatCo2e(recommendation.co2_reduction)} kg CO2e</span>{" "}
          reduction
        </span>
        <span>{costLabels[recommendation.estimated_cost]}</span>
        <span>Payback: {formatPayback(recommendation.payback_period)}</span>
        <span className="font-semibold text-primary">Score: {formatScore(recommendation.score)}</span>
      </div>
    </li>
  );
}

export default RecommendationCard;
