import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import WasteStep from "./WasteStep";

describe("WasteStep", () => {
  it("maps the 'Landfilled' radio selection to the 'landfilled' enum value on submit", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<WasteStep onSubmit={onSubmit} onBack={vi.fn()} isSubmitting={false} error={null} />);
    await userEvent.click(screen.getByRole("button", { name: /add waste entry/i }));
    await userEvent.type(screen.getAllByLabelText(/waste type/i)[0], "Scrap metal");
    await userEvent.type(screen.getAllByLabelText(/quantity/i)[0], "10");
    await userEvent.type(screen.getAllByLabelText(/unit/i)[0], "kg");
    await userEvent.click(screen.getByLabelText(/landfilled/i));
    await userEvent.click(screen.getByRole("button", { name: /finish/i }));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.arrayContaining([expect.objectContaining({ disposal_method: "landfilled" })]),
    );
  });

  it("rejects a non-positive quantity without calling onSubmit", async () => {
    const onSubmit = vi.fn();
    render(<WasteStep onSubmit={onSubmit} onBack={vi.fn()} isSubmitting={false} error={null} />);
    await userEvent.click(screen.getByRole("button", { name: /add waste entry/i }));
    await userEvent.type(screen.getAllByLabelText(/waste type/i)[0], "Scrap");
    await userEvent.type(screen.getAllByLabelText(/quantity/i)[0], "0");
    await userEvent.click(screen.getByLabelText(/other/i));
    await userEvent.click(screen.getByRole("button", { name: /finish/i }));
    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByText(/quantity must be greater than 0/i)).toBeInTheDocument();
  });
});
