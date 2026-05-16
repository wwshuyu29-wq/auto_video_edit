import { revalidatePath } from "next/cache";
import { createProjectScaffold } from "@/lib/project-scaffold";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      projectName?: string;
      productName?: string;
      referenceAccountUrl?: string;
      referenceVideoUrl?: string;
      materialDirectory?: string;
      templateName?: string;
      videoLength?: string;
      tone?: string;
      notes?: string;
    };

    if (!body.projectName?.trim()) {
      return Response.json({ error: "Project name is required." }, { status: 400 });
    }

    if (!body.productName?.trim()) {
      return Response.json({ error: "Product is required." }, { status: 400 });
    }

    if (!body.referenceAccountUrl?.trim() && !body.referenceVideoUrl?.trim()) {
      return Response.json({ error: "Add at least one TikTok reference URL." }, { status: 400 });
    }

    const created = await createProjectScaffold({
      projectName: body.projectName.trim(),
      productName: body.productName.trim(),
      referenceAccountUrl: body.referenceAccountUrl?.trim() || "",
      referenceVideoUrl: body.referenceVideoUrl?.trim() || "",
      materialDirectory: body.materialDirectory?.trim() || "",
      templateName: body.templateName?.trim() || "",
      videoLength: body.videoLength?.trim() || "",
      tone: body.tone?.trim() || "",
      notes: body.notes?.trim() || ""
    });

    revalidatePath("/");
    revalidatePath(`/projects/${created.slug}`);

    return Response.json(created, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to create project scaffold.";
    return Response.json({ error: message }, { status: 500 });
  }
}

