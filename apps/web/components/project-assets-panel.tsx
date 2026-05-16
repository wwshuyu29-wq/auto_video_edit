"use client";

import { useRouter } from "next/navigation";
import { useRef, useState, useTransition } from "react";

type AssetPreview = {
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
};

type AssetLibrary = {
  status: string;
  assetCount: number;
  sourceMaterialDir: string;
  updatedAt?: string;
  assets: AssetPreview[];
};

type Props = {
  slug: string;
  assetLibrary: AssetLibrary;
};

function formatDuration(duration: number | null) {
  if (duration === null) return "unknown";
  return `${duration.toFixed(1)}s`;
}

function formatDate(value?: string) {
  if (!value) return "Not indexed yet";
  return value.replace("T", " ").replace(/\.\d+/, "").replace("+00:00", " UTC").replace("Z", " UTC");
}

function mediaUrl(localPath?: string) {
  if (!localPath) return "";
  return `/api/media?path=${encodeURIComponent(localPath)}`;
}

function listToText(items: string[]) {
  return items.join(", ");
}

function AssetCard({ slug, asset, onSaved }: { slug: string; asset: AssetPreview; onSaved: () => void }) {
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState("");
  const [shotType, setShotType] = useState(asset.shotType);
  const [scene, setScene] = useState(asset.scene);
  const [bestUse, setBestUse] = useState(listToText(asset.bestUse));
  const [visibleObjects, setVisibleObjects] = useState(listToText(asset.visibleObjects));
  const [textOverlaySafeArea, setTextOverlaySafeArea] = useState(asset.textOverlaySafeArea);
  const [notes, setNotes] = useState(asset.notes);

  function saveLabels() {
    setError("");
    startTransition(async () => {
      try {
        const response = await fetch(`/api/projects/${slug}/assets`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            clipId: asset.clipId,
            patch: {
              shot_type: shotType,
              scene,
              best_use: bestUse,
              visible_objects: visibleObjects,
              text_overlay_safe_area: textOverlaySafeArea,
              notes
            }
          })
        });
        const data = (await response.json()) as { error?: string };
        if (!response.ok) {
          throw new Error(data.error || "Failed to save labels.");
        }
        onSaved();
      } catch (saveError) {
        setError(saveError instanceof Error ? saveError.message : "Failed to save labels.");
      }
    });
  }

  return (
    <div className="grid gap-4 border border-black/10 bg-[#f8f8f4] p-3 text-sm lg:grid-cols-[130px_1fr]">
      <div className="overflow-hidden border border-black/10 bg-black">
        {asset.thumbnailPath ? (
          <img src={mediaUrl(asset.thumbnailPath)} alt={asset.clipId} className="aspect-[9/16] w-full object-cover" />
        ) : (
          <div className="flex aspect-[9/16] items-center justify-center px-3 text-center font-mono text-[10px] uppercase tracking-[0.18em] text-white/45">
            no thumbnail
          </div>
        )}
      </div>

      <div className="min-w-0">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="truncate font-medium">{asset.clipId}</div>
          <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-steel">
            {formatDuration(asset.duration)} / {asset.orientation}
          </div>
        </div>
        <div className="mt-2 truncate font-mono text-[11px] text-black/42">{asset.filePath}</div>

        <div className="mt-4 grid gap-3 lg:grid-cols-2">
          <label className="grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Shot type</span>
            <input
              value={shotType}
              onChange={(event) => setShotType(event.target.value)}
              placeholder="landing page / search results / CTA"
              className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
          <label className="grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Scene</span>
            <input
              value={scene}
              onChange={(event) => setScene(event.target.value)}
              placeholder="Google Scholar / Citely verify result"
              className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
          <label className="grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Best use</span>
            <input
              value={bestUse}
              onChange={(event) => setBestUse(event.target.value)}
              placeholder="opening hook, product proof, CTA"
              className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
          <label className="grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Visible objects</span>
            <input
              value={visibleObjects}
              onChange={(event) => setVisibleObjects(event.target.value)}
              placeholder="logo, search bar, result list"
              className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
          <label className="grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Subtitle safe area</span>
            <input
              value={textOverlaySafeArea}
              onChange={(event) => setTextOverlaySafeArea(event.target.value)}
              placeholder="top center / lower third / center"
              className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
          <div className="flex items-end">
            <button
              type="button"
              onClick={saveLabels}
              disabled={isPending}
              className="w-full rounded-md border border-black bg-black px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isPending ? "Saving..." : "Save Labels"}
            </button>
          </div>
        </div>

        <label className="mt-3 grid gap-1">
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">Notes</span>
          <textarea
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            rows={2}
            className="resize-none border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
          />
        </label>
        {error ? <div className="mt-3 border border-[#d5a6a6] bg-[#fff6f6] px-3 py-2 text-sm text-[#8d2d2d]">{error}</div> : null}
      </div>
    </div>
  );
}

