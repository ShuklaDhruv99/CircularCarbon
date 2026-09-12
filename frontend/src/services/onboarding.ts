import { request } from "./api";
import type {
  Factory,
  FactoryCreate,
  Process,
  ProcessCreate,
  EnergyConsumption,
  EnergyConsumptionCreate,
  Material,
  MaterialCreate,
  Waste,
  WasteCreate,
} from "../types/domain";

export function createFactory(data: FactoryCreate) {
  return request<Factory>("/api/factories", { method: "POST", body: JSON.stringify(data) });
}

export function getFactory(factoryId: number) {
  return request<Factory>(`/api/factories/${factoryId}`);
}

export function createProcess(data: ProcessCreate) {
  return request<Process>("/api/processes", { method: "POST", body: JSON.stringify(data) });
}

export function createEnergyEntry(data: EnergyConsumptionCreate) {
  return request<EnergyConsumption>("/api/energy", { method: "POST", body: JSON.stringify(data) });
}

export function createMaterialEntry(data: MaterialCreate) {
  return request<Material>("/api/materials", { method: "POST", body: JSON.stringify(data) });
}

export function createWasteEntry(data: WasteCreate) {
  return request<Waste>("/api/waste", { method: "POST", body: JSON.stringify(data) });
}
