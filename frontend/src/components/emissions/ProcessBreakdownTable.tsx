import type { ProcessBreakdown } from "../../types/domain";

interface ProcessBreakdownTableProps {
  processes: ProcessBreakdown[];
}

// co2e/percentage arrive as Decimal-backed strings from the backend; parse to
// Number only for display formatting, never to recompute any value.
function formatCo2e(value: string): string {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString(undefined, { maximumFractionDigits: 2 }) : value;
}

function ProcessBreakdownTable({ processes }: ProcessBreakdownTableProps) {
  if (processes.length === 0) {
    return <p className="text-sm text-muted">No process data available.</p>;
  }

  return (
    <table className="w-full text-left text-sm text-text">
      <thead>
        <tr className="border-b border-border">
          <th className="py-2 font-semibold">Process</th>
          <th className="py-2 font-semibold">CO2e (kg)</th>
          <th className="py-2 font-semibold">% of total</th>
        </tr>
      </thead>
      <tbody>
        {processes.map((process) => (
          <tr key={process.process_id} className="border-b border-border last:border-0">
            <td className="py-2">{process.process_name}</td>
            <td className="py-2">{formatCo2e(process.co2e)}</td>
            <td className="py-2">{process.percentage}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default ProcessBreakdownTable;
