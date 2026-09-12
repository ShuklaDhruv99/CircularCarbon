import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../services/api";
import { rememberFactory } from "../services/persistence";
import {
  createEnergyEntry,
  createFactory,
  createMaterialEntry,
  createProcess,
  createWasteEntry,
} from "../services/onboarding";
import type {
  EnergyConsumptionCreate,
  FactoryCreate,
  MaterialCreate,
  ProcessCreate,
  WasteCreate,
} from "../types/domain";
import StepIndicator from "../components/onboarding/StepIndicator";
import FactoryStep from "../components/onboarding/FactoryStep";
import ProcessStep from "../components/onboarding/ProcessStep";
import EnergyMaterialsStep from "../components/onboarding/EnergyMaterialsStep";
import WasteStep from "../components/onboarding/WasteStep";

interface WizardState {
  step: 1 | 2 | 3 | 4;
  factoryId: number | null;
  processId: number | null;
}

function toErrorMessage(e: unknown): string {
  return e instanceof ApiError ? e.message : "Something went wrong. Please try again.";
}

function Onboarding() {
  const navigate = useNavigate();
  const [wizard, setWizard] = useState<WizardState>({ step: 1, factoryId: null, processId: null });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFactorySubmit(draft: FactoryCreate) {
    setIsSubmitting(true);
    setError(null);
    try {
      const factory = await createFactory(draft);
      rememberFactory(factory);
      setWizard((current) => ({ ...current, factoryId: factory.id, step: 2 }));
    } catch (e) {
      setError(toErrorMessage(e));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleProcessSubmit(draft: Omit<ProcessCreate, "factory_id">) {
    if (wizard.factoryId === null) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const process = await createProcess({ ...draft, factory_id: wizard.factoryId });
      setWizard((current) => ({ ...current, processId: process.id, step: 3 }));
    } catch (e) {
      setError(toErrorMessage(e));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleEnergyMaterialsSubmit(
    energyRows: Omit<EnergyConsumptionCreate, "process_id">[],
    materialRows: Omit<MaterialCreate, "process_id">[],
  ) {
    if (wizard.processId === null) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await Promise.all([
        ...energyRows.map((row) => createEnergyEntry({ ...row, process_id: wizard.processId as number })),
        ...materialRows.map((row) => createMaterialEntry({ ...row, process_id: wizard.processId as number })),
      ]);
      setWizard((current) => ({ ...current, step: 4 }));
    } catch (e) {
      setError(toErrorMessage(e));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleWasteSubmit(rows: Omit<WasteCreate, "process_id">[]) {
    if (wizard.processId === null || wizard.factoryId === null) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await Promise.all(
        rows.map((row) => createWasteEntry({ ...row, process_id: wizard.processId as number })),
      );
      navigate(`/onboarding/complete/${wizard.factoryId}`);
    } catch (e) {
      setError(toErrorMessage(e));
    } finally {
      setIsSubmitting(false);
    }
  }

  function goBack() {
    setError(null);
    setWizard((current) => ({ ...current, step: (Math.max(1, current.step - 1) as 1 | 2 | 3 | 4) }));
  }

  return (
    <div className="wizard-shell">
      <header className="wizard-nav"><div className="page-frame wizard-nav-inner"><Link to="/" className="brand"><span className="brand-mark" />CircularCarbon</Link><span className="nav-status"><span className="status-dot" />Secure assessment</span></div></header>
      <div className="page-frame wizard-layout">
        <aside className="wizard-aside"><div className="eyebrow">Factory assessment</div><div className="wizard-intro"><h1>Build your carbon baseline.</h1><p>A short guided intake turns your operating data into an actionable emissions model.</p></div><StepIndicator currentStep={wizard.step} /></aside>
        <main className="form-card">
          {wizard.step === 1 && <FactoryStep onSubmit={handleFactorySubmit} isSubmitting={isSubmitting} error={error} />}
          {wizard.step === 2 && <ProcessStep onSubmit={handleProcessSubmit} onBack={goBack} isSubmitting={isSubmitting} error={error} />}
          {wizard.step === 3 && <EnergyMaterialsStep onSubmit={handleEnergyMaterialsSubmit} onBack={goBack} isSubmitting={isSubmitting} error={error} />}
          {wizard.step === 4 && <WasteStep onSubmit={handleWasteSubmit} onBack={goBack} isSubmitting={isSubmitting} error={error} />}
        </main>
      </div>
    </div>
  );
}

export default Onboarding;
