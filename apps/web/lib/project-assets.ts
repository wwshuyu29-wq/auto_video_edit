import { execFile } from "child_process";
import { promises as fs } from "fs";
import path from "path";
import { promisify } from "util";
import { projectDirFromSlug } from "@/lib/project-paths";

const execFileAsync = promisify(execFile);

const VIDEO_EXTENSIONS = new Set([".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"]);

type ProbeStream = {
  codec_type?: string;
  codec_name?: string;
  width?: number;
  height?: number;
  duration?: string;
  avg_frame_rate?: string;
};

type ProbeData = {
  streams?: ProbeStream[];
  format?: {
    duration?: string;
  };
};

export type AssetLibraryFile = {
  assets: AssetEntry[];
  status: string;
  source_material_dir: string;
  asset_count: number;
  updated_at: string;
  note?: string;
};

export type AssetEntry = {
  clip_id: string;
  file_path: string;
  duration: number;
  orientation: string;
  quality_score: number;
  shot_type: string;
  camera_motion: string;
  scene: string;
  visible_objects: string[];
  emotion: string;
  best_use: string[];
  not_good_for: string[];
  usable_segments: Array<{
    start: number;
    end: number;
    reason: string;
  }>;
  text_overlay_safe_area: string;
  audio_quality: string;
  notes: string;
};

function isVideoFile(filePath: string) {
  return VIDEO_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

function sanitizeFileName(fileName: string) {
  const parsed = path.parse(fileName);
  const base = parsed.name
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 80);
  const safeBase = base || "uploaded_clip";
  const ext = parsed.ext.toLowerCase();
  return `${safeBase}${ext}`;
}

function parseDuration(value?: string) {
  if (!value) return 0;
  const duration = Number(value);
  return Number.isFinite(duration) ? Math.max(0, duration) : 0;
}

async function pathExists(target: string) {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
}

