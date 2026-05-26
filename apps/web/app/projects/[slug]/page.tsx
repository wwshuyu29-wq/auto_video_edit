import { promises as fs } from "fs";
import path from "path";
import Link from "next/link";
import { notFound } from "next/navigation";
import { projectDirFromSlug } from "@/lib/project-paths";

export const dynamic = "force-dynamic";

type ProductSummary = {
  name: string;
  dir: string;
  status: string;
  video?: string;
  report?: string;
};

const repoRoot = path.resolve(process.cwd(), "../..");

async function exists(target: string) {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
}

async function readJson(target: string) {
  try {
    return JSON.parse(await fs.readFile(target, "utf8"));
  } catch {
    return null;
  }
}

async function readProductSummary(dir: string): Promise<ProductSummary> {
  const name = path.basename(dir);
  const job = await readJson(path.join(dir, "project_job.json"));
  const reportPath = path.join(dir, "output", "render_report.json");
  const report = await readJson(reportPath);
  const video =
    report?.video ||
    report?.output_video ||
    report?.outputs?.preview_video ||
    report?.outputs?.final_video ||
    job?.delivery?.preview_video ||
    job?.delivery?.final_video ||
    undefined;

  return {
    name: job?.product_name || name,
    dir,
    status: report?.status || job?.status || "ready",
    video: video
      ? path.isAbsolute(video)
        ? video
        : video.startsWith("projects/")
          ? path.join(repoRoot, video)
          : path.join(dir, video)
      : undefined,
    report: (await exists(reportPath)) ? reportPath : undefined
  };
}

async function getProjectSummaries(root: string) {
  if (!(await exists(root))) return null;
  const rootJob = path.join(root, "project_job.json");
  if (await exists(rootJob)) return [await readProductSummary(root)];

  const entries = await fs.readdir(root, { withFileTypes: true });
  const productDirs = entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(root, entry.name));

  const summaries = [];
  for (const dir of productDirs) {
    if ((await exists(path.join(dir, "project_job.json"))) || (await exists(path.join(dir, "output")))) {
      summaries.push(await readProductSummary(dir));
    }
  }
  return summaries;
}

function fileUrl(target?: string) {
  if (!target) return undefined;
  return `/api/media?path=${encodeURIComponent(target)}`;
}

export default async function ProjectOverviewPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const projectDir = projectDirFromSlug(slug);
  const products = await getProjectSummaries(projectDir);
  if (!products) notFound();

  return (
    <div className="space-y-8 pb-12">
      <section className="rounded-lg border border-black/10 bg-white p-5">
        <div className="text-sm font-semibold uppercase tracking-[0.18em] text-black/40">
          Project Workspace
        </div>
        <h1 className="mt-3 text-4xl font-semibold text-black">{path.basename(projectDir)}</h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-black/64">
          这是轻量项目页，先保证页面可以快速打开。后面可以继续把素材标注、功能分组、视频预览和生成按钮加回来。
        </p>
        <div className="mt-4 break-all rounded-md bg-[#f8f8f4] px-3 py-2 font-mono text-xs text-black/50">
          {projectDir}
        </div>
      </section>

      <section>
        <div className="flex items-end justify-between gap-4">
          <div>
            <div className="text-sm font-semibold uppercase tracking-[0.18em] text-black/40">
              Products
            </div>
            <h2 className="mt-3 text-3xl font-semibold text-black">当前产品和输出</h2>
          </div>
          <Link
            href="/"
            className="rounded-md border border-black/12 bg-white px-4 py-2 text-sm font-semibold text-black"
          >
            Back home
          </Link>
        </div>

        {products.length ? (
          <div className="mt-6 grid gap-4 lg:grid-cols-3">
            {products.map((product) => (
              <article key={product.dir} className="rounded-lg border border-black/10 bg-white p-5">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-xl font-semibold capitalize text-black">{product.name}</h3>
                  <span className="rounded-md bg-[#eef4f1] px-2 py-1 text-xs font-medium text-black/60">
                    {product.status}
                  </span>
                </div>
                <div className="mt-4 break-all font-mono text-xs leading-5 text-black/45">
                  {product.dir}
                </div>
                <div className="mt-5 flex flex-wrap gap-2">
                  {product.video ? (
                    <Link
                      href={fileUrl(product.video) || "#"}
                      target="_blank"
                      className="rounded-md bg-black px-3 py-2 text-sm font-semibold text-white"
                    >
                      Open video
                    </Link>
                  ) : null}
                  {product.report ? (
                    <Link
                      href={fileUrl(product.report) || "#"}
                      target="_blank"
                      className="rounded-md border border-black/12 px-3 py-2 text-sm font-semibold text-black"
                    >
                      Render report
                    </Link>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="mt-6 rounded-lg border border-dashed border-black/20 bg-white p-5 text-sm text-black/55">
            这个目录下还没有检测到可显示的产品项目。
          </div>
        )}
      </section>
    </div>
  );
}
