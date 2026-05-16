const products = [
  {
    name: "Literfy",
    angle: "AI literature review workflow",
    note: "Best for paper search, structure, draft flow, and review-start pain."
  },
  {
    name: "Citely",
    angle: "Citation verification and source tracing",
    note: "Best for fake-reference fear, source lookup, and proof-driven hooks."
  },
  {
    name: "FigPad",
    angle: "Scientific figure generation",
    note: "Best for sketch-to-figure, figure cleanup, and experiment visuals."
  }
];

const steps = [
  "Choose product",
  "Add TikTok reference URL or upload reference video",
  "Upload raw footage, landing page, and screen recordings",
  "Select template and video length",
  "Generate project work order"
];

export default function NewProjectPage() {
  return (
    <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
      <section className="space-y-6">
        <div className="border border-black/10 bg-panel p-6 shadow-panel lg:p-8">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">New Project</div>
          <h2 className="mt-4 text-4xl font-semibold tracking-[-0.05em] lg:text-5xl">Build one work order, not one-off chaos.</h2>
          <p className="mt-4 max-w-2xl text-sm leading-6 text-black/66">
            This form is designed to create a single standard project job. The worker uses that file to decide what to
            analyze, what to reuse, what to render, and where outputs should land.
          </p>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Product</div>
          <div className="mt-5 grid gap-3">
            {products.map((product, index) => (
              <div
                key={product.name}
                className={`border p-4 ${index === 0 ? "border-black bg-black text-white" : "border-black/10 bg-[#f8f8f4]"}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-lg font-semibold">{product.name}</div>
                    <div className={`mt-2 text-sm ${index === 0 ? "text-white/72" : "text-black/64"}`}>{product.angle}</div>
                  </div>
                  <div className={`font-mono text-[11px] uppercase tracking-[0.24em] ${index === 0 ? "text-white/45" : "text-steel"}`}>
                    {index === 0 ? "Selected" : "Available"}
                  </div>
                </div>
                <div className={`mt-3 text-sm leading-6 ${index === 0 ? "text-white/78" : "text-black/68"}`}>{product.note}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Inputs</div>
          <div className="mt-5 grid gap-4">
            <div className="border border-black/10 bg-[#f8f8f4] p-4">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Reference TikTok</div>
              <div className="mt-3 rounded-md border border-black/10 bg-white px-4 py-3 text-sm text-black/42">
                https://www.tiktok.com/@reference-account/video/...
              </div>
            </div>
            <div className="grid gap-4 lg:grid-cols-2">
              <div className="border border-dashed border-black/20 bg-[#f8f8f4] p-5">
                <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Raw Footage</div>
                <div className="mt-8 text-sm text-black/62">Drop handheld clips, landing page recordings, and workflow screen captures.</div>
              </div>
              <div className="border border-dashed border-black/20 bg-[#f8f8f4] p-5">
                <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Template Settings</div>
                <div className="mt-8 text-sm text-black/62">Google Scholar trust template, 25s preview render, A/B/C variant toggle.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <div className="border border-black/10 bg-[#161616] p-6 text-white shadow-panel lg:p-8">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-white/45">Worker Contract</div>
          <div className="mt-4 space-y-3">
            {steps.map((step, index) => (
              <div key={step} className="flex items-center justify-between border-b border-white/10 pb-3 text-sm last:border-b-0 last:pb-0">
                <span>
                  {index + 1}. {step}
                </span>
                <span className="font-mono text-[11px] uppercase tracking-[0.24em] text-white/45">Queued</span>
              </div>
            ))}
          </div>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Generated Work Order</div>
          <div className="mt-4 rounded-md border border-black/10 bg-[#121212] p-4 font-mono text-[12px] leading-6 text-white/78">
            <div>{`{`}</div>
            <div className="pl-4">{`"product_name": "Literfy",`}</div>
            <div className="pl-4">{`"workflow_mode": "fresh",`}</div>
            <div className="pl-4">{`"stages": ["viral_deconstruction", "product_script_rewrite", "asset_matching", "video_rendering"]`}</div>
            <div>{`}`}</div>
          </div>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Primary Action</div>
          <button className="mt-4 w-full rounded-md border border-black bg-black px-4 py-3 text-sm font-medium text-white">
            Generate Project Job
          </button>
          <p className="mt-3 text-sm leading-6 text-black/62">
            First version creates the work order and passes it to the worker. Cloud storage and database wiring come next.
          </p>
        </div>
      </section>
    </div>
  );
}
