import Link from "next/link";

const flowSteps = [
  {
    marker: "01",
    title: "1. Reference",
    description: "拆解对标视频的 hook、字幕节奏和内容逻辑。"
  },
  {
    marker: "02",
    title: "2. Script",
    description: "为产品写脚本、分镜文案和屏幕字幕。"
  },
  {
    marker: "03",
    title: "3. Assets",
    description: "整理素材库，并把不同功能的视频标注成可复用镜头。"
  },
  {
    marker: "04",
    title: "4. Render",
    description: "按 shot plan 生成视频、封面和渲染报告。"
  },
  {
    marker: "05",
    title: "5. Publish",
    description: "整理发布标题、文案、tags 和注意事项。"
  }
];

const projectLinks = [
  {
    label: "StudyingWithYun Batch",
    href: "/projects/batch__studyingwithyun-7637665419305782546",
    description: "当前批量项目入口，适合继续检查 FigPad / Citely / Clearfy。"
  },
  {
    label: "Create New Project",
    href: "/projects/new",
    description: "新建一个产品视频项目，上传素材并开始生成流程。"
  }
];

export default function HomePage() {
  return (
    <div className="space-y-12 pb-12">
      <section className="grid gap-8 border-b border-ink/10 pb-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-end">
        <div className="max-w-3xl">
          <div className="text-sm font-semibold uppercase tracking-[0.18em] text-ink/45">
            Auto Video Console
          </div>
          <h1 className="mt-4 text-5xl font-semibold leading-[1.02] text-ink lg:text-6xl">
            管理素材、脚本和视频成片。
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-ink/68">
            先从项目入口进入，后面我们可以继续改页面结构、素材标注方式和生成流程。
          </p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/projects/new"
              className="inline-flex items-center justify-center rounded-md bg-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink/90"
            >
              Start a video project
            </Link>
            <Link
              href="/projects/batch__studyingwithyun-7637665419305782546"
              className="inline-flex items-center justify-center rounded-md border border-ink/12 bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:border-ink/28"
            >
              Open current batch
            </Link>
          </div>
        </div>

        <div className="grid gap-3 rounded-lg border border-ink/10 bg-white p-4">
          {flowSteps.map((step, index) => {
            return (
              <div
                key={step.title}
                className="grid grid-cols-[36px_minmax(0,1fr)] gap-3 border-b border-ink/10 pb-3 last:border-b-0 last:pb-0"
              >
                <div className="grid h-9 w-9 place-items-center rounded-md bg-[#eef4f1] text-[#3f8f78]">
                  <span className="font-mono text-xs font-semibold">{step.marker}</span>
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

      <section>
        <div className="text-sm font-semibold uppercase tracking-[0.18em] text-ink/45">
          Projects
        </div>
        <h2 className="mt-4 text-4xl font-semibold text-ink">选择一个项目继续编辑</h2>
        <div className="mt-8 grid gap-4 lg:grid-cols-2">
          {projectLinks.map((project) => (
            <Link
              key={project.href}
              href={project.href}
              className="group rounded-lg border border-ink/10 bg-white px-5 py-5 transition hover:-translate-y-0.5 hover:border-ink/25 hover:shadow-[0_18px_45px_rgba(31,46,43,0.08)]"
            >
              <h3 className="text-xl font-semibold text-ink">{project.label}</h3>
              <p className="mt-3 text-sm leading-6 text-ink/62">{project.description}</p>
              <div className="mt-5 text-sm font-medium text-ink transition group-hover:translate-x-1">
                Open project
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
