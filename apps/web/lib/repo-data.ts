import { promises as fs } from "fs";
import path from "path";

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
};

const REPO_ROOT = path.resolve(process.cwd(), "../..");
const PROJECTS_ROOT = path.join(REPO_ROOT, "projects");

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

function slugFor(group: string, name: string) {
  return `${group}__${name}`;
}

function projectFromSlug(slug: string) {
  const [group, ...rest] = slug.split("__");
  return { group, name: rest.join("__") };
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
      projectDirs.push({
        group: group.name,
        name: project.name,
        dir: path.join(groupPath, project.name)
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
    path.join(projectDir, "output", "final_delivery_manifest.json")
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
      const deliverables = normalizeDeliverables(dir, delivery);

      return {
        slug: slugFor(group, name),
        group,
        name,
        productName: job?.product_name || "Unassigned",
        workflowMode: job?.workflow_mode || "mixed",
        status: statusFromArtifacts(job, delivery, shotPlan),
        stageCount: job?.stages?.length || 0,
        deliverableCount: deliverables.length,
        headline:
          script?.scripts?.find((item) => item.type === "native_creator_version")?.script_title ||
          script?.scripts?.[0]?.script_title ||
          "No script headline yet",
        updatedAt: await updatedAtFor(dir)
      };
    })
  );

  return projects.sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));
}

export async function getProjectDetail(slug: string): Promise<ProjectDetail | null> {
  const { group, name } = projectFromSlug(slug);
  const projectDir = path.join(PROJECTS_ROOT, group, name);
  if (!(await pathExists(projectDir))) return null;

  const job = await readJson<ProjectJob>(path.join(projectDir, "project_job.json"));
  const full = await readJson<FullWorkflowInput>(path.join(projectDir, "full_workflow_input.json"));
  const script = await readJson<ScriptCard>(path.join(projectDir, "output", "product_script_card.json"));
  const viral = await readJson<ViralCard>(path.join(projectDir, "output", "viral_pattern_card.json"));
  const shotPlan = await readJson<MatchingPlan>(path.join(projectDir, "output", "shot_matching_plan.json"));
  const deliveryPath = await findDeliveryManifest(projectDir);
  const delivery = deliveryPath ? await readJson<any>(deliveryPath) : null;
  const deliverables = normalizeDeliverables(projectDir, delivery);
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
    productName: job?.product_name || "Unassigned",
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
    renderReport
  };
}

export async function getDashboardMetrics() {
  const projects = await getProjectSummaries();
  return {
    totalProjects: projects.length,
    readyProjects: projects.filter((item) => item.status === "ready" || item.status === "final_delivery_cleaned").length,
    configuredProjects: projects.filter((item) => item.status === "configured" || item.status === "matched").length,
    totalDeliverables: projects.reduce((sum, item) => sum + item.deliverableCount, 0),
    projects
  };
}

export function mediaUrl(localPath?: string) {
  if (!localPath) return null;
  return `/api/media?path=${encodeURIComponent(localPath)}`;
}
