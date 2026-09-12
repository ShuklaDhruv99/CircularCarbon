import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ReportDownloadButton from "./ReportDownloadButton";

describe("ReportDownloadButton", () => {
  it("renders an enabled download link pointing at the report endpoint when emissions are calculated", () => {
    render(<ReportDownloadButton factoryId={7} hasCalculatedEmissions />);

    const link = screen.getByRole("link", { name: /download report/i });
    expect(link).toHaveAttribute("href", expect.stringContaining("/api/report/factory/7"));
    expect(link).toHaveAttribute("download");
  });

  it("renders a disabled state with no functioning download link when emissions are not calculated", () => {
    render(<ReportDownloadButton factoryId={7} hasCalculatedEmissions={false} />);

    expect(screen.queryByRole("link", { name: /download report/i })).not.toBeInTheDocument();
    expect(screen.getByText(/download report/i)).toBeInTheDocument();
  });
});
