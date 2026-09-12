const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function reportUrl(factoryId: number): string {
  return `${API_BASE_URL}/api/report/factory/${factoryId}`;
}
