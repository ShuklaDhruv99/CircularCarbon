import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ExplanationPanel from "./ExplanationPanel";
import type { Explanation } from "../../types/domain";

const explanation: Explanation = {
  recommendation_id: 1,
  why: "Electricity is the largest hotspot at 62% of total emissions.",
  what_to_do: "Switch to a renewable electricity contract for the main production line.",
  expected_benefit: "Reduces emissions by 450.00 kg CO2e based on the recommendation's estimate.",
  assumptions: "Assumes the renewable contract has a lower emission factor than the grid mix.",
  source: "gemini",
};

describe("ExplanationPanel", () => {
  it("renders the four labeled sections from the explanation", () => {
    render(<ExplanationPanel explanation={explanation} />);

    expect(screen.getByText("Why")).toBeInTheDocument();
    expect(screen.getByText(explanation.why)).toBeInTheDocument();

    expect(screen.getByText("What to do")).toBeInTheDocument();
    expect(screen.getByText(explanation.what_to_do)).toBeInTheDocument();

    expect(screen.getByText("Expected benefit")).toBeInTheDocument();
    expect(screen.getByText(explanation.expected_benefit)).toBeInTheDocument();

    expect(screen.getByText("Assumptions")).toBeInTheDocument();
    expect(screen.getByText(explanation.assumptions)).toBeInTheDocument();
  });

  it("shows a loading state when isLoading is true", () => {
    render(<ExplanationPanel isLoading />);
    expect(screen.getByText(/loading explanation/i)).toBeInTheDocument();
  });

  it("shows an error message when error is set", () => {
    render(<ExplanationPanel error="Unable to generate explanations." />);
    expect(screen.getByRole("alert")).toHaveTextContent("Unable to generate explanations.");
  });

  it("renders nothing when there is no explanation, loading, or error", () => {
    const { container } = render(<ExplanationPanel />);
    expect(container).toBeEmptyDOMElement();
  });
});
