"use client";

import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type CaptionStyle = {
  lines?: string[];
  font_size?: number;
  line_gap?: number;
  y_ratio?: number;
  max_width?: number;
  highlight_terms?: string[];
  highlight_fill?: number[];
  [key: string]: unknown;
};

type EditPlanItem = {
  beat?: string;
  time?: string;
  voiceover?: string;
  clip_id?: string;
  clip_start?: number;
  clip_end?: number;
  playback_speed?: number;
  speed_reason?: string;
  reason?: string;
  on_screen_text?: string;
  caption_style?: CaptionStyle;
  transition?: string;
  subtitle_priority?: string;
  [key: string]: unknown;
};

type MissingAsset = {
  need?: string;
  suggestion?: string;
  [key: string]: unknown;
};

type ShotMatchingPlan = {
  source_script_card?: string;
  selected_script_type?: string;
  editing_style?: Record<string, unknown>;
  edit_plan?: EditPlanItem[];
  missing_assets?: MissingAsset[];
  risk_notes?: string[];
  needs_script_revision?: boolean;
  reason?: string;
  suggested_revision?: string;
  scores?: Record<string, number>;
  [key: string]: unknown;
};

type Props = {
  draft: string;
  onChange: (value: string) => void;
  assetLibrary?: AssetLibrary;
};

type AssetLibrary = {
  assets: AssetOption[];
};

type AssetOption = {
  clipId: string;
  filePath: string;
  thumbnailPath?: string;
  duration: number | null;
  orientation: string;
  shotType: string;
  scene: string;
  visibleObjects: string[];
  bestUse: string[];
  textOverlaySafeArea: string;
  notes: string;
};

function parseDraft(draft: string): ShotMatchingPlan | null {
  try {
    const parsed = JSON.parse(draft);
    if (!parsed || typeof parsed !== "object" || !Array.isArray(parsed.edit_plan)) return null;
    return parsed as ShotMatchingPlan;
  } catch {
    return null;
  }
}

function toDraft(data: ShotMatchingPlan) {
  return JSON.stringify(data, null, 2);
}

function clone(data: ShotMatchingPlan): ShotMatchingPlan {
  return JSON.parse(JSON.stringify(data)) as ShotMatchingPlan;
}

function listToText(items?: unknown[]) {
  return Array.isArray(items) ? items.map(String).join(", ") : "";
}

function textToList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function linesToText(items?: string[]) {
  return Array.isArray(items) ? items.join("\n") : "";
}

