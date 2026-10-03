import { useState, type FormEvent } from "react";
import { Check, CheckCircle2, Clipboard, Loader2, MessageCircle, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { workshopConfig } from "@/data/workshopConfig";
import { submitRegistration } from "@/services/registrationService";
import {
  buildInviteLink,
  buildWhatsAppUrl,
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

export function RegistrationForm({ ctaSource }: { ctaSource: CtaSource }) {
  const [fields, setFields] = useState(initialFields);
  const [errors, setErrors] = useState<FormErrors>({});
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [referralCode, setReferralCode] = useState("");
  const [copied, setCopied] = useState(false);

  function updateField<Key extends keyof FormFields>(key: Key, value: FormFields[Key]) {
    setFields((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: undefined, apiError: undefined }));
    if (!started) {
      setStarted(true);
      trackEvent("registration_started", { cta_source: ctaSource });
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
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
    const attribution = readAttribution(window.localStorage);

    // Call service layer for registration
    const result = await submitRegistration({
      fullName: parsed.data.fullName,
      email: parsed.data.email,
      phone: parsed.data.phone,
      college: parsed.data.college,
      branch: parsed.data.branch,
      graduationYear: parsed.data.graduationYear,
      discoverySource: fields.discoverySource || undefined,
    });

    if (!result.success) {
      setErrors({ apiError: result.error || "Registration failed. Please try again." });
      setLoading(false);
      return;
    }

    const returnedCode = result.referralCode;
    setReferralCode(returnedCode);

    saveDemoSubmission(window.localStorage, {
      ...parsed.data,
      attribution,
      ctaSource,
      referralCode: returnedCode,
      submittedAt: new Date().toISOString(),
    });

    trackEvent("registration_completed", { cta_source: ctaSource, referral: attribution.referral });
    setLoading(false);
  }

  function getInviteLink() {
    return buildInviteLink(window.location.origin + window.location.pathname, referralCode);
  }

  async function copyInvite() {
    await navigator.clipboard.writeText(getInviteLink());
    setCopied(true);
    trackEvent("referral_copied", { referral_code: referralCode });
    window.setTimeout(() => setCopied(false), 1800);
  }

  if (referralCode) {
    const whatsappUrl = buildWhatsAppUrl(getInviteLink());
    return (
      <div className="success-panel" role="status" aria-live="polite">
        <div className="success-icon"><CheckCircle2 aria-hidden="true" /></div>
        <p className="eyebrow text-accent">Registration successful</p>
        <h3 className="mt-3 font-display text-3xl font-semibold text-primary-foreground sm:text-4xl">You’re on the list.</h3>
        <p className="mt-3 max-w-md text-sm leading-6 text-hero-muted">{workshopConfig.operationalDetails.access}</p>
        <div className="referral-code" aria-label={`Your referral code is ${referralCode}`}>
          <span>Your invite code</span><strong>{referralCode}</strong>
        </div>
        <p className="mt-7 text-sm font-semibold text-primary-foreground">Invite your friends</p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <Button size="xl" asChild>
            <a href={whatsappUrl} target="_blank" rel="noreferrer" onClick={() => trackEvent("share_whatsapp", { location: "success" })}>
              <MessageCircle /> Share on WhatsApp
            </a>
          </Button>
          <Button size="xl" variant="heroOutline" onClick={copyInvite}>
            {copied ? <Check /> : <Clipboard />} {copied ? "Copied" : "Copy Invite Link"}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <form className="registration-form" onSubmit={handleSubmit} noValidate>
      {errors.apiError && (
        <div className="mb-4 rounded-md bg-destructive/15 p-3 text-sm text-destructive font-medium">
          {errors.apiError}
        </div>
      )}
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Full Name" fieldId="full-name" error={errors.fullName}>
          <Input id="full-name" name="fullName" autoComplete="name" maxLength={80} value={fields.fullName} onChange={(e) => updateField("fullName", e.target.value)} aria-invalid={Boolean(errors.fullName)} />
        </Field>
        <Field label="Email" fieldId="email" error={errors.email}>
          <Input id="email" name="email" type="email" autoComplete="email" maxLength={120} value={fields.email} onChange={(e) => updateField("email", e.target.value)} aria-invalid={Boolean(errors.email)} />
        </Field>
        <Field label="Phone Number" fieldId="phone-number" error={errors.phone}>
          <Input id="phone-number" name="phone" type="tel" inputMode="numeric" autoComplete="tel" maxLength={10} value={fields.phone} onChange={(e) => updateField("phone", e.target.value.replace(/\D/g, ""))} aria-invalid={Boolean(errors.phone)} />
        </Field>
        <Field label="College Name" fieldId="college-name" error={errors.college}>
          <Input id="college-name" name="college" autoComplete="organization" maxLength={120} value={fields.college} onChange={(e) => updateField("college", e.target.value)} aria-invalid={Boolean(errors.college)} />
        </Field>
        <Field label="Branch" fieldId="branch" error={errors.branch}>
          <Input id="branch" name="branch" maxLength={80} value={fields.branch} onChange={(e) => updateField("branch", e.target.value)} aria-invalid={Boolean(errors.branch)} />
        </Field>
        <Field label="Graduation Year" fieldId="graduation-year" error={errors.graduationYear}>
          <select id="graduation-year" name="graduationYear" className="form-select" value={fields.graduationYear} onChange={(e) => updateField("graduationYear", e.target.value as FormFields["graduationYear"])} aria-invalid={Boolean(errors.graduationYear)}>
            <option value="">Select year</option><option value="2026">2026</option><option value="2027">2027</option><option value="2028">2028</option>
          </select>
        </Field>
      </div>
      <div className="mt-5">
        <Field label="How did you hear about this workshop? (optional)" fieldId="discovery-source">
          <select id="discovery-source" name="discoverySource" className="form-select" value={fields.discoverySource} onChange={(e) => updateField("discoverySource", e.target.value as FormFields["discoverySource"])}>
            <option value="">Select an option</option>
            {['WhatsApp', 'College Club', 'Friend', 'LinkedIn', 'Instagram', 'Email', 'Other'].map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </Field>
      </div>
      <Button className="mt-7 w-full" size="xl" type="submit" disabled={loading}>
        {loading ? <><Loader2 className="animate-spin" /> Registering…</> : "Register Free"}
      </Button>
      <p className="mt-4 flex items-center justify-center gap-2 text-center text-xs text-muted-foreground"><ShieldCheck className="size-4" /> We’ll only use your details for workshop communication.</p>
    </form>
  );
}

function Field({ label, fieldId, error, children }: { label: string; fieldId: string; error?: string | undefined; children: React.ReactNode }) {
  return (
    <div>
      <Label htmlFor={fieldId}>{label}</Label>
      <div className="mt-2">{children}</div>
      {error ? <p className="mt-1.5 text-xs font-medium text-destructive">{error}</p> : null}
    </div>
  );
}