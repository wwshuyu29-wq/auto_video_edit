import { promises as fs } from "fs";
import path from "path";
import { PROJECTS_ROOT, projectDirFromSlug, projectFromSlug, slugFor } from "@/lib/project-paths";
import { readEditableArtifacts } from "@/lib/project-artifacts";
import { runProjectPreflight, type PreflightReport } from "@/lib/project-preflight";
import { readWorkerStatus } from "@/lib/worker-status";

export type StageMode = "run" | "reuse_existing";
export type StageName =
  | "viral_deconstruction"
  | "product_script_rewrite"
  | "asset_matching"
  | "video_rendering";

type ProjectJob = {
  project_id: string;
  project_dir: string;
  product_name?: string;
  workflow_mode: "fresh" | "mixed";
  stages: Array<{ name: StageName; mode: StageMode }>;
  delivery?: {
    mode?: string;
    preview_video?: string;
    render_report?: string;
  };
};

type ScriptCard = {
  platform?: string;
  tone?: string;
  video_length?: string;
  scripts?: Array<{
    type: string;
    script_title?: string;
    script_angle?: string;
  }>;
};

type ViralCard = {
  analysis_goal?: string;
  main_content_logic?: string;
  caption_logic?: {
    visible_sequence?: string[];
  };
};

type FullWorkflowInput = {
  analysis_goal?: string;
  tone?: string;
  video_length?: string;
  product?: {
    product_name?: string;
    one_liner?: string;
    good_tiktok_angles?: string[];
  };
  intake?: {
    notes?: string;
    template_name?: string;
  };
};

type MatchingPlan = {
  scores?: Record<string, number>;
  missing_assets?: unknown[];
  risk_notes?: string[];
  edit_plan?: Array<{
    beat?: string;
    clip_id?: string;
    on_screen_text?: string;
    time?: string;
  }>;
};

type DeliveryVariant = {
  name: string;
  video?: string;
  cover?: string;
  duration?: number | null;
};

type AssetLibrary = {
  assets?: Array<{
    clip_id?: string;
    file_path?: string;
    thumbnail_path?: string;
    duration?: number;
    orientation?: string;
    shot_type?: string;
    camera_motion?: string;
    scene?: string;
    visible_objects?: string[];
    best_use?: string[];
    text_overlay_safe_area?: string;
    notes?: string;
  }>;
  status?: string;
  source_material_dir?: string;
  updated_at?: string;
} | Array<{
  clip_id?: string;
  file_path?: string;
  thumbnail_path?: string;
  duration?: number;
  orientation?: string;
  shot_type?: string;
  camera_motion?: string;
  scene?: string;
  visible_objects?: string[];
  best_use?: string[];
  text_overlay_safe_area?: string;
  notes?: string;
}>;

export type ProjectSummary = {
  slug: string;
  group: string;
  name: string;
  productName: string;
  workflowMode: string;
  status: string;
  stageCount: number;
  deliverableCount: number;
  headline: string;
  updatedAt: string;
  workerState: "idle" | "running" | "completed" | "failed";
};

export type ProjectDetail = {
  slug: string;
  group: string;
  name: string;
  productName: string;
  workflowMode: string;
  status: string;
  projectDir: string;
  stages: Array<{ name: StageName; mode: StageMode }>;
  headline: string;
  tone: string;
  videoLength: string;
  viralGoal: string;
  contentLogic: string;
  captionSequence: string[];
  scripts: Array<{ type: string; title: string; angle: string }>;
  matchingScores: Record<string, number>;
  missingAssetCount: number;
  riskNotes: string[];
  editPreview: Array<{ beat: string; clipId: string; text: string; time: string }>;
  deliverables: DeliveryVariant[];
  previewVideo?: string;
  renderReport?: string;
  preflight: PreflightReport;
  editableArtifacts: Array<{
    key: string;
    label: string;
    description: string;
    path: string;
    exists: boolean;
    updatedAt: string | null;
    data: unknown;
  }>;
  assetLibrary: {
    status: string;
    assetCount: number;
    sourceMaterialDir: string;
    updatedAt?: string;
    assets: Array<{
      clipId: string;
      filePath: string;
      thumbnailPath?: string;
      duration: number | null;
      orientation: string;
      shotType: string;
      cameraMotion: string;
      scene: string;
      visibleObjects: string[];
      bestUse: string[];
      textOverlaySafeArea: string;
      notes: string;
    }>;
  };
  workerStatus: {
    state: "idle" | "running" | "completed" | "failed";
    startedAt?: string | null;
    finishedAt?: string | null;
    logPath?: string | null;
    error?: string | null;
    logExcerpt: string[];
    stages: Array<{
      name: string;
      mode?: string;
      state: "pending" | "running" | "completed" | "failed";
      startedAt?: string | null;
      finishedAt?: string | null;
      output?: string | null;
      report?: string | null;
    }>;
  };
};

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

