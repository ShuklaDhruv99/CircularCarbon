import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getFactory } from "../services/onboarding";
import type { Factory } from "../types/domain";
import { rememberFactory } from "../services/persistence";

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
      .then((result) => { rememberFactory(result); setFactory(result); })
      .catch(() => setError("Unable to load the saved factory data."));
  }, [factoryId]);

  if (error) {
    return (
      <div className="app-shell page-frame py-10">
        <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>
        <Link to="/" className="text-primary underline">
          Back to home
        </Link>
      </div>
    );
  }

  if (!factory) {
    return (
      <div className="app-shell page-frame py-10">
        <p className="text-muted">Loading saved data...</p>
      </div>
    );
  }

  return (
    <div className="completion-page"><header className="wizard-nav"><div className="page-frame wizard-nav-inner"><Link to="/" className="brand"><span className="brand-mark" />CircularCarbon</Link><span className="nav-status"><span className="status-dot" />Assessment complete</span></div></header><main className="page-frame completion-main">
      <div className="completion-hero"><div><div className="eyebrow">Baseline created / 04</div><h1>Your facility is ready to be measured.</h1><p>Your operating context is saved. Next, turn the baseline into a ranked emissions view and a practical action plan.</p></div><div className="completion-check">✓<span>Saved</span></div></div>
      <div className="completion-summary"><div><span>FACILITY</span><strong>{factory.name}</strong></div><div><span>INDUSTRY</span><strong>{factory.industry}</strong></div><div><span>PROCESSES</span><strong>{factory.processes.length}</strong></div><div><span>STATUS</span><strong className="completion-live">Ready to calculate</strong></div></div>

      <section className="form-card completion-details" style={{ marginBottom: 16 }}>
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
        <section key={process.id} className="form-card completion-details" style={{ marginBottom: 16 }}>
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

      <div className="completion-actions">
      {factoryId && (
        <Link
          to={`/factories/${factoryId}/emissions`}
          className="primary-btn"
        >
          View emissions dashboard
        </Link>
      )}

      <Link to="/" className="secondary-btn">
        Back to home
      </Link>
      </div>
    </main></div>
  );
}

export default OnboardingComplete;
