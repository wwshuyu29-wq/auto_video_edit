import { notFound } from "next/navigation";
import { ArtifactReviewPanel } from "@/components/artifact-review-panel";
import { ProjectWorkflowShell, DensePanel } from "@/components/project-workflow-shell";
import { getProjectDetail } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

export default async function ReferencePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  return (
    <ProjectWorkflowShell project={project} active="reference">
      <div className="grid gap-5 xl:grid-cols-[0.7fr_1.3fr]">
        <DensePanel title="Reference Logic" description="这个页面只处理爆款拆解，不写产品脚本。">
          <div className="max-h-[640px] overflow-y-auto pr-2">
            <div className="text-lg font-semibold tracking-[-0.03em]">{project.viralGoal}</div>
            <p className="mt-4 text-sm leading-6 text-black/65">{project.contentLogic}</p>
            <div className="mt-5 grid gap-2">
              {project.captionSequence.map((line) => (
                <div key={line} className="border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm text-black/76">
                  {line}
                </div>
              ))}
            </div>
          </div>
        </DensePanel>
        <div className="max-h-[760px] overflow-y-auto pr-2">
          <ArtifactReviewPanel slug={project.slug} artifacts={project.editableArtifacts} artifactKeys={["viral_pattern_card"]} hideTabs />
        </div>
      </div>
    </ProjectWorkflowShell>
  );
}
