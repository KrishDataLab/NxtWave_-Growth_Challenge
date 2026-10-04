import { useState, useEffect, useRef } from "react";
import { KeyRound, Loader2, ArrowLeft, RefreshCw, ShieldAlert, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";

type OTPVerificationProps = {
  email: string;
  verificationId: string;
  onVerify: (otp: string) => Promise<{ success: boolean; error?: string }>;
  onResend: () => Promise<{ success: boolean; error?: string }>;
  onBack: () => void;
};

export function OTPVerification({
  email,
  verificationId,
  onVerify,
  onResend,
  onBack,
}: OTPVerificationProps) {
  const [digits, setDigits] = useState<string[]>(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [resendSuccessMsg, setResendSuccessMsg] = useState<string | null>(null);

  // Timers
  const [expirySeconds, setExpirySeconds] = useState(600); // 10 minutes
  const [resendCooldown, setResendCooldown] = useState(30); // 30 seconds

  const inputRefs = [
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
  ];

  // Expiry Countdown Timer
  useEffect(() => {
    if (expirySeconds <= 0) return;
    const timer = setInterval(() => {
      setExpirySeconds((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [expirySeconds]);

  // Resend Cooldown Timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  function handleDigitChange(index: number, value: string) {
    setErrorMsg(null);
    setResendSuccessMsg(null);

    // Handle paste of full 6-digit code
    if (value.length > 1) {
      const pastedDigits = value.replace(/\D/g, "").slice(0, 6).split("");
      const newDigits = [...digits];
      pastedDigits.forEach((d, idx) => {
        if (idx < 6) newDigits[idx] = d;
      });
      setDigits(newDigits);
      const nextFocus = Math.min(pastedDigits.length, 5);
      inputRefs[nextFocus].current?.focus();
      return;
    }

    const cleanChar = value.replace(/\D/g, "");
    const newDigits = [...digits];
    newDigits[index] = cleanChar;
    setDigits(newDigits);

    if (cleanChar && index < 5) {
      inputRefs[index + 1].current?.focus();
    }
  }

  function handleKeyDown(index: number, e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Backspace" && !digits[index] && index > 0) {
      inputRefs[index - 1].current?.focus();
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const otp = digits.join("");
    if (otp.length !== 6) {
      setErrorMsg("Please enter all 6 digits of the verification code.");
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    const result = await onVerify(otp);
    setLoading(false);

    if (!result.success) {
      setErrorMsg(result.error || "Verification failed. Please check the code and try again.");
    }
  }

  async function handleResendCode() {
    if (resendCooldown > 0 || resending) return;

    setResending(true);
    setErrorMsg(null);
    setResendSuccessMsg(null);

    const result = await onResend();
    setResending(false);

    if (result.success) {
      setResendCooldown(30);
      setExpirySeconds(600);
      setDigits(["", "", "", "", "", ""]);
      setResendSuccessMsg("A new verification code has been sent to your email.");
      inputRefs[0].current?.focus();
    } else {
      setErrorMsg(result.error || "Failed to resend verification code. Please try again.");
    }
  }

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const s = secs % 60;
    return `${mins}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div className="rounded-2xl border border-border/80 bg-card p-6 shadow-2xl sm:p-8">
      {/* Back button */}
      <button
        type="button"
        onClick={onBack}
        className="mb-4 inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="size-3.5" /> Back to registration
      </button>

      {/* Header Required by Prompt */}
      <div className="text-center">
        <div className="mx-auto mb-3 flex size-12 items-center justify-center rounded-full bg-accent/15 text-accent ring-4 ring-accent/10">
          <KeyRound className="size-6" />
        </div>
        <h3 className="font-display text-2xl font-bold text-foreground sm:text-3xl">
          Verify your email to confirm your registration.
        </h3>
        <p className="mt-2 text-sm text-muted-foreground">
          We’ve sent a 6-digit verification code to{" "}
          <strong className="text-foreground font-semibold">{email}</strong>.
        </p>
      </div>

      {/* Error / Info Banners */}
      {errorMsg && (
        <div className="mt-4 flex items-center gap-2 rounded-xl bg-destructive/15 p-3.5 text-xs font-medium text-destructive sm:text-sm">
          <ShieldAlert className="size-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {resendSuccessMsg && (
        <div className="mt-4 flex items-center gap-2 rounded-xl bg-emerald-500/15 p-3.5 text-xs font-medium text-emerald-300 sm:text-sm">
          <CheckCircle2 className="size-4 shrink-0 text-emerald-400" />
          <span>{resendSuccessMsg}</span>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="mt-6">
        <div className="flex items-center justify-center gap-2 sm:gap-3">
          {digits.map((digit, idx) => (
            <input
              key={idx}
              ref={inputRefs[idx]}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleDigitChange(idx, e.target.value)}
              onKeyDown={(e) => handleKeyDown(idx, e)}
              className="size-11 rounded-xl border border-input bg-background/80 text-center font-mono text-xl font-bold text-foreground shadow-sm focus:border-accent focus:ring-2 focus:ring-accent/30 focus:outline-none sm:size-13 sm:text-2xl"
              aria-label={`Digit ${idx + 1}`}
              disabled={loading}
              autoFocus={idx === 0}
            />
          ))}
        </div>

        {/* Expiry Timer */}
        <div className="mt-4 text-center text-xs font-medium text-muted-foreground">
          {expirySeconds > 0 ? (
            <span>
              Code expires in <strong className="font-mono text-accent">{formatTime(expirySeconds)}</strong>
            </span>
          ) : (
            <span className="text-destructive font-semibold">
              Verification code expired. Please request a new code.
            </span>
          )}
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          className="mt-6 w-full"
          size="xl"
          disabled={loading || digits.join("").length !== 6 || expirySeconds <= 0}
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin size-4" /> Verifying Code…
            </>
          ) : (
            "Verify & Confirm Seat"
          )}
        </Button>
      </form>

      {/* Resend Action */}
      <div className="mt-6 flex items-center justify-between border-t border-border/60 pt-4 text-xs font-medium">
        <span className="text-muted-foreground">Didn’t receive the code?</span>
        <button
          type="button"
          onClick={handleResendCode}
          disabled={resendCooldown > 0 || resending}
          className="inline-flex items-center gap-1.5 font-semibold text-accent hover:underline disabled:opacity-50 disabled:no-underline cursor-pointer"
        >
          {resending ? (
            <Loader2 className="size-3.5 animate-spin" />
          ) : (
            <RefreshCw className="size-3.5" />
          )}
          {resendCooldown > 0 ? `Resend code in ${resendCooldown}s` : "Resend Code"}
        </button>
      </div>
    </div>
  );
}
