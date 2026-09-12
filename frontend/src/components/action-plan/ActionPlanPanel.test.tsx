import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ActionPlanPanel from "./ActionPlanPanel";
import type { ActionPlan, Recommendation } from "../../types/domain";

function makeRecommendation(overrides: Partial<Recommendation>): Recommendation {
  return {
    id: 1,
    hotspot_id: 10,
    hotspot_category: "energy",
    hotspot_activity: "electricity",
    title: "Switch to renewable electricity",
    description: "Replace grid electricity with a renewable energy contract.",
    strategy: "substitute",
    estimated_cost: "low",
    co2_reduction: "450.00",
    payback_period: "6",
    score: "82.50",
    created_at: "2024-01-01T00:00:00Z",
    ...overrides,
  };
}

const plan: ActionPlan = {
  factory_id: 1,
  now: {
    phase: "now",
    recommendations: [makeRecommendation({ id: 1, title: "Switch to renewable electricity" })],
    total_co2_reduction: "450.00",
    total_implementation_cost: "50000.00",
  },
  next: {
    phase: "next",
    recommendations: [makeRecommendation({ id: 2, title: "Install waste heat recovery" })],
    total_co2_reduction: "300.00",
    total_implementation_cost: "150000.00",
  },
  later: {
    phase: "later",
    recommendations: [],
    total_co2_reduction: "0.00",
    total_implementation_cost: "0.00",
  },
};

describe("ActionPlanPanel", () => {
  it("renders a Generate Action Plan button that calls onGenerate", async () => {
    const onGenerate = vi.fn();
    render(<ActionPlanPanel plan={null} onGenerate={onGenerate} />);
    await userEvent.click(screen.getByRole("button", { name: /generate action plan/i }));
    expect(onGenerate).toHaveBeenCalledTimes(1);
  });

  it("shows a loading state", () => {
    render(<ActionPlanPanel plan={null} isLoading onGenerate={vi.fn()} />);
    expect(screen.getByRole("button", { name: /generating/i })).toBeDisabled();
  });

  it("shows an error message", () => {
    render(<ActionPlanPanel plan={null} error="Unable to generate action plan." onGenerate={vi.fn()} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Unable to generate action plan.");
  });

  it("renders three phase sections with recommendation titles and phase totals", () => {
    render(<ActionPlanPanel plan={plan} onGenerate={vi.fn()} />);

    expect(screen.getByText(/now \(0-3 months\)/i)).toBeInTheDocument();
    expect(screen.getByText(/next \(3-12 months\)/i)).toBeInTheDocument();
    expect(screen.getByText(/later \(12\+ months\)/i)).toBeInTheDocument();

    expect(screen.getByText("Switch to renewable electricity")).toBeInTheDocument();
    expect(screen.getByText("Install waste heat recovery")).toBeInTheDocument();
    expect(screen.getByText(/no recommendations in this phase/i)).toBeInTheDocument();

    const nowSection = screen.getByTestId("action-plan-phase-now");
    expect(nowSection).toHaveTextContent("450");
    expect(nowSection).toHaveTextContent("50,000");
  });
});
