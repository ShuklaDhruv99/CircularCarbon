import { useState } from "react";
import type { ProcessCreate } from "../../types/domain";
import Button from "../ui/Button";
import TextField from "../ui/TextField";

interface ProcessStepProps {
  onSubmit: (draft: Omit<ProcessCreate, "factory_id">) => Promise<void>;
  onBack: () => void;
  isSubmitting: boolean;
  error: string | null;
}

function ProcessStep({ onSubmit, onBack, isSubmitting, error }: ProcessStepProps) {
  const [name, setName] = useState("");
  const [processType, setProcessType] = useState("");
  const [productionVolume, setProductionVolume] = useState("");
  const [nameError, setNameError] = useState<string | undefined>();

  function handleSubmit() {
    if (!name.trim()) {
      setNameError("Name is required.");
      return;
    }
    setNameError(undefined);

    const draft: Omit<ProcessCreate, "factory_id"> = {
      name: name.trim(),
      process_type: processType.trim() ? processType.trim() : undefined,
      production_volume: productionVolume.trim() ? Number(productionVolume) : undefined,
    };
    void onSubmit(draft);
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold text-text">Describe your main production process</h2>

      {error && <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>}

      <TextField
        label="Process Name"
        name="process_name"
        value={name}
        onChange={setName}
        required
        error={nameError}
        helpText="E.g. Smelting, Weaving, Packaging."
      />
      <TextField
        label="Process Type"
        name="process_type"
        value={processType}
        onChange={setProcessType}
        helpText="Optional — category or classification of this process."
      />
      <TextField
        label="Production Volume"
        name="process_production_volume"
        type="number"
        value={productionVolume}
        onChange={setProductionVolume}
        helpText="Optional — output volume attributable to this process."
      />

      <div className="flex justify-between">
        <Button type="button" variant="ghost" onClick={onBack} disabled={isSubmitting}>
          Back
        </Button>
        <Button type="button" onClick={handleSubmit} isLoading={isSubmitting}>
          Continue
        </Button>
      </div>
    </div>
  );
}

export default ProcessStep;
