import { revalidatePath } from "next/cache";
import { indexProjectAssets, readAssetLibraryForSlug, uploadProjectAssets } from "@/lib/project-assets";

export async function GET(_request: Request, context: { params: Promise<{ slug: string }> }) {
  try {
    const { slug } = await context.params;
    const assetLibrary = await readAssetLibraryForSlug(slug);
    return Response.json(assetLibrary || { assets: [], status: "not_indexed", asset_count: 0 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to read asset library.";
    return Response.json({ error: message }, { status: 500 });
  }
}

export async function POST(request: Request, context: { params: Promise<{ slug: string }> }) {
  try {
    const { slug } = await context.params;
    const formData = await request.formData();
    const files = formData.getAll("files").filter((item): item is File => item instanceof File);
    const result =
      files.length > 0
        ? await uploadProjectAssets(slug, files)
        : { savedFiles: [], assetLibrary: await indexProjectAssets(slug) };

    revalidatePath("/");
    revalidatePath(`/projects/${slug}`);

    return Response.json(result, { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to upload or index assets.";
    return Response.json({ error: message }, { status: 500 });
  }
}
