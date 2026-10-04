import { useEffect, useState } from "react";
import {
  BarChart3,
  CheckCircle2,
  Download,
  IndianRupee,
  Lock,
  PieChart,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Users,
  Zap,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  adminLogin,
  downloadRegistrationCSV,
  fetchAdminDashboard,
  seedDemoData,
  type AdminDashboardData,
} from "@/services/adminService";

export function AdminDashboard({ onClose }: { onClose: () => void }) {
  const [token, setToken] = useState<string | null>(
    () => (typeof window !== "undefined" ? localStorage.getItem("nxtwave_admin_token") : null)
  );
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [mode, setMode] = useState<"real" | "demo" | "combined">("real");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const res = await adminLogin(password);
    setLoading(false);
    if (!res.success || !res.token) {
      setError(res.error || "Invalid password");
      return;
    }
    setToken(res.token);
    localStorage.setItem("nxtwave_admin_token", res.token);
    loadDashboard(res.token, mode);
  }

  async function loadDashboard(authToken: string, targetMode: "real" | "demo" | "combined" = mode) {
    setLoading(true);
    const res = await fetchAdminDashboard(authToken, targetMode);
    setLoading(false);
    if (!res) {
      setError("Session expired. Please log in again.");
      setToken(null);
      localStorage.removeItem("nxtwave_admin_token");
      return;
    }
    setData(res);
  }

  useEffect(() => {
    if (token) {
      loadDashboard(token, mode);
    }
  }, [token]);

  function handleModeChange(newMode: "real" | "demo" | "combined") {
    setMode(newMode);
    if (token) {
      loadDashboard(token, newMode);
    }
  }

  async function handleSeedDemoData() {
    if (!token) return;
    setLoading(true);
    const res = await seedDemoData(token);
    setLoading(false);
    if (res.success) {
      setMode("demo");
      loadDashboard(token, "demo");
    } else {
      setError(res.error || "Failed to seed demo dataset");
    }
  }

  function handleLogout() {
    setToken(null);
    setData(null);
    localStorage.removeItem("nxtwave_admin_token");
  }

  if (!token || !data) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md p-4">
        <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl text-card-foreground">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div className="flex items-center gap-2 font-display text-xl font-bold">
              <Lock className="size-5 text-accent" />
              <span>Admin Growth Dashboard</span>
            </div>
            <button onClick={onClose} className="rounded-lg p-1 text-muted-foreground hover:bg-muted hover:text-foreground">
              <X className="size-5" />
            </button>
          </div>

          <form onSubmit={handleLogin} className="mt-6 space-y-4">
            {error && (
              <div className="rounded-lg bg-destructive/15 p-3 text-xs font-semibold text-destructive flex items-center gap-2">
                <ShieldAlert className="size-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <div>
              <label className="text-xs font-semibold text-muted-foreground">Admin Access Password</label>
              <Input
                type="password"
                placeholder="Enter admin password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1.5"
                required
              />
            </div>
            <Button className="w-full" size="lg" type="submit" disabled={loading}>
              {loading ? "Authenticating…" : "Unlock Dashboard"}
            </Button>
          </form>
        </div>
      </div>
    );
  }

  const { summary, channel_performance, verification_friction_analysis } = data;
  const opt = channel_performance.budget_optimization;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-background/95 backdrop-blur-xl p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-border bg-card/60 p-6 shadow-lg backdrop-blur-md">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-accent/15 px-3 py-1 text-xs font-bold text-accent">
              <Sparkles className="size-3.5" /> Growth Acquisition Engine v2.0
            </div>
            <h1 className="mt-2 font-display text-2xl font-bold text-foreground sm:text-3xl">
              NxtWave Growth & Analytics Dashboard
            </h1>
            <p className="mt-1 text-xs text-muted-foreground">
              Real-Time Conversion Metrics • Channel Attribution • Acquisition Engine Optimization
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Mode Filter Selector */}
            <div className="flex items-center rounded-xl bg-muted/60 p-1 text-xs font-semibold">
              <button
                onClick={() => handleModeChange("real")}
                className={`rounded-lg px-3 py-1.5 transition-all ${
                  mode === "real" ? "bg-card text-foreground shadow-sm font-bold" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Real Data
              </button>
              <button
                onClick={() => handleModeChange("demo")}
                className={`rounded-lg px-3 py-1.5 transition-all ${
                  mode === "demo" ? "bg-amber-500/20 text-amber-300 shadow-sm font-bold border border-amber-500/30" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Demo Data
              </button>
              <button
                onClick={() => handleModeChange("combined")}
                className={`rounded-lg px-3 py-1.5 transition-all ${
                  mode === "combined" ? "bg-card text-foreground shadow-sm font-bold" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Combined
              </button>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleSeedDemoData}
              disabled={loading}
              className="gap-1.5 text-xs border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
            >
              <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} /> Seed Demo Data
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => token && downloadRegistrationCSV(token, mode)}
              className="gap-2 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-xs"
            >
              <Download className="size-4" /> Export CSV
            </Button>

            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground text-xs">
              Log out
            </Button>
            <button onClick={onClose} className="rounded-lg p-2 text-muted-foreground hover:bg-muted">
              <X className="size-5" />
            </button>
          </div>
        </div>

        {/* Demo Simulation Banner */}
        {mode === "demo" && (
          <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 text-amber-300 flex items-center justify-between shadow-lg animate-in fade-in duration-300">
            <div className="flex items-center gap-3">
              <ShieldAlert className="size-5 shrink-0 text-amber-400" />
              <div>
                <strong className="font-bold text-sm tracking-wide">SIMULATION DATA — DEMO ONLY</strong>
                <p className="text-xs text-amber-200/80 mt-0.5">
                  Displaying synthetic challenge simulation dataset (85 test records). Real campaign registrations remain completely separated.
                </p>
              </div>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleModeChange("real")}
              className="border-amber-400/40 text-amber-300 hover:bg-amber-500/20 text-xs shrink-0"
            >
              Switch to Real Data
            </Button>
          </div>
        )}

        {/* Top KPI Metric Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Total Verified Registrations"
            value={summary.total_registrations}
            subtitle={`+${summary.registrations_today} today`}
            icon={<Users className="size-5 text-indigo-400" />}
          />
          <KpiCard
            title="Funnel Conversion Rate"
            value={`${summary.registration_conversion_rate}%`}
            subtitle="Started → Verified"
            icon={<TrendingUp className="size-5 text-emerald-400" />}
          />
          <KpiCard
            title="Referral Share Rate"
            value={`${summary.referral_share_rate}%`}
            subtitle="Registrants who share"
            icon={<PieChart className="size-5 text-amber-400" />}
          />
          <KpiCard
            title="Referral Registration Contribution"
            value={`${summary.referral_registration_rate}%`}
            subtitle="Signups via referrals"
            icon={<Zap className="size-5 text-sky-400" />}
          />
        </div>

        {/* Acquisition Engine ₹2,000 Budget Optimization Recommendation */}
        <div className="rounded-2xl border border-accent/20 bg-accent/5 p-6 shadow-md">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="font-display text-lg font-bold text-foreground flex items-center gap-2">
              <IndianRupee className="size-5 text-accent" /> Acquisition Engine Optimization (₹2,000 Budget Allocation)
            </h2>
            <span className="rounded-full bg-accent/20 px-3 py-1 text-xs font-semibold text-accent">
              Highest Converting Channel: {opt.highest_converting_source}
            </span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Based on real conversion and referral performance data, the ₹2,000 acquisition budget should be shifted toward the highest-converting traffic source to maximize total verified registrations.
          </p>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <ChannelCard
              name="WhatsApp Communities"
              count={channel_performance.whatsapp.registrations}
              pct={channel_performance.whatsapp.percentage}
              budget={opt.recommended_allocation.whatsapp || 0}
            />
            <ChannelCard
              name="Student Communities"
              count={channel_performance.student_communities.registrations}
              pct={channel_performance.student_communities.percentage}
              budget={opt.recommended_allocation.student_communities || 0}
              highlight
            />
            <ChannelCard
              name="Paid Amplification"
              count={channel_performance.paid_amplification.registrations}
              pct={channel_performance.paid_amplification.percentage}
              budget={opt.recommended_allocation.paid_amplification || 0}
            />
          </div>
        </div>

        {/* Verification Friction & Referral Leaderboard */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Verification Friction */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-md space-y-4">
            <h2 className="font-display text-base font-bold text-foreground flex items-center gap-2">
              <Zap className="size-4 text-amber-400" /> Verification Friction Reduction (OTP vs 1-Click Magic Link)
            </h2>
            <div className="rounded-xl border border-border bg-muted/40 p-4">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-muted-foreground">1-Click Magic Link Adoption</span>
                <span className="font-bold text-emerald-400 text-sm">{verification_friction_analysis.magic_link_adoption_pct}%</span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">Faster mobile completion</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-border p-3 text-center">
                <span className="text-[11px] text-muted-foreground block">Standard OTP Verifications</span>
                <strong className="text-lg font-bold text-foreground">{verification_friction_analysis.otp_verified_registrations}</strong>
              </div>
              <div className="rounded-xl border border-border p-3 text-center">
                <span className="text-[11px] text-muted-foreground block">Magic Link Auto-Verifications</span>
                <strong className="text-lg font-bold text-emerald-400">{verification_friction_analysis.magic_link_verified_registrations}</strong>
              </div>
            </div>
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3 text-xs text-emerald-300 flex items-center gap-2">
              <CheckCircle2 className="size-4 shrink-0" />
              <span>Estimated completion time saved: ~{verification_friction_analysis.estimated_time_saved_seconds} seconds across registrants</span>
            </div>
          </div>

          {/* Referral Leaderboard */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-md">
            <h2 className="font-display text-base font-bold text-foreground flex items-center gap-2">
              <BarChart3 className="size-4 text-indigo-400" /> Top Referral Leaderboard
            </h2>
            <div className="mt-4 space-y-2">
              {summary.top_referral_codes.length === 0 ? (
                <p className="py-8 text-center text-xs text-muted-foreground">No referral signups recorded yet.</p>
              ) : (
                summary.top_referral_codes.map((item, idx) => (
                  <div key={item.referral_code} className="flex items-center justify-between rounded-xl border border-border p-3 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="flex size-6 items-center justify-center rounded-full bg-accent/15 font-bold text-accent text-[11px]">
                        {idx + 1}
                      </span>
                      <code className="font-mono text-foreground font-semibold">{item.referral_code}</code>
                    </div>
                    <span className="font-bold text-emerald-400">{item.count} referrals</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* College & Branch Distribution */}
        <div className="grid gap-6 md:grid-cols-2">
          <DistributionCard title="College Distribution" data={summary.registrations_by_college} />
          <DistributionCard title="Branch Distribution" data={summary.registrations_by_branch} />
        </div>
      </div>
    </div>
  );
}

function KpiCard({ title, value, subtitle, icon }: { title: string; value: string | number; subtitle: string; icon: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-md space-y-2">
      <div className="flex items-center justify-between text-muted-foreground">
        <span className="text-xs font-medium">{title}</span>
        {icon}
      </div>
      <div className="text-2xl font-bold font-display text-foreground">{value}</div>
      <p className="text-[11px] text-muted-foreground">{subtitle}</p>
    </div>
  );
}

function ChannelCard({ name, count, pct, budget, highlight = false }: { name: string; count: number; pct: number; budget: number; highlight?: boolean }) {
  return (
    <div className={`rounded-xl border p-4 transition-all ${highlight ? "border-accent bg-accent/10 shadow-md" : "border-border bg-card/80"}`}>
      <div className="flex items-center justify-between text-xs font-bold text-foreground">
        <span>{name}</span>
        <span className="text-muted-foreground">{pct}% of total</span>
      </div>
      <div className="mt-2 text-xl font-bold font-display text-foreground">{count}</div>
      <div className="mt-4 flex items-center justify-between border-t border-border/50 pt-2 text-xs">
        <span className="text-muted-foreground">Reallocated Budget:</span>
        <strong className="text-accent font-bold">₹{budget}</strong>
      </div>
    </div>
  );
}

function DistributionCard({ title, data }: { title: string; data: Record<string, number> }) {
  const entries = Object.entries(data);
  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-md">
      <h3 className="font-display text-sm font-bold text-foreground mb-4">{title}</h3>
      {entries.length === 0 ? (
        <p className="py-6 text-center text-xs text-muted-foreground">No data recorded yet.</p>
      ) : (
        <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
          {entries.map(([label, count]) => (
            <div key={label} className="flex items-center justify-between text-xs rounded-lg bg-muted/40 p-2.5">
              <span className="text-muted-foreground truncate max-w-[200px]">{label}</span>
              <span className="font-bold text-foreground">{count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
