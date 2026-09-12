import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import StepIndicator from "./StepIndicator";

describe("StepIndicator", () => {
  it("marks the current step as active, earlier as complete, later as upcoming", () => {
    render(<StepIndicator currentStep={2} />);
    expect(screen.getByTestId("step-2")).toHaveAttribute("data-status", "current");
    expect(screen.getByTestId("step-1")).toHaveAttribute("data-status", "complete");
    expect(screen.getByTestId("step-3")).toHaveAttribute("data-status", "upcoming");
    expect(screen.getByTestId("step-4")).toHaveAttribute("data-status", "upcoming");
  });
});
