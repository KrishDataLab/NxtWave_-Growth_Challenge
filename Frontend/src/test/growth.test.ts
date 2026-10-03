import { describe, expect, it, vi } from "vitest";
import { buildInviteLink, captureAttribution, generateReferralCode } from "@/utils/growth";
import { registrationSchema } from "@/utils/registration";

function memoryStorage() {
  const data = new Map<string, string>();
  return { getItem: (key: string) => data.get(key) ?? null, setItem: (key: string, value: string) => data.set(key, value) };
}

describe("campaign growth rules", () => {
  it("captures the four requested UTM fields and referral source", () => {
    const storage = memoryStorage();
    const result = captureAttribution("?utm_source=club&utm_medium=whatsapp&utm_campaign=launch&utm_content=poster&ref=AI60ABC", storage);
    expect(result).toEqual({ utm_source: "club", utm_medium: "whatsapp", utm_campaign: "launch", utm_content: "poster", referral: "AI60ABC" });
  });

  it("creates an AI60 referral code and adds it to invite links", () => {
    const code = generateReferralCode(vi.fn(() => 0));
    expect(code).toBe("AI60-AAAA");
    expect(buildInviteLink("https://example.com/", code)).toBe("https://example.com/?ref=AI60-AAAA");
  });

  it("accepts a complete final-year student registration", () => {
    expect(registrationSchema.safeParse({ fullName: "Asha Rao", email: "asha@example.com", phone: "9876543210", college: "Example Engineering College", branch: "Computer Science", graduationYear: "2026" }).success).toBe(true);
  });

  it("rejects an invalid mobile number", () => {
    expect(registrationSchema.safeParse({ fullName: "Asha Rao", email: "asha@example.com", phone: "123", college: "Example Engineering College", branch: "Computer Science", graduationYear: "2026" }).success).toBe(false);
  });
});