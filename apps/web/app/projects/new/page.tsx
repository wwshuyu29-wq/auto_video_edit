import { NewProjectForm } from "@/components/new-project-form";
import { getProductLibrary } from "@/lib/product-catalog";

export const dynamic = "force-dynamic";

export default async function NewProjectPage() {
  const library = await getProductLibrary();

  return <NewProjectForm activeProduct={library.activeProduct} products={library.products} />;
}
