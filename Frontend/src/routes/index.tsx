import { createFileRoute } from "@tanstack/react-router";
import { CampaignPage } from "@/components/CampaignPage";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Build Your First AI Project in 60 Minutes | NxtWave Growth Challenge" },
      { name: "description", content: "A free, hands-on online AI project workshop concept for final-year engineering students." },
      { property: "og:title", content: "Build Your First AI Project in 60 Minutes" },
      { property: "og:description", content: "A free, hands-on online AI project workshop concept for final-year engineering students." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: CampaignPage,
});
