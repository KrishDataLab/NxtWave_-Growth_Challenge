import { API_BASE_URL, USE_MOCK_API } from "./apiConfig";
import { generateReferralCode, readAttribution, type Attribution } from "@/utils/growth";

export type RegistrationPayload = {
  fullName: string;
  email: string;
  phone: string;
  college: string;
  branch: string;
  graduationYear: string;
  discoverySource?: string;
};

export type RegistrationServiceResult = {
  success: boolean;
  registrationId?: string;
  referralCode: string;
  message?: string;
  error?: string;
};

export async function submitRegistration(
  data: RegistrationPayload
): Promise<RegistrationServiceResult> {
  const storage = typeof window !== "undefined" ? window.localStorage : null;
  const attribution: Attribution = storage ? readAttribution(storage) : {};

  if (USE_MOCK_API) {
    const mockCode = generateReferralCode();
    return {
      success: true,
      registrationId: "mock-" + Date.now(),
      referralCode: mockCode,
      message: "Registration successful (Mock Mode)",
    };
  }

  const payload = {
    full_name: data.fullName,
    email: data.email,
    phone: data.phone,
    college_name: data.college,
    branch: data.branch,
    graduation_year: Number(data.graduationYear),
    source: attribution.utm_source || data.discoverySource?.toLowerCase() || "direct",
    medium: attribution.utm_medium || "community",
    campaign: attribution.utm_campaign || "ai60",
    content: attribution.utm_content,
    referral_code: attribution.referral || undefined,
  };

  try {
    const response = await fetch(`${API_BASE_URL}/registrations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const resData = await response.json();

    if (!response.ok) {
      if (response.status === 400 && resData.detail) {
        return {
          success: false,
          referralCode: "",
          error: typeof resData.detail === "string" ? resData.detail : "Registration failed.",
        };
      }
      if (response.status === 429) {
        return {
          success: false,
          referralCode: "",
          error: "Too many registration attempts. Please wait a minute before trying again.",
        };
      }
      if (response.status === 422) {
        return {
          success: false,
          referralCode: "",
          error: "Please verify your input fields and try again.",
        };
      }
      return {
        success: false,
        referralCode: "",
        error: resData.detail || "Registration failed. Please try again later.",
      };
    }

    return {
      success: true,
      registrationId: resData.registration_id,
      referralCode: resData.referral_code,
      message: resData.message || "Registration successful",
    };
  } catch (err) {
    console.error("[registrationService] Network error", err);
    return {
      success: false,
      referralCode: "",
      error: "Unable to connect to registration server. Please check your network connection or try again later.",
    };
  }
}
