import { request } from "./api";
import type { Explanation } from "../types/domain";

export function generateExplanations(factoryId: number) {
  return request<Explanation[]>(`/api/explanations/generate/${factoryId}`, { method: "POST" });
}
