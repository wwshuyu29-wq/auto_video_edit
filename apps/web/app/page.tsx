import Link from "next/link";
import {
  Captions,
  CheckCircle2,
  Clapperboard,
  FileText,
  FolderUp,
  Sparkles,
  Video
} from "lucide-react";
import { getDashboardMetrics } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

const flowSteps = [
  {
    icon: Video,
    title: "Add reference videos",
    description: "Paste TikTok links or upload saved clips, screenshots, captions, and transcripts."
  },
  {
    icon: FileText,
    title: "Describe your product truth",
    description: "Add the features, proof points, audience, offer, and claims the video must avoid."
  },
  {
    icon: FolderUp,
    title: "Upload your footage",
    description: "Drop in handheld clips, screen recordings, demos, and product proof shots."
  },
  {
    icon: Clapperboard,
    title: "Get scripts and shot plans",
    description: "The workflow rewrites the reference pattern into product-safe hooks, beats, and footage needs."
  },
  {
    icon: Captions,
    title: "Review a captioned draft",
    description: "Check the cover, subtitles, edit plan, and TikTok title before publishing."
  }
];

const outputs = [
  "Reference formula teardown",
  "Product-safe script variants",
  "Beat-by-beat storyboard",
  "Footage match table",
  "Captioned preview video",
  "TikTok title, caption, hashtags"
];

function ProjectLink({
  project
}: {
  project: Awaited<ReturnType<typeof getDashboardMetrics>>["projects"][number];
}) {
  return (
    <Link
      href={`/projects/${project.slug}`}
      className="group block rounded-lg border border-ink/10 bg-white px-5 py-5 transition hover:-translate-y-0.5 hover:border-ink/25 hover:shadow-[0_18px_45px_rgba(31,46,43,0.08)]"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink/45">
            {project.productName}
          </div>
          <h3 className="mt-3 text-xl font-semibold leading-tight text-ink">
            {project.headline}
          </h3>
        </div>
        <span className="rounded-full border border-ink/10 px-3 py-1 text-xs text-ink/55">
          {project.deliverableCount} outputs
        </span>
      </div>
      <p className="mt-4 text-sm leading-6 text-ink/62">{project.name}</p>
      <div className="mt-5 text-sm font-medium text-ink transition group-hover:translate-x-1">
        Continue this video
      </div>
    </Link>
  );
}

export default async function HomePage() {
  const data = await getDashboardMetrics();
  const featuredProjects = data.projects.slice(0, 3);

  return (
    <div className="space-y-20 pb-12">
      <section className="grid min-h-[calc(100vh-140px)] items-center gap-12 py-10 lg:grid-cols-[1.02fr_0.98fr] lg:py-16">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-ink/10 bg-white px-3 py-1.5 text-sm text-ink/62 shadow-[0_10px_30px_rgba(31,46,43,0.05)]">
            <Sparkles className="h-4 w-4 text-[#c9713a]" />
            TikTok reference to product-ready draft
          </div>
          <h1 className="mt-7 max-w-[11ch] text-6xl font-semibold leading-[0.94] tracking-[-0.04em] text-ink lg:text-7xl">
            Turn reference videos into your next short.
          </h1>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-ink/68">
            Upload competitor examples, product facts, and your own footage. The workflow gives you
            product-safe hooks, scripts, shot plans, captions, and a preview you can review before
            posting.
          </p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/projects/new"
              className="inline-flex items-center justify-center rounded-md bg-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink/90"
            >
              Start a video project
            </Link>
            <a
              href="#flow"
              className="inline-flex items-center justify-center rounded-md border border-ink/12 bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:border-ink/28"
            >
              See the workflow
            </a>
          </div>
        </div>

        <div className="relative">
          <div className="relative rounded-[8px] border border-ink/10 bg-white p-5 shadow-[0_24px_80px_rgba(31,46,43,0.10)]">
            <div className="relative aspect-[9/16] overflow-hidden rounded-[6px] bg-[#202321] p-4 text-white">
              <div className="flex items-center justify-between text-xs text-white/55">
                <span>Reference pattern</span>
                <span>00:24</span>
              </div>
              <div className="mt-10 rounded-[6px] bg-white/10 p-4 backdrop-blur">
                <div className="text-[11px] uppercase tracking-[0.18em] text-[#f0c86d]">Hook</div>
                <div className="mt-3 text-3xl font-semibold leading-none">
                  Stop losing good ideas in drafts
                </div>
              </div>
              <div className="mt-6 space-y-3">
                {["Open the reference", "Map the proof", "Match the footage"].map((item) => (
                  <div key={item} className="flex items-center gap-3 rounded-[6px] bg-white px-3 py-3 text-sm text-[#202321]">
                    <CheckCircle2 className="h-4 w-4 text-[#3f8f78]" />
                    {item}
                  </div>
                ))}
              </div>
              <div className="absolute bottom-9 left-9 right-9 rounded-[6px] bg-white px-4 py-3 text-center text-lg font-semibold leading-tight text-[#202321]">
                Product-safe captioned preview
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="flow" className="scroll-mt-24">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold uppercase tracking-[0.18em] text-ink/45">
            The workflow
          </div>
          <h2 className="mt-4 text-4xl font-semibold leading-tight tracking-[-0.03em] text-ink">
            Simple enough for creators. Structured enough for repeatable videos.
          </h2>
        </div>
        <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {flowSteps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.title} className="rounded-lg border border-ink/10 bg-white p-5">
                <div className="flex items-center justify-between">
                  <Icon className="h-5 w-5 text-[#3f8f78]" />
                  <span className="text-sm font-semibold text-ink/35">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>
                <h3 className="mt-8 text-lg font-semibold leading-snug text-ink">{step.title}</h3>
                <p className="mt-3 text-sm leading-6 text-ink/62">{step.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      <section className="grid gap-10 border-y border-ink/10 py-14 lg:grid-cols-[0.85fr_1.15fr]">
        <div>
          <div className="text-sm font-semibold uppercase tracking-[0.18em] text-ink/45">
            What you get
          </div>
          <h2 className="mt-4 text-4xl font-semibold leading-tight tracking-[-0.03em] text-ink">
            Not a black box. A clear edit package.
          </h2>
          <p className="mt-5 text-base leading-7 text-ink/64">
            Each project keeps the creative reasoning visible, so you can approve the idea before
            spending time on final editing.
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {outputs.map((output) => (
            <div key={output} className="flex items-center gap-3 rounded-lg bg-white px-4 py-4 text-sm font-medium text-ink">
              <CheckCircle2 className="h-4 w-4 shrink-0 text-[#3f8f78]" />
              {output}
            </div>
          ))}
        </div>
      </section>

      {featuredProjects.length > 0 ? (
        <section>
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div>
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-ink/45">
                Continue
              </div>
              <h2 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-ink">
                Recent video projects
              </h2>
            </div>
            <Link
              href="/projects/new"
              className="inline-flex items-center justify-center rounded-md border border-ink/12 bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:border-ink/28"
            >
              Create another project
            </Link>
          </div>
          <div className="mt-8 grid gap-4 lg:grid-cols-3">
            {featuredProjects.map((project) => (
              <ProjectLink key={project.slug} project={project} />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
