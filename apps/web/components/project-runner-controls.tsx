"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition } from "react";

type WorkerStatus = {
  state: "idle" | "running" | "completed" | "failed";
  startedAt?: string | null;
  finishedAt?: string | null;
  logPath?: string | null;
  error?: string | null;
};

type Props = {
  slug: string;
  workerStatus: WorkerStatus;
};

function stateLabel(state: WorkerStatus["state"]) {
  if (state === "running") return "Running";
  if (state === "completed") return "Completed";
  if (state === "failed") return "Failed";
  return "Idle";
}

function formatDate(value?: string | null) {
  if (!value) return "Not available";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export function ProjectRunnerControls({ slug, workerStatus }: Props) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState("");

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
          disabled={isPending || workerStatus.state === "running"}
          onClick={runProject}
          className="rounded-md border border-black bg-black px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-60"
        >
          {workerStatus.state === "running" ? "Worker Running..." : isPending ? "Starting..." : "Run Worker"}
        </button>
      </div>

      <div className="mt-4 space-y-2 text-sm text-black/64">
        <div>Started: {workerStatus.startedAt ? formatDate(workerStatus.startedAt) : "Not started"}</div>
        <div>Finished: {workerStatus.finishedAt ? formatDate(workerStatus.finishedAt) : "Not finished"}</div>
        <div>Log: {workerStatus.logPath || "Not created yet"}</div>
        {workerStatus.state === "running" ? <div>Auto refresh: every 3 seconds</div> : null}
      </div>

      {workerStatus.error ? (
        <div className="mt-4 border border-[#d5a6a6] bg-[#fff6f6] px-4 py-3 text-sm text-[#8d2d2d]">
          {workerStatus.error}
        </div>
      ) : null}
      {error ? <div className="mt-4 border border-[#d5a6a6] bg-[#fff6f6] px-4 py-3 text-sm text-[#8d2d2d]">{error}</div> : null}
    </div>
  );
}
