import { projectDirFromSlug } from "@/lib/project-paths";
import { runProjectPreflight } from "@/lib/project-preflight";

export async function GET(_request: Request, context: { params: Promise<{ slug: string }> }) {
  try {
    const { slug } = await context.params;
    const projectDir = projectDirFromSlug(slug);
    return Response.json(await runProjectPreflight(projectDir));
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to run preflight.";
    return Response.json({ error: message }, { status: 500 });
  }
}
