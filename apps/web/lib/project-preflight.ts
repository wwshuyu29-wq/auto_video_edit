import { execFile } from "child_process";
import { promises as fs } from "fs";
import path from "path";
import { promisify } from "util";
import { getProductByName } from "@/lib/product-catalog";

const execFileAsync = promisify(execFile);
const REPO_ROOT = path.resolve(process.cwd(), "../..");
const VENV_PYTHON_BIN = path.join(REPO_ROOT, ".venv", "bin", "python3");

type StageName = "reference_hook_analysis" | "viral_deconstruction" | "human_hook_generation" | "product_script_rewrite" | "asset_matching" | "video_rendering";
type StageMode = "run" | "reuse_existing";

type ProjectJob = {
  product_name?: string;
  workflow_mode?: "fresh" | "mixed";
  source?: {
    full_workflow_input?: string;
  };
  artifacts?: {
    hook_frame_index?: string;
    human_hook_observation?: string;
    viral_pattern_card?: string;
    human_hook_card?: string;
    product_script_card?: string;
    shot_matching_plan?: string;
    asset_library?: string;
  };
  delivery?: {
    preview_video?: string;
    render_report?: string;
  };
  stages?: Array<{ name?: StageName; mode?: StageMode }>;
};

type AssetLibrary = {
  assets?: Array<{
    clip_id?: string;
    file_path?: string;
    thumbnail_path?: string;
    shot_type?: string;
    scene?: string;
    best_use?: string[];
  }>;
};

type FullWorkflowInput = {
  account_url?: string;
  video_list?: Array<{ video_url?: string }>;
  product?: {
    product_name?: string;
  };
  asset_library?: unknown[];
};

export type PreflightSeverity = "pass" | "warning" | "blocker";

export type PreflightCheck = {
  id: string;
  label: string;
  severity: PreflightSeverity;
  message: string;
};

