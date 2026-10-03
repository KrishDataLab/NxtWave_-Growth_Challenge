import { API_BASE_URL, USE_MOCK_API } from "./apiConfig";
import { readAttribution } from "@/utils/growth";

export type TrackingEventName =
  | "page_view"
  | "cta_click"
  | "registration_started"
  | "registration_completed"
  | "registration_abandoned"
  | "share_whatsapp"
  | "referral_copied";

export async function sendAnalyticsEvent(
  event: TrackingEventName,
  properties: Record<string, unknown> = {}
): Promise<void> {
  console.info("[campaign-analytics]", event, properties);

  if (USE_MOCK_API) {
    return;
  }

  // Map frontend event names to backend supported event names
  let backendEvent = "page_view";
  if (event === "page_view") backendEvent = "page_view";
  else if (event === "cta_click") backendEvent = "hero_cta_click";
  else if (event === "registration_started") backendEvent = "registration_started";
  else if (event === "registration_completed") backendEvent = "registration_completed";
  else if (event === "share_whatsapp") backendEvent = "whatsapp_share";
  else if (event === "referral_copied") backendEvent = "referral_copied";
  else if (event === "registration_abandoned") return; // Client-side only event

  try {
    const storage = typeof window !== "undefined" ? window.localStorage : null;
    const attribution = storage ? readAttribution(storage) : {};

    const payload = {
      event_name: backendEvent,
      source: attribution.utm_source || (properties.cta_source as string) || "direct",
      medium: attribution.utm_medium || "web",
      campaign: attribution.utm_campaign || "ai60",
      content: attribution.utm_content,
      referral_code: attribution.referral,
      metadata: properties,
    };

    await fetch(`${API_BASE_URL}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.warn("[analyticsService] Failed to record event", err);
  }
}
