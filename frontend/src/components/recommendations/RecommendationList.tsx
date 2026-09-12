import type { Recommendation } from "../../types/domain";
import RecommendationCard from "./RecommendationCard";

interface RecommendationListProps {
  recommendations: Recommendation[];
}

// Renders recommendations in the order provided by the backend (already
// sorted by `score` descending); this component does not re-sort.
function RecommendationList({ recommendations }: RecommendationListProps) {
  if (recommendations.length === 0) {
    return <p className="text-sm text-muted">No recommendations available yet.</p>;
  }

  return (
    <ol className="flex flex-col gap-2">
      {recommendations.map((recommendation) => (
        <RecommendationCard key={recommendation.id} recommendation={recommendation} />
      ))}
    </ol>
  );
}

export default RecommendationList;