export type PreflightReport = {
  status: "ready" | "blocked";
  blockerCount: number;
  warningCount: number;
  checks: PreflightCheck[];
  checkedAt: string;
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

function resolveProjectPath(projectDir: string, target?: string | null) {
  if (!target) return null;
  return path.isAbsolute(target) ? target : path.join(projectDir, target);
}

async function checkBinary(binary: string): Promise<PreflightCheck> {
  try {
    await execFileAsync(binary, ["-version"], { timeout: 5000 });
    return {
      id: `binary_${binary}`,
      label: `${binary} installed`,
      severity: "pass",
      message: `${binary} is available.`
    };
  } catch {
    return {
      id: `binary_${binary}`,
      label: `${binary} installed`,
      severity: "blocker",
      message: `${binary} is missing or cannot run. Install FFmpeg before rendering videos.`
    };
  }
}

async function checkPythonPackage(moduleName: string, packageName: string): Promise<PreflightCheck> {
  const pythonBin = (await pathExists(VENV_PYTHON_BIN)) ? VENV_PYTHON_BIN : "python3";
  try {
    await execFileAsync(pythonBin, ["-c", `import ${moduleName}`], { timeout: 5000 });
    return {
      id: `python_package_${moduleName}`,
      label: `${packageName} installed`,
      severity: "pass",
      message: `${packageName} is available to ${pythonBin}.`
    };
  } catch {
    return {
      id: `python_package_${moduleName}`,
      label: `${packageName} installed`,
      severity: "blocker",
      message: `${packageName} is missing for ${pythonBin}. Install it before preview rendering.`
    };
  }
}

function addCheck(checks: PreflightCheck[], check: PreflightCheck) {
  checks.push(check);
}

function artifactKeyForStage(stage: StageName) {
  if (stage === "reference_hook_analysis") return "human_hook_observation";
  if (stage === "viral_deconstruction") return "viral_pattern_card";
  if (stage === "human_hook_generation") return "human_hook_card";
  if (stage === "product_script_rewrite") return "product_script_card";
  if (stage === "asset_matching") return "shot_matching_plan";
  return "shot_matching_plan";
}

function isDefaultAssetLabel(asset: NonNullable<AssetLibrary["assets"]>[number]) {
  const defaultShotType = !asset.shot_type || asset.shot_type === "uploaded footage" || asset.shot_type === "unlabeled";
  const defaultScene = !asset.scene || asset.scene === "needs labeling";
  const defaultBestUse = !asset.best_use?.length || asset.best_use.includes("needs review");
  return defaultShotType && defaultScene && defaultBestUse;
}

export async function runProjectPreflight(projectDir: string): Promise<PreflightReport> {
  const checks: PreflightCheck[] = [];
  const jobPath = path.join(projectDir, "project_job.json");
  const assetLibraryPath = path.join(projectDir, "output", "asset_library.json");

  addCheck(
    checks,
    (await pathExists(projectDir))
      ? {
          id: "project_dir",
          label: "Project folder",
          severity: "pass",
          message: "Project folder exists."
        }
      : {
          id: "project_dir",
          label: "Project folder",
          severity: "blocker",
          message: `Project folder does not exist: ${projectDir}`
        }
  );

  addCheck(checks, await checkBinary("ffmpeg"));
  addCheck(checks, await checkBinary("ffprobe"));

  const job = await readJson<ProjectJob>(jobPath);
  const fullInputPath = resolveProjectPath(projectDir, job?.source?.full_workflow_input) || path.join(projectDir, "full_workflow_input.json");
  const fullInput = await readJson<FullWorkflowInput>(fullInputPath);
  const stages = job?.stages || [];
  const needsFullInput = stages.some(
    (stage) =>
      stage.mode === "run" &&
      (stage.name === "reference_hook_analysis" || stage.name === "viral_deconstruction" || stage.name === "product_script_rewrite")
  );
  const needsPreviewRendering = stages.some((stage) => stage.mode === "run" && stage.name === "video_rendering");
  const needsReferenceHookAnalysis = stages.some((stage) => stage.mode === "run" && stage.name === "reference_hook_analysis");
  const needsHumanHookGeneration = stages.some((stage) => stage.mode === "run" && stage.name === "human_hook_generation");
  const reusesViralDeconstruction = stages.some((stage) => stage.name === "viral_deconstruction" && stage.mode === "reuse_existing");

  if (needsPreviewRendering) {
    addCheck(checks, await checkPythonPackage("PIL", "Pillow"));
  }

  if (needsReferenceHookAnalysis) {
    const envPath = path.join(REPO_ROOT, ".env.local");
    const envText = await fs.readFile(envPath, "utf8").catch(() => "");
    const hasOfficialOpenAIKey = process.env.OPENAI_API_KEY || /\bOPENAI_API_KEY\s*=/.test(envText);
    const hasEvolinkGateway =
      (process.env.EVOLINK_API_KEY || process.env.AI_REAL_PERSON_VIDEO_API_KEY || /\b(EVOLINK_API_KEY|AI_REAL_PERSON_VIDEO_API_KEY)\s*=/.test(envText)) &&
      (process.env.EVOLINK_OPENAI_RESPONSES_ENDPOINT ||
        process.env.EVOLINK_RESPONSES_ENDPOINT ||
        process.env.EVOLINK_OPENAI_CHAT_COMPLETIONS_ENDPOINT ||
        process.env.EVOLINK_CHAT_COMPLETIONS_ENDPOINT ||
        process.env.EVOLINK_OPENAI_BASE_URL ||
        /\b(EVOLINK_OPENAI_RESPONSES_ENDPOINT|EVOLINK_RESPONSES_ENDPOINT|EVOLINK_OPENAI_CHAT_COMPLETIONS_ENDPOINT|EVOLINK_CHAT_COMPLETIONS_ENDPOINT|EVOLINK_OPENAI_BASE_URL)\s*=/.test(envText));
    addCheck(
      checks,
      hasOfficialOpenAIKey || hasEvolinkGateway
        ? {
            id: "reference_hook_openai_key",
            label: "Reference hook vision key",
            severity: "pass",
            message: hasOfficialOpenAIKey
              ? "OpenAI API key is configured for reference hook visual analysis."
              : "Evolink OpenAI-compatible endpoint is configured for reference hook visual analysis."
          }
        : {
            id: "reference_hook_openai_key",
            label: "Reference hook vision key",
            severity: "warning",
            message: "No OPENAI_API_KEY or Evolink OpenAI-compatible responses endpoint found. The worker can extract frames, but visual analysis will use the heuristic fallback."
          }
    );
  }

  if (needsHumanHookGeneration) {
    const envPath = path.join(REPO_ROOT, ".env.local");
    const envText = await fs.readFile(envPath, "utf8").catch(() => "");
    const hasVideoKey =
      process.env.EVOLINK_API_KEY ||
      process.env.AI_REAL_PERSON_VIDEO_API_KEY ||
      /\b(EVOLINK_API_KEY|AI_REAL_PERSON_VIDEO_API_KEY)\s*=/.test(envText);
    addCheck(
      checks,
      hasVideoKey
        ? {
            id: "human_hook_video_api_key",
            label: "Human hook video API key",
            severity: "pass",
            message: "Video generation API key is configured for AI human hook generation."
          }
        : {
            id: "human_hook_video_api_key",
            label: "Human hook video API key",
            severity: "warning",
            message: "No EVOLINK_API_KEY or AI_REAL_PERSON_VIDEO_API_KEY found. The worker can write a prompt, but cannot generate the AI human hook clip."
          }
    );
  }

  addCheck(
    checks,
    job
      ? {
          id: "project_job",
          label: "Worker work order",
          severity: "pass",
          message: "project_job.json exists and can be read."
        }
      : {
          id: "project_job",
          label: "Worker work order",
          severity: "blocker",
          message: "Missing or invalid project_job.json."
        }
  );

  addCheck(
    checks,
    fullInput
      ? {
          id: "full_workflow_input",
          label: "Workflow input",
          severity: "pass",
          message: "full_workflow_input.json exists and can be read."
        }
      : !needsFullInput
        ? {
            id: "full_workflow_input",
            label: "Workflow input",
            severity: "pass",
            message: "Not required because the project is reusing existing workflow artifacts."
          }
      : {
          id: "full_workflow_input",
          label: "Workflow input",
          severity: "blocker",
          message: "Missing or invalid full_workflow_input.json."
        }
  );

  const productName = job?.product_name || fullInput?.product?.product_name || "";
  const product = productName ? await getProductByName(productName) : null;
  addCheck(
    checks,
    product
      ? {
          id: "product_profile",
          label: "Product profile",
          severity: "pass",
          message: `${productName} is listed in product-library/products.json.`
        }
      : {
          id: "product_profile",
          label: "Product profile",
          severity: "blocker",
          message: productName
            ? `${productName} is not an approved product. Use only Literfy, Citely, or FigPad.`
            : "Project has no product name."
        }
  );

  const hasReference =
    Boolean(fullInput?.account_url) || Boolean(fullInput?.video_list?.some((item) => item.video_url?.trim()));
  addCheck(
    checks,
    hasReference
      ? {
          id: "reference_input",
          label: "Reference input",
          severity: "pass",
          message: "Reference account or video URL is present."
        }
      : reusesViralDeconstruction
        ? {
            id: "reference_input",
            label: "Reference input",
            severity: "pass",
            message: "Reference logic is reused from an existing viral pattern card."
          }
      : {
          id: "reference_input",
          label: "Reference input",
          severity: "warning",
          message: "No reference URL found. The worker may still run, but viral deconstruction will be weak."
        }
  );

  const expectedStages: StageName[] = ["viral_deconstruction", "product_script_rewrite", "asset_matching", "video_rendering"];
  const stageNames = job?.stages?.map((stage) => stage.name).filter(Boolean) || [];
  const hasAllStages = expectedStages.every((stage) => stageNames.includes(stage));
  addCheck(
    checks,
    hasAllStages
      ? {
          id: "worker_stages",
          label: "Worker stages",
          severity: "pass",
            message: needsHumanHookGeneration
            ? "Core worker stages, reference hook analysis, and AI human hook generation are configured."
            : "All four core worker stages are configured."
        }
      : {
          id: "worker_stages",
          label: "Worker stages",
          severity: "blocker",
          message: "Project job must include viral, script, asset matching, and rendering stages."
        }
  );

  const assetLibrary = await readJson<AssetLibrary>(assetLibraryPath);
  const assets = assetLibrary?.assets || [];
  addCheck(
    checks,
    assets.length > 0
      ? {
          id: "asset_library",
          label: "Asset library",
          severity: "pass",
          message: `${assets.length} uploaded clips are indexed.`
        }
      : {
          id: "asset_library",
          label: "Asset library",
          severity: "blocker",
          message: "No indexed footage found. Upload clips or re-index the raw folder first."
        }
  );

  const missingAssetFiles = [];
  const missingThumbnails = [];
  for (const asset of assets) {
    if (!asset.file_path || !(await pathExists(asset.file_path))) {
      missingAssetFiles.push(asset.clip_id || "unknown");
    }
    if (!asset.thumbnail_path || !(await pathExists(asset.thumbnail_path))) {
      missingThumbnails.push(asset.clip_id || "unknown");
    }
  }

  addCheck(
    checks,
    missingAssetFiles.length === 0
      ? {
          id: "asset_files",
          label: "Asset files",
          severity: assets.length > 0 ? "pass" : "warning",
          message: assets.length > 0 ? "All indexed asset files exist." : "No asset files to check yet."
        }
      : {
          id: "asset_files",
          label: "Asset files",
          severity: "blocker",
          message: `Missing source files for: ${missingAssetFiles.slice(0, 6).join(", ")}`
        }
  );

  addCheck(
    checks,
    missingThumbnails.length === 0
      ? {
          id: "asset_thumbnails",
          label: "Asset thumbnails",
          severity: assets.length > 0 ? "pass" : "warning",
          message: assets.length > 0 ? "All indexed clips have thumbnails." : "No thumbnails to check yet."
        }
      : {
          id: "asset_thumbnails",
          label: "Asset thumbnails",
          severity: "warning",
          message: `Some clips have no thumbnail: ${missingThumbnails.slice(0, 6).join(", ")}`
        }
  );

  const manuallyLabeledCount = assets.filter((asset) => !isDefaultAssetLabel(asset)).length;
  addCheck(
    checks,
    manuallyLabeledCount > 0
      ? {
          id: "asset_labels",
          label: "Asset labels",
          severity: "pass",
          message: `${manuallyLabeledCount} clips have manual labels.`
        }
      : {
          id: "asset_labels",
          label: "Asset labels",
          severity: assets.length > 0 ? "warning" : "pass",
          message:
            assets.length > 0
              ? "No manual clip labels yet. Matching can run, but quality will be weaker."
              : "No clips indexed yet."
        }
  );

  for (const stage of job?.stages || []) {
    if (stage.mode !== "reuse_existing" || !stage.name) continue;
    const artifactKey = artifactKeyForStage(stage.name);
    const artifactPath = resolveProjectPath(projectDir, job?.artifacts?.[artifactKey]);
    addCheck(
      checks,
      artifactPath && (await pathExists(artifactPath))
        ? {
            id: `reuse_${stage.name}`,
            label: `Reuse ${stage.name}`,
            severity: "pass",
            message: `Reusable artifact exists: ${artifactPath}`
          }
        : {
            id: `reuse_${stage.name}`,
            label: `Reuse ${stage.name}`,
            severity: "blocker",
            message: `Stage is set to reuse_existing, but ${artifactKey} is missing.`
          }
    );
  }

  const blockerCount = checks.filter((check) => check.severity === "blocker").length;
  const warningCount = checks.filter((check) => check.severity === "warning").length;
  return {
    status: blockerCount > 0 ? "blocked" : "ready",
    blockerCount,
    warningCount,
    checks,
    checkedAt: new Date().toISOString()
  };
}
