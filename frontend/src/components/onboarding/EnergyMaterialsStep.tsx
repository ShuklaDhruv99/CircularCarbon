import { useState } from "react";
import type { EnergyConsumptionCreate, EnergyType, MaterialCreate } from "../../types/domain";
import Button from "../ui/Button";
import TextField from "../ui/TextField";
import SelectField from "../ui/SelectField";

type EnergyRowDraft = Omit<EnergyConsumptionCreate, "process_id">;
type MaterialRowDraft = Omit<MaterialCreate, "process_id">;

interface EnergyRowState {
  energy_type: string;
  quantity: string;
  unit: string;
  period: string;
}

interface MaterialRowState {
  material_name: string;
  quantity: string;
  unit: string;
  recycled_percentage: string;
  source: string;
}

interface EnergyMaterialsStepProps {
  onSubmit: (energyRows: EnergyRowDraft[], materialRows: MaterialRowDraft[]) => Promise<void>;
  onBack: () => void;
  isSubmitting: boolean;
  error: string | null;
}

const ENERGY_TYPE_OPTIONS: { value: EnergyType; label: string }[] = [
  { value: "electricity", label: "Electricity" },
  { value: "natural_gas", label: "Natural Gas" },
  { value: "diesel", label: "Diesel" },
  { value: "coal", label: "Coal" },
  { value: "renewable_electricity", label: "Renewable Electricity" },
  { value: "other", label: "Other" },
];

const EMPTY_ENERGY_ROW: EnergyRowState = { energy_type: "", quantity: "", unit: "", period: "" };
const EMPTY_MATERIAL_ROW: MaterialRowState = {
  material_name: "",
  quantity: "",
  unit: "",
  recycled_percentage: "",
  source: "",
};

function isEnergyRowBlank(row: EnergyRowState): boolean {
  return !row.energy_type && !row.quantity.trim() && !row.unit.trim() && !row.period.trim();
}

function isMaterialRowBlank(row: MaterialRowState): boolean {
  return (
    !row.material_name.trim() &&
    !row.quantity.trim() &&
    !row.unit.trim() &&
    !row.recycled_percentage.trim() &&
    !row.source.trim()
  );
}

