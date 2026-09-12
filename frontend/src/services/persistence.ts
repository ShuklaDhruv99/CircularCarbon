import type { Factory } from "../types/domain";

const ACTIVE_FACTORY_KEY = "circularcarbon.activeFactory";
const SESSION_KEY = "circularcarbon.session";
const ACTIVE_FACTORY_COOKIE = "cc_active_factory";
const SESSION_COOKIE = "cc_session";

function setCookie(name: string, value: string, days = 30) {
  document.cookie = `${name}=${encodeURIComponent(value)}; Max-Age=${days * 86400}; Path=/; SameSite=Lax`;
}

function clearCookie(name: string) {
  document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Lax`;
}

function readCookie(name: string): string | null {
  const match = document.cookie.split("; ").find((entry) => entry.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.slice(name.length + 1)) : null;
}

export function rememberFactory(factory: Factory) {
  localStorage.setItem(ACTIVE_FACTORY_KEY, JSON.stringify(factory));
  setCookie(ACTIVE_FACTORY_COOKIE, String(factory.id));
  localStorage.setItem(SESSION_KEY, "active");
  setCookie(SESSION_COOKIE, "active");
}

export function getActiveFactoryId(): number | null {
  const cookieValue = readCookie(ACTIVE_FACTORY_COOKIE);
  const stored = localStorage.getItem(ACTIVE_FACTORY_KEY);
  let storedId: number | null = null;
  try { storedId = stored ? ((JSON.parse(stored) as Partial<Factory>).id ?? null) : null; } catch { /* ignore malformed browser storage */ }
  const id = cookieValue ?? storedId;
  const parsed = Number(id);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

export function getRememberedFactory(): Factory | null {
  const stored = localStorage.getItem(ACTIVE_FACTORY_KEY);
  if (!stored) return null;
  try {
    return JSON.parse(stored) as Factory;
  } catch {
    localStorage.removeItem(ACTIVE_FACTORY_KEY);
    return null;
  }
}

export function isLoggedIn() {
  return readCookie(SESSION_COOKIE) === "active" || localStorage.getItem(SESSION_KEY) === "active";
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
  clearCookie(SESSION_COOKIE);
}
