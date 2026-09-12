import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getFactory } from "../services/onboarding";
import type { Factory } from "../types/domain";

// The backend returns Decimal-backed fields (quantity, production_volume, ...)
// as full-precision strings like "100000.0000000000" — trim that down to a
// plain, human-readable number for display.
function formatDecimal(value: string | undefined): string | undefined {
  if (value === undefined) return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString() : value;
}

function OnboardingComplete() {
  const { factoryId } = useParams<{ factoryId: string }>();
  const [factory, setFactory] = useState<Factory | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!factoryId) return;
    getFactory(Number(factoryId))
      .then((result) => setFactory(result))
      .catch(() => setError("Unable to load the saved factory data."));
  }, [factoryId]);

  if (error) {
    return (
      <div className="mx-auto flex min-h-screen max-w-2xl flex-col gap-4 bg-background px-4 py-10">
        <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>
        <Link to="/" className="text-primary underline">
          Back to home
        </Link>
      </div>
    );
  }

  if (!factory) {
    return (
      <div className="mx-auto flex min-h-screen max-w-2xl flex-col gap-4 bg-background px-4 py-10">
        <p className="text-muted">Loading saved data...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col gap-8 bg-background px-4 py-10">
      <h1 className="text-2xl font-semibold text-text">Assessment data saved</h1>

      <section className="flex flex-col gap-2 rounded-md border border-border bg-surface p-4">
        <h2 className="text-lg font-semibold text-text">Factory</h2>
        <p className="text-sm text-text">Name: {factory.name}</p>
        <p className="text-sm text-text">Industry: {factory.industry}</p>
        {factory.location && <p className="text-sm text-text">Location: {factory.location}</p>}
        {factory.production_volume !== undefined && (
          <p className="text-sm text-text">
            Production Volume: {formatDecimal(factory.production_volume)} {factory.production_unit ?? ""}
          </p>
        )}
        {factory.assessment_period && (
          <p className="text-sm text-text">Assessment Period: {factory.assessment_period}</p>
        )}
      </section>

      {factory.processes.map((process) => (
        <section key={process.id} className="flex flex-col gap-4 rounded-md border border-border bg-surface p-4">
          <h2 className="text-lg font-semibold text-text">Process: {process.name}</h2>
          {process.process_type && <p className="text-sm text-text">Type: {process.process_type}</p>}
          {process.production_volume !== undefined && (
            <p className="text-sm text-text">Production Volume: {formatDecimal(process.production_volume)}</p>
          )}

          <div>
            <h3 className="text-sm font-semibold text-text">Energy Consumption</h3>
            {process.energy_consumption.length === 0 ? (
              <p className="text-sm text-muted">No energy entries recorded.</p>
            ) : (
              <ul className="list-disc pl-5 text-sm text-text">
                {process.energy_consumption.map((entry) => (
                  <li key={entry.id}>
                    {entry.energy_type}: {formatDecimal(entry.quantity)} {entry.unit} ({entry.period})
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <h3 className="text-sm font-semibold text-text">Materials</h3>
            {process.materials.length === 0 ? (
              <p className="text-sm text-muted">No material entries recorded.</p>
            ) : (
              <ul className="list-disc pl-5 text-sm text-text">
                {process.materials.map((entry) => (
                  <li key={entry.id}>
                    {entry.material_name}: {formatDecimal(entry.quantity)} {entry.unit}
                    {entry.recycled_percentage !== undefined
                      ? ` (${formatDecimal(entry.recycled_percentage)}% recycled)`
                      : ""}
                    {entry.source ? ` — source: ${entry.source}` : ""}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <h3 className="text-sm font-semibold text-text">Waste</h3>
            {process.waste.length === 0 ? (
              <p className="text-sm text-muted">No waste entries recorded.</p>
            ) : (
              <ul className="list-disc pl-5 text-sm text-text">
                {process.waste.map((entry) => (
                  <li key={entry.id}>
                    {entry.waste_type}: {formatDecimal(entry.quantity)} {entry.unit} — {entry.disposal_method}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      ))}

      {factoryId && (
        <Link
          to={`/factories/${factoryId}/emissions`}
          className="w-fit rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
        >
          View emissions dashboard
        </Link>
      )}

      <Link to="/" className="text-primary underline">
        Back to home
      </Link>
    </div>
  );
}

export default OnboardingComplete;
