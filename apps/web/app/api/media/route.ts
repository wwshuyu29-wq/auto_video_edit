import { promises as fs } from "fs";
import path from "path";

const REPO_ROOT = path.resolve(process.cwd(), "../..");

function contentType(filePath: string) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".png") return "image/png";
  if (ext === ".mp4") return "video/mp4";
  if (ext === ".mov") return "video/quicktime";
  if (ext === ".json") return "application/json";
  return "application/octet-stream";
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const rawPath = searchParams.get("path");
  if (!rawPath) {
    return new Response("Missing path", { status: 400 });
  }

  const resolved = path.resolve(rawPath);
  if (!resolved.startsWith(REPO_ROOT)) {
    return new Response("Forbidden", { status: 403 });
  }

  try {
    const data = await fs.readFile(resolved);
    return new Response(data, {
      headers: {
        "Content-Type": contentType(resolved),
        "Cache-Control": "no-store"
      }
    });
  } catch {
    return new Response("Not found", { status: 404 });
  }
}
