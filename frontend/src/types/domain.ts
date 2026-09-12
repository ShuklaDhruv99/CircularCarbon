export type Industry = "Metal Manufacturing" | "Textile Manufacturing" | "Food Processing";

export type EnergyType =
  | "electricity"
  | "natural_gas"
  | "diesel"
  | "coal"
  | "other"
  | "renewable_electricity";

export type DisposalMethod = "reused" | "recycled" | "sold" | "landfilled" | "other";

export interface EnergyConsumptionCreate {
  process_id: number;
  energy_type: EnergyType;
  quantity: number;
  unit: string;
  period: string;
}

// The backend serializes Numeric/Decimal columns as JSON strings (to avoid
// float precision loss), so every *Read type re-types those fields as
// `string` rather than inheriting the `number` used when creating them.
export interface EnergyConsumption extends Omit<EnergyConsumptionCreate, "quantity"> {
  id: number;
  quantity: string;
}

export interface MaterialCreate {
  process_id: number;
  material_name: string;
  quantity: number;
  unit: string;
  recycled_percentage?: number;
  source?: string;
}

export interface Material extends Omit<MaterialCreate, "quantity" | "recycled_percentage"> {
  id: number;
  quantity: string;
  recycled_percentage?: string;
}

export interface WasteCreate {
  process_id: number;
  waste_type: string;
  quantity: number;
  unit: string;
  disposal_method: DisposalMethod;
  recycled_quantity?: number;
  landfilled_quantity?: number;
  reused_quantity?: number;
}

export interface Waste
  extends Omit<WasteCreate, "quantity" | "recycled_quantity" | "landfilled_quantity" | "reused_quantity"> {
  id: number;
  quantity: string;
  recycled_quantity?: string;
  landfilled_quantity?: string;
  reused_quantity?: string;
}

export interface ProcessCreate {
  factory_id: number;
  name: string;
  process_type?: string;
  production_volume?: number;
}

export interface Process extends Omit<ProcessCreate, "production_volume"> {
  id: number;
  production_volume?: string;
  energy_consumption: EnergyConsumption[];
  materials: Material[];
  waste: Waste[];
}

export interface FactoryCreate {
  name: string;
  industry: Industry;
  location?: string;
  production_volume?: number;
  production_unit?: string;
  assessment_period?: string;
}

export interface Factory extends Omit<FactoryCreate, "production_volume"> {
  id: number;
  production_volume?: string;
  created_at: string;
  processes: Process[];
}

export interface EmissionResult {
  id: number;
  process_id: number;
  category: string; // "energy" | "materials" | "waste"
  activity: string;
  emission_factor: string;
  emission_factor_source: string | null;
  co2e: string;
  period: string;
  created_at: string;
}

export interface CategoryBreakdown {
  category: string;
  co2e: string;
  percentage: string;
}

export interface ProcessBreakdown {
  process_id: number;
  process_name: string;
  co2e: string;
  percentage: string;
}

export interface EmissionsBreakdown {
  factory_id: number;
  factory_total_co2e: string;
  category_breakdown: CategoryBreakdown[];
  process_breakdown: ProcessBreakdown[];
  results: EmissionResult[];
}

export interface Hotspot extends EmissionResult {
  percentage: string;
  is_hotspot: boolean;
}

export type RecommendationStrategy =
  | "reduce"
  | "reuse"
  | "recycle"
  | "substitute"
  | "recover"
  | "process_optimization";

export type RecommendationCostTier = "low" | "medium" | "high";

export interface Recommendation {
  id: number;
  hotspot_id: number;
  hotspot_category: string;
  hotspot_activity: string;
  title: string;
  description: string;
  strategy: RecommendationStrategy;
  estimated_cost: RecommendationCostTier;
  co2_reduction: string;
  payback_period: string | null;
  score: string | null;
  created_at: string;
}
