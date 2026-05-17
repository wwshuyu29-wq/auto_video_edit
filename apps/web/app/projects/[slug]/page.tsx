import Link from "next/link";
import { notFound } from "next/navigation";
import { ProjectWorkflowShell, DensePanel } from "@/components/project-workflow-shell";
import { Badge } from "@/components/ui/badge";
import { ButtonLink } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getProjectDetail, mediaUrl } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

export default async function ProjectOverviewPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  const flowCards = [
    {
      href: `/projects/${project.slug}/reference`,
      title: "1. Reference",
      desc: "拆对标视频逻辑、钩子、字幕节奏。",
      stat: `${project.captionSequence.length} caption lines`
    },
    {
      href: `/projects/${project.slug}/script`,
      title: "2. Script",
      desc: "改写成产品脚本，不在这里选素材。",
      stat: `${project.scripts.length} variants`
    },
    {
      href: `/projects/${project.slug}/assets`,
      title: "3. Assets",
      desc: "管理素材库、镜头标签、分镜匹配表。",
      stat: `${project.assetLibrary.assetCount} clips`
    },
    {
      href: `/projects/${project.slug}/render`,
      title: "4. Render",
      desc: "运行 worker、预览成片、查看交付物。",
      stat: `${project.deliverables.length} outputs`
    }
  ];

  return (
    <ProjectWorkflowShell project={project} active="overview">
      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <DensePanel title="Workflow Control" description="Four pages, four decisions. No more one-page scroll wall.">
          <div className="grid gap-3 md:grid-cols-2">
            {flowCards.map((item) => (
              <Link key={item.href} href={item.href} className="border border-black/10 bg-[#f8f8f4] p-5 transition hover:border-black/35">
                <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-steel">{item.stat}</div>
                <div className="mt-3 text-lg font-semibold tracking-[-0.03em]">{item.title}</div>
                <div className="mt-2 text-sm leading-6 text-black/60">{item.desc}</div>
              </Link>
            ))}
          </div>
        </DensePanel>

        <DensePanel title="Where Your Files Are" description="旧素材和视频没有丢，只是早期没有统一 manifest。">
          <div className="grid gap-3 text-sm">
            <div className="border border-black/10 bg-[#f8f8f4] p-3">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Project folder</div>
              <div className="mt-2 break-all text-black/70">{project.projectDir}</div>
            </div>
            <div className="border border-black/10 bg-[#f8f8f4] p-3">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Raw footage</div>
              <div className="mt-2 break-all text-black/70">{project.assetLibrary.sourceMaterialDir}</div>
            </div>
            <div className="border border-black/10 bg-[#f8f8f4] p-3">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Generated videos</div>
              <div className="mt-2 break-all text-black/70">{project.projectDir}/output</div>
            </div>
          </div>
        </DensePanel>
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.85fr_1.15fr]">
        <Card>
          <CardHeader>
            <CardTitle>Current State</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            <div>
              <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-steel">Tone</div>
              <div className="mt-2 text-sm text-black/70">{project.tone}</div>
            </div>
            <div>
              <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-steel">Length</div>
              <div className="mt-2 text-sm text-black/70">{project.videoLength}</div>
            </div>
            <div>
              <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-steel">Worker</div>
              <div className="mt-2 text-sm text-black/70">{project.workerStatus.state}</div>
            </div>
            <div>
              <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-steel">Missing assets</div>
              <div className="mt-2 text-sm text-black/70">{project.missingAssetCount}</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-3">
            <div>
              <CardTitle>Recent Deliverables</CardTitle>
              <p className="mt-1 text-sm text-black/55">Includes manifest outputs and older discovered `.mp4` files.</p>
            </div>
            <ButtonLink href={`/projects/${project.slug}/render`} variant="outline">
              Open Render
            </ButtonLink>
          </CardHeader>
          <CardContent>
            {project.deliverables.length ? (
              <div className="grid max-h-[360px] gap-3 overflow-y-auto pr-2 md:grid-cols-2">
                {project.deliverables.slice(0, 8).map((item) => (
                  <div key={`${item.name}-${item.video}`} className="border border-black/10 bg-[#f8f8f4] p-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="truncate text-sm font-semibold">{item.name}</div>
                      <Badge variant="outline">{item.duration ? `${item.duration}s` : "mp4"}</Badge>
                    </div>
                    {item.cover ? (
                      <img src={mediaUrl(item.cover) || undefined} alt={item.name} className="mt-3 aspect-[9/16] max-h-[180px] w-full object-cover" />
                    ) : null}
                    {item.video ? (
                      <Link href={mediaUrl(item.video) || "#"} className="mt-3 inline-block text-sm underline underline-offset-4">
                        Open video
                      </Link>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : (
              <div className="border border-dashed border-black/20 bg-[#f8f8f4] p-6 text-sm text-black/55">
                No generated videos discovered yet.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </ProjectWorkflowShell>
  );
}
