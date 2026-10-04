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
};

export function RegistrationSuccess({
  referralCode,
  emailVerified,
  whatsappOptIn,
  whatsappStatus,
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

      <div className="mt-3 flex flex-wrap items-center justify-center gap-2">
        {emailVerified && (
          <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-300">
            <Check className="size-3 text-emerald-400" /> Email Verified
          </span>
        )}
        {whatsappOptIn && (
          <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-300">
            <MessageSquareText className="size-3 text-emerald-400" /> WhatsApp Updates Enabled (Mock)
          </span>
        )}
      </div>

      {/* Required Header */}
      <h3 className="mt-4 font-display text-3xl font-bold text-primary-foreground sm:text-4xl">
        Congratulations! Your seat is booked.
      </h3>

      <div className="mt-2 inline-flex items-center gap-1.5 rounded-lg border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">
        <Sparkles className="size-3.5" />
        <span>Build Your First AI Project in 60 Minutes</span>
      </div>

      <p className="mt-4 max-w-md mx-auto text-sm leading-6 text-hero-muted">
        {workshopConfig.operationalDetails.access}
      </p>

      {whatsappOptIn && whatsappStatus === "mocked" && (
        <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-950/30 p-3 text-xs text-emerald-200">
          <p className="font-semibold text-emerald-300">WhatsApp Confirmation Simulated</p>
          <p className="mt-0.5 opacity-80">
            We logged a mock WhatsApp message containing your referral code for challenge demonstration.
          </p>
        </div>
      )}

      {/* Referral Code Box */}
      <div className="referral-code mt-6" aria-label={`Your referral code is ${referralCode}`}>
        <span>Your invite code</span>
        <strong className="tracking-wider text-accent">{referralCode}</strong>
      </div>

      <p className="mt-6 text-sm font-semibold text-primary-foreground">
        Invite your friends to register
      </p>

      {/* Share CTAs */}
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