function EnergyMaterialsStep({ onSubmit, onBack, isSubmitting, error }: EnergyMaterialsStepProps) {
  const [energyRows, setEnergyRows] = useState<EnergyRowState[]>([]);
  const [materialRows, setMaterialRows] = useState<MaterialRowState[]>([]);
  const [energyErrors, setEnergyErrors] = useState<Record<number, string>>({});
  const [materialErrors, setMaterialErrors] = useState<Record<number, string>>({});

  function updateEnergyRow(index: number, patch: Partial<EnergyRowState>) {
    setEnergyRows((rows) => rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function updateMaterialRow(index: number, patch: Partial<MaterialRowState>) {
    setMaterialRows((rows) => rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function removeEnergyRow(index: number) {
    setEnergyRows((rows) => rows.filter((_, i) => i !== index));
  }

  function removeMaterialRow(index: number) {
    setMaterialRows((rows) => rows.filter((_, i) => i !== index));
  }

  function handleSubmit() {
    const nextEnergyErrors: Record<number, string> = {};
    const nextMaterialErrors: Record<number, string> = {};
    const validEnergyRows: EnergyRowDraft[] = [];
    const validMaterialRows: MaterialRowDraft[] = [];

    energyRows.forEach((row, index) => {
      if (isEnergyRowBlank(row)) return;
      const quantity = Number(row.quantity);
      if (!row.energy_type || !row.unit.trim() || !row.period.trim() || !row.quantity.trim()) {
        nextEnergyErrors[index] = "All fields are required for this entry.";
        return;
      }
      if (!(quantity > 0)) {
        nextEnergyErrors[index] = "Quantity must be greater than 0.";
        return;
      }
      validEnergyRows.push({
        energy_type: row.energy_type as EnergyType,
        quantity,
        unit: row.unit.trim(),
        period: row.period.trim(),
      });
    });

    materialRows.forEach((row, index) => {
      if (isMaterialRowBlank(row)) return;
      const quantity = Number(row.quantity);
      if (!row.material_name.trim() || !row.unit.trim() || !row.quantity.trim()) {
        nextMaterialErrors[index] = "Material name, quantity, and unit are required for this entry.";
        return;
      }
      if (!(quantity > 0)) {
        nextMaterialErrors[index] = "Quantity must be greater than 0.";
        return;
      }
      let recycledPercentage: number | undefined;
      if (row.recycled_percentage.trim()) {
        recycledPercentage = Number(row.recycled_percentage);
        if (recycledPercentage < 0 || recycledPercentage > 100) {
          nextMaterialErrors[index] = "Recycled percentage must be between 0 and 100.";
          return;
        }
      }
      validMaterialRows.push({
        material_name: row.material_name.trim(),
        quantity,
        unit: row.unit.trim(),
        recycled_percentage: recycledPercentage,
        source: row.source.trim() ? row.source.trim() : undefined,
      });
    });

    setEnergyErrors(nextEnergyErrors);
    setMaterialErrors(nextMaterialErrors);

    if (Object.keys(nextEnergyErrors).length > 0 || Object.keys(nextMaterialErrors).length > 0) {
      return;
    }

    void onSubmit(validEnergyRows, validMaterialRows);
  }

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-text">Energy and materials used</h2>

      {error && <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>}

      <section className="flex flex-col gap-4">
        <h3 className="text-base font-semibold text-text">Energy Entries</h3>
        {energyRows.map((row, index) => (
          <div key={index} className="flex flex-col gap-3 rounded-md border border-border p-4">
            <SelectField
              label="Energy Type"
              name={`energy_type_${index}`}
              value={row.energy_type}
              onChange={(value) => updateEnergyRow(index, { energy_type: value })}
              options={ENERGY_TYPE_OPTIONS}
              placeholder="Select energy type"
            />
            <TextField
              label="Quantity"
              name={`energy_quantity_${index}`}
              type="number"
              value={row.quantity}
              onChange={(value) => updateEnergyRow(index, { quantity: value })}
            />
            <TextField
              label="Unit"
              name={`energy_unit_${index}`}
              value={row.unit}
              onChange={(value) => updateEnergyRow(index, { unit: value })}
              placeholder="e.g. kWh, liters"
            />
            <TextField
              label="Period"
              name={`energy_period_${index}`}
              value={row.period}
              onChange={(value) => updateEnergyRow(index, { period: value })}
              placeholder="e.g. Monthly, 2025 Q1"
            />
            {energyErrors[index] && <p className="text-xs text-danger">{energyErrors[index]}</p>}
            <div className="flex justify-end">
              <Button type="button" variant="ghost" onClick={() => removeEnergyRow(index)}>
                Remove
              </Button>
            </div>
          </div>
        ))}
        <div>
          <Button
            type="button"
            variant="secondary"
            onClick={() => setEnergyRows((rows) => [...rows, { ...EMPTY_ENERGY_ROW }])}
          >
            Add energy entry
          </Button>
        </div>
      </section>

      <section className="flex flex-col gap-4">
        <h3 className="text-base font-semibold text-text">Material Entries</h3>
        {materialRows.map((row, index) => (
          <div key={index} className="flex flex-col gap-3 rounded-md border border-border p-4">
            <TextField
              label="Material Name"
              name={`material_name_${index}`}
              value={row.material_name}
              onChange={(value) => updateMaterialRow(index, { material_name: value })}
            />
            <TextField
              label="Quantity"
              name={`material_quantity_${index}`}
              type="number"
              value={row.quantity}
              onChange={(value) => updateMaterialRow(index, { quantity: value })}
            />
            <TextField
              label="Unit"
              name={`material_unit_${index}`}
              value={row.unit}
              onChange={(value) => updateMaterialRow(index, { unit: value })}
              placeholder="e.g. kg, tonnes"
            />
            <TextField
              label="Recycled Percentage"
              name={`material_recycled_percentage_${index}`}
              type="number"
              value={row.recycled_percentage}
              onChange={(value) => updateMaterialRow(index, { recycled_percentage: value })}
              helpText="Optional — 0 to 100."
            />
            <TextField
              label="Source"
              name={`material_source_${index}`}
              value={row.source}
              onChange={(value) => updateMaterialRow(index, { source: value })}
              helpText="Optional — supplier or origin."
            />
            {materialErrors[index] && <p className="text-xs text-danger">{materialErrors[index]}</p>}
            <div className="flex justify-end">
              <Button type="button" variant="ghost" onClick={() => removeMaterialRow(index)}>
                Remove
              </Button>
            </div>
          </div>
        ))}
        <div>
          <Button
            type="button"
            variant="secondary"
            onClick={() => setMaterialRows((rows) => [...rows, { ...EMPTY_MATERIAL_ROW }])}
          >
            Add material entry
          </Button>
        </div>
      </section>

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

export default EnergyMaterialsStep;
