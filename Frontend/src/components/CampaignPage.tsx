import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  ArrowDown, ArrowRight, Award, BookOpenCheck, Bot, BrainCircuit, BriefcaseBusiness,
  CheckCircle2, ChevronRight, CircleCheck, Code2, ExternalLink, GraduationCap, Menu,
  MessageCircle, Play, Sparkles, X, Zap,
} from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { RegistrationForm } from "@/components/RegistrationForm";
import { faqs, timeline, workshopConfig } from "@/data/workshopConfig";
import { buildWhatsAppUrl, captureAttribution, trackEvent, type CtaSource } from "@/utils/growth";

const navItems = [["Why Attend", "why-attend"], ["What You'll Build", "project"], ["How It Works", "timeline"], ["FAQ", "faq"]] as const;

export function CampaignPage() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [ctaSource, setCtaSource] = useState<CtaSource>("hero");
  const formStarted = useRef(false);

  useEffect(() => {
    captureAttribution(window.location.search, window.localStorage);
    trackEvent("page_view", { path: window.location.pathname });
    return () => {
      if (formStarted.current) trackEvent("registration_abandoned");
    };
  }, []);

  function goToRegistration(source: CtaSource) {
    setCtaSource(source);
    trackEvent("cta_click", { cta_source: source });
    document.querySelector("#register")?.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-background">
      <AnnouncementBar />
      <Navbar menuOpen={menuOpen} setMenuOpen={setMenuOpen} onRegister={() => goToRegistration("navbar")} />
      <main>
        <Hero onRegister={() => goToRegistration("hero")} />
        <ProblemSection />
        <TimelineSection />
        <ProjectPreview onRegister={() => goToRegistration("project_preview")} />
        <Benefits />
        <Credibility />
        <Audience />
        <section id="register" className="registration-section scroll-mt-28" onFocusCapture={() => { formStarted.current = true; }}>
          <div className="section-shell registration-layout">
            <div className="registration-copy">
              <span className="section-kicker section-kicker-dark">Your next build starts here</span>
              <h2 className="section-title section-title-dark">Save your seat.</h2>
              <p className="section-copy section-copy-dark">Free, online, and designed for final-year engineering students ready to turn AI concepts into something tangible.</p>
              <ul className="mt-8 space-y-4">
                {["No payment required", "No prior AI experience required", "Workshop updates sent directly to you"].map((item) => <li key={item} className="flex items-center gap-3 text-sm text-hero-muted"><CircleCheck className="size-5 text-accent" />{item}</li>)}
              </ul>
            </div>
            <div className="form-card"><RegistrationForm ctaSource={ctaSource} /></div>
          </div>
        </section>
        <ReferralShare />
        <FaqSection />
        <FinalCta onRegister={() => goToRegistration("final_cta")} />
      </main>
      <Footer />
      <div className="mobile-cta"><Button className="w-full" size="lg" onClick={() => goToRegistration("mobile")}>Register Free <ArrowRight /></Button></div>
    </div>
  );
}

function Brand({ inverse = false }: { inverse?: boolean }) {
  return <a href="#top" className={`brand ${inverse ? "brand-inverse" : ""}`} aria-label="NxtWave AI workshop home"><span className="brand-mark"><i /><i /><i /></span><span>NxtWave<small>AI BUILD 60</small></span></a>;
}

function AnnouncementBar() {
  return <div className="announcement"><Sparkles className="size-3.5" /> NxtWave Growth Challenge <span>•</span> Free Online Workshop</div>;
}

function Navbar({ menuOpen, setMenuOpen, onRegister }: { menuOpen: boolean; setMenuOpen: (value: boolean) => void; onRegister: () => void }) {
  return <header className="site-header"><div className="nav-shell"><Brand /><nav className="hidden items-center gap-7 lg:flex" aria-label="Primary navigation">{navItems.map(([label, id]) => <a key={id} href={`#${id}`} className="nav-link">{label}</a>)}</nav><div className="flex shrink-0 items-center gap-2"><Button className="hidden sm:inline-flex" onClick={onRegister}>Register Free <ArrowRight /></Button><Button variant="ghost" size="icon" className="lg:hidden" aria-label={menuOpen ? "Close menu" : "Open menu"} aria-expanded={menuOpen} onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? <X /> : <Menu />}</Button></div></div>{menuOpen ? <nav className="mobile-menu" aria-label="Mobile navigation">{navItems.map(([label, id]) => <a key={id} href={`#${id}`} onClick={() => setMenuOpen(false)}>{label}<ChevronRight /></a>)}</nav> : null}</header>;
}

