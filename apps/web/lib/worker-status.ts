import { promises as fs } from "fs";
import path from "path";
import { spawn } from "child_process";

const REPO_ROOT = path.resolve(process.cwd(), "../..");
const VENV_PYTHON_BIN = path.join(REPO_ROOT, ".venv", "bin", "python3");
const FALLBACK_PYTHON_BIN = "python3";
const BACKGROUND_RUNNER = path.join(REPO_ROOT, "apps", "worker", "run_project_background.py");

export type WorkerRunState = "idle" | "running" | "completed" | "failed";
export type WorkerStageState = "pending" | "running" | "completed" | "failed";

export type WorkerStageStatus = {
  name: string;
  mode?: string;
  state: WorkerStageState;
  started_at?: string | null;
  finished_at?: string | null;
  output?: string | null;
  report?: string | null;
};

export type WorkerRunStatus = {
  state: WorkerRunState;
  job_file?: string;
  project_dir?: string;
  started_at?: string | null;
  finished_at?: string | null;
  return_code?: number | null;
  log_path?: string | null;
  error?: string | null;
  log_excerpt?: string[];
  stages?: WorkerStageStatus[];
};

function statusFilePath(projectDir: string) {
  return path.join(projectDir, "output", "worker_run_status.json");
}

function logFilePath(projectDir: string) {
  return path.join(projectDir, "output", "worker_run.log");
}

async function pathExists(target: string) {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
}

async function readRecentLogLines(target: string, maxLines = 80) {
  if (!(await pathExists(target))) return [];

  try {
    const stats = await fs.stat(target);
    const readSize = Math.min(stats.size, 80_000);
    const handle = await fs.open(target, "r");
    try {
      const buffer = Buffer.alloc(readSize);
      await handle.read(buffer, 0, readSize, Math.max(0, stats.size - readSize));
      return buffer
        .toString("utf8")
        .split(/\r?\n/)
        .filter(Boolean)
        .slice(-maxLines);
    } finally {
      await handle.close();
    }
  } catch {
    return ["Could not read worker log."];
  }
}

export async function readWorkerStatus(projectDir: string): Promise<WorkerRunStatus> {
  const target = statusFilePath(projectDir);
  const defaultLogPath = logFilePath(projectDir);
  if (!(await pathExists(target))) {
    return {
      state: "idle",
      project_dir: projectDir,
      log_path: defaultLogPath,
      log_excerpt: await readRecentLogLines(defaultLogPath),
      stages: []
    };
  }

  try {
    const raw = await fs.readFile(target, "utf8");
    const data = JSON.parse(raw) as WorkerRunStatus;
    const resolvedLogPath = data.log_path || defaultLogPath;
    return {
      state: data.state || "idle",
      job_file: data.job_file,
      project_dir: data.project_dir || projectDir,
      started_at: data.started_at || null,
      finished_at: data.finished_at || null,
      return_code: typeof data.return_code === "number" ? data.return_code : null,
      log_path: resolvedLogPath,
      error: data.error || null,
      log_excerpt: await readRecentLogLines(resolvedLogPath),
      stages: Array.isArray(data.stages) ? data.stages : []
    };
  } catch {
    return {
      state: "failed",
      project_dir: projectDir,
      log_path: defaultLogPath,
      error: "Could not read worker status file.",
      log_excerpt: await readRecentLogLines(defaultLogPath),
      stages: []
    };
  }
}

export async function startWorkerRun(projectDir: string) {
  const jobFile = path.join(projectDir, "project_job.json");
  if (!(await pathExists(jobFile))) {
    throw new Error(`Missing project_job.json in ${projectDir}`);
  }

  const current = await readWorkerStatus(projectDir);
  if (current.state === "running") {
    return current;
  }

  const pythonBin = (await pathExists(VENV_PYTHON_BIN)) ? VENV_PYTHON_BIN : FALLBACK_PYTHON_BIN;
  const child = spawn(pythonBin, [BACKGROUND_RUNNER, "--job-file", jobFile], {
    cwd: projectDir,
    detached: true,
    stdio: "ignore"
  });
  child.unref();

  return {
    state: "running" as const,
    project_dir: projectDir,
    job_file: jobFile,
    started_at: new Date().toISOString(),
    finished_at: null,
    return_code: null,
    log_path: logFilePath(projectDir),
    error: null,
    log_excerpt: current.log_excerpt || [],
    stages: current.stages || []
  };
}
