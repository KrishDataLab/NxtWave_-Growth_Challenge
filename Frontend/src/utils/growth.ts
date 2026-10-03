import { sendAnalyticsEvent, type TrackingEventName } from "@/services/analyticsService";

export type CtaSource = "hero" | "navbar" | "project_preview" | "final_cta" | "mobile";
export type TrackingEvent = TrackingEventName;

export type Attribution = {
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_content?: string;
  referral?: string;
};

const ATTRIBUTION_KEY = "ai60_attribution";
const SUBMISSIONS_KEY = "ai60_demo_submissions";
const REFERRAL_KEY = "ai60_referral_code";
const SESSION_KEY = "ai60_session_id";

export function getOrCreateSessionId(storage?: Pick<Storage, "getItem" | "setItem">): string {
  try {
    const s = storage || (typeof window !== "undefined" ? window.sessionStorage : null);
    if (!s) return "sess_" + Date.now();
    const existing = s.getItem(SESSION_KEY);
    if (existing) return existing;
    const newId = "sess_" + Date.now() + "_" + Math.random().toString(36).substring(2, 8);
    s.setItem(SESSION_KEY, newId);
    return newId;
  } catch {
    return "sess_" + Date.now();
  }
}

export function trackEvent(event: TrackingEvent, properties: Record<string, unknown> = {}) {
  sendAnalyticsEvent(event, properties);
}

export function captureAttribution(search: string, storage: Pick<Storage, "getItem" | "setItem">): Attribution {
  const params = new URLSearchParams(search);
  const previous = readAttribution(storage);
  const next: Attribution = { ...previous };
  const keys = ["utm_source", "utm_medium", "utm_campaign", "utm_content"] as const;

  for (const key of keys) {
    const value = params.get(key)?.trim().slice(0, 120);
    if (value) next[key] = value;
  }

  const referral = params.get("ref")?.trim().toUpperCase();
  if (referral && /^AI60[A-Z0-9-]{3,16}$/.test(referral)) next.referral = referral;

  storage.setItem(ATTRIBUTION_KEY, JSON.stringify(next));
  return next;
}

export function readAttribution(storage: Pick<Storage, "getItem">): Attribution {
  try {
    const saved = storage.getItem(ATTRIBUTION_KEY);
    return saved ? (JSON.parse(saved) as Attribution) : {};
  } catch {
    return {};
  }
}

export function generateReferralCode(random = Math.random): string {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let suffix = "";
  for (let index = 0; index < 4; index += 1) {
    suffix += alphabet[Math.floor(random() * alphabet.length)] ?? "X";
  }
  return `AI60-${suffix}`;
}

export function getOrCreateReferralCode(storage: Pick<Storage, "getItem" | "setItem">) {
  const existing = storage.getItem(REFERRAL_KEY);
  if (existing) return existing;
  const code = generateReferralCode();
  storage.setItem(REFERRAL_KEY, code);
  return code;
}

export function saveDemoSubmission(storage: Pick<Storage, "getItem" | "setItem">, submission: Record<string, unknown>) {
  let previous: unknown[] = [];
  try {
    previous = JSON.parse(storage.getItem(SUBMISSIONS_KEY) ?? "[]") as unknown[];
  } catch {
    previous = [];
  }
  storage.setItem(SUBMISSIONS_KEY, JSON.stringify([...previous, submission]));
}

export function buildInviteLink(origin: string, referral: string) {
  const url = new URL(origin);
  url.searchParams.set("ref", referral);
  return url.toString();
}

export function buildWhatsAppUrl(inviteLink: string) {
  const message = `Hey! NxtWave is hosting a free online workshop:\nBuild Your First AI Project in 60 Minutes.\n\nI registered. You should join too:\n${inviteLink}`;
  return `https://wa.me/?text=${encodeURIComponent(message)}`;
}