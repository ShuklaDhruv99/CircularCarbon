import { useState } from "react";
import type { DisposalMethod, WasteCreate } from "../../types/domain";
import Button from "../ui/Button";
import TextField from "../ui/TextField";

type WasteRowDraft = Omit<WasteCreate, "process_id">;

interface WasteRowState {
  waste_type: string;
  quantity: string;
  unit: string;
  disposal_method: DisposalMethod | "";
  recycled_quantity: string;
  landfilled_quantity: string;
  reused_quantity: string;
}

interface WasteStepProps {
  onSubmit: (rows: WasteRowDraft[]) => Promise<void>;
  onBack: () => void;
  isSubmitting: boolean;
  error: string | null;
}

const DISPOSAL_OPTIONS: { value: DisposalMethod; label: string }[] = [
  { value: "reused", label: "Reused" },
  { value: "recycled", label: "Recycled" },
  { value: "sold", label: "Sold" },
  { value: "landfilled", label: "Landfilled" },
  { value: "other", label: "Other" },
];

const EMPTY_WASTE_ROW: WasteRowState = {
  waste_type: "",
  quantity: "",
  unit: "",
  disposal_method: "",
  recycled_quantity: "",
  landfilled_quantity: "",
  reused_quantity: "",
};

function isWasteRowBlank(row: WasteRowState): boolean {
  return (
    !row.waste_type.trim() &&
    !row.quantity.trim() &&
    !row.unit.trim() &&
    !row.disposal_method &&
    !row.recycled_quantity.trim() &&
    !row.landfilled_quantity.trim() &&
    !row.reused_quantity.trim()
  );
}

function WasteStep({ onSubmit, onBack, isSubmitting, error }: WasteStepProps) {
  const [rows, setRows] = useState<WasteRowState[]>([]);
  const [rowErrors, setRowErrors] = useState<Record<number, string>>({});

  function updateRow(index: number, patch: Partial<WasteRowState>) {
    setRows((current) => current.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function removeRow(index: number) {
    setRows((current) => current.filter((_, i) => i !== index));
  }

  function handleSubmit() {
    const nextErrors: Record<number, string> = {};
    const validRows: WasteRowDraft[] = [];

    rows.forEach((row, index) => {
      if (isWasteRowBlank(row)) return;

      const quantity = Number(row.quantity);
      if (!row.quantity.trim() || !(quantity > 0)) {
        nextErrors[index] = "Quantity must be greater than 0.";
        return;
      }
      if (!row.disposal_method) {
        nextErrors[index] = "Please select a disposal method.";
        return;
      }
      if (!row.waste_type.trim() || !row.unit.trim()) {
        nextErrors[index] = "Waste type and unit are required for this entry.";
        return;
      }

      validRows.push({
        waste_type: row.waste_type.trim(),
        quantity,
        unit: row.unit.trim(),
        disposal_method: row.disposal_method,
        recycled_quantity: row.recycled_quantity.trim() ? Number(row.recycled_quantity) : undefined,
        landfilled_quantity: row.landfilled_quantity.trim()
          ? Number(row.landfilled_quantity)
          : undefined,
        reused_quantity: row.reused_quantity.trim() ? Number(row.reused_quantity) : undefined,
      });
    });

    setRowErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    void onSubmit(validRows);
  }

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-text">Waste generated</h2>

      {error && <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>}

      {rows.map((row, index) => (
        <div key={index} className="flex flex-col gap-3 rounded-md border border-border p-4">
          <TextField
            label="Waste Type"
            name={`waste_type_${index}`}
            value={row.waste_type}
            onChange={(value) => updateRow(index, { waste_type: value })}
          />
          <TextField
            label="Quantity"
            name={`waste_quantity_${index}`}
            type="number"
            value={row.quantity}
            onChange={(value) => updateRow(index, { quantity: value })}
          />
          <TextField
            label="Unit"
            name={`waste_unit_${index}`}
            value={row.unit}
            onChange={(value) => updateRow(index, { unit: value })}
            placeholder="e.g. kg, tonnes"
          />

          <fieldset className="flex flex-col gap-2">
            <legend className="text-sm font-medium text-text">Disposal Method</legend>
            <div className="flex flex-wrap gap-4">
              {DISPOSAL_OPTIONS.map((option) => {
                const inputId = `disposal-method-${index}-${option.value}`;
                return (
                  <label key={option.value} htmlFor={inputId} className="flex items-center gap-2 text-sm text-text">
                    <input
                      id={inputId}
                      type="radio"
                      name={`disposal-method-${index}`}
                      value={option.value}
                      checked={row.disposal_method === option.value}
                      onChange={() => updateRow(index, { disposal_method: option.value })}
                    />
                    {option.label}
                  </label>
                );
              })}
            </div>
          </fieldset>

          <TextField
            label="Recycling Quantity"
            name={`waste_recycled_quantity_${index}`}
            type="number"
            value={row.recycled_quantity}
            onChange={(value) => updateRow(index, { recycled_quantity: value })}
            helpText="Optional."
          />
          <TextField
            label="Landfill Quantity"
            name={`waste_landfilled_quantity_${index}`}
            type="number"
            value={row.landfilled_quantity}
            onChange={(value) => updateRow(index, { landfilled_quantity: value })}
            helpText="Optional."
          />
          <TextField
            label="Reuse Quantity"
            name={`waste_reused_quantity_${index}`}
            type="number"
            value={row.reused_quantity}
            onChange={(value) => updateRow(index, { reused_quantity: value })}
            helpText="Optional."
          />

          {rowErrors[index] && <p className="text-xs text-danger">{rowErrors[index]}</p>}
          <div className="flex justify-end">
            <Button type="button" variant="ghost" onClick={() => removeRow(index)}>
              Remove
            </Button>
          </div>
        </div>
      ))}

      <div>
        <Button
          type="button"
          variant="secondary"
          onClick={() => setRows((current) => [...current, { ...EMPTY_WASTE_ROW }])}
        >
          Add waste entry
        </Button>
      </div>

      <div className="flex justify-between">
        <Button type="button" variant="ghost" onClick={onBack} disabled={isSubmitting}>
          Back
        </Button>
        <Button type="button" onClick={handleSubmit} isLoading={isSubmitting}>
          Finish
        </Button>
      </div>
    </div>
  );
}

export default WasteStep;
