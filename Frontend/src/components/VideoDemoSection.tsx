import { useState } from "react";
import { Play, ArrowRight, ExternalLink, Info, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { videoConfig } from "@/config/videoConfig";

function getYouTubeEmbedUrl(rawUrl: string): string | null {
  if (!rawUrl || !rawUrl.trim()) return null;
  const url = rawUrl.trim();
  try {
    let videoId = "";
    if (url.includes("youtu.be/")) {
      videoId = url.split("youtu.be/")[1].split("?")[0].split("#")[0];
    } else if (url.includes("youtube.com/watch")) {
      const parsed = new URL(url);
      videoId = parsed.searchParams.get("v") || "";
    } else if (url.includes("youtube.com/embed/")) {
      videoId = url.split("youtube.com/embed/")[1].split("?")[0].split("#")[0];
    } else if (!url.includes("/")) {
      videoId = url;
    }
    if (videoId) {
      return `https://www.youtube-nocookie.com/embed/${videoId}?rel=0&autoplay=0`;
    }
  } catch {
    // Return rawUrl if parsing fails
  }
  return url;
}

export function VideoDemoSection({ onRegister }: { onRegister?: () => void }) {
  const embedUrl = getYouTubeEmbedUrl(videoConfig.videoUrl);
  const [showMessage, setShowMessage] = useState(false);

  function handlePlaceholderClick() {
    setShowMessage(true);
    window.setTimeout(() => setShowMessage(false), 3000);
  }

  return (
    <section id="demo-video" className="section-band section-tint scroll-mt-24">
      <div className="section-shell max-w-4xl mx-auto text-center">
        <span className="section-kicker">3-minute product walkthrough</span>
        <h2 className="section-title">Watch the 3-minute walkthrough</h2>
        <p className="section-copy mx-auto max-w-2xl">
          See how registration, referrals and campaign measurement work together.
        </p>

        <div className="mt-8 overflow-hidden rounded-2xl border border-border/80 bg-card shadow-2xl">
          {embedUrl ? (
            <div className="relative w-full aspect-video bg-black/90">
              <iframe
                src={embedUrl}
                title={videoConfig.title}
                className="absolute inset-0 h-full w-full border-0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                loading="lazy"
              />
            </div>
          ) : (
            <div
              onClick={handlePlaceholderClick}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  handlePlaceholderClick();
                }
              }}
              aria-label="Play demo video (coming soon)"
              className="group relative flex aspect-video w-full flex-col justify-between overflow-hidden bg-[#0A0E17] p-5 text-left select-none cursor-pointer transition-colors"
            >
              {/* Radial spotlight & subtle grid background */}
              <div
                className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/30 via-slate-900/80 to-[#0A0E17]"
                aria-hidden="true"
              />
              <div
                className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,#1f293715_1px,transparent_1px),linear-gradient(to_bottom,#1f293715_1px,transparent_1px)] bg-[size:24px_24px]"
                aria-hidden="true"
              />

              {/* Top Bar Controls */}
              <div className="relative z-10 flex items-center justify-between">
                <div className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-black/60 px-3 py-1 text-xs font-semibold text-white/90 backdrop-blur-md">
                  <Sparkles className="size-3.5 text-accent" />
                  <span>Product Demo</span>
                </div>

                <div className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/15 px-3 py-1 text-xs font-semibold text-amber-300 backdrop-blur-md">
                  <span className="size-2 rounded-full bg-amber-400 animate-pulse" />
                  <span>Video coming soon</span>
                </div>
              </div>

              {/* Center Play Button & Dynamic Toast Message */}
              <div className="relative z-10 flex flex-col items-center justify-center my-auto py-4 text-center">
                {showMessage ? (
                  <div className="mb-4 inline-flex items-center gap-2 rounded-xl border border-sky-500/30 bg-slate-900/95 px-4 py-2.5 text-sm font-semibold text-sky-200 shadow-2xl backdrop-blur-md transition-all animate-in fade-in zoom-in duration-200">
                    <Info className="size-4.5 text-sky-400 shrink-0" />
                    <span>Demo video will be available soon.</span>
                  </div>
                ) : null}

                <div className="relative flex size-20 items-center justify-center rounded-full bg-red-600/90 text-white shadow-2xl transition-all duration-300 group-hover:scale-110 group-hover:bg-red-600 group-hover:shadow-red-600/40 ring-4 ring-red-600/20">
                  <Play className="size-9 translate-x-0.5 fill-white text-white" />
                </div>

                <h3 className="mt-4 font-display text-lg font-bold text-white sm:text-2xl tracking-tight drop-shadow-md">
                  Build Your First AI Project in 60 Minutes
                </h3>
                <p className="mt-1 text-xs font-medium text-slate-300 sm:text-sm">
                  3-minute product walkthrough
                </p>
              </div>

              {/* Bottom Player Timeline Mockup */}
              <div className="relative z-10 flex flex-col gap-2 pt-2">
                <div className="flex items-center justify-between text-xs font-mono font-medium text-slate-400">
                  <span>0:00</span>
                  <span className="rounded bg-black/80 px-2 py-0.5 font-bold text-white border border-white/10 backdrop-blur-sm">
                    3:00
                  </span>
                </div>

                {/* Progress bar line */}
                <div className="relative h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full w-1/3 rounded-full bg-red-600 transition-all duration-300 group-hover:w-1/2" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Below Video CTAs */}
        <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a
            href="https://nxt-wave-growth-challenge.vercel.app/"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:underline"
          >
            Watch the 3-minute walkthrough <ArrowRight className="size-4" />
          </a>
          <Button size="lg" className="sm:inline-flex" onClick={onRegister}>
            Try the Live Product <ExternalLink className="size-4 ml-1" />
          </Button>
        </div>
      </div>
    </section>
  );
}