function Hero({ onRegister }: { onRegister: () => void }) {
  return <section id="top" className="hero"><div className="hero-grid-pattern" aria-hidden="true" /><div className="hero-particle hero-particle-one" /><div className="hero-particle hero-particle-two" /><div className="section-shell hero-layout"><div className="hero-copy"><div className="hero-label"><span className="status-dot" /> Built for final-year engineering students</div><h1>Build Your First<br /><span>AI Project</span><br />in 60 Minutes.</h1><p>{workshopConfig.workshopDescription}</p><div className="hero-actions"><Button size="xl" onClick={onRegister}>Reserve My Free Seat <ArrowRight /></Button><Button size="xl" variant="heroOutline" asChild><a href="#project"><Play /> See What You’ll Build</a></Button></div><div className="trust-line"><span>Free</span><i /><span>Online</span><i /><span>60 minutes</span></div></div><HeroProduct /></div></section>;
}

function HeroProduct() {
  const steps = [{ icon: Sparkles, label: "Idea" }, { icon: BrainCircuit, label: "AI Logic" }, { icon: Code2, label: "Build" }, { icon: CheckCircle2, label: "Working Project" }];
  return <div className="hero-product" aria-label="Visual showing an AI project moving from idea to working project"><div className="window-bar"><div><i /><i /><i /></div><span>ai-project.tsx</span><Zap className="size-4" /></div><div className="project-canvas"><div className="canvas-meta"><span>PROJECT FLOW</span><span className="live-chip"><i /> LIVE</span></div><div className="flow-list">{steps.map(({ icon: Icon, label }, index) => <div key={label} className={`flow-step flow-step-${index + 1}`}><div className="flow-icon"><Icon /></div><div><small>STEP 0{index + 1}</small><strong>{label}</strong></div>{index < steps.length - 1 ? <ArrowDown className="flow-arrow" /> : null}</div>)}</div><div className="build-status"><span>Build status</span><strong><CheckCircle2 /> Ready to test</strong></div></div></div>;
}

function SectionHeading({ kicker, title, copy, centered = false }: { kicker: string; title: ReactNode; copy?: string; centered?: boolean }) {
  return <div className={centered ? "mx-auto max-w-3xl text-center" : "max-w-3xl"}><span className="section-kicker">{kicker}</span><h2 className="section-title">{title}</h2>{copy ? <p className="section-copy">{copy}</p> : null}</div>;
}

function ProblemSection() {
  const items = [["01", "Watching", "Tutorials and explanations"], ["02", "Learning", "Concepts and tools"], ["03", "Building", "A working AI project"]] as const;
  return <section id="why-attend" className="section-band"><div className="section-shell"><SectionHeading kicker="Make the shift" title={<>You’ve watched AI tutorials.<br />Now build something.</>} centered /><div className="progress-cards">{items.map(([number, title, copy], index) => <article className={`progress-card ${index === 2 ? "progress-card-active" : ""}`} key={title}><span>{number}</span><div className="progress-icon">{index === 0 ? <Play /> : index === 1 ? <BookOpenCheck /> : <Code2 />}</div><h3>{title}</h3><p>{copy}</p>{index < 2 ? <ArrowRight className="progress-arrow" /> : <span className="build-badge">THE GOAL</span>}</article>)}</div></div></section>;
}

function TimelineSection() {
  return <section id="timeline" className="section-band section-tint scroll-mt-24"><div className="section-shell"><SectionHeading kicker="Proposed campaign format" title="What happens in 60 minutes?" copy="A focused path from a blank screen to a testable AI project." /><div className="timeline" role="list">{timeline.map(([time, label], index) => <div className="timeline-step" role="listitem" key={time}><span className="timeline-time">{time}</span><div className={`timeline-node ${index === timeline.length - 1 ? "timeline-node-final" : ""}`}>{index === timeline.length - 1 ? <CheckCircle2 /> : index + 1}</div><strong>{label}</strong></div>)}</div><p className="disclosure">This is a proposed workshop structure for this campaign prototype, not an official NxtWave curriculum.</p></div></section>;
}

function ProjectPreview({ onRegister }: { onRegister: () => void }) {
  const [running, setRunning] = useState(false);
  return <section id="project" className="section-band scroll-mt-24"><div className="section-shell"><div className="project-heading"><SectionHeading kicker="Workshop project preview" title="From blank screen to AI project." copy="See how a user input can move through AI processing into a useful output." /><Button variant="outline" size="lg" onClick={onRegister}>I Want to Build This <ArrowRight /></Button></div><div className="demo-window"><div className="demo-sidebar"><div className="demo-logo"><Bot /></div><span>AI Debugger</span><div className="demo-nav active"><Sparkles /> New analysis</div><div className="demo-nav"><Code2 /> Projects</div></div><div className="demo-main"><div className="demo-topbar"><span>Untitled project</span><span className="preview-chip">PREVIEW</span></div><div className="demo-content"><div className="demo-input"><label htmlFor="demo-prompt">INPUT</label><div id="demo-prompt">Explain why this code is failing.</div><Button size="sm" onClick={() => { setRunning(true); window.setTimeout(() => setRunning(false), 900); }}><Zap /> Run analysis</Button></div><div className="processing-line"><span>INPUT</span><i /><span>AI PROCESSING</span><i /><span>OUTPUT</span></div><div className={`demo-output ${running ? "is-running" : ""}`}><div><Bot /><span>AI-generated explanation</span></div><p>The function expects a number, but the value arrives as text. Convert the input before running the calculation.</p><div className="code-line"><span>const</span> total = Number(input) + 1;</div></div></div></div></div><p className="disclosure">{workshopConfig.operationalDetails.projectDisclosure}</p></div></section>;
}

