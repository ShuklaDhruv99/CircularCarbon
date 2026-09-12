import { request } from "./api";
import type { ActionPlan } from "../types/domain";

export function getActionPlan(factoryId: number) {
  return request<ActionPlan>(`/api/action-plan/factory/${factoryId}`);
}