async function findProjectDirs() {
  const groups = await fs.readdir(PROJECTS_ROOT, { withFileTypes: true });
  const projectDirs: Array<{ group: string; name: string; dir: string }> = [];

  for (const group of groups) {
    if (!group.isDirectory()) continue;
    const groupPath = path.join(PROJECTS_ROOT, group.name);
    const projects = await fs.readdir(groupPath, { withFileTypes: true });
    for (const project of projects) {
      if (!project.isDirectory()) continue;
      const dir = path.join(groupPath, project.name);
      const hasWorkflowFiles =
        (await pathExists(path.join(dir, "project_job.json"))) ||
        (await pathExists(path.join(dir, "output"))) ||
        (await pathExists(path.join(dir, "materials")));
      if (!hasWorkflowFiles) continue;
      projectDirs.push({
        group: group.name,
        name: project.name,
        dir
      });
    }
  }

  return projectDirs;
}

async function findDeliveryManifest(projectDir: string) {
  const primary = path.join(projectDir, "output", "final_delivery_manifest.json");
  const secondary = path.join(projectDir, "output", "final_delivery", "final_delivery_manifest.json");
  if (await pathExists(primary)) return primary;
  if (await pathExists(secondary)) return secondary;
  return null;
}

function normalizeArtifactPath(projectDir: string, target?: string | null) {
  if (!target) return undefined;
  return path.isAbsolute(target) ? target : path.join(projectDir, target);
}

function normalizeDeliverables(projectDir: string, data: any): DeliveryVariant[] {
  if (!data) return [];

  if (Array.isArray(data.deliverables)) {
    return data.deliverables.map((item: any) => ({
      name: item.variant ?? "variant",
      video: normalizeArtifactPath(projectDir, item.video),
      cover: normalizeArtifactPath(projectDir, item.cover),
      duration: typeof item.duration_seconds === "number" ? item.duration_seconds : null
    }));
  }

  if (data.variants && typeof data.variants === "object") {
    return Object.entries(data.variants).map(([name, item]: [string, any]) => ({
      name,
      video: normalizeArtifactPath(projectDir, item.video),
      cover: normalizeArtifactPath(projectDir, item.cover),
      duration: null
    }));
  }

  return [];
}

function normalizeAssetEntries(assetLibrary: AssetLibrary | null) {
  if (Array.isArray(assetLibrary)) return assetLibrary;
  return assetLibrary?.assets || [];
}

function normalizeAssetLibraryMeta(assetLibrary: AssetLibrary | null, projectDir: string) {
  if (Array.isArray(assetLibrary)) {
    return {
      status: "indexed_legacy",
      sourceMaterialDir: path.join(projectDir, "materials", "raw"),
      updatedAt: undefined
    };
  }
  return {
    status: assetLibrary?.status || "not_indexed",
    sourceMaterialDir: assetLibrary?.source_material_dir || path.join(projectDir, "materials", "raw"),
    updatedAt: assetLibrary?.updated_at
  };
}

async function resolveAssetThumbnail(projectDir: string, clipId?: string, explicitPath?: string) {
  if (explicitPath && (await pathExists(explicitPath))) return explicitPath;
  if (!clipId) return undefined;
  const candidates = [
    path.join(projectDir, "materials", "contact_sheets", "frames", `${clipId}.jpg`),
    path.join(projectDir, "materials", "contact_sheets", "timelines", `${clipId}_timeline.jpg`),
    path.join(projectDir, "materials", "contact_sheets", "new_find_papers", `${clipId}_timeline.jpg`)
  ];
  for (const candidate of candidates) {
    if (await pathExists(candidate)) return candidate;
  }
  return undefined;
}

async function listFilesRecursive(root: string): Promise<string[]> {
  if (!(await pathExists(root))) return [];
  const entries = await fs.readdir(root, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map(async (entry) => {
      const target = path.join(root, entry.name);
      if (entry.isDirectory()) return listFilesRecursive(target);
      return [target];
    })
  );
  return nested.flat();
}

