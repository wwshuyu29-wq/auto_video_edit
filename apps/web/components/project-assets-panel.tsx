"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState, useTransition } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

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

function FieldLabel({ children }: { children: string }) {
  return <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted-foreground">{children}</span>;
}

export function ProjectAssetsPanel({ slug, assetLibrary }: Props) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState("");
  const [selectedCount, setSelectedCount] = useState(0);
  const [activeClipId, setActiveClipId] = useState(assetLibrary.assets[0]?.clipId || "");
  const activeAsset = useMemo(
    () => assetLibrary.assets.find((asset) => asset.clipId === activeClipId) || assetLibrary.assets[0],
    [activeClipId, assetLibrary.assets]
  );
  const [shotType, setShotType] = useState(activeAsset?.shotType || "");
  const [scene, setScene] = useState(activeAsset?.scene || "");
  const [bestUse, setBestUse] = useState(activeAsset ? listToText(activeAsset.bestUse) : "");
  const [visibleObjects, setVisibleObjects] = useState(activeAsset ? listToText(activeAsset.visibleObjects) : "");
  const [textOverlaySafeArea, setTextOverlaySafeArea] = useState(activeAsset?.textOverlaySafeArea || "");
  const [notes, setNotes] = useState(activeAsset?.notes || "");

  useEffect(() => {
    if (!activeAsset) return;
    setShotType(activeAsset.shotType);
    setScene(activeAsset.scene);
    setBestUse(listToText(activeAsset.bestUse));
    setVisibleObjects(listToText(activeAsset.visibleObjects));
    setTextOverlaySafeArea(activeAsset.textOverlaySafeArea);
    setNotes(activeAsset.notes);
  }, [activeAsset]);

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

  function saveLabels() {
    if (!activeAsset) return;
    setError("");
    startTransition(async () => {
      try {
        const response = await fetch(`/api/projects/${slug}/assets`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            clipId: activeAsset.clipId,
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
        router.refresh();
      } catch (saveError) {
        setError(saveError instanceof Error ? saveError.message : "Failed to save labels.");
      }
    });
  }

  return (
    <Card className="h-full min-h-0 rounded-none border-black/10 bg-panel">
      <CardHeader className="border-b border-black/10">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">Assets</div>
            <CardTitle className="mt-2 text-2xl tracking-[-0.04em]">Footage library</CardTitle>
          </div>
          <Badge variant="outline">{assetLibrary.assetCount} clips</Badge>
        </div>
        <div className="mt-3 grid gap-1 text-xs text-muted-foreground">
          <div>Status: {assetLibrary.status}</div>
          <div>Updated: {formatDate(assetLibrary.updatedAt)}</div>
          <div className="truncate">Folder: {assetLibrary.sourceMaterialDir}</div>
        </div>
      </CardHeader>

      <CardContent className="grid min-h-0 gap-4 p-4 xl:grid-cols-[300px_minmax(0,1fr)]">
        <div className="flex min-h-0 flex-col gap-3">
          <div className="border border-dashed border-black/20 bg-[#f8f8f4] p-3">
            <Input
              ref={fileInputRef}
              type="file"
              accept=".mp4,.mov,.m4v,.avi,.mkv,.webm,video/*"
              multiple
              onChange={(event) => setSelectedCount(event.target.files?.length || 0)}
              className="h-auto bg-white file:mr-3 file:rounded-md file:border-0 file:bg-black file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-white"
            />
            <div className="mt-3 flex flex-wrap gap-2">
              <Button type="button" onClick={uploadAssets} disabled={isPending || selectedCount === 0} size="sm">
                {selectedCount > 0 ? `Upload ${selectedCount}` : "Upload"}
              </Button>
              <Button type="button" onClick={indexExistingAssets} disabled={isPending} size="sm" variant="outline">
                Re-index
              </Button>
            </div>
          </div>

          <ScrollArea className="h-[520px] rounded-none border border-black/10 bg-white">
            <div className="flex flex-col">
              {assetLibrary.assets.map((asset) => {
                const active = asset.clipId === activeAsset?.clipId;
                return (
                  <button
                    key={asset.clipId}
                    type="button"
                    onClick={() => setActiveClipId(asset.clipId)}
                    className={cn(
                      "grid grid-cols-[72px_minmax(0,1fr)] gap-3 border-b border-black/10 p-3 text-left transition last:border-b-0",
                      active ? "bg-black text-white" : "bg-white hover:bg-black/[0.035]"
                    )}
                  >
                    <div className="overflow-hidden border border-black/10 bg-black">
                      {asset.thumbnailPath ? (
                        <img src={mediaUrl(asset.thumbnailPath)} alt={asset.clipId} className="aspect-[9/16] w-full object-cover" />
                      ) : (
                        <div className="flex aspect-[9/16] items-center justify-center px-2 text-center font-mono text-[9px] uppercase tracking-[0.12em] text-white/45">
                          no thumb
                        </div>
                      )}
                    </div>
                    <div className="min-w-0">
                      <div className="truncate text-sm font-semibold">{asset.clipId}</div>
                      <div className={cn("mt-1 font-mono text-[10px] uppercase tracking-[0.16em]", active ? "text-white/55" : "text-muted-foreground")}>
                        {formatDuration(asset.duration)} / {asset.orientation}
                      </div>
                      <div className={cn("mt-2 line-clamp-2 text-xs", active ? "text-white/68" : "text-black/58")}>{asset.scene}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </ScrollArea>
        </div>

        {activeAsset ? (
          <div className="min-w-0 border border-black/10 bg-white">
            <div className="grid gap-4 border-b border-black/10 p-4 lg:grid-cols-[180px_minmax(0,1fr)]">
              <div className="overflow-hidden border border-black/10 bg-black">
                {activeAsset.thumbnailPath ? (
                  <img src={mediaUrl(activeAsset.thumbnailPath)} alt={activeAsset.clipId} className="aspect-[9/16] w-full object-cover" />
                ) : (
                  <div className="flex aspect-[9/16] items-center justify-center px-3 text-center font-mono text-[10px] uppercase tracking-[0.18em] text-white/45">
                    no thumbnail
                  </div>
                )}
              </div>
              <div className="min-w-0">
                <div className="truncate text-xl font-semibold tracking-[-0.03em]">{activeAsset.clipId}</div>
                <div className="mt-2 font-mono text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
                  {formatDuration(activeAsset.duration)} / {activeAsset.orientation}
                </div>
                <div className="mt-4 truncate font-mono text-xs text-black/45">{activeAsset.filePath}</div>
                <div className="mt-4 grid gap-2 text-xs text-black/58 sm:grid-cols-2">
                  <div>
                    <span className="font-mono uppercase tracking-[0.16em] text-muted-foreground">best use</span>
                    <div className="mt-1 line-clamp-2">{activeAsset.bestUse.join(", ") || "unlabeled"}</div>
                  </div>
                  <div>
                    <span className="font-mono uppercase tracking-[0.16em] text-muted-foreground">safe area</span>
                    <div className="mt-1 line-clamp-2">{activeAsset.textOverlaySafeArea}</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-3 p-4 xl:grid-cols-2">
              <label className="grid gap-1">
                <FieldLabel>Shot type</FieldLabel>
                <Input value={shotType} onChange={(event) => setShotType(event.target.value)} />
              </label>
              <label className="grid gap-1">
                <FieldLabel>Scene</FieldLabel>
                <Input value={scene} onChange={(event) => setScene(event.target.value)} />
              </label>
              <label className="grid gap-1">
                <FieldLabel>Best use</FieldLabel>
                <Input value={bestUse} onChange={(event) => setBestUse(event.target.value)} />
              </label>
              <label className="grid gap-1">
                <FieldLabel>Visible objects</FieldLabel>
                <Input value={visibleObjects} onChange={(event) => setVisibleObjects(event.target.value)} />
              </label>
              <label className="grid gap-1 xl:col-span-2">
                <FieldLabel>Subtitle safe area</FieldLabel>
                <Input value={textOverlaySafeArea} onChange={(event) => setTextOverlaySafeArea(event.target.value)} />
              </label>
              <label className="grid gap-1 xl:col-span-2">
                <FieldLabel>Notes</FieldLabel>
                <Textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={3} />
              </label>
              <div className="flex justify-end xl:col-span-2">
                <Button type="button" onClick={saveLabels} disabled={isPending}>
                  {isPending ? "Saving..." : "Save Labels"}
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="border border-black/10 bg-[#111111] p-4 text-sm text-white/70">
            No clips indexed yet. Upload `.mov` or `.mp4` files, or place them in the raw folder and re-index.
          </div>
        )}
      </CardContent>

      {error ? <div className="mx-4 mb-4 border border-[#d5a6a6] bg-[#fff6f6] px-4 py-3 text-sm text-[#8d2d2d]">{error}</div> : null}
    </Card>
  );
}
