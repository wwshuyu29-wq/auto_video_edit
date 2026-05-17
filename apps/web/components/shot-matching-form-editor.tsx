"use client";

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
    subtitle_priority: "normal"
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

export function ShotMatchingFormEditor({ draft, onChange, assetLibrary }: Props) {
  const data = parseDraft(draft);
  if (!data || !Array.isArray(data.edit_plan)) {
    return (
      <div className="mt-4 border border-[#d9c58f] bg-[#fffaf0] px-4 py-3 text-sm text-[#735b16]">
        Shot matching form is available after this plan contains a valid `edit_plan` array.
      </div>
    );
  }
  const assets = assetLibrary?.assets || [];
  const assetById = new Map(assets.map((asset) => [asset.clipId, asset]));

  function updatePlan(patch: Partial<ShotMatchingPlan>) {
    const next = {
      ...clone(data!),
      ...patch
    };
    onChange(toDraft(next));
  }

  function updateEditingStyle(key: string, value: string) {
    const next = clone(data!);
    next.editing_style = {
      ...(next.editing_style || {}),
      [key]: value
    };
    onChange(toDraft(next));
  }

  function updateScore(key: string, value: string) {
    const next = clone(data!);
    const parsed = numberOrUndefined(value);
    next.scores = {
      ...(next.scores || {}),
      [key]: parsed ?? 0
    };
    onChange(toDraft(next));
  }

  function addScore() {
    const next = clone(data!);
    next.scores = {
      ...(next.scores || {}),
      new_score: 0
    };
    onChange(toDraft(next));
  }

  function updateEditItem(index: number, patch: Partial<EditPlanItem>) {
    const next = clone(data!);
    next.edit_plan = [...(next.edit_plan || [])];
    next.edit_plan[index] = {
      ...(next.edit_plan[index] || {}),
      ...patch
    };
    onChange(toDraft(next));
  }

  function updateCaptionStyle(index: number, patch: Partial<CaptionStyle>) {
    const next = clone(data!);
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
    const next = clone(data!);
    next.edit_plan = [...(next.edit_plan || []), emptyEditPlanItem()];
    onChange(toDraft(next));
  }

  function removeEditItem(index: number) {
    const next = clone(data!);
    next.edit_plan = [...(next.edit_plan || [])];
    next.edit_plan.splice(index, 1);
    onChange(toDraft(next));
  }

  function duplicateEditItem(index: number) {
    const next = clone(data!);
    next.edit_plan = [...(next.edit_plan || [])];
    const source = next.edit_plan[index] || emptyEditPlanItem();
    next.edit_plan.splice(index + 1, 0, {
      ...source,
      beat: `${source.beat || "beat"}_copy`
    });
    onChange(toDraft(next));
  }

  function updateMissingAsset(index: number, patch: Partial<MissingAsset>) {
    const next = clone(data!);
    next.missing_assets = [...(next.missing_assets || [])];
    next.missing_assets[index] = {
      ...(next.missing_assets[index] || {}),
      ...patch
    };
    onChange(toDraft(next));
  }

  function addMissingAsset() {
    const next = clone(data!);
    next.missing_assets = [...(next.missing_assets || []), emptyMissingAsset()];
    onChange(toDraft(next));
  }

  function removeMissingAsset(index: number) {
    const next = clone(data!);
    next.missing_assets = [...(next.missing_assets || [])];
    next.missing_assets.splice(index, 1);
    onChange(toDraft(next));
  }

  return (
    <div className="mt-4 border border-black/10 bg-[#f8f8f4] p-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Structured Shot Matching Editor</div>
          <div className="mt-1 text-lg font-semibold tracking-[-0.03em]">Clip decisions, timing, captions, and risks</div>
        </div>
        <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-black/42">
          {data.edit_plan.length} beats / {assets.length} indexed clips
        </div>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <label className="grid gap-1">
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">selected script type</span>
          <input
            value={data.selected_script_type || ""}
            onChange={(event) => updatePlan({ selected_script_type: event.target.value })}
            className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
          />
        </label>
        <label className="grid gap-1">
          <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">needs script revision</span>
          <select
            value={boolLabel(data.needs_script_revision)}
            onChange={(event) => updatePlan({ needs_script_revision: event.target.value === "true" })}
            className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
          >
            <option value="false">false</option>
            <option value="true">true</option>
          </select>
        </label>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-4">
        {(["pace", "average_clip_duration", "platform", "aspect_ratio"] as const).map((field) => (
          <label key={field} className="grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">{fieldLabel(field)}</span>
            <input
              value={String(data.editing_style?.[field] || "")}
              onChange={(event) => updateEditingStyle(field, event.target.value)}
              className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
        ))}
      </div>

      <div className="mt-4 border border-black/10 bg-white p-3">
        <div className="flex items-center justify-between gap-3">
          <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Scores</div>
          <button type="button" onClick={addScore} className="rounded-md border border-black/20 bg-white px-3 py-1.5 text-xs font-medium">
            Add Score
          </button>
        </div>
        <div className="mt-3 grid gap-3 lg:grid-cols-5">
          {Object.entries(data.scores || {}).map(([key, value]) => (
            <label key={key} className="grid gap-1">
              <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-steel">{fieldLabel(key)}</span>
              <input
                type="number"
                value={String(value)}
                onChange={(event) => updateScore(key, event.target.value)}
                className="border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
              />
            </label>
          ))}
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between">
        <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Edit plan</div>
        <button type="button" onClick={addEditItem} className="rounded-md border border-black bg-black px-3 py-2 text-xs font-medium text-white">
          Add Beat
        </button>
      </div>

      <div className="mt-3 space-y-4">
        {data.edit_plan.map((item, index) => (
          <div key={`${item.beat || "beat"}-${index}`} className="border border-black/10 bg-white p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-black/45">beat {index + 1}</div>
                <div className="mt-1 text-lg font-semibold tracking-[-0.03em]">{item.beat || "Untitled beat"}</div>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => duplicateEditItem(index)}
                  className="rounded-md border border-black/20 bg-white px-3 py-1.5 text-xs font-medium"
                >
                  Duplicate
                </button>
                <button
                  type="button"
                  onClick={() => removeEditItem(index)}
                  className="rounded-md border border-black/20 bg-white px-3 py-1.5 text-xs font-medium"
                >
                  Remove
                </button>
              </div>
            </div>

            <div className="mt-4 grid gap-3 lg:grid-cols-[0.8fr_1fr_0.8fr]">
              {(["time", "beat", "transition"] as const).map((field) => (
                <label key={field} className="grid gap-1">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">{fieldLabel(field)}</span>
                  <input
                    value={String(item[field] || "")}
                    onChange={(event) => updateEditItem(index, { [field]: event.target.value })}
                    className="border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
                  />
                </label>
              ))}
            </div>

            <div className="mt-3 grid gap-3 border border-black/10 bg-[#f8f8f4] p-3 lg:grid-cols-[118px_1fr]">
              <div className="overflow-hidden border border-black/10 bg-black">
                {assetById.get(item.clip_id || "")?.thumbnailPath ? (
                  <img
                    src={mediaUrl(assetById.get(item.clip_id || "")?.thumbnailPath)}
                    alt={item.clip_id || "selected clip"}
                    className="aspect-[9/16] w-full object-cover"
                  />
                ) : (
                  <div className="flex aspect-[9/16] items-center justify-center px-2 text-center font-mono text-[10px] uppercase tracking-[0.16em] text-white/45">
                    no selected thumbnail
                  </div>
                )}
              </div>
              <div className="min-w-0">
                <div className="grid gap-3 lg:grid-cols-2">
                  <label className="grid gap-1">
                    <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">asset picker</span>
                    <select
                      value={item.clip_id || ""}
                      onChange={(event) => updateEditItem(index, { clip_id: event.target.value })}
                      className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
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
                    <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">clip id</span>
                    <input
                      value={item.clip_id || ""}
                      onChange={(event) => updateEditItem(index, { clip_id: event.target.value })}
                      className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
                    />
                  </label>
                </div>
                {assetById.get(item.clip_id || "") ? (
                  <div className="mt-3 grid gap-2 text-xs text-black/62 lg:grid-cols-2">
                    <div>
                      <span className="font-mono uppercase tracking-[0.16em] text-steel">duration</span>{" "}
                      {formatDuration(assetById.get(item.clip_id || "")?.duration ?? null)}
                    </div>
                    <div>
                      <span className="font-mono uppercase tracking-[0.16em] text-steel">orientation</span>{" "}
                      {assetById.get(item.clip_id || "")?.orientation}
                    </div>
                    <div>
                      <span className="font-mono uppercase tracking-[0.16em] text-steel">best use</span>{" "}
                      {(assetById.get(item.clip_id || "")?.bestUse || []).join(", ") || "unlabeled"}
                    </div>
                    <div>
                      <span className="font-mono uppercase tracking-[0.16em] text-steel">safe area</span>{" "}
                      {assetById.get(item.clip_id || "")?.textOverlaySafeArea}
                    </div>
                    <div className="lg:col-span-2">
                      <span className="font-mono uppercase tracking-[0.16em] text-steel">notes</span>{" "}
                      {assetById.get(item.clip_id || "")?.notes || "No notes"}
                    </div>
                  </div>
                ) : null}
              </div>
            </div>

            <div className="mt-3 grid gap-3 lg:grid-cols-4">
              {(["clip_start", "clip_end", "playback_speed"] as const).map((field) => (
                <label key={field} className="grid gap-1">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">{fieldLabel(field)}</span>
                  <input
                    type="number"
                    step="0.05"
                    value={item[field] === undefined ? "" : String(item[field])}
                    onChange={(event) => updateEditItem(index, { [field]: numberOrUndefined(event.target.value) })}
                    className="border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
                  />
                </label>
              ))}
              <label className="grid gap-1">
                <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">subtitle priority</span>
                <select
                  value={item.subtitle_priority || "normal"}
                  onChange={(event) => updateEditItem(index, { subtitle_priority: event.target.value })}
                  className="border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
                >
                  <option value="normal">normal</option>
                  <option value="large">large</option>
                  <option value="small">small</option>
                </select>
              </label>
            </div>

            <div className="mt-3 grid gap-3 lg:grid-cols-2">
              {(["voiceover", "on_screen_text", "reason", "speed_reason"] as const).map((field) => (
                <label key={field} className="grid gap-1">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">{fieldLabel(field)}</span>
                  <textarea
                    value={String(item[field] || "")}
                    onChange={(event) => updateEditItem(index, { [field]: event.target.value })}
                    rows={2}
                    className="resize-none border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
                  />
                </label>
              ))}
            </div>

            <div className="mt-4 border border-black/10 bg-[#f8f8f4] p-3">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Caption style</div>
              <div className="mt-3 grid gap-3 lg:grid-cols-2">
                <label className="grid gap-1">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">lines</span>
                  <textarea
                    value={(item.caption_style?.lines || []).join("\n")}
                    onChange={(event) => updateCaptionStyle(index, { lines: event.target.value.split(/\r?\n/).filter(Boolean) })}
                    rows={3}
                    placeholder="one subtitle line per row"
                    className="resize-none border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
                  />
                </label>
                <label className="grid gap-1">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">highlight terms</span>
                  <textarea
                    value={listToText(item.caption_style?.highlight_terms)}
                    onChange={(event) => updateCaptionStyle(index, { highlight_terms: textToList(event.target.value) })}
                    rows={3}
                    className="resize-none border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
                  />
                </label>
              </div>
              <div className="mt-3 grid gap-3 lg:grid-cols-4">
                {(["font_size", "line_gap", "y_ratio", "max_width"] as const).map((field) => (
                  <label key={field} className="grid gap-1">
                    <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">{fieldLabel(field)}</span>
                    <input
                      type="number"
                      step={field === "y_ratio" ? "0.01" : "1"}
                      value={item.caption_style?.[field] === undefined ? "" : String(item.caption_style?.[field])}
                      onChange={(event) => updateCaptionStyle(index, { [field]: numberOrUndefined(event.target.value) })}
                      className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
                    />
                  </label>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <div className="border border-black/10 bg-white p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Missing assets</div>
            <button
              type="button"
              onClick={addMissingAsset}
              className="rounded-md border border-black/20 bg-white px-3 py-1.5 text-xs font-medium"
            >
              Add
            </button>
          </div>
          <div className="mt-3 space-y-3">
            {(data.missing_assets || []).map((asset, index) => (
              <div key={index} className="border border-black/10 bg-[#f8f8f4] p-3">
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={() => removeMissingAsset(index)}
                    className="rounded-md border border-black/20 bg-white px-3 py-1.5 text-xs font-medium"
                  >
                    Remove
                  </button>
                </div>
                <label className="mt-2 grid gap-1">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">need</span>
                  <textarea
                    value={asset.need || ""}
                    onChange={(event) => updateMissingAsset(index, { need: event.target.value })}
                    rows={2}
                    className="resize-none border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
                  />
                </label>
                <label className="mt-2 grid gap-1">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">suggestion</span>
                  <textarea
                    value={asset.suggestion || ""}
                    onChange={(event) => updateMissingAsset(index, { suggestion: event.target.value })}
                    rows={2}
                    className="resize-none border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
                  />
                </label>
              </div>
            ))}
          </div>
        </div>

        <div className="border border-black/10 bg-white p-4">
          <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Risk notes and revision</div>
          <label className="mt-3 grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">risk notes</span>
            <textarea
              value={(data.risk_notes || []).join("\n")}
              onChange={(event) => updatePlan({ risk_notes: event.target.value.split(/\r?\n/).filter(Boolean) })}
              rows={5}
              className="resize-none border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
          <label className="mt-3 grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">revision reason</span>
            <textarea
              value={data.reason || ""}
              onChange={(event) => updatePlan({ reason: event.target.value })}
              rows={2}
              className="resize-none border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
          <label className="mt-3 grid gap-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">suggested revision</span>
            <textarea
              value={data.suggested_revision || ""}
              onChange={(event) => updatePlan({ suggested_revision: event.target.value })}
              rows={2}
              className="resize-none border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
            />
          </label>
        </div>
      </div>
    </div>
  );
}
