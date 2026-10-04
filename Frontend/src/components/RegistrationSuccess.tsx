import { useState } from "react";
import { Check, CheckCircle2, Clipboard, MessageCircle, ShieldCheck, Sparkles, MessageSquareText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { workshopConfig } from "@/data/workshopConfig";
import { buildInviteLink, buildWhatsAppUrl, trackEvent } from "@/utils/growth";

type RegistrationSuccessProps = {
  referralCode: string;
  emailVerified: boolean;
  whatsappOptIn: boolean;
  whatsappStatus?: string | undefined;
  alreadyRegistered?: boolean;
};

export function RegistrationSuccess({
  referralCode,
  emailVerified,
  whatsappOptIn,
  whatsappStatus,
  alreadyRegistered,
}: RegistrationSuccessProps) {
  const [copied, setCopied] = useState(false);

  function getInviteLink() {
    return buildInviteLink(window.location.origin + window.location.pathname, referralCode);
  }

  async function copyInvite() {
    await navigator.clipboard.writeText(getInviteLink());
    setCopied(true);
    trackEvent("referral_copied", { referral_code: referralCode });
    window.setTimeout(() => setCopied(false), 1800);
  }

  const whatsappUrl = buildWhatsAppUrl(getInviteLink());

  return (
    <div className="success-panel text-center" role="status" aria-live="polite">
      <div className="success-icon mx-auto">
        <CheckCircle2 aria-hidden="true" />
      </div>

      {/* Badges */}
      <div className="mt-3 flex flex-wrap items-center justify-center gap-2">
        {emailVerified && (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-300">
            <Check className="size-3.5 text-emerald-400" /> Email Verified ✓
          </span>
        )}
        {alreadyRegistered && (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/15 px-3 py-1 text-xs font-semibold text-amber-300">
            Existing Registration
          </span>
        )}
        {whatsappOptIn && (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-sky-500/30 bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-300">
            <MessageSquareText className="size-3.5 text-sky-400" /> WhatsApp Confirmation: Simulated
          </span>
        )}
      </div>

      {/* Headline */}
      <h3 className="mt-4 font-display text-3xl font-bold text-primary-foreground sm:text-4xl">
        {alreadyRegistered ? "You're already registered!" : "Congratulations! Your seat is booked."}
      </h3>

      <div className="mt-2 inline-flex items-center gap-1.5 rounded-lg border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">
        <Sparkles className="size-3.5" />
        <span>{alreadyRegistered ? "Your seat is already booked." : "Build Your First AI Project in 60 Minutes"}</span>
      </div>

      <p className="mt-4 max-w-md mx-auto text-sm leading-6 text-hero-muted">
        {workshopConfig.operationalDetails.access}
      </p>

      {whatsappOptIn && (whatsappStatus === "mocked" || whatsappStatus === "skipped") && (
        <div className="mt-4 rounded-xl border border-sky-500/20 bg-slate-900/80 p-3.5 text-xs text-sky-200">
          <p className="font-semibold text-sky-300">Your WhatsApp confirmation has been prepared.</p>
          <p className="mt-1 text-[11px] opacity-80 leading-relaxed">
            In this challenge simulation, the confirmation message payload was generated and logged safely.
          </p>
        </div>
      )}

      {/* Referral Code */}
      <div className="referral-code mt-6" aria-label={`Your referral code is ${referralCode}`}>
        <span>Your referral code</span>
        <strong className="tracking-wider text-accent">{referralCode}</strong>
      </div>

      <p className="mt-6 text-sm font-semibold text-primary-foreground">
        Invite your friends to register
      </p>

      {/* Primary CTA: Share on WhatsApp */}
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <Button size="xl" asChild>
          <a
            href={whatsappUrl}
            target="_blank"
            rel="noreferrer"
            onClick={() => trackEvent("share_whatsapp", { location: "success_screen" })}
          >
            <MessageCircle /> Share on WhatsApp
          </a>
        </Button>
        <Button size="xl" variant="heroOutline" onClick={copyInvite}>
          {copied ? <Check /> : <Clipboard />} {copied ? "Copied Link" : "Copy Invite Link"}
        </Button>
      </div>

      <p className="mt-6 flex items-center justify-center gap-2 text-center text-xs text-muted-foreground">
        <ShieldCheck className="size-4" /> You will receive workshop updates and access links via email.
      </p>
    </div>
  );
}
