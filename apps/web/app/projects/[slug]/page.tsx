import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { ProjectWorkflowShell } from "@/components/project-workflow-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getProjectDetail, mediaUrl } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

function EmptyState({ label }: { label: string }) {
  return (
    <div className="rounded-md border border-dashed border-black/20 bg-[#f8f8f4] p-4 text-sm text-black/55">
      {label}
    </div>
  );
}

function OutputStep({
  number,
  title,
  description,
  children
}: {
  number: string;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="border-b border-black/10 bg-white">
        <div className="flex items-start gap-4">
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-black text-sm font-semibold text-white">
            {number}
          </div>
          <div>
            <CardTitle>{title}</CardTitle>
            <p className="mt-1 text-sm leading-6 text-black/58">{description}</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-5">{children}</CardContent>
    </Card>
  );
}

export default async function ProjectOverviewPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  const videosWithCopy = project.videoVariants.filter((item) => item.publishingCopy).length;

  return (
    <ProjectWorkflowShell project={project} active="overview">
      <section className="grid gap-4 rounded-lg border border-black/10 bg-white p-5 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
        <div>
          <div className="text-sm font-semibold uppercase tracking-[0.18em] text-black/40">
            Project Output Review
          </div>
          <p className="mt-3 max-w-3xl text-base leading-7 text-black/68">
            按 5 个流程检查输出，并在最后确认视频、封面、标题和发布文案是否齐全。
          </p>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm sm:grid-cols-4 lg:min-w-[420px]">
          <div className="rounded-md bg-[#f8f8f4] p-3">
            <div className="text-black/45">Scripts</div>
            <div className="mt-1 text-xl font-semibold">{project.scripts.length}</div>
          </div>
          <div className="rounded-md bg-[#f8f8f4] p-3">
            <div className="text-black/45">Assets</div>
            <div className="mt-1 text-xl font-semibold">{project.assetLibrary.assetCount}</div>
          </div>
          <div className="rounded-md bg-[#f8f8f4] p-3">
            <div className="text-black/45">Videos</div>
            <div className="mt-1 text-xl font-semibold">{project.videoVariants.length}</div>
          </div>
          <div className="rounded-md bg-[#f8f8f4] p-3">
            <div className="text-black/45">Copy</div>
            <div className="mt-1 text-xl font-semibold">
              {videosWithCopy}/{project.videoVariants.length}
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-5">
        <OutputStep
          number="1"
          title="Reference output"
          description="对标视频拆解结果：内容逻辑和可复用的字幕节奏。"
        >
          <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="rounded-md border border-black/10 bg-[#f8f8f4] p-4">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-black/35">
                Content logic
              </div>
              <p className="mt-3 text-sm leading-6 text-black/70">{project.contentLogic}</p>
            </div>
            {project.captionSequence.length ? (
              <div className="grid gap-2">
                {project.captionSequence.map((line, index) => (
                  <div key={`${line}-${index}`} className="rounded-md border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm text-black/70">
                    <span className="mr-2 font-mono text-xs text-black/35">{index + 1}</span>
                    {line}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState label="No reference caption sequence found yet." />
            )}
          </div>
        </OutputStep>

        <OutputStep
          number="2"
          title="Script output"
          description="产品脚本结果：每个版本的标题、角度和脚本行数。"
        >
          {project.videoVariants.length ? (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {project.videoVariants.map((variant) => (
                <div key={variant.id} className="rounded-md border border-black/10 bg-[#f8f8f4] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <Badge variant="outline">{variant.scriptType || "script"}</Badge>
                    <span className="text-xs text-black/45">{variant.scriptBeats.length} lines</span>
                  </div>
                  <h3 className="mt-3 text-base font-semibold leading-snug">{variant.scriptTitle}</h3>
                  <p className="mt-2 line-clamp-3 text-sm leading-6 text-black/62">{variant.scriptAngle}</p>
                  {variant.scriptBeats.length ? (
                    <div className="mt-3 space-y-2 border-t border-black/10 pt-3">
                      {variant.scriptBeats.slice(0, 3).map((beat, index) => (
                        <div key={`${variant.id}-${index}`} className="text-xs leading-5 text-black/62">
                          <span className="font-semibold text-black">{beat.time || `Beat ${index + 1}`}</span>
                          {beat.onScreenText ? ` · ${beat.onScreenText}` : ""}
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <EmptyState label="No script output found yet." />
          )}
        </OutputStep>

        <OutputStep
          number="3"
          title="Assets and shot matching output"
          description="素材和镜头匹配结果：素材数量、缺口和每个 beat 对应的 clip。"
        >
          <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
            <div className="rounded-md border border-black/10 bg-[#f8f8f4] p-4">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-black/45">Asset status</div>
                  <div className="mt-1 font-semibold">{project.assetLibrary.status}</div>
                </div>
                <div>
                  <div className="text-black/45">Missing assets</div>
                  <div className="mt-1 font-semibold">{project.missingAssetCount}</div>
                </div>
              </div>
              <div className="mt-4 break-all text-xs leading-5 text-black/45">
                {project.assetLibrary.sourceMaterialDir}
              </div>
            </div>
            {project.editPreview.length ? (
              <div className="grid gap-2">
                {project.editPreview.map((item, index) => (
                  <div key={`${item.beat}-${index}`} className="rounded-md border border-black/10 bg-[#f8f8f4] p-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="secondary">{item.time || `Beat ${index + 1}`}</Badge>
                      <Badge variant="outline">{item.clipId}</Badge>
                    </div>
                    <div className="mt-2 text-sm font-medium">{item.beat}</div>
                    {item.text ? <div className="mt-1 text-sm text-black/58">{item.text}</div> : null}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState label="No shot matching output found yet." />
            )}
          </div>
        </OutputStep>

        <OutputStep
          number="4"
          title="Video and cover output"
          description="最终视频和封面结果：每个版本都应该能直接打开视频并看到封面。"
        >
          {project.videoVariants.length ? (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {project.videoVariants.map((variant) => (
                <div key={variant.id} className="overflow-hidden rounded-md border border-black/10 bg-[#f8f8f4]">
                  {variant.cover ? (
                    <img src={mediaUrl(variant.cover) || undefined} alt={variant.name} className="aspect-[9/16] w-full object-cover" />
                  ) : (
                    <div className="grid aspect-[9/16] place-items-center bg-[#202321] px-5 text-center text-sm text-white/60">
                      Cover missing
                    </div>
                  )}
                  <div className="p-3">
                    <div className="truncate text-sm font-semibold">{variant.name}</div>
                    <div className="mt-2 flex items-center justify-between gap-3">
                      <Badge variant="outline">{variant.duration ? `${variant.duration}s` : "mp4"}</Badge>
                      {variant.video ? (
                        <Link href={mediaUrl(variant.video) || "#"} target="_blank" className="text-sm underline underline-offset-4">
                          Open video
                        </Link>
                      ) : (
                        <span className="text-xs text-black/40">Video missing</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState label="No rendered video output found yet." />
          )}
        </OutputStep>

        <OutputStep
          number="5"
          title="Title and publishing copy output"
          description="发布结果：每条视频对应标题、caption、hashtags 和关键词。"
        >
          {project.videoVariants.length ? (
            <div className="grid gap-4 lg:grid-cols-2">
              {project.videoVariants.map((variant) => {
                const copy = variant.publishingCopy;
                return (
                  <div key={variant.id} className="rounded-md border border-black/10 bg-[#f8f8f4] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="truncate text-base font-semibold">{variant.name}</h3>
                      <Badge variant={copy ? "secondary" : "outline"}>{copy ? "copy ready" : "copy missing"}</Badge>
                    </div>
                    <div className="mt-4 grid gap-3">
                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-black/35">
                          Title
                        </div>
                        <p className="mt-1 text-sm leading-6 text-black/75">
                          {copy?.recommendedTitle || variant.scriptTitle}
                        </p>
                      </div>
                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-black/35">
                          Caption
                        </div>
                        <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-black/70">
                          {copy?.recommendedCaption || "No publishing caption generated yet."}
                        </p>
                      </div>
                      {copy?.hashtags?.length ? (
                        <div className="flex flex-wrap gap-2">
                          {copy.hashtags.map((tag) => (
                            <Badge key={tag} variant="outline">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      ) : null}
                      {copy?.keywords?.length ? (
                        <div className="text-xs leading-5 text-black/45">
                          Keywords: {copy.keywords.join(", ")}
                        </div>
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState label="No publishing output found yet." />
          )}
        </OutputStep>
      </div>
    </ProjectWorkflowShell>
  );
}
