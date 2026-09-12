import { useState } from "react";
import type { FactoryCreate, Industry } from "../../types/domain";
import Button from "../ui/Button";
import TextField from "../ui/TextField";
import SelectField from "../ui/SelectField";

interface FactoryStepProps {
  onSubmit: (draft: FactoryCreate) => Promise<void>;
  isSubmitting: boolean;
  error: string | null;
}

const INDUSTRY_OPTIONS: { value: Industry; label: string }[] = [
  { value: "Metal Manufacturing", label: "Metal Manufacturing" },
  { value: "Textile Manufacturing", label: "Textile Manufacturing" },
  { value: "Food Processing", label: "Food Processing" },
  { value: "Electronics Manufacturing", label: "Electronics & Electrical" },
  { value: "Chemical Manufacturing", label: "Chemical Manufacturing" },
  { value: "Plastics & Rubber", label: "Plastics & Rubber" },
  { value: "Paper & Packaging", label: "Paper & Packaging" },
  { value: "Pharmaceuticals", label: "Pharmaceuticals" },
  { value: "Automotive Manufacturing", label: "Automotive Manufacturing" },
  { value: "Construction Materials", label: "Construction Materials" },
  { value: "Other Manufacturing", label: "Other manufacturing" },
];

const ALLOWED_INDUSTRIES: Industry[] = INDUSTRY_OPTIONS.map((option) => option.value);

const PRODUCTION_UNIT_OPTIONS = [
  { value: "units/month", label: "units/month" },
  { value: "units/year", label: "units/year" },
  { value: "tonnes/month", label: "tonnes/month" },
  { value: "tonnes/year", label: "tonnes/year" },
  { value: "kg/month", label: "kg/month" },
  { value: "kg/year", label: "kg/year" },
  { value: "pieces/month", label: "pieces/month" },
  { value: "pieces/year", label: "pieces/year" },
  { value: "liters/month", label: "liters/month" },
  { value: "liters/year", label: "liters/year" },
  { value: "batches/month", label: "batches/month" },
  { value: "m²/month", label: "m²/month" },
  { value: "Other", label: "Other" },
];

const ASSESSMENT_PERIOD_OPTIONS = [
  { value: "Weekly", label: "Weekly" },
  { value: "Biweekly", label: "Every two weeks" },
  { value: "Monthly", label: "Monthly" },
  { value: "Quarterly", label: "Quarterly" },
  { value: "Yearly", label: "Yearly" },
  { value: "Other", label: "Other" },
];

