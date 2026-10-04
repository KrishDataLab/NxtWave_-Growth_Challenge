import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { videoConfig } from "@/config/videoConfig";

function getYouTubeEmbedUrl(rawUrl: string): string {
  if (!rawUrl || !rawUrl.trim()) return "https://www.youtube-nocookie.com/embed/p8N7wBKeTVY?rel=0&controls=1";
  const url = rawUrl.trim();
  try {
    let videoId = "";
    if (url.includes("youtu.be/")) {
      videoId = url.split("youtu.be/")[1].split("?")[0].split("#")[0];
    } else if (url.includes("youtube.com/watch")) {
      const parsed = new URL(url);
      videoId = parsed.searchParams.get("v") || "";
    } else if (url.includes("youtube-nocookie.com/embed/")) {
      videoId = url.split("youtube-nocookie.com/embed/")[1].split("?")[0].split("#")[0];
    } else if (url.includes("youtube.com/embed/")) {
      videoId = url.split("youtube.com/embed/")[1].split("?")[0].split("#")[0];
    } else if (!url.includes("/")) {
      videoId = url;
    }
    if (videoId) {
      return `https://www.youtube-nocookie.com/embed/${videoId}?rel=0&controls=1`;
    }
  } catch {
    // Fall back to configured embedUrl or default
  }
  return videoConfig.embedUrl || "https://www.youtube-nocookie.com/embed/p8N7wBKeTVY?rel=0&controls=1";
}

export function VideoDemoSection({ onRegister }: { onRegister?: () => void }) {
  const embedUrl = getYouTubeEmbedUrl(videoConfig.videoUrl || videoConfig.embedUrl);

  return (
    <section id="demo-video" className="section-band section-tint scroll-mt-24">
      <div className="section-shell max-w-4xl mx-auto text-center">
        <span className="section-kicker">Workshop Walkthrough</span>
        <h2 className="section-title">Build Your First AI Project in 60 Minutes</h2>
        <p className="section-copy mx-auto max-w-2xl">
          Watch how final-year engineering students learn and build practical AI projects step-by-step.
        </p>

        <div className="mt-8 overflow-hidden rounded-2xl border border-border/80 bg-black shadow-2xl">
          <div className="relative w-full aspect-video">
            <iframe
              src={embedUrl}
              title={videoConfig.title}
              className="absolute inset-0 h-full w-full border-0 rounded-2xl"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
              loading="lazy"
            />
          </div>
        </div>

        {/* Below Video CTA */}
        <div className="mt-8 flex items-center justify-center">
          <Button size="xl" onClick={onRegister} className="gap-2">
            Reserve My Free Seat <ArrowRight className="size-5" />
          </Button>
        </div>
      </div>
    </section>
  );
}
