import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
export const WEB_ROOT = path.resolve(SCRIPT_DIR, "..");
export const REPO_ROOT = path.resolve(WEB_ROOT, "../..");
export const PROJECTS_ROOT = path.join(REPO_ROOT, "projects");

export const MEDIA_EXTENSIONS = new Set([
  ".mp4",
  ".mov",
  ".m4v",
  ".webm",
  ".jpg",
  ".jpeg",
  ".png",
  ".srt",
  ".json"
]);

export const CONTENT_TYPES = new Map([
  [".mp4", "video/mp4"],
  [".mov", "video/quicktime"],
  [".m4v", "video/x-m4v"],
  [".webm", "video/webm"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".png", "image/png"],
  [".srt", "application/x-subrip"],
  [".json", "application/json"]
]);

export async function loadEnvFile(filePath) {
  if (!existsSync(filePath)) return;
  const raw = await fs.readFile(filePath, "utf8");
  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const equals = trimmed.indexOf("=");
    if (equals === -1) continue;
    const key = trimmed.slice(0, equals).trim();
    let value = trimmed.slice(equals + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (!process.env[key]) process.env[key] = value;
  }
}

async function listFiles(root) {
  const entries = await fs.readdir(root, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(root, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await listFiles(fullPath)));
    } else if (entry.isFile()) {
      files.push(fullPath);
    }
  }

  return files;
}

export async function projectRoots(args) {
  if (args.all) {
    const productDirs = await fs.readdir(PROJECTS_ROOT, { withFileTypes: true });
    const roots = [];
    for (const productDir of productDirs) {
      if (!productDir.isDirectory()) continue;
      const productPath = path.join(PROJECTS_ROOT, productDir.name);
      const projectDirs = await fs.readdir(productPath, { withFileTypes: true });
      for (const projectDir of projectDirs) {
        if (projectDir.isDirectory()) roots.push(path.join(productPath, projectDir.name));
      }
    }
    return roots.sort();
  }

  const cleanProject = args.project.replace(/^\/+/, "");
  const candidates = [
    path.resolve(REPO_ROOT, cleanProject),
    path.resolve(PROJECTS_ROOT, cleanProject),
    path.resolve(PROJECTS_ROOT, cleanProject.replace(/^projects\//, ""))
  ];
  const found = candidates.find((candidate) => existsSync(candidate));
  if (!found) throw new Error(`Project not found: ${args.project}`);
  return [found];
}

export function isTemporary(relativePath) {
  const parts = relativePath.split(path.sep);
  return parts.includes("preview_render") || parts.includes("render_work") || parts.includes("qa_frames") || parts.includes("segments") || parts.some((part) => part.endsWith("_workdir"));
}

function shouldInclude(filePath, args) {
  const ext = path.extname(filePath).toLowerCase();
  if (!MEDIA_EXTENSIONS.has(ext)) return false;
  const relativeRepoPath = path.relative(REPO_ROOT, filePath);
  if (!args.includeTemporary && isTemporary(relativeRepoPath)) return false;
  if (relativeRepoPath.includes(`${path.sep}.DS_Store`)) return false;
  return true;
}

function classifyAsset(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const relativeRepoPath = path.relative(REPO_ROOT, filePath);
  const parts = relativeRepoPath.split(path.sep);
  const basename = path.basename(filePath).toLowerCase();

  if (isTemporary(relativeRepoPath)) return "temporary";
  if (basename.includes("render_report")) return "render_report";
  if (ext === ".srt") return "subtitle_file";
  if (ext === ".json") return "json_artifact";
  if (parts.includes("materials") && parts.includes("raw")) return "raw_video";
  if (parts.includes("references") && [".mp4", ".mov", ".m4v", ".webm"].includes(ext)) return "reference_video";
  if (parts.includes("references") && [".jpg", ".jpeg", ".png"].includes(ext)) return "reference_frame";
  if (parts.includes("output") && [".jpg", ".jpeg", ".png"].includes(ext)) return "cover_image";
  if (parts.includes("output") && [".mp4", ".mov", ".m4v", ".webm"].includes(ext)) return "final_video";
  return "json_artifact";
}

export function storageKey(filePath, args) {
  const relativeRepoPath = path.relative(REPO_ROOT, filePath).split(path.sep).join("/");
  return [args.prefix, relativeRepoPath].filter(Boolean).join("/");
}

async function checksum(filePath) {
  const hash = createHash("sha256");
  const file = await fs.open(filePath, "r");
  try {
    for await (const chunk of file.createReadStream()) hash.update(chunk);
  } finally {
    await file.close();
  }
  return `sha256:${hash.digest("hex")}`;
}

async function buildAssetRecord(filePath, args) {
  const stats = await fs.stat(filePath);
  const relativeRepoPath = path.relative(REPO_ROOT, filePath).split(path.sep).join("/");
  const projectPathParts = relativeRepoPath.split("/");
  const projectId = projectPathParts.slice(1, 3).join("/");
  const key = storageKey(filePath, args);
  const kind = classifyAsset(filePath);

  return {
    asset_id: createHash("sha1").update(relativeRepoPath).digest("hex").slice(0, 16),
    project_id: projectId,
    kind,
    local_path: relativeRepoPath,
    storage_key: key,
    content_type: CONTENT_TYPES.get(path.extname(filePath).toLowerCase()) || "application/octet-stream",
    bytes: stats.size,
    checksum: await checksum(filePath),
    created_at: new Date().toISOString()
  };
}

export async function collectAssets(args) {
  const roots = await projectRoots(args);
  const selectedFiles = [];

  for (const root of roots) {
    const files = await listFiles(root);
    selectedFiles.push(...files.filter((file) => shouldInclude(file, args)));
  }

  const assets = [];
  for (const file of selectedFiles.sort()) {
    assets.push(await buildAssetRecord(file, args));
  }
  return assets;
}

export function summarize(assets) {
  const summary = {};
  for (const asset of assets) {
    summary[asset.kind] = summary[asset.kind] || { count: 0, bytes: 0 };
    summary[asset.kind].count += 1;
    summary[asset.kind].bytes += asset.bytes;
  }
  return summary;
}
