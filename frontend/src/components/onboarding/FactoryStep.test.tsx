import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import FactoryStep from "./FactoryStep";

describe("FactoryStep", () => {
  it("blocks submission and shows an error when name is missing", async () => {
    const onSubmit = vi.fn();
    render(<FactoryStep onSubmit={onSubmit} isSubmitting={false} error={null} />);
    await userEvent.click(screen.getByRole("button", { name: /continue/i }));
    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByText(/name is required/i)).toBeInTheDocument();
  });

  it("calls onSubmit with the entered data when required fields are filled", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<FactoryStep onSubmit={onSubmit} isSubmitting={false} error={null} />);
    await userEvent.type(screen.getByLabelText(/factory name/i), "Acme Steel");
    await userEvent.selectOptions(screen.getByLabelText(/industry/i), "Metal Manufacturing");
    await userEvent.click(screen.getByRole("button", { name: /continue/i }));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ name: "Acme Steel", industry: "Metal Manufacturing" }),
    );
  });
});
