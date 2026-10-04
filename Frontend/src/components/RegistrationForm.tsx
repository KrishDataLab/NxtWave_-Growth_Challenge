import { useState, type FormEvent } from "react";
import { Loader2, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { WhatsAppOptIn } from "@/components/WhatsAppOptIn";
import { OTPVerification } from "@/components/OTPVerification";
import { RegistrationSuccess } from "@/components/RegistrationSuccess";
import {
  startRegistrationVerification,
  verifyRegistrationOTP,
} from "@/services/registrationService";
import {
  readAttribution,
  saveDemoSubmission,
  trackEvent,
  type CtaSource,
} from "@/utils/growth";
import { registrationSchema, type RegistrationData } from "@/utils/registration";

type FormFields = Omit<RegistrationData, "graduationYear" | "discoverySource"> & {
  graduationYear: RegistrationData["graduationYear"] | "";
  discoverySource: RegistrationData["discoverySource"] | "";
};
type FormErrors = Partial<Record<keyof FormFields, string>> & { apiError?: string };

const initialFields: FormFields = {
  fullName: "",
  email: "",
  phone: "",
  college: "",
  branch: "",
  graduationYear: "",
  discoverySource: "",
};

type FlowStage = "form" | "otp" | "success";

export function RegistrationForm({ ctaSource }: { ctaSource: CtaSource }) {
  const [stage, setStage] = useState<FlowStage>("form");
  const [fields, setFields] = useState(initialFields);
  const [whatsappOptIn, setWhatsappOptIn] = useState(true);
  const [errors, setErrors] = useState<FormErrors>({});
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);

  // OTP Verification Session state
  const [verificationId, setVerificationId] = useState("");

  // Confirmed Registration state
  const [referralCode, setReferralCode] = useState("");
  const [emailVerified, setEmailVerified] = useState(false);
  const [whatsappStatus, setWhatsappStatus] = useState<string | undefined>();

  function updateField<Key extends keyof FormFields>(key: Key, value: FormFields[Key]) {
    setFields((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: undefined, apiError: undefined }));
    if (!started) {
      setStarted(true);
      trackEvent("registration_started", { cta_source: ctaSource });
    }
  }

  async function handleStartVerification(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const parsed = registrationSchema.safeParse({
      ...fields,
      discoverySource: fields.discoverySource || undefined,
    });
    if (!parsed.success) {
      const nextErrors: FormErrors = {};
      for (const issue of parsed.error.issues) {
        const key = issue.path[0];
        if (typeof key === "string" && !(key in nextErrors)) nextErrors[key as keyof FormFields] = issue.message;
      }
      setErrors(nextErrors);
      const firstError = event.currentTarget.querySelector<HTMLElement>("[aria-invalid='true']");
      firstError?.focus();
      return;
    }

    setLoading(true);

    const result = await startRegistrationVerification({
      fullName: parsed.data.fullName,
      email: parsed.data.email,
      phone: parsed.data.phone,
      college: parsed.data.college,
      branch: parsed.data.branch,
      graduationYear: parsed.data.graduationYear,
      discoverySource: fields.discoverySource || undefined,
      whatsappOptIn,
    });

    setLoading(false);

    if (!result.success || !result.verificationId) {
      setErrors({ apiError: result.error || "Failed to send verification code. Please try again." });
      return;
    }

    setVerificationId(result.verificationId);
    trackEvent("otp_sent", { email: parsed.data.email, cta_source: ctaSource });
    setStage("otp");
  }

  async function handleVerifyOTP(otp: string): Promise<{ success: boolean; error?: string }> {
    const result = await verifyRegistrationOTP(verificationId, otp);

    if (!result.success) {
      return { success: false, error: result.error };
    }

    const attribution = readAttribution(window.localStorage);
    setReferralCode(result.referralCode);
    setEmailVerified(Boolean(result.emailVerified));
    setWhatsappStatus(result.whatsappStatus);

    saveDemoSubmission(window.localStorage, {
      ...fields,
      attribution,
      ctaSource,
      referralCode: result.referralCode,
      emailVerified: true,
      whatsappOptIn,
      submittedAt: new Date().toISOString(),
    });

    trackEvent("otp_verified", { verification_id: verificationId });
    trackEvent("registration_completed", {
      cta_source: ctaSource,
      referral: attribution.referral,
      whatsapp_opt_in: whatsappOptIn,
    });

    setStage("success");
    return { success: true };
  }

  async function handleResendOTP(): Promise<{ success: boolean; error?: string }> {
    const parsed = registrationSchema.safeParse({
      ...fields,
      discoverySource: fields.discoverySource || undefined,
    });
    if (!parsed.success) {
      return { success: false, error: "Form details invalid. Please return to step 1." };
    }

    const result = await startRegistrationVerification({
      fullName: parsed.data.fullName,
      email: parsed.data.email,
      phone: parsed.data.phone,
      college: parsed.data.college,
      branch: parsed.data.branch,
      graduationYear: parsed.data.graduationYear,
      discoverySource: fields.discoverySource || undefined,
      whatsappOptIn,
    });

    if (result.success && result.verificationId) {
      setVerificationId(result.verificationId);
      trackEvent("otp_sent", { email: parsed.data.email, is_resend: true });
      return { success: true };
    }

    return { success: false, error: result.error || "Failed to resend verification code." };
  }

  if (stage === "otp") {
    return (
      <OTPVerification
        email={fields.email}
        verificationId={verificationId}
        onVerify={handleVerifyOTP}
        onResend={handleResendOTP}
        onBack={() => setStage("form")}
      />
    );
  }

  if (stage === "success") {
    return (
      <RegistrationSuccess
        referralCode={referralCode}
        emailVerified={emailVerified}
        whatsappOptIn={whatsappOptIn}
        whatsappStatus={whatsappStatus}
      />
    );
  }

  return (
    <form className="registration-form" onSubmit={handleStartVerification} noValidate>
      {errors.apiError && (
        <div className="mb-4 rounded-md bg-destructive/15 p-3 text-sm text-destructive font-medium">
          {errors.apiError}
        </div>
      )}
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Full Name" fieldId="full-name" error={errors.fullName}>
          <Input
            id="full-name"
            name="fullName"
            autoComplete="name"
            maxLength={80}
            value={fields.fullName}
            onChange={(e) => updateField("fullName", e.target.value)}
            aria-invalid={Boolean(errors.fullName)}
          />
        </Field>
        <Field label="Email" fieldId="email" error={errors.email}>
          <Input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            maxLength={120}
            value={fields.email}
            onChange={(e) => updateField("email", e.target.value)}
            aria-invalid={Boolean(errors.email)}
          />
        </Field>
        <Field label="Phone Number" fieldId="phone-number" error={errors.phone}>
          <Input
            id="phone-number"
            name="phone"
            type="tel"
            inputMode="numeric"
            autoComplete="tel"
            maxLength={10}
            value={fields.phone}
            onChange={(e) => updateField("phone", e.target.value.replace(/\D/g, ""))}
            aria-invalid={Boolean(errors.phone)}
          />
        </Field>
        <Field label="College Name" fieldId="college-name" error={errors.college}>
          <Input
            id="college-name"
            name="college"
            autoComplete="organization"
            maxLength={120}
            value={fields.college}
            onChange={(e) => updateField("college", e.target.value)}
            aria-invalid={Boolean(errors.college)}
          />
        </Field>
        <Field label="Branch" fieldId="branch" error={errors.branch}>
          <Input
            id="branch"
            name="branch"
            maxLength={80}
            value={fields.branch}
            onChange={(e) => updateField("branch", e.target.value)}
            aria-invalid={Boolean(errors.branch)}
          />
        </Field>
        <Field label="Graduation Year" fieldId="graduation-year" error={errors.graduationYear}>
          <select
            id="graduation-year"
            name="graduationYear"
            className="form-select"
            value={fields.graduationYear}
            onChange={(e) => updateField("graduationYear", e.target.value as FormFields["graduationYear"])}
            aria-invalid={Boolean(errors.graduationYear)}
          >
            <option value="">Select year</option>
            <option value="2026">2026</option>
            <option value="2027">2027</option>
            <option value="2028">2028</option>
          </select>
        </Field>
      </div>

      <div className="mt-5">
        <Field label="How did you hear about this workshop? (optional)" fieldId="discovery-source">
          <select
            id="discovery-source"
            name="discoverySource"
            className="form-select"
            value={fields.discoverySource}
            onChange={(e) => updateField("discoverySource", e.target.value as FormFields["discoverySource"])}
          >
            <option value="">Select an option</option>
            {["WhatsApp", "College Club", "Friend", "LinkedIn", "Instagram", "Email", "Other"].map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </Field>
      </div>

      <div className="mt-5">
        <WhatsAppOptIn checked={whatsappOptIn} onCheckedChange={setWhatsappOptIn} />
      </div>

      <Button className="mt-7 w-full" size="xl" type="submit" disabled={loading}>
        {loading ? (
          <>
            <Loader2 className="animate-spin" /> Sending Verification Code…
          </>
        ) : (
          "Continue to Verification"
        )}
      </Button>

      <p className="mt-4 flex items-center justify-center gap-2 text-center text-xs text-muted-foreground">
        <ShieldCheck className="size-4" /> We’ll send a 6-digit code to verify your email.
      </p>
    </form>
  );
}

function Field({
  label,
  fieldId,
  error,
  children,
}: {
  label: string;
  fieldId: string;
  error?: string | undefined;
  children: React.ReactNode;
}) {
  return (
    <div>
      <Label htmlFor={fieldId}>{label}</Label>
      <div className="mt-2">{children}</div>
      {error ? <p className="mt-1.5 text-xs font-medium text-destructive">{error}</p> : null}
    </div>
  );
}