function FactoryStep({ onSubmit, isSubmitting, error }: FactoryStepProps) {
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [location, setLocation] = useState("");
  const [productionVolume, setProductionVolume] = useState("");
  const [productionUnitOption, setProductionUnitOption] = useState("");
  const [productionUnitCustom, setProductionUnitCustom] = useState("");
  const [assessmentPeriodOption, setAssessmentPeriodOption] = useState("Monthly");
  const [assessmentPeriodCustom, setAssessmentPeriodCustom] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{
    name?: string;
    industry?: string;
    production_volume?: string;
    production_unit?: string;
    assessment_period?: string;
  }>({});

  function handleSubmit() {
    const errors: typeof fieldErrors = {};
    if (!name.trim()) {
      errors.name = "Name is required.";
    }
    if (!ALLOWED_INDUSTRIES.includes(industry as Industry)) {
      errors.industry = "Please select a supported industry.";
    }

    const trimmedVolume = productionVolume.trim();
    let productionVolumeValue: number | undefined;
    if (trimmedVolume) {
      const parsed = Number(trimmedVolume);
      if (!Number.isFinite(parsed) || parsed <= 0) {
        errors.production_volume = "Enter a valid positive number.";
      } else {
        productionVolumeValue = parsed;
      }
    }

    let productionUnitValue: string | undefined;
    if (productionUnitOption === "Other") {
      if (!productionUnitCustom.trim()) {
        errors.production_unit = "Enter a production unit, or choose one from the list.";
      } else {
        productionUnitValue = productionUnitCustom.trim();
      }
    } else if (productionUnitOption) {
      productionUnitValue = productionUnitOption;
    }

    let assessmentPeriodValue: string | undefined;
    if (assessmentPeriodOption === "Other") {
      if (!assessmentPeriodCustom.trim()) {
        errors.assessment_period = "Enter an assessment period, or choose one from the list.";
      } else {
        assessmentPeriodValue = assessmentPeriodCustom.trim();
      }
    } else if (assessmentPeriodOption) {
      assessmentPeriodValue = assessmentPeriodOption;
    }

    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    const draft: FactoryCreate = {
      name: name.trim(),
      industry: industry as Industry,
      location: location.trim() ? location.trim() : undefined,
      production_volume: productionVolumeValue,
      production_unit: productionUnitValue,
      assessment_period: assessmentPeriodValue,
    };
    void onSubmit(draft);
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="onboarding-step-heading"><div><span className="eyebrow">Step 1 / Facility profile</span><h2 className="text-xl font-semibold text-text">Set up your factory in under two minutes.</h2><p>Start with the basics. You can refine optional details later.</p></div><span className="onboarding-time">≈ 2 min</span></div>

      {error && <p className="rounded-md bg-red-50 px-4 py-2 text-sm text-danger">{error}</p>}

      <TextField
        label="Factory Name"
        name="name"
        value={name}
        onChange={setName}
        required
        error={fieldErrors.name}
        placeholder="e.g. GreenForge Components"
        helpText="Required — used to identify this facility across assessments."
      />
      <SelectField
        label="Industry"
        name="industry"
        value={industry}
        onChange={setIndustry}
        options={INDUSTRY_OPTIONS}
        required
        error={fieldErrors.industry}
        placeholder="Choose the closest match"
      />
      <TextField
        label="Location"
        name="location"
        value={location}
        onChange={setLocation}
        placeholder="e.g. Pune, Maharashtra, India"
        helpText="Optional — city or region helps contextualize energy factors."
      />
      <TextField
        label="Production Volume"
        name="production_volume"
        type="number"
        value={productionVolume}
        onChange={setProductionVolume}
        error={fieldErrors.production_volume}
        placeholder="e.g. 1200"
        helpText="Optional — total output for the selected period."
      />
      <SelectField
        label="Production Unit"
        name="production_unit"
        value={productionUnitOption}
        onChange={setProductionUnitOption}
        options={PRODUCTION_UNIT_OPTIONS}
        error={productionUnitOption === "Other" ? undefined : fieldErrors.production_unit}
        placeholder="Optional — choose an output unit"
      />
      {productionUnitOption === "Other" && (
        <TextField
          label="Custom Production Unit"
          name="production_unit_custom"
          value={productionUnitCustom}
          onChange={setProductionUnitCustom}
          error={fieldErrors.production_unit}
          helpText="e.g. reels, batches, sq. meters."
        />
      )}
      <SelectField
        label="Assessment Period"
        name="assessment_period"
        value={assessmentPeriodOption}
        onChange={setAssessmentPeriodOption}
        options={ASSESSMENT_PERIOD_OPTIONS}
        error={assessmentPeriodOption === "Other" ? undefined : fieldErrors.assessment_period}
        placeholder="Monthly (recommended)"
      />
      {assessmentPeriodOption === "Other" && (
        <TextField
          label="Custom Assessment Period"
          name="assessment_period_custom"
          value={assessmentPeriodCustom}
          onChange={setAssessmentPeriodCustom}
          error={fieldErrors.assessment_period}
          helpText="e.g. 2025 Q1, FY2025."
        />
      )}

      <div className="flex justify-end">
        <Button type="button" onClick={handleSubmit} isLoading={isSubmitting}>
          Continue
        </Button>
      </div>
    </div>
  );
}

export default FactoryStep;
