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

type ScriptVariant = {
  type: string;
  script_title?: string;
  script_angle?: string;
  caption?: string;
  hashtags?: string[];
  full_script?: Array<{
    time?: string;
    beat?: string;
    voiceover?: string;
    on_screen_text?: string;
    visual_need?: string;
    preferred_clip_id?: string;
  }>;
};

type ScriptCard = {
  platform?: string;
  tone?: string;
  video_length?: string;
  selected_script_type?: string;
  script_title?: string;
  script_angle?: string;
  caption?: string;
  hashtags?: string[];
  full_script?: ScriptVariant["full_script"];
  scripts?: ScriptVariant[];
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
    reason?: string;
  }>;
};

type DeliveryVariant = {
  name: string;
  video?: string;
  cover?: string;
  duration?: number | null;
};

type ScriptArtifact = {
  path: string;
  suffix: string;
  card: ScriptCard | null;
};

type ShotPlanArtifact = {
  path: string;
  suffix: string;
  plan: MatchingPlan | null;
};

type PublishingCopyCard = {
  publishing_variants?: Array<{
    variant_id?: string;
    recommended_title?: string;
    recommended_caption?: string;
    hashtags?: string[];
    keywords?: string[];
    posting_notes?: string[];
    compliance_notes?: string[];
  }>;
};

