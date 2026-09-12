import type { Explanation } from "../../types/domain";

interface ExplanationPanelProps {
  explanation?: Explanation;
  isLoading?: boolean;
  error?: string | null;
}

// Presentational only: the parent (EmissionsDashboard) owns the "Explain
// Recommendations" API call and state; this component just renders whatever
// explanation/loading/error state it is given for a single recommendation.
function ExplanationPanel({ explanation, isLoading, error }: ExplanationPanelProps) {
  if (isLoading) {
    return (
      <div className="rounded-md border border-border bg-background p-3 text-sm text-muted">
        Loading explanation...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-3 text-sm text-danger" role="alert">
        {error}
      </div>
    );
  }

  if (!explanation) {
    return null;
  }

  return (
    <div className="flex flex-col gap-2 rounded-md border border-border bg-background p-3 text-sm text-text">
      <div>
        <span className="font-semibold">Why</span>
        <p className="text-muted">{explanation.why}</p>
      </div>
      <div>
        <span className="font-semibold">What to do</span>
        <p className="text-muted">{explanation.what_to_do}</p>
      </div>
      <div>
        <span className="font-semibold">Expected benefit</span>
        <p className="text-muted">{explanation.expected_benefit}</p>
      </div>
      <div>
        <span className="font-semibold">Assumptions</span>
        <p className="text-muted">{explanation.assumptions}</p>
      </div>
    </div>
  );
}

export default ExplanationPanel;
