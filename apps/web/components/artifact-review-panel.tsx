"use client";

import { useMemo, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

type EditableArtifact = {
  key: string;
  label: string;
  description: string;
  path: string;
  exists: boolean;
  updatedAt: string | null;
  data: unknown;
};

type Props = {
  slug: string;
  artifacts: EditableArtifact[];
};

function formatDate(value: string | null) {
  if (!value) return "Not created yet";
  return value.replace("T", " ").replace(/\.\d+/, "").replace("+00:00", " UTC").replace("Z", " UTC");
}

function prettyJson(data: unknown) {
  if (data === null || data === undefined) return "{\n  \n}";
  return JSON.stringify(data, null, 2);
}

function boundaryNote(key: string) {
  if (key === "viral_pattern_card") return "Only edit reference logic here. Do not write product scripts in this card.";
  if (key === "product_script_card") return "Only edit product scripts here. Do not choose footage in this card.";
  return "Only edit clip decisions here. Do not rewrite the core script in this plan.";
}

export function ArtifactReviewPanel({ slug, artifacts }: Props) {
  const router = useRouter();
  const [activeKey, setActiveKey] = useState(artifacts[0]?.key || "");
  const activeArtifact = useMemo(
    () => artifacts.find((artifact) => artifact.key === activeKey) || artifacts[0],
    [activeKey, artifacts]
  );
  const [drafts, setDrafts] = useState<Record<string, string>>(() =>
    Object.fromEntries(artifacts.map((artifact) => [artifact.key, prettyJson(artifact.data)]))
  );
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  if (!activeArtifact) return null;

  const draft = drafts[activeArtifact.key] ?? prettyJson(activeArtifact.data);

  function updateDraft(value: string) {
    setError("");
    setMessage("");
    setDrafts((current) => ({
      ...current,
      [activeArtifact.key]: value
    }));
  }

  function formatDraft() {
    setError("");
    setMessage("");
    try {
      const parsed = JSON.parse(draft);
      updateDraft(JSON.stringify(parsed, null, 2));
    } catch (formatError) {
      setError(formatError instanceof Error ? formatError.message : "Invalid JSON.");
    }
  }

  function saveDraft() {
    setError("");
    setMessage("");
    let parsed: unknown;
    try {
      parsed = JSON.parse(draft);
    } catch (parseError) {
      setError(parseError instanceof Error ? parseError.message : "Invalid JSON.");
      return;
    }

    startTransition(async () => {
      try {
        const response = await fetch(`/api/projects/${slug}/artifacts/${activeArtifact.key}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data: parsed })
        });
        const data = (await response.json()) as { error?: string };
        if (!response.ok) {
          throw new Error(data.error || "Failed to save artifact.");
        }
        setMessage("Saved. Project data has been refreshed.");
        router.refresh();
      } catch (saveError) {
        setError(saveError instanceof Error ? saveError.message : "Failed to save artifact.");
      }
    });
  }

  return (
    <div className="border border-black/10 bg-panel p-6 shadow-panel">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Review Cards</div>
          <div className="mt-2 text-2xl font-semibold tracking-[-0.04em]">Editable workflow artifacts</div>
        </div>
        <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-black/42">
          {artifacts.filter((artifact) => artifact.exists).length} / {artifacts.length} created
        </div>
      </div>

      <div className="mt-5 grid gap-2 lg:grid-cols-3">
        {artifacts.map((artifact) => (
          <button
            key={artifact.key}
            type="button"
            onClick={() => {
              setActiveKey(artifact.key);
              setError("");
              setMessage("");
            }}
            className={`border px-3 py-3 text-left transition ${
              artifact.key === activeArtifact.key
                ? "border-black bg-black text-white"
                : "border-black/10 bg-[#f8f8f4] text-black"
            }`}
          >
            <div className="font-mono text-[10px] uppercase tracking-[0.2em] opacity-55">
              {artifact.exists ? "created" : "missing"}
            </div>
            <div className="mt-1 text-sm font-medium">{artifact.label}</div>
          </button>
        ))}
      </div>

      <div className="mt-5 border border-black/10 bg-[#f8f8f4] p-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-lg font-semibold tracking-[-0.03em]">{activeArtifact.label}</div>
            <div className="mt-1 max-w-2xl text-sm leading-6 text-black/62">{activeArtifact.description}</div>
          </div>
          <div className="text-right font-mono text-[11px] uppercase tracking-[0.18em] text-black/42">
            {formatDate(activeArtifact.updatedAt)}
          </div>
        </div>
        <div className="mt-3 border border-black/10 bg-white px-3 py-2 text-sm text-black/62">{boundaryNote(activeArtifact.key)}</div>
        <div className="mt-3 truncate font-mono text-[11px] text-black/40">{activeArtifact.path}</div>
      </div>

      <textarea
        value={draft}
        onChange={(event) => updateDraft(event.target.value)}
        spellCheck={false}
        className="mt-4 h-[420px] w-full resize-y border border-black/10 bg-[#111111] p-4 font-mono text-[12px] leading-5 text-white/82 outline-none focus:border-black"
      />

      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={saveDraft}
          disabled={isPending}
          className="rounded-md border border-black bg-black px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isPending ? "Saving..." : "Save JSON"}
        </button>
        <button
          type="button"
          onClick={formatDraft}
          disabled={isPending}
          className="rounded-md border border-black/20 bg-white px-4 py-2 text-sm font-medium text-black transition disabled:cursor-not-allowed disabled:opacity-50"
        >
          Format JSON
        </button>
      </div>

      {error ? <div className="mt-4 border border-[#d5a6a6] bg-[#fff6f6] px-4 py-3 text-sm text-[#8d2d2d]">{error}</div> : null}
      {message ? <div className="mt-4 border border-black/10 bg-[#f8f8f4] px-4 py-3 text-sm text-black/66">{message}</div> : null}
    </div>
  );
}
