import { revalidatePath } from "next/cache";
import { readEditableArtifact, updateEditableArtifact } from "@/lib/project-artifacts";

export async function GET(_request: Request, context: { params: Promise<{ slug: string; artifact: string }> }) {
  try {
    const { slug, artifact } = await context.params;
    return Response.json(await readEditableArtifact(slug, artifact));
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to read artifact.";
    return Response.json({ error: message }, { status: 400 });
  }
}

export async function PATCH(request: Request, context: { params: Promise<{ slug: string; artifact: string }> }) {
  try {
    const { slug, artifact } = await context.params;
    const body = (await request.json()) as { data?: unknown };
    if (body.data === undefined) {
      return Response.json({ error: "data is required." }, { status: 400 });
    }

    const updated = await updateEditableArtifact(slug, artifact, body.data);

    revalidatePath("/");
    revalidatePath(`/projects/${slug}`);

    return Response.json(updated, { status: 200 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to update artifact.";
    return Response.json({ error: message }, { status: 400 });
  }
}
