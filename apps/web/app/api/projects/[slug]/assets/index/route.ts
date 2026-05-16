import { revalidatePath } from "next/cache";
import { indexProjectAssets } from "@/lib/project-assets";

export async function POST(_request: Request, context: { params: Promise<{ slug: string }> }) {
  try {
    const { slug } = await context.params;
    const assetLibrary = await indexProjectAssets(slug);

    revalidatePath("/");
    revalidatePath(`/projects/${slug}`);

    return Response.json({ assetLibrary }, { status: 200 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to index project assets.";
    return Response.json({ error: message }, { status: 500 });
  }
}
