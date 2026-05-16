"use client";

import { useMemo, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

type ProductOption = {
  product_name: string;
  one_liner: string;
  good_tiktok_angles?: string[];
};

type NewProjectFormProps = {
  activeProduct: string;
  products: ProductOption[];
};

type FormState = {
  projectName: string;
  productName: string;
  referenceAccountUrl: string;
  referenceVideoUrl: string;
  materialDirectory: string;
  templateName: string;
  videoLength: string;
  tone: string;
  notes: string;
};

const steps = [
  "Choose product",
  "Add TikTok reference URL or reference account",
  "Point to your local raw footage folder",
  "Select template and video length",
  "Generate project work order"
];

const defaultState = (activeProduct: string): FormState => ({
  projectName: "",
  productName: activeProduct,
  referenceAccountUrl: "",
  referenceVideoUrl: "",
  materialDirectory: "",
  templateName: "Google Scholar trust template",
  videoLength: "25-35s",
  tone: "native creator style, casual, not too salesy",
  notes: ""
});

function inputClassName() {
  return "mt-3 w-full rounded-md border border-black/10 bg-white px-4 py-3 text-sm text-black outline-none transition placeholder:text-black/32 focus:border-black";
}

export function NewProjectForm({ activeProduct, products }: NewProjectFormProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState("");
  const [createdProject, setCreatedProject] = useState<null | { slug: string; projectDir: string }>(null);
  const [form, setForm] = useState<FormState>(() => defaultState(activeProduct));

  const selectedProduct = useMemo(
    () => products.find((product) => product.product_name === form.productName) || products[0],
    [form.productName, products]
  );

  const workOrderPreview = useMemo(
    () => ({
      product_name: form.productName || activeProduct,
      workflow_mode: "fresh",
      template_name: form.templateName,
      stages: ["viral_deconstruction", "product_script_rewrite", "asset_matching", "video_rendering"],
      reference: form.referenceVideoUrl || form.referenceAccountUrl || "pending",
      material_directory: form.materialDirectory || "pending"
    }),
    [activeProduct, form]
  );

  function updateField<Key extends keyof FormState>(key: Key, value: FormState[Key]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setCreatedProject(null);

    startTransition(async () => {
      try {
        const response = await fetch("/api/projects", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form)
        });

        const data = (await response.json()) as { error?: string; slug?: string; projectDir?: string };
        if (!response.ok) {
          throw new Error(data.error || "Failed to create project job.");
        }

        setCreatedProject({ slug: data.slug!, projectDir: data.projectDir! });
        router.push(`/projects/${data.slug}`);
        router.refresh();
      } catch (submitError) {
        setError(submitError instanceof Error ? submitError.message : "Failed to create project job.");
      }
    });
  }

  return (
    <form onSubmit={onSubmit} className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
      <section className="space-y-6">
        <div className="border border-black/10 bg-panel p-6 shadow-panel lg:p-8">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">New Project</div>
          <h2 className="mt-4 text-4xl font-semibold tracking-[-0.05em] lg:text-5xl">Build one work order, not one-off chaos.</h2>
          <p className="mt-4 max-w-2xl text-sm leading-6 text-black/66">
            Fill this intake once. The page will create a new project folder, write the worker work order, and prepare
            the standard files the backend expects.
          </p>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Project Setup</div>
          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            <label className="block">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Project name</div>
              <input
                value={form.projectName}
                onChange={(event) => updateField("projectName", event.target.value)}
                className={inputClassName()}
                placeholder="citely-google-scholar-template-v2"
                required
              />
            </label>
            <label className="block">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Product</div>
              <select
                value={form.productName}
                onChange={(event) => updateField("productName", event.target.value)}
                className={inputClassName()}
              >
                {products.map((product) => (
                  <option key={product.product_name} value={product.product_name}>
                    {product.product_name}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Product</div>
          <div className="mt-5 space-y-3">
            {products.map((product) => {
              const selected = product.product_name === form.productName;
              return (
                <button
                  key={product.product_name}
                  type="button"
                  onClick={() => updateField("productName", product.product_name)}
                  className={`w-full border p-4 text-left transition ${
                    selected ? "border-black bg-black text-white" : "border-black/10 bg-[#f8f8f4] hover:border-black/25"
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="text-lg font-semibold">{product.product_name}</div>
                      <div className={`mt-2 text-sm ${selected ? "text-white/72" : "text-black/64"}`}>{product.one_liner}</div>
                    </div>
                    <div className={`font-mono text-[11px] uppercase tracking-[0.24em] ${selected ? "text-white/45" : "text-steel"}`}>
                      {selected ? "Selected" : "Available"}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Inputs</div>
          <div className="mt-5 grid gap-4">
            <label className="block border border-black/10 bg-[#f8f8f4] p-4">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Reference account URL</div>
              <input
                value={form.referenceAccountUrl}
                onChange={(event) => updateField("referenceAccountUrl", event.target.value)}
                className={inputClassName()}
                placeholder="https://www.tiktok.com/@research.connect"
              />
            </label>

            <label className="block border border-black/10 bg-[#f8f8f4] p-4">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Reference video URL</div>
              <input
                value={form.referenceVideoUrl}
                onChange={(event) => updateField("referenceVideoUrl", event.target.value)}
                className={inputClassName()}
                placeholder="https://www.tiktok.com/@reference/video/..."
              />
            </label>

            <div className="grid gap-4 lg:grid-cols-2">
              <label className="block border border-black/10 bg-[#f8f8f4] p-4">
                <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Raw footage folder</div>
                <input
                  value={form.materialDirectory}
                  onChange={(event) => updateField("materialDirectory", event.target.value)}
                  className={inputClassName()}
                  placeholder="/Users/kk/Desktop/auto video/projects/.../materials/raw"
                />
                <div className="mt-3 text-sm leading-6 text-black/58">
                  This version saves the folder path into intake notes. Upload automation comes next.
                </div>
              </label>

              <div className="border border-black/10 bg-[#f8f8f4] p-4">
                <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Reference angle hints</div>
                <div className="mt-4 space-y-2">
                  {(selectedProduct?.good_tiktok_angles || []).slice(0, 3).map((angle) => (
                    <div key={angle} className="border border-black/10 bg-white px-3 py-2 text-sm text-black/70">
                      {angle}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <label className="block border border-black/10 bg-[#f8f8f4] p-4">
                <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Template</div>
                <input
                  value={form.templateName}
                  onChange={(event) => updateField("templateName", event.target.value)}
                  className={inputClassName()}
                  placeholder="Google Scholar trust template"
                />
              </label>
              <label className="block border border-black/10 bg-[#f8f8f4] p-4">
                <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Video length</div>
                <select
                  value={form.videoLength}
                  onChange={(event) => updateField("videoLength", event.target.value)}
                  className={inputClassName()}
                >
                  <option value="20-25s">20-25s</option>
                  <option value="25-35s">25-35s</option>
                  <option value="35-45s">35-45s</option>
                </select>
              </label>
            </div>

            <label className="block border border-black/10 bg-[#f8f8f4] p-4">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Tone</div>
              <input
                value={form.tone}
                onChange={(event) => updateField("tone", event.target.value)}
                className={inputClassName()}
                placeholder="native creator style, casual, not too salesy"
              />
            </label>

            <label className="block border border-black/10 bg-[#f8f8f4] p-4">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-steel">Notes</div>
              <textarea
                value={form.notes}
                onChange={(event) => updateField("notes", event.target.value)}
                className={`${inputClassName()} min-h-32 resize-y`}
                placeholder="Example: use question hook, keep second line as strong website CTA, stay close to research.connect tone."
              />
            </label>
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
                <span className="font-mono text-[11px] uppercase tracking-[0.24em] text-white/45">
                  {isPending ? "Writing" : "Queued"}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Generated Work Order</div>
          <pre className="mt-4 overflow-x-auto rounded-md border border-black/10 bg-[#121212] p-4 font-mono text-[12px] leading-6 text-white/78">
            {JSON.stringify(workOrderPreview, null, 2)}
          </pre>
        </div>

        <div className="border border-black/10 bg-panel p-6 shadow-panel">
          <div className="font-mono text-[11px] uppercase tracking-[0.28em] text-steel">Primary Action</div>
          <button
            type="submit"
            disabled={isPending}
            className="mt-4 w-full rounded-md border border-black bg-black px-4 py-3 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isPending ? "Creating project job..." : "Generate Project Job"}
          </button>
          <p className="mt-3 text-sm leading-6 text-black/62">
            This version creates the project folder, `full_workflow_input.json`, starter `asset_library.json`, and
            `project_job.json`.
          </p>
          {error ? <div className="mt-4 border border-[#d5a6a6] bg-[#fff6f6] px-4 py-3 text-sm text-[#8d2d2d]">{error}</div> : null}
          {createdProject ? (
            <div className="mt-4 border border-black/10 bg-[#f8f8f4] px-4 py-3 text-sm text-black/70">
              Created: {createdProject.projectDir}
            </div>
          ) : null}
        </div>
      </section>
    </form>
  );
}

