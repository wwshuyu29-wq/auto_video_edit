import { promises as fs } from "fs";
import path from "path";
import { projectDirFromSlug } from "@/lib/project-paths";

export type EditableArtifactKey =
  | "human_hook_observation"
  | "viral_pattern_card"
  | "human_hook_card"
  | "product_script_card"
  | "shot_matching_plan";

const ARTIFACTS: Record<
  EditableArtifactKey,
  {
    label: string;
    description: string;
    relativePath: string;
  }
> = {
  human_hook_observation: {
    label: "Human Hook Observation",
    description: "Extracted hook frames and visual observation from the reference video's first seconds.",
    relativePath: "output/human_hook_observation.json"
  },
  viral_pattern_card: {
    label: "Viral Pattern Card",
    description: "Why the reference works. This should not write your product script.",
    relativePath: "output/viral_pattern_card.json"
  },
  human_hook_card: {
    label: "Human Hook Card",
    description: "AI human opening analysis, text-to-video prompt, generation status, and generated hook asset.",
    relativePath: "output/human_hook_card.json"
  },
  product_script_card: {
    label: "Product Script Card",
    description: "Product-native TikTok script variants. This should not choose footage.",
    relativePath: "output/product_script_card.json"
  },
  shot_matching_plan: {
    label: "Shot Matching Plan",
    description: "Clip decisions for each script beat. This should not rewrite the script.",
    relativePath: "output/shot_matching_plan.json"
  }
};

export function editableArtifactKeys() {
  return Object.keys(ARTIFACTS) as EditableArtifactKey[];
}

export function artifactDefinition(key: string) {
  return ARTIFACTS[key as EditableArtifactKey] || null;
}

async function pathExists(target: string) {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
}

async function readJson(target: string) {
  try {
    const raw = await fs.readFile(target, "utf8");
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

async function writeJson(target: string, data: unknown) {
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

export async function readEditableArtifact(slug: string, key: string) {
  const definition = artifactDefinition(key);
  if (!definition) {
    throw new Error(`Unsupported artifact: ${key}`);
  }

  const projectDir = projectDirFromSlug(slug);
  const artifactPath = path.join(projectDir, definition.relativePath);
  const exists = await pathExists(artifactPath);
  const data = exists ? await readJson(artifactPath) : null;
  let updatedAt: string | null = null;
  if (exists) {
    try {
      updatedAt = (await fs.stat(artifactPath)).mtime.toISOString();
    } catch {
      updatedAt = null;
    }
  }

  return {
    key,
    label: definition.label,
    description: definition.description,
    path: artifactPath,
    exists,
    updatedAt,
    data
  };
}

export async function readEditableArtifacts(slug: string) {
  return Promise.all(editableArtifactKeys().map((key) => readEditableArtifact(slug, key)));
}

export async function updateEditableArtifact(slug: string, key: string, data: unknown) {
  const definition = artifactDefinition(key);
  if (!definition) {
    throw new Error(`Unsupported artifact: ${key}`);
  }

  const projectDir = projectDirFromSlug(slug);
  const artifactPath = path.join(projectDir, definition.relativePath);
  await writeJson(artifactPath, data);
  return readEditableArtifact(slug, key);
}
