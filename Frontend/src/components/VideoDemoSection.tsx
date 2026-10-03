import { Play, ArrowRight, ExternalLink } from "lucide-react";
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

  return (
    <section id="demo-video" className="section-band section-tint scroll-mt-24">
      <div className="section-shell max-w-4xl mx-auto text-center">
        <span className="section-kicker">3-minute product walkthrough</span>
        <h2 className="section-title">See the Product in 3 Minutes</h2>
        <p className="section-copy mx-auto max-w-2xl">
          Watch how the workshop campaign moves from student registration to referral and measurable growth.
        </p>

        <div className="mt-8 overflow-hidden rounded-2xl border border-border/60 bg-card shadow-2xl">
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
            <div className="relative flex aspect-video w-full flex-col items-center justify-center bg-gradient-to-br from-card via-muted/40 to-card p-6 text-center">
              <div className="mb-4 flex size-16 items-center justify-center rounded-full bg-accent/15 text-accent shadow-inner ring-1 ring-accent/30">
                <Play className="size-8 translate-x-0.5 fill-accent/30 text-accent" />
              </div>
              <h3 className="font-display text-xl font-bold text-foreground sm:text-2xl">
                Demo video coming soon
              </h3>
              <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                The 3-minute product walkthrough video will be embedded here.
              </p>
            </div>
          )}
        </div>

        <div className="mt-6 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a
            href="https://nxt-wave-growth-challenge.vercel.app/"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:underline"
          >
            Watch the full demo <ArrowRight className="size-4" />
          </a>
          <Button size="lg" variant="outline" className="sm:inline-flex" onClick={onRegister}>
            Try the Live Product <ExternalLink className="size-4 ml-1" />
          </Button>
        </div>
      </div>
    </section>
  );
}
