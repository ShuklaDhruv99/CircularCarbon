import { request } from "./api";
import type { Recommendation } from "../types/domain";

export function generateRecommendations(factoryId: number) {
  return request<Recommendation[]>(`/api/recommendations/generate/${factoryId}`, { method: "POST" });
}

export function getRecommendations(factoryId: number) {
  return request<Recommendation[]>(`/api/recommendations/factory/${factoryId}`);
}
