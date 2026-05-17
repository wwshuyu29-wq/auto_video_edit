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
    const type = contentType(resolved);
    const range = request.headers.get("range");
    const stat = await fs.stat(resolved);

    if (range && type.startsWith("video/")) {
      const [startText, endText] = range.replace(/bytes=/, "").split("-");
      const start = Number.parseInt(startText, 10);
      const end = endText ? Number.parseInt(endText, 10) : Math.min(start + 1024 * 1024, stat.size - 1);
      const safeStart = Number.isFinite(start) ? start : 0;
      const safeEnd = Number.isFinite(end) ? Math.min(end, stat.size - 1) : stat.size - 1;
      const data = await fs.readFile(resolved);
      const chunk = data.subarray(safeStart, safeEnd + 1);
      return new Response(chunk, {
        status: 206,
        headers: {
          "Content-Type": type,
          "Content-Length": String(chunk.length),
          "Content-Range": `bytes ${safeStart}-${safeEnd}/${stat.size}`,
          "Accept-Ranges": "bytes",
          "Cache-Control": "no-store"
        }
      });
    }

    const data = await fs.readFile(resolved);
    return new Response(data, {
      headers: {
        "Content-Type": type,
        "Content-Length": String(stat.size),
        "Accept-Ranges": type.startsWith("video/") ? "bytes" : "none",
        "Cache-Control": "no-store"
      }
    });
  } catch {
    return new Response("Not found", { status: 404 });
  }
}
