import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SimulationPanel from "./SimulationPanel";
import type { SimulationResult } from "../../types/domain";

const result: SimulationResult = {
  factory_id: 1,
  baseline_co2e: "1000.00",
  projected_co2e: "550.00",
  co2_reduction: "450.00",
  reduction_percentage: "45.00",
  total_implementation_cost: "200000.00",
  estimated_payback_months: "18.00",
  applied_recommendations: [
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
  ],
};

describe("SimulationPanel", () => {
  it("renders a Run What-If Simulation button that calls onRun", async () => {
    render(<SimulationPanel result={null} onRun={vi.fn()} />);
    const button = screen.getByRole("button", { name: /run what-if simulation/i });
    expect(button).toBeInTheDocument();
  });

  it("calls onRun when the button is clicked", async () => {
    const onRun = vi.fn();
    render(<SimulationPanel result={null} onRun={onRun} />);
    await userEvent.click(screen.getByRole("button", { name: /run what-if simulation/i }));
    expect(onRun).toHaveBeenCalledTimes(1);
  });

  it("shows a loading state", () => {
    render(<SimulationPanel result={null} isLoading onRun={vi.fn()} />);
    expect(screen.getByRole("button", { name: /simulating/i })).toBeDisabled();
  });

  it("shows an error message", () => {
    render(<SimulationPanel result={null} error="Unable to run simulation." onRun={vi.fn()} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Unable to run simulation.");
  });

  it("renders before/after CO2e, reduction, cost, payback, and applied recommendations", () => {
    render(<SimulationPanel result={result} onRun={vi.fn()} />);

    expect(screen.getByText(/1,000 kg/i)).toBeInTheDocument();
    expect(screen.getByText(/550 kg/i)).toBeInTheDocument();
    expect(screen.getByText(/450 kg \(45%\)/i)).toBeInTheDocument();
    const costValue = screen.getByText("Implementation Cost").nextElementSibling?.textContent ?? "";
    expect(costValue.replace(/,/g, "")).toBe("200000");
    expect(screen.getByText(/18 months/i)).toBeInTheDocument();
    expect(screen.getByText("Switch to renewable electricity")).toBeInTheDocument();
  });
});
