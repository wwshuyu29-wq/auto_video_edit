import { revalidatePath } from "next/cache";
import { projectDirFromSlug } from "@/lib/project-paths";
import { runProjectPreflight } from "@/lib/project-preflight";
import { startWorkerRun } from "@/lib/worker-status";

export async function POST(_request: Request, context: { params: Promise<{ slug: string }> }) {
  try {
    const { slug } = await context.params;
    const projectDir = projectDirFromSlug(slug);
    const preflight = await runProjectPreflight(projectDir);
    if (preflight.status === "blocked") {
      return Response.json(
        {
          error: `Worker preflight failed: ${preflight.blockerCount} blocker${preflight.blockerCount === 1 ? "" : "s"}.`,
          preflight
        },
        { status: 409 }
      );
    }

    const status = await startWorkerRun(projectDir);
    revalidatePath("/");
    revalidatePath(`/projects/${slug}`);
    return Response.json(status, { status: 202 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to start worker.";
    return Response.json({ error: message }, { status: 500 });
  }
}
