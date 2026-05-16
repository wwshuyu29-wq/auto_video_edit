import path from "path";
import { revalidatePath } from "next/cache";
import { startWorkerRun } from "@/lib/worker-status";

const REPO_ROOT = path.resolve(process.cwd(), "../..");
const PROJECTS_ROOT = path.join(REPO_ROOT, "projects");

function projectDirFromSlug(slug: string) {
  const [group, ...rest] = slug.split("__");
  return path.join(PROJECTS_ROOT, group, rest.join("__"));
}

export async function POST(_request: Request, context: { params: Promise<{ slug: string }> }) {
  try {
    const { slug } = await context.params;
    const projectDir = projectDirFromSlug(slug);
    const status = await startWorkerRun(projectDir);
    revalidatePath("/");
    revalidatePath(`/projects/${slug}`);
    return Response.json(status, { status: 202 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to start worker.";
    return Response.json({ error: message }, { status: 500 });
  }
}

