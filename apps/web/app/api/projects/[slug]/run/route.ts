import { revalidatePath } from "next/cache";
import { projectDirFromSlug } from "@/lib/project-paths";
import { startWorkerRun } from "@/lib/worker-status";

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
