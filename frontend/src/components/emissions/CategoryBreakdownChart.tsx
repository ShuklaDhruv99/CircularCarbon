import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { CategoryBreakdown } from "../../types/domain";

interface CategoryBreakdownChartProps {
  categories: CategoryBreakdown[];
}

const CATEGORY_COLORS: Record<string, string> = {
  energy: "#126B5A",
  materials: "#20A67A",
  waste: "#D79520",
};

// Backend supplies co2e/percentage as Decimal-backed strings; parse to Number
// here only for chart rendering, never to recompute any value.
function CategoryBreakdownChart({ categories }: CategoryBreakdownChartProps) {
  if (categories.length === 0) {
    return <p className="text-sm text-muted">No category data available.</p>;
  }

  const data = categories.map((category) => ({
    category: category.category,
    co2e: Number(category.co2e),
    percentage: category.percentage,
  }));

  return (
    <div className="h-64 w-full" data-testid="category-breakdown-chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#DCE4E0" />
          <XAxis dataKey="category" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} label={{ value: "kg CO2e", angle: -90, position: "insideLeft" }} />
          <Tooltip
            formatter={(value) => [`${Number(value).toLocaleString()} kg CO2e`, "CO2e"]}
            labelFormatter={(label) => `Category: ${label}`}
          />
          <Bar dataKey="co2e" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.category} fill={CATEGORY_COLORS[entry.category] ?? "#126B5A"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default CategoryBreakdownChart;