async function discoverMediaDeliverables(projectDir: string): Promise<DeliveryVariant[]> {
  const outputDir = path.join(projectDir, "output");
  const files = await listFilesRecursive(outputDir);
  const videos = files
    .filter((file) => path.extname(file).toLowerCase() === ".mp4")
    .filter((file) => !path.basename(file).includes("_sheet") && !path.basename(file).includes("midpoint"));
  const covers = files.filter((file) => /\.(jpe?g|png)$/i.test(file) && path.basename(file).toLowerCase().includes("cover"));

  return videos.map((video) => {
    const base = path.basename(video, path.extname(video));
    const simplifiedBase = base
      .replace(/_final$/, "")
      .replace(/_preview(_v\d+)?$/, "")
      .replace(/_25s_captioned$/, "");
    const cover =
      covers.find((candidate) => path.basename(candidate).includes(simplifiedBase)) ||
      covers.find((candidate) => path.basename(candidate).includes(base)) ||
      undefined;
    return {
      name: simplifiedBase,
      video,
      cover,
      duration: null
    };
  });
}

function statusFromArtifacts(job: ProjectJob | null, delivery: any, shotPlan: MatchingPlan | null) {
  if (delivery?.status) return String(delivery.status);
  if (shotPlan?.edit_plan?.length) return "matched";
  if (job?.stages?.length) return "configured";
  return "draft";
}

async function updatedAtFor(projectDir: string) {
  const candidates = [
    path.join(projectDir, "project_job.json"),
    path.join(projectDir, "output", "shot_matching_plan.json"),
    path.join(projectDir, "output", "final_delivery", "final_delivery_manifest.json"),
    path.join(projectDir, "output", "final_delivery_manifest.json"),
    path.join(projectDir, "output", "worker_run_status.json")
  ];
  const stats = await Promise.all(
    candidates.map(async (target) => {
      try {
        return await fs.stat(target);
      } catch {
        return null;
      }
    })
  );
  const latest = stats.filter(Boolean).sort((a, b) => b!.mtimeMs - a!.mtimeMs)[0];
  return latest ? latest.mtime.toISOString() : new Date().toISOString();
}

export async function getProjectSummaries(): Promise<ProjectSummary[]> {
  const dirs = await findProjectDirs();
  const projects = await Promise.all(
    dirs.map(async ({ group, name, dir }) => {
      const job = await readJson<ProjectJob>(path.join(dir, "project_job.json"));
      const script = await readJson<ScriptCard>(path.join(dir, "output", "product_script_card.json"));
      const shotPlan = await readJson<MatchingPlan>(path.join(dir, "output", "shot_matching_plan.json"));
      const deliveryPath = await findDeliveryManifest(dir);
      const delivery = deliveryPath ? await readJson<any>(deliveryPath) : null;
      const manifestDeliverables = normalizeDeliverables(dir, delivery);
      const deliverables = manifestDeliverables.length ? manifestDeliverables : await discoverMediaDeliverables(dir);
      const workerStatus = await readWorkerStatus(dir);

      return {
        slug: slugFor(group, name),
        group,
        name,
        productName: job?.product_name || group,
        workflowMode: job?.workflow_mode || "mixed",
        status: statusFromArtifacts(job, delivery, shotPlan),
        stageCount: job?.stages?.length || 0,
        deliverableCount: deliverables.length,
        headline:
          script?.scripts?.find((item) => item.type === "native_creator_version")?.script_title ||
          script?.scripts?.[0]?.script_title ||
          "No script headline yet",
        updatedAt: await updatedAtFor(dir),
        workerState: workerStatus.state
      };
    })
  );

  return projects.sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));
}