type PublishingCopy = {
  path?: string;
  variantId: string;
  recommendedTitle: string;
  recommendedCaption: string;
  hashtags: string[];
  keywords: string[];
  postingNotes: string[];
  complianceNotes: string[];
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
  videoVariants: Array<{
    id: string;
    name: string;
    video?: string;
    cover?: string;
    duration?: number | null;
    scriptPath?: string;
    shotPlanPath?: string;
    scriptType?: string;
    scriptTitle: string;
    scriptAngle: string;
    publishingCopy?: PublishingCopy;
    scriptBeats: Array<{
      time: string;
      beat: string;
      onScreenText: string;
      voiceover: string;
      visualNeed: string;
      preferredClipId: string;
    }>;
    shotBeats: Array<{
      time: string;
      beat: string;
      clipId: string;
      onScreenText: string;
      reason: string;
    }>;
  }>;
  publishingCopyPath?: string;
  publishingCopyDeliveryPath?: string;
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

async function findPublishingCopy(projectDir: string, delivery: any) {
  const cardFromManifest = normalizeArtifactPath(projectDir, delivery?.publishing_copy_card);
  const deliveryFromManifest = normalizeArtifactPath(projectDir, delivery?.publishing_copy_delivery);
  const card = cardFromManifest || path.join(projectDir, "output", "publishing_copy_card.json");
  const readable = deliveryFromManifest || path.join(projectDir, "output", "publishing_copy_delivery.md");
  return {
    card: (await pathExists(card)) ? card : undefined,
    delivery: (await pathExists(readable)) ? readable : undefined
  };
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

async function listOutputFiles(projectDir: string, matcher: (fileName: string) => boolean) {
  const outputDir = path.join(projectDir, "output");
  const files = await listFilesRecursive(outputDir);
  return files.filter((file) => matcher(path.basename(file))).sort();
}

function suffixFromArtifact(filePath: string, baseName: string) {
  const name = path.basename(filePath, ".json");
  if (name === baseName) return "";
  return name.replace(`${baseName}_`, "");
}

function normalizeKey(value?: string | null) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function tokenScore(target: string, candidate?: string) {
  const targetTokens = new Set(normalizeKey(target).split("_").filter(Boolean));
  const candidateTokens = normalizeKey(candidate).split("_").filter(Boolean);
  return candidateTokens.reduce((score, token) => score + (targetTokens.has(token) ? 1 : 0), 0);
}

function scriptVariantsFromCard(card: ScriptCard | null | undefined): ScriptVariant[] {
  if (!card) return [];
  if (card.scripts?.length) return card.scripts;
  if (!card.script_title && !card.caption && !card.full_script?.length) return [];

  return [
    {
      type: card.selected_script_type || "single_script_version",
      script_title: card.script_title,
      script_angle: card.script_angle,
      caption: card.caption,
      hashtags: card.hashtags,
      full_script: card.full_script
    }
  ];
}

async function readScriptArtifacts(projectDir: string): Promise<ScriptArtifact[]> {
  const files = await listOutputFiles(
    projectDir,
    (fileName) => /^product_script_card(?:_[a-z0-9_]+)?\.json$/i.test(fileName)
  );
  return Promise.all(
    files.map(async (file) => ({
      path: file,
      suffix: suffixFromArtifact(file, "product_script_card"),
      card: await readJson<ScriptCard>(file)
    }))
  );
}

async function readShotPlanArtifacts(projectDir: string): Promise<ShotPlanArtifact[]> {
  const files = await listOutputFiles(
    projectDir,
    (fileName) => /^shot_matching_plan(?:_[a-z0-9_]+)?\.json$/i.test(fileName)
  );
  return Promise.all(
    files.map(async (file) => ({
      path: file,
      suffix: suffixFromArtifact(file, "shot_matching_plan"),
      plan: await readJson<MatchingPlan>(file)
    }))
  );
}

function chooseSuffixedArtifact<T extends { suffix: string }>(deliverableName: string, artifacts: T[]) {
  const normalizedName = normalizeKey(deliverableName);
  const explicit = artifacts
    .filter((artifact) => artifact.suffix && normalizedName.includes(normalizeKey(artifact.suffix)))
    .sort((a, b) => b.suffix.length - a.suffix.length)[0];
  if (explicit) return explicit;
  return artifacts.find((artifact) => !artifact.suffix) || artifacts[0];
}

function chooseScriptVariant(deliverableName: string, card: ScriptCard | null) {
  const scripts = scriptVariantsFromCard(card);
  if (!scripts.length) return null;
  if (scripts.length === 1) return scripts[0];

  const normalizedName = normalizeKey(deliverableName);
  const variantLetter = normalizedName.match(/(?:^|_)([abc])$/)?.[1];
  if (variantLetter) {
    const explicit = scripts.find((script) => normalizeKey(script.type).includes(`variant_${variantLetter}`));
    if (explicit) return explicit;
  }

  if (normalizedName.startsWith("a_")) {
    return scripts.find((script) => normalizeKey(script.type).includes("safe")) || scripts[0];
  }
  if (normalizedName.startsWith("b_")) {
    return scripts.find((script) => normalizeKey(script.type).includes("viral")) || scripts[1] || scripts[0];
  }
  if (normalizedName.startsWith("c_")) {
    return scripts.find((script) => normalizeKey(script.type).includes("native")) || scripts[2] || scripts[0];
  }

  return (
    scripts
      .map((script) => ({
        script,
        score:
          tokenScore(deliverableName, script.type) +
          tokenScore(deliverableName, script.script_title) +
          tokenScore(deliverableName, script.script_angle)
      }))
      .sort((a, b) => b.score - a.score)[0]?.script ||
    scripts.find((script) => normalizeKey(script.type).includes("native")) ||
    scripts[0]
  );
}

function choosePublishingCopy(deliverableName: string, card: PublishingCopyCard | null | undefined) {
  const variants = card?.publishing_variants || [];
  if (!variants.length) return null;
  const normalizedName = normalizeKey(deliverableName);
  return (
    variants.find((item) => normalizeKey(item.variant_id) === normalizedName) ||
    variants
      .map((item) => ({
        item,
        score: tokenScore(deliverableName, item.variant_id)
      }))
      .sort((a, b) => b.score - a.score)[0]?.item ||
    variants[0]
  );
}

function fallbackPublishingCopy(
  deliverableName: string,
  script: ScriptVariant | null | undefined,
  scriptArtifactPath?: string
): PublishingCopy | undefined {
  if (!script?.script_title && !script?.caption && !script?.hashtags?.length) return undefined;
  const hashtags = script.hashtags || [];
  return {
    path: scriptArtifactPath,
    variantId: deliverableName,
    recommendedTitle: script.script_title || deliverableName,
    recommendedCaption: script.caption || script.script_title || "",
    hashtags,
    keywords: hashtags.map((tag) => tag.replace(/^#/, "")),
    postingNotes: [
      "Use the matching cover image with this captioned video.",
      "Add TikTok trending music inside TikTok.",
      "Review product claims before publishing."
    ],
    complianceNotes: ["Use product-safe wording and avoid exaggerated claims."]
  };
}

function buildVideoVariants(
  deliverables: DeliveryVariant[],
  scriptArtifacts: ScriptArtifact[],
  shotPlanArtifacts: ShotPlanArtifact[],
  publishingCopyCard?: PublishingCopyCard | null,
  publishingCopyPath?: string
) {
  return deliverables.map((deliverable) => {
    const scriptArtifact = chooseSuffixedArtifact(deliverable.name, scriptArtifacts);
    const shotPlanArtifact = chooseSuffixedArtifact(deliverable.name, shotPlanArtifacts);
    const script = chooseScriptVariant(deliverable.name, scriptArtifact?.card || null);
    const publishing = choosePublishingCopy(deliverable.name, publishingCopyCard);
    const publishingCopy = publishing
      ? {
          path: publishingCopyPath,
          variantId: publishing.variant_id || deliverable.name,
          recommendedTitle: publishing.recommended_title || script?.script_title || deliverable.name,
          recommendedCaption: publishing.recommended_caption || script?.caption || "",
          hashtags: publishing.hashtags || script?.hashtags || [],
          keywords:
            publishing.keywords ||
            (publishing.hashtags || script?.hashtags || []).map((tag) => tag.replace(/^#/, "")),
          postingNotes: publishing.posting_notes || [],
          complianceNotes: publishing.compliance_notes || []
        }
      : fallbackPublishingCopy(deliverable.name, script, scriptArtifact?.path);

    return {
      id: normalizeKey(deliverable.name) || "video",
      name: deliverable.name,
      video: deliverable.video,
      cover: deliverable.cover,
      duration: deliverable.duration,
      scriptPath: scriptArtifact?.path,
      shotPlanPath: shotPlanArtifact?.path,
      scriptType: script?.type,
      scriptTitle: script?.script_title || deliverable.name,
      scriptAngle: script?.script_angle || "No script angle found",
      publishingCopy,
      scriptBeats:
        script?.full_script?.map((beat) => ({
          time: beat.time || "",
          beat: beat.beat || "",
          onScreenText: beat.on_screen_text || "",
          voiceover: beat.voiceover || "",
          visualNeed: beat.visual_need || "",
          preferredClipId: beat.preferred_clip_id || ""
        })) || [],
      shotBeats:
        shotPlanArtifact?.plan?.edit_plan?.map((beat) => ({
          time: beat.time || "",
          beat: beat.beat || "",
          clipId: beat.clip_id || "",
          onScreenText: beat.on_screen_text || "",
          reason: beat.reason || ""
        })) || []
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
          scriptVariantsFromCard(script).find((item) => item.type === "native_creator_version")?.script_title ||
          scriptVariantsFromCard(script)[0]?.script_title ||
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
  const scriptArtifacts = await readScriptArtifacts(projectDir);
  const shotPlanArtifacts = await readShotPlanArtifacts(projectDir);
  const publishingCopy = await findPublishingCopy(projectDir, delivery);
  const publishingCopyCard = publishingCopy.card ? await readJson<PublishingCopyCard>(publishingCopy.card) : null;
  const videoVariants = buildVideoVariants(
    deliverables,
    scriptArtifacts,
    shotPlanArtifacts,
    publishingCopyCard,
    publishingCopy.card
  );
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
      scriptVariantsFromCard(script).find((item) => item.type === "native_creator_version")?.script_title ||
      scriptVariantsFromCard(script)[0]?.script_title ||
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
      scriptVariantsFromCard(script).map((item) => ({
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
    videoVariants,
    publishingCopyPath: publishingCopy.card,
    publishingCopyDeliveryPath: publishingCopy.delivery,
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
