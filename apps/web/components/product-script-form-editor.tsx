"use client";

type ScriptBeat = {
  time?: string;
  beat?: string;
  voiceover?: string;
  on_screen_text?: string;
  visual_need?: string;
  preferred_clip_id?: string;
  product_feature?: string;
};

type ScriptVariant = {
  type?: string;
  style?: string;
  script_title?: string;
  script_angle?: string;
  target_viewer?: string;
  version?: string;
  full_script?: ScriptBeat[];
  caption?: string;
  hashtags?: string[];
  compliance_notes?: string[];
};

type ProductScriptCard = {
  scripts?: ScriptVariant[];
  [key: string]: unknown;
};

type Props = {
  draft: string;
  onChange: (value: string) => void;
};

function parseDraft(draft: string): ProductScriptCard | null {
  try {
    const parsed = JSON.parse(draft);
    if (!parsed || typeof parsed !== "object" || !Array.isArray(parsed.scripts)) return null;
    return parsed as ProductScriptCard;
  } catch {
    return null;
  }
}

function toDraft(data: ProductScriptCard) {
  return JSON.stringify(data, null, 2);
}

function clone(data: ProductScriptCard): ProductScriptCard {
  return JSON.parse(JSON.stringify(data)) as ProductScriptCard;
}

function listToText(items?: string[]) {
  return Array.isArray(items) ? items.join(", ") : "";
}

function textToList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function emptyBeat(): ScriptBeat {
  return {
    time: "",
    beat: "",
    voiceover: "",
    on_screen_text: "",
    visual_need: "",
    preferred_clip_id: "",
    product_feature: ""
  };
}

function fieldLabel(value: string) {
  return value.replaceAll("_", " ");
}

