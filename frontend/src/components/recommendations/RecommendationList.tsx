import type { Explanation, Recommendation } from "../../types/domain";
import RecommendationCard from "./RecommendationCard";
import ExplanationPanel from "./ExplanationPanel";

interface RecommendationListProps {
  recommendations: Recommendation[];
  explanations?: Record<number, Explanation>;
}

// Renders recommendations in the order provided by the backend (already
// sorted by `score` descending); this component does not re-sort.
function RecommendationList({ recommendations, explanations }: RecommendationListProps) {
  if (recommendations.length === 0) {
    return <p className="text-sm text-muted">No recommendations available yet.</p>;
  }

  return (
    <ol className="flex flex-col gap-2">
      {recommendations.map((recommendation) => {
        const explanation = explanations?.[recommendation.id];
        return (
          <RecommendationCard key={recommendation.id} recommendation={recommendation}>
            {explanation && <ExplanationPanel explanation={explanation} />}
          </RecommendationCard>
        );
      })}
    </ol>
  );
}

export default RecommendationList;
