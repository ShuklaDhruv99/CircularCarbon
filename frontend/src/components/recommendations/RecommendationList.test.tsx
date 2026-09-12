import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import RecommendationList from "./RecommendationList";
import type { Recommendation } from "../../types/domain";

const recommendations: Recommendation[] = [
  {
    id: 1,
    hotspot_id: 10,
    hotspot_category: "energy",
    hotspot_activity: "electricity",
    title: "Switch to renewable electricity",
    description: "Replace grid electricity with a renewable energy contract.",
    strategy: "substitute",
    estimated_cost: "medium",
    co2_reduction: "450.00",
    payback_period: "18",
    score: "82.50",
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    hotspot_id: 11,
    hotspot_category: "waste",
    hotspot_activity: "scrap_metal",
    title: "Recycle scrap metal instead of landfilling",
    description: "Divert scrap metal waste to a recycling partner.",
    strategy: "recycle",
    estimated_cost: "low",
    co2_reduction: "120.00",
    payback_period: "6",
    score: "91.20",
    created_at: "2024-01-01T00:00:00Z",
  },
];

describe("RecommendationList", () => {
  it("shows an empty state when there are no recommendations", () => {
    render(<RecommendationList recommendations={[]} />);
    expect(screen.getByText(/no recommendations available yet/i)).toBeInTheDocument();
  });

  it("renders recommendation cards in the order provided (score descending)", () => {
    render(<RecommendationList recommendations={recommendations} />);

    const items = screen.getAllByRole("listitem");
    expect(items).toHaveLength(2);

    expect(screen.getByText("Switch to renewable electricity")).toBeInTheDocument();
    expect(screen.getByText("Recycle scrap metal instead of landfilling")).toBeInTheDocument();
    expect(screen.getByText(/electricity \(energy\)/i)).toBeInTheDocument();
    expect(screen.getByText(/scrap_metal \(waste\)/i)).toBeInTheDocument();
    expect(screen.getByText(/450 kg CO2e/i)).toBeInTheDocument();
    expect(screen.getByText(/score: 91.20/i)).toBeInTheDocument();
    expect(screen.getByText(/score: 82.50/i)).toBeInTheDocument();

    // First rendered item should be the highest-scored recommendation, since
    // this component trusts the backend's score-descending ordering.
    expect(items[0]).toHaveTextContent("Switch to renewable electricity");
    expect(items[1]).toHaveTextContent("Recycle scrap metal instead of landfilling");
  });
});
