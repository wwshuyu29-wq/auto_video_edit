import { promises as fs } from "fs";
import path from "path";
import { getProductByName, type ProductProfile } from "@/lib/product-catalog";

const REPO_ROOT = path.resolve(process.cwd(), "../..");
const PROJECTS_ROOT = path.join(REPO_ROOT, "projects");

export type CreateProjectInput = {
  projectName: string;
  productName: string;
  referenceAccountUrl?: string;
  referenceVideoUrl?: string;
  materialDirectory?: string;
  templateName?: string;
  videoLength?: string;
  tone?: string;
  notes?: string;
};

type ProjectJob = {
  project_id: string;
  project_dir: string;
  product_name: string;
  workflow_mode: "fresh";
  source: {
    full_workflow_input: string;
  };
  artifacts: {
    hook_frame_index: string;
    human_hook_observation: string;
    viral_pattern_card: string;
    human_hook_card: string;
    product_script_card: string;
    shot_matching_plan: string;
    asset_library: string;
  };
  delivery: {
    mode: "preview_render";
    preview_video: string;
    render_report: string;
  };
  stages: Array<{
    name: "reference_hook_analysis" | "viral_deconstruction" | "human_hook_generation" | "product_script_rewrite" | "asset_matching" | "video_rendering";
    mode: "run";
  }>;
  defaults: {
    template_name: string;
    editing_style: {
      pace: string;
      average_clip_duration: string;
      platform: string;
      aspect_ratio: string;
    };
  };
};

function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
}

function productGroup(productName: string) {
  return slugify(productName);
}

async function ensureMissing(target: string) {
  try {
    await fs.access(target);
    throw new Error(`Project already exists: ${target}`);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return;
    throw error;
  }
}

async function writeJson(target: string, data: unknown) {
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function buildFullWorkflowInput(input: CreateProjectInput, product: ProductProfile, projectDir: string) {
  const accountUrl = input.referenceAccountUrl?.trim() || input.referenceVideoUrl?.trim() || "";
  const referenceVideoUrl = input.referenceVideoUrl?.trim();

  return {
    account_url: accountUrl,
    target_platform: "TikTok",
    analysis_goal: "Extract reusable TikTok product-marketing video structures for this reference workflow.",
    video_list: referenceVideoUrl
      ? [
          {
            video_url: referenceVideoUrl,
            views: 0,
            likes: 0,
            comments: 0,
            caption: "",
            transcript: "",
            frames_summary: ""
          }
        ]
      : [],
    platform: "TikTok",
    video_length: input.videoLength || "25-35s",
    tone: input.tone || "native creator style, casual, not too salesy",
    product: {
      ...product,
      cta: `try ${product.product_name}`
    },
    asset_library: [],
    editing_style: {
      pace: "fast",
      average_clip_duration: "1.5-2.5s",
      platform: "TikTok",
      aspect_ratio: "9:16"
    },
    intake: {
      template_name: input.templateName || "Google Scholar trust template",
      material_directory: input.materialDirectory?.trim() || "",
      notes: input.notes?.trim() || "",
      project_dir: projectDir
    }
  };
}

function buildProjectJob(projectDir: string, product: ProductProfile, templateName: string): ProjectJob {
  return {
    project_id: path.basename(projectDir),
    project_dir: projectDir,
    product_name: product.product_name,
    workflow_mode: "fresh",
    source: {
      full_workflow_input: "full_workflow_input.json"
    },
    artifacts: {
      hook_frame_index: "output/hook_frame_index.json",
      human_hook_observation: "output/human_hook_observation.json",
      viral_pattern_card: "output/viral_pattern_card.json",
      human_hook_card: "output/human_hook_card.json",
      product_script_card: "output/product_script_card.json",
      shot_matching_plan: "output/shot_matching_plan.json",
      asset_library: "output/asset_library.json"
    },
    delivery: {
      mode: "preview_render",
      preview_video: "output/final_delivery/worker_preview.mp4",
      render_report: "output/final_delivery/worker_render_report.json"
    },
    stages: [
      { name: "reference_hook_analysis", mode: "run" },
      { name: "viral_deconstruction", mode: "run" },
      { name: "human_hook_generation", mode: "run" },
      { name: "product_script_rewrite", mode: "run" },
      { name: "asset_matching", mode: "run" },
      { name: "video_rendering", mode: "run" }
    ],
    defaults: {
      template_name: templateName,
      editing_style: {
        pace: "fast",
        average_clip_duration: "1.5-2.5s",
        platform: "TikTok",
        aspect_ratio: "9:16"
      }
    }
  };
}

export async function createProjectScaffold(input: CreateProjectInput) {
  const product = await getProductByName(input.productName);
  if (!product) {
    throw new Error(`Unknown product: ${input.productName}`);
  }

  const projectId = slugify(input.projectName);
  if (!projectId) {
    throw new Error("Project name is required.");
  }

  const group = productGroup(product.product_name);
  const projectDir = path.join(PROJECTS_ROOT, group, projectId);
  await ensureMissing(projectDir);

  await fs.mkdir(path.join(projectDir, "materials", "raw"), { recursive: true });
  await fs.mkdir(path.join(projectDir, "references"), { recursive: true });
  await fs.mkdir(path.join(projectDir, "output", "final_delivery"), { recursive: true });

  const fullWorkflowInput = buildFullWorkflowInput(input, product, projectDir);
  const assetLibrary = {
    assets: [],
    status: "needs_indexing",
    source_material_dir: input.materialDirectory?.trim() || "",
    note: "Index raw clips into this file before running full asset matching and render."
  };
  const intakeNotes = {
    project_name: input.projectName,
    product_name: product.product_name,
    template_name: input.templateName || "Google Scholar trust template",
    reference_account_url: input.referenceAccountUrl?.trim() || "",
    reference_video_url: input.referenceVideoUrl?.trim() || "",
    material_directory: input.materialDirectory?.trim() || "",
    notes: input.notes?.trim() || ""
  };
  const projectJob = buildProjectJob(projectDir, product, input.templateName || "Google Scholar trust template");

  await writeJson(path.join(projectDir, "full_workflow_input.json"), fullWorkflowInput);
  await writeJson(path.join(projectDir, "project_job.json"), projectJob);
  await writeJson(path.join(projectDir, "output", "asset_library.json"), assetLibrary);
  await writeJson(path.join(projectDir, "output", "intake_notes.json"), intakeNotes);

  return {
    slug: `${group}__${projectId}`,
    projectDir,
    projectId,
    group,
    productName: product.product_name
  };
}
