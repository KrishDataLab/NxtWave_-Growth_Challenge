import { useState } from "react";
import {
  BarChart3,
  CheckCircle2,
  Download,
  IndianRupee,
  Lock,
  PieChart,
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
  type AdminDashboardData,
} from "@/services/adminService";

export function AdminDashboard({ onClose }: { onClose: () => void }) {
  const [token, setToken] = useState<string | null>(
    () => typeof window !== "undefined" ? localStorage.getItem("nxtwave_admin_token") : null
  );
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AdminDashboardData | null>(null);

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
    loadDashboard(res.token);
  }

  async function loadDashboard(authToken: string) {
    setLoading(true);
    const res = await fetchAdminDashboard(authToken);
    setLoading(false);
    if (!res) {
      setError("Session expired. Please log in again.");
      setToken(null);
      localStorage.removeItem("nxtwave_admin_token");
      return;
    }
    setData(res);
  }

  // Load data if already logged in
  useState(() => {
    if (token) loadDashboard(token);
  });

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

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => downloadRegistrationCSV(token)}
              className="gap-2 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
            >
              <Download className="size-4" /> Export CSV Analysis
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground">
              Log out
            </Button>
            <button onClick={onClose} className="rounded-lg p-2 text-muted-foreground hover:bg-muted">
              <X className="size-5" />
            </button>
          </div>
        </div>

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
        <div className="rounded-2xl border border-accent/30 bg-gradient-to-br from-card to-accent/5 p-6 shadow-lg">
          <div className="flex items-center justify-between border-b border-border/50 pb-4">
            <div className="flex items-center gap-2">
              <IndianRupee className="size-5 text-accent" />
              <h2 className="font-display text-lg font-bold text-foreground">
                Acquisition Engine Optimization (₹2,000 Budget Allocation)
              </h2>
            </div>
            <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-bold text-emerald-400 border border-emerald-500/30">
              Highest Converting Channel: {opt.highest_converting_source}
            </span>
          </div>

          <p className="mt-4 text-xs text-muted-foreground leading-relaxed">
            Based on real conversion and referral performance data, the ₹2,000 acquisition budget should be shifted toward the highest-converting traffic source to maximize total verified registrations.
          </p>

          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <BudgetItem
              name="WhatsApp Communities"
              count={channel_performance.whatsapp.registrations}
              percentage={channel_performance.whatsapp.percentage}
              recommended={`₹${opt.recommended_allocation.whatsapp || 600}`}
            />
            <BudgetItem
              name="Student Communities"
              count={channel_performance.student_communities.registrations}
              percentage={channel_performance.student_communities.percentage}
              recommended={`₹${opt.recommended_allocation.student_communities || 1100}`}
              highlight={opt.highest_converting_source === "Student Communities"}
            />
            <BudgetItem
              name="Paid Amplification"
              count={channel_performance.paid_amplification.registrations}
              percentage={channel_performance.paid_amplification.percentage}
              recommended={`₹${opt.recommended_allocation.paid_amplification || 300}`}
              highlight={opt.highest_converting_source === "Paid Amplification"}
            />
          </div>
        </div>

        {/* Middle Grid: Verification Friction & Referral Leaderboard */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Verification Friction Comparison */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-md">
            <div className="flex items-center gap-2 border-b border-border pb-3 font-display text-base font-bold text-foreground">
              <Zap className="size-4 text-amber-400" />
              <span>Verification Friction Reduction (OTP vs 1-Click Magic Link)</span>
            </div>
            <div className="mt-4 space-y-4">
              <div className="flex items-center justify-between rounded-xl bg-muted/40 p-3">
                <div>
                  <div className="text-xs font-semibold text-foreground">1-Click Magic Link Adoption</div>
                  <div className="text-[11px] text-muted-foreground">Faster mobile completion</div>
                </div>
                <div className="text-right font-display text-lg font-bold text-emerald-400">
                  {verification_friction_analysis.magic_link_adoption_pct}%
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="rounded-xl border border-border p-3">
                  <div className="text-xs text-muted-foreground">Standard OTP Verifications</div>
                  <div className="mt-1 font-display text-xl font-bold text-foreground">
                    {verification_friction_analysis.otp_verified_registrations}
                  </div>
                </div>
                <div className="rounded-xl border border-border p-3">
                  <div className="text-xs text-muted-foreground">Magic Link Auto-Verifications</div>
                  <div className="mt-1 font-display text-xl font-bold text-accent">
                    {verification_friction_analysis.magic_link_verified_registrations}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 p-3 text-xs text-emerald-300">
                <CheckCircle2 className="size-4 shrink-0 text-emerald-400" />
                <span>Estimated completion time saved: ~{verification_friction_analysis.estimated_time_saved_seconds} seconds across registrants</span>
              </div>
            </div>
          </div>

          {/* Top Referral Leaderboard */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-md">
            <div className="flex items-center gap-2 border-b border-border pb-3 font-display text-base font-bold text-foreground">
              <BarChart3 className="size-4 text-accent" />
              <span>Top Referral Leaderboard</span>
            </div>

            <div className="mt-4 space-y-3">
              {summary.top_referral_codes.length === 0 ? (
                <p className="text-center text-xs text-muted-foreground py-6">No referral signups recorded yet.</p>
              ) : (
                summary.top_referral_codes.map((item, idx) => (
                  <div key={item.referral_code} className="flex items-center justify-between rounded-xl bg-muted/30 p-2.5 text-xs">
                    <div className="flex items-center gap-2 font-mono font-bold text-accent">
                      <span className="flex size-5 items-center justify-center rounded-full bg-accent/20 text-[10px] text-accent">
                        #{idx + 1}
                      </span>
                      {item.referral_code}
                    </div>
                    <div className="font-semibold text-foreground">{item.count} signups</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Bottom Distribution: College & Branch Progress Bars */}
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
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-muted-foreground">{title}</span>
        {icon}
      </div>
      <div className="mt-3 font-display text-3xl font-bold text-foreground">{value}</div>
      <div className="mt-1 text-[11px] font-medium text-emerald-400">{subtitle}</div>
    </div>
  );
}

function BudgetItem({ name, count, percentage, recommended, highlight }: { name: string; count: number; percentage: number; recommended: string; highlight?: boolean }) {
  return (
    <div className={`rounded-xl border p-4 transition-all ${highlight ? "border-accent bg-accent/15" : "border-border bg-muted/20"}`}>
      <div className="text-xs font-semibold text-foreground">{name}</div>
      <div className="mt-2 flex items-baseline justify-between">
        <span className="font-display text-xl font-bold text-foreground">{count}</span>
        <span className="text-xs text-muted-foreground">{percentage}% of total</span>
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-border/40 pt-2 text-xs">
        <span className="text-muted-foreground">Reallocated Budget:</span>
        <span className="font-bold text-emerald-400">{recommended}</span>
      </div>
    </div>
  );
}

function DistributionCard({ title, data }: { title: string; data: Record<string, number> }) {
  const entries = Object.entries(data);
  const total = entries.reduce((acc, [_, count]) => acc + count, 0) || 1;

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-md">
      <h3 className="border-b border-border pb-3 font-display text-base font-bold text-foreground">{title}</h3>
      <div className="mt-4 space-y-3">
        {entries.length === 0 ? (
          <p className="text-center text-xs text-muted-foreground py-4">No data recorded yet.</p>
        ) : (
          entries.map(([name, count]) => {
            const pct = Math.round((count / total) * 100);
            return (
              <div key={name} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-foreground">{name}</span>
                  <span className="font-bold text-muted-foreground">{count} ({pct}%)</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div className="h-full bg-accent transition-all duration-500" style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
