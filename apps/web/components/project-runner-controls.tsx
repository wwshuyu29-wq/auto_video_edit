"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition } from "react";

type WorkerStatus = {
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

type PreflightReport = {
  status: "ready" | "blocked";
  blockerCount: number;
  warningCount: number;
  checkedAt: string;
  checks: Array<{
    id: string;
    label: string;
    severity: "pass" | "warning" | "blocker";
    message: string;
  }>;
};

type Props = {
  slug: string;
  workerStatus: WorkerStatus;
  preflight: PreflightReport;
};

function stateLabel(state: WorkerStatus["state"]) {
  if (state === "running") return "Running";
  if (state === "completed") return "Completed";
  if (state === "failed") return "Failed";
  return "Idle";
}

function stageLabel(name: string) {
  return name.replaceAll("_", " ");
}

function stageStateClassName(state: WorkerStatus["stages"][number]["state"]) {
  if (state === "completed") return "border-black bg-black text-white";
  if (state === "running") return "border-black bg-[#f8f8f4] text-black";
  if (state === "failed") return "border-[#d5a6a6] bg-[#fff6f6] text-[#8d2d2d]";
  return "border-black/10 bg-[#f8f8f4] text-black/58";
}

function formatDate(value?: string | null) {
  if (!value) return "Not available";
  return value.replace("T", " ").replace(/\.\d+/, "").replace("+00:00", " UTC").replace("Z", " UTC");
}

function preflightClassName(severity: PreflightReport["checks"][number]["severity"]) {
  if (severity === "pass") return "border-black/10 bg-[#f8f8f4] text-black/64";
  if (severity === "warning") return "border-[#d9c58f] bg-[#fffaf0] text-[#735b16]";
  return "border-[#d5a6a6] bg-[#fff6f6] text-[#8d2d2d]";
}

function preflightLabel(status: PreflightReport["status"]) {
  return status === "ready" ? "Ready" : "Blocked";
}

export function ProjectRunnerControls({ slug, workerStatus, preflight }: Props) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState("");
  const hasBlockers = preflight.status === "blocked";

  useEffect(() => {
    if (workerStatus.state !== "running") return;

    const timer = window.setInterval(() => {
      router.refresh();
    }, 3000);

    return () => window.clearInterval(timer);
  }, [router, workerStatus.state]);

  function runProject() {
    setError("");
    startTransition(async () => {
      try {
        const response = await fetch(`/api/projects/${slug}/run`, { method: "POST" });
        const data = (await response.json()) as { error?: string };
        if (!response.ok) {
          throw new Error(data.error || "Failed to start worker.");
        }
        router.refresh();
      } catch (runError) {
        setError(runError instanceof Error ? runError.message : "Failed to start worker.");
      }
    });
  }

  return (
    <div className="border border-black/10 bg-panel p-6 shadow-panel">
      <div className="flex items-end justify-between gap-4">
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Worker Run</div>
          <div className="mt-2 flex items-center gap-3">
            <div className="text-2xl font-semibold tracking-[-0.04em]">{stateLabel(workerStatus.state)}</div>
            {workerStatus.state === "running" ? <div className="h-2.5 w-2.5 rounded-full bg-black animate-pulse" /> : null}
          </div>
        </div>
        <button
          type="button"
          disabled={isPending || workerStatus.state === "running" || hasBlockers}
          onClick={runProject}
          className="rounded-md border border-black bg-black px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-60"
        >
          {workerStatus.state === "running" ? "Worker Running..." : isPending ? "Starting..." : "Run Worker"}
        </button>
      </div>

      <div className="mt-5 border border-black/10 bg-white p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Preflight</div>
            <div className="mt-1 text-lg font-semibold tracking-[-0.03em]">{preflightLabel(preflight.status)}</div>
          </div>
          <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-black/48">
            {preflight.blockerCount} blockers / {preflight.warningCount} warnings
          </div>
        </div>
        <div className="mt-3 grid gap-2">
          {preflight.checks.map((check) => (
            <div key={check.id} className={`border px-3 py-2 text-sm ${preflightClassName(check.severity)}`}>
              <div className="flex items-center justify-between gap-3">
                <div className="font-medium">{check.label}</div>
                <div className="font-mono text-[10px] uppercase tracking-[0.18em]">{check.severity}</div>
              </div>
              <div className="mt-1 leading-5 opacity-80">{check.message}</div>
            </div>
          ))}
        </div>
        {hasBlockers ? (
          <div className="mt-3 border border-[#d5a6a6] bg-[#fff6f6] px-3 py-2 text-sm text-[#8d2d2d]">
            Fix the blocker checks before running the worker.
          </div>
        ) : null}
      </div>

      <div className="mt-4 space-y-2 text-sm text-black/64">
        <div>Started: {workerStatus.startedAt ? formatDate(workerStatus.startedAt) : "Not started"}</div>
        <div>Finished: {workerStatus.finishedAt ? formatDate(workerStatus.finishedAt) : "Not finished"}</div>
        <div>Log: {workerStatus.logPath || "Not created yet"}</div>
        {workerStatus.state === "running" ? <div>Auto refresh: every 3 seconds</div> : null}
      </div>

      {workerStatus.stages.length > 0 ? (
        <div className="mt-5 grid gap-2">
          {workerStatus.stages.map((stage, index) => (
            <div
              key={stage.name}
              className={`flex items-center justify-between border px-3 py-2 text-sm transition ${stageStateClassName(stage.state)}`}
            >
              <div className="min-w-0">
                <div className="truncate font-medium">
                  {index + 1}. {stageLabel(stage.name)}
                </div>
                <div className={`mt-1 font-mono text-[11px] uppercase tracking-[0.2em] ${stage.state === "completed" ? "text-white/55" : "text-black/45"}`}>
                  {stage.mode || "run"}
                </div>
              </div>
              <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.2em]">
                {stage.state === "running" ? <span className="h-2 w-2 rounded-full bg-black animate-pulse" /> : null}
                {stage.state}
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {workerStatus.logExcerpt.length > 0 ? (
        <div className="mt-5 border border-black/10 bg-[#111111] p-4 text-white">
          <div className="flex items-center justify-between gap-4">
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-white/45">Recent Log</div>
            <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-white/35">
              last {workerStatus.logExcerpt.length} lines
            </div>
          </div>
          <pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap break-words font-mono text-[11px] leading-5 text-white/70">
            {workerStatus.logExcerpt.join("\n")}
          </pre>
        </div>
      ) : null}

      {workerStatus.error ? (
        <div className="mt-4 border border-[#d5a6a6] bg-[#fff6f6] px-4 py-3 text-sm text-[#8d2d2d]">
          {workerStatus.error}
        </div>
      ) : null}
      {error ? <div className="mt-4 border border-[#d5a6a6] bg-[#fff6f6] px-4 py-3 text-sm text-[#8d2d2d]">{error}</div> : null}
    </div>
  );
}
