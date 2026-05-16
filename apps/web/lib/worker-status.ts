import { promises as fs } from "fs";
import path from "path";
import { spawn } from "child_process";

const REPO_ROOT = path.resolve(process.cwd(), "../..");
const PYTHON_BIN = "python3";
const BACKGROUND_RUNNER = path.join(REPO_ROOT, "apps", "worker", "run_project_background.py");

export type WorkerRunState = "idle" | "running" | "completed" | "failed";

export type WorkerRunStatus = {
  state: WorkerRunState;
  job_file?: string;
  project_dir?: string;
  started_at?: string | null;
  finished_at?: string | null;
  return_code?: number | null;
  log_path?: string | null;
  error?: string | null;
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

export async function readWorkerStatus(projectDir: string): Promise<WorkerRunStatus> {
  const target = statusFilePath(projectDir);
  if (!(await pathExists(target))) {
    return { state: "idle", project_dir: projectDir, log_path: logFilePath(projectDir) };
  }

  try {
    const raw = await fs.readFile(target, "utf8");
    const data = JSON.parse(raw) as WorkerRunStatus;
    return {
      state: data.state || "idle",
      job_file: data.job_file,
      project_dir: data.project_dir || projectDir,
      started_at: data.started_at || null,
      finished_at: data.finished_at || null,
      return_code: typeof data.return_code === "number" ? data.return_code : null,
      log_path: data.log_path || logFilePath(projectDir),
      error: data.error || null
    };
  } catch {
    return {
      state: "failed",
      project_dir: projectDir,
      log_path: logFilePath(projectDir),
      error: "Could not read worker status file."
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

  const child = spawn(PYTHON_BIN, [BACKGROUND_RUNNER, "--job-file", jobFile], {
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
    error: null
  };
}