export function ProjectAssetsPanel({ slug, assetLibrary }: Props) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState("");
  const [selectedCount, setSelectedCount] = useState(0);

  function uploadAssets() {
    setError("");
    startTransition(async () => {
      try {
        const files = fileInputRef.current?.files;
        if (!files || files.length === 0) {
          throw new Error("Choose at least one video file first.");
        }

        const formData = new FormData();
        Array.from(files).forEach((file) => formData.append("files", file));
        const response = await fetch(`/api/projects/${slug}/assets`, {
          method: "POST",
          body: formData
        });
        const data = (await response.json()) as { error?: string };
        if (!response.ok) {
          throw new Error(data.error || "Failed to upload assets.");
        }
        if (fileInputRef.current) fileInputRef.current.value = "";
        setSelectedCount(0);
        router.refresh();
      } catch (uploadError) {
        setError(uploadError instanceof Error ? uploadError.message : "Failed to upload assets.");
      }
    });
  }

  function indexExistingAssets() {
    setError("");
    startTransition(async () => {
      try {
        const response = await fetch(`/api/projects/${slug}/assets/index`, { method: "POST" });
        const data = (await response.json()) as { error?: string };
        if (!response.ok) {
          throw new Error(data.error || "Failed to index existing files.");
        }
        router.refresh();
      } catch (indexError) {
        setError(indexError instanceof Error ? indexError.message : "Failed to index existing files.");
      }
    });
  }

  return (
    <div className="border border-black/10 bg-panel p-6 shadow-panel">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Assets</div>
          <div className="mt-2 text-2xl font-semibold tracking-[-0.04em]">Footage library</div>
        </div>
        <div className="rounded-full border border-black/10 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.22em] text-black/62">
          {assetLibrary.assetCount} clips
        </div>
      </div>

      <div className="mt-4 grid gap-3 text-sm text-black/64">
        <div>Status: {assetLibrary.status}</div>
        <div>Updated: {formatDate(assetLibrary.updatedAt)}</div>
        <div className="break-all">Folder: {assetLibrary.sourceMaterialDir}</div>
      </div>

      <div className="mt-5 border border-dashed border-black/20 bg-[#f8f8f4] p-4">
        <input
          ref={fileInputRef}
          type="file"
          accept=".mp4,.mov,.m4v,.avi,.mkv,.webm,video/*"
          multiple
          onChange={(event) => setSelectedCount(event.target.files?.length || 0)}
          className="block w-full text-sm text-black/70 file:mr-4 file:rounded-md file:border file:border-black file:bg-black file:px-4 file:py-2 file:text-sm file:font-medium file:text-white"
        />
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={uploadAssets}
            disabled={isPending || selectedCount === 0}
            className="rounded-md border border-black bg-black px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isPending ? "Working..." : selectedCount > 0 ? `Upload ${selectedCount} File${selectedCount > 1 ? "s" : ""}` : "Upload Files"}
          </button>
          <button
            type="button"
            onClick={indexExistingAssets}
            disabled={isPending}
            className="rounded-md border border-black/20 bg-white px-4 py-2 text-sm font-medium text-black transition disabled:cursor-not-allowed disabled:opacity-50"
          >
            Re-index Folder
          </button>
        </div>
      </div>

      {assetLibrary.assets.length > 0 ? (
        <div className="mt-5 space-y-3">
          {assetLibrary.assets.map((asset) => (
            <AssetCard key={asset.clipId} slug={slug} asset={asset} onSaved={() => router.refresh()} />
          ))}
        </div>
      ) : (
        <div className="mt-5 border border-black/10 bg-[#111111] p-4 text-sm text-white/70">
          No clips indexed yet. Upload `.mov` or `.mp4` files, or place them in the raw folder and re-index.
        </div>
      )}

      {error ? <div className="mt-4 border border-[#d5a6a6] bg-[#fff6f6] px-4 py-3 text-sm text-[#8d2d2d]">{error}</div> : null}
    </div>
  );
}
