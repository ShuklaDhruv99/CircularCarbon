import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import EmissionsDashboard from "./EmissionsDashboard";
import { ApiError } from "../services/api";
import * as emissionsService from "../services/emissions";
import type { EmissionsBreakdown, Hotspot } from "../types/domain";

vi.mock("../services/emissions");

const breakdown: EmissionsBreakdown = {
  factory_id: 1,
  factory_total_co2e: "1000.00",
  category_breakdown: [
    { category: "energy", co2e: "600.00", percentage: "60.00" },
    { category: "materials", co2e: "300.00", percentage: "30.00" },
    { category: "waste", co2e: "100.00", percentage: "10.00" },
  ],
  process_breakdown: [{ process_id: 1, process_name: "Smelting", co2e: "1000.00", percentage: "100.00" }],
  results: [],
};

const hotspots: Hotspot[] = [
  {
    id: 1,
    process_id: 1,
    category: "energy",
    activity: "electricity",
    emission_factor: "0.5",
    emission_factor_source: "EPA",
    co2e: "600.00",
    period: "2024",
    created_at: "2024-01-01T00:00:00Z",
    percentage: "60.00",
    is_hotspot: true,
  },
];

function renderDashboard() {
  return render(
    <MemoryRouter initialEntries={["/factories/1/emissions"]}>
      <Routes>
        <Route path="/factories/:factoryId/emissions" element={<EmissionsDashboard />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("EmissionsDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows a loading state while fetching data", () => {
    vi.mocked(emissionsService.getFactoryEmissions).mockReturnValue(new Promise(() => {}));
    vi.mocked(emissionsService.getHotspots).mockReturnValue(new Promise(() => {}));
    renderDashboard();
    expect(screen.getByText(/loading emissions data/i)).toBeInTheDocument();
  });

  it("prompts to calculate when emissions have not been calculated yet, and calculates on click", async () => {
    vi.mocked(emissionsService.getFactoryEmissions).mockRejectedValueOnce(new ApiError("not found", 404));
    vi.mocked(emissionsService.getHotspots).mockRejectedValueOnce(new ApiError("not found", 404));
    vi.mocked(emissionsService.calculateEmissions).mockResolvedValue(breakdown);
    vi.mocked(emissionsService.getFactoryEmissions).mockResolvedValueOnce(breakdown);
    vi.mocked(emissionsService.getHotspots).mockResolvedValueOnce(hotspots);

    renderDashboard();

    expect(await screen.findByText(/emissions not yet calculated/i)).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /calculate emissions/i }));

    await waitFor(() => {
      expect(emissionsService.calculateEmissions).toHaveBeenCalledWith(1);
    });
    expect(await screen.findByText(/total emissions/i)).toBeInTheDocument();
  });

  it("renders breakdown and hotspot data once available", async () => {
    vi.mocked(emissionsService.getFactoryEmissions).mockResolvedValue(breakdown);
    vi.mocked(emissionsService.getHotspots).mockResolvedValue(hotspots);

    renderDashboard();

    expect(await screen.findAllByText(/1,000/)).not.toHaveLength(0);
    expect(screen.getByText("Smelting")).toBeInTheDocument();
    expect(screen.getByText(/electricity \(energy\)/i)).toBeInTheDocument();
    expect(screen.getByTestId("hotspot-row-1")).toHaveAttribute("data-hotspot", "true");
  });

  it("refreshes data when Recalculate is clicked", async () => {
    vi.mocked(emissionsService.getFactoryEmissions).mockResolvedValue(breakdown);
    vi.mocked(emissionsService.getHotspots).mockResolvedValue(hotspots);
    vi.mocked(emissionsService.calculateEmissions).mockResolvedValue(breakdown);

    renderDashboard();

    await screen.findByText(/total emissions/i);

    await userEvent.click(screen.getByRole("button", { name: /recalculate/i }));

    await waitFor(() => {
      expect(emissionsService.calculateEmissions).toHaveBeenCalledWith(1);
    });
    expect(emissionsService.getFactoryEmissions).toHaveBeenCalledTimes(2);
  });
});
