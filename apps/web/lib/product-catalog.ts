import { promises as fs } from "fs";
import path from "path";

const REPO_ROOT = path.resolve(process.cwd(), "../..");
const PRODUCT_LIBRARY_PATH = path.join(REPO_ROOT, "product-library", "products.json");

export type ProductProfile = {
  product_name: string;
  one_liner: string;
  target_users?: string[];
  core_features?: Array<{
    feature_name: string;
    description: string;
    user_benefit?: string;
    visual_need?: string;
  }>;
  most_painful_user_scenarios?: string[];
  forbidden_claims?: string[];
  good_tiktok_angles?: string[];
  source_grounding_note?: string;
  allowed_claim_boundaries?: string[];
};

type ProductLibrary = {
  active_product?: string;
  rules?: string[];
  products?: ProductProfile[];
};

async function readJson<T>(target: string): Promise<T | null> {
  try {
    const raw = await fs.readFile(target, "utf8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export async function getProductLibrary() {
  const data = await readJson<ProductLibrary>(PRODUCT_LIBRARY_PATH);
  return {
    activeProduct: data?.active_product || "",
    rules: data?.rules || [],
    products: data?.products || []
  };
}

export async function getProductByName(productName: string) {
  const library = await getProductLibrary();
  return library.products.find((product) => product.product_name === productName) || null;
}