export async function getProjectDetail(slug: string): Promise<ProjectDetail | null> {
  const { group, name } = projectFromSlug(slug);
  const projectDir = projectDirFromSlug(slug);
  if (!(await pathExists(projectDir))) return null;

  const job = await readJson<ProjectJob>(path.join(projectDir, "project_job.json"));
  const full = await readJson<FullWorkflowInput>(path.join(projectDir, "full_workflow_input.json"));
  const script = await readJson<ScriptCard>(path.join(projectDir, "output", "product_script_card.json"));
  const viral = await readJson<ViralCard>(path.join(projectDir, "output", "viral_pattern_card.json"));
  const shotPlan = await readJson<MatchingPlan>(path.join(projectDir, "output", "shot_matching_plan.json"));
  const assetLibrary = await readJson<AssetLibrary>(path.join(projectDir, "output", "asset_library.json"));
  const assets = normalizeAssetEntries(assetLibrary);
  const assetMeta = normalizeAssetLibraryMeta(assetLibrary, projectDir);
  const normalizedAssets = await Promise.all(
    assets.map(async (asset) => ({
      clipId: asset.clip_id || "clip",
      filePath: asset.file_path || "",
      thumbnailPath: await resolveAssetThumbnail(projectDir, asset.clip_id, asset.thumbnail_path),
      duration: typeof asset.duration === "number" ? asset.duration : null,
      orientation: asset.orientation || "unknown",
      shotType: asset.shot_type || "unlabeled",
      cameraMotion: asset.camera_motion || "unknown",
      scene: asset.scene || "needs labeling",
      visibleObjects: asset.visible_objects || [],
      bestUse: asset.best_use || [],
      textOverlaySafeArea: asset.text_overlay_safe_area || "center",
      notes: asset.notes || ""
    }))
  );
  const deliveryPath = await findDeliveryManifest(projectDir);
  const delivery = deliveryPath ? await readJson<any>(deliveryPath) : null;
  const manifestDeliverables = normalizeDeliverables(projectDir, delivery);
  const deliverables = manifestDeliverables.length ? manifestDeliverables : await discoverMediaDeliverables(projectDir);
  const workerStatus = await readWorkerStatus(projectDir);
  const preflight = await runProjectPreflight(projectDir);
  const editableArtifacts = await readEditableArtifacts(slug);
  const configuredPreviewVideo = normalizeArtifactPath(projectDir, job?.delivery?.preview_video);
  const previewVideo =
    configuredPreviewVideo && (await pathExists(configuredPreviewVideo))
      ? configuredPreviewVideo
      : deliverables.find((item) => item.video)?.video;
  const configuredRenderReport = normalizeArtifactPath(projectDir, job?.delivery?.render_report);
  const renderReport =
    configuredRenderReport && (await pathExists(configuredRenderReport)) ? configuredRenderReport : undefined;

  return {
    slug,
    group,
    name,
    productName: job?.product_name || group,
    workflowMode: job?.workflow_mode || "mixed",
    status: statusFromArtifacts(job, delivery, shotPlan),
    projectDir,
    stages: job?.stages || [],
    headline:
      script?.scripts?.find((item) => item.type === "native_creator_version")?.script_title ||
      script?.scripts?.[0]?.script_title ||
      full?.product?.good_tiktok_angles?.[0] ||
      `${job?.product_name || full?.product?.product_name || "Project"} intake scaffold ready`,
    tone: script?.tone || full?.tone || "Not set",
    videoLength: script?.video_length || full?.video_length || "Not set",
    viralGoal: viral?.analysis_goal || full?.analysis_goal || "Not set",
    contentLogic:
      viral?.main_content_logic ||
      full?.product?.one_liner ||
      "Project scaffold created. Index assets first, then run the worker pipeline.",
    captionSequence: viral?.caption_logic?.visible_sequence?.slice(0, 6) || [],
    scripts:
      script?.scripts?.map((item) => ({
        type: item.type,
        title: item.script_title || item.type,
        angle: item.script_angle || "No angle"
      })) || [],
    matchingScores: shotPlan?.scores || {},
    missingAssetCount: shotPlan?.missing_assets?.length || 0,
    riskNotes: shotPlan?.risk_notes || [],
    editPreview:
      shotPlan?.edit_plan?.slice(0, 6).map((item) => ({
        beat: item.beat || "beat",
        clipId: item.clip_id || "clip",
        text: item.on_screen_text || "",
        time: item.time || ""
      })) || [],
    deliverables,
    previewVideo,
    renderReport,
    preflight,
    editableArtifacts,
    assetLibrary: {
      status: assetMeta.status,
      assetCount: assets.length,
      sourceMaterialDir: assetMeta.sourceMaterialDir,
      updatedAt: assetMeta.updatedAt,
      assets: normalizedAssets
    },
    workerStatus: {
      state: workerStatus.state,
      startedAt: workerStatus.started_at,
      finishedAt: workerStatus.finished_at,
      logPath: workerStatus.log_path,
      error: workerStatus.error,
      logExcerpt: workerStatus.log_excerpt || [],
      stages:
        workerStatus.stages?.map((stage) => ({
          name: stage.name,
          mode: stage.mode,
          state: stage.state,
          startedAt: stage.started_at,
          finishedAt: stage.finished_at,
          output: stage.output,
          report: stage.report
        })) || []
    }
  };
}

export async function getDashboardMetrics() {
  const projects = await getProjectSummaries();
  return {
    totalProjects: projects.length,
    readyProjects: projects.filter((item) => item.status === "ready" || item.status === "final_delivery_cleaned").length,
    configuredProjects: projects.filter((item) => item.status === "configured" || item.status === "matched").length,
    totalDeliverables: projects.reduce((sum, item) => sum + item.deliverableCount, 0),
    runningProjects: projects.filter((item) => item.workerState === "running").length,
    projects
  };
}

export function mediaUrl(localPath?: string) {
  if (!localPath) return null;
  return `/api/media?path=${encodeURIComponent(localPath)}`;
}
