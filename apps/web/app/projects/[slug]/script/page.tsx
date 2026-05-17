import { notFound } from "next/navigation";
import { ArtifactReviewPanel } from "@/components/artifact-review-panel";
import { ProjectWorkflowShell, DensePanel } from "@/components/project-workflow-shell";
import { Badge } from "@/components/ui/badge";
import { getProjectDetail, mediaUrl } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

export default async function ScriptPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  return (
    <ProjectWorkflowShell project={project} active="script">
      <div className="grid gap-5 xl:grid-cols-[0.62fr_1.38fr]">
        <DensePanel title="Video Linked Scripts" description="每条视频对应一份脚本。这里看文案逻辑，不做素材选择。">
          <div className="grid max-h-[720px] gap-4 overflow-y-auto pr-2">
            {project.videoVariants.map((variant) => (
              <div key={variant.id} className="border border-black/10 bg-[#f8f8f4] p-4">
                <div className="flex items-start gap-3">
                  {variant.cover ? (
                    <img src={mediaUrl(variant.cover) || undefined} alt={variant.name} className="aspect-[9/16] h-28 shrink-0 object-cover" />
                  ) : null}
                  <div className="min-w-0">
                    <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-steel">{variant.name}</div>
                    <div className="mt-2 text-base font-semibold tracking-[-0.03em]">{variant.scriptTitle}</div>
                    <div className="mt-2 text-sm leading-5 text-black/62">{variant.scriptAngle}</div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <Badge variant="outline">{variant.scriptType || "script"}</Badge>
                      <Badge variant="secondary">{variant.scriptBeats.length} lines</Badge>
                    </div>
                  </div>
                </div>
                <div className="mt-4 grid gap-2">
                  {variant.scriptBeats.slice(0, 8).map((beat, index) => (
                    <div key={`${variant.id}-${index}`} className="border border-black/10 bg-white p-3">
                      <div className="flex items-center justify-between gap-3">
                        <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-black/42">{beat.time || `beat ${index + 1}`}</div>
                        <div className="truncate font-mono text-[10px] uppercase tracking-[0.16em] text-black/35">{beat.beat}</div>
                      </div>
                      <div className="mt-2 text-sm font-medium leading-5">{beat.onScreenText || beat.voiceover}</div>
                      {beat.visualNeed ? <div className="mt-1 line-clamp-2 text-xs leading-5 text-black/50">{beat.visualNeed}</div> : null}
                    </div>
                  ))}
                </div>
                {variant.scriptPath ? <div className="mt-3 truncate font-mono text-[10px] text-black/35">{variant.scriptPath}</div> : null}
              </div>
            ))}
          </div>
        </DensePanel>
        <div className="max-h-[760px] overflow-y-auto pr-2">
          <ArtifactReviewPanel slug={project.slug} artifacts={project.editableArtifacts} artifactKeys={["product_script_card"]} hideTabs />
        </div>
      </div>
    </ProjectWorkflowShell>
  );
}