async function readJson<T>(target: string): Promise<T | null> {
  try {
    const raw = await fs.readFile(target, "utf8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

async function writeJson(target: string, data: unknown) {
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

async function uniqueUploadPath(rawDir: string, originalName: string) {
  const safeName = sanitizeFileName(originalName);
  const parsed = path.parse(safeName);
  let candidate = path.join(rawDir, safeName);
  let counter = 2;

  while (await pathExists(candidate)) {
    candidate = path.join(rawDir, `${parsed.name}_${counter}${parsed.ext}`);
    counter += 1;
  }

  return candidate;
}

async function listVideoFiles(rawDir: string) {
  try {
    const entries = await fs.readdir(rawDir, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isFile() && isVideoFile(entry.name))
      .map((entry) => path.join(rawDir, entry.name))
      .sort((a, b) => a.localeCompare(b));
  } catch {
    return [];
  }
}

async function probeVideo(filePath: string): Promise<ProbeData> {
  const { stdout } = await execFileAsync("ffprobe", [
    "-v",
    "error",
    "-print_format",
    "json",
    "-show_format",
    "-show_streams",
    filePath
  ]);
  return JSON.parse(stdout) as ProbeData;
}

function buildAssetEntry(filePath: string, probe: ProbeData): AssetEntry {
  const streams = probe.streams || [];
  const videoStream = streams.find((stream) => stream.codec_type === "video") || {};
  const audioStream = streams.find((stream) => stream.codec_type === "audio");
  const width = Number(videoStream.width || 0);
  const height = Number(videoStream.height || 0);
  const duration = parseDuration(videoStream.duration || probe.format?.duration);
  const usableEnd = duration > 0 ? Math.min(duration, 3) : 0;
  const orientation = height > width ? "vertical" : width > height ? "landscape_source_for_vertical_crop" : "unknown";

  return {
    clip_id: path.parse(filePath).name,
    file_path: path.resolve(filePath),
    duration: Number(duration.toFixed(3)),
    orientation,
    quality_score: orientation === "vertical" ? 7 : 5,
    shot_type: "uploaded footage",
    camera_motion: "unknown",
    scene: "needs labeling",
    visible_objects: [],
    emotion: "neutral",
    best_use: ["needs review"],
    not_good_for: [],
    usable_segments: [
      {
        start: 0,
        end: Number(usableEnd.toFixed(3)),
        reason: "Auto-indexed segment; review before final matching."
      }
    ],
    text_overlay_safe_area: "center",
    audio_quality: audioStream ? "present" : "not needed",
    notes: "Auto-indexed from uploaded local asset. Add human labels before final creative matching."
  };
}

function buildErroredAssetEntry(filePath: string, error: unknown): AssetEntry {
  const message = error instanceof Error ? error.message : "ffprobe failed";
  return {
    clip_id: path.parse(filePath).name,
    file_path: path.resolve(filePath),
    duration: 0,
    orientation: "unknown",
    quality_score: 0,
    shot_type: "unreadable video",
    camera_motion: "unknown",
    scene: "needs repair",
    visible_objects: [],
    emotion: "unknown",
    best_use: [],
    not_good_for: ["rendering until ffprobe can read this file"],
    usable_segments: [],
    text_overlay_safe_area: "unknown",
    audio_quality: "unknown",
    notes: `Auto-index failed: ${message}`
  };
}

async function writeMaterialIndex(projectDir: string, assets: AssetEntry[]) {
  const rawDir = path.join(projectDir, "materials", "raw");
  const payload = {
    footage_dir: rawDir,
    count: assets.length,
    items: assets.map((asset) => ({
      id: asset.clip_id,
      path: asset.file_path,
      relative_path: path.relative(rawDir, asset.file_path),
      duration_s: asset.duration,
      orientation: asset.orientation,
      has_audio: asset.audio_quality === "present",
      tags: {
        scene: asset.scene,
        shot_type: asset.shot_type,
        quality: asset.quality_score,
        best_ranges: asset.usable_segments
      }
    }))
  };
  await writeJson(path.join(projectDir, "output", "material_index.json"), payload);
}

async function syncFullWorkflowInput(projectDir: string, assets: AssetEntry[], rawDir: string) {
  const fullPath = path.join(projectDir, "full_workflow_input.json");
  const full = (await readJson<Record<string, any>>(fullPath)) || {};
  full.asset_library = assets;
  full.intake = {
    ...(full.intake || {}),
    material_directory: rawDir
  };
  await writeJson(fullPath, full);
}

export async function readAssetLibraryForSlug(slug: string): Promise<AssetLibraryFile | null> {
  const projectDir = projectDirFromSlug(slug);
  return readJson<AssetLibraryFile>(path.join(projectDir, "output", "asset_library.json"));
}

export async function uploadProjectAssets(slug: string, files: File[]) {
  const projectDir = projectDirFromSlug(slug);
  const rawDir = path.join(projectDir, "materials", "raw");
  await fs.mkdir(rawDir, { recursive: true });

  const savedFiles: string[] = [];
  for (const file of files) {
    if (!file.name || !isVideoFile(file.name)) continue;
    const target = await uniqueUploadPath(rawDir, file.name);
    const buffer = Buffer.from(await file.arrayBuffer());
    await fs.writeFile(target, buffer);
    savedFiles.push(target);
  }

  const assetLibrary = await indexProjectAssets(slug);
  return {
    savedFiles,
    assetLibrary
  };
}

export async function indexProjectAssets(slug: string): Promise<AssetLibraryFile> {
  const projectDir = projectDirFromSlug(slug);
  const rawDir = path.join(projectDir, "materials", "raw");
  await fs.mkdir(path.join(projectDir, "output"), { recursive: true });
  await fs.mkdir(rawDir, { recursive: true });

  const videoFiles = await listVideoFiles(rawDir);
  const assets: AssetEntry[] = [];
  for (const videoFile of videoFiles) {
    try {
      assets.push(buildAssetEntry(videoFile, await probeVideo(videoFile)));
    } catch (error) {
      assets.push(buildErroredAssetEntry(videoFile, error));
    }
  }

  const payload: AssetLibraryFile = {
    assets,
    status: assets.length > 0 ? "indexed" : "empty",
    source_material_dir: rawDir,
    asset_count: assets.length,
    updated_at: new Date().toISOString(),
    note:
      assets.length > 0
        ? "Auto-indexed by the local web console. Human visual labels can improve matching quality."
        : "No video files found in materials/raw yet."
  };

  await writeJson(path.join(projectDir, "output", "asset_library.json"), payload);
  await writeMaterialIndex(projectDir, assets);
  await syncFullWorkflowInput(projectDir, assets, rawDir);
  return payload;
}
