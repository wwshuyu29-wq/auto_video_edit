import Link from "next/link";
import { notFound } from "next/navigation";
import { ProjectRunnerControls } from "@/components/project-runner-controls";
import { ProjectWorkflowShell, DensePanel } from "@/components/project-workflow-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getProjectDetail, mediaUrl } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

export default async function RenderPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  return (
    <ProjectWorkflowShell project={project} active="render">
      <div className="grid gap-5 xl:grid-cols-[0.74fr_1.26fr]">
        <div className="flex flex-col gap-5">
          <ProjectRunnerControls slug={project.slug} workerStatus={project.workerStatus} preflight={project.preflight} />
          <DensePanel title="Render Notes" description="这里只负责运行和查看输出，不重新决定脚本或分镜。">
            <div className="grid gap-3 text-sm text-black/65">
              <div>Worker state: {project.workerStatus.state}</div>
              <div>Preview video: {project.previewVideo ? "available" : "not found"}</div>
              <div>Render report: {project.renderReport ? "available" : "not found"}</div>
            </div>
          </DensePanel>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Preview and Deliverables</CardTitle>
            <p className="mt-1 text-sm text-black/55">成片、封面、脚本和分镜在这里按视频版本配对展示。</p>
          </CardHeader>
          <CardContent>
            {project.previewVideo ? (
              <div className="overflow-hidden border border-black/10 bg-black">
                <video src={mediaUrl(project.previewVideo) || undefined} controls muted playsInline />
              </div>
            ) : null}
            <div className="mt-5 grid max-h-[720px] gap-4 overflow-y-auto pr-2 md:grid-cols-2 xl:grid-cols-3">
              {project.videoVariants.map((item) => (
                <div key={`${item.name}-${item.video}`} className="border border-black/10 bg-[#f8f8f4] p-4">
                  <div className="flex items-center justify-between gap-2">
                    <div className="truncate text-sm font-semibold">{item.name}</div>
                    <Badge variant="outline">{item.duration ? `${item.duration}s` : "video"}</Badge>
                  </div>
                  {item.video ? (
                    <div className="mt-4 overflow-hidden border border-black/10 bg-black">
                      <video src={mediaUrl(item.video) || undefined} controls muted playsInline className="aspect-[9/16] w-full object-cover" />
                    </div>
                  ) : item.cover ? (
                    <img src={mediaUrl(item.cover) || undefined} alt={item.name} className="mt-4 aspect-[9/16] w-full object-cover" />
                  ) : null}
                  <div className="mt-4 border-t border-black/10 pt-3">
                    <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-steel">{item.scriptType || "script"}</div>
                    <div className="mt-1 line-clamp-2 text-sm font-medium leading-5">{item.scriptTitle}</div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <Badge variant="secondary">{item.scriptBeats.length} script beats</Badge>
                      <Badge variant="secondary">{item.shotBeats.length} shot beats</Badge>
                    </div>
                  </div>
                  {item.video ? (
                    <Link href={mediaUrl(item.video) || "#"} className="mt-4 inline-block text-sm underline underline-offset-4">
                      Open video file
                    </Link>
                  ) : null}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </ProjectWorkflowShell>
  );
}
