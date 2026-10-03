export const workshopConfig = {
  workshopTitle: "Build Your First AI Project in 60 Minutes",
  workshopDescription:
    "A free, hands-on online workshop for final-year engineering students who want to stop just learning about AI and start building with it.",
  date: "To be announced",
  time: "To be announced",
  duration: "60 minutes",
  registrationUrl: "#register",
  utmCampaign: "ai-project-60",
  brandSettings: {
    name: "NxtWave",
    campaignLabel: "Growth Challenge",
    officialWebsite: "https://www.ccbp.in/",
  },
  operationalDetails: {
    access: "Workshop access details will be shared after registration.",
    requirements: "Bring a laptop, a stable internet connection, and curiosity. Prior AI experience is not required for this campaign concept.",
    projectDisclosure:
      "The project shown is a campaign preview. The final workshop project can be updated here once confirmed.",
  },
} as const;

export const timeline = [
  ["00:00", "Start"],
  ["10:00", "Understand the project"],
  ["20:00", "Build the core"],
  ["40:00", "Connect the AI"],
  ["55:00", "Test it"],
  ["60:00", "Working project"],
] as const;

export const faqs = [
  ["Is the workshop free?", "Yes. This campaign is for a free online workshop."],
  ["Who can attend?", "The campaign is designed for final-year engineering students."],
  ["How long is it?", "The proposed workshop duration is 60 minutes."],
  ["Is it online?", "Yes. It is planned as an online workshop."],
  ["Do I need prior AI experience?", "No prior AI experience is required for this campaign concept."],
  ["What will I build?", workshopConfig.operationalDetails.projectDisclosure],
  ["What should I bring?", workshopConfig.operationalDetails.requirements],
  ["How will I receive workshop details?", workshopConfig.operationalDetails.access],
] as const;