function textToLines(value: string) {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function numberOrUndefined(value: string) {
  if (value.trim() === "") return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function boolLabel(value?: boolean) {
  return value ? "true" : "false";
}

function emptyEditPlanItem(): EditPlanItem {
  return {
    beat: "",
    time: "",
    voiceover: "",
    clip_id: "",
    clip_start: 0,
    clip_end: 0,
    playback_speed: 1,
    speed_reason: "",
    reason: "",
    on_screen_text: "",
    transition: "hard cut",
    subtitle_priority: "normal",
    caption_style: {
      lines: []
    }
  };
}

function emptyMissingAsset(): MissingAsset {
  return {
    need: "",
    suggestion: ""
  };
}

function fieldLabel(value: string) {
  return value.replaceAll("_", " ");
}

function mediaUrl(localPath?: string) {
  if (!localPath) return "";
  return `/api/media?path=${encodeURIComponent(localPath)}`;
}

function formatDuration(duration: number | null) {
  if (duration === null) return "unknown";
  return `${duration.toFixed(1)}s`;
}

function FieldLabel({ children }: { children: string }) {
  return <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">{children}</span>;
}

export function ShotMatchingFormEditor({ draft, onChange, assetLibrary }: Props) {
  const data = parseDraft(draft);
  const [activeIndex, setActiveIndex] = useState(0);
  const parsedEditPlan = Array.isArray(data?.edit_plan) ? data.edit_plan : [];
  const totalSeconds = useMemo(
    () =>
      parsedEditPlan.reduce((sum, item) => {
        const start = typeof item.clip_start === "number" ? item.clip_start : 0;
        const end = typeof item.clip_end === "number" ? item.clip_end : start;
        const speed = typeof item.playback_speed === "number" && item.playback_speed > 0 ? item.playback_speed : 1;
        return sum + Math.max(0, end - start) / speed;
      }, 0),
    [parsedEditPlan]
  );

  if (!data || !Array.isArray(data.edit_plan)) {
    return (
      <div className="mt-4 border border-[#d9c58f] bg-[#fffaf0] px-4 py-3 text-sm text-[#735b16]">
        Shot matching form is available after this plan contains a valid `edit_plan` array.
      </div>
    );
  }

  const plan = data;
  const assets = assetLibrary?.assets || [];
  const assetById = new Map(assets.map((asset) => [asset.clipId, asset]));
  const editPlan = parsedEditPlan;
  const safeActiveIndex = Math.min(activeIndex, Math.max(editPlan.length - 1, 0));
  const activeItem = editPlan[safeActiveIndex] || emptyEditPlanItem();
  const activeAsset = assetById.get(activeItem.clip_id || "");

  function updatePlan(patch: Partial<ShotMatchingPlan>) {
    onChange(toDraft({ ...clone(plan), ...patch }));
  }

  function updateEditingStyle(key: string, value: string) {
    const next = clone(plan);
    next.editing_style = {
      ...(next.editing_style || {}),
      [key]: value
    };
    onChange(toDraft(next));
  }

  function updateScore(key: string, value: string) {
    const next = clone(plan);
    const parsed = numberOrUndefined(value);
    next.scores = {
      ...(next.scores || {}),
      [key]: parsed ?? 0
    };
    onChange(toDraft(next));
  }

  function addScore() {
    const next = clone(plan);
    next.scores = {
      ...(next.scores || {}),
      new_score: 0
    };
    onChange(toDraft(next));
  }

  function updateEditItem(index: number, patch: Partial<EditPlanItem>) {
    const next = clone(plan);
    next.edit_plan = [...(next.edit_plan || [])];
    next.edit_plan[index] = {
      ...(next.edit_plan[index] || {}),
      ...patch
    };
    onChange(toDraft(next));
  }

  function updateCaptionStyle(index: number, patch: Partial<CaptionStyle>) {
    const next = clone(plan);
    next.edit_plan = [...(next.edit_plan || [])];
    const item = { ...(next.edit_plan[index] || {}) };
    item.caption_style = {
      ...(item.caption_style || {}),
      ...patch
    };
    next.edit_plan[index] = item;
    onChange(toDraft(next));
  }

  function addEditItem() {
    const next = clone(plan);
    next.edit_plan = [...(next.edit_plan || []), emptyEditPlanItem()];
    onChange(toDraft(next));
    setActiveIndex((next.edit_plan?.length || 1) - 1);
  }

  function removeEditItem(index: number) {
    const next = clone(plan);
    next.edit_plan = [...(next.edit_plan || [])];
    next.edit_plan.splice(index, 1);
    onChange(toDraft(next));
    setActiveIndex(Math.max(0, Math.min(index, next.edit_plan.length - 1)));
  }

  function duplicateEditItem(index: number) {
    const next = clone(plan);
    next.edit_plan = [...(next.edit_plan || [])];
    const source = next.edit_plan[index] || emptyEditPlanItem();
    next.edit_plan.splice(index + 1, 0, {
      ...source,
      beat: `${source.beat || "beat"}_copy`
    });
    onChange(toDraft(next));
    setActiveIndex(index + 1);
  }

  function updateMissingAsset(index: number, patch: Partial<MissingAsset>) {
    const next = clone(plan);
    next.missing_assets = [...(next.missing_assets || [])];
    next.missing_assets[index] = {
      ...(next.missing_assets[index] || {}),
      ...patch
    };
    onChange(toDraft(next));
  }

  function addMissingAsset() {
    const next = clone(plan);
    next.missing_assets = [...(next.missing_assets || []), emptyMissingAsset()];
    onChange(toDraft(next));
  }

  function removeMissingAsset(index: number) {
    const next = clone(plan);
    next.missing_assets = [...(next.missing_assets || [])];
    next.missing_assets.splice(index, 1);
    onChange(toDraft(next));
  }

  return (
    <Card className="mt-4 rounded-none border-black/10 bg-[#f8f8f4] shadow-none">
      <CardHeader className="border-b border-black/10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">Structured Shot Matching</div>
            <CardTitle className="mt-2 text-2xl tracking-[-0.04em]">Beat decisions</CardTitle>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">{editPlan.length} beats</Badge>
            <Badge variant="outline">{assets.length} clips</Badge>
            <Badge variant="outline">{totalSeconds.toFixed(1)}s est.</Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 p-4">
        <div className="grid gap-3 xl:grid-cols-[1fr_190px]">
          <label className="grid gap-1">
            <FieldLabel>Selected script type</FieldLabel>
            <Input value={data.selected_script_type || ""} onChange={(event) => updatePlan({ selected_script_type: event.target.value })} />
          </label>
          <label className="grid gap-1">
            <FieldLabel>Needs script revision</FieldLabel>
            <select
              value={boolLabel(data.needs_script_revision)}
              onChange={(event) => updatePlan({ needs_script_revision: event.target.value === "true" })}
              className="h-9 border border-input bg-white px-3 text-sm outline-none focus:border-black"
            >
              <option value="false">false</option>
              <option value="true">true</option>
            </select>
          </label>
        </div>

        <div className="grid gap-3 lg:grid-cols-4">
          {(["pace", "average_clip_duration", "platform", "aspect_ratio"] as const).map((field) => (
            <label key={field} className="grid gap-1">
              <FieldLabel>{fieldLabel(field)}</FieldLabel>
              <Input value={String(data.editing_style?.[field] || "")} onChange={(event) => updateEditingStyle(field, event.target.value)} />
            </label>
          ))}
        </div>

        <div className="border border-black/10 bg-white p-3">
          <div className="flex items-center justify-between gap-3">
            <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-muted-foreground">Scores</div>
            <Button type="button" onClick={addScore} size="sm" variant="outline">
              Add Score
            </Button>
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {Object.entries(data.scores || {}).map(([key, value]) => (
              <label key={key} className="grid gap-1">
                <FieldLabel>{fieldLabel(key)}</FieldLabel>
                <Input type="number" value={String(value)} onChange={(event) => updateScore(key, event.target.value)} />
              </label>
            ))}
          </div>
        </div>

        <div className="grid min-h-0 gap-4 xl:grid-cols-[280px_minmax(0,1fr)]">
          <div className="min-h-0 border border-black/10 bg-white">
            <div className="flex items-center justify-between gap-3 border-b border-black/10 p-3">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-muted-foreground">Edit plan</div>
              <Button type="button" onClick={addEditItem} size="sm">
                Add Beat
              </Button>
            </div>
            <ScrollArea className="h-[610px]">
              <div className="flex flex-col">
                {editPlan.map((item, index) => (
                  <button
                    key={`${item.beat || "beat"}-${index}`}
                    type="button"
                    onClick={() => setActiveIndex(index)}
                    className={cn(
                      "border-b border-black/10 p-3 text-left transition last:border-b-0",
                      index === safeActiveIndex ? "bg-black text-white" : "bg-white hover:bg-black/[0.035]"
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className={cn("font-mono text-[10px] uppercase tracking-[0.18em]", index === safeActiveIndex ? "text-white/50" : "text-black/42")}>
                        beat {index + 1}
                      </span>
                      <span className={cn("font-mono text-[10px]", index === safeActiveIndex ? "text-white/50" : "text-black/42")}>{item.time || "no time"}</span>
                    </div>
                    <div className="mt-1 truncate text-sm font-semibold">{item.beat || "Untitled beat"}</div>
                    <div className={cn("mt-2 line-clamp-2 text-xs", index === safeActiveIndex ? "text-white/65" : "text-black/55")}>
                      {item.on_screen_text || item.voiceover || "No subtitle yet"}
                    </div>
                    <div className={cn("mt-2 truncate font-mono text-[10px]", index === safeActiveIndex ? "text-white/45" : "text-black/38")}>
                      {item.clip_id || "No clip selected"}
                    </div>
                  </button>
                ))}
              </div>
            </ScrollArea>
          </div>

          <div className="min-w-0 border border-black/10 bg-white">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-black/10 p-4">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-black/45">Beat {safeActiveIndex + 1}</div>
                <div className="mt-1 text-xl font-semibold tracking-[-0.03em]">{activeItem.beat || "Untitled beat"}</div>
              </div>
              <div className="flex gap-2">
                <Button type="button" onClick={() => duplicateEditItem(safeActiveIndex)} size="sm" variant="outline">
                  Duplicate
                </Button>
                <Button type="button" onClick={() => removeEditItem(safeActiveIndex)} size="sm" variant="outline">
                  Remove
                </Button>
              </div>
            </div>

            <div className="grid gap-4 p-4">
              <div className="grid gap-3 lg:grid-cols-[0.8fr_1fr_0.8fr]">
                {(["time", "beat", "transition"] as const).map((field) => (
                  <label key={field} className="grid gap-1">
                    <FieldLabel>{fieldLabel(field)}</FieldLabel>
                    <Input value={String(activeItem[field] || "")} onChange={(event) => updateEditItem(safeActiveIndex, { [field]: event.target.value })} />
                  </label>
                ))}
              </div>

              <div className="grid gap-3 border border-black/10 bg-[#f8f8f4] p-3 lg:grid-cols-[132px_minmax(0,1fr)]">
                <div className="overflow-hidden border border-black/10 bg-black">
                  {activeAsset?.thumbnailPath ? (
                    <img src={mediaUrl(activeAsset.thumbnailPath)} alt={activeItem.clip_id || "selected clip"} className="aspect-[9/16] w-full object-cover" />
                  ) : (
                    <div className="flex aspect-[9/16] items-center justify-center px-2 text-center font-mono text-[10px] uppercase tracking-[0.16em] text-white/45">
                      no selected thumbnail
                    </div>
                  )}
                </div>
                <div className="min-w-0">
                  <div className="grid gap-3 lg:grid-cols-2">
                    <label className="grid gap-1">
                      <FieldLabel>Asset picker</FieldLabel>
                      <select
                        value={activeItem.clip_id || ""}
                        onChange={(event) => updateEditItem(safeActiveIndex, { clip_id: event.target.value })}
                        className="h-9 min-w-0 border border-input bg-white px-3 text-sm outline-none focus:border-black"
                      >
                        <option value="">Choose indexed clip</option>
                        {assets.map((asset) => (
                          <option key={asset.clipId} value={asset.clipId}>
                            {asset.clipId} / {asset.shotType} / {asset.scene}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="grid gap-1">
                      <FieldLabel>Clip id</FieldLabel>
                      <Input value={activeItem.clip_id || ""} onChange={(event) => updateEditItem(safeActiveIndex, { clip_id: event.target.value })} />
                    </label>
                  </div>
                  {activeAsset ? (
                    <div className="mt-3 grid gap-2 text-xs text-black/62 lg:grid-cols-2">
                      <div>
                        <span className="font-mono uppercase tracking-[0.16em] text-muted-foreground">duration</span> {formatDuration(activeAsset.duration)}
                      </div>
                      <div>
                        <span className="font-mono uppercase tracking-[0.16em] text-muted-foreground">orientation</span> {activeAsset.orientation}
                      </div>
                      <div>
                        <span className="font-mono uppercase tracking-[0.16em] text-muted-foreground">best use</span>{" "}
                        {activeAsset.bestUse.join(", ") || "unlabeled"}
                      </div>
                      <div>
                        <span className="font-mono uppercase tracking-[0.16em] text-muted-foreground">safe area</span> {activeAsset.textOverlaySafeArea}
                      </div>
                      <div className="lg:col-span-2">
                        <span className="font-mono uppercase tracking-[0.16em] text-muted-foreground">notes</span> {activeAsset.notes || "No notes"}
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>

              <div className="grid gap-3 lg:grid-cols-4">
                {(["clip_start", "clip_end", "playback_speed"] as const).map((field) => (
                  <label key={field} className="grid gap-1">
                    <FieldLabel>{fieldLabel(field)}</FieldLabel>
                    <Input
                      type="number"
                      step="0.05"
                      value={activeItem[field] === undefined ? "" : String(activeItem[field])}
                      onChange={(event) => updateEditItem(safeActiveIndex, { [field]: numberOrUndefined(event.target.value) })}
                    />
                  </label>
                ))}
                <label className="grid gap-1">
                  <FieldLabel>Subtitle priority</FieldLabel>
                  <select
                    value={activeItem.subtitle_priority || "normal"}
                    onChange={(event) => updateEditItem(safeActiveIndex, { subtitle_priority: event.target.value })}
                    className="h-9 border border-input bg-white px-3 text-sm outline-none focus:border-black"
                  >
                    <option value="normal">normal</option>
                    <option value="large">large</option>
                    <option value="small">small</option>
                  </select>
                </label>
              </div>

              <div className="grid gap-3 lg:grid-cols-2">
                {(["voiceover", "on_screen_text", "reason", "speed_reason"] as const).map((field) => (
                  <label key={field} className="grid gap-1">
                    <FieldLabel>{fieldLabel(field)}</FieldLabel>
                    <Textarea
                      value={String(activeItem[field] || "")}
                      onChange={(event) => updateEditItem(safeActiveIndex, { [field]: event.target.value })}
                      rows={2}
                    />
                  </label>
                ))}
              </div>

              <div className="border border-black/10 bg-[#f8f8f4] p-3">
                <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-muted-foreground">Caption style</div>
                <div className="mt-3 grid gap-3 lg:grid-cols-2">
                  <label className="grid gap-1">
                    <FieldLabel>Lines</FieldLabel>
                    <Textarea
                      value={linesToText(activeItem.caption_style?.lines)}
                      onChange={(event) => updateCaptionStyle(safeActiveIndex, { lines: textToLines(event.target.value) })}
                      rows={3}
                      placeholder="one subtitle line per row"
                    />
                  </label>
                  <label className="grid gap-1">
                    <FieldLabel>Highlight terms</FieldLabel>
                    <Textarea
                      value={listToText(activeItem.caption_style?.highlight_terms)}
                      onChange={(event) => updateCaptionStyle(safeActiveIndex, { highlight_terms: textToList(event.target.value) })}
                      rows={3}
                    />
                  </label>
                </div>
                <div className="mt-3 grid gap-3 lg:grid-cols-4">
                  {(["font_size", "line_gap", "y_ratio", "max_width"] as const).map((field) => (
                    <label key={field} className="grid gap-1">
                      <FieldLabel>{fieldLabel(field)}</FieldLabel>
                      <Input
                        type="number"
                        step={field === "y_ratio" ? "0.01" : "1"}
                        value={activeItem.caption_style?.[field] === undefined ? "" : String(activeItem.caption_style?.[field])}
                        onChange={(event) => updateCaptionStyle(safeActiveIndex, { [field]: numberOrUndefined(event.target.value) })}
                      />
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="border border-black/10 bg-white p-4">
            <div className="flex items-center justify-between gap-3">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-muted-foreground">Missing assets</div>
              <Button type="button" onClick={addMissingAsset} size="sm" variant="outline">
                Add
              </Button>
            </div>
            <div className="mt-3 space-y-3">
              {(data.missing_assets || []).map((asset, index) => (
                <div key={index} className="border border-black/10 bg-[#f8f8f4] p-3">
                  <div className="flex justify-end">
                    <Button type="button" onClick={() => removeMissingAsset(index)} size="sm" variant="outline">
                      Remove
                    </Button>
                  </div>
                  <label className="mt-2 grid gap-1">
                    <FieldLabel>Need</FieldLabel>
                    <Textarea value={asset.need || ""} onChange={(event) => updateMissingAsset(index, { need: event.target.value })} rows={2} />
                  </label>
                  <label className="mt-2 grid gap-1">
                    <FieldLabel>Suggestion</FieldLabel>
                    <Textarea value={asset.suggestion || ""} onChange={(event) => updateMissingAsset(index, { suggestion: event.target.value })} rows={2} />
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="border border-black/10 bg-white p-4">
            <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-muted-foreground">Risk notes and revision</div>
            <label className="mt-3 grid gap-1">
              <FieldLabel>Risk notes</FieldLabel>
              <Textarea value={(data.risk_notes || []).join("\n")} onChange={(event) => updatePlan({ risk_notes: textToLines(event.target.value) })} rows={5} />
            </label>
            <label className="mt-3 grid gap-1">
              <FieldLabel>Revision reason</FieldLabel>
              <Textarea value={data.reason || ""} onChange={(event) => updatePlan({ reason: event.target.value })} rows={2} />
            </label>
            <label className="mt-3 grid gap-1">
              <FieldLabel>Suggested revision</FieldLabel>
              <Textarea value={data.suggested_revision || ""} onChange={(event) => updatePlan({ suggested_revision: event.target.value })} rows={2} />
            </label>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