function Benefits() {
  const benefits = ["Build something you can show", "Understand how an AI project comes together", "Move from theory to hands-on building", "Experience what building with AI feels like"];
  return <section className="section-band section-dark"><div className="section-shell"><SectionHeading kicker="Why this hour matters" title="One hour. One project. One useful starting point." /><div className="benefit-grid">{benefits.map((benefit, index) => <article key={benefit}><span>0{index + 1}</span><h3>{benefit}</h3><ArrowRight /></article>)}</div></div></section>;
}

function Credibility() {
  const claims = [{ icon: BrainCircuit, title: "Industry-relevant tech skills", source: "NxtWave mission" }, { icon: GraduationCap, title: "Trainers from IITs & top MNCs", source: "Official website" }, { icon: BriefcaseBusiness, title: "2500+ companies have hired NxtWave learners", source: "Official website" }, { icon: Award, title: "2024 Technology Pioneer", source: "Recognition highlighted by NxtWave" }];
  return <section className="section-band"><div className="section-shell credibility-layout"><div><SectionHeading kicker="Why NxtWave" title="Built around practical, industry-relevant learning." copy="NxtWave focuses on bridging the gap between academia and industry through technology skills, real-world projects, and career development." /><a className="text-link" href={workshopConfig.brandSettings.officialWebsite} target="_blank" rel="noreferrer">Learn more about NxtWave <ExternalLink /></a></div><div className="credibility-grid">{claims.map(({ icon: Icon, title, source }) => <article key={title}><Icon /><div><h3>{title}</h3><p>{source}</p></div></article>)}</div></div></section>;
}

function Audience() {
  const statements = ["I have learned AI but haven’t built much.", "I want a practical project.", "I want to understand how AI products are built.", "I want something tangible to work on."];
  return <section className="section-band section-tint"><div className="section-shell"><SectionHeading kicker="Who it’s for" title="Built for students who are close to their first career step." copy="Primary audience: final-year engineering students." centered /><div className="audience-grid">{statements.map((statement) => <article key={statement}><CheckCircle2 /><p>“{statement}”</p></article>)}</div></div></section>;
}

function ReferralShare() {
  function share() {
    const link = window.location.origin + window.location.pathname;
    trackEvent("share_whatsapp", { location: "share_section" });
    window.open(buildWhatsAppUrl(link), "_blank", "noopener,noreferrer");
  }
  return <section className="share-band"><div className="section-shell share-layout"><div className="share-avatars" aria-hidden="true"><span>AI</span><span>&lt;/&gt;</span><span>+</span></div><div><span className="section-kicker">Build together</span><h2>Know 3 engineering students who should build this too?</h2><p>Share the workshop with your classmates and build together.</p></div><Button size="xl" onClick={share}><MessageCircle /> Share on WhatsApp</Button></div></section>;
}

function FaqSection() {
  return <section id="faq" className="section-band scroll-mt-24"><div className="section-shell faq-layout"><SectionHeading kicker="Quick answers" title="Questions before you build?" copy="Known campaign details are answered here. Operational details remain configurable until confirmed." /><Accordion type="single" collapsible className="faq-list">{faqs.map(([question, answer], index) => <AccordionItem value={`faq-${index}`} key={question}><AccordionTrigger>{question}</AccordionTrigger><AccordionContent>{answer}</AccordionContent></AccordionItem>)}</Accordion></div></section>;
}

function FinalCta({ onRegister }: { onRegister: () => void }) {
  return <section className="final-cta"><div className="final-grid" aria-hidden="true" /><div className="section-shell"><span className="section-kicker section-kicker-dark">Your first AI project</span><h2>Don’t just learn about AI.<br /><span>Build with it.</span></h2><p>Join the 60-minute workshop.</p><Button size="xl" onClick={onRegister}>Reserve My Free Seat <ArrowRight /></Button></div></section>;
}

function Footer() {
  return <footer><div className="section-shell footer-main"><Brand inverse /><nav aria-label="Footer navigation"><a href="#timeline">Workshop</a><a href="#privacy">Privacy</a><a href="#terms">Terms</a><a href={workshopConfig.brandSettings.officialWebsite} target="_blank" rel="noreferrer">NxtWave website</a></nav></div><div className="section-shell footer-bottom"><p>Workshop campaign prototype created for the NxtWave Growth Challenge.</p><p>Not an officially launched NxtWave campaign.</p></div><span id="privacy" className="sr-only">Details are used only for workshop communication in this local prototype.</span><span id="terms" className="sr-only">This prototype does not confirm workshop scheduling or official launch.</span></footer>;
}