export function ProductScriptFormEditor({ draft, onChange }: Props) {
  const data = parseDraft(draft);
  if (!data || !Array.isArray(data.scripts)) {
    return (
      <div className="mt-4 border border-[#d9c58f] bg-[#fffaf0] px-4 py-3 text-sm text-[#735b16]">
        Product script form is available after this card contains a valid `scripts` array.
      </div>
    );
  }

  function updateVariant(index: number, patch: Partial<ScriptVariant>) {
    const next = clone(data!);
    next.scripts = [...(next.scripts || [])];
    next.scripts[index] = {
      ...(next.scripts[index] || {}),
      ...patch
    };
    onChange(toDraft(next));
  }

  function updateBeat(scriptIndex: number, beatIndex: number, patch: Partial<ScriptBeat>) {
    const next = clone(data!);
    next.scripts = [...(next.scripts || [])];
    const script = { ...(next.scripts[scriptIndex] || {}) };
    script.full_script = [...(script.full_script || [])];
    script.full_script[beatIndex] = {
      ...(script.full_script[beatIndex] || {}),
      ...patch
    };
    next.scripts[scriptIndex] = script;
    onChange(toDraft(next));
  }

  function addBeat(scriptIndex: number) {
    const next = clone(data!);
    next.scripts = [...(next.scripts || [])];
    const script = { ...(next.scripts[scriptIndex] || {}) };
    script.full_script = [...(script.full_script || []), emptyBeat()];
    next.scripts[scriptIndex] = script;
    onChange(toDraft(next));
  }

  function removeBeat(scriptIndex: number, beatIndex: number) {
    const next = clone(data!);
    next.scripts = [...(next.scripts || [])];
    const script = { ...(next.scripts[scriptIndex] || {}) };
    script.full_script = [...(script.full_script || [])];
    script.full_script.splice(beatIndex, 1);
    next.scripts[scriptIndex] = script;
    onChange(toDraft(next));
  }

  function duplicateVariant(index: number) {
    const next = clone(data!);
    const source = next.scripts?.[index] || {};
    next.scripts = [...(next.scripts || [])];
    next.scripts.splice(index + 1, 0, {
      ...source,
      type: `${source.type || "script"}_copy`,
      script_title: `${source.script_title || "Untitled"} copy`
    });
    onChange(toDraft(next));
  }

  return (
    <div className="mt-4 border border-black/10 bg-[#f8f8f4] p-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Structured Script Editor</div>
          <div className="mt-1 text-lg font-semibold tracking-[-0.03em]">Script variants and subtitle beats</div>
        </div>
        <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-black/42">
          {data.scripts.length} variants
        </div>
      </div>

      <div className="mt-4 space-y-5">
        {data.scripts.map((script, scriptIndex) => (
          <div key={`${script.type || "script"}-${scriptIndex}`} className="border border-black/10 bg-white p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.22em] text-steel">
                  {script.type || `script_${scriptIndex + 1}`}
                </div>
                <div className="mt-1 text-lg font-semibold tracking-[-0.03em]">
                  {script.script_title || "Untitled script"}
                </div>
              </div>
              <button
                type="button"
                onClick={() => duplicateVariant(scriptIndex)}
                className="rounded-md border border-black/20 bg-white px-3 py-2 text-xs font-medium text-black"
              >
                Duplicate Variant
              </button>
            </div>

            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              {(["type", "script_title", "script_angle", "target_viewer", "version", "style"] as const).map((field) => (
                <label key={field} className="grid gap-1">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">{fieldLabel(field)}</span>
                  <input
                    value={String(script[field] || "")}
                    onChange={(event) => updateVariant(scriptIndex, { [field]: event.target.value })}
                    className="border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
                  />
                </label>
              ))}
            </div>

            <div className="mt-3 grid gap-3 lg:grid-cols-2">
              <label className="grid gap-1">
                <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">caption</span>
                <textarea
                  value={script.caption || ""}
                  onChange={(event) => updateVariant(scriptIndex, { caption: event.target.value })}
                  rows={2}
                  className="resize-none border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
                />
              </label>
              <label className="grid gap-1">
                <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">hashtags</span>
                <textarea
                  value={listToText(script.hashtags)}
                  onChange={(event) => updateVariant(scriptIndex, { hashtags: textToList(event.target.value) })}
                  rows={2}
                  placeholder="#researchtools, #aitools"
                  className="resize-none border border-black/10 bg-[#f8f8f4] px-3 py-2 text-sm outline-none focus:border-black"
                />
              </label>
            </div>

            <div className="mt-5 flex items-center justify-between">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Subtitle beats</div>
              <button
                type="button"
                onClick={() => addBeat(scriptIndex)}
                className="rounded-md border border-black bg-black px-3 py-2 text-xs font-medium text-white"
              >
                Add Beat
              </button>
            </div>

            <div className="mt-3 space-y-3">
              {(script.full_script || []).map((beat, beatIndex) => (
                <div key={`${scriptIndex}-${beatIndex}`} className="border border-black/10 bg-[#f8f8f4] p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-black/45">
                      beat {beatIndex + 1}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeBeat(scriptIndex, beatIndex)}
                      className="rounded-md border border-black/20 bg-white px-3 py-1.5 text-xs font-medium text-black"
                    >
                      Remove
                    </button>
                  </div>

                  <div className="mt-3 grid gap-3 lg:grid-cols-[0.7fr_0.9fr_1.4fr]">
                    {(["time", "beat", "product_feature"] as const).map((field) => (
                      <label key={field} className="grid gap-1">
                        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">{fieldLabel(field)}</span>
                        <input
                          value={String(beat[field] || "")}
                          onChange={(event) => updateBeat(scriptIndex, beatIndex, { [field]: event.target.value })}
                          className="border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
                        />
                      </label>
                    ))}
                  </div>

                  <div className="mt-3 grid gap-3 lg:grid-cols-2">
                    {(["voiceover", "on_screen_text", "visual_need", "preferred_clip_id"] as const).map((field) => (
                      <label key={field} className="grid gap-1">
                        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-steel">{fieldLabel(field)}</span>
                        <textarea
                          value={String(beat[field] || "")}
                          onChange={(event) => updateBeat(scriptIndex, beatIndex, { [field]: event.target.value })}
                          rows={field === "preferred_clip_id" ? 1 : 2}
                          className="resize-none border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black"
                        />
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
