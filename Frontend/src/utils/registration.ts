import { z } from "zod";

const graduationYears = ["2026", "2027", "2028"] as const;

export const registrationSchema = z.object({
  fullName: z.string().trim().min(2, "Enter your full name").max(80, "Keep your name under 80 characters"),
  email: z.string().trim().email("Enter a valid email address").max(120),
  phone: z.string().trim().regex(/^[6-9]\d{9}$/, "Enter a valid 10-digit Indian mobile number"),
  college: z.string().trim().min(2, "Enter your college name").max(120),
  branch: z.string().trim().min(2, "Enter your branch").max(80),
  graduationYear: z.enum(graduationYears, { message: "Select your graduation year" }),
  discoverySource: z.enum(["WhatsApp", "College Club", "Friend", "LinkedIn", "Instagram", "Email", "Other"]).optional(),
});

export type RegistrationData = z.infer<typeof registrationSchema>;