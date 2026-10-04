import { API_BASE_URL } from "./apiConfig";

export type AdminDashboardData = {
  summary: {
    total_registrations: number;
    registrations_today: number;
    registration_conversion_rate: number;
    referral_share_rate: number;
    referral_registration_rate: number;
    registrations_by_college: Record<string, number>;
    registrations_by_branch: Record<string, number>;
    top_referral_codes: Array<{ referral_code: string; count: number }>;
  };
  channel_performance: {
    whatsapp: { registrations: number; percentage: number };
    student_communities: { registrations: number; percentage: number };
    paid_amplification: { registrations: number; percentage: number };
    direct_other: { registrations: number; percentage: number };
    budget_optimization: {
      total_budget: number;
      recommended_allocation: Record<string, number>;
      highest_converting_source: string;
    };
  };
  verification_friction_analysis: {
    otp_verified_registrations: number;
    magic_link_verified_registrations: number;
    magic_link_adoption_pct: number;
    estimated_time_saved_seconds: number;
  };
};

export async function adminLogin(password: string): Promise<{ success: boolean; token?: string; error?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    const data = await res.json();
    if (!res.ok) {
      return { success: false, error: data.detail || "Authentication failed" };
    }
    return { success: true, token: data.token };
  } catch (err) {
    return { success: false, error: "Network error logging into Admin dashboard" };
  }
}

export async function fetchAdminDashboard(token: string): Promise<AdminDashboardData | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/dashboard`, {
      headers: { "X-Admin-Token": token },
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function downloadRegistrationCSV(token: string): Promise<void> {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/export-csv`, {
      headers: { "X-Admin-Token": token },
    });
    if (!res.ok) throw new Error("Failed to export CSV");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `nxtwave_registrations_export_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch (err) {
    console.error("CSV download error", err);
  }
}

export async function verifyMagicToken(token: string): Promise<{
  success: boolean;
  referralCode?: string;
  alreadyRegistered?: boolean;
  error?: string;
}> {
  try {
    const res = await fetch(`${API_BASE_URL}/registrations/verify-magic`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ magic_token: token }),
    });
    const data = await res.json();
    if (!res.ok) {
      return { success: false, error: data.detail || "Magic link verification failed" };
    }
    return {
      success: true,
      referralCode: data.referral_code,
      alreadyRegistered: Boolean(data.already_registered),
    };
  } catch (err) {
    return { success: false, error: "Unable to verify magic link connection." };
  }
}
