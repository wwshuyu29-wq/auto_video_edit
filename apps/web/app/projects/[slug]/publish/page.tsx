import Link from "next/link";
import { notFound } from "next/navigation";
import { ProjectWorkflowShell, DensePanel } from "@/components/project-workflow-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getProjectDetail, mediaUrl } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

function CopyBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-black/10 bg-white p-3">
      <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-black/42">{label}</div>
      <div className="mt-2 text-sm leading-6 text-black/76">{value || "Not generated yet"}</div>
    </div>
  );
}

export default async function PublishPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProjectDetail(slug);
  if (!project) notFound();

  const withCopy = project.videoVariants.filter((variant) => variant.publishingCopy);

  return (
    <ProjectWorkflowShell project={project} active="publish">
      <div className="grid gap-5 xl:grid-cols-[0.74fr_1.26fr]">
        <DensePanel title="Publishing Files" description="以后交付视频时，这里必须同时出现标题、文案、hashtags 和关键词。">
          <div className="grid gap-3 text-sm">
            <div className="border border-black/10 bg-[#f8f8f4] p-3">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Copy card</div>
              <div className="mt-2 break-all text-black/70">{project.publishingCopyPath || "Not generated yet"}</div>
            </div>
            <div className="border border-black/10 bg-[#f8f8f4] p-3">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Readable delivery</div>
              <div className="mt-2 break-all text-black/70">{project.publishingCopyDeliveryPath || "Not generated yet"}</div>
            </div>
            <div className="border border-black/10 bg-[#f8f8f4] p-3">
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Status</div>
              <div className="mt-2 text-black/70">
                {withCopy.length} / {project.videoVariants.length} videos have publishing copy
              </div>
            </div>
          </div>
        </DensePanel>

        <Card>
          <CardHeader>
            <CardTitle>Publishing Copy</CardTitle>
            <p className="mt-1 text-sm text-black/55">按视频版本配对展示，发布 TikTok 时直接使用对应这一组。</p>
          </CardHeader>
          <CardContent>
            <div className="grid max-h-[760px] gap-4 overflow-y-auto pr-2">
              {project.videoVariants.map((variant) => {
                const copy = variant.publishingCopy;
                return (
                  <div key={variant.id} className="border border-black/10 bg-[#f8f8f4] p-4">
                    <div className="grid gap-4 lg:grid-cols-[120px_minmax(0,1fr)]">
                      <div>
                        {variant.cover ? (
                          <img src={mediaUrl(variant.cover) || undefined} alt={variant.name} className="aspect-[9/16] w-full object-cover" />
                        ) : null}
                        {variant.video ? (
                          <Link href={mediaUrl(variant.video) || "#"} className="mt-3 block text-xs underline underline-offset-4">
                            Open video
                          </Link>
                        ) : null}
                      </div>

                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant="outline">{variant.name}</Badge>
                          <Badge variant={copy ? "secondary" : "destructive"}>{copy ? "copy ready" : "missing copy"}</Badge>
                        </div>
                        <div className="mt-4 grid gap-3">
                          <CopyBlock label="Recommended title" value={copy?.recommendedTitle || ""} />
                          <CopyBlock label="Recommended caption" value={copy?.recommendedCaption || ""} />
                          <CopyBlock label="Hashtags" value={copy?.hashtags.join(" ") || ""} />
                          <CopyBlock label="Keywords" value={copy?.keywords.join(", ") || ""} />
                        </div>

                        {copy?.postingNotes?.length ? (
                          <div className="mt-3 border border-black/10 bg-white p-3">
                            <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-black/42">Posting notes</div>
                            <ul className="mt-2 grid gap-1 text-sm leading-6 text-black/68">
                              {copy.postingNotes.map((note) => (
                                <li key={note}>{note}</li>
                              ))}
                            </ul>
                          </div>
                        ) : null}

                        {copy?.complianceNotes?.length ? (
                          <div className="mt-3 border border-black/10 bg-white p-3">
                            <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-black/42">Compliance</div>
                            <ul className="mt-2 grid gap-1 text-sm leading-6 text-black/68">
                              {copy.complianceNotes.map((note) => (
                                <li key={note}>{note}</li>
                              ))}
                            </ul>
                          </div>
                        ) : null}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </ProjectWorkflowShell>
  );
}
