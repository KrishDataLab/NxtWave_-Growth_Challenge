import { MessageSquareText } from "lucide-react";
import { Label } from "@/components/ui/label";

type WhatsAppOptInProps = {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
};

export function WhatsAppOptIn({ checked, onCheckedChange }: WhatsAppOptInProps) {
  return (
    <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4 transition-all hover:border-emerald-500/50">
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          id="whatsapp-opt-in"
          checked={checked}
          onChange={(e) => onCheckedChange(e.target.checked)}
          className="mt-0.5 size-4 rounded border-emerald-500/50 bg-slate-900 text-emerald-500 focus:ring-emerald-500 focus:ring-offset-0 cursor-pointer accent-emerald-500 shrink-0"
        />
        <div className="grid gap-1 leading-none">
          <Label
            htmlFor="whatsapp-opt-in"
            className="flex items-center gap-1.5 text-xs font-semibold text-emerald-300 cursor-pointer sm:text-sm"
          >
            <MessageSquareText className="size-4 text-emerald-400 shrink-0" />
            I agree to receive workshop confirmation and updates from NxtWave on WhatsApp.
          </Label>
          <p className="text-[11px] text-emerald-200/70 leading-normal mt-1">
            No spam. We will only share workshop access link, referral notifications, and reminders.
          </p>
        </div>
      </div>
    </div>
  );
}
