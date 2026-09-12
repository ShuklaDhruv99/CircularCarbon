import type { HealthStatus } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.status = status;
  }
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail)) {
        detail = body.detail
          .map((entry) =>
            typeof entry === "object" && entry !== null && "msg" in entry
              ? String((entry as { msg: unknown }).msg)
              : JSON.stringify(entry),
          )
          .join("; ");
      }
    } catch {
      // response body was not JSON (or empty) — fall back to generic message
    }
    throw new ApiError(
      detail ?? `Request to ${path} failed with status ${response.status}`,
      response.status,
    );
  }

  return response.json() as Promise<T>;
}

export function getHealth() {
  return request<HealthStatus>("/health");
}
