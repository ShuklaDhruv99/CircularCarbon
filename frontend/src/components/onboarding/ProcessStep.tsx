import { useState } from "react";
import type { ProcessCreate } from "../../types/domain";
import Button from "../ui/Button";
import TextField from "../ui/TextField";
import SelectField from "../ui/SelectField";

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

  const processTypeOptions = [
    { value: "Assembly", label: "Assembly" },
    { value: "Cutting & Machining", label: "Cutting & machining" },
    { value: "Smelting & Casting", label: "Smelting & casting" },
    { value: "Weaving & Dyeing", label: "Weaving & dyeing" },
    { value: "Food Preparation", label: "Food preparation" },
    { value: "Chemical Processing", label: "Chemical processing" },
    { value: "Finishing", label: "Finishing" },
    { value: "Packaging", label: "Packaging" },
    { value: "Other", label: "Other" },
  ];

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
      <div className="onboarding-step-heading"><div><span className="eyebrow">Step 2 / Production</span><h2 className="text-xl font-semibold text-text">What happens on your main production line?</h2><p>Choose the closest process type. You can add more detail in the next steps.</p></div><span className="onboarding-time">≈ 1 min</span></div>

      {error && <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>}

      <TextField
        label="Process Name"
        name="process_name"
        value={name}
        onChange={setName}
        required
        error={nameError}
        placeholder="e.g. Main assembly line"
        helpText="Required — use the name your team uses internally."
      />
      <SelectField
        label="Process Type"
        name="process_type"
        value={processType}
        onChange={setProcessType}
        options={processTypeOptions}
        placeholder="Choose a process type"
      />
      <TextField
        label="Production Volume"
        name="process_production_volume"
        type="number"
        value={productionVolume}
        onChange={setProductionVolume}
        placeholder="Optional — e.g. 1200"
        helpText="Optional — output attributable to this process."
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
