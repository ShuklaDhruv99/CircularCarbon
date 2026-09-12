import type { Hotspot } from "../../types/domain";

interface HotspotListProps {
  hotspots: Hotspot[];
}

function formatCo2e(value: string): string {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString(undefined, { maximumFractionDigits: 2 }) : value;
}

// Ranked list of emission results (highest CO2e first, as returned by the
// backend), visually flagging rows the backend marked as hotspots
// (cumulative contribution up to ~80% of factory total).
function HotspotList({ hotspots }: HotspotListProps) {
  if (hotspots.length === 0) {
    return <p className="text-sm text-muted">No emission results available.</p>;
  }

  return (
    <ol className="flex flex-col gap-2">
      {hotspots.map((hotspot) => (
        <li
          key={hotspot.id}
          data-testid={`hotspot-row-${hotspot.id}`}
          data-hotspot={hotspot.is_hotspot}
          className={`flex items-center justify-between gap-4 rounded-md border p-3 text-sm ${
            hotspot.is_hotspot
              ? "border-danger bg-red-50 text-text"
              : "border-border bg-surface text-text"
          }`}
        >
          <div className="flex flex-col">
            <span className="font-semibold">
              {hotspot.is_hotspot && <span className="mr-2 text-danger">Hotspot</span>}
              {hotspot.activity} ({hotspot.category})
            </span>
            <span className="text-xs text-muted">Period: {hotspot.period}</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="font-semibold">{formatCo2e(hotspot.co2e)} kg CO2e</span>
            <span className="text-xs text-muted">{hotspot.percentage}% of total</span>
          </div>
        </li>
      ))}
    </ol>
  );
}

export default HotspotList;
