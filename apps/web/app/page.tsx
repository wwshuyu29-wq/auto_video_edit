import Link from "next/link";
import {
  Captions,
  Clapperboard,
  FileText,
  FolderUp,
  Video
} from "lucide-react";
import { GeneratedVideoCard } from "@/components/generated-video-card";
import { getDashboardMetrics, getGeneratedVideos } from "@/lib/repo-data";

export const dynamic = "force-dynamic";

const flowSteps = [
  {
    icon: Video,
    title: "1. Reference",
    description: "查看对标视频拆解、内容逻辑和字幕节奏。"
  },
  {
    icon: FileText,
    title: "2. Script",
    description: "查看产品脚本、钩子、分镜文案和口播。"
  },
  {
    icon: FolderUp,
    title: "3. Assets",
    description: "查看素材库、镜头标签和每个脚本 beat 匹配到的素材。"
  },
  {
    icon: Clapperboard,
    title: "4. Video & Cover",
    description: "查看生成视频、封面、字幕文件和渲染报告。"
  },
  {
    icon: Captions,
    title: "5. Publish Copy",
    description: "查看标题、发布文案、hashtags、关键词和注意事项。"
  }
];

function ProjectLink({
  project
}: {
  project: Awaited<ReturnType<typeof getDashboardMetrics>>["projects"][number];
}) {
  return (
    <Link
      href={`/projects/${project.slug}`}
      className="group block rounded-lg border border-ink/10 bg-white px-5 py-5 transition hover:-translate-y-0.5 hover:border-ink/25 hover:shadow-[0_18px_45px_rgba(31,46,43,0.08)]"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink/45">
            {project.productName}
          </div>
          <h3 className="mt-3 text-xl font-semibold leading-tight text-ink">
            {project.headline}
          </h3>
        </div>
        <span className="rounded-full border border-ink/10 px-3 py-1 text-xs text-ink/55">
          {project.deliverableCount} outputs
        </span>
      </div>
      <p className="mt-4 text-sm leading-6 text-ink/62">{project.name}</p>
      <div className="mt-5 text-sm font-medium text-ink transition group-hover:translate-x-1">
        Continue this video
      </div>
    </Link>
  );
}

export default async function HomePage() {
  const [data, generatedVideos] = await Promise.all([getDashboardMetrics(), getGeneratedVideos()]);
  const featuredProjects = [...data.projects]
    .sort((a, b) => {
      if (a.deliverableCount !== b.deliverableCount) return b.deliverableCount - a.deliverableCount;
      return a.updatedAt < b.updatedAt ? 1 : -1;
    })
    .slice(0, 3);

  return (
    <div className="space-y-14 pb-12">
      <section className="grid gap-8 border-b border-ink/10 pb-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-end">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold uppercase tracking-[0.18em] text-ink/45">
            Auto Video Console
          </div>
          <h1 className="mt-4 text-5xl font-semibold leading-[1.02] tracking-[-0.04em] text-ink lg:text-6xl">
            查看每一步输出，最后交付视频和发布文案。
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-ink/68">
            这个网站只做一件事：把短视频生产流程拆成 5 步，让 reference、script、assets、video/cover、title/caption 都能被检查。
          </p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/projects/new"
              className="inline-flex items-center justify-center rounded-md bg-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink/90"
            >
              Start a video project
            </Link>
            {featuredProjects[0] ? (
              <Link
                href={`/projects/${featuredProjects[0].slug}`}
                className="inline-flex items-center justify-center rounded-md border border-ink/12 bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:border-ink/28"
              >
                Open latest project
              </Link>
            ) : null}
          </div>
        </div>

        <div className="grid gap-3 rounded-lg border border-ink/10 bg-white p-4">
          {flowSteps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.title} className="grid grid-cols-[36px_minmax(0,1fr)] gap-3 border-b border-ink/10 pb-3 last:border-b-0 last:pb-0">
                <div className="grid h-9 w-9 place-items-center rounded-md bg-[#eef4f1] text-[#3f8f78]">
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink/35">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <h2 className="text-sm font-semibold text-ink">{step.title}</h2>
                  </div>
                  <p className="mt-1 text-sm leading-6 text-ink/58">{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {featuredProjects.length > 0 ? (
        <section>
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div>
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-ink/45">
                Projects
              </div>
              <h2 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-ink">
                打开项目查看 5 步输出
              </h2>
            </div>
            <Link
              href="/projects/new"
              className="inline-flex items-center justify-center rounded-md border border-ink/12 bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:border-ink/28"
            >
              Create project
            </Link>
          </div>
          <div className="mt-8 grid gap-4 lg:grid-cols-3">
            {featuredProjects.map((project) => (
              <ProjectLink key={project.slug} project={project} />
            ))}
          </div>
        </section>
      ) : null}

      {generatedVideos.length > 0 ? (
        <section>
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div>
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-ink/45">
                Final outputs
              </div>
              <h2 className="mt-4 text-4xl font-semibold tracking-[-0.03em] text-ink">
                已生成的视频和封面
              </h2>
              <p className="mt-4 max-w-2xl text-base leading-7 text-ink/64">
                这里只展示最终成片入口。完整标题和文案在项目详情页第 5 步。
              </p>
            </div>
            <Link
              href="/projects/new"
              className="inline-flex items-center justify-center rounded-md border border-ink/12 bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:border-ink/28"
            >
              Make another video
            </Link>
          </div>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {generatedVideos.map((video) => (
              <GeneratedVideoCard key={video.id} video={video} />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
