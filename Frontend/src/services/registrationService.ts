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
  whatsappOptIn?: boolean;
};

export type StartVerificationResult = {
  success: boolean;
  verificationId?: string;
  expiresInSeconds?: number;
  message?: string;
  error?: string;
};

export type VerifyOTPResult = {
  success: boolean;
  registrationId?: string;
  referralCode: string;
  emailVerified?: boolean;
  whatsappOptIn?: boolean;
  whatsappStatus?: string;
  message?: string;
  error?: string;
};

export async function startRegistrationVerification(
  data: RegistrationPayload
): Promise<StartVerificationResult> {
  const storage = typeof window !== "undefined" ? window.localStorage : null;
  const attribution: Attribution = storage ? readAttribution(storage) : {};

  if (USE_MOCK_API) {
    return {
      success: true,
      verificationId: "mock-verif-" + Date.now(),
      expiresInSeconds: 600,
      message: "Verification code sent (Mock Mode)",
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
    whatsapp_opt_in: data.whatsappOptIn ?? true,
  };

  try {
    const response = await fetch(`${API_BASE_URL}/registrations/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const resData = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error:
          typeof resData.detail === "string"
            ? resData.detail
            : resData.detail?.[0]?.msg || "Failed to start registration verification.",
      };
    }

    return {
      success: true,
      verificationId: resData.verification_id,
      expiresInSeconds: resData.expires_in_seconds,
      message: resData.message || "Verification code sent to email",
    };
  } catch (err) {
    console.error("[registrationService] Start verification network error", err);
    return {
      success: false,
      error: "Unable to connect to server. Please check your connection and try again.",
    };
  }
}

export async function verifyRegistrationOTP(
  verificationId: string,
  otp: string
): Promise<VerifyOTPResult> {
  if (USE_MOCK_API) {
    const mockCode = generateReferralCode();
    return {
      success: true,
      registrationId: "mock-reg-" + Date.now(),
      referralCode: mockCode,
      emailVerified: true,
      whatsappOptIn: true,
      whatsappStatus: "mocked",
      message: "Registration verified (Mock Mode)",
    };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/registrations/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        verification_id: verificationId,
        otp,
      }),
    });

    const resData = await response.json();

    if (!response.ok) {
      return {
        success: false,
        referralCode: "",
        error:
          typeof resData.detail === "string"
            ? resData.detail
            : "Invalid verification code. Please try again.",
      };
    }

    return {
      success: true,
      registrationId: resData.registration_id,
      referralCode: resData.referral_code,
      emailVerified: resData.email_verified,
      whatsappOptIn: resData.whatsapp_opt_in,
      whatsappStatus: resData.whatsapp_status,
      message: resData.message || "Registration verified successfully",
    };
  } catch (err) {
    console.error("[registrationService] Verify OTP network error", err);
    return {
      success: false,
      referralCode: "",
      error: "Unable to connect to server. Please check your network connection.",
    };
  }
}

export async function submitRegistration(
  data: RegistrationPayload
): Promise<VerifyOTPResult> {
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
      return {
        success: false,
        referralCode: "",
        error: typeof resData.detail === "string" ? resData.detail : "Registration failed.",
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
      error: "Unable to connect to registration server.",
    };
  }
}
