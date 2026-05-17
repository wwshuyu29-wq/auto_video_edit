import { notFound } from "next/navigation";
import { ArtifactReviewPanel } from "@/components/artifact-review-panel";
import { ProjectWorkflowShell, DensePanel } from "@/components/project-workflow-shell";
import { getProjectDetail } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

export default async function ScriptPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  return (
    <ProjectWorkflowShell project={project} active="script">
      <div className="grid gap-5 xl:grid-cols-[0.62fr_1.38fr]">
        <DensePanel title="Script Variants" description="这个页面只改产品脚本，不选择素材。">
          <div className="grid max-h-[640px] gap-3 overflow-y-auto pr-2">
            {project.scripts.map((script) => (
              <div key={script.type} className="border border-black/10 bg-[#f8f8f4] p-4">
                <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-steel">{script.type}</div>
                <div className="mt-2 text-base font-semibold tracking-[-0.03em]">{script.title}</div>
                <div className="mt-2 text-sm text-black/62">{script.angle}</div>
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
