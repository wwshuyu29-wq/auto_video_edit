import Link from "next/link";
import { getDashboardMetrics } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

function metricLabel(value: number, label: string) {
  return (
    <div className="border-t border-black/8 py-5 first:border-t-0 lg:border-t-0 lg:border-l lg:px-6 lg:first:border-l-0">
      <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">{label}</div>
      <div className="mt-3 text-4xl font-semibold tracking-[-0.04em]">{value}</div>
    </div>
  );
}

export default async function DashboardPage() {
  const data = await getDashboardMetrics();

  return (
    <div className="space-y-6">
      <section className="grid gap-4 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="border border-black/10 bg-panel p-6 shadow-panel lg:p-8">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Dashboard</div>
          <h2 className="mt-4 max-w-[12ch] text-5xl font-semibold leading-[0.95] tracking-[-0.05em] lg:text-6xl">
            Black-box automation, opened up.
          </h2>
          <p className="mt-5 max-w-2xl text-sm leading-6 text-black/68 lg:text-base">
            This console exposes the exact middle layer of the workflow: reference logic, product-native script,
            shot plan, preview render, and publishing copy.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/projects/new" className="rounded-md border border-black bg-black px-4 py-2 text-sm text-white">
              Create New Project
            </Link>
            <div className="rounded-md border border-black/10 bg-[#f1f1ed] px-4 py-2 text-sm text-black/66">
              Worker mode: local preview render
            </div>
          </div>
        </div>
        <div className="border border-black/10 bg-[#161616] p-6 text-white shadow-panel lg:p-8">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-white/45">Pipeline State</div>
          <div className="mt-6 space-y-3">
            {[
              "1 / Viral pattern card",
              "2 / Product script card",
              "3 / Shot matching plan",
              "4 / Preview render"
            ].map((line) => (
              <div key={line} className="flex items-center justify-between border-b border-white/10 pb-3 text-sm">
                <span>{line}</span>
                <span className="font-mono text-[11px] uppercase tracking-[0.24em] text-white/45">Online</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid border border-black/10 bg-panel lg:grid-cols-4">
        {metricLabel(data.totalProjects, "Projects")}
        {metricLabel(data.readyProjects, "Ready")}
        {metricLabel(data.configuredProjects, "In Pipeline")}
        {metricLabel(data.totalDeliverables, "Deliverables")}
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="flex items-end justify-between">
            <div>
              <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Projects</div>
              <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em]">Current production queue</h3>
            </div>
          </div>
          <div className="mt-6 space-y-3">
            {data.projects.map((project) => (
              <Link
                key={project.slug}
                href={`/projects/${project.slug}`}
                className="grid gap-4 border border-black/10 bg-[#f8f8f4] p-4 transition hover:border-black/25 lg:grid-cols-[1.5fr_0.8fr_0.7fr_0.7fr]"
              >
                <div>
                  <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">{project.productName}</div>
                  <div className="mt-2 text-lg font-semibold tracking-[-0.03em]">{project.headline}</div>
                  <div className="mt-2 text-sm text-black/62">{project.name}</div>
                </div>
                <div>
                  <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Status</div>
                  <div className="mt-2 text-sm">{project.status}</div>
                </div>
                <div>
                  <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Mode</div>
                  <div className="mt-2 text-sm">{project.workflowMode}</div>
                </div>
                <div>
                  <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Outputs</div>
                  <div className="mt-2 text-sm">{project.deliverableCount}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="border border-black/10 bg-panel p-6 shadow-panel">
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Template Direction</div>
            <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em]">Google Scholar trust template</h3>
            <p className="mt-4 text-sm leading-6 text-black/66">
              The current system centers around one research-tool template: trust doorway hook, creator-style disbelief,
              screen proof, then a short CTA.
            </p>
          </div>
          <div className="border border-black/10 bg-panel p-6 shadow-panel">
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Next Action</div>
            <div className="mt-3 text-2xl font-semibold tracking-[-0.04em]">Wire the upload form to `project_job.json`.</div>
            <p className="mt-4 text-sm leading-6 text-black/66">
              The worker already accepts one standard work order. The web app now needs to create that file shape from user input.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
