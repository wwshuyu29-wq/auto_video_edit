import Link from "next/link";
import { notFound } from "next/navigation";
import { ArtifactReviewPanel } from "@/components/artifact-review-panel";
import { ProjectAssetsPanel } from "@/components/project-assets-panel";
import { ProjectRunnerControls } from "@/components/project-runner-controls";
import { getProjectDetail, mediaUrl } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

function stageState(mode: string) {
  return mode === "run" ? "Run" : "Reuse";
}

export default async function ProjectDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  return (
    <div className="space-y-6">
      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="border border-black/10 bg-panel p-6 shadow-panel lg:p-8">
          <div className="flex flex-wrap items-center gap-3">
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">{project.productName}</div>
            <div className="rounded-full border border-black/10 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.22em] text-black/62">
              {project.status}
            </div>
            <div className="rounded-full border border-black/10 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.22em] text-black/62">
              {project.workflowMode}
            </div>
          </div>
          <h2 className="mt-5 max-w-[16ch] text-4xl font-semibold tracking-[-0.05em] lg:text-5xl">{project.headline}</h2>
          <div className="mt-6 grid gap-4 text-sm text-black/66 lg:grid-cols-3">
            <div>
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Tone</div>
              <div className="mt-2">{project.tone}</div>
            </div>
            <div>
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Length</div>
              <div className="mt-2">{project.videoLength}</div>
            </div>
            <div>
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Project</div>
              <div className="mt-2">{project.name}</div>
            </div>
          </div>
        </div>
        <div className="border border-black/10 bg-[#161616] p-6 text-white shadow-panel lg:p-8">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-white/45">Workflow</div>
          <div className="mt-5 space-y-3">
            {project.stages.map((stage, index) => (
              <div key={stage.name} className="flex items-center justify-between border-b border-white/10 pb-3 text-sm last:border-b-0 last:pb-0">
                <span>
                  {index + 1}. {stage.name.replaceAll("_", " ")}
                </span>
                <span className="font-mono text-[11px] uppercase tracking-[0.24em] text-white/45">{stageState(stage.mode)}</span>
              </div>
            ))}
          </div>
          <div className="mt-6 text-sm text-white/66">
            Preview output path is controlled by the worker job, not by the page.
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="space-y-6">
          <ArtifactReviewPanel slug={project.slug} artifacts={project.editableArtifacts} />

          <div className="border border-black/10 bg-panel p-6 shadow-panel">
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Viral Logic</div>
            <div className="mt-4 text-lg font-semibold tracking-[-0.03em]">{project.viralGoal}</div>
            <p className="mt-3 text-sm leading-6 text-black/66">{project.contentLogic}</p>
            <div className="mt-5 space-y-2">
              {project.captionSequence.map((line) => (
                <div key={line} className="border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm text-black/76">
                  {line}
                </div>
              ))}
            </div>
          </div>

          <div className="border border-black/10 bg-panel p-6 shadow-panel">
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Script Variants</div>
            <div className="mt-5 space-y-3">
              {project.scripts.map((script) => (
                <div key={script.type} className="border border-black/10 bg-[#f8f8f4] p-4">
                  <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">{script.type}</div>
                  <div className="mt-2 text-lg font-semibold tracking-[-0.03em]">{script.title}</div>
                  <div className="mt-2 text-sm text-black/64">{script.angle}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <ProjectAssetsPanel slug={project.slug} assetLibrary={project.assetLibrary} />

          <ProjectRunnerControls slug={project.slug} workerStatus={project.workerStatus} preflight={project.preflight} />

          <div className="border border-black/10 bg-panel p-6 shadow-panel">
            <div className="flex items-end justify-between">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Shot Matching</div>
                <div className="mt-2 text-2xl font-semibold tracking-[-0.04em]">Material decisions</div>
              </div>
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">
                Missing assets: {project.missingAssetCount}
              </div>
            </div>
            <div className="mt-5 grid gap-3 lg:grid-cols-3">
              {Object.entries(project.matchingScores).map(([key, value]) => (
                <div key={key} className="border border-black/10 bg-[#f8f8f4] p-4">
                  <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">{key}</div>
                  <div className="mt-2 text-2xl font-semibold tracking-[-0.04em]">{value}</div>
                </div>
              ))}
            </div>
            <div className="mt-5 space-y-2">
              {project.editPreview.map((item) => (
                <div key={`${item.beat}-${item.clipId}-${item.time}`} className="grid gap-2 border border-black/10 bg-[#f8f8f4] p-3 text-sm lg:grid-cols-[0.7fr_0.8fr_1.5fr_0.8fr]">
                  <div className="font-medium">{item.beat}</div>
                  <div className="text-black/62">{item.clipId}</div>
                  <div className="text-black/74">{item.text}</div>
                  <div className="font-mono text-[12px] text-black/52">{item.time}</div>
                </div>
              ))}
            </div>
            {project.riskNotes.length > 0 ? (
              <div className="mt-5 border border-black/10 bg-[#111111] p-4 text-sm text-white/76">
                {project.riskNotes.join(" ")}
              </div>
            ) : null}
          </div>

          <div className="border border-black/10 bg-panel p-6 shadow-panel">
            <div className="flex items-end justify-between">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Delivery</div>
                <div className="mt-2 text-2xl font-semibold tracking-[-0.04em]">Preview and variants</div>
              </div>
              {project.renderReport ? (
                <div className="rounded-full border border-black/10 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.22em] text-black/62">
                  worker report
                </div>
              ) : null}
            </div>
            {project.previewVideo ? (
              <div className="mt-5 overflow-hidden border border-black/10 bg-black">
                <video src={mediaUrl(project.previewVideo) || undefined} controls muted playsInline />
              </div>
            ) : null}
            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              {project.deliverables.map((item) => (
                <div key={item.name} className="border border-black/10 bg-[#f8f8f4] p-4">
                  <div className="flex items-center justify-between">
                    <div className="text-base font-semibold">{item.name}</div>
                    {item.duration ? (
                      <div className="font-mono text-[11px] uppercase tracking-[0.22em] text-steel">{item.duration}s</div>
                    ) : null}
                  </div>
                  {item.cover ? (
                    <div className="mt-4 overflow-hidden border border-black/10 bg-white">
                      <img src={mediaUrl(item.cover) || undefined} alt={item.name} className="h-auto w-full object-cover" />
                    </div>
                  ) : null}
                  {item.video ? (
                    <div className="mt-4">
                      <Link href={mediaUrl(item.video) || "#"} className="text-sm underline underline-offset-4">
                        Open video file
                      </Link>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
