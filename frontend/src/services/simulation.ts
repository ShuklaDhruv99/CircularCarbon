import { request } from "./api";
import type { SimulationResult } from "../types/domain";

export function simulateFactory(factoryId: number, recommendationIds: number[]) {
  return request<SimulationResult>(`/api/simulations/factory/${factoryId}`, {
    method: "POST",
    body: JSON.stringify({ recommendation_ids: recommendationIds }),
  });
}
