import { notFound } from "next/navigation";
import { ArtifactReviewPanel } from "@/components/artifact-review-panel";
import { ProjectAssetsPanel } from "@/components/project-assets-panel";
import { ProjectWorkflowShell } from "@/components/project-workflow-shell";
import { getProjectDetail } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

export default async function AssetsPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  return (
    <ProjectWorkflowShell project={project} active="assets">
      <div className="grid gap-5 xl:grid-cols-[0.92fr_1.08fr]">
        <div className="max-h-[760px] overflow-y-auto pr-2">
          <ProjectAssetsPanel slug={project.slug} assetLibrary={project.assetLibrary} />
        </div>
        <div className="max-h-[760px] overflow-y-auto pr-2">
          <ArtifactReviewPanel
            slug={project.slug}
            artifacts={project.editableArtifacts}
            assetLibrary={project.assetLibrary}
            artifactKeys={["shot_matching_plan"]}
            hideTabs
          />
        </div>
      </div>
    </ProjectWorkflowShell>
  );
}
