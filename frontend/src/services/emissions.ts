import { request } from "./api";
import type { EmissionsBreakdown, Hotspot } from "../types/domain";

export function calculateEmissions(factoryId: number) {
  return request<EmissionsBreakdown>(`/api/emissions/calculate/${factoryId}`, { method: "POST" });
}

export function getFactoryEmissions(factoryId: number) {
  return request<EmissionsBreakdown>(`/api/emissions/factory/${factoryId}`);
}

export function getHotspots(factoryId: number) {
  return request<Hotspot[]>(`/api/emissions/hotspots/${factoryId}`);